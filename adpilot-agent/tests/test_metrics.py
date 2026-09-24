from adpilot_agent.util.metrics import new_run_metrics, record_tool_call, record_token_usage, format_run_summary


def test_metrics_initialization():
    metrics = new_run_metrics()
    assert metrics["total_tool_calls"] == 0
    assert metrics["total_tool_errors"] == 0


def test_record_tool_call_and_errors():
    metrics = new_run_metrics()
    record_tool_call(metrics, scope_label="ExploitNode", is_error=False)
    record_tool_call(metrics, scope_label="ExploitNode", is_error=True)

    assert metrics["total_tool_calls"] == 2
    assert metrics["total_tool_errors"] == 1
    assert metrics["exploit_node_tool_calls"] == 2

def test_record_token_usage():
    metrics = new_run_metrics()
    record_token_usage(
        metrics,
        usage_metadata={"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
    )
    assert metrics["input_tokens"] == 100
    assert metrics["output_tokens"] == 50
    assert metrics["total_tokens"] == 150

    summary = format_run_summary(metrics)
    assert "Tokens used: 150 total" in summary
