import asyncio
import json
import logging
from base64 import b64encode
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import Any

from httpx import AsyncClient, Timeout
from langchain.messages import ToolMessage
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from .config import get_settings
from .metrics import record_tool_call

# Set up logging
logger = logging.getLogger(__name__)
execution_logger = logging.getLogger("execution")


class HTTPClient(AsyncClient):
    def __init__(
        self,
        auth_token: str,
        *args,
        extra_headers: dict[str, str] | None = None,
        **kwargs,
    ):
        # Allow long-running pentest tool executions (read=None) while enforcing connection & write limits
        kwargs.setdefault(
            "timeout", Timeout(connect=15.0, read=None, write=30.0, pool=15.0)
        )

        headers = {
            # Ngrok's authorization header
            "Authorization": f"Basic {b64encode(auth_token.encode()).decode()}",
        }
        if extra_headers:
            headers.update(extra_headers)

        super().__init__(
            headers=headers,
            *args,
            **kwargs,
        )


def record_tool_result(
    result: Any,
    metrics: dict[str, Any] | None,
    limit_scope_label: str,
    phase_name: str | None = None,
) -> None:
    if metrics is None:
        return

    is_error = True  # Default to error unless we can confirm success
    content_list = getattr(result, "content", None)
    if content_list and len(content_list) > 0:
        first_part = content_list[0]
        part_type = getattr(first_part, "type", None)
        if part_type != "text" and not hasattr(first_part, "text"):
            logger.warning(f"Unexpected result type: {first_part}. Expected 'text'.")
            raise TypeError(f"Unexpected result type: {part_type}. Expected 'text'.")

        result_string = getattr(first_part, "text", str(first_part))
        try:
            result_json = json.loads(result_string)
            if isinstance(result_json, dict):
                if "success" in result_json:
                    is_error = not result_json["success"]
                elif "returncode" in result_json:
                    is_error = result_json["returncode"] != 0
        except (json.JSONDecodeError, TypeError, KeyError):
            logger.warning(f"Failed to decode JSON from tool result: {result_string}")
            is_error = True

    record_tool_call(
        metrics,
        phase=phase_name,
        scope_label=limit_scope_label,
        is_error=is_error,
    )


def list_tools(tools) -> str:
    out = []
    for tool in tools:
        args_schema = getattr(tool, "args_schema", None) or getattr(tool, "args", "")
        a = ""
        a += f"## Tool Name: {tool.name}\n"
        a += f"### Description: {tool.description}\n"
        a += f"**Args Schema:** ```{args_schema}```\n"
        out.append(a)
    return ("\n").join(out)


def _format_tool_error(request: MCPToolCallRequest, error: Exception) -> ToolMessage:
    """Build an observation string that the model can use to self-correct after a tool call fails."""
    runtime = request.runtime
    tool_call_id = (
        getattr(runtime, "tool_call_id", None)
        or getattr(request, "tool_call_id", None)
        or "call_error"
    )
    return ToolMessage(
        "TOOL_CALL_ERROR\n"
        f"tool: {request.name}\n"
        f"args: {request.args}\n"
        f"error_type: {error.__class__.__name__}\n"
        f"error_message: {error}\n"
        "next_step: Fix Action Input so it matches the tool parameter schema and retry.",
        tool_call_id=tool_call_id,
    )


def _format_tool_limit_reached(
    request: MCPToolCallRequest,
    *,
    limit: int,
    calls_used: int,
    scope_label: str,
) -> ToolMessage:
    """Build an observation string for deterministic behavior when tool budget is exhausted."""
    runtime = request.runtime
    tool_call_id = (
        getattr(runtime, "tool_call_id", None)
        or getattr(request, "tool_call_id", None)
        or "call_limit"
    )
    return ToolMessage(
        "TOOL_CALL_LIMIT_REACHED\n"
        f"scope: {scope_label}\n"
        f"tool: {request.name}\n"
        f"args: {request.args}\n"
        f"tool_call_limit: {limit}\n"
        f"tool_calls_used: {calls_used}\n"
        "next_step: Stop tool usage and provide final response with evidence gathered so far.",
        tool_call_id=tool_call_id,
    )


def _format_tool_consecutive_limit_reached(
    request: MCPToolCallRequest,
    *,
    consecutive_limit: int,
    current_consecutive_calls: int,
    scope_label: str,
) -> ToolMessage:
    """Build an observation string when the same tool is called too many times in a row."""
    runtime = request.runtime
    tool_call_id = (
        getattr(runtime, "tool_call_id", None)
        or getattr(request, "tool_call_id", None)
        or "call_streak_limit"
    )
    return ToolMessage(
        "TOOL_CALL_CONSECUTIVE_LIMIT_REACHED\n"
        f"scope: {scope_label}\n"
        f"tool: {request.name}\n"
        f"args: {request.args}\n"
        f"same_tool_streak_limit: {consecutive_limit}\n"
        f"same_tool_streak_count: {current_consecutive_calls}\n"
        "next_step: Stop repeating this tool. Either finalize with gathered evidence or switch approach.",
        tool_call_id=tool_call_id,
    )


