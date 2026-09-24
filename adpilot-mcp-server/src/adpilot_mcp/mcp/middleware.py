import copy
import logging
from typing import Any

from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware, MiddlewareContext

from adpilot_mcp.config import get_settings
from adpilot_mcp.models.phases import PentestPhase

logger = logging.getLogger(__name__)


def _extract_phase(
    headers: dict[str, Any] | None, header_key: str
) -> PentestPhase | None:
    """Extract and parse pentest phase from headers case-insensitively, handling underscores and hyphens."""
    if not headers:
        return None

    phase_str = headers.get(header_key, None)
    try:
        return PentestPhase(phase_str) if phase_str else None
    except ValueError:
        logger.warning(f"Invalid pentest phase received: {phase_str}")
        return None


class ToolFilterMiddleware(Middleware):
    """
    Middleware that inspects client HTTP headers (e.g. 'pentest_phase')
    and dynamically filters exposed tools based on the current pentest phase.
    """

    async def on_list_tools(self, context: MiddlewareContext, call_next):
        tools = await call_next(context)
        settings = get_settings()

        headers = get_http_headers()
        phase = _extract_phase(headers, settings.agent_phase_header)

        # If phase is None, return all tools. Otherwise, filter tools by phase.
        if phase is not None:
            tools = [tool for tool in tools if phase in tool.tags]
        else:
            tools = [
                tool for tool in tools if PentestPhase.CHECK_RESULTS not in tool.tags
            ]

        # Clean tags from tools to avoid confusing the LLM
        clean_tools = []
        for tool in tools:
            tool_copy = copy.deepcopy(tool)
            tool_copy.tags = set()
            clean_tools.append(tool_copy)

        return clean_tools
