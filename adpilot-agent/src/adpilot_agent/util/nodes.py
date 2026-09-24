import asyncio
import logging
import random
import re
import time
from pathlib import Path
from typing import Any

from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.callbacks import get_usage_metadata_callback

from ..prompts import (
    CHECK_PROMPT,
    EXPLOIT_PROMPT,
    SELECT_TASK_PROMPT,
    SUMMARIZER_PROMPT,
    REPORT_PROMPT,
    build_plan_prompt,
    build_update_plan_prompt,
)
from .exceptions import InvalidLLMResponseError, EmptyLLMResponseError

from .config import get_settings
from .execution_logger import log_execution_event
from .mcp_session import list_tools, mcp_tool_session
from .metrics import record_exploit_node_run, record_token_usage
from .models import get_agent
from .state import CheckVerdict, PentestState, Phase

# Set up logging
logger = logging.getLogger(__name__)


# ! needs to be the same as the ones in the MCP Server
_PHASE_PLAN_KEYS: dict[Phase, str] = {
    Phase.EXTERNAL_RECON: "external_recon_plan",
    Phase.INITIAL_ACCESS: "initial_access_plan",
    Phase.INTERNAL_RECON: "internal_recon_plan",
    Phase.LATERAL_PRIVESC: "lateral_privesc_plan",
}

# ! needs to be the same as the one in the MCP Server
AGENT_PHASE_HEADER = "pentest_phase"  # todo put in .env/config.py


def _format_historical_task_trees(state: PentestState) -> str:
    """Consolidate plans from completed phases into a single clean string with clear section headers."""
    phase_sections = [
        ("External Reconnaissance Phase", state.get("external_recon_plan", "")),
        ("Initial Access Phase", state.get("initial_access_plan", "")),
        ("Internal Reconnaissance Phase", state.get("internal_recon_plan", "")),
        (
            "Lateral Movement & Privilege Escalation Phase",
            state.get("lateral_privesc_plan", ""),
        ),
    ]
    formatted = []
    for title, plan in phase_sections:
        if plan and plan.strip():
            formatted.append(f"### {title}:\n{plan.strip()}")
    return "\n\n".join(formatted)


def _extract_tool_text(result: Any) -> str:
    """Safely extract text content from tool results across lists, dicts, strings, and objects."""
    if isinstance(result, str):
        return result
    if isinstance(result, list):
        if not result:
            return ""
        first = result[0]
        if isinstance(first, str):
            return first
        if isinstance(first, dict):
            return str(first.get("text", first.get("content", "")))
        return getattr(first, "text", str(first))
    if isinstance(result, dict):
        return str(result.get("text", result.get("content", "")))
    return getattr(result, "text", str(result))


def _extract_token_usage(
    usage_metadata: dict[str, Any] | None,
    configured_model_name: str,
) -> dict[str, int] | None:
    """Extract and aggregate token usage across single and hybrid model configurations."""
    if not usage_metadata:
        return None

    # Handle "provider:model"
    model_name_split = configured_model_name.split(":")
    model_name = model_name_split[-1]

    if model_name in usage_metadata:
        return usage_metadata[model_name]
    elif len(usage_metadata) == 1:
        return next(iter(usage_metadata.values()))
    else:  # Hybrid or multi-model setups
        logger.debug("Hybrid/multi-model usage metadata detected: %s", usage_metadata)
        return {
            "input_tokens": sum(
                int(m.get("input_tokens", 0) or 0) for m in usage_metadata.values()
            ),
            "output_tokens": sum(
                int(m.get("output_tokens", 0) or 0) for m in usage_metadata.values()
            ),
            "total_tokens": sum(
                int(m.get("total_tokens", 0) or 0) for m in usage_metadata.values()
            ),
        }


def _extract_ai_message(result: Any) -> AIMessage:
    """Extract and validate the final AIMessage from agent execution result."""
    message = (
        result["messages"][-1]
        if isinstance(result, dict) and "messages" in result and result["messages"]
        else result
    )

    if not isinstance(message, AIMessage):
        raise InvalidLLMResponseError(
            f"Expected AIMessage, got {type(message).__name__}"
        )

    return message