def _build_tool_interceptor(
    *,
    tool_call_limit: int | None = None,
    same_tool_streak_limit: int | None = None,
    limit_scope_label: str = "MCPToolSession",
    phase: str | None = None,
    metrics: dict[str, Any] | None = None,
) -> Callable[..., Any]:
    tool_calls_used = 0
    last_tool_name = ""
    same_tool_streak_count = 0
    lock = asyncio.Lock()

    async def _tool_interceptor(request: MCPToolCallRequest, handler):
        """Log tool calls before and after execution, optionally enforcing a per-session call limit."""
        nonlocal tool_calls_used, last_tool_name, same_tool_streak_count
        phase_name = phase
        if phase_name is None and request.headers:
            phase_name = request.headers.get("pentest_phase")

        async with lock:
            if tool_call_limit is not None and tool_calls_used >= tool_call_limit:
                execution_logger.info(
                    "Tool call limit reached for %s (%s/%s). Blocking tool '%s'. Agent must provide final response with gathered evidence.",
                    limit_scope_label,
                    tool_calls_used,
                    tool_call_limit,
                    request.name,
                )
                if metrics is not None:
                    record_tool_call(
                        metrics,
                        phase=phase_name,
                        scope_label=limit_scope_label,
                        is_error=True,
                    )
                return _format_tool_limit_reached(
                    request,
                    limit=tool_call_limit,
                    calls_used=tool_calls_used,
                    scope_label=limit_scope_label,
                )

            prospective_streak = (
                same_tool_streak_count + 1 if request.name == last_tool_name else 1
            )
            if (
                same_tool_streak_limit is not None
                and prospective_streak > same_tool_streak_limit
            ):
                execution_logger.info(
                    "Consecutive tool call limit reached for %s using tool '%s' (%s/%s). Agent must switch to a different tool or finalize with gathered evidence.",
                    limit_scope_label,
                    request.name,
                    same_tool_streak_count,
                    same_tool_streak_limit,
                )
                if metrics is not None:
                    record_tool_call(
                        metrics,
                        phase=phase_name,
                        scope_label=limit_scope_label,
                        is_error=True,
                    )
                return _format_tool_consecutive_limit_reached(
                    request,
                    consecutive_limit=same_tool_streak_limit,
                    current_consecutive_calls=same_tool_streak_count,
                    scope_label=limit_scope_label,
                )

            tool_calls_used += 1
            current_calls = tool_calls_used
            last_tool_name = request.name
            same_tool_streak_count = prospective_streak
            current_streak = same_tool_streak_count

        execution_logger.info(
            "Calling tool (%s/%s) in %s: %s (streak %s/%s) with args: %s",
            current_calls,
            tool_call_limit if tool_call_limit is not None else "unbounded",
            limit_scope_label,
            request.name,
            current_streak,
            same_tool_streak_limit
            if same_tool_streak_limit is not None
            else "unbounded",
            request.args,
        )

        try:
            result = await handler(request)
        except Exception as error:
            execution_logger.info(
                "Tool %s failed with error: %s.",
                request.name,
                error,
            )
            # Return a structured observation instead of raising so the model can recover.
            if metrics is not None:
                record_tool_call(
                    metrics,
                    phase=phase_name,
                    scope_label=limit_scope_label,
                    is_error=True,
                )
            return _format_tool_error(request, error)

        try:
            record_tool_result(result, metrics, limit_scope_label, phase_name)
        except Exception:
            logger.warning("Failed to record tool result metrics")
        execution_logger.info(f"Tool {request.name} returned: {result}")
        return result

    return _tool_interceptor


@asynccontextmanager
async def mcp_tool_session(
    *,
    tool_call_limit: int | None = None,
    same_tool_streak_limit: int | None = None,
    limit_scope_label: str = "MCPToolSession",
    extra_headers: dict[str, str] | None = None,
    phase: str | None = None,
    metrics: dict[str, Any] | None = None,
) -> AsyncGenerator[list[Any]]:
    settings = get_settings()
    tool_interceptor = _build_tool_interceptor(
        tool_call_limit=tool_call_limit,
        same_tool_streak_limit=same_tool_streak_limit,
        limit_scope_label=limit_scope_label,
        phase=phase,
        metrics=metrics,
    )

    async with (
        HTTPClient(
            auth_token=settings.ATTACKER_MACHINE_AUTH_TOKEN.get_secret_value(),
            extra_headers=extra_headers,
        ) as http_client,
        streamable_http_client(
            str(settings.ATTACKER_MACHINE_URL), http_client=http_client
        ) as (
            read,
            write,
            _,
        ),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        logger.debug("Connected to MCP session successfully.")
        tools = await load_mcp_tools(session, tool_interceptors=[tool_interceptor])
        yield tools
