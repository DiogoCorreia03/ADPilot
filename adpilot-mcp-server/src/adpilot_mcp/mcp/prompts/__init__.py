from fastmcp import FastMCP
from adpilot_mcp.mcp.prompts import playbooks


def register_all_prompts(mcp: FastMCP) -> None:
    """Register all MCP prompts with FastMCP."""
    playbooks.register(mcp)


__all__ = ["register_all_prompts"]
