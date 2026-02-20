"""Tests for agent prompt extraction and prompt rendering."""

from pathlib import Path

import pytest

from benchmark import extract_system_prompt, render_prompt


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestExtractSystemPrompt:
    def test_strips_frontmatter(self):
        result = extract_system_prompt(FIXTURES_DIR / "sample_agent.md")
        assert result.startswith("## Jurisdiction")
        assert "---" not in result
        assert "name: test-agent" not in result

    def test_no_frontmatter(self, tmp_path):
        agent_file = tmp_path / "plain.md"
        agent_file.write_text("## Just Content\n\nNo frontmatter here.\n")
        result = extract_system_prompt(agent_file)
        assert result == "## Just Content\n\nNo frontmatter here."

    def test_missing_file(self, tmp_path):
        with pytest.raises(SystemExit):
            extract_system_prompt(tmp_path / "nonexistent.md")


class TestRenderPrompt:
    def test_agent_prompt(self, field_map, sample_dataset):
        template = "Review this:\n{scenario}\n\nYour answer:"
        result = render_prompt(template, sample_dataset[0], field_map)
        assert "500 GB" in result
        assert "{scenario}" not in result

    def test_judge_prompt(self, field_map, sample_dataset):
        template = (
            "Scenario: {scenario}\n"
            "Correct: {expected_answer}\n"
            "Response: {response}"
        )
        result = render_prompt(
            template, sample_dataset[0], field_map,
            response="Use S3 Transfer Acceleration",
        )
        assert "500 GB" in result
        assert "S3 Transfer Acceleration" in result
        # expected_answer maps to correct_answer field
        assert "multipart uploads" in result

    def test_literal_braces(self, field_map, sample_dataset):
        template = (
            "Scenario: {scenario}\n"
            'Output: {{"key": "value"}}'
        )
        result = render_prompt(template, sample_dataset[0], field_map)
        assert '{"key": "value"}' in result
        assert "500 GB" in result
