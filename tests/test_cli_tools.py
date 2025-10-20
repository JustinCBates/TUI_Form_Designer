"""Tests for CLI tools integration."""

import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import json

from tui_form_designer.tools.validator import FlowValidator
from tui_form_designer.tools.tester import FlowTester
from tui_form_designer.tools.preview import FlowPreviewer
from tui_form_designer.tools.designer import InteractiveFlowDesigner


class TestFlowValidator:
    """Test suite for FlowValidator."""

    def test_init(self, temp_flows_dir):
        """Test FlowValidator initialization."""
        validator = FlowValidator(flows_dir=str(temp_flows_dir))
        assert validator.flows_dir == temp_flows_dir
        assert validator.ui is not None
        assert validator.flow_engine is not None

    def test_validate_flow_file_valid(self, temp_flows_dir, sample_flow_definition):
        """Test validating a valid flow file."""
        # Create valid flow file
        flow_path = temp_flows_dir / "valid_flow.yml"
        with open(flow_path, "w") as f:
            yaml.dump(sample_flow_definition, f)

        validator = FlowValidator(flows_dir=str(temp_flows_dir))
        with patch.object(validator.ui, "show_success") as mock_success:
            result = validator.validate_flow_file(flow_path)
            assert result is True
            mock_success.assert_called_with("✅ Valid")

    def test_validate_flow_file_invalid(self, temp_flows_dir, invalid_flow_definition):
        """Test validating an invalid flow file."""
        # Create invalid flow file
        flow_path = temp_flows_dir / "invalid_flow.yml"
        with open(flow_path, "w") as f:
            yaml.dump(invalid_flow_definition, f)

        validator = FlowValidator(flows_dir=str(temp_flows_dir))
        with patch.object(validator.ui, "show_error") as mock_error:
            result = validator.validate_flow_file(flow_path)
            assert result is False
            mock_error.assert_called()

    def test_validate_flow_file_yaml_error(self, temp_flows_dir):
        """Test validating a file with YAML syntax errors."""
        # Create file with invalid YAML
        flow_path = temp_flows_dir / "yaml_error.yml"
        with open(flow_path, "w") as f:
            f.write("invalid: yaml: [")

        validator = FlowValidator(flows_dir=str(temp_flows_dir))
        with patch.object(validator.ui, "show_error") as mock_error:
            result = validator.validate_flow_file(flow_path)
            assert result is False
            mock_error.assert_called()

    def test_validate_all_flows_empty(self, temp_flows_dir):
        """Test validating all flows in empty directory."""
        validator = FlowValidator(flows_dir=str(temp_flows_dir))
        with patch.object(validator.ui, "show_warning") as mock_warning:
            result = validator.validate_all_flows()
            assert result is True
            mock_warning.assert_called_with("No flow files found")

    def test_validate_all_flows_success(self, temp_flows_dir, sample_flow_definition):
        """Test validating all flows successfully."""
        # Create valid flow file
        flow_path = temp_flows_dir / "test_flow.yml"
        with open(flow_path, "w") as f:
            yaml.dump(sample_flow_definition, f)

        validator = FlowValidator(flows_dir=str(temp_flows_dir))
        with patch.object(validator.ui, "show_success") as mock_success:
            result = validator.validate_all_flows()
            assert result is True
            mock_success.assert_called()

    def test_validate_specific_flows(self, temp_flows_dir, sample_flow_definition):
        """Test validating specific flow files."""
        # Create flow file
        flow_path = temp_flows_dir / "test_flow.yml"
        with open(flow_path, "w") as f:
            yaml.dump(sample_flow_definition, f)

        validator = FlowValidator(flows_dir=str(temp_flows_dir))
        result = validator.validate_specific_flows(["test_flow.yml"])
        assert result is True

    def test_validate_specific_flows_not_found(self, temp_flows_dir):
        """Test validating non-existent flow files."""
        validator = FlowValidator(flows_dir=str(temp_flows_dir))
        with patch.object(validator.ui, "show_error") as mock_error:
            result = validator.validate_specific_flows(["nonexistent.yml"])
            assert result is False
            mock_error.assert_called()


