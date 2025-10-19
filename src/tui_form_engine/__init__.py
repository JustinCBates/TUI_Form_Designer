"""
TUI Form Engine - Lightweight runtime engine for executing YAML-defined interactive forms.

This is the production runtime component of TUI Form Designer. It provides the core
engine for executing forms without the development/editing tools.

Perfect for production environments where you only need to run forms, not create them.
"""

__version__ = "1.0.0"
__author__ = "OpenProject Team"
__email__ = "support@openproject.org"

from .core.form_executor import FormExecutor
from .ui.questionary_ui import QuestionaryUI
from .core.exceptions import (
    FormValidationError, 
    FormExecutionError,
    # Backward compatibility aliases
    FlowValidationError,
    FlowExecutionError,
)
from .preprocessing import LayoutPreprocessor, DefaultsPreprocessor

# Export new names
__all__ = [
    "FormExecutor",
    "QuestionaryUI", 
    "FormValidationError",
    "FormExecutionError",
    "LayoutPreprocessor",
    "DefaultsPreprocessor",
    # Backward compatibility
    "FlowEngine",
    "FlowValidationError",
    "FlowExecutionError",
]

# Backward compatibility alias
FlowEngine = FormExecutor