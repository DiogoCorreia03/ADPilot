import logging
import re
from typing import Literal

from .config import get_settings
from .execution_logger import log_execution_event
from .state import CheckVerdict, PentestState, Phase

logger = logging.getLogger(__name__)


def route_after_selector(
    state: PentestState,
) -> Literal["ExploitNode", "SelectNextTask", "PhaseTransitionNode"]:
    """
    Routes to the next node after the SelectorNode based on the current state of the pentest.
    """

    # SelectorNode will set the "next_task" field in the state based on the selected task.
    next_task = state["next_task"].strip() if state.get("next_task") else ""

    # Check for phase completion signal (standalone token or surrounded by word boundary)
    if (
        re.search(r"(?<!\w)\[?FINISHED\]?(?!\w)", next_task, re.IGNORECASE)
        or next_task.upper() == "[FINISHED]"
    ):
        logger.info("Phase completion token detected (%s). Transitioning phase.", next_task)
        route = "PhaseTransitionNode"  # Current phase is finished, transition to the next phase.
    elif next_task:
        route = "ExploitNode"  # There is a next task to perform, route to the ExploitNode to execute it.
    else:
        route = "SelectNextTask"  # No next task was selected, route back to the SelectorNode to select a different task.

    log_execution_event(
        event_type="routing_decision",
        caller="Selector",
        phase=state.get("current_phase"),
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
        phase=state.get("current_phase"),
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


def route_after_phase_transition(
    state: PentestState,
) -> Literal["InitialPlan", "FinalReport"]:
    """
    Routes to the next node after the PhaseTransitionNode based on the current phase of the pentest.
    """
    next_phase = state.get("current_phase")
    phase_label = next_phase.name if (next_phase and hasattr(next_phase, "name")) else str(next_phase)

    # Route to FinalReport if all phases completed (None) or legacy wrap-around to EXTERNAL_RECON
    if next_phase is None or next_phase == Phase.EXTERNAL_RECON:
        target = "FinalReport"
        logger.info("All phases completed. Routing to FinalReport.")
    else:
        target = "InitialPlan"
        logger.info("Transitioning to next phase: %s. Routing to InitialPlan.", phase_label)

    return target
