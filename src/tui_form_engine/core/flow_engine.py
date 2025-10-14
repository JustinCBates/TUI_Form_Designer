"""Form executor for executing YAML-defined forms using Questionary."""

import questionary
from questionary import Style
import yaml
from typing import Dict, Any, Optional, List, Callable, Union
from pathlib import Path
import re
from .exceptions import FlowValidationError, FlowExecutionError


class FormExecutor:
    """Execute YAML-defined forms using Questionary."""
    
    def __init__(self, 
                 flows_dir: Optional[Union[str, Path]] = None,
                 style: Optional[Style] = None,
                 theme: str = "default"):
        """
        Initialize FormExecutor.
        
        Args:
            flows_dir: Directory containing flow definition files
            style: Custom Questionary style
            theme: Pre-built theme name ('default', 'dark', 'minimal')
        """
        self.flows_dir = Path(flows_dir or "flows")
        self.style = style or self._get_theme_style(theme)
        self.validators = self._load_validators()
    
    def _get_theme_style(self, theme: str) -> Style:
        """Get predefined theme styles."""
        themes = {
            "default": Style([
                ('question', 'bold blue'),
                ('answer', 'fg:#ff9d00 bold'),
                ('pointer', 'fg:#673ab7 bold'),
                ('highlighted', 'fg:#673ab7 bold'),
                ('selected', 'fg:#cc5454'),
                ('instruction', 'italic'),
            ]),
            "dark": Style([
                ('question', 'bold cyan'),
                ('answer', 'fg:#00ff00 bold'),
                ('pointer', 'fg:#ff00ff bold'),
                ('highlighted', 'fg:#ff00ff bold'),
                ('selected', 'fg:#ffff00'),
                ('instruction', 'italic fg:#888888'),
            ]),
            "minimal": Style([
                ('question', 'bold'),
                ('answer', 'bold'),
                ('pointer', 'fg:#ffffff bold'),
                ('highlighted', 'bold'),
                ('selected', 'bold'),
                ('instruction', 'italic'),
            ])
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
    
    def execute_flow(self, 
                     flow_id: str, 
                     context: Optional[Dict[str, Any]] = None,
                     mock_responses: Optional[Dict[str, Any]] = None,
                     flow_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a flow by ID or with provided flow data.
        
        Args:
            flow_id: ID of the flow to execute (or just a name if flow_data is provided)
            context: Initial context variables
            mock_responses: Mock responses for testing (maps step_id -> response)
            flow_data: Optional pre-loaded/preprocessed flow definition (bypasses file loading)
            
        Returns:
            Dictionary containing flow results
        """
        # If flow_data is provided, use it directly (for preprocessed layouts)
        if flow_data is not None:
            flow_def = flow_data
        else:
            flow_def = self._load_flow(flow_id)
        context = context or {}
        mock_responses = mock_responses or {}
        
        # Validate flow definition
        self.validate_flow(flow_def)
        
        # Show flow header
        questionary.print(f"\\n{flow_def.get('icon', '🔧')} {flow_def['title']}", style="bold blue")
        if flow_def.get('description'):
            questionary.print(f"   {flow_def['description']}", style="italic")
        
        # Execute steps sequentially to handle conditional logic
        answers = {}
        
        for step in flow_def['steps']:
            if step['type'] == 'computed':
                # Handle computed values
                if 'compute' in step:
                    computed_value = self._evaluate_expression(step['compute'], {**context, **answers})
                    answers[step['id']] = computed_value
                continue
                
            # Check if step should be shown
            if not self._should_show_step(step, {**context, **answers}):
                continue
            
            # Use mock response if provided
            if step['id'] in mock_responses:
                answers[step['id']] = mock_responses[step['id']]
                questionary.print(f"   🤖 Mock: {step['message']} -> {mock_responses[step['id']]}", style="italic")
                continue
                
            # Build and ask question
            question = self._build_question(step, {**context, **answers})
            if question:
                try:
                    answer = question.ask()
                    answers[step['id']] = answer
                    
                    # Show preview if defined
                    if 'preview' in step:
                        preview_text = self._format_preview(step['preview'], {**context, **answers})
                        questionary.print(f"   📋 {preview_text}", style="bold green")
                except KeyboardInterrupt:
                    questionary.print("\\n❌ Flow execution cancelled by user.", style="bold red")
                    raise FlowExecutionError("Flow execution cancelled by user")
        
        # Apply output mapping if specified
        if 'output_mapping' in flow_def:
            return self._apply_output_mapping(answers, flow_def['output_mapping'])
        
        return answers
    
    def validate_flow(self, flow_definition: Dict[str, Any]) -> List[str]:
        """
        Validate flow definition and return list of errors.
        
        Args:
            flow_definition: Flow definition dictionary
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Required top-level fields
        required_fields = ['flow_id', 'title', 'steps']
        for field in required_fields:
            if field not in flow_definition:
                errors.append(f"Missing required field: {field}")
        
        # Validate steps
        if 'steps' in flow_definition:
            step_ids = set()
            for i, step in enumerate(flow_definition['steps']):
                # Check required step fields
                if 'id' not in step:
                    errors.append(f"Step {i}: Missing 'id' field")
                elif step['id'] in step_ids:
                    errors.append(f"Step {i}: Duplicate step ID '{step['id']}'")
                else:
                    step_ids.add(step['id'])
                
                if 'type' not in step:
                    errors.append(f"Step {i}: Missing 'type' field")
                elif step['type'] not in ['text', 'select', 'confirm', 'password', 'computed']:
                    errors.append(f"Step {i}: Invalid step type '{step['type']}'")
                
                if 'message' not in step and step.get('type') != 'computed':
                    errors.append(f"Step {i}: Missing 'message' field")
                
                # Validate select choices
                if step.get('type') == 'select' and 'choices' not in step:
                    errors.append(f"Step {i}: Select step missing 'choices' field")
        
        return errors
    
    def _build_question(self, step: Dict[str, Any], context: Dict[str, Any]):
        """Build a questionary question from step definition."""
        
        if step['type'] == 'info':
            # Info/message steps - just print and continue
            title = step.get('title', '')
            message = step.get('message', '')
            instruction = step.get('instruction', 'Press Enter to continue')
            
            if title:
                questionary.print(f"\n{title}", style="bold blue")
            if message:
                questionary.print(message, style="")
            
            return questionary.confirm(
                instruction,
                default=True,
                style=self.style
            )
        
        elif step['type'] == 'select':
            choices = []
            for choice in step['choices']:
                if isinstance(choice, dict):
                    choices.append(choice['name'])
                else:
                    choices.append(choice)
            
            return questionary.select(
                step['message'],
                choices=choices,
                default=step.get('default'),
                instruction=step.get('instruction'),
                style=self.style
            )
        
        elif step['type'] == 'text':
            # Build text question with validation
            if 'validate' in step:
                validator_name = step['validate']
                validator_func = self.validators.get(validator_name)
                return questionary.text(
                    step['message'],
                    default=step.get('default', ''),
                    instruction=step.get('instruction'),
                    validate=validator_func,
                    style=self.style
                )
            else:
                return questionary.text(
                    step['message'],
                    default=step.get('default', ''),
                    instruction=step.get('instruction'),
                    style=self.style
                )
        
        elif step['type'] == 'password':
            return questionary.password(
                step['message'],
                instruction=step.get('instruction'),
                style=self.style
            )
        
        elif step['type'] == 'confirm':
            return questionary.confirm(
                step['message'],
                default=step.get('default', True),
                instruction=step.get('instruction'),
                style=self.style
            )
        
        return None
    
    def _should_show_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if a step should be shown based on conditions."""
        if 'condition' not in step and 'when' not in step:
            return True
        
        condition = step.get('condition') or step.get('when')
        return self._evaluate_expression(condition, context)
    
    def _evaluate_expression(self, expression: str, context: Dict[str, Any]) -> Any:
        """Evaluate a simple expression against context."""
        # Simple expression evaluator for conditions like "enable_email == true"
        
        # Handle simple equality checks
        if '==' in expression:
            left, right = expression.split('==', 1)
            left = left.strip()
            right = right.strip().strip("'\\\"")
            
            # Convert string boolean values
            if right.lower() == 'true':
                right = True
            elif right.lower() == 'false':
                right = False
            elif right.isdigit():
                right = int(right)
            elif right.replace('.', '', 1).isdigit():
                right = float(right)
            
            left_value = self._get_nested_value(context, left)
            return left_value == right
        
        # Handle simple boolean checks
        if expression in context:
            return bool(context[expression])
        
        return False
    
    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        """Get nested value using dot notation."""
        keys = key.split('.')
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
        
        return re.sub(r'\\{([^}]+)\\}', replace_var, preview_template)
    
    def _load_flow(self, flow_id: str) -> Dict[str, Any]:
        """Load flow definition from YAML file."""
        flow_path = self.flows_dir / f"{flow_id}.yml"
        if not flow_path.exists():
            raise FlowValidationError(f"Flow definition not found: {flow_path}")
        
        try:
            with open(flow_path, 'r') as f:
                flow_def = yaml.safe_load(f)
                if not flow_def:
                    raise FlowValidationError(f"Empty or invalid YAML in {flow_path}")
                
                # Load and merge defaults if defaults_file is specified
                if 'defaults_file' in flow_def:
                    flow_def = self._merge_defaults(flow_def, flow_path)
                
                return flow_def
        except yaml.YAMLError as e:
            raise FlowValidationError(f"Invalid YAML in {flow_path}: {e}")
    
    def _merge_defaults(self, flow_def: Dict[str, Any], flow_path: Path) -> Dict[str, Any]:
        """
        Load defaults file and merge defaults into step definitions.
        
        Priority:
        1. Hardcoded default in step (lowest priority - fallback)
        2. Value from defaults_file (highest priority - intelligent defaults)
        
        Args:
            flow_def: Flow definition with defaults_file field
            flow_path: Path to the flow file (for resolving relative paths)
            
        Returns:
            Flow definition with intelligent defaults merged into steps
        """
        defaults_file = flow_def.get('defaults_file')
        if not defaults_file:
            return flow_def
        
        # Resolve defaults file path (can be absolute or relative to flow file)
        defaults_path = Path(defaults_file)
        if not defaults_path.is_absolute():
            defaults_path = flow_path.parent / defaults_file
        
        if not defaults_path.exists():
            return flow_def
        
        try:
            with open(defaults_path, 'r') as f:
                defaults_data = yaml.safe_load(f)
            
            if not defaults_data or 'defaults' not in defaults_data:
                return flow_def
            
            defaults = defaults_data['defaults']
            
            # Merge intelligent defaults into steps (overwrites hardcoded defaults)
            for step in flow_def.get('steps', []):
                step_id = step.get('id')
                if step_id and step_id in defaults:
                    # Intelligent defaults take priority over hardcoded defaults
                    step['default'] = defaults[step_id]
            
            return flow_def
            
        except Exception as e:
            # Silently fail - use hardcoded defaults if defaults file fails
            return flow_def
    
    def _apply_output_mapping(self, answers: Dict[str, Any], mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Apply output mapping to transform answers."""
        result = {}
        
        def apply_mapping(source_dict: Dict[str, Any], mapping_dict: Dict[str, Any], target_dict: Dict[str, Any]):
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
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$', value):
                raise questionary.ValidationError(message="Invalid email format")
            return True
        
        def domain_validator(value: str) -> bool:
            """Validate domain format."""
            if not value:
                raise questionary.ValidationError(message="Domain cannot be empty")
            if not re.match(r'^[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$', value):
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
                raise questionary.ValidationError(message="Password must be at least 8 characters long")
            return True
        
        return {
            'required': required_validator,
            'email': email_validator,
            'domain': domain_validator,
            'integer': integer_validator,
            'password_length': password_length_validator,
        }