#!/usr/bin/env python3
"""
Agent Benchmark Harness

A generic, config-driven test harness for evaluating Claude Code agents against
domain-specific datasets. Each benchmark is defined by a suite directory
containing a suite.yaml config and a dataset file.

Usage:
  python3 benchmark.py <suite-path>                     # Run all modes
  python3 benchmark.py <suite-path> --mode direct       # Single mode
  python3 benchmark.py <suite-path> --sample 20         # Random sample
  python3 benchmark.py <suite-path> --ids 1,2,5,10      # Specific IDs
  python3 benchmark.py <suite-path> --dry-run            # Show prompts only

Requires: ANTHROPIC_API_KEY environment variable
"""

import argparse
import csv
import json
import os
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env", override=True)

try:
    import anthropic
except ImportError:
    print("Error: anthropic package required. Install with: pip install anthropic")
    sys.exit(1)


REPO_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Suite loading
# ---------------------------------------------------------------------------

def load_suite(suite_path: Path) -> dict:
    """Load and validate a suite.yaml config."""
    config_path = suite_path / "suite.yaml"
    if not config_path.exists():
        print(f"Error: {config_path} not found")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Validate required fields
    for key in ("suite", "dataset_fields", "modes"):
        if key not in config:
            print(f"Error: '{key}' missing from {config_path}")
            sys.exit(1)

    suite = config["suite"]
    for key in ("name", "agent", "dataset"):
        if key not in suite:
            print(f"Error: 'suite.{key}' missing from {config_path}")
            sys.exit(1)

    return config


def load_dataset(suite_path: Path, config: dict) -> list[dict]:
    """Load the dataset file referenced by the suite config."""
    dataset_path = suite_path / config["suite"]["dataset"]
    if not dataset_path.exists():
        print(f"Error: dataset not found: {dataset_path}")
        sys.exit(1)

    with open(dataset_path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Agent prompt extraction
# ---------------------------------------------------------------------------

def extract_system_prompt(agent_path: Path) -> str:
    """Read an agent .md file and strip YAML frontmatter."""
    if not agent_path.exists():
        print(f"Error: agent file not found: {agent_path}")
        sys.exit(1)

    text = agent_path.read_text()
    match = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
    if match:
        return text[match.end():].strip()
    return text.strip()


# ---------------------------------------------------------------------------
# Prompt rendering
# ---------------------------------------------------------------------------

def render_prompt(template: str, question: dict, field_map: dict,
                  response: str = None) -> str:
    """Substitute variables in a prompt template."""
    values = {
        "scenario": question[field_map["scenario"]],
        "expected_answer": question[field_map["expected_answer"]],
    }
    if response is not None:
        values["response"] = response
    return template.format(**values)


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def call_agent(client: anthropic.Anthropic, system_prompt: str,
               user_prompt: str, model: str, max_tokens: int = 2048) -> str:
    """Send a prompt to the agent and return the response."""
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text


def call_judge(client: anthropic.Anthropic, judge_prompt: str,
               model: str) -> dict:
    """Send a prompt to the judge and parse the JSON response."""
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": judge_prompt}],
    )
    text = response.content[0].text.strip()
    # Extract JSON from response (handle markdown code blocks)
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return json.loads(text)


# ---------------------------------------------------------------------------
# Benchmark runner
# ---------------------------------------------------------------------------

