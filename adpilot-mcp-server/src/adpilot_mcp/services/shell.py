import re

from adpilot_mcp.core.executor import run_command_async
from adpilot_mcp.models.execution import CommandResult

# Matches 'ls' with recursive flag (-R, -r, --recursive, -laR, etc.) targeting root '/'
_BLOCKED_COMMAND_PATTERNS = [
    re.compile(r"\bls\b(?:\s+-[a-zA-Z0-9]*[Rr][a-zA-Z0-9]*|\s+--recursive)+\s+(?:/[*\s]*$|/(?:\s+|$))"),
    # Catch find / or tree / if you also want to prevent full filesystem walks:
    re.compile(r"\bfind\s+/\s*(?:-print\b)?$"),
    re.compile(r"\btree\s+/\s*$"),
]

def is_command_blocked(cmd: str) -> tuple[bool, str]:
    """Check if the command matches prohibited destructive/runaway patterns."""
    clean_cmd = cmd.strip()
    
    for pattern in _BLOCKED_COMMAND_PATTERNS:
        if pattern.search(clean_cmd):
            return True, f"Execution denied: recursive root exploration is disallowed ('{clean_cmd}')"
            
    return False, ""


async def shell_exec(command: str, timeout: int = 300) -> CommandResult:
    """Execute an arbitrary shell command with timeout limit check."""
    if is_command_blocked(command)[0]:
        return CommandResult(
            command=command,
            stdout="",
            stderr=f"Execution denied: recursive root exploration is disallowed ('{command}') as it would crash the system.",
            returncode=-1,
            success=False,
        )
    return await run_command_async(command, timeout=timeout)