def _extract_text_content(content: Any) -> str:
    """Extract and concatenate text from message content, ignoring internal thinking/reasoning blocks."""
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                if "text" in part and isinstance(part["text"], str):
                    parts.append(part["text"])
                elif part.get("type") in ("thinking", "thought"):
                    continue
                elif "content" in part and isinstance(part["content"], str):
                    parts.append(part["content"])
                else:
                    logger.warning(
                        "Skipping non-text content part in message: %s", part
                    )
            elif hasattr(part, "text") and isinstance(part.text, str):
                parts.append(part.text)
            else:
                logger.warning(
                    "Skipping unhandled content part type: %s", type(part).__name__
                )
        text = "".join(parts)
    else:
        raise InvalidLLMResponseError(
            f"Agent invocation returned invalid result: {content}"
        )

    cleaned = text.strip()
    if not cleaned:
        raise EmptyLLMResponseError("Agent invocation returned empty result.")

    return cleaned


def _compute_retry_delay(
    attempt: int,
    base_delay: float,
    max_delay: float,
) -> float:
    """Compute exponential backoff delay with full jitter."""
    exp_delay = base_delay * (2 ** (attempt - 1))
    jitter = random.uniform(0, base_delay)
    return min(max_delay, exp_delay) + jitter


async def _invoke_agent_once(
    agent: Any,
    messages: list,
    *,
    metrics: dict[str, Any],
    phase: Phase | None,
    caller: str = "Agent",
) -> str:
    """Execute a single agent invocation pass, record token metrics, and return extracted text content."""
    settings = get_settings()
    with get_usage_metadata_callback() as cb:
        result = await agent.ainvoke({"messages": messages})

    usage_data = _extract_token_usage(
        getattr(cb, "usage_metadata", None),
        settings.MODEL_NAME,
    )
    if usage_data:
        record_token_usage(
            metrics,
            phase=phase,
            usage_metadata=usage_data,
        )

    message = _extract_ai_message(result)
    response = _extract_text_content(message.content)

    messages = result.get("messages", []) if isinstance(result, dict) else messages
    prompts = [m for m in messages if not isinstance(m, AIMessage)]
    serialized_prompts = [
        {
            "role": getattr(m, "type", "user"),
            "content": _extract_text_content(getattr(m, "content", str(m))),
        }
        for m in prompts
    ]

    log_execution_event(
        event_type="llm_call",
        caller=caller,
        phase=phase,
        input=serialized_prompts,
        output=response,
    )

    return response


async def _invoke_agent_with_retries(
    agent,
    messages: list,
    *,
    metrics: dict[str, Any],
    phase: Phase | None,
    caller: str = "Agent",
    max_attempts: int | None = None,
) -> str:
    """Retry agent invocation with exponential backoff in case of exceptions."""
    settings = get_settings()
    attempts_limit = max_attempts or settings.LLM_RETRY_MAX_ATTEMPTS
    base_delay = settings.LLM_RETRY_BASE_DELAY
    max_delay = settings.LLM_RETRY_MAX_DELAY

    for attempt in range(1, attempts_limit + 1):
        try:
            return await _invoke_agent_once(
                agent,
                messages,
                metrics=metrics,
                phase=phase,
                caller=caller,
            )
        except Exception as error:
            # If we get here, the exception did not come from tool execution (handled by interceptor),
            # but rather from the agent invocation itself (e.g. LLM timeout, formatting issues).
            log_execution_event(
                event_type="llm_error",
                caller=caller,
                phase=phase,
                message=f"Agent invocation failed for {caller} (attempt {attempt}/{attempts_limit}): {error}",
                level=logging.WARNING if attempt < attempts_limit else logging.ERROR,
            )

            # If this was the last allowed attempt, re-raise the exception.
            if attempt >= attempts_limit:
                raise

            delay = _compute_retry_delay(attempt, base_delay, max_delay)
            log_execution_event(
                event_type="llm_retry",
                caller=caller,
                phase=phase,
                message=f"Retrying agent invocation for {caller} in {delay:.2f} seconds (attempt {attempt + 1}/{attempts_limit}).",
            )
            await asyncio.sleep(delay)

    raise RuntimeError("Unreachable retry loop state in _invoke_agent_with_retries.")