class TestFlowTester:
    """Test suite for FlowTester."""

    def test_init(self, temp_flows_dir):
        """Test FlowTester initialization."""
        tester = FlowTester(flows_dir=str(temp_flows_dir))
        assert tester.flows_dir == temp_flows_dir
        assert tester.ui is not None
        assert tester.flow_engine is not None

    def test_test_flow_with_mocks(
        self, temp_flows_dir, sample_flow_definition, mock_responses
    ):
        """Test flow execution with mock responses."""
        # Create flow file
        flow_path = temp_flows_dir / "test_flow.yml"
        with open(flow_path, "w") as f:
            yaml.dump(sample_flow_definition, f)

        # Create mock file
        mock_file = temp_flows_dir / "mock_responses.json"
        with open(mock_file, "w") as f:
            json.dump(mock_responses, f)

        tester = FlowTester(flows_dir=str(temp_flows_dir))
        with patch.object(tester.ui, "show_success") as mock_success:
            result = tester.test_flow("test_flow", str(mock_file))
            assert result is True
            mock_success.assert_called()

    def test_test_flow_invalid_mock_file(self, temp_flows_dir, sample_flow_definition):
        """Test flow testing with invalid mock file."""
        # Create flow file
        flow_path = temp_flows_dir / "test_flow.yml"
        with open(flow_path, "w") as f:
            yaml.dump(sample_flow_definition, f)

        tester = FlowTester(flows_dir=str(temp_flows_dir))
        with patch.object(tester.ui, "show_error") as mock_error:
            result = tester.test_flow("test_flow", "nonexistent.json")
            assert result is False
            mock_error.assert_called()

    def test_generate_mock_template(self, temp_flows_dir, sample_flow_definition):
        """Test generating mock response template."""
        # Create flow file
        flow_path = temp_flows_dir / "test_flow.yml"
        with open(flow_path, "w") as f:
            yaml.dump(sample_flow_definition, f)

        tester = FlowTester(flows_dir=str(temp_flows_dir))

        # Change to temp directory to control where template is created
        import os

        original_cwd = os.getcwd()
        os.chdir(str(temp_flows_dir))

        try:
            with patch.object(tester.ui, "show_success") as mock_success:
                tester.generate_mock_template("test_flow")

                # Check template file was created
                template_file = Path("test_flow_mock_template.json")
                assert template_file.exists()

                # Verify template content
                with open(template_file) as f:
                    template = json.load(f)

                assert "name" in template
                assert "age" in template
                assert "email" in template
                assert "subscribe" in template

                mock_success.assert_called()
        finally:
            os.chdir(original_cwd)

    def test_test_all_flows(self, temp_flows_dir, sample_flow_definition):
        """Test validating all flows."""
        # Create flow file
        flow_path = temp_flows_dir / "test_flow.yml"
        with open(flow_path, "w") as f:
            yaml.dump(sample_flow_definition, f)

        tester = FlowTester(flows_dir=str(temp_flows_dir))
        with patch.object(tester.ui, "show_success") as mock_success:
            result = tester.test_all_flows()
            assert result is True
            mock_success.assert_called()


class TestFlowPreviewer:
    """Test suite for FlowPreviewer."""

    def test_init(self, temp_flows_dir):
        """Test FlowPreviewer initialization."""
        previewer = FlowPreviewer(flows_dir=str(temp_flows_dir))
        assert previewer.flows_dir == temp_flows_dir
        assert previewer.ui is not None
        assert previewer.flow_engine is not None

    def test_preview_flow(self, temp_flows_dir, sample_flow_definition):
        """Test previewing a flow."""
        # Create flow file
        flow_path = temp_flows_dir / "test_flow.yml"
        with open(flow_path, "w") as f:
            yaml.dump(sample_flow_definition, f)

        previewer = FlowPreviewer(flows_dir=str(temp_flows_dir))
        with patch.object(previewer.ui, "show_title") as mock_title, patch.object(
            previewer.ui, "show_info"
        ) as mock_info:
            previewer.preview_flow("test_flow")

            mock_title.assert_called()
            mock_info.assert_called()

    def test_preview_flow_not_found(self, temp_flows_dir):
        """Test previewing non-existent flow."""
        previewer = FlowPreviewer(flows_dir=str(temp_flows_dir))
        with patch.object(previewer.ui, "show_error") as mock_error:
            previewer.preview_flow("nonexistent")
            mock_error.assert_called_with("Flow not found: nonexistent")

    def test_preview_step(self, temp_flows_dir, sample_flow_definition):
        """Test previewing a specific step."""
        # Create flow file
        flow_path = temp_flows_dir / "test_flow.yml"
        with open(flow_path, "w") as f:
            yaml.dump(sample_flow_definition, f)

        previewer = FlowPreviewer(flows_dir=str(temp_flows_dir))
        with patch.object(previewer.ui, "show_title") as mock_title:
            previewer.preview_flow("test_flow", "name")
            mock_title.assert_called()

    def test_preview_step_not_found(self, temp_flows_dir, sample_flow_definition):
        """Test previewing non-existent step."""
        # Create flow file
        flow_path = temp_flows_dir / "test_flow.yml"
        with open(flow_path, "w") as f:
            yaml.dump(sample_flow_definition, f)

        previewer = FlowPreviewer(flows_dir=str(temp_flows_dir))
        with patch.object(previewer.ui, "show_error") as mock_error:
            previewer.preview_flow("test_flow", "nonexistent_step")
            mock_error.assert_called_with("Step not found: nonexistent_step")

    def test_list_flows(self, temp_flows_dir, sample_flow_definition):
        """Test listing all flows."""
        # Create flow file
        flow_path = temp_flows_dir / "test_flow.yml"
        with open(flow_path, "w") as f:
            yaml.dump(sample_flow_definition, f)

        previewer = FlowPreviewer(flows_dir=str(temp_flows_dir))
        with patch.object(previewer.ui, "show_title") as mock_title, patch.object(
            previewer.ui, "show_section_header"
        ) as mock_header:
            previewer.list_flows()

            mock_title.assert_called()
            mock_header.assert_called()

    def test_list_flows_empty(self, temp_flows_dir):
        """Test listing flows in empty directory."""
        previewer = FlowPreviewer(flows_dir=str(temp_flows_dir))
        with patch.object(previewer.ui, "show_error") as mock_error:
            previewer.list_flows()
            mock_error.assert_called_with("No flows found")


