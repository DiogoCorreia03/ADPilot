import logging
from typing import Any, TypedDict
from enum import StrEnum
import asyncio


# Set up logging
logger = logging.getLogger(__name__)


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
    plan: str # The task tree
    next_task: str  # The next task selected by the Planner to be executed.
    task_result: str  # The result of the executed task, to be analyzed by the Planner for updating the plan.
    check_count: int  # Number of times the current task has been checked for success/failure. Used to decide when to give up on a task.
    check_output: str  # The output of the last check performed by the CheckerNode, used to analyze if a task should be retried or marked as failed.
    check_verdict: CheckVerdict  # Normalized verdict from the checker, used for routing and update handling.
    run_metrics: dict[str, Any]  # Aggregated tool-call and token usage for the entire run.