async def initial_scan(state: PentestState) -> dict[str, Any]:
    settings = get_settings()
    phase = state["current_phase"]
    if phase is None:
        logger.warning("Current phase is None.")
        raise RuntimeError("Current phase is required for initial scan.")
    metrics = state["run_metrics"]

    async with mcp_tool_session(
        limit_scope_label="InitialScan",
        extra_headers={
            AGENT_PHASE_HEADER: "shell_only"
        },  # TODO meter no .env/config.py
        phase=phase.value,
        metrics=metrics,
    ) as tools:
        shell_tool = next((t for t in tools if "shell_exec" in t.name), None)
        if shell_tool is None:
            logger.error("Shell tool not found among loaded tools.")
            raise RuntimeError("Shell tool is required for initial scan.")

        # Run initial scan
        raw_scan_result = await shell_tool.ainvoke(
            {
                "command": f"nmap -sV -sC --reason --open -T4 --exclude {settings.IGNORED_HOSTS_NMAP_EXCLUDE} {state['network']}",
                # TODO scripts a experimentar: smb-os-discovery,smb-protocols,smb-security-mode, ssl-cert, http-title,http-headers, snmp-info, modbus-discover,bacnet-info,enip-info,s7-info; -sU (UDP scan)
            }
        )

        scan_result = _extract_tool_text(raw_scan_result)
        logger.debug(f"Initial NMAP scan raw output: {scan_result}")

    messages = [
        SystemMessage(SUMMARIZER_PROMPT),
        HumanMessage(scan_result),
    ]

    # Summarize initial scan results
    agent = get_agent("InitialScan")
    scan_result = await _invoke_agent_with_retries(
        agent,
        messages,
        metrics=metrics,
        phase=phase,
        caller="InitialScan",
    )
    logger.debug(f"Initial scan analysis result:\n{scan_result}")

    return {
        "initial_scan_results": scan_result,
        "run_metrics": metrics,
    }


async def create_initial_plan(state: PentestState) -> dict[str, Any]:
    settings = get_settings()
    metrics = state["run_metrics"]

    scan_results = state.get("initial_scan_results", "")
    if not scan_results:
        logger.error(
            "No initial scan results found in state when creating initial plan."
        )
        raise RuntimeError("Initial scan results are required to create initial plan.")

    phase = state.get("current_phase", "")
    if not phase:
        logger.error("No current phase found in state when creating initial plan.")
        raise RuntimeError("Current phase is required to create initial plan.")

    async with mcp_tool_session(
        extra_headers={AGENT_PHASE_HEADER: phase.value},
        phase=phase.value,
        metrics=metrics,
    ) as tools:
        tools_str = list_tools(tools)

    log_execution_event(
        event_type="tools_loaded",
        phase=phase,
        message=f"Loaded {len(tools)} tools for phase {phase.value}: {', '.join([getattr(t, 'name', str(t)) for t in tools])}",
        tools=tools_str,
    )

    messages = [
        SystemMessage(
            build_plan_prompt(
                phase=phase,
                dc_ip=settings.DC_IP,
                network=settings.NETWORK,
                ignored_hosts=settings.IGNORED_HOSTS_PROMPT,
                scan_results=scan_results,
                tools=tools_str,
                previous_task_trees=_format_historical_task_trees(state),
            )
        ),
        HumanMessage(
            "Provide the hierarchical task plan as answer. Break down the overall objective into smaller tasks and subtasks. Do not include a title or an appendix."
        ),
    ]

    # This agent doesn't need to (and should not) call any tools, but we include the tool list in the scenario prompt to give it context about the capabilities of the workers.

    # Create the initial plan
    agent = get_agent("InitialPlan")
    plan = await _invoke_agent_with_retries(
        agent,
        messages,
        metrics=metrics,
        phase=phase,
        caller="Planner",
    )
    logger.info(f"Initial plan created:\n{plan}")

    return {
        "plan": plan,
        "run_metrics": metrics,
        "tools": tools_str,
        "scan_results": scan_results,
    }


