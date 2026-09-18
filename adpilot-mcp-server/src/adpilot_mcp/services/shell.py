from adpilot_mcp.core.executor import run_command_async
from adpilot_mcp.models.execution import CommandResult


async def shell_exec(command: str, timeout: int = 300) -> CommandResult:
    """Execute an arbitrary shell command with timeout limit check."""
    return await run_command_async(command, timeout=timeout)
