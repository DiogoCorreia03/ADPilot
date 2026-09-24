import pytest
from types import SimpleNamespace

from adpilot_agent.util.metrics import new_run_metrics, format_run_summary, record_token_usage
from adpilot_agent.util.nodes import _extract_tool_text, _format_historical_task_trees, _parse_check_verdict
from adpilot_agent.util.mcp_session import record_tool_result
from adpilot_agent.util.state import CheckVerdict, Phase, PentestState


def test_extract_tool_text():
    # String input
    assert _extract_tool_text("hello world") == "hello world"

    # Empty list
    assert _extract_tool_text([]) == ""

    # List with dict
    assert _extract_tool_text([{"type": "text", "text": "result content"}]) == "result content"

    # List with object having text attribute
    obj = SimpleNamespace(type="text", text="object text")
    assert _extract_tool_text([obj]) == "object text"

    # Single dict
    assert _extract_tool_text({"text": "dict text"}) == "dict text"


def test_format_historical_task_trees_with_headers():
    state: PentestState = {
        "external_recon_plan": "1.1. [SUCCESS] Port scan",
        "initial_access_plan": "2.1. [SUCCESS] AS-REP roast",
        "internal_recon_plan": "",
        "lateral_privesc_plan": "",
    } # type: ignore
    formatted = _format_historical_task_trees(state)
    assert "### External Reconnaissance Phase" in formatted
    assert "1.1. [SUCCESS] Port scan" in formatted
    assert "### Initial Access Phase" in formatted
    assert "2.1. [SUCCESS] AS-REP roast" in formatted
    assert "Internal Reconnaissance" not in formatted


def test_format_run_summary_accounting():
    metrics = new_run_metrics()
    # Record normal phase tokens
    record_token_usage(metrics, phase=Phase.EXTERNAL_RECON, usage_metadata={"total_tokens": 500, "input_tokens": 400, "output_tokens": 100})
    # Record final report tokens (recorded under unknown when phase is None)
    record_token_usage(metrics, phase=None, usage_metadata={"total_tokens": 1200, "input_tokens": 1000, "output_tokens": 200})

    summary = format_run_summary(metrics)
    assert "Tokens used: 1,700 total" in summary
    assert "final_report / other" in summary
