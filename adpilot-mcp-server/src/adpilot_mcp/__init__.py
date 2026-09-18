"""ADPilot MCP Server for Active Directory Pentesting Automation."""

__version__ = "0.1.0"

from adpilot_mcp.mcp.server import create_server
from adpilot_mcp.models.phases import PentestPhase

__all__ = ["__version__", "create_server", "PentestPhase"]
