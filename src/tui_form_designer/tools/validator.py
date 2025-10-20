#!/usr/bin/env python3
"""
Flow Validator Tool
Validate YAML flow definitions for syntax and logic errors.
"""

import yaml
from pathlib import Path
import sys
from typing import List, Dict, Any
import argparse

from ..core.flow_engine import FlowEngine
from ..core.exceptions import FlowValidationError
from ..ui.questionary_ui import QuestionaryUI


class FlowValidator:
    """Validate flow definitions."""

    def __init__(self, flows_dir: str = "flows", strict: bool = True):
        """
        Initialize validator.

        Args:
            flows_dir: Directory containing flow files
            strict: Enable production-ready validation (catches incomplete development)
                   DEFAULT: True (no backward compatibility)
        """
        self.flows_dir = Path(flows_dir)
        self.flow_engine = FlowEngine(flows_dir=flows_dir)
        self.ui = QuestionaryUI()
        self.strict = strict

    def validate_all_flows(self) -> bool:
        """Validate all flows in the flows directory."""
        if not self.flows_dir.exists():
            self.ui.show_error(f"Flows directory not found: {self.flows_dir}")
            return False

        flow_files = list(self.flows_dir.glob("*.yml"))
        if not flow_files:
            self.ui.show_warning("No flow files found")
            return True

        self.ui.show_title("Flow Validation", "🔍")

        all_valid = True
        for flow_file in flow_files:
            valid = self.validate_flow_file(flow_file)
            if not valid:
                all_valid = False

        if all_valid:
            self.ui.show_success(f"All {len(flow_files)} flows are valid! ✨")
        else:
            self.ui.show_error("Some flows have validation errors")

        return all_valid

    def validate_flow_file(self, flow_path: Path) -> bool:
        """Validate a single flow file."""
        self.ui.show_section_header(f"Validating: {flow_path.name}")

        try:
            # Validate encoding first
            encoding_errors = self._validate_file_encoding(flow_path)
            if encoding_errors:
                for error in encoding_errors:
                    self.ui.show_error(error)
                return False

            # Load YAML with explicit UTF-8 encoding
            with open(flow_path, encoding="utf-8") as f:
                flow_content = f.read()
                flow_def = yaml.safe_load(flow_content)

            if not flow_def:
                self.ui.show_error("Empty or invalid YAML file")
                return False

            # Detect if this is a sublayout (fragment) or standalone flow
            is_sublayout = (
                "sublayout" in str(flow_path)
                or "subdefaults" in flow_content
                or ("sublayout_defaults" in flow_def and "layout_id" not in flow_def)
            )

            # Check for TODO comments in raw YAML (strict mode)
            if self.strict and "TODO" in flow_content:
                self.ui.show_warning(
                    "⚠️  TODO comments found in YAML - incomplete development"
                )

            # Validate using FlowEngine
            # Sublayouts don't need layout_id, so we validate differently
            if is_sublayout:
                errors = self._validate_sublayout(flow_def, flow_path)
            else:
                errors = self.flow_engine.validate_flow(flow_def, strict=self.strict)

                # Validate defaults file if specified
                if "defaults_file" in flow_def:
                    defaults_errors = self._validate_defaults_file(
                        flow_def["defaults_file"], flow_path
                    )
                    errors.extend(defaults_errors)

                # Validate referenced sublayouts
                if "steps" in flow_def:
                    sublayout_errors = self._validate_sublayout_references(
                        flow_def["steps"], flow_path
                    )
                    errors.extend(sublayout_errors)

            if not errors:
                layout_type = "sublayout" if is_sublayout else "flow"
                # Tests expect plain '✅ Valid' for flows
                if not is_sublayout:
                    self.ui.show_success("✅ Valid")
                else:
                    # Keep explicit message for sublayouts
                    self.ui.show_success("✅ Valid sublayout")
                return True
            else:
                error_type = "errors/warnings" if self.strict else "validation errors"
                self.ui.show_error(f"❌ {len(errors)} {error_type}:")
                for error in errors:
                    self.ui.show_step(f"• {error}")
                return False

        except yaml.YAMLError as e:
            self.ui.show_error(f"YAML syntax error: {e}")
            return False
        except Exception as e:
            self.ui.show_error(f"Validation error: {e}")
            return False

    def _validate_file_encoding(self, file_path: Path) -> List[str]:
        """
        Validate file encoding and detect problematic Unicode characters.

        Args:
            file_path: Path to the file to validate

        Returns:
            List of encoding-related error messages
        """
        errors = []

        try:
            # Try to read file without encoding specified (system default)
            with open(file_path) as f:
                content = f.read()
        except UnicodeDecodeError as e:
            errors.append(f"🔧 ENCODING ERROR: {e}")
            errors.append(
                "💡 Fix: Convert file to UTF-8 encoding or replace problematic Unicode characters"
            )

            # Try to read with UTF-8 to identify specific issues
            try:
                with open(file_path, encoding="utf-8", errors="replace") as f:
                    utf8_content = f.read()

                # Check for common problematic characters
                problematic_chars = {
                    """: "smart quote (U+2018) - replace with regular apostrophe '",
                    """: "smart quote (U+2019) - replace with regular apostrophe '",
                    """: 'smart quote (U+201C) - replace with regular quote "',
                    """: 'smart quote (U+201D) - replace with regular quote "',
                    "–": "en dash (U+2013) - replace with regular dash -",
                    "—": "em dash (U+2014) - replace with regular dash -",
                    "←": "left arrow (U+2190) - replace with <-",
                    "→": "right arrow (U+2192) - replace with ->",
                    "…": "ellipsis (U+2026) - replace with ...",
                }

                found_chars = []
                for char, description in problematic_chars.items():
                    if char in utf8_content:
                        # Find positions of the character
                        positions = [i for i, c in enumerate(utf8_content) if c == char]
                        found_chars.append(
                            f"   • {description} (found at positions: {positions[:3]}{'...' if len(positions) > 3 else ''})"
                        )

                if found_chars:
                    errors.append("🔍 PROBLEMATIC CHARACTERS FOUND:")
                    errors.extend(found_chars)

            except Exception as inner_e:
                errors.append(f"Unable to analyze file content: {inner_e}")

        except Exception as e:
            errors.append(f"File read error: {e}")

        return errors

    def _validate_sublayout(
        self, sublayout_def: Dict[str, Any], flow_path: Path = None
    ) -> List[str]:
        """
        Validate a sublayout (fragment used in modular forms).
        Sublayouts don't need layout_id but do need title and steps.

        Args:
            sublayout_def: Sublayout definition dictionary
            flow_path: Path to the sublayout file (for resolving relative paths)
        """
        errors = []

        # Required fields for sublayouts
        if "title" not in sublayout_def:
            errors.append("Missing required field: title")

        if "steps" not in sublayout_def:
            errors.append("Missing required field: steps")
        elif (
            not isinstance(sublayout_def["steps"], list)
            or len(sublayout_def["steps"]) == 0
        ):
            errors.append("'steps' must be a non-empty list")
        else:
            # Validate steps using same logic as FlowEngine
            step_ids = set()
            for i, step in enumerate(sublayout_def["steps"]):
                if "id" not in step:
                    errors.append(f"Step {i}: Missing 'id' field")
                elif step["id"] in step_ids:
                    errors.append(f"Step {i}: Duplicate step ID '{step['id']}'")
                else:
                    step_ids.add(step["id"])

                if "type" not in step:
                    errors.append(f"Step {i}: Missing 'type' field")
                elif step["type"] not in [
                    "text",
                    "select",
                    "multiselect",
                    "confirm",
                    "password",
                    "computed",
                    "info",
                ]:
                    errors.append(f"Step {i}: Invalid step type '{step['type']}'")

                # Message required for most types (not computed or info)
                if "message" not in step and step.get("type") not in [
                    "computed",
                    "info",
                ]:
                    errors.append(f"Step {i}: Missing 'message' field")

                # Validate select/multiselect choices
                if (
                    step.get("type") in ["select", "multiselect"]
                    and "choices" not in step
                ):
                    errors.append(
                        f"Step {i}: {step['type']} step missing 'choices' field"
                    )

        # Validate sublayout_defaults file if specified
        if "sublayout_defaults" in sublayout_def and flow_path:
            defaults_errors = self._validate_defaults_file(
                sublayout_def["sublayout_defaults"], flow_path
            )
            errors.extend(defaults_errors)

        # Production-ready validation (if strict mode)
        if self.strict and "steps" in sublayout_def:
            errors.extend(self._validate_production_ready_steps(sublayout_def["steps"]))

        return errors

    def _validate_production_ready_steps(
        self, steps: List[Dict[str, Any]]
    ) -> List[str]:
        """Check steps for production-readiness (placeholder patterns, etc.)."""
        warnings = []

        placeholder_patterns = [
            "example_",
            "test_",
            "placeholder_",
            "sample_",
            "demo_",
            "temp_",
            "mock_",
            "dummy_",
        ]
        generic_messages = [
            "Enter a value:",
            "Provide configuration input",
            "Enter text here",
        ]

        placeholder_count = 0
        for i, step in enumerate(steps):
            step_id = step.get("id", f"step_{i}")

            # Check for placeholder IDs
            if any(step_id.startswith(pattern) for pattern in placeholder_patterns):
                warnings.append(
                    f"Step {i} ({step_id}): Placeholder ID detected - not production-ready"
                )
                placeholder_count += 1

            # Check for generic messages
            message = step.get("message", "")
            if message in generic_messages:
                warnings.append(
                    f"Step {i} ({step_id}): Generic message '{message}' - needs customization"
                )

            # Check for generic instructions
            instruction = step.get("instruction", "")
            if instruction in ["Provide configuration input", "Enter your input"]:
                warnings.append(
                    f"Step {i} ({step_id}): Generic instruction '{instruction}' - needs customization"
                )

        # Check if form appears incomplete (minimal steps with placeholders)
        if placeholder_count > 0 and len(steps) == 1:
            warnings.append(
                f"Only {len(steps)} step with placeholder ID - form appears incomplete"
            )

        return warnings

    def _validate_defaults_file(
        self, defaults_path: str, layout_path: Path
    ) -> List[str]:
        """
        Validate that a defaults file exists and contains valid YAML.

        Args:
            defaults_path: Path to defaults file (relative to layout file)
            layout_path: Path to the layout file (for resolving relative paths)

        Returns:
            List of validation errors
        """
        errors = []

        # Resolve relative path from layout file location
        if layout_path:
            base_dir = layout_path.parent
            full_defaults_path = (base_dir / defaults_path).resolve()
        else:
            full_defaults_path = Path(defaults_path).resolve()

        # Check if file exists
        if not full_defaults_path.exists():
            errors.append(
                f"Defaults file not found: {defaults_path} (resolved to: {full_defaults_path})"
            )
            return errors

        # Validate encoding first
        encoding_errors = self._validate_file_encoding(full_defaults_path)
        if encoding_errors:
            errors.extend(
                [
                    f"Defaults file encoding issue in {defaults_path}: {error}"
                    for error in encoding_errors
                ]
            )
            return errors

        # Validate YAML syntax
        try:
            with open(full_defaults_path, encoding="utf-8") as f:
                defaults_content = yaml.safe_load(f)

            if defaults_content is None:
                errors.append(f"Defaults file is empty: {defaults_path}")
            elif not isinstance(defaults_content, dict):
                errors.append(
                    f"Defaults file must contain a dictionary/mapping: {defaults_path}"
                )

        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML in defaults file {defaults_path}: {e}")
        except Exception as e:
            errors.append(f"Error reading defaults file {defaults_path}: {e}")

        return errors

    def _validate_sublayout_references(
        self, steps: List[Dict[str, Any]], layout_path: Path
    ) -> List[str]:
        """
        Validate sublayout references in steps.

        Args:
            steps: List of step definitions
            layout_path: Path to the parent layout file

        Returns:
            List of validation errors
        """
        errors = []
        base_dir = layout_path.parent if layout_path else Path.cwd()

        for i, step in enumerate(steps):
            if "sublayout" in step:
                sublayout_path_str = step["sublayout"]
                sublayout_full_path = (base_dir / sublayout_path_str).resolve()

                # Check if sublayout file exists
                if not sublayout_full_path.exists():
                    errors.append(
                        f"Step {i}: Sublayout file not found: {sublayout_path_str} "
                        f"(resolved to: {sublayout_full_path})"
                    )
                    continue

                # Validate the sublayout file itself
                try:
                    with open(sublayout_full_path) as f:
                        sublayout_content = f.read()
                        sublayout_def = yaml.safe_load(sublayout_content)

                    if not sublayout_def:
                        errors.append(
                            f"Step {i}: Sublayout file is empty: {sublayout_path_str}"
                        )
                        continue

                    # Recursively validate the sublayout
                    sublayout_errors = self._validate_sublayout(
                        sublayout_def, sublayout_full_path
                    )

                    # Prefix errors with sublayout reference
                    for error in sublayout_errors:
                        errors.append(
                            f"Step {i} (sublayout {sublayout_path_str}): {error}"
                        )

                except yaml.YAMLError as e:
                    errors.append(
                        f"Step {i}: Invalid YAML in sublayout {sublayout_path_str}: {e}"
                    )
                except Exception as e:
                    errors.append(
                        f"Step {i}: Error reading sublayout {sublayout_path_str}: {e}"
                    )

        return errors

    def validate_specific_flows(self, flow_files: List[str]) -> bool:
        """Validate specific flow files."""
        self.ui.show_title("Flow Validation", "🔍")

        all_valid = True
        for flow_file in flow_files:
            flow_path = Path(flow_file)
            if not flow_path.exists():
                # Try in flows directory
                flow_path = self.flows_dir / flow_file
                if not flow_path.exists():
                    flow_path = self.flows_dir / f"{flow_file}.yml"

            if not flow_path.exists():
                self.ui.show_error(f"Flow file not found: {flow_file}")
                all_valid = False
                continue

            valid = self.validate_flow_file(flow_path)
            if not valid:
                all_valid = False

        return all_valid

    def interactive_validate(self):
        """Interactive flow validation."""
        flows = self.flow_engine.get_available_flows()
        if not flows:
            self.ui.show_error("No flows found")
            return

        self.ui.show_title("Interactive Flow Validation", "🔍")

        while True:
            action = self.ui.select(
                "What would you like to validate?",
                choices=["All flows", "Specific flow", "Exit"],
            )

            if action == "All flows":
                self.validate_all_flows()
            elif action == "Specific flow":
                flow_id = self.ui.select("Select flow to validate:", flows)
                flow_path = self.flows_dir / f"{flow_id}.yml"
                self.validate_flow_file(flow_path)
            elif action == "Exit":
                break


