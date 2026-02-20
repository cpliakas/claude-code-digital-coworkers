"""Tests for suite loading and dataset loading."""

import json
from pathlib import Path

import pytest
import yaml

from benchmark import load_suite, load_dataset


class TestLoadSuite:
    def test_valid(self, suite_dir):
        config = load_suite(suite_dir)
        assert "suite" in config
        assert "dataset_fields" in config
        assert "modes" in config
        assert config["suite"]["name"] == "Test Suite"

    def test_missing_file(self, tmp_path):
        with pytest.raises(SystemExit):
            load_suite(tmp_path / "nonexistent")

    def test_missing_required_key(self, tmp_path):
        suite_path = tmp_path / "bad-suite"
        suite_path.mkdir()
        config = {"suite": {"name": "X", "agent": "a.md", "dataset": "q.json"}}
        # Missing 'modes' and 'dataset_fields'
        with open(suite_path / "suite.yaml", "w") as f:
            yaml.dump(config, f)
        with pytest.raises(SystemExit):
            load_suite(suite_path)

    def test_missing_suite_subkey(self, tmp_path):
        suite_path = tmp_path / "bad-suite2"
        suite_path.mkdir()
        config = {
            "suite": {"name": "X", "description": "Missing agent and dataset"},
            "dataset_fields": {"id": "id", "scenario": "s",
                               "expected_answer": "a"},
            "modes": {"test": {}},
        }
        with open(suite_path / "suite.yaml", "w") as f:
            yaml.dump(config, f)
        with pytest.raises(SystemExit):
            load_suite(suite_path)


class TestLoadDataset:
    def test_valid(self, suite_dir, sample_suite_config):
        questions = load_dataset(suite_dir, sample_suite_config)
        assert len(questions) == 3
        assert questions[0]["id"] == 1
        assert "scenario" in questions[0]
        assert "correct_answer" in questions[0]

    def test_missing_file(self, tmp_path, sample_suite_config):
        suite_path = tmp_path / "empty-suite"
        suite_path.mkdir()
        with pytest.raises(SystemExit):
            load_dataset(suite_path, sample_suite_config)