def run_mode(client: anthropic.Anthropic, question: dict, system_prompt: str,
             mode_name: str, mode_config: dict, field_map: dict,
             agent_model: str, judge_model: str, dry_run: bool) -> dict:
    """Run a single question through one mode."""
    id_field = field_map["id"]
    user_prompt = render_prompt(mode_config["agent_prompt"], question, field_map)

    if dry_run:
        return {
            "mode": mode_name,
            "id": question[id_field],
            "prompt": user_prompt,
            "skipped": True,
        }

    max_tokens = mode_config.get("agent_max_tokens", 2048)
    response = call_agent(client, system_prompt, user_prompt, agent_model,
                          max_tokens)

    judge_prompt = render_prompt(mode_config["judge_prompt"], question,
                                field_map, response=response)
    scores = call_judge(client, judge_prompt, judge_model)

    result = {
        "mode": mode_name,
        "id": question[id_field],
        "agent_response": response,
    }

    scoring = mode_config["scoring"]

    if scoring["type"] == "binary":
        result[scoring["correct_field"]] = scores.get(
            scoring["correct_field"], False
        )
        for metric in scoring.get("metrics", []):
            result[metric["name"]] = scores.get(metric["name"], 0)
    elif scoring["type"] == "dimensional":
        for dim in scoring.get("dimensions", []):
            result[dim] = scores.get(dim, 0)

    for field in scoring.get("text_fields", []):
        result[field] = scores.get(field, "")

    return result


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_results(results: list[dict], output_dir: Path, mode: str):
    """Write results to CSV and JSON."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"results_{mode}_{timestamp}.json"
    csv_path = output_dir / f"results_{mode}_{timestamp}.csv"

    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    if not results or results[0].get("skipped"):
        print(f"Dry run — prompts saved to {json_path}")
        return json_path, None

    # Write CSV (exclude error entries)
    scored = [r for r in results if "error" not in r]
    if not scored:
        return json_path, None

    fieldnames = [k for k in scored[0].keys() if k != "agent_response"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in scored:
            writer.writerow({k: v for k, v in row.items()
                             if k != "agent_response"})

    return json_path, csv_path


def print_summary(results: list[dict], mode_name: str, mode_config: dict):
    """Print a summary of benchmark results."""
    if not results or results[0].get("skipped"):
        return

    errors = [r for r in results if "error" in r]
    results = [r for r in results if "error" not in r]

    if not results:
        print(f"\n  All {len(errors)} questions failed. No results to summarize.")
        return

    print(f"\n{'=' * 60}")
    print(f"  BENCHMARK RESULTS — {mode_name.upper()} MODE")
    print(f"  {len(results)} questions evaluated")
    if errors:
        print(f"  ({len(errors)} questions failed — excluded from stats)")
    print(f"{'=' * 60}\n")

    scoring = mode_config["scoring"]
    summary = mode_config.get("summary", {})

    if scoring["type"] == "binary":
        correct_field = scoring["correct_field"]
        correct = sum(1 for r in results if r.get(correct_field))
        total = len(results)
        pct = (correct / total) * 100 if total else 0
        print(f"  Accuracy:   {correct}/{total} ({pct:.1f}%)")

        # Print averages for numeric metrics
        for metric in scoring.get("metrics", []):
            name = metric["name"]
            vals = [r.get(name, 0) for r in results]
            if vals:
                avg = sum(vals) / len(vals)
                print(f"  Avg {name}: {avg:.2f}")

        # Show failures
        if summary.get("show_failures", False):
            misses = [r for r in results if not r.get(correct_field)]
            if misses:
                max_shown = summary.get("max_failures_shown", 10)
                print(f"\n  Incorrect answers ({len(misses)}):")
                text_fields = scoring.get("text_fields", [])
                detail_field = text_fields[0] if text_fields else None
                for r in misses[:max_shown]:
                    detail = r.get(detail_field, "")[:80] if detail_field else ""
                    print(f"    Q{r['id']}: {detail}")
                if len(misses) > max_shown:
                    print(f"    ... and {len(misses) - max_shown} more")

    elif scoring["type"] == "dimensional":
        dimensions = scoring.get("dimensions", [])
        print(f"  {'Dimension':<22} {'Avg':>6} {'Min':>6} {'Max':>6}")
        print(f"  {'-' * 42}")
        for dim in dimensions:
            vals = [r.get(dim, 0) for r in results]
            if vals:
                avg = sum(vals) / len(vals)
                print(f"  {dim:<22} {avg:>6.2f} {min(vals):>6.1f} "
                      f"{max(vals):>6.1f}")

        # Weakness keyword analysis
        keywords = summary.get("weakness_keywords", [])
        if keywords:
            text_fields = scoring.get("text_fields", [])
            weakness_field = next(
                (f for f in text_fields if "weakness" in f.lower()), None
            )
            if weakness_field:
                print(f"\n  Common weaknesses:")
                counts: dict[str, int] = {}
                for r in results:
                    w = r.get(weakness_field, "")
                    if w:
                        for word in keywords:
                            if word.lower() in w.lower():
                                counts[word] = counts.get(word, 0) + 1
                for word, count in sorted(counts.items(),
                                          key=lambda x: -x[1])[:5]:
                    print(f"    '{word}' mentioned in {count}/{len(results)} "
                          f"weakness notes")

    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Agent Benchmark Harness"
    )
    parser.add_argument(
        "suite", type=str,
        help="Path to the suite directory (contains suite.yaml)"
    )
    parser.add_argument(
        "--mode", type=str, default="all",
        help="Mode to run (from suite.yaml), or 'all' (default: all)"
    )
    parser.add_argument(
        "--sample", type=int, default=0,
        help="Random sample size (0 = all questions)"
    )
    parser.add_argument(
        "--ids", type=str, default="",
        help="Comma-separated question IDs to test"
    )
    parser.add_argument(
        "--agent-model", type=str, default=None,
        help="Override agent model (default: from suite.yaml)"
    )
    parser.add_argument(
        "--judge-model", type=str, default=None,
        help="Override judge model (default: from suite.yaml)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show prompts without making API calls"
    )
    parser.add_argument(
        "--output-dir", type=str, default=None,
        help="Output directory (default: <suite>/results)"
    )
    args = parser.parse_args()

    # Load suite
    suite_path = Path(args.suite)
    config = load_suite(suite_path)
    field_map = config["dataset_fields"]
    defaults = config.get("defaults", {})

    # Resolve models
    agent_model = args.agent_model or defaults.get(
        "agent_model", "claude-haiku-4-5-20251001"
    )
    judge_model = args.judge_model or defaults.get(
        "judge_model", "claude-sonnet-4-5-20250929"
    )

    # Load dataset
    questions = load_dataset(suite_path, config)

    # Filter
    id_field = field_map["id"]
    if args.ids:
        target_ids = set(int(x) for x in args.ids.split(","))
        questions = [q for q in questions if q[id_field] in target_ids]
    elif args.sample > 0:
        questions = random.sample(questions, min(args.sample, len(questions)))

    if not questions:
        print("No questions to evaluate.")
        sys.exit(1)

    # Resolve modes
    available_modes = config["modes"]
    if args.mode == "all":
        mode_names = list(available_modes.keys())
    else:
        if args.mode not in available_modes:
            print(f"Error: mode '{args.mode}' not found in suite.yaml. "
                  f"Available: {', '.join(available_modes.keys())}")
            sys.exit(1)
        mode_names = [args.mode]

    # Resolve agent system prompt
    agent_path = REPO_ROOT / config["suite"]["agent"]
    system_prompt = extract_system_prompt(agent_path)

    # Output directory
    output_dir = Path(args.output_dir) if args.output_dir else (
        suite_path / "results"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Suite: {config['suite']['name']}")
    print(f"Benchmarking {len(questions)} questions, "
          f"modes: {', '.join(mode_names)}")
    print(f"Agent model: {agent_model}")
    print(f"Judge model: {judge_model}")

    # Setup API client
    client = None
    if not args.dry_run:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY environment variable required")
            sys.exit(1)
        client = anthropic.Anthropic(api_key=api_key)

    # Run benchmarks
    for mode_name in mode_names:
        mode_config = available_modes[mode_name]
        results = []

        for i, question in enumerate(questions):
            qid = question[id_field]
            print(f"  [{i + 1}/{len(questions)}] Q{qid} ({mode_name})...",
                  end="", flush=True)
            try:
                result = run_mode(
                    client, question, system_prompt, mode_name, mode_config,
                    field_map, agent_model, judge_model, args.dry_run,
                )
                results.append(result)
                if not args.dry_run:
                    scoring = mode_config["scoring"]
                    if scoring["type"] == "binary":
                        correct_field = scoring["correct_field"]
                        status = ("correct" if result.get(correct_field)
                                  else "WRONG")
                    else:
                        primary = mode_config.get("summary", {}).get(
                            "primary_dimension", "overall"
                        )
                        status = f"{primary}={result.get(primary, 0):.1f}"
                    print(f" {status}")
                else:
                    print(" (dry run)")
            except Exception as e:
                print(f" ERROR: {e}")
                results.append({
                    "mode": mode_name,
                    "id": qid,
                    "error": str(e),
                })

            # Rate limiting
            if not args.dry_run:
                time.sleep(0.5)

        json_path, csv_path = write_results(results, output_dir, mode_name)
        print(f"\nResults written to: {json_path}")
        if csv_path:
            print(f"CSV written to:     {csv_path}")
        print_summary(results, mode_name, mode_config)


if __name__ == "__main__":
    main()
