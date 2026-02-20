# Agent Benchmark Harness

A generic, config-driven test harness for evaluating Claude Code agents against domain-specific datasets. Each benchmark is defined by a **suite**: a directory containing a `suite.yaml` config and a dataset file.

## Quick Start

```bash
cd benchmark

# Install dependencies
pip install -r requirements.txt

# Set your API key
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY

# Run a benchmark (dry run, no API calls)
python3 benchmark.py suites/aws-solutions-architect --dry-run --sample 3

# Run for real (small sample)
python3 benchmark.py suites/aws-solutions-architect --mode direct --sample 10

# Full run, all modes
python3 benchmark.py suites/aws-solutions-architect
```

## CLI Reference

```
python3 benchmark.py <suite-path> [options]
```

| Flag | Default | Description |
|------|---------|-------------|
| `<suite-path>` | *(required)* | Path to suite directory containing `suite.yaml` |
| `--mode MODE` | `all` | Mode name from `suite.yaml`, or `all` to run every mode |
| `--sample N` | `0` | Random sample of N questions (0 = all) |
| `--ids 1,2,5` | | Comma-separated question IDs to test |
| `--agent-model` | from suite.yaml | Override the agent model |
| `--judge-model` | from suite.yaml | Override the judge model |
| `--dry-run` | | Show prompts without making API calls |
| `--output-dir` | `<suite>/results` | Output directory for results |

## Creating a New Suite

1. Create a directory under `suites/`:

```
suites/my-agent/
├── suite.yaml
├── dataset.json
└── results/          # created automatically
```

2. Write `suite.yaml` (see [Suite Configuration](#suite-configuration) below).

3. Prepare your dataset as a JSON array of objects. Each object needs at minimum an ID field, a scenario/question field, and an expected answer field. The field names are flexible since you map them in `suite.yaml`.

4. Run: `python3 benchmark.py suites/my-agent --dry-run --sample 3`

## Suite Configuration

A `suite.yaml` has four sections:

### `suite` (metadata)

```yaml
suite:
  name: "Human-readable suite name"
  description: "What this benchmark tests"
  agent: "plugins/cloud-infra/agents/aws-solutions-architect.md"  # relative to repo root
  dataset: "questions.json"  # relative to suite directory
```

### `dataset_fields` (field mapping)

Maps your dataset's JSON keys to the harness variables used in prompt templates:

```yaml
dataset_fields:
  id: "id"                        # unique identifier
  scenario: "scenario"            # the input/question text
  expected_answer: "correct_answer"  # known correct answer
  explanation: "explanation"      # optional, for reference
```

### `defaults` (model defaults)

```yaml
defaults:
  agent_model: "claude-haiku-4-5-20251001"
  judge_model: "claude-sonnet-4-5-20250929"
```

### `modes` (test modes)

Each mode defines how the agent is prompted, how the judge evaluates, and how results are scored.

**Binary scoring** (correct/incorrect):

```yaml
modes:
  direct:
    description: "Binary answer check"
    agent_max_tokens: 512
    agent_prompt: |
      ... {scenario} ...
    judge_prompt: |
      ... {scenario} ... {expected_answer} ... {response} ...
      Respond with ONLY a JSON object:
      {{
        "correct": true/false,
        "confidence": 0.0-1.0,
        "explanation": "..."
      }}
    scoring:
      type: "binary"
      correct_field: "correct"
      metrics:
        - name: "confidence"
          type: "float"
      text_fields:
        - "explanation"
    summary:
      show_failures: true
      max_failures_shown: 10
```

**Dimensional scoring** (multiple dimensions, 1-5 scale):

```yaml
modes:
  reasoning:
    description: "Multi-dimension quality assessment"
    agent_max_tokens: 2048
    agent_prompt: |
      ... {scenario} ...
    judge_prompt: |
      ... {scenario} ... {expected_answer} ... {response} ...
      Respond with ONLY a JSON object:
      {{
        "dim_one": <1-5>,
        "dim_two": <1-5>,
        "overall": <1.0-5.0>,
        "strengths": "...",
        "weaknesses": "..."
      }}
    scoring:
      type: "dimensional"
      dimensions:
        - "dim_one"
        - "dim_two"
        - "overall"
      text_fields:
        - "strengths"
        - "weaknesses"
    summary:
      primary_dimension: "overall"
      weakness_keywords:
        - "keyword1"
        - "keyword2"
```

### Prompt template variables

Templates use Python `.format()` syntax with these variables:

| Variable | Source | Available in |
|----------|--------|--------------|
| `{scenario}` | `dataset_fields.scenario` | agent + judge prompts |
| `{expected_answer}` | `dataset_fields.expected_answer` | judge prompt only |
| `{response}` | agent's response | judge prompt only |

Literal JSON braces in prompts must be doubled: `{{` and `}}`.

## Output

Each run produces timestamped files in the results directory:

- `results_<mode>_<timestamp>.json` contains full results including agent responses
- `results_<mode>_<timestamp>.csv` contains scores only (no agent responses)

## Testing

The harness has its own unit tests covering suite loading, prompt rendering, API interactions, the benchmark runner, and output formatting. All API calls are mocked so no `ANTHROPIC_API_KEY` is needed.

```bash
cd benchmark
pytest
```

## Available Suites

| Suite | Agent | Questions | Description |
|-------|-------|-----------|-------------|
| `aws-solutions-architect` | `aws-solutions-architect` | 494 | SAA-C03 exam scenarios |
