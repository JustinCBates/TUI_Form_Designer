"""Signal handling tests for FlowEngine.

These tests ensure that Ctrl+C (KeyboardInterrupt) and None-returning prompts
are both treated as user cancellations and surfaced as FlowExecutionError.
"""

import pytest
from types import SimpleNamespace

from tui_form_designer.core.exceptions import FlowExecutionError


def test_execute_flow_treats_none_as_cancellation(
    flow_engine, sample_flow_file, monkeypatch
):
    """If a prompt returns None (swallowed Ctrl+C), raise FlowExecutionError."""

    class DummyQuestion:
        def ask(self):
            return None

    # Ensure every built question returns our dummy that yields None
    monkeypatch.setattr(
        type(flow_engine),
        "_build_question",
        lambda self, step, ctx: DummyQuestion(),
        raising=True,
    )

    with pytest.raises(FlowExecutionError, match="cancelled by user"):
        flow_engine.execute_flow("test_flow")


def test_execute_flow_keyboardinterrupt_raises(
    flow_engine, sample_flow_file, monkeypatch
):
    """If a prompt raises KeyboardInterrupt, it should surface as FlowExecutionError."""

    class InterruptQuestion:
        def ask(self):
            raise KeyboardInterrupt()

    monkeypatch.setattr(
        type(flow_engine),
        "_build_question",
        lambda self, step, ctx: InterruptQuestion(),
        raising=True,
    )

    with pytest.raises(FlowExecutionError, match="cancelled by user"):
        flow_engine.execute_flow("test_flow")
