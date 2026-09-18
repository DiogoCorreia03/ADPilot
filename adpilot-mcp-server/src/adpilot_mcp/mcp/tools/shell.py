from fastmcp import FastMCP
from adpilot_mcp.models.phases import PentestPhase
from adpilot_mcp.services import shell as shell_service


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        tags={
            PentestPhase.EXTERNAL_RECONNAISSANCE,
            PentestPhase.INITIAL_ACCESS,
            PentestPhase.INTERNAL_RECONNAISSANCE,
            PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC,
            PentestPhase.SHELL_ONLY,
        }
    )
    async def shell_exec(command: str, timeout: int = 300) -> str:
        """
        Execute an arbitrary shell command on the attacker machine.
        Use for any tool not covered by a dedicated tool.

        :param command: The shell command to execute.
        :param timeout: Maximum time in seconds that the command is allowed to run for (default is 300 seconds).
        :return: stdout, stderr, returncode.
        """
        result = await shell_service.shell_exec(command, timeout=timeout)
        return result.to_mcp_result()
