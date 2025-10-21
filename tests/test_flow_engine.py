"""Tests for FlowEngine core functionality."""

import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

from tui_form_designer.core.flow_engine import FlowEngine
from tui_form_designer.core.exceptions import FlowValidationError, FlowExecutionError


class TestFlowEngine:
    """Test suite for FlowEngine."""

    def test_init_with_default_flows_dir(self):
        """Test FlowEngine initialization with default flows directory."""
        engine = FlowEngine()
        assert engine.flows_dir == Path("flows")
        assert engine.style is not None
        assert isinstance(engine.validators, dict)

    def test_init_with_custom_flows_dir(self, temp_flows_dir):
        """Test FlowEngine initialization with custom flows directory."""
        engine = FlowEngine(flows_dir=str(temp_flows_dir))
        assert engine.flows_dir == temp_flows_dir

    def test_init_with_theme(self):
        """Test FlowEngine initialization with different themes."""
        # Test default theme
        engine = FlowEngine(theme="default")
        assert engine.style is not None

        # Test dark theme
        engine = FlowEngine(theme="dark")
        assert engine.style is not None

        # Test minimal theme
        engine = FlowEngine(theme="minimal")
        assert engine.style is not None

    def test_get_available_flows_empty_dir(self, flow_engine):
        """Test getting flows from empty directory."""
        flows = flow_engine.get_available_flows()
        assert flows == []

    def test_get_available_flows_with_flows(self, flow_engine, sample_flow_file):
        """Test getting flows from directory with flows."""
        flows = flow_engine.get_available_flows()
        assert "test_flow" in flows

    def test_load_flow_valid(
        self, flow_engine, sample_flow_file, sample_flow_definition
    ):
        """Test loading a valid flow definition."""
        flow_def = flow_engine._load_flow("test_flow")
        assert flow_def == sample_flow_definition

    def test_load_flow_not_found(self, flow_engine):
        """Test loading a non-existent flow."""
        with pytest.raises(FlowValidationError, match="Flow definition not found"):
            flow_engine._load_flow("nonexistent")

    def test_validate_flow_valid(self, flow_engine, sample_flow_definition):
        """Test validation of a valid flow."""
        errors = flow_engine.validate_flow(sample_flow_definition)
        assert errors == []

    def test_validate_flow_missing_required_fields(self, flow_engine):
        """Test validation of flow missing required fields."""
        invalid_flow = {}
        errors = flow_engine.validate_flow(invalid_flow)
        assert len(errors) == 3  # Missing layout_id, title, steps
        assert any("Missing required field: layout_id" in error for error in errors)
        assert any("Missing required field: title" in error for error in errors)
        assert any("Missing required field: steps" in error for error in errors)

    def test_validate_flow_invalid_steps(self, flow_engine, invalid_flow_definition):
        """Test validation of flow with invalid steps."""
        errors = flow_engine.validate_flow(invalid_flow_definition)
        assert len(errors) > 0
        assert any("Missing 'id' field" in error for error in errors)
        assert any("Duplicate step ID" in error for error in errors)
        assert any("Invalid step type" in error for error in errors)

    def test_should_show_step_no_condition(self, flow_engine):
        """Test step visibility with no condition."""
        step = {"id": "test", "type": "text", "message": "Test"}
        context = {}
        assert flow_engine._should_show_step(step, context) is True

    def test_should_show_step_with_condition_true(self, flow_engine):
        """Test step visibility with condition that evaluates to true."""
        step = {
            "id": "test",
            "type": "text",
            "message": "Test",
            "condition": "enable_feature == true",
        }
        context = {"enable_feature": True}
        assert flow_engine._should_show_step(step, context) is True

    def test_should_show_step_with_condition_false(self, flow_engine):
        """Test step visibility with condition that evaluates to false."""
        step = {
            "id": "test",
            "type": "text",
            "message": "Test",
            "condition": "enable_feature == true",
        }
        context = {"enable_feature": False}
        assert flow_engine._should_show_step(step, context) is False

    def test_evaluate_expression_equality(self, flow_engine):
        """Test expression evaluation with equality operators."""
        context = {"value": "test", "number": 42, "flag": True}

        assert flow_engine._evaluate_expression("value == test", context) is True
        assert flow_engine._evaluate_expression("value == other", context) is False
        assert flow_engine._evaluate_expression("number == 42", context) is True
        assert flow_engine._evaluate_expression("flag == true", context) is True
        assert flow_engine._evaluate_expression("flag == false", context) is False

    def test_evaluate_expression_boolean_check(self, flow_engine):
        """Test expression evaluation with boolean checks."""
        context = {"enabled": True, "disabled": False}

        assert flow_engine._evaluate_expression("enabled", context) is True
        assert flow_engine._evaluate_expression("disabled", context) is False
        assert flow_engine._evaluate_expression("nonexistent", context) is False

    def test_get_nested_value(self, flow_engine):
        """Test getting nested values from context."""
        context = {"user": {"name": "John", "profile": {"email": "john@example.com"}}}

        assert flow_engine._get_nested_value(context, "user.name") == "John"
        assert (
            flow_engine._get_nested_value(context, "user.profile.email")
            == "john@example.com"
        )
        assert flow_engine._get_nested_value(context, "user.nonexistent") is None

    def test_format_preview(self, flow_engine):
        """Test preview text formatting."""
        context = {"name": "John", "age": 25}
        template = "User {name} is {age} years old"

        result = flow_engine._format_preview(template, context)
        assert result == "User John is 25 years old"

    def test_apply_output_mapping_simple(self, flow_engine):
        """Test simple output mapping."""
        answers = {"name": "John", "age": 25}
        mapping = {"user_name": "name", "user_age": "age"}

        result = flow_engine._apply_output_mapping(answers, mapping)
        assert result == {"user_name": "John", "user_age": 25}

    def test_apply_output_mapping_nested(self, flow_engine):
        """Test nested output mapping."""
        answers = {"name": "John", "email": "john@example.com", "subscribe": True}
        mapping = {
            "user": {"name": "name", "email": "email"},
            "preferences": {"newsletter": "subscribe"},
        }

        result = flow_engine._apply_output_mapping(answers, mapping)
        expected = {
            "user": {"name": "John", "email": "john@example.com"},
            "preferences": {"newsletter": True},
        }
        assert result == expected

    @patch("questionary.print")
    def test_execute_flow_with_mocks(
        self, mock_print, flow_engine, sample_flow_file, mock_responses
    ):
        """Test flow execution with mock responses."""
        result = flow_engine.execute_flow("test_flow", mock_responses=mock_responses)

        # Should contain mapped output
        assert "user" in result
        assert "preferences" in result
        assert result["user"]["name"] == "Test User"
        assert result["user"]["email"] == "test@example.com"
        assert result["preferences"]["newsletter"] is True

        # Should have printed flow header
        mock_print.assert_called()

    def test_build_question_text(self, flow_engine):
        """Test building text question."""
        step = {
            "id": "test",
            "type": "text",
            "message": "Enter text:",
            "default": "default_value",
            "instruction": "Help text",
        }
        context = {}

        question = flow_engine._build_question(step, context)
        assert question is not None
        # Can't easily test questionary internals, but verify it was created

    def test_build_question_select(self, flow_engine):
        """Test building select question."""
        step = {
            "id": "test",
            "type": "select",
            "message": "Choose option:",
            "choices": ["Option 1", "Option 2", "Option 3"],
            "default": "Option 1",
        }
        context = {}

        question = flow_engine._build_question(step, context)
        assert question is not None

    def test_build_question_confirm(self, flow_engine):
        """Test building confirm question."""
        step = {
            "id": "test",
            "type": "confirm",
            "message": "Confirm action?",
            "default": True,
        }
        context = {}

        question = flow_engine._build_question(step, context)
        assert question is not None

    def test_build_question_password(self, flow_engine):
        """Test building password question."""
        step = {
            "id": "test",
            "type": "password",
            "message": "Enter password:",
            "instruction": "At least 8 characters",
        }
        context = {}

        question = flow_engine._build_question(step, context)
        assert question is not None

    def test_validators_required(self, flow_engine):
        """Test required validator."""
        validator = flow_engine.validators["required"]

        assert validator("test") is True

        with pytest.raises(Exception):  # ValidationError
            validator("")

        with pytest.raises(Exception):  # ValidationError
            validator("   ")

    def test_validators_email(self, flow_engine):
        """Test email validator."""
        validator = flow_engine.validators["email"]

        assert validator("test@example.com") is True
        assert validator("") is True  # Allow empty for optional fields

        with pytest.raises(Exception):  # ValidationError
            validator("invalid-email")

    def test_validators_integer(self, flow_engine):
        """Test integer validator."""
        validator = flow_engine.validators["integer"]

        assert validator("123") is True
        assert validator("0") is True
        assert validator("") is True  # Allow empty for optional fields

        with pytest.raises(Exception):  # ValidationError
            validator("not-a-number")

    def test_validators_password_length(self, flow_engine):
        """Test password length validator."""
        validator = flow_engine.validators["password_length"]

        assert validator("12345678") is True
        assert validator("verylongpassword") is True

        with pytest.raises(Exception):  # ValidationError
            validator("short")

    def test_load_flow_invalid_yaml(self, flow_engine, temp_flows_dir):
        """Test loading flow with invalid YAML."""
        # Create invalid YAML file
        invalid_yaml = temp_flows_dir / "invalid.yml"
        with open(invalid_yaml, "w") as f:
            f.write("invalid: yaml: content: [")

        with pytest.raises(FlowValidationError, match="Invalid YAML"):
            flow_engine._load_flow("invalid")

    def test_execute_flow_validation_error(
        self, flow_engine, temp_flows_dir, invalid_flow_definition
    ):
        """Test flow execution with validation errors."""
        # Create flow file with validation errors
        flow_path = temp_flows_dir / "invalid_flow.yml"
        with open(flow_path, "w") as f:
            yaml.dump(invalid_flow_definition, f)

        with pytest.raises(FlowValidationError):
            flow_engine.execute_flow("invalid_flow")
