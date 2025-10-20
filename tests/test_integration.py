"""Integration tests for complete workflows."""

import pytest
import yaml
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from tui_form_designer import FlowEngine, QuestionaryUI
from tui_form_designer.core.exceptions import FlowValidationError, FlowExecutionError


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""

    def test_complete_survey_workflow(self, temp_flows_dir):
        """Test complete survey creation and execution workflow."""
        # Create survey flow
        survey_flow = {
            "flow_id": "customer_survey",
            "title": "Customer Satisfaction Survey",
            "description": "Help us improve our service",
            "icon": "📋",
            "steps": [
                {
                    "id": "customer_name",
                    "type": "text",
                    "message": "Your name:",
                    "validate": "required",
                },
                {
                    "id": "satisfaction_level",
                    "type": "select",
                    "message": "Satisfaction level:",
                    "choices": [
                        "Very Satisfied",
                        "Satisfied",
                        "Neutral",
                        "Dissatisfied",
                    ],
                    "default": "Satisfied",
                },
                {
                    "id": "feedback",
                    "type": "text",
                    "message": "Additional feedback:",
                    "instruction": "Optional - help us improve",
                },
                {
                    "id": "follow_up",
                    "type": "confirm",
                    "message": "May we contact you for follow-up?",
                    "default": False,
                },
                {
                    "id": "contact_method",
                    "type": "select",
                    "message": "Preferred contact method:",
                    "choices": ["Email", "Phone", "SMS"],
                    "condition": "follow_up == true",
                },
            ],
            "output_mapping": {
                "customer": {
                    "name": "customer_name",
                    "satisfaction": "satisfaction_level",
                    "feedback": "feedback",
                },
                "contact": {"allow_followup": "follow_up", "method": "contact_method"},
            },
        }

        # Save flow
        flow_path = temp_flows_dir / "customer_survey.yml"
        with open(flow_path, "w") as f:
            yaml.dump(survey_flow, f)

        # Test execution with mock responses
        engine = FlowEngine(flows_dir=str(temp_flows_dir))
        mock_responses = {
            "customer_name": "John Doe",
            "satisfaction_level": "Very Satisfied",
            "feedback": "Great service!",
            "follow_up": True,
            "contact_method": "Email",
        }

        result = engine.execute_flow("customer_survey", mock_responses=mock_responses)

        # Verify structured output
        assert result["customer"]["name"] == "John Doe"
        assert result["customer"]["satisfaction"] == "Very Satisfied"
        assert result["customer"]["feedback"] == "Great service!"
        assert result["contact"]["allow_followup"] is True
        assert result["contact"]["method"] == "Email"

    def test_application_configuration_workflow(self, temp_flows_dir):
        """Test application configuration workflow with conditional logic."""
        config_flow = {
            "flow_id": "app_config",
            "title": "Application Configuration",
            "description": "Configure your application settings",
            "steps": [
                {
                    "id": "app_name",
                    "type": "text",
                    "message": "Application name:",
                    "validate": "required",
                    "default": "MyApp",
                },
                {
                    "id": "environment",
                    "type": "select",
                    "message": "Environment:",
                    "choices": ["development", "staging", "production"],
                    "default": "development",
                },
                {
                    "id": "debug_mode",
                    "type": "confirm",
                    "message": "Enable debug mode?",
                    "default": True,
                    "condition": "environment == development",
                },
                {
                    "id": "database_url",
                    "type": "text",
                    "message": "Database URL:",
                    "validate": "required",
                    "default": "postgresql://localhost/myapp",
                },
                {
                    "id": "ssl_required",
                    "type": "confirm",
                    "message": "Require SSL?",
                    "default": True,
                    "condition": "environment == production",
                },
                {
                    "id": "admin_email",
                    "type": "text",
                    "message": "Administrator email:",
                    "validate": "email",
                },
            ],
            "output_mapping": {
                "app": {
                    "name": "app_name",
                    "environment": "environment",
                    "debug": "debug_mode",
                },
                "database": {"url": "database_url"},
                "security": {"ssl_required": "ssl_required"},
                "admin": {"email": "admin_email"},
            },
        }

        # Save flow
        flow_path = temp_flows_dir / "app_config.yml"
        with open(flow_path, "w") as f:
            yaml.dump(config_flow, f)

        # Test development environment
        engine = FlowEngine(flows_dir=str(temp_flows_dir))
        dev_responses = {
            "app_name": "DevApp",
            "environment": "development",
            "debug_mode": True,
            "database_url": "sqlite:///dev.db",
            "admin_email": "admin@dev.com",
        }

        result = engine.execute_flow("app_config", mock_responses=dev_responses)

        assert result["app"]["name"] == "DevApp"
        assert result["app"]["environment"] == "development"
        assert result["app"]["debug"] is True
        assert "ssl_required" not in result.get(
            "security", {}
        )  # Conditional step not executed

        # Test production environment
        prod_responses = {
            "app_name": "ProdApp",
            "environment": "production",
            "database_url": "postgresql://prod-server/app",
            "ssl_required": True,
            "admin_email": "admin@prod.com",
        }

        result = engine.execute_flow("app_config", mock_responses=prod_responses)

        assert result["app"]["name"] == "ProdApp"
        assert result["app"]["environment"] == "production"
        assert "debug" not in result.get(
            "app", {}
        )  # Debug step not executed in production
        assert result["security"]["ssl_required"] is True

    def test_validation_workflow(self, temp_flows_dir):
        """Test validation workflow with various input types."""
        validation_flow = {
            "flow_id": "validation_test",
            "title": "Validation Test",
            "description": "Test input validation",
            "steps": [
                {
                    "id": "required_field",
                    "type": "text",
                    "message": "Required field:",
                    "validate": "required",
                },
                {
                    "id": "email_field",
                    "type": "text",
                    "message": "Email address:",
                    "validate": "email",
                },
                {
                    "id": "number_field",
                    "type": "text",
                    "message": "Number:",
                    "validate": "integer",
                },
                {
                    "id": "password_field",
                    "type": "password",
                    "message": "Password:",
                    "validate": "password_length",
                },
            ],
        }

        # Save flow
        flow_path = temp_flows_dir / "validation_test.yml"
        with open(flow_path, "w") as f:
            yaml.dump(validation_flow, f)

        # Test with valid inputs
        engine = FlowEngine(flows_dir=str(temp_flows_dir))
        valid_responses = {
            "required_field": "Valid input",
            "email_field": "user@example.com",
            "number_field": "42",
            "password_field": "SecurePassword123",
        }

        result = engine.execute_flow("validation_test", mock_responses=valid_responses)

        assert result["required_field"] == "Valid input"
        assert result["email_field"] == "user@example.com"
        assert result["number_field"] == "42"
        assert result["password_field"] == "SecurePassword123"

    def test_error_handling_workflow(self, temp_flows_dir):
        """Test error handling in various scenarios."""
        # Test with invalid flow definition
        invalid_flow = {
            "flow_id": "invalid_test",
            "title": "Invalid Test",
            "steps": [
                {
                    # Missing required fields
                    "type": "invalid_type",
                    "message": "Invalid step",
                }
            ],
        }

        flow_path = temp_flows_dir / "invalid_test.yml"
        with open(flow_path, "w") as f:
            yaml.dump(invalid_flow, f)

        engine = FlowEngine(flows_dir=str(temp_flows_dir))

        # Should raise validation error
        with pytest.raises(FlowValidationError):
            engine.execute_flow("invalid_test")

    def test_complex_nested_mapping_workflow(self, temp_flows_dir):
        """Test complex nested output mapping."""
        complex_flow = {
            "flow_id": "complex_mapping",
            "title": "Complex Mapping Test",
            "steps": [
                {"id": "user_name", "type": "text", "message": "Name:"},
                {"id": "user_email", "type": "text", "message": "Email:"},
                {"id": "company_name", "type": "text", "message": "Company:"},
                {
                    "id": "company_size",
                    "type": "select",
                    "message": "Size:",
                    "choices": ["Small", "Medium", "Large"],
                },
                {"id": "contact_phone", "type": "text", "message": "Phone:"},
                {"id": "contact_email_ok", "type": "confirm", "message": "Email OK?"},
                {
                    "id": "newsletter_signup",
                    "type": "confirm",
                    "message": "Newsletter?",
                },
            ],
            "output_mapping": {
                "profile": {
                    "personal": {"name": "user_name", "email": "user_email"},
                    "company": {"name": "company_name", "size": "company_size"},
                },
                "contact_preferences": {
                    "phone": "contact_phone",
                    "email_ok": "contact_email_ok",
                    "newsletter": "newsletter_signup",
                },
            },
        }

        flow_path = temp_flows_dir / "complex_mapping.yml"
        with open(flow_path, "w") as f:
            yaml.dump(complex_flow, f)

        engine = FlowEngine(flows_dir=str(temp_flows_dir))
        responses = {
            "user_name": "John Doe",
            "user_email": "john@example.com",
            "company_name": "ACME Corp",
            "company_size": "Medium",
            "contact_phone": "555-1234",
            "contact_email_ok": True,
            "newsletter_signup": False,
        }

        result = engine.execute_flow("complex_mapping", mock_responses=responses)

        # Verify deeply nested structure
        assert result["profile"]["personal"]["name"] == "John Doe"
        assert result["profile"]["personal"]["email"] == "john@example.com"
        assert result["profile"]["company"]["name"] == "ACME Corp"
        assert result["profile"]["company"]["size"] == "Medium"
        assert result["contact_preferences"]["phone"] == "555-1234"
        assert result["contact_preferences"]["email_ok"] is True
        assert result["contact_preferences"]["newsletter"] is False

    def test_flow_discovery_and_execution(self, temp_flows_dir):
        """Test flow discovery and execution workflow."""
        # Create multiple flows
        flows = {
            "survey": {
                "flow_id": "survey",
                "title": "Survey",
                "steps": [{"id": "q1", "type": "text", "message": "Question 1:"}],
            },
            "config": {
                "flow_id": "config",
                "title": "Configuration",
                "steps": [{"id": "setting", "type": "text", "message": "Setting:"}],
            },
        }

        for flow_id, flow_def in flows.items():
            flow_path = temp_flows_dir / f"{flow_id}.yml"
            with open(flow_path, "w") as f:
                yaml.dump(flow_def, f)

        engine = FlowEngine(flows_dir=str(temp_flows_dir))

        # Test flow discovery
        available_flows = engine.get_available_flows()
        assert "survey" in available_flows
        assert "config" in available_flows
        assert len(available_flows) == 2

        # Test execution of discovered flows
        result = engine.execute_flow("survey", mock_responses={"q1": "Answer 1"})
        assert result["q1"] == "Answer 1"

        result = engine.execute_flow("config", mock_responses={"setting": "Value 1"})
        assert result["setting"] == "Value 1"


