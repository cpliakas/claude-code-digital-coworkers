"""Tests for the run_mode() function."""

import json
from unittest.mock import Mock

import pytest

from benchmark import run_mode
from conftest import make_mock_response


class TestRunModeDryRun:
    def test_returns_skipped(self, sample_dataset, field_map,
                             direct_mode_config):
        result = run_mode(
            client=None,
            question=sample_dataset[0],
            system_prompt="system",
            mode_name="direct",
            mode_config=direct_mode_config,
            field_map=field_map,
            agent_model="model",
            judge_model="model",
            dry_run=True,
        )
        assert result["skipped"] is True
        assert result["mode"] == "direct"
        assert result["id"] == 1
        assert "prompt" in result

    def test_dry_run_does_not_call_api(self, sample_dataset, field_map,
                                       direct_mode_config):
        client = Mock()
        run_mode(
            client=client,
            question=sample_dataset[0],
            system_prompt="system",
            mode_name="direct",
            mode_config=direct_mode_config,
            field_map=field_map,
            agent_model="model",
            judge_model="model",
            dry_run=True,
        )
        client.messages.create.assert_not_called()


class TestRunModeBinary:
    def test_correct(self, sample_dataset, field_map, direct_mode_config):
        client = Mock()
        client.messages.create.side_effect = [
            make_mock_response("Use S3 Transfer Acceleration."),
            make_mock_response(json.dumps({
                "correct": True,
                "confidence": 0.95,
                "explanation": "Matches.",
            })),
        ]
        result = run_mode(
            client=client,
            question=sample_dataset[0],
            system_prompt="system",
            mode_name="direct",
            mode_config=direct_mode_config,
            field_map=field_map,
            agent_model="model",
            judge_model="model",
            dry_run=False,
        )
        assert result["correct"] is True
        assert result["confidence"] == 0.95
        assert result["explanation"] == "Matches."
        assert result["mode"] == "direct"
        assert result["id"] == 1

    def test_incorrect(self, sample_dataset, field_map, direct_mode_config):
        client = Mock()
        client.messages.create.side_effect = [
            make_mock_response("Use Lambda instead."),
            make_mock_response(json.dumps({
                "correct": False,
                "confidence": 0.85,
                "explanation": "Wrong approach.",
            })),
        ]
        result = run_mode(
            client=client,
            question=sample_dataset[0],
            system_prompt="system",
            mode_name="direct",
            mode_config=direct_mode_config,
            field_map=field_map,
            agent_model="model",
            judge_model="model",
            dry_run=False,
        )
        assert result["correct"] is False

    def test_includes_agent_response(self, sample_dataset, field_map,
                                     direct_mode_config):
        client = Mock()
        agent_text = "Use S3 Transfer Acceleration."
        client.messages.create.side_effect = [
            make_mock_response(agent_text),
            make_mock_response(json.dumps({
                "correct": True, "confidence": 1.0, "explanation": "OK",
            })),
        ]
        result = run_mode(
            client=client,
            question=sample_dataset[0],
            system_prompt="system",
            mode_name="direct",
            mode_config=direct_mode_config,
            field_map=field_map,
            agent_model="model",
            judge_model="model",
            dry_run=False,
        )
        assert result["agent_response"] == agent_text


class TestRunModeDimensional:
    def test_all_dimensions_present(self, sample_dataset, field_map,
                                    reasoning_mode_config):
        client = Mock()
        client.messages.create.side_effect = [
            make_mock_response("Full review text here."),
            make_mock_response(json.dumps({
                "answer_accuracy": 4,
                "specificity": 5,
                "overall": 4.5,
                "strengths": "Good specificity.",
                "weaknesses": "Lacks cost detail.",
            })),
        ]
        result = run_mode(
            client=client,
            question=sample_dataset[0],
            system_prompt="system",
            mode_name="reasoning",
            mode_config=reasoning_mode_config,
            field_map=field_map,
            agent_model="model",
            judge_model="model",
            dry_run=False,
        )
        assert result["answer_accuracy"] == 4
        assert result["specificity"] == 5
        assert result["overall"] == 4.5
        assert result["strengths"] == "Good specificity."
        assert result["weaknesses"] == "Lacks cost detail."
        assert result["mode"] == "reasoning"
        assert "agent_response" in result


class TestRunModeMaxTokens:
    def test_uses_config_max_tokens(self, sample_dataset, field_map,
                                    direct_mode_config):
        client = Mock()
        client.messages.create.side_effect = [
            make_mock_response("response"),
            make_mock_response(json.dumps({
                "correct": True, "confidence": 1.0, "explanation": "OK",
            })),
        ]
        run_mode(
            client=client,
            question=sample_dataset[0],
            system_prompt="system",
            mode_name="direct",
            mode_config=direct_mode_config,
            field_map=field_map,
            agent_model="test-model",
            judge_model="judge-model",
            dry_run=False,
        )
        # First call is to agent — check max_tokens=512 from config
        agent_call = client.messages.create.call_args_list[0]
        assert agent_call.kwargs["max_tokens"] == 512
