"""Tests for result writing and summary printing."""

import csv
import json
from pathlib import Path

import pytest

from benchmark import write_results, print_summary


class TestWriteResults:
    def test_json_output(self, tmp_path):
        results = [
            {"mode": "direct", "id": 1, "correct": True, "confidence": 0.95,
             "explanation": "OK", "agent_response": "Use S3."},
        ]
        json_path, csv_path = write_results(results, tmp_path, "direct")
        assert json_path.exists()
        with open(json_path) as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["correct"] is True
        assert data[0]["agent_response"] == "Use S3."

    def test_csv_excludes_agent_response(self, tmp_path):
        results = [
            {"mode": "direct", "id": 1, "correct": True, "confidence": 0.95,
             "explanation": "OK", "agent_response": "Use S3."},
            {"mode": "direct", "id": 2, "correct": False, "confidence": 0.8,
             "explanation": "Wrong", "agent_response": "Use Lambda."},
        ]
        _, csv_path = write_results(results, tmp_path, "direct")
        assert csv_path.exists()
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 2
        assert "agent_response" not in rows[0]
        assert "correct" in rows[0]

    def test_dry_run_no_csv(self, tmp_path):
        results = [
            {"mode": "direct", "id": 1, "prompt": "test", "skipped": True},
        ]
        json_path, csv_path = write_results(results, tmp_path, "direct")
        assert json_path.exists()
        assert csv_path is None

    def test_errors_excluded_from_csv(self, tmp_path):
        results = [
            {"mode": "direct", "id": 1, "correct": True, "confidence": 1.0,
             "explanation": "OK", "agent_response": "S3."},
            {"mode": "direct", "id": 2, "error": "API error"},
        ]
        _, csv_path = write_results(results, tmp_path, "direct")
        assert csv_path.exists()
        with open(csv_path) as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 1
        assert rows[0]["id"] == "1"


class TestPrintSummaryBinary:
    def test_accuracy_output(self, capsys, direct_mode_config):
        results = [
            {"mode": "direct", "id": 1, "correct": True, "confidence": 0.95,
             "explanation": "OK"},
            {"mode": "direct", "id": 2, "correct": False, "confidence": 0.8,
             "explanation": "Wrong approach"},
            {"mode": "direct", "id": 3, "correct": True, "confidence": 1.0,
             "explanation": "OK"},
        ]
        print_summary(results, "direct", direct_mode_config)
        output = capsys.readouterr().out
        assert "2/3" in output
        assert "66.7%" in output
        assert "Incorrect answers (1)" in output
        assert "Wrong approach" in output

    def test_skipped_no_output(self, capsys, direct_mode_config):
        results = [
            {"mode": "direct", "id": 1, "skipped": True, "prompt": "test"},
        ]
        print_summary(results, "direct", direct_mode_config)
        output = capsys.readouterr().out
        assert output == ""

    def test_all_errors(self, capsys, direct_mode_config):
        results = [
            {"mode": "direct", "id": 1, "error": "fail"},
            {"mode": "direct", "id": 2, "error": "fail"},
        ]
        print_summary(results, "direct", direct_mode_config)
        output = capsys.readouterr().out
        assert "All 2 questions failed" in output


class TestPrintSummaryDimensional:
    def test_dimension_table(self, capsys, reasoning_mode_config):
        results = [
            {"mode": "reasoning", "id": 1, "answer_accuracy": 4,
             "specificity": 5, "overall": 4.5,
             "strengths": "Good", "weaknesses": "cost analysis lacking"},
            {"mode": "reasoning", "id": 2, "answer_accuracy": 3,
             "specificity": 4, "overall": 3.5,
             "strengths": "OK", "weaknesses": "vague and generic"},
        ]
        print_summary(results, "reasoning", reasoning_mode_config)
        output = capsys.readouterr().out
        assert "answer_accuracy" in output
        assert "specificity" in output
        assert "overall" in output
        assert "REASONING" in output

    def test_weakness_keywords(self, capsys, reasoning_mode_config):
        results = [
            {"mode": "reasoning", "id": 1, "answer_accuracy": 4,
             "specificity": 5, "overall": 4.5,
             "strengths": "Good", "weaknesses": "cost analysis is weak"},
            {"mode": "reasoning", "id": 2, "answer_accuracy": 3,
             "specificity": 4, "overall": 3.5,
             "strengths": "OK", "weaknesses": "too vague on cost details"},
        ]
        print_summary(results, "reasoning", reasoning_mode_config)
        output = capsys.readouterr().out
        assert "'cost' mentioned in 2/2" in output
        assert "'vague' mentioned in 1/2" in output
