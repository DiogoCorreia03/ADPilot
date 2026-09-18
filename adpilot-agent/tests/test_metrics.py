from adpilot_agent.util.metrics import new_run_metrics, record_tool_call, record_token_usage, format_run_summary
from adpilot_agent.util.state import Phase


def test_metrics_initialization():
    metrics = new_run_metrics()
    assert metrics["total_tool_calls"] == 0
    assert metrics["total_tool_errors"] == 0
    assert Phase.EXTERNAL_RECON.value in metrics["phases"]


def test_record_tool_call_and_errors():
    metrics = new_run_metrics()
    record_tool_call(metrics, phase=Phase.EXTERNAL_RECON, scope_label="ExploitNode", is_error=False)
    record_tool_call(metrics, phase=Phase.EXTERNAL_RECON, scope_label="ExploitNode", is_error=True)

    assert metrics["total_tool_calls"] == 2
    assert metrics["total_tool_errors"] == 1
    assert metrics["exploit_node_tool_calls"] == 2
    assert metrics["phases"][Phase.EXTERNAL_RECON.value]["tool_calls"] == 2
    assert metrics["phases"][Phase.EXTERNAL_RECON.value]["tool_errors"] == 1


def test_record_token_usage():
    metrics = new_run_metrics()
    record_token_usage(
        metrics,
        phase=Phase.INITIAL_ACCESS,
        usage_metadata={"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
    )
    phase_data = metrics["phases"][Phase.INITIAL_ACCESS.value]
    assert phase_data["input_tokens"] == 100
    assert phase_data["output_tokens"] == 50
    assert phase_data["total_tokens"] == 150

    summary = format_run_summary(metrics)
    assert "Tokens used: 150 total" in summary
