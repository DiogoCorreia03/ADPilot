from adpilot_agent.util.state import CheckVerdict, PentestState, Phase
from adpilot_agent.util.routers import route_after_selector, route_after_check, route_after_phase_transition


def test_route_after_selector_with_task(base_state: PentestState):
    base_state["next_task"] = "1. Enumerate SMB"
    assert route_after_selector(base_state) == "ExploitNode"


def test_route_after_selector_finished(base_state: PentestState):
    base_state["next_task"] = "[FINISHED]"
    assert route_after_selector(base_state) == "PhaseTransitionNode"

    base_state["next_task"] = "Selected task: [FINISHED]"
    assert route_after_selector(base_state) == "PhaseTransitionNode"

    base_state["next_task"] = "All tasks completed. FINISHED"
    assert route_after_selector(base_state) == "PhaseTransitionNode"


def test_route_after_selector_empty(base_state: PentestState):
    base_state["next_task"] = ""
    assert route_after_selector(base_state) == "SelectNextTask"


def test_route_after_check_success(base_state: PentestState):
    base_state["check_verdict"] = CheckVerdict.SUCCESS
    assert route_after_check(base_state) == "UpdatePlanSuccess"


def test_route_after_check_retry(base_state: PentestState):
    base_state["check_verdict"] = CheckVerdict.RETRY
    base_state["check_count"] = 1
    assert route_after_check(base_state) == "ExploitNode"


def test_route_after_check_retry_limit_exceeded(base_state: PentestState):
    base_state["check_verdict"] = CheckVerdict.RETRY
    base_state["check_count"] = 4
    assert route_after_check(base_state) == "UpdatePlanFailure"


def test_route_after_check_failure(base_state: PentestState):
    base_state["check_verdict"] = CheckVerdict.FAILURE
    assert route_after_check(base_state) == "UpdatePlanFailure"


def test_route_after_phase_transition_intermediate(base_state: PentestState):
    base_state["current_phase"] = Phase.INITIAL_ACCESS
    assert route_after_phase_transition(base_state) == "InitialPlan"


def test_route_after_phase_transition_completed(base_state: PentestState):
    # Wrap-around to EXTERNAL_RECON indicates completion
    base_state["current_phase"] = Phase.EXTERNAL_RECON
    assert route_after_phase_transition(base_state) == "FinalReport"


def test_route_after_phase_transition_none_completed(base_state: PentestState):
    # Explicit None also indicates completion
    base_state["current_phase"] = None
    assert route_after_phase_transition(base_state) == "FinalReport"
