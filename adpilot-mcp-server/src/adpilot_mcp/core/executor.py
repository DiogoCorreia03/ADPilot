import asyncio
import logging
import os
import signal
import subprocess
from typing import Any

from adpilot_mcp.core.security import sanitize_env
from adpilot_mcp.models.execution import CommandResult

logger = logging.getLogger(__name__)


async def _terminate_process_group(proc: asyncio.subprocess.Process) -> None:
    """Safely terminate a subprocess and all of its child processes in its process group."""
    if proc.returncode is not None:
        return
    try:
        pgid = os.getpgid(proc.pid)
        os.killpg(pgid, signal.SIGTERM)
        try:
            await asyncio.wait_for(proc.wait(), timeout=2.0)
            return
        except asyncio.TimeoutError:
            os.killpg(pgid, signal.SIGKILL)
            await proc.wait()
    except (ProcessLookupError, OSError):
        try:
            proc.kill()
            await proc.wait()
        except Exception:
            pass


async def run_command_async(
    cmd: str, timeout: int = 120, env_extra: dict[str, Any] | None = None
) -> CommandResult:
    """
    Run a shell command asynchronously and return structured output without blocking the event loop.
    Ensures full process group cleanup on timeout or task cancellation.
    """
    if timeout <= 0:
        return CommandResult(
            command=cmd,
            stdout="",
            stderr="Timeout must be a positive integer greater than 0",
            returncode=-1,
            success=False,
        )

    if timeout > 900:
        return CommandResult(
            command=cmd,
            stdout="",
            stderr="Timeout too long, must be 900 seconds or less",
            returncode=-1,
            success=False,
        )

    env = os.environ.copy()
    if env_extra:
        env.update(sanitize_env(env_extra))

    proc = None
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            cwd="/root",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            start_new_session=True,
        )

        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )

        stdout_str = stdout_bytes.decode(errors="replace").strip()
        stderr_str = stderr_bytes.decode(errors="replace").strip()
        returncode = proc.returncode if proc.returncode is not None else 0

        return CommandResult(
            command=cmd,
            stdout=stdout_str,
            stderr=stderr_str,
            returncode=returncode,
            success=(returncode == 0),
        )

    except asyncio.TimeoutError:
        if proc:
            await _terminate_process_group(proc)
        return CommandResult(
            command=cmd,
            stdout="",
            stderr=f"Command timed out after {timeout}s",
            returncode=-1,
            success=False,
        )

    except asyncio.CancelledError:
        if proc:
            await _terminate_process_group(proc)
        raise

    except Exception as e:
        logger.error(f"Command execution failed: {cmd} - {e}")
        if proc:
            await _terminate_process_group(proc)
        return CommandResult(
            command=cmd,
            stdout="",
            stderr=str(e),
            returncode=-1,
            success=False,
        )


def run_command(
    cmd: str, timeout: int = 120, env_extra: dict[str, Any] | None = None
) -> CommandResult:
    """
    Synchronous fallback to run shell command and return structured CommandResult.
    Maintains compatibility with sync calls.
    """
    if timeout <= 0:
        return CommandResult(
            command=cmd,
            stdout="",
            stderr="Timeout must be a positive integer greater than 0",
            returncode=-1,
            success=False,
        )

    if timeout > 900:
        return CommandResult(
            command=cmd,
            stdout="",
            stderr="Timeout too long, must be 900 seconds or less",
            returncode=-1,
            success=False,
        )

    env = os.environ.copy()
    if env_extra:
        env.update(sanitize_env(env_extra))

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return CommandResult(
            command=cmd,
            stdout=result.stdout.strip(),
            stderr=result.stderr.strip(),
            returncode=result.returncode,
            success=(result.returncode == 0),
        )
    except subprocess.TimeoutExpired:
        return CommandResult(
            command=cmd,
            stdout="",
            stderr=f"Command timed out after {timeout}s",
            returncode=-1,
            success=False,
        )
    except Exception as e:
        return CommandResult(
            command=cmd,
            stdout="",
            stderr=str(e),
            returncode=-1,
            success=False,
        )
