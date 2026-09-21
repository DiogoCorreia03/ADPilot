from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def new_run_metrics() -> dict[str, Any]:
    return {
        "tool_calls": 0,
        "tool_errors": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
    }


def record_tool_call(
    metrics: dict[str, Any],
    *,
    is_error: bool = False,
) -> None:

    metrics["tool_calls"] = metrics.get("tool_calls", 0) + 1

    if is_error:
        metrics["tool_errors"] = metrics.get("tool_errors", 0) + 1


def record_token_usage(
    metrics: dict[str, Any],
    *,
    usage_metadata: Mapping[str, Any] | None,
) -> None:
    if not usage_metadata:
        return

    input_tokens = int(usage_metadata.get("input_tokens", 0) or 0)
    output_tokens = int(usage_metadata.get("output_tokens", 0) or 0)
    total_tokens = int(usage_metadata.get("total_tokens", 0) or 0)

    metrics["input_tokens"] = metrics.get("input_tokens", 0) + input_tokens
    metrics["output_tokens"] = metrics.get("output_tokens", 0) + output_tokens
    metrics["total_tokens"] = metrics.get("total_tokens", 0) + total_tokens


def format_run_summary(metrics: dict[str, Any]) -> str:
    tool_calls = int(metrics.get("tool_calls", 0))
    tool_errors = int(metrics.get("tool_errors", 0))
    input_tokens = int(metrics.get("input_tokens", 0))
    output_tokens = int(metrics.get("output_tokens", 0))
    total_tokens = int(metrics.get("total_tokens", 0))

    return (
        "Run summary\n"
        f"Tool calls: {tool_calls} total, {tool_errors} errors\n"
        f"Tokens used: {total_tokens:,} total "
        f"(input={input_tokens:,}, output={output_tokens:,})\n"
    )