async def select_next_task(state: PentestState) -> dict[str, Any]:
    metrics = state["run_metrics"]

    advance_phase_request = state.get("advance_phase_request")
    if (
        isinstance(advance_phase_request, asyncio.Event)
        and advance_phase_request.is_set()
    ):
        logger.info("Advance-phase request received. Finishing current phase.")
        advance_phase_request.clear()
        return {
            "next_task": "FINISHED",
            "run_metrics": metrics,
            "check_count": 0,
        }

    plan = state.get("plan", "")
    if not plan:
        logger.warning("No plan found in state when selecting next task.")
        raise RuntimeError("Plan is required to select next task.")

    phase = state.get("current_phase", "")
    if not phase:
        logger.warning("No current phase found in state when creating initial plan.")
        raise RuntimeError("Current phase is required to create initial plan.")

    tools = state.get("tools", "")
    if not tools:
        logger.warning("No tools found in state when selecting next task.")
        raise RuntimeError("Tools are required to select next task.")

    messages = [
        SystemMessage(
            SELECT_TASK_PROMPT.format(
                task_tree=plan, phase_name=phase.value, tools=tools
            )
        ),
        HumanMessage(
            "Select the next task to be executed from the provided task tree, as specified before. Return only the selected task, without any additional commentary or formatting."
        ),
    ]

    # Select the next task
    agent = get_agent("SelectNextTask")
    next_task = await _invoke_agent_with_retries(
        agent,
        messages,
        metrics=metrics,
        phase=phase,
        caller="Selector",
    )
    logger.info(f"Selected next task: {next_task}")

    return {
        "next_task": next_task,
        "run_metrics": metrics,
        "check_count": 0,  # reset check count for new task
    }


async def exploit_node(state: PentestState) -> dict[str, Any]:
    settings = get_settings()
    metrics = state["run_metrics"]

    task = state.get("next_task", "")
    if not task:
        logger.warning("No next task found in state when attempting exploitation.")
        raise RuntimeError("Next task is required to attempt exploitation.")

    phase = state.get("current_phase", "")
    if not phase:
        logger.warning("No current phase found in state when attempting exploitation.")
        raise RuntimeError("Current phase is required for exploitation.")

    record_exploit_node_run(metrics)

    async with mcp_tool_session(
        tool_call_limit=settings.EXPLOIT_MAX_TOOL_CALLS,
        same_tool_streak_limit=settings.EXPLOIT_MAX_SAME_TOOL_CALLS_IN_A_ROW,
        limit_scope_label="ExploitNode",
        extra_headers={AGENT_PHASE_HEADER: phase.value},
        phase=phase.value,
        metrics=metrics,
    ) as tools:
        messages = [
            SystemMessage(
                EXPLOIT_PROMPT.format(
                    task=task,
                    tools=list_tools(tools),
                    max=3,
                    tool_call_limit=settings.EXPLOIT_MAX_TOOL_CALLS,
                    same_tool_streak_limit=settings.EXPLOIT_MAX_SAME_TOOL_CALLS_IN_A_ROW,
                    dc_ip=settings.DC_IP,
                    network=settings.NETWORK,
                    ignored_hosts=settings.IGNORED_HOSTS_PROMPT,
                )
            ),
            HumanMessage(
                "Attempt to execute the task as specified before. Use the provided tools to execute commands and achieve the task objective. Be concise in your actions and focus on achieving the task objective efficiently."
            ),
        ]

        # Attempt the exploitation task
        agent = get_agent("ExploitNode", tools=tools)
        exploit_output = await _invoke_agent_with_retries(
            agent,
            messages,
            metrics=metrics,
            phase=phase,
            caller="Executor",
        )
        logger.info(f"Exploit output: {exploit_output}")

    return {
        "task_result": exploit_output,
        "run_metrics": metrics,
    }


