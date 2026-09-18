import logging
import re
from typing import Literal

from .config import get_settings
from .state import CheckVerdict, PentestState, Phase

logger = logging.getLogger(__name__)
execution_logger = logging.getLogger("execution")


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
        return "PhaseTransitionNode"  # Current phase is finished, transition to the next phase.
    elif next_task:
        return "ExploitNode"  # There is a next task to perform, route to the ExploitNode to execute it.
    else:
        return "SelectNextTask"  # No next task was selected, route back to the SelectorNode to select a different task.


def route_after_check(
    state: PentestState,
) -> Literal["ExploitNode", "UpdatePlanSuccess", "UpdatePlanFailure", "CheckNode"]:
    """
    Routes to the next node after the CheckNode based on the output of the check.
    """
    check_verdict = state.get("check_verdict", CheckVerdict.RETRY)
    max_retries = get_settings().CHECK_MAX_RETRIES

    if check_verdict == CheckVerdict.SUCCESS:
        execution_logger.info("Task marked as successful. Proceeding to update the plan.")
        return "UpdatePlanSuccess"

    elif check_verdict == CheckVerdict.RETRY:
        if state["check_count"] > max_retries:
            execution_logger.info(
                "Task has been retried %s times. Marking as failed and moving on to the next task.",
                state["check_count"],
            )
            return "UpdatePlanFailure"

        execution_logger.info("Task marked for retry. Will attempt exploitation again.")
        return "ExploitNode"

    elif check_verdict == CheckVerdict.FAILURE:
        execution_logger.info(
            "Task marked as failed. Proceeding to update the plan."
        )
        return "UpdatePlanFailure"

    else:
        execution_logger.warning(
            "Unexpected CheckNode output format. Defaulting to retrying the check."
        )
        return "CheckNode"


def route_after_phase_transition(
    state: PentestState,
) -> Literal["InitialPlan", "FinalReport"]:
    """
    Routes to the next node after the PhaseTransitionNode based on the current phase of the pentest.
    """
    next_phase = state.get("current_phase")
    phase_label = next_phase.name if (next_phase and hasattr(next_phase, "name")) else str(next_phase)
    execution_logger.info("Transitioning to next phase: %s", phase_label) # TODO maybe print FinalReport if next_phase is None

    # Route to FinalReport if all phases completed (None) or legacy wrap-around to EXTERNAL_RECON
    if next_phase is None or next_phase == Phase.EXTERNAL_RECON:
        logger.info("All phases completed. Routing to FinalReport.")
        return "FinalReport"

    logger.info("Transitioning to next phase: %s. Routing to InitialPlan.", phase_label)
    return "InitialPlan"
