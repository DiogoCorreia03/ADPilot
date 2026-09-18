from fastmcp import FastMCP
from adpilot_mcp.mcp.tools import (
    ad_enum,
    credentials,
    kerberos,
    lateral,
    recon,
    shell,
)


def register_all_tools(mcp: FastMCP) -> None:
    """Register all modular tool suites with the FastMCP instance."""
    shell.register(mcp)
    credentials.register(mcp)
    recon.register(mcp)
    ad_enum.register(mcp)
    kerberos.register(mcp)
    lateral.register(mcp)


__all__ = ["register_all_tools"]