async def check_node(state: PentestState) -> dict[str, Any]:
    task = state.get("next_task", "")
    if not task:
        logger.error("No next task found in state when checking task results.")
        raise RuntimeError("Next task is required to check task results.")

    task_result = state.get("task_result", "")
    if not task_result:
        logger.error("No task result found in state when checking task results.")
        raise RuntimeError("Task result is required to check task results.")

    metrics = state["run_metrics"]
    phase = state["current_phase"]
    if phase is None:
        logger.error("Current phase is None.")
        raise RuntimeError("Current phase is required for check node.")

    async with mcp_tool_session(
        limit_scope_label="CheckNode",
        extra_headers={AGENT_PHASE_HEADER: "check_results"},
        phase=phase.value,
        metrics=metrics,
    ) as tools:
        messages = [
            SystemMessage(CHECK_PROMPT.format(task=task, result=task_result)),
            HumanMessage("Evaluate the execution of the task as specified before."),
        ]

        agent = get_agent("CheckNode", tools=tools)
        check_output = await _invoke_agent_with_retries(
            agent,
            messages,
            metrics=metrics,
            phase=phase,
            caller="Checker",
        )

    logger.info(f"Check output: {check_output}")
    check_count = state.get("check_count", 0) + 1  # Increment check count for this task
    check_verdict = _parse_check_verdict(str(check_output))

    return {
        "check_output": check_output,
        "check_verdict": check_verdict,
        "run_metrics": metrics,
        "check_count": check_count,
    }


def _parse_check_verdict(check_output: str) -> CheckVerdict:
    # 1. Look for explicit VERDICT: [VERDICT] or VERDICT: VERDICT
    match = re.search(
        r"\bVERDICT:\s*\[?(SUCCESS|RETRY|FAILURE)\]?\b", check_output, re.IGNORECASE
    )
    if match:
        return CheckVerdict[match.group(1).upper()]

    # 2. Look for standalone bracketed tokens like [SUCCESS], [RETRY], [FAILURE]
    bracket_match = re.search(
        r"\[(SUCCESS|RETRY|FAILURE)\]", check_output, re.IGNORECASE
    )
    if bracket_match:
        return CheckVerdict[bracket_match.group(1).upper()]

    # 3. Fall back to word boundary checks. Checking retry first prioritizes recovery when a command fails but can be re-attempted.
    if re.search(r"\bretry\b", check_output, re.IGNORECASE):
        logger.warning(
            "Falling back to retry verdict parsing from free-form checker output."
        )
        return CheckVerdict.RETRY

    if re.search(r"\b(failure|failed)\b", check_output, re.IGNORECASE):
        logger.warning(
            "Falling back to failure verdict parsing from free-form checker output."
        )
        return CheckVerdict.FAILURE

    if re.search(r"\bsuccess(ful)?\b", check_output, re.IGNORECASE):
        logger.warning(
            "Falling back to success verdict parsing from free-form checker output."
        )
        return CheckVerdict.SUCCESS

    logger.warning("Unable to parse checker verdict. Defaulting to failure.")
    return CheckVerdict.FAILURE  # TODO maybe default to RETRY instead of FAILURE, to avoid skipping tasks that might be recoverable, perguntar


