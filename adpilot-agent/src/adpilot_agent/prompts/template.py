import logging


from .planner import PLAN_PROMPT
from .updater import UPDATE_PLAN_PROMPT

logger = logging.getLogger(__name__)



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
    dc_ip: str,
    network: str,
    ignored_hosts: str,
    scan_results: str = "",
    tools: str = "",
) -> str:
    formatted_scan_results = (_format_scan_results(scan_results))

    return PLAN_PROMPT.format(
        dc_ip=dc_ip,
        network=network,
        ignored_hosts=ignored_hosts,
        scan_results=formatted_scan_results,
        tools=tools,
    )


def build_update_plan_prompt(
    dc_ip: str,
    network: str,
    ignored_hosts: str,
    tools: str,
    plan: str,
    task: str,
    task_result: str,
    task_verdict: str,
) -> str:

    return UPDATE_PLAN_PROMPT.format(
        dc_ip=dc_ip,
        network=network,
        ignored_hosts=ignored_hosts,
        tools=tools,
        plan=plan,
        task=task,
        task_result=task_result,
        task_verdict=task_verdict,
    )
