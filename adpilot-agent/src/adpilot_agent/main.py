import re
import sys
from pathlib import Path

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

from langchain.messages import HumanMessage, SystemMessage

from .prompts import build_big_prompt
from .util import (
    get_agent,
    get_settings,
    list_tools,
    mcp_tool_session,
    setup_execution_logger,
)
from .util.metrics import format_run_summary, new_run_metrics
from .util.nodes import invoke_agent_once

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

execution_logger, execution_handler = setup_execution_logger(
    executionFolder / f"execution-{t}.jsonl"
)

# ! needs to be the same as the one in the MCP Server
AGENT_PHASE_HEADER = "pentest_phase"  # todo put in .env/config.py


async def async_main():
    start_time = time.perf_counter()
    metrics = new_run_metrics()

    try:
        async with mcp_tool_session(
            # extra_headers={AGENT_PHASE_HEADER: "shell_only"}, # use when you want only shell tool
            same_tool_streak_limit=settings.EXPLOIT_MAX_SAME_TOOL_CALLS_IN_A_ROW,
            metrics=metrics,
        ) as tools:
            agent = get_agent(tools=tools)

            messages = [
                SystemMessage(
                    build_big_prompt(
                        dc_ip=settings.DC_IP,
                        network=settings.NETWORK,
                        ignored_hosts=str(settings.IGNORED_HOSTS),
                        tools=list_tools(tools),
                    )
                ),
                HumanMessage("Start the penetration test as specified in the prompt."),
            ]

            try:
                result = await invoke_agent_once(
                    agent,
                    messages,
                    metrics=metrics,
                )

                sanitized_model = re.sub(r"[^\w\-.]", "_", get_settings().MODEL_NAME)
                report_path = (
                    BASE_DIR
                    / "reports"
                    / f"{sanitized_model}-{time.strftime('%Y-%m-%d_%H-%M-%S')}.md"
                )
                report_path.parent.mkdir(parents=True, exist_ok=True)
                report_path.write_text(result, encoding="utf-8")

            except Exception as error:
                # If we get here, the exception did not come from tool execution (handled by interceptor),
                # but rather from the agent invocation itself (e.g. LLM timeout, formatting issues).
                execution_logger.info(
                    "Agent invocation failed: %s",
                    error,
                )
    finally:
        print(format_run_summary(metrics))
        elapsed_seconds = time.perf_counter() - start_time
        print(f"Execution time: {elapsed_seconds:.2f}s")


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