async def _update_plan_with_outcome(
    state: PentestState,
    *,
    verdict: CheckVerdict,
) -> dict[str, Any]:
    settings = get_settings()
    metrics = state["run_metrics"]

    tools = state.get("tools", "")
    if not tools:
        logger.warning("No tools found in state when updating plan.")
        raise RuntimeError("Tools are required to update plan.")

    plan = state.get("plan", "")
    if not plan:
        logger.warning("No plan found in state when updating plan.")
        raise RuntimeError("Plan is required to update plan.")

    task = state.get("next_task", "")
    if not task:
        logger.warning("No next task found in state when updating plan.")
        raise RuntimeError("Next task is required to update plan.")

    task_result = state.get("task_result", "")
    if not task_result:
        logger.warning("No task result found in state when updating plan.")
        raise RuntimeError("Task result is required to update plan.")

    phase = state.get("current_phase", "")
    if not phase:
        logger.warning("No current phase found in state when updating plan.")
        raise RuntimeError("Current phase is required to update plan.")

    messages = [
        SystemMessage(
            build_update_plan_prompt(
                phase=phase,
                dc_ip=settings.DC_IP,
                network=settings.NETWORK,
                ignored_hosts=settings.IGNORED_HOSTS_PROMPT,
                tools=tools,
                plan=plan,
                task=task,
                task_result=task_result,
                task_verdict=verdict.value,
                previous_task_trees=_format_historical_task_trees(state),
            )
        ),
        HumanMessage(
            "Update the existing plan as specified before. Return only the updated plan, without any additional commentary or formatting."
        ),
    ]

    agent = get_agent("UpdatePlan")
    updated_plan = await _invoke_agent_with_retries(
        agent,
        messages,
        metrics=metrics,
        phase=phase,
        caller="Updater",
    )
    logger.info(f"Updated plan: {updated_plan}")

    return {
        "plan": updated_plan,
        "run_metrics": metrics,
    }


async def update_plan_success(state: PentestState) -> dict[str, Any]:
    return await _update_plan_with_outcome(state, verdict=CheckVerdict.SUCCESS)


async def update_plan_failure(state: PentestState) -> dict[str, Any]:
    return await _update_plan_with_outcome(state, verdict=CheckVerdict.FAILURE)


async def phase_transition_node(state: PentestState) -> dict[str, Any]:
    current_phase = state["current_phase"]

    if current_phase is None:
        logger.warning("Current phase is None.")
        raise RuntimeError("Current phase is required for phase transition.")

    next_phase = current_phase.next()

    log_execution_event(
        event_type="phase_transition",
        caller="PhaseTransition",
        phase=current_phase,
        message=f"Phase transition from {current_phase.value} to {next_phase.value if next_phase else 'END'}",
    )

    plan_key = _PHASE_PLAN_KEYS.get(current_phase)
    if plan_key is None:
        logger.warning("Unexpected phase value: %s", current_phase)
        raise RuntimeError(f"Unsupported phase transition from {current_phase!r}.")

    return {
        plan_key: state["plan"],
        "current_phase": next_phase,
    }


async def final_report(state: PentestState) -> dict[str, Any]:
    metrics = state["run_metrics"]
    phase = state["current_phase"]

    async with mcp_tool_session(
        limit_scope_label="FinalReport",  # TODO maybe remover
        metrics=metrics,  # TODO maybe remover
    ) as tools:
        credentials_result = ""
        credentials_tool = next((t for t in tools if "credentials_get" in t.name), None)
        if credentials_tool is None:
            logger.warning("Credentials tool not found among loaded tools.")
        else:
            raw_credentials_result = await credentials_tool.ainvoke({})
            logger.debug(f"Retrieved credentials: {raw_credentials_result}")
            credentials_result = _extract_tool_text(raw_credentials_result)

    messages = [
        SystemMessage(
            REPORT_PROMPT.format(
                task_trees=_format_historical_task_trees(state),
                credentials=credentials_result,
            )
        ),
        HumanMessage(
            "Generate a comprehensive report, as specified before, based on the provided information."
        ),
    ]
    agent = get_agent("FinalReport")
    final_report = await _invoke_agent_with_retries(
        agent,
        messages,
        metrics=metrics,
        phase=phase,
        caller="Reporter",
    )

    sanitized_model = re.sub(r"[^\w\-.]", "_", get_settings().MODEL_NAME)
    base_dir = Path(__file__).resolve().parent.parent.parent
    report_path = (
        base_dir
        / "reports"
        / f"{sanitized_model}-{time.strftime('%Y-%m-%d_%H-%M-%S')}.md"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(final_report, encoding="utf-8")

    print(f"Final report written to {report_path}")
    logger.debug(f"Final report: {final_report}")
    logger.info(f"Final report written to {report_path}")

    return {}
