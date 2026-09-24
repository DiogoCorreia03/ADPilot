# ruff: noqa: E402
from pathlib import Path
import sys
import threading

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = Path(__file__).resolve().parent.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Load env at start so it can connect to LangSmith
load_dotenv(BASE_DIR / ".env")

import asyncio
import logging
import time

from langgraph.graph import END, START, StateGraph

from .util import (
    CheckVerdict,
    PentestState,
    Phase,
    get_settings,
    route_after_check,
    route_after_selector,
    route_after_phase_transition,
)
from .util.nodes import (
    check_node,
    create_initial_plan,
    exploit_node,
    final_report,
    initial_scan,
    phase_transition_node,
    select_next_task,
    update_plan_failure,
    update_plan_success,
)
from .util.metrics import format_run_summary, new_run_metrics

# Load settings
settings = get_settings()

# Set up logging and reporting
reportFolder = BASE_DIR / "reports"
reportFolder.mkdir(exist_ok=True)
logFolder = BASE_DIR / "logs"
logFolder.mkdir(exist_ok=True)
executionFolder = BASE_DIR / "executions"
executionFolder.mkdir(exist_ok=True)

t = time.strftime("%Y-%m-%d_%H-%M-%S")

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=f"{logFolder}/run-{t}.log",
    filemode="w",
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

execution_handler = logging.FileHandler(executionFolder / f"execution-{t}.log", mode="w") # TODO maybe use JSONL, see https://gemini.google.com/app/34eebd6d8fb67db3
execution_handler.setLevel(logging.INFO)
execution_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
execution_logger = logging.getLogger("execution")
execution_logger.setLevel(logging.INFO)
execution_logger.addHandler(execution_handler)



async def async_main():
    loop = asyncio.get_running_loop()
    advance_phase_request = asyncio.Event()
    start_time = time.perf_counter()

    def watch_for_phase_advance() -> None:
        print(
            "Type 'n' or 'next' in the terminal to advance to the next phase.",
            flush=True,
        )
        try:
            while True:
                command = sys.stdin.readline()
                if not command:
                    return

                normalized_command = command.strip().lower()
                if normalized_command in {"n", "next"}:
                    loop.call_soon_threadsafe(advance_phase_request.set)
                    print(
                        "Advance-phase request queued for the next selector pass.",
                        flush=True,
                    )
                    logger.debug(
                        "Advance-phase request queued for the next selector pass."
                    )
        except (EOFError, OSError):
            return

    workflow = StateGraph(PentestState)
    workflow.add_node("InitialScan", initial_scan)
    workflow.add_node("InitialPlan", create_initial_plan)
    workflow.add_node("SelectNextTask", select_next_task)
    workflow.add_node("ExploitNode", exploit_node)
    workflow.add_node("CheckNode", check_node)
    workflow.add_node("UpdatePlanSuccess", update_plan_success)
    workflow.add_node("UpdatePlanFailure", update_plan_failure)
    workflow.add_node("PhaseTransitionNode", phase_transition_node)
    workflow.add_node("FinalReport", final_report)

    workflow.add_edge(START, "InitialScan")
    workflow.add_edge("InitialScan", "InitialPlan")
    workflow.add_edge("InitialPlan", "SelectNextTask")

    workflow.add_conditional_edges("SelectNextTask", route_after_selector)

    workflow.add_edge("ExploitNode", "CheckNode")
    workflow.add_edge("UpdatePlanSuccess", "SelectNextTask")
    workflow.add_edge("UpdatePlanFailure", "SelectNextTask")

    workflow.add_conditional_edges("CheckNode", route_after_check)

    workflow.add_conditional_edges("PhaseTransitionNode", route_after_phase_transition)

    workflow.add_edge("FinalReport", END)

    graph = workflow.compile()

    initial_state: PentestState = {
        "dc_ip": settings.DC_IP,
        "network": settings.NETWORK,
        "initial_scan_results": "",
        "tools": "",
        "scan_results": "",
        "scenario": "",
        "plan": "",
        "external_recon_plan": "",
        "initial_access_plan": "",
        "internal_recon_plan": "",
        "lateral_privesc_plan": "",
        "next_task": "",
        "task_result": "",
        "check_count": 0,
        "check_output": "",
        "check_verdict": CheckVerdict.RETRY,
        "current_phase": Phase.EXTERNAL_RECON,
        "advance_phase_request": advance_phase_request,
        "run_metrics": new_run_metrics(),
    }

    if settings.ENABLE_INTERACTIVE_CLI and sys.stdin and sys.stdin.isatty():
        watcher_thread = threading.Thread(target=watch_for_phase_advance, daemon=True)
        watcher_thread.start()
    else:
        print("Interactive CLI phase watcher disabled (non-interactive environment).")
    try:
        final_state = await graph.ainvoke(initial_state)
        print(format_run_summary(final_state["run_metrics"]))
        print(f"external_recon_plan: {final_state['external_recon_plan']}")
        print(f"initial_access_plan: {final_state['initial_access_plan']}")
        print(f"internal_recon_plan: {final_state['internal_recon_plan']}")
        print(f"lateral_privesc_plan: {final_state['lateral_privesc_plan']}")
    finally:
        elapsed_seconds = time.perf_counter() - start_time
        print(f"Execution time: {elapsed_seconds:.2f}s")


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
