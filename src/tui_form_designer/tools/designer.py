#!/usr/bin/env python3
"""
Interactive Flow Designer Tool
Create and edit YAML flows using Questionary interface.
"""

import questionary
from questionary import Style
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import sys
from datetime import datetime

from ..core.flow_engine import FlowEngine
from ..core.exceptions import FlowValidationError
from ..ui.questionary_ui import QuestionaryUI


class InteractiveFlowDesigner:
    """Interactive tool for designing and editing YAML flows."""

    def __init__(self, flows_dir: str = "flows"):
        self.flows_dir = Path(flows_dir)
        self.flows_dir.mkdir(exist_ok=True)
        self.ui = QuestionaryUI()
        self.flow_engine = FlowEngine(flows_dir=flows_dir)

        # Available step types and their configurations
        self.step_types = {
            "text": {
                "name": "Text Input",
                "description": "Single line text input with optional validation",
                "required_fields": ["id", "message"],
                "optional_fields": ["default", "instruction", "validate"],
            },
            "select": {
                "name": "Single Selection",
                "description": "Choose one option from a list",
                "required_fields": ["id", "message", "choices"],
                "optional_fields": ["default", "instruction"],
            },
            "confirm": {
                "name": "Yes/No Confirmation",
                "description": "Boolean confirmation prompt",
                "required_fields": ["id", "message"],
                "optional_fields": ["default", "instruction"],
            },
            "password": {
                "name": "Password Input",
                "description": "Secure password input field",
                "required_fields": ["id", "message"],
                "optional_fields": ["instruction", "validate"],
            },
        }

        self.validators = ["required", "email", "domain", "integer", "password_length"]

    def run(self):
        """Run the interactive flow designer."""
        self.ui.show_title("Interactive Flow Designer", "🎨")
        self.ui.show_info("Design and edit YAML flows using an interactive interface")

        while True:
            action = self.ui.select(
                "What would you like to do?",
                choices=[
                    "Create New Flow",
                    "Edit Existing Flow",
                    "Test Flow",
                    "List All Flows",
                    "Validate Flow",
                    "Exit",
                ],
            )

            try:
                if action == "Create New Flow":
                    self.create_new_flow()
                elif action == "Edit Existing Flow":
                    self.edit_existing_flow()
                elif action == "Test Flow":
                    self.test_flow()
                elif action == "List All Flows":
                    self.list_flows()
                elif action == "Validate Flow":
                    self.validate_flow()
                elif action == "Exit":
                    self.ui.show_info("Goodbye! 👋")
                    break
            except KeyboardInterrupt:
                self.ui.show_warning("Operation cancelled")
                continue
            except Exception as e:
                self.ui.show_error(f"Error: {e}")
                continue

    def create_new_flow(self):
        """Create a new flow interactively."""
        self.ui.show_phase_header("Creating New Flow", "✨")

        # Basic flow information
        layout_id = (
            self.ui.prompt("Layout ID (filename without .yml):", allow_empty=False)
            .lower()
            .replace(" ", "_")
        )

        title = self.ui.prompt("Flow Title:", allow_empty=False)
        description = self.ui.prompt("Description (optional):")
        icon = self.ui.prompt("Icon (emoji, optional):", default="🔧")

        # Create flow structure
        flow_def = {
            "layout_id": layout_id,
            "title": title,
            "description": description,
            "icon": icon,
            "steps": [],
        }

        # Add steps
        self.ui.show_section_header(f"Adding steps to '{title}'", "📝")
        while self.ui.confirm("Add a step?"):
            step = self.create_step()
            if step:
                flow_def["steps"].append(step)
                self.ui.show_success(f"Added step: {step['id']}")

        # Configure output mapping
        if self.ui.confirm("Configure output mapping?"):
            output_mapping = self.create_output_mapping(flow_def["steps"])
            if output_mapping:
                flow_def["output_mapping"] = output_mapping

        # Save flow
        flow_path = self.flows_dir / f"{layout_id}.yml"
        try:
            with open(flow_path, "w") as f:
                yaml.dump(flow_def, f, default_flow_style=False, sort_keys=False)
            self.ui.show_success(f"Flow '{layout_id}' created successfully!")
        except Exception as e:
            self.ui.show_error(f"Failed to save flow: {e}")

    def edit_existing_flow(self):
        """Edit an existing flow."""
        flows = self.flow_engine.get_available_flows()
        if not flows:
            self.ui.show_error("No flows found")
            return

        flow_id = self.ui.select("Select flow to edit:", flows)
        # Load and edit flow (simplified implementation)
        self.ui.show_info(f"Editing flow: {flow_id}")
        self.ui.show_warning("Edit functionality coming soon - use text editor for now")

    def test_flow(self):
        """Test an existing flow."""
        flows = self.flow_engine.get_available_flows()
        if not flows:
            self.ui.show_error("No flows found")
            return

        flow_id = self.ui.select("Select flow to test:", flows)

        self.ui.show_phase_header(f"Testing Flow: {flow_id}", "🧪")
        try:
            results = self.flow_engine.execute_flow(flow_id)
            self.ui.show_success("Flow execution completed!")
            self.ui.show_section_header("Results", "📊")
            for key, value in results.items():
                self.ui.show_info(f"{key}: {value}")
        except Exception as e:
            self.ui.show_error(f"Flow test failed: {e}")

    def list_flows(self):
        """List all available flows."""
        flows = self.flow_engine.get_available_flows()
        if not flows:
            self.ui.show_error("No flows found")
            return

        self.ui.show_section_header("Available Flows", "📁")
        for flow_id in flows:
            try:
                flow_path = self.flows_dir / f"{flow_id}.yml"
                with open(flow_path, "r") as f:
                    flow_def = yaml.safe_load(f)
                title = flow_def.get("title", flow_id)
                description = flow_def.get("description", "No description")
                icon = flow_def.get("icon", "📄")
                steps_count = len(flow_def.get("steps", []))

                self.ui.show_info(f"{icon} {title} ({flow_id})")
                self.ui.show_step(f"{description} - {steps_count} steps")
            except Exception as e:
                self.ui.show_error(f"Error reading {flow_id}: {e}")

    def validate_flow(self):
        """Validate an existing flow."""
        flows = self.flow_engine.get_available_flows()
        if not flows:
            self.ui.show_error("No flows found")
            return

        flow_id = self.ui.select("Select flow to validate:", flows)

        try:
            flow_path = self.flows_dir / f"{flow_id}.yml"
            with open(flow_path, "r") as f:
                flow_def = yaml.safe_load(f)

            errors = self.flow_engine.validate_flow(flow_def)
            if not errors:
                self.ui.show_success(f"Flow '{flow_id}' is valid! ✨")
            else:
                self.ui.show_error(f"Flow '{flow_id}' has validation errors:")
                for error in errors:
                    self.ui.show_step(error)
        except Exception as e:
            self.ui.show_error(f"Failed to validate flow: {e}")

    def create_step(self) -> Optional[Dict[str, Any]]:
        """Create a step interactively."""
        # Select step type
        step_type_names = [
            f"{info['name']} - {info['description']}"
            for info in self.step_types.values()
        ]
        selected = self.ui.select("Step type:", step_type_names)

        # Find the actual step type
        step_type = None
        for key, info in self.step_types.items():
            if selected.startswith(info["name"]):
                step_type = key
                break

        if not step_type:
            return None

        step = {"type": step_type}

        # Get required fields
        step["id"] = self.ui.prompt("Step ID:", allow_empty=False)
        if step_type != "computed":
            step["message"] = self.ui.prompt("Question/Message:", allow_empty=False)

        # Handle choices for select type
        if step_type == "select":
            choices = []
            self.ui.show_info("Enter choices (press Enter on empty choice to finish):")
            while True:
                choice = self.ui.prompt("Choice:", allow_empty=True)
                if not choice:
                    break
                choices.append(choice)
            step["choices"] = choices

        # Optional fields
        if self.ui.confirm("Add default?"):
            default = self.ui.prompt("Default value:")
            if step_type == "confirm":
                default = default.lower() in ("y", "yes", "true", "1")
            step["default"] = default

        if self.ui.confirm("Add instruction?"):
            step["instruction"] = self.ui.prompt("Instruction (help text):")

        if self.ui.confirm("Add validation?"):
            validator = self.ui.select("Validator:", self.validators)
            step["validate"] = validator

        if self.ui.confirm("Add condition?"):
            step["condition"] = self.ui.prompt(
                "Condition (e.g., 'other_field == true'):"
            )

        return step

    def create_output_mapping(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create output mapping for steps."""
        self.ui.show_section_header("Configuring Output Mapping", "🗂️")
        self.ui.show_info("Map step responses to final output structure")

        mapping = {}
        for step in steps:
            if step["type"] == "computed":
                continue

            if self.ui.confirm(f"Map '{step['id']}' to output?"):
                output_key = self.ui.prompt(
                    f"Map '{step['id']}' to:", default=step["id"]
                )
                mapping[step["id"]] = output_key

        return mapping


def main():
    """Main entry point for the flow designer."""
    import argparse

    parser = argparse.ArgumentParser(description="Interactive Flow Designer")
    parser.add_argument(
        "--flows-dir", default="flows", help="Directory containing flow files"
    )
    parser.add_argument("--flow", help="Specific flow to work with")

    args = parser.parse_args()

    designer = InteractiveFlowDesigner(flows_dir=args.flows_dir)
    if args.flow:
        # Direct flow operations could be added here
        pass

    designer.run()


if __name__ == "__main__":
    main()
