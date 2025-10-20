#!/usr/bin/env python3
"""
Flow Tester Tool
Test flow execution with mock responses and validation.
"""

import json
from pathlib import Path
import sys
from typing import Dict, Any, Optional
import argparse

from ..core.flow_engine import FlowEngine
from ..core.exceptions import FlowValidationError, FlowExecutionError
from ..ui.questionary_ui import QuestionaryUI


class FlowTester:
    """Test flow execution with various scenarios."""

    def __init__(self, flows_dir: str = "flows"):
        self.flows_dir = Path(flows_dir)
        self.ui = QuestionaryUI()
        self.flow_engine = FlowEngine(flows_dir=flows_dir)

    def test_flow(self, flow_id: str, mock_file: Optional[str] = None) -> bool:
        """Test a specific flow with optional mock responses."""
        self.ui.show_title(f"Testing Flow: {flow_id}", "🧪")

        # Load mock responses if provided
        mock_responses = {}
        if mock_file:
            try:
                with open(mock_file) as f:
                    mock_responses = json.load(f)
                self.ui.show_info(f"Loaded mock responses from {mock_file}")
            except Exception as e:
                self.ui.show_error(f"Failed to load mock file: {e}")
                return False

        try:
            # Execute the flow
            results = self.flow_engine.execute_flow(
                flow_id, mock_responses=mock_responses
            )

            self.ui.show_success("✅ Flow execution completed!")

            # Display results
            self.ui.show_section_header("Results", "📊")
            self._display_results(results)

            return True

        except FlowValidationError as e:
            self.ui.show_error(f"Flow validation failed: {e}")
            return False
        except FlowExecutionError as e:
            self.ui.show_error(f"Flow execution failed: {e}")
            return False
        except Exception as e:
            self.ui.show_error(f"Unexpected error: {e}")
            return False

    def test_all_flows(self) -> bool:
        """Test all flows with basic validation."""
        flows = self.flow_engine.get_available_flows()
        if not flows:
            self.ui.show_error("No flows found")
            return False

        self.ui.show_title("Testing All Flows", "🧪")

        all_passed = True
        for i, flow_id in enumerate(flows, 1):
            self.ui.show_progress(i, len(flows), f"Testing {flow_id}")

            try:
                # Just validate the flow without executing
                flow_path = self.flows_dir / f"{flow_id}.yml"
                import yaml

                with open(flow_path) as f:
                    flow_def = yaml.safe_load(f)

                errors = self.flow_engine.validate_flow(flow_def)
                if errors:
                    self.ui.show_error(f"❌ {flow_id}: Validation failed")
                    for error in errors:
                        self.ui.show_step(f"• {error}")
                    all_passed = False
                else:
                    self.ui.show_success(f"✅ {flow_id}: Valid")

            except Exception as e:
                self.ui.show_error(f"❌ {flow_id}: Error - {e}")
                all_passed = False

        if all_passed:
            self.ui.show_success(f"All {len(flows)} flows passed validation! 🎉")
        else:
            self.ui.show_error("Some flows failed validation")

        return all_passed

    def interactive_test(self):
        """Interactive flow testing."""
        flows = self.flow_engine.get_available_flows()
        if not flows:
            self.ui.show_error("No flows found")
            return

        self.ui.show_title("Interactive Flow Testing", "🧪")

        while True:
            action = self.ui.select(
                "What would you like to test?",
                choices=[
                    "Test specific flow",
                    "Test all flows (validation only)",
                    "Test with mock responses",
                    "Generate mock template",
                    "Exit",
                ],
            )

            if action == "Test specific flow":
                flow_id = self.ui.select("Select flow to test:", flows)
                self.test_flow(flow_id)

            elif action == "Test all flows (validation only)":
                self.test_all_flows()

            elif action == "Test with mock responses":
                flow_id = self.ui.select("Select flow to test:", flows)
                mock_file = self.ui.prompt(
                    "Mock responses file (JSON):", allow_empty=True
                )
                if mock_file and not Path(mock_file).exists():
                    self.ui.show_error(f"Mock file not found: {mock_file}")
                    continue
                self.test_flow(flow_id, mock_file)

            elif action == "Generate mock template":
                flow_id = self.ui.select("Select flow for mock template:", flows)
                self.generate_mock_template(flow_id)

            elif action == "Exit":
                break

    def generate_mock_template(self, flow_id: str):
        """Generate a mock response template for a flow."""
        try:
            flow_path = self.flows_dir / f"{flow_id}.yml"
            import yaml

            with open(flow_path) as f:
                flow_def = yaml.safe_load(f)

            mock_template = {}
            for step in flow_def.get("steps", []):
                if step.get("type") == "computed":
                    continue

                step_id = step["id"]
                step_type = step["type"]

                # Generate appropriate mock values
                if step_type == "text":
                    mock_template[step_id] = "sample_text"
                elif step_type == "select":
                    choices = step.get("choices", [])
                    if choices:
                        mock_template[step_id] = choices[0]
                    else:
                        mock_template[step_id] = "choice1"
                elif step_type == "confirm":
                    mock_template[step_id] = True
                elif step_type == "password":
                    mock_template[step_id] = "sample_password"
                else:
                    mock_template[step_id] = "sample_value"

            # Save template
            template_file = f"{flow_id}_mock_template.json"
            with open(template_file, "w") as f:
                json.dump(mock_template, f, indent=2)

            self.ui.show_success(f"Mock template generated: {template_file}")
            self.ui.show_info("Edit this file with your test values")

        except Exception as e:
            self.ui.show_error(f"Failed to generate mock template: {e}")

    def _display_results(self, results: Dict[str, Any], indent: int = 0):
        """Display results recursively."""
        prefix = "  " * indent

        for key, value in results.items():
            if isinstance(value, dict):
                self.ui.show_info(f"{prefix}{key}:")
                self._display_results(value, indent + 1)
            else:
                self.ui.show_info(f"{prefix}{key}: {value}")


def main():
    """Main entry point for flow testing."""
    parser = argparse.ArgumentParser(description="Test YAML flow execution")
    parser.add_argument("--flow", help="Specific flow to test")
    parser.add_argument("--mock-data", help="JSON file with mock responses")
    parser.add_argument(
        "--flows-dir", default="flows", help="Directory containing flow files"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive mode"
    )
    parser.add_argument("--all", action="store_true", help="Test all flows")

    args = parser.parse_args()

    tester = FlowTester(flows_dir=args.flows_dir)

    if args.interactive:
        tester.interactive_test()
        return 0

    if args.all:
        success = tester.test_all_flows()
        return 0 if success else 1

    if args.flow:
        success = tester.test_flow(args.flow, args.mock_data)
        return 0 if success else 1

    # Default to interactive mode
    tester.interactive_test()
    return 0


if __name__ == "__main__":
    sys.exit(main())
