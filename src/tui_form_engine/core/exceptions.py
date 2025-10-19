"""Custom exceptions for TUI Form Designer."""


class TUIFormDesignerError(Exception):
    """Base exception for TUI Form Designer."""
    pass


class FormValidationError(TUIFormDesignerError):
    """Raised when form definition validation fails."""
    pass


class FormExecutionError(TUIFormDesignerError):
    """Raised when form execution encounters an error."""
    pass


class FormNotFoundError(TUIFormDesignerError):
    """Raised when a requested form cannot be found."""
    pass


# Deprecated aliases for backward compatibility
FlowValidationError = FormValidationError
FlowExecutionError = FormExecutionError
FlowNotFoundError = FormNotFoundError