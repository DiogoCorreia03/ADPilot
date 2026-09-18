from fastmcp import FastMCP
from adpilot_mcp.mcp.resources import state_resources


def register_all_resources(mcp: FastMCP) -> None:
    """Register all MCP resources with FastMCP."""
    state_resources.register(mcp)


__all__ = ["register_all_resources"]