def main():
    """Main entry point for flow validation."""
    parser = argparse.ArgumentParser(
        description="Validate YAML flow definitions - STRICT MODE BY DEFAULT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Production-ready validation (DEFAULT - strict mode enabled)
  tui-designer validate

  # Validate specific files (strict by default)
  tui-designer validate my_form.yml

  # Disable strict mode for development (NOT RECOMMENDED)
  tui-designer validate --no-strict

  # Interactive mode
  tui-designer validate --interactive

Validation Modes:
  STRICT (DEFAULT): Production-readiness checks including:
  - Detection of TODO comments
  - Placeholder ID patterns (example_*, test_*, etc.)
  - Generic messages and instructions
  - Scaffolding template patterns

  Use --no-strict only during active development.
  Always use strict mode (default) before committing or deploying.
        """,
    )
    parser.add_argument("flows", nargs="*", help="Specific flow files to validate")
    parser.add_argument(
        "--flows-dir", default="flows", help="Directory containing flow files"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive mode"
    )
    parser.add_argument(
        "--strict",
        "-s",
        action="store_true",
        default=True,
        help="Enable strict production-ready validation (DEFAULT - always on unless --no-strict)",
    )
    parser.add_argument(
        "--no-strict",
        action="store_false",
        dest="strict",
        help="Disable strict mode (NOT RECOMMENDED - only for active development)",
    )
    parser.add_argument(
        "--production",
        "-p",
        action="store_true",
        help="Alias for --strict (redundant since strict is now default)",
    )

    args = parser.parse_args()

    # Strict mode is DEFAULT (args.strict defaults to True)
    # Only disabled if --no-strict is explicitly provided
    strict_mode = args.strict

    validator = FlowValidator(flows_dir=args.flows_dir, strict=strict_mode)

    if strict_mode:
        print("🔒 STRICT MODE (default) - Production-ready validation enabled")
        print("   Use --no-strict to disable (not recommended)")
    else:
        print("⚠️  DEVELOPMENT MODE - Strict validation disabled")
        print("   This mode should only be used during active development")

    if args.interactive:
        validator.interactive_validate()
        return 0

    if args.flows:
        success = validator.validate_specific_flows(args.flows)
    else:
        success = validator.validate_all_flows()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