class TestPerformanceAndReliability:
    """Test performance and reliability aspects."""

    def test_large_flow_performance(self, temp_flows_dir):
        """Test performance with large flows."""
        # Create flow with many steps
        large_flow = {"flow_id": "large_flow", "title": "Large Flow Test", "steps": []}

        # Generate 50 steps
        for i in range(50):
            step = {
                "id": f"step_{i}",
                "type": "text",
                "message": f"Step {i}:",
                "default": f"default_{i}",
            }
            large_flow["steps"].append(step)

        flow_path = temp_flows_dir / "large_flow.yml"
        with open(flow_path, "w") as f:
            yaml.dump(large_flow, f)

        # Generate mock responses
        mock_responses = {f"step_{i}": f"response_{i}" for i in range(50)}

        engine = FlowEngine(flows_dir=str(temp_flows_dir))

        # Measure execution time
        import time

        start_time = time.time()
        result = engine.execute_flow("large_flow", mock_responses=mock_responses)
        execution_time = time.time() - start_time

        # Should complete quickly (under 1 second even with 50 steps)
        assert execution_time < 1.0
        assert len(result) == 50

        # Verify all responses are present
        for i in range(50):
            assert result[f"step_{i}"] == f"response_{i}"

    def test_malformed_yaml_handling(self, temp_flows_dir):
        """Test handling of malformed YAML files."""
        # Create file with malformed YAML
        malformed_path = temp_flows_dir / "malformed.yml"
        with open(malformed_path, "w") as f:
            f.write(
                """
            flow_id: test
            title: Test
            steps:
              - id: step1
                type: text
                message: "Unclosed quote
                invalid: [yaml content
            """
            )

        engine = FlowEngine(flows_dir=str(temp_flows_dir))

        with pytest.raises(FlowValidationError, match="Invalid YAML"):
            engine.execute_flow("malformed")

    def test_memory_usage_with_many_flows(self, temp_flows_dir):
        """Test memory usage with many flow files."""
        # Create many small flows
        for i in range(100):
            flow = {
                "flow_id": f"flow_{i}",
                "title": f"Flow {i}",
                "steps": [
                    {"id": "step1", "type": "text", "message": f"Step in flow {i}:"}
                ],
            }

            flow_path = temp_flows_dir / f"flow_{i}.yml"
            with open(flow_path, "w") as f:
                yaml.dump(flow, f)

        engine = FlowEngine(flows_dir=str(temp_flows_dir))

        # Should be able to discover all flows efficiently
        available_flows = engine.get_available_flows()
        assert len(available_flows) == 100

        # Should be able to execute flows without memory issues
        for i in range(0, 100, 10):  # Test every 10th flow
            result = engine.execute_flow(
                f"flow_{i}", mock_responses={"step1": f"response_{i}"}
            )
            assert result["step1"] == f"response_{i}"
