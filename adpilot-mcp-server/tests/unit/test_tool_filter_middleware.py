import pytest
from unittest.mock import MagicMock, patch
from fastmcp.tools import Tool
from adpilot_mcp.mcp.middleware import ToolFilterMiddleware
from adpilot_mcp.models.phases import PentestPhase


@pytest.mark.asyncio
async def test_tool_filter_middleware_no_phase_returns_all_tools_with_cleared_tags():
    middleware = ToolFilterMiddleware()
    context = MagicMock()

    dummy_tool1 = Tool.from_function(
        lambda: None,
        name="tool_recon",
        description="recon tool",
        tags={PentestPhase.EXTERNAL_RECONNAISSANCE},
    )
    dummy_tool2 = Tool.from_function(
        lambda: None,
        name="tool_lateral",
        description="lateral tool",
        tags={PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC},
    )

    async def call_next(ctx):
        return [dummy_tool1, dummy_tool2]

    with patch("adpilot_mcp.mcp.middleware.get_http_headers", return_value={}):
        filtered = await middleware.on_list_tools(context, call_next)

    assert len(filtered) == 2
    for t in filtered:
        assert t.tags == set()


@pytest.mark.asyncio
async def test_tool_filter_middleware_with_phase_header():
    middleware = ToolFilterMiddleware()
    context = MagicMock()

    dummy_tool1 = Tool.from_function(
        lambda: None,
        name="tool_recon",
        description="recon tool",
        tags={PentestPhase.EXTERNAL_RECONNAISSANCE},
    )
    dummy_tool2 = Tool.from_function(
        lambda: None,
        name="tool_lateral",
        description="lateral tool",
        tags={PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC},
    )

    async def call_next(ctx):
        return [dummy_tool1, dummy_tool2]

    with patch(
        "adpilot_mcp.mcp.middleware.get_http_headers",
        return_value={"pentest_phase": "external_reconnaissance"},
    ):
        filtered = await middleware.on_list_tools(context, call_next)

    assert len(filtered) == 1
    assert filtered[0].name == "tool_recon"
    assert filtered[0].tags == set()


@pytest.mark.asyncio
async def test_tool_filter_middleware_shell_only():
    middleware = ToolFilterMiddleware()
    context = MagicMock()

    dummy_tool1 = Tool.from_function(
        lambda: None,
        name="tool_recon",
        description="recon tool",
        tags={PentestPhase.EXTERNAL_RECONNAISSANCE},
    )
    dummy_shell = Tool.from_function(
        lambda: None,
        name="shell_exec",
        description="shell tool",
        tags={
            PentestPhase.EXTERNAL_RECONNAISSANCE,
            PentestPhase.SHELL_ONLY,
            PentestPhase.SHELL_EXEC,
        },
    )

    async def call_next(ctx):
        return [dummy_tool1, dummy_shell]

    # Test "shell_only"
    with patch(
        "adpilot_mcp.mcp.middleware.get_http_headers",
        return_value={"pentest_phase": "shell_only"},
    ):
        filtered = await middleware.on_list_tools(context, call_next)

    assert len(filtered) == 1
    assert filtered[0].name == "shell_exec"
    assert filtered[0].tags == set()

    # Test "shell_exec"
    with patch(
        "adpilot_mcp.mcp.middleware.get_http_headers",
        return_value={"pentest_phase": "shell_exec"},
    ):
        filtered2 = await middleware.on_list_tools(context, call_next)

    assert len(filtered2) == 1
    assert filtered2[0].name == "shell_exec"

