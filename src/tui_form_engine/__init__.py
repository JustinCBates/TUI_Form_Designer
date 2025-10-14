"""
TUI Form Engine - Lightweight runtime engine for executing YAML-defined interactive flows.

This is the production runtime component of TUI Form Designer. It provides the core
engine for executing flows without the development/editing tools.

Perfect for production environments where you only need to run flows, not create them.
"""

__version__ = "1.0.0"
__author__ = "OpenProject Team"
__email__ = "support@openproject.org"

from .core.flow_engine import FlowEngine
from .ui.questionary_ui import QuestionaryUI
from .core.exceptions import FlowValidationError, FlowExecutionError
from .preprocessing import LayoutPreprocessor, DefaultsPreprocessor

__all__ = [
    "FlowEngine",
    "QuestionaryUI", 
    "FlowValidationError",
    "FlowExecutionError",
    "LayoutPreprocessor",
    "DefaultsPreprocessor",
]