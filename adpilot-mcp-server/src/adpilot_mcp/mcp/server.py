import logging
from fastmcp import FastMCP
from adpilot_mcp.mcp.middleware import ToolFilterMiddleware
from adpilot_mcp.mcp.prompts import register_all_prompts
from adpilot_mcp.mcp.resources import register_all_resources
from adpilot_mcp.mcp.tools import register_all_tools

logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    """
    Factory function to construct, configure, and register all components
    on a FastMCP server instance.
    """
    mcp = FastMCP("ADPilot MCP Server", version="0.1.0")

    # Add phase-based tool filtering middleware
    mcp.add_middleware(ToolFilterMiddleware())

    # Register modular tools, resources, and prompts
    register_all_tools(mcp)
    # register_all_resources(mcp)
    # register_all_prompts(mcp)

    logger.info("FastMCP server initialized with modular tools, resources, and prompts.")
    return mcp
