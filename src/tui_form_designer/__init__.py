"""
TUI Form Designer - Interactive form designer for Questionary-based terminal user interfaces.

Create beautiful, interactive command-line forms and configuration wizards using
YAML flow definitions instead of hardcoded Python prompts.
"""

__version__ = "2.1.0"
__author__ = "OpenProject Team"
__email__ = "support@openproject.org"

from .core.flow_engine import FlowEngine
from .ui.questionary_ui import QuestionaryUI
from .core.exceptions import FlowValidationError, FlowExecutionError

__all__ = [
    "FlowEngine",
    "QuestionaryUI",
    "FlowValidationError",
    "FlowExecutionError",
]
