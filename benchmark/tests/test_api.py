"""Tests for API helper functions."""

import json
from unittest.mock import Mock

import pytest

from benchmark import call_agent, call_judge
from conftest import make_mock_response


class TestCallAgent:
    def test_returns_text(self):
        client = Mock()
        client.messages.create.return_value = make_mock_response(
            "Use S3 Transfer Acceleration."
        )
        text, tool_calls = call_agent(client, "system prompt", "user prompt", "model-id")
        assert text == "Use S3 Transfer Acceleration."
        assert tool_calls == []

    def test_passes_params(self):
        client = Mock()
        client.messages.create.return_value = make_mock_response("response")
        call_agent(
            client, "my system prompt", "my user prompt",
            "claude-haiku-4-5-20251001", max_tokens=512,
        )
        client.messages.create.assert_called_once_with(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system="my system prompt",
            messages=[{"role": "user", "content": "my user prompt"}],
        )


class TestCallJudge:
    def test_parses_plain_json(self):
        client = Mock()
        judge_json = {"correct": True, "confidence": 0.95}
        client.messages.create.return_value = make_mock_response(
            json.dumps(judge_json)
        )
        result = call_judge(client, "judge prompt", "model-id")
        assert result == judge_json

    def test_parses_markdown_wrapped_json(self):
        client = Mock()
        judge_json = {"correct": False, "confidence": 0.8}
        wrapped = f"```json\n{json.dumps(judge_json)}\n```"
        client.messages.create.return_value = make_mock_response(wrapped)
        result = call_judge(client, "judge prompt", "model-id")
        assert result == judge_json

    def test_parses_bare_code_block(self):
        client = Mock()
        judge_json = {"correct": True, "confidence": 1.0}
        wrapped = f"```\n{json.dumps(judge_json)}\n```"
        client.messages.create.return_value = make_mock_response(wrapped)
        result = call_judge(client, "judge prompt", "model-id")
        assert result == judge_json