class TestInteractiveFlowDesigner:
    """Test suite for InteractiveFlowDesigner."""

    def test_init(self, temp_flows_dir):
        """Test InteractiveFlowDesigner initialization."""
        designer = InteractiveFlowDesigner(flows_dir=str(temp_flows_dir))
        assert designer.flows_dir == temp_flows_dir
        assert designer.ui is not None
        assert designer.flow_engine is not None
        assert isinstance(designer.step_types, dict)
        assert isinstance(designer.validators, list)

    def test_create_step_text(self, temp_flows_dir):
        """Test creating a text step."""
        designer = InteractiveFlowDesigner(flows_dir=str(temp_flows_dir))

        with patch.object(designer.ui, "select") as mock_select, patch.object(
            designer.ui, "prompt"
        ) as mock_prompt, patch.object(designer.ui, "confirm") as mock_confirm:

            # Mock user selections
            mock_select.return_value = (
                "Text Input - Single line text input with optional validation"
            )
            mock_prompt.side_effect = ["test_id", "Test message"]
            mock_confirm.side_effect = [
                False,
                False,
                False,
                False,
            ]  # No optional fields

            step = designer.create_step()

            assert step is not None
            assert step["type"] == "text"
            assert step["id"] == "test_id"
            assert step["message"] == "Test message"

    def test_create_step_select(self, temp_flows_dir):
        """Test creating a select step."""
        designer = InteractiveFlowDesigner(flows_dir=str(temp_flows_dir))

        with patch.object(designer.ui, "select") as mock_select, patch.object(
            designer.ui, "prompt"
        ) as mock_prompt, patch.object(designer.ui, "confirm") as mock_confirm:

            # Mock user selections
            mock_select.return_value = (
                "Single Selection - Choose one option from a list"
            )
            mock_prompt.side_effect = [
                "choice_id",
                "Choose option:",
                "Option 1",
                "Option 2",
                "",  # Choices, empty to finish
            ]
            mock_confirm.side_effect = [
                False,
                False,
                False,
                False,
            ]  # No optional fields

            step = designer.create_step()

            assert step is not None
            assert step["type"] == "select"
            assert step["id"] == "choice_id"
            assert step["choices"] == ["Option 1", "Option 2"]

    def test_create_output_mapping(self, temp_flows_dir):
        """Test creating output mapping."""
        designer = InteractiveFlowDesigner(flows_dir=str(temp_flows_dir))

        steps = [
            {"id": "name", "type": "text"},
            {"id": "email", "type": "text"},
            {"id": "computed_value", "type": "computed"},  # Should be skipped
        ]

        with patch.object(designer.ui, "confirm") as mock_confirm, patch.object(
            designer.ui, "prompt"
        ) as mock_prompt:

            # Mock confirmations for mapping steps
            mock_confirm.side_effect = [True, True]  # Map both non-computed steps
            mock_prompt.side_effect = ["user.name", "user.email"]

            mapping = designer.create_output_mapping(steps)

            assert mapping == {"name": "user.name", "email": "user.email"}


class TestCLIIntegration:
    """Test suite for CLI integration."""

    def test_cli_tools_importable(self):
        """Test that all CLI tools can be imported."""
        from tui_form_designer.tools import (
            cli,
            designer,
            validator,
            tester,
            preview,
            demo,
        )

        # All modules should be importable
        assert cli is not None
        assert designer is not None
        assert validator is not None
        assert tester is not None
        assert preview is not None
        assert demo is not None

    @patch("sys.argv", ["tui-designer", "--help"])
    def test_cli_help(self):
        """Test CLI help functionality."""
        from tui_form_designer.tools.cli import main

        with pytest.raises(SystemExit) as exc_info:
            main()

        # Help should exit with code 0
        assert exc_info.value.code == 0
