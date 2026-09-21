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

from .util import (
    get_agent,
    get_settings,
    mcp_tool_session,
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

execution_handler = logging.FileHandler(
    executionFolder / f"execution-{t}.log", mode="w"
)  # TODO maybe use JSONL, see https://gemini.google.com/app/34eebd6d8fb67db3
execution_handler.setLevel(logging.INFO)
execution_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
execution_logger = logging.getLogger("execution")
execution_logger.setLevel(logging.INFO)
execution_logger.addHandler(execution_handler)

# TODO successful tasks should probably be marked with SUCCESS instead of DONE

# ! needs to be the same as the one in the MCP Server
AGENT_PHASE_HEADER = "pentest_phase"  # todo put in .env/config.py


async def async_main():
    start_time = time.perf_counter()

    try:
        metrics = new_run_metrics()
        async with mcp_tool_session(
            # extra_headers={AGENT_PHASE_HEADER: "shell_only"}, # use when you want only shell tool
            metrics=metrics,
        ) as tools:
            agent = get_agent(tools=tools)
            # TODO queremos este llm simples a gerar um report no fim ou só olhamos para os execution logs?

            messages = [
                SystemMessage(), # TODO prompt gigante
                HumanMessage(),
            ]
            
        try:
            return await invoke_agent_once(
                agent,
                messages,
                metrics=metrics,
            )
        except Exception as error:
            # If we get here, the exception did not come from tool execution (handled by interceptor),
            # but rather from the agent invocation itself (e.g. LLM timeout, formatting issues).
            execution_logger.info(
                "Agent invocation failed: %s",
                error,
            )

        print(format_run_summary(metrics))
    finally:
        elapsed_seconds = time.perf_counter() - start_time
        print(f"Execution time: {elapsed_seconds:.2f}s")


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
