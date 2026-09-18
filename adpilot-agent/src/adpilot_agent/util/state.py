import logging
from typing import Any, TypedDict
from enum import StrEnum
import asyncio


# Set up logging
logger = logging.getLogger(__name__)


class Phase(StrEnum):
    #! String representations of the phases need to be the same as the ones in the MCP Server
    EXTERNAL_RECON = "external_reconnaissance"
    INITIAL_ACCESS = "initial_access"
    INTERNAL_RECON = "internal_reconnaissance"
    LATERAL_PRIVESC = "lateral_movement_and_privilege_escalation"

    def __str__(self) -> str:
        return self.value

    def next(self) -> "Phase | None":
        return get_next_phase(self)


PHASE_SEQUENCE: tuple[Phase, ...] = (
    Phase.EXTERNAL_RECON,
    Phase.INITIAL_ACCESS,
    Phase.INTERNAL_RECON,
    Phase.LATERAL_PRIVESC,
)


def get_next_phase(phase: Phase) -> Phase | None:
    """Return the next Phase in the defined pentest sequence, or None if the sequence is complete."""
    try:
        current_index = PHASE_SEQUENCE.index(phase)
    except ValueError:
        return None

    if current_index + 1 < len(PHASE_SEQUENCE):
        return PHASE_SEQUENCE[current_index + 1]
    return None


class CheckVerdict(StrEnum):
    SUCCESS = "SUCCESS"
    RETRY = "RETRY"
    FAILURE = "FAILURE"

class PentestState(TypedDict):
    dc_ip: str
    network: str
    initial_scan_results: str
    tools: str
    scan_results: str
    scenario: str
    plan: str # The plan of the current phase
    external_recon_plan: str  # Plan for the external reconnaissance phase.
    initial_access_plan: str  # Plan for the initial access phase.
    internal_recon_plan: str  # Plan for the internal reconnaissance phase.
    lateral_privesc_plan: str  # Plan for the lateral movement and privilege escalation phase.
    next_task: str  # The next task selected by the Planner to be executed.
    task_result: str  # The result of the executed task, to be analyzed by the Planner for updating the plan.
    check_count: int  # Number of times the current task has been checked for success/failure. Used to decide when to give up on a task.
    check_output: str  # The output of the last check performed by the CheckerNode, used to analyze if a task should be retried or marked as failed.
    check_verdict: CheckVerdict  # Normalized verdict from the checker, used for routing and update handling.
    current_phase: Phase | None  # The current phase of the pentest, or None when all phases have completed.
    advance_phase_request: asyncio.Event  # Shared signal that asks the selector to finish the current phase.
    run_metrics: dict[str, Any]  # Aggregated tool-call and token usage for the entire run.
