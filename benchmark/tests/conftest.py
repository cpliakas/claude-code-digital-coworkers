"""Shared fixtures for benchmark harness tests."""

import json
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest
import yaml

# Add benchmark directory to path so we can import benchmark module
sys.path.insert(0, str(Path(__file__).parent.parent))


FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Dataset fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_dataset():
    """Three realistic questions for testing."""
    return [
        {
            "id": 1,
            "scenario": (
                "A company collects data for temperature and humidity "
                "across multiple continents. The average volume is 500 GB "
                "daily. Which solution meets these requirements?"
            ),
            "correct_answer": (
                "Turn on S3 Transfer Acceleration on the destination "
                "S3 bucket. Use multipart uploads"
            ),
            "explanation": "S3 Transfer Acceleration uses Edge Locations.",
        },
        {
            "id": 2,
            "scenario": (
                "A company needs to analyze log files stored in JSON "
                "format in an Amazon S3 bucket. Queries will be simple "
                "and run on-demand."
            ),
            "correct_answer": (
                "Use Amazon Athena directly with Amazon S3 to run "
                "the queries as needed"
            ),
            "explanation": "Athena is an interactive query service.",
        },
        {
            "id": 3,
            "scenario": (
                "A company uses AWS Organizations to manage multiple "
                "AWS accounts. The company wants to limit S3 bucket "
                "access to organization members only."
            ),
            "correct_answer": (
                "Add the aws PrincipalOrgID global condition key to "
                "the S3 bucket policy"
            ),
            "explanation": "aws:PrincipalOrgID simplifies cross-account.",
        },
    ]


@pytest.fixture
def field_map():
    """Standard dataset field mapping."""
    return {
        "id": "id",
        "scenario": "scenario",
        "expected_answer": "correct_answer",
        "explanation": "explanation",
    }


# ---------------------------------------------------------------------------
# Suite config fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def direct_mode_config():
    """Configuration for a binary scoring mode."""
    return {
        "description": "Binary correct/incorrect answer check",
        "agent_max_tokens": 512,
        "agent_prompt": (
            "Answer this question in 1-3 sentences.\n\n"
            "Scenario:\n{scenario}\n\nYour answer:"
        ),
        "judge_prompt": (
            "Does the response match?\n\n"
            "Scenario: {scenario}\n"
            "Correct: {expected_answer}\n"
            "Response: {response}\n\n"
            "JSON only:\n"
            '{{"correct": true/false, "confidence": 0.0-1.0, '
            '"explanation": "..."}}'
        ),
        "scoring": {
            "type": "binary",
            "correct_field": "correct",
            "metrics": [{"name": "confidence", "type": "float"}],
            "text_fields": ["explanation"],
        },
        "summary": {
            "show_failures": True,
            "max_failures_shown": 10,
        },
    }


@pytest.fixture
def reasoning_mode_config():
    """Configuration for a dimensional scoring mode."""
    return {
        "description": "Multi-dimension reasoning quality assessment",
        "agent_max_tokens": 2048,
        "agent_prompt": (
            "Provide a detailed review.\n\n"
            "Scenario:\n{scenario}\n\nYour review:"
        ),
        "judge_prompt": (
            "Score each dimension 1-5.\n\n"
            "Scenario: {scenario}\n"
            "Correct: {expected_answer}\n"
            "Review: {response}\n\n"
            "JSON only:\n"
            '{{"answer_accuracy": 1-5, "specificity": 1-5, '
            '"overall": 1.0-5.0, "strengths": "...", '
            '"weaknesses": "..."}}'
        ),
        "scoring": {
            "type": "dimensional",
            "dimensions": [
                "answer_accuracy",
                "specificity",
                "overall",
            ],
            "text_fields": ["strengths", "weaknesses"],
        },
        "summary": {
            "primary_dimension": "overall",
            "weakness_keywords": ["cost", "vague", "generic"],
        },
    }


@pytest.fixture
def sample_suite_config(direct_mode_config, reasoning_mode_config):
    """Complete suite config dict."""
    return {
        "suite": {
            "name": "Test Suite",
            "description": "A test benchmark suite",
            "agent": "tests/fixtures/sample_agent.md",
            "dataset": "questions.json",
        },
        "dataset_fields": {
            "id": "id",
            "scenario": "scenario",
            "expected_answer": "correct_answer",
            "explanation": "explanation",
        },
        "defaults": {
            "agent_model": "claude-haiku-4-5-20251001",
            "judge_model": "claude-sonnet-4-5-20250929",
        },
        "modes": {
            "direct": direct_mode_config,
            "reasoning": reasoning_mode_config,
        },
    }


@pytest.fixture
def suite_dir(tmp_path, sample_suite_config, sample_dataset):
    """Create a temp suite directory with suite.yaml and questions.json."""
    suite_path = tmp_path / "test-suite"
    suite_path.mkdir()

    # Write suite.yaml
    with open(suite_path / "suite.yaml", "w") as f:
        yaml.dump(sample_suite_config, f, default_flow_style=False)

    # Write questions.json
    with open(suite_path / "questions.json", "w") as f:
        json.dump(sample_dataset, f)

    # Create results dir
    (suite_path / "results").mkdir()

    # Write a minimal agent file at the expected path relative to "repo root"
    # For tests, we set REPO_ROOT to tmp_path
    agent_dir = tmp_path / "tests" / "fixtures"
    agent_dir.mkdir(parents=True)
    agent_md = agent_dir / "sample_agent.md"
    agent_md.write_text(
        "---\nname: test-agent\ndescription: \"Test\"\n"
        "model: inherit\nmemory: project\n---\n\n"
        "## Jurisdiction\n\nTest content.\n"
    )

    return suite_path


# ---------------------------------------------------------------------------
# Mock API response fixtures
# ---------------------------------------------------------------------------

def make_mock_response(text: str) -> Mock:
    """Create a mock Anthropic API response with the given text."""
    content_block = Mock()
    content_block.text = text
    response = Mock()
    response.content = [content_block]
    return response


@pytest.fixture
def mock_agent_response():
    """Mock agent response for a direct-mode question."""
    return make_mock_response(
        "Use S3 Transfer Acceleration with multipart uploads to speed "
        "up data transfer from multiple continents to a single S3 bucket."
    )


@pytest.fixture
def mock_judge_response_binary():
    """Mock judge response for binary scoring (correct)."""
    return make_mock_response(json.dumps({
        "correct": True,
        "confidence": 0.95,
        "explanation": "Matches the correct answer.",
    }))


@pytest.fixture
def mock_judge_response_binary_incorrect():
    """Mock judge response for binary scoring (incorrect)."""
    return make_mock_response(json.dumps({
        "correct": False,
        "confidence": 0.85,
        "explanation": "Agent recommended Lambda instead of EC2 Auto Scaling.",
    }))


@pytest.fixture
def mock_judge_response_dimensional():
    """Mock judge response for dimensional scoring."""
    return make_mock_response(json.dumps({
        "answer_accuracy": 4,
        "specificity": 5,
        "overall": 4.5,
        "strengths": "Excellent specificity with exact service names.",
        "weaknesses": "Could improve cost analysis.",
    }))


@pytest.fixture
def mock_client(mock_agent_response, mock_judge_response_binary):
    """Mock Anthropic client that returns agent then judge responses."""
    client = Mock()
    client.messages.create.side_effect = [
        mock_agent_response,
        mock_judge_response_binary,
    ]
    return client
