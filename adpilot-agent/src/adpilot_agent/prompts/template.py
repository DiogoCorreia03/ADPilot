import logging

from ..util.state import Phase

from .planner import PLAN_PROMPT
from .specs import get_phase_spec
from .updater import UPDATE_PLAN_PROMPT

logger = logging.getLogger(__name__)


def _format_previous_trees(previous_task_trees: str) -> str:
    cleaned = previous_task_trees.strip() if previous_task_trees else ""
    if not cleaned:
        return ""
    # Avoid duplicate tags if already wrapped
    if "<previous_task_trees>" in cleaned:
        return f"Previous Phases Completed Task Trees:\n{cleaned}"
    return (
        "Previous Phases Completed Task Trees:\n<previous_task_trees>\n"
        + cleaned
        + "\n</previous_task_trees>"
    )


def _format_scan_results(scan_results: str) -> str:
    cleaned = scan_results.strip() if scan_results else ""
    if not cleaned:
        return ""
    # Avoid duplicate tags if already wrapped
    if "<scan_results>" in cleaned:
        return f"Network reconnaissance summary:\n{cleaned}"
    return (
        "Network reconnaissance summary:\n<scan_results>\n"
        + cleaned
        + "\n</scan_results>"
    )


def build_plan_prompt(
    phase: Phase,
    dc_ip: str,
    network: str,
    ignored_hosts: str,
    scan_results: str = "",
    tools: str = "",
    previous_task_trees: str = "",
) -> str:
    spec = get_phase_spec(phase)
    # External recon phase does not use previous phase trees
    formatted_trees = (
        ""
        if phase == Phase.EXTERNAL_RECON
        else _format_previous_trees(previous_task_trees)
    )

    # Only external recon phase uses network scan results
    formatted_scan_results = (
        _format_scan_results(scan_results) if phase == Phase.EXTERNAL_RECON else ""
    )

    return PLAN_PROMPT.format(
        dc_ip=dc_ip,
        network=network,
        ignored_hosts=ignored_hosts,
        scan_results=formatted_scan_results,
        previous_task_trees=formatted_trees,
        tools=tools,
        phase_name=spec.name,
        phase_objective=spec.objective,
        phase_scope=spec.scope,
        forbidden_task_categories=spec.forbidden_categories,
        allowed_task_categories=spec.allowed_categories,
        planning_principle_examples=spec.planning_principle_examples,
        phase_generation_rules=spec.generation_rules,
    )


def build_update_plan_prompt(
    phase: Phase,
    dc_ip: str,
    network: str,
    ignored_hosts: str,
    tools: str,
    plan: str,
    task: str,
    task_result: str,
    task_verdict: str,
    previous_task_trees: str = "",
) -> str:
    spec = get_phase_spec(phase)
    # External recon phase does not use previous phase trees
    formatted_trees = (
        ""
        if phase == Phase.EXTERNAL_RECON
        else _format_previous_trees(previous_task_trees)
    )

    return UPDATE_PLAN_PROMPT.format(
        dc_ip=dc_ip,
        network=network,
        ignored_hosts=ignored_hosts,
        previous_task_trees=formatted_trees,
        tools=tools,
        plan=plan,
        task=task,
        task_result=task_result,
        task_verdict=task_verdict,
        phase_name=spec.name,
        phase_objective=spec.objective,
        phase_scope=spec.scope,
        forbidden_task_categories=spec.forbidden_categories,
        allowed_task_categories=spec.allowed_categories,
        phase_generation_rules=spec.generation_rules,
    )
