"""Test configuration and shared fixtures."""

import pytest
from pathlib import Path
import tempfile
import shutil
import yaml
from typing import Dict, Any

from tui_form_designer.core.flow_engine import FlowEngine
from tui_form_designer.ui.questionary_ui import QuestionaryUI


@pytest.fixture
def temp_flows_dir():
    """Create a temporary directory for test flows."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_flow_definition() -> Dict[str, Any]:
    """Sample flow definition for testing."""
    return {
        "flow_id": "test_flow",
        "title": "Test Flow",
        "description": "A flow for testing",
        "icon": "🧪",
        "steps": [
            {
                "id": "name",
                "type": "text",
                "message": "Enter your name:",
                "validate": "required",
            },
            {
                "id": "age",
                "type": "text",
                "message": "Enter your age:",
                "validate": "integer",
            },
            {
                "id": "email",
                "type": "text",
                "message": "Enter your email:",
                "validate": "email",
            },
            {
                "id": "subscribe",
                "type": "confirm",
                "message": "Subscribe to newsletter?",
                "default": False,
            },
        ],
        "output_mapping": {
            "user": {"name": "name", "age": "age", "email": "email"},
            "preferences": {"newsletter": "subscribe"},
        },
    }


@pytest.fixture
def conditional_flow_definition() -> Dict[str, Any]:
    """Flow definition with conditional logic for testing."""
    return {
        "flow_id": "conditional_test",
        "title": "Conditional Test Flow",
        "description": "Testing conditional logic",
        "steps": [
            {
                "id": "enable_feature",
                "type": "confirm",
                "message": "Enable advanced features?",
                "default": False,
            },
            {
                "id": "feature_config",
                "type": "text",
                "message": "Configure feature:",
                "condition": "enable_feature == true",
            },
            {
                "id": "basic_setting",
                "type": "text",
                "message": "Basic setting:",
                "condition": "enable_feature == false",
            },
        ],
    }


@pytest.fixture
def invalid_flow_definition() -> Dict[str, Any]:
    """Invalid flow definition for testing validation."""
    return {
        "flow_id": "invalid_flow",
        "title": "Invalid Flow",
        "steps": [
            {
                # Missing 'id' field
                "type": "text",
                "message": "This step has no ID",
            },
            {"id": "duplicate_id", "type": "text", "message": "First step"},
            {
                "id": "duplicate_id",  # Duplicate ID
                "type": "text",
                "message": "Second step with same ID",
            },
            {
                "id": "invalid_type",
                "type": "invalid_type",  # Invalid step type
                "message": "Invalid step type",
            },
        ],
    }


@pytest.fixture
def flow_engine(temp_flows_dir):
    """FlowEngine instance with temporary flows directory."""
    return FlowEngine(flows_dir=str(temp_flows_dir))


@pytest.fixture
def questionary_ui():
    """QuestionaryUI instance for testing."""
    return QuestionaryUI()


@pytest.fixture
def sample_flow_file(temp_flows_dir, sample_flow_definition):
    """Create a sample flow file."""
    flow_path = temp_flows_dir / "test_flow.yml"
    with open(flow_path, "w") as f:
        yaml.dump(sample_flow_definition, f)
    return flow_path


@pytest.fixture
def mock_responses():
    """Sample mock responses for testing."""
    return {
        "name": "Test User",
        "age": "25",
        "email": "test@example.com",
        "subscribe": True,
    }
