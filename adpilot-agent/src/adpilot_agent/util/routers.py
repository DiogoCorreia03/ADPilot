import logging
import re
from typing import Literal

from .config import get_settings
from .execution_logger import log_execution_event
from .state import CheckVerdict, PentestState

logger = logging.getLogger(__name__)


def route_after_selector(
    state: PentestState,
) -> Literal["ExploitNode", "SelectNextTask", "FinalReport"]:
    """
    Routes to the next node after the SelectorNode based on the current state of the pentest.
    """

    # SelectorNode will set the "next_task" field in the state based on the selected task.
    next_task = state["next_task"].strip() if state.get("next_task") else ""

    # Check for completion signal (standalone token or surrounded by word boundary)
    if (
        re.search(r"(?<!\w)\[?FINISHED\]?(?!\w)", next_task, re.IGNORECASE)
        or next_task.upper() == "[FINISHED]"
    ):
        logger.info("Pentest completion token detected (%s). Terminating pentest.", next_task)
        route = "FinalReport"
    elif next_task:
        route = "ExploitNode"  # There is a next task to perform, route to the ExploitNode to execute it.
    else:
        route = "SelectNextTask"  # No next task was selected, route back to the SelectorNode to select a different task.

    log_execution_event(
        event_type="routing_decision",
        caller="Selector",
        input={"next_task": next_task},
        output=route,
    )
    return route


def route_after_check(
    state: PentestState,
) -> Literal["ExploitNode", "UpdatePlanSuccess", "UpdatePlanFailure", "CheckNode"]:
    """
    Routes to the next node after the CheckNode based on the output of the check.
    """
    check_verdict = state.get("check_verdict", CheckVerdict.RETRY)
    max_retries = get_settings().CHECK_MAX_RETRIES

    if check_verdict == CheckVerdict.SUCCESS:
        route = "UpdatePlanSuccess"
        msg = "Task marked as successful. Proceeding to update the plan."
    elif check_verdict == CheckVerdict.RETRY:
        if state["check_count"] > max_retries:
            route = "UpdatePlanFailure"
            msg = f"Task has been retried {state['check_count']} times. Marking as failed and moving on to the next task."
        else:
            route = "ExploitNode"
            msg = "Task marked for retry. Will attempt exploitation again."
    elif check_verdict == CheckVerdict.FAILURE:
        route = "UpdatePlanFailure"
        msg = "Task marked as failed. Proceeding to update the plan."
    else:
        route = "CheckNode"
        msg = "Unexpected CheckNode output format. Defaulting to retrying the check."

    log_execution_event(
        event_type="routing_decision",
        caller="Checker",
        input={
            "verdict": check_verdict.value if hasattr(check_verdict, "value") else str(check_verdict),
            "check_count": state.get("check_count"),
            "max_retries": max_retries,
        },
        output=route,
        message=msg,
        level=logging.WARNING if route == "CheckNode" else logging.INFO,
    )
    return route
