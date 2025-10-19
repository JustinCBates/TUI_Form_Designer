"""Flow engine for executing YAML-defined flows using Questionary."""

import signal
import sys
import questionary
from questionary import Style
import yaml
from typing import Dict, Any, Optional, List, Callable, Union
from pathlib import Path
import re
from .exceptions import FlowValidationError, FlowExecutionError


class FlowEngine:
    """Execute YAML-defined flows using Questionary."""

    def __init__(
        self,
        flows_dir: Optional[Union[str, Path]] = None,
        style: Optional[Style] = None,
        theme: str = "default",
    ):
        """
        Initialize FlowEngine.

        Args:
            flows_dir: Directory containing flow definition files
            style: Custom Questionary style
            theme: Pre-built theme name ('default', 'dark', 'minimal')
        """
        self.flows_dir = Path(flows_dir or "flows")
        self.style = style or self._get_theme_style(theme)
        self.validators = self._load_validators()
        self._exit_requested = False
        self._original_sigint_handler = None

    def _get_theme_style(self, theme: str) -> Style:
        """Get predefined theme styles."""
        themes = {
            "default": Style(
                [
                    ("question", "bold blue"),
                    ("answer", "fg:#ff9d00 bold"),
                    ("pointer", "fg:#673ab7 bold"),
                    ("highlighted", "fg:#673ab7 bold"),
                    ("selected", "fg:#cc5454"),
                    ("instruction", "italic"),
                ]
            ),
            "dark": Style(
                [
                    ("question", "bold cyan"),
                    ("answer", "fg:#00ff00 bold"),
                    ("pointer", "fg:#ff00ff bold"),
                    ("highlighted", "fg:#ff00ff bold"),
                    ("selected", "fg:#ffff00"),
                    ("instruction", "italic fg:#888888"),
                ]
            ),
            "minimal": Style(
                [
                    ("question", "bold"),
                    ("answer", "bold"),
                    ("pointer", "fg:#ffffff bold"),
                    ("highlighted", "bold"),
                    ("selected", "bold"),
                    ("instruction", "italic"),
                ]
            ),
        }
        return themes.get(theme, themes["default"])

    def get_available_flows(self) -> List[str]:
        """Get list of available flow IDs."""
        if not self.flows_dir.exists():
            return []

        flows = []
        for flow_file in self.flows_dir.glob("*.yml"):
            flows.append(flow_file.stem)
        return flows

    def _emergency_exit_handler(self, signum, frame):
        """Handle double Ctrl+C for emergency exit."""
        if self._exit_requested:
            questionary.print("\\n🚨 EMERGENCY EXIT - Force quitting...", style="bold red")
            sys.exit(130)  # Standard exit code for SIGINT
        else:
            self._exit_requested = True
            questionary.print(
                "\\n⚠️  Exit requested. Press Ctrl+C again within 2 seconds to force quit.",
                style="bold yellow"
            )
            raise KeyboardInterrupt()

    def execute_flow(
        self,
        flow_id: str,
        context: Optional[Dict[str, Any]] = None,
        mock_responses: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a flow by ID with optional context and mock responses.

        Args:
            flow_id: ID of the flow to execute
            context: Initial context variables
            mock_responses: Mock responses for testing (maps step_id -> response)

        Returns:
            Dictionary containing flow results
        """
        # Install emergency exit handler
        self._exit_requested = False
        self._original_sigint_handler = signal.signal(signal.SIGINT, self._emergency_exit_handler)

        try:
            return self._execute_flow_internal(flow_id, context, mock_responses)
        finally:
            # Restore original signal handler
            if self._original_sigint_handler is not None:
                signal.signal(signal.SIGINT, self._original_sigint_handler)

    def _execute_flow_internal(
        self,
        flow_id: str,
        context: Optional[Dict[str, Any]] = None,
        mock_responses: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Internal flow execution logic."""
        flow_def = self._load_flow(flow_id)
        context = context or {}
        mock_responses = mock_responses or {}

        # Validate flow definition
        self.validate_flow(flow_def)

        # Show flow header
        questionary.print(
            f"\\n{flow_def.get('icon', '🔧')} {flow_def['title']}", style="bold blue"
        )
        if flow_def.get("description"):
            questionary.print(f"   {flow_def['description']}", style="italic")

        # Execute steps sequentially to handle conditional logic
        answers = {}

        for step in flow_def["steps"]:
            if step["type"] == "computed":
                # Handle computed values
                if "compute" in step:
                    computed_value = self._evaluate_expression(
                        step["compute"], {**context, **answers}
                    )
                    answers[step["id"]] = computed_value
                continue

            # Check if step should be shown
            if not self._should_show_step(step, {**context, **answers}):
                continue

            # Use mock response if provided
            if step["id"] in mock_responses:
                answers[step["id"]] = mock_responses[step["id"]]
                questionary.print(
                    f"   🤖 Mock: {step['message']} -> {mock_responses[step['id']]}",
                    style="italic",
                )
                continue

            # Build and ask question
            question = self._build_question(step, {**context, **answers})
            if question:
                try:
                    answer = question.ask()
                    # Some prompt libraries (e.g., questionary/prompt_toolkit) can swallow Ctrl+C
                    # and return None instead of raising KeyboardInterrupt. Treat None as a
                    # user cancellation to avoid infinite loops in calling applications.
                    if answer is None:
                        questionary.print(
                            "\n❌ Flow execution cancelled by user.", style="bold red"
                        )
                        raise FlowExecutionError("Flow execution cancelled by user")

                    answers[step["id"]] = answer

                    # Show preview if defined
                    if "preview" in step:
                        preview_text = self._format_preview(
                            step["preview"], {**context, **answers}
                        )
                        questionary.print(f"   📋 {preview_text}", style="bold green")
                except KeyboardInterrupt:
                    questionary.print(
                        "\n❌ Flow execution cancelled by user.", style="bold red"
                    )
                    raise FlowExecutionError("Flow execution cancelled by user")

        # Apply output mapping if specified
        if "output_mapping" in flow_def:
            return self._apply_output_mapping(answers, flow_def["output_mapping"])

        return answers

    def validate_flow(
        self, flow_definition: Dict[str, Any], strict: bool = True
    ) -> List[str]:
        """
        Validate flow definition and return list of errors.

        Args:
            flow_definition: Flow definition dictionary
            strict: Enable production-ready validation (catches incomplete development)
                   DEFAULT: True (no backward compatibility - forms must be production-ready)

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Required top-level fields
        required_fields = ["layout_id", "title", "steps"]
        for field in required_fields:
            if field not in flow_definition:
                errors.append(f"Missing required field: {field}")

        # Validate steps
        if "steps" in flow_definition:
            step_ids = set()
            subids = set()
            for i, step in enumerate(flow_definition["steps"]):
                # Check if this is a sublayout reference
                is_sublayout = "sublayout" in step

                if is_sublayout:
                    # Sublayout validation
                    if "subid" not in step:
                        errors.append(f"Step {i}: Sublayout missing 'subid' field")
                    elif step["subid"] in subids:
                        errors.append(f"Step {i}: Duplicate subid '{step['subid']}'")
                    else:
                        subids.add(step["subid"])

                    if "sublayout" not in step:
                        errors.append(f"Step {i}: Missing 'sublayout' path")
                else:
                    # Regular step validation
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

        # Production-ready validation (strict mode - NOW DEFAULT)
        if strict:
            errors.extend(self._validate_production_ready(flow_definition))

        return errors

    def _validate_production_ready(self, flow_definition: Dict[str, Any]) -> List[str]:
        """
        Validate that flow is production-ready (no scaffolding placeholders).

        Detects incomplete development work like TODO comments, placeholder IDs,
        and generic messages that indicate the form hasn't been customized.

        Args:
            flow_definition: Flow definition dictionary

        Returns:
            List of production-readiness warnings/errors
        """
        warnings = []

        # Check for TODO comments in the YAML (would need raw YAML for this)
        # Note: This is checked in the validator tool when loading from file

        # Placeholder ID patterns
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

        # Generic messages that indicate incomplete customization
        generic_messages = [
            "Enter a value:",
            "Provide configuration input",
            "Enter text here",
            "Select an option",
            "Choose a value",
            "Input value",
            "Type something",
        ]

        # Generic instructions
        generic_instructions = [
            "Provide configuration input",
            "Enter your input",
            "Fill in this field",
        ]

        # Check steps for placeholders
        if "steps" in flow_definition:
            for i, step in enumerate(flow_definition["steps"]):
                step_id = step.get("id", "")

                # Check for placeholder IDs
                for pattern in placeholder_patterns:
                    if step_id.lower().startswith(pattern):
                        warnings.append(
                            f"Step {i} ({step_id}): Placeholder ID detected - "
                            f"appears to be scaffolding that hasn't been customized"
                        )
                        break

                # Check for generic messages
                message = step.get("message", "")
                if message in generic_messages:
                    warnings.append(
                        f"Step {i} ({step_id}): Generic message '{message}' - "
                        f"should be customized for production"
                    )

                # Check for generic instructions
                instruction = step.get("instruction", "")
                if instruction in generic_instructions:
                    warnings.append(
                        f"Step {i} ({step_id}): Generic instruction '{instruction}' - "
                        f"should be customized for production"
                    )

                # Check for exact scaffolding template pattern
                if (
                    step_id == "example_input"
                    and step.get("type") == "text"
                    and message == "Enter a value:"
                    and instruction == "Provide configuration input"
                ):
                    warnings.append(
                        f"Step {i}: Matches exact scaffolding template - "
                        f"this step has not been customized at all!"
                    )

        # Check for minimal step count (might indicate incomplete form)
        if "steps" in flow_definition and len(flow_definition["steps"]) == 1:
            step = flow_definition["steps"][0]
            if any(step.get("id", "").startswith(p) for p in placeholder_patterns):
                warnings.append(
                    "Only 1 step with placeholder ID - form appears incomplete"
                )

        return warnings

    def _build_question(self, step: Dict[str, Any], context: Dict[str, Any]):
        """Build a questionary question from step definition."""

        if step["type"] == "select":
            choices = []
            for choice in step["choices"]:
                if isinstance(choice, dict):
                    choices.append(choice["name"])
                else:
                    choices.append(choice)

            return questionary.select(
                step["message"],
                choices=choices,
                default=step.get("default"),
                instruction=step.get("instruction"),
                style=self.style,
            )

        elif step["type"] == "text":
            # Build text question with validation
            if "validate" in step:
                validator_name = step["validate"]
                validator_func = self.validators.get(validator_name)
                return questionary.text(
                    step["message"],
                    default=step.get("default", ""),
                    instruction=step.get("instruction"),
                    validate=validator_func,
                    style=self.style,
                )
            else:
                return questionary.text(
                    step["message"],
                    default=step.get("default", ""),
                    instruction=step.get("instruction"),
                    style=self.style,
                )

        elif step["type"] == "password":
            return questionary.password(
                step["message"], instruction=step.get("instruction"), style=self.style
            )

        elif step["type"] == "confirm":
            return questionary.confirm(
                step["message"],
                default=step.get("default", True),
                instruction=step.get("instruction"),
                style=self.style,
            )

        return None

    def _should_show_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if a step should be shown based on conditions."""
        if "condition" not in step and "when" not in step:
            return True

        condition = step.get("condition") or step.get("when")
        return self._evaluate_expression(condition, context)

    def _evaluate_expression(self, expression: str, context: Dict[str, Any]) -> Any:
        """Evaluate a simple expression against context."""
        # Simple expression evaluator for conditions like "enable_email == true"

        # Handle simple equality checks
        if "==" in expression:
            left, right = expression.split("==", 1)
            left = left.strip()
            right = right.strip().strip("'\\\"")

            # Convert string boolean values
            if right.lower() == "true":
                right = True
            elif right.lower() == "false":
                right = False
            elif right.isdigit():
                right = int(right)
            elif right.replace(".", "", 1).isdigit():
                right = float(right)

            left_value = self._get_nested_value(context, left)
            return left_value == right

        # Handle simple boolean checks
        if expression in context:
            return bool(context[expression])

        return False

    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        """Get nested value using dot notation."""
        keys = key.split(".")
        value = data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        return value

    def _format_preview(self, preview_template: str, context: Dict[str, Any]) -> str:
        """Format preview text with context variables."""

        def replace_var(match):
            var_name = match.group(1)
            value = self._get_nested_value(context, var_name)
            return str(value) if value is not None else f"{{{var_name}}}"

        return re.sub(r"\\{([^}]+)\\}", replace_var, preview_template)

    def _load_flow(self, flow_id: str) -> Dict[str, Any]:
        """Load flow definition from YAML file."""
        flow_path = self.flows_dir / f"{flow_id}.yml"
        if not flow_path.exists():
            raise FlowValidationError(f"Flow definition not found: {flow_path}")

        try:
            with open(flow_path, "r", encoding="utf-8") as f:
                flow_def = yaml.safe_load(f)
                if not flow_def:
                    raise FlowValidationError(f"Empty or invalid YAML in {flow_path}")
                return flow_def
        except yaml.YAMLError as e:
            raise FlowValidationError(f"Invalid YAML in {flow_path}: {e}")

    def _apply_output_mapping(
        self, answers: Dict[str, Any], mapping: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply output mapping to transform answers."""
        result = {}

        def apply_mapping(
            source_dict: Dict[str, Any],
            mapping_dict: Dict[str, Any],
            target_dict: Dict[str, Any],
        ):
            for key, value in mapping_dict.items():
                if isinstance(value, dict):
                    # Nested mapping
                    target_dict[key] = {}
                    apply_mapping(source_dict, value, target_dict[key])
                elif isinstance(value, str) and value in source_dict:
                    # Direct mapping
                    target_dict[key] = source_dict[value]

        apply_mapping(answers, mapping, result)
        return result

    def _load_validators(self) -> Dict[str, Callable]:
        """Load built-in validators."""

        def required_validator(value: str) -> bool:
            """Validate that value is not empty."""
            if not value or not value.strip():
                raise questionary.ValidationError(message="This field is required")
            return True

        def email_validator(value: str) -> bool:
            """Validate email format."""
            if not value:
                return True  # Allow empty for optional fields
            if not re.match(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", value
            ):
                raise questionary.ValidationError(message="Invalid email format")
            return True

        def domain_validator(value: str) -> bool:
            """Validate domain format."""
            if not value:
                raise questionary.ValidationError(message="Domain cannot be empty")
            if not re.match(r"^[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", value):
                raise questionary.ValidationError(message="Invalid domain format")
            return True

        def integer_validator(value: str) -> bool:
            """Validate integer format."""
            if not value:
                return True  # Allow empty for optional fields
            try:
                int(value)
                return True
            except ValueError:
                raise questionary.ValidationError(message="Must be a valid integer")

        def password_length_validator(value: str) -> bool:
            """Validate password length (minimum 8 characters)."""
            if len(value) < 8:
                raise questionary.ValidationError(
                    message="Password must be at least 8 characters long"
                )
            return True

        return {
            "required": required_validator,
            "email": email_validator,
            "domain": domain_validator,
            "integer": integer_validator,
            "password_length": password_length_validator,
        }
