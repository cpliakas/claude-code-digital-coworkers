"""Integration tests for main() with mocked API."""

import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

from benchmark import main
from conftest import make_mock_response


def _make_suite_env(tmp_path, questions, suite_config_override=None):
    """Set up a complete suite environment in tmp_path.

    Returns (suite_path, repo_root) where repo_root is the fake repo root
    that contains the agent file at the path referenced in suite.yaml.
    """
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    # Write agent file
    agent_dir = repo_root / "agents"
    agent_dir.mkdir()
    (agent_dir / "test-agent.md").write_text(
        "---\nname: test-agent\ndescription: \"Test\"\n"
        "model: inherit\nmemory: project\n---\n\n"
        "## Jurisdiction\n\nTest agent content.\n"
    )

    # Write suite
    suite_path = repo_root / "suites" / "test-agent"
    suite_path.mkdir(parents=True)
    (suite_path / "results").mkdir()

    config = suite_config_override or {
        "suite": {
            "name": "Integration Test Suite",
            "description": "For integration tests",
            "agent": "agents/test-agent.md",
            "dataset": "questions.json",
        },
        "dataset_fields": {
            "id": "id",
            "scenario": "scenario",
            "expected_answer": "correct_answer",
            "explanation": "explanation",
        },
        "defaults": {
            "agent_model": "test-model",
            "judge_model": "test-judge",
        },
        "modes": {
            "direct": {
                "description": "Binary check",
                "agent_max_tokens": 256,
                "agent_prompt": "Q: {scenario}\nA:",
                "judge_prompt": (
                    "S: {scenario} C: {expected_answer} R: {response}\n"
                    '{{"correct": true, "confidence": 1.0, '
                    '"explanation": "ok"}}'
                ),
                "scoring": {
                    "type": "binary",
                    "correct_field": "correct",
                    "metrics": [{"name": "confidence", "type": "float"}],
                    "text_fields": ["explanation"],
                },
                "summary": {"show_failures": True, "max_failures_shown": 5},
            },
        },
    }

    with open(suite_path / "suite.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    with open(suite_path / "questions.json", "w") as f:
        json.dump(questions, f)

    return suite_path, repo_root


def _make_binary_side_effects(n):
    """Create n pairs of (agent, judge) mock responses."""
    effects = []
    for _ in range(n):
        effects.append(make_mock_response("Test agent answer."))
        effects.append(make_mock_response(json.dumps({
            "correct": True,
            "confidence": 0.9,
            "explanation": "Matches.",
        })))
    return effects


QUESTIONS = [
    {"id": i, "scenario": f"Scenario {i}", "correct_answer": f"Answer {i}",
     "explanation": f"Explanation {i}"}
    for i in range(1, 6)
]


class TestMainDryRun:
    def test_creates_result_files(self, tmp_path, monkeypatch):
        suite_path, repo_root = _make_suite_env(tmp_path, QUESTIONS)
        monkeypatch.setattr(
            "benchmark.REPO_ROOT", repo_root,
        )
        monkeypatch.setattr(
            sys, "argv",
            ["benchmark.py", str(suite_path), "--dry-run", "--sample", "2"],
        )
        main()
        results_dir = suite_path / "results"
        json_files = list(results_dir.glob("*.json"))
        assert len(json_files) >= 1
        with open(json_files[0]) as f:
            data = json.load(f)
        assert all(r.get("skipped") for r in data)


class TestMainSingleMode:
    def test_only_direct_results(self, tmp_path, monkeypatch):
        suite_path, repo_root = _make_suite_env(tmp_path, QUESTIONS[:2])
        monkeypatch.setattr("benchmark.REPO_ROOT", repo_root)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        mock_client = Mock()
        mock_client.messages.create.side_effect = _make_binary_side_effects(2)

        with patch("benchmark.anthropic.Anthropic", return_value=mock_client):
            monkeypatch.setattr(
                sys, "argv",
                ["benchmark.py", str(suite_path), "--mode", "direct"],
            )
            main()

        results_dir = suite_path / "results"
        json_files = list(results_dir.glob("*.json"))
        assert len(json_files) == 1
        with open(json_files[0]) as f:
            data = json.load(f)
        assert len(data) == 2
        assert all(r["mode"] == "direct" for r in data)


class TestMainFiltering:
    def test_ids_filter(self, tmp_path, monkeypatch):
        suite_path, repo_root = _make_suite_env(tmp_path, QUESTIONS)
        monkeypatch.setattr("benchmark.REPO_ROOT", repo_root)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        mock_client = Mock()
        mock_client.messages.create.side_effect = _make_binary_side_effects(2)

        with patch("benchmark.anthropic.Anthropic", return_value=mock_client):
            monkeypatch.setattr(
                sys, "argv",
                ["benchmark.py", str(suite_path), "--ids", "1,3"],
            )
            main()

        results_dir = suite_path / "results"
        json_files = list(results_dir.glob("*.json"))
        with open(json_files[0]) as f:
            data = json.load(f)
        assert len(data) == 2
        ids = {r["id"] for r in data}
        assert ids == {1, 3}

    def test_sample_filter(self, tmp_path, monkeypatch):
        suite_path, repo_root = _make_suite_env(tmp_path, QUESTIONS)
        monkeypatch.setattr("benchmark.REPO_ROOT", repo_root)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        mock_client = Mock()
        mock_client.messages.create.side_effect = _make_binary_side_effects(2)

        with patch("benchmark.anthropic.Anthropic", return_value=mock_client):
            monkeypatch.setattr(
                sys, "argv",
                ["benchmark.py", str(suite_path), "--sample", "2"],
            )
            main()

        results_dir = suite_path / "results"
        json_files = list(results_dir.glob("*.json"))
        with open(json_files[0]) as f:
            data = json.load(f)
        assert len(data) == 2


class TestMainErrorHandling:
    def test_api_error_captured(self, tmp_path, monkeypatch):
        suite_path, repo_root = _make_suite_env(tmp_path, QUESTIONS[:1])
        monkeypatch.setattr("benchmark.REPO_ROOT", repo_root)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API down")

        with patch("benchmark.anthropic.Anthropic", return_value=mock_client):
            monkeypatch.setattr(
                sys, "argv",
                ["benchmark.py", str(suite_path)],
            )
            # Should not raise — errors are captured in results
            main()

        results_dir = suite_path / "results"
        json_files = list(results_dir.glob("*.json"))
        with open(json_files[0]) as f:
            data = json.load(f)
        assert len(data) == 1
        assert "error" in data[0]
        assert "API down" in data[0]["error"]
