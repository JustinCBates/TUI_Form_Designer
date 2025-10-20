"""Custom exceptions for TUI Form Designer."""


class TUIFormDesignerError(Exception):
    """Base exception for TUI Form Designer."""

    pass


class FlowValidationError(TUIFormDesignerError):
    """Raised when flow definition validation fails."""

    pass


class FlowExecutionError(TUIFormDesignerError):
    """Raised when flow execution encounters an error."""

    pass


class FlowNotFoundError(TUIFormDesignerError):
    """Raised when a requested flow cannot be found."""

    pass
