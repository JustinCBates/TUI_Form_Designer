"""
TUI Form Editor - Development tools for creating and managing YAML flow definitions.

This package provides interactive tools for designing, testing, and validating flows.
It builds on top of the tui-form-engine to provide a complete development experience.

Includes:
- Interactive flow designer
- Flow validation tools  
- Mock testing framework
- Flow preview capabilities
- Command-line interface
"""

__version__ = "1.0.0"
__author__ = "OpenProject Team"
__email__ = "support@openproject.org"

# Import engine components
from tui_form_engine import FlowEngine, QuestionaryUI, FlowValidationError, FlowExecutionError

# Import editor-specific tools
from .tools.designer import InteractiveFlowDesigner
from .tools.validator import FlowValidator
from .tools.tester import FlowTester
from .tools.preview import FlowPreviewer

__all__ = [
    # Engine components (re-exported)
    "FlowEngine",
    "QuestionaryUI", 
    "FlowValidationError",
    "FlowExecutionError",
    # Editor tools
    "InteractiveFlowDesigner",
    "FlowValidator",
    "FlowTester", 
    "FlowPreviewer",
]