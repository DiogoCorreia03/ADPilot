from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .state import Phase


def new_run_metrics() -> dict[str, Any]:
    return {
        "total_tool_calls": 0,
        "total_tool_errors": 0,
        "exploit_node_tool_calls": 0,
        "exploit_node_runs": 0,
        "phases": {
            phase.value: {
                "tool_calls": 0,
                "tool_errors": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            }
            for phase in Phase
        },
    }


def record_tool_call(
    metrics: dict[str, Any],
    *,
    phase: Phase | str | None,
    scope_label: str,
    is_error: bool = False,
) -> None:
    phase_name = phase.value if isinstance(phase, Phase) else phase
    if not phase_name:
        phase_name = "unknown"

    phases = metrics.setdefault("phases", {})
    phase_metrics = phases.setdefault(
        phase_name,
        {
            "tool_calls": 0,
            "tool_errors": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        },
    )

    metrics["total_tool_calls"] = metrics.get("total_tool_calls", 0) + 1
    phase_metrics["tool_calls"] = phase_metrics.get("tool_calls", 0) + 1

    if is_error:
        metrics["total_tool_errors"] = metrics.get("total_tool_errors", 0) + 1
        phase_metrics["tool_errors"] = phase_metrics.get("tool_errors", 0) + 1

    if scope_label == "ExploitNode":
        metrics["exploit_node_tool_calls"] = metrics.get(
            "exploit_node_tool_calls", 0
        ) + 1


def record_exploit_node_run(metrics: dict[str, Any]) -> None:
    metrics["exploit_node_runs"] = metrics.get("exploit_node_runs", 0) + 1


def record_token_usage(
    metrics: dict[str, Any],
    *,
    phase: Phase | str | None,
    usage_metadata: Mapping[str, Any] | None,
) -> None:
    if not usage_metadata:
        return

    phase_name = phase.value if isinstance(phase, Phase) else phase
    if not phase_name:
        phase_name = "unknown"

    phases = metrics.setdefault("phases", {})
    phase_metrics = phases.setdefault(
        phase_name,
        {
            "tool_calls": 0,
            "tool_errors": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        },
    )

    input_tokens = int(usage_metadata.get("input_tokens", 0) or 0)
    output_tokens = int(usage_metadata.get("output_tokens", 0) or 0)
    total_tokens = int(usage_metadata.get("total_tokens", 0) or 0)

    phase_metrics["input_tokens"] = phase_metrics.get("input_tokens", 0) + input_tokens
    phase_metrics["output_tokens"] = phase_metrics.get("output_tokens", 0) + output_tokens
    phase_metrics["total_tokens"] = phase_metrics.get("total_tokens", 0) + total_tokens


def format_run_summary(metrics: dict[str, Any]) -> str:
    total_tool_calls = int(metrics.get("total_tool_calls", 0))
    total_tool_errors = int(metrics.get("total_tool_errors", 0))
    exploit_node_tool_calls = int(metrics.get("exploit_node_tool_calls", 0))
    exploit_node_runs = int(metrics.get("exploit_node_runs", 0))
    phases = metrics.get("phases", {})

    total_input_tokens = 0
    total_output_tokens = 0
    total_tokens = 0
    phase_lines: list[str] = []

    # Display known phases first in sequence, then any other scopes (e.g. unknown / final report)
    ordered_phase_keys = [phase.value for phase in Phase]
    for key in phases:
        if key not in ordered_phase_keys:
            ordered_phase_keys.append(key)

    active_phase_count = 0
    for phase_key in ordered_phase_keys:
        phase_metrics = phases.get(phase_key, {})
        input_tokens = int(phase_metrics.get("input_tokens", 0))
        output_tokens = int(phase_metrics.get("output_tokens", 0))
        phase_total_tokens = int(phase_metrics.get("total_tokens", 0))
        phase_tool_calls = int(phase_metrics.get("tool_calls", 0))
        phase_tool_errors = int(phase_metrics.get("tool_errors", 0))

        if phase_tool_calls > 0 or phase_total_tokens > 0:
            active_phase_count += 1

        total_input_tokens += input_tokens
        total_output_tokens += output_tokens
        total_tokens += phase_total_tokens

        phase_label = "final_report / other" if phase_key == "unknown" else phase_key
        phase_lines.append(
            f"- {phase_label}: tool_calls={phase_tool_calls}, errors={phase_tool_errors}, "
            f"tokens={phase_total_tokens:,} (input={input_tokens:,}, output={output_tokens:,})"
        )

    phase_denominator = active_phase_count if active_phase_count > 0 else len(Phase)
    avg_tool_calls_per_phase = total_tool_calls / phase_denominator if phase_denominator else 0.0
    avg_tool_calls_per_exploit_node = (
        exploit_node_tool_calls / exploit_node_runs if exploit_node_runs else 0.0
    )

    return (
        "Run summary\n"
        f"Tool calls: {total_tool_calls} total, {total_tool_errors} errors\n"
        f"Average tool calls per phase: {avg_tool_calls_per_phase:.2f}\n"
        f"Average tool calls per ExploitNode: {avg_tool_calls_per_exploit_node:.2f} "
        f"over {exploit_node_runs} run(s)\n"
        f"Tokens used: {total_tokens:,} total "
        f"(input={total_input_tokens:,}, output={total_output_tokens:,})\n"
        "Per phase:\n"
        + "\n".join(phase_lines)
    )