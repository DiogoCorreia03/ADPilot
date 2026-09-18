import asyncio
import pytest
from adpilot_mcp.core.executor import run_command_async, run_command


@pytest.mark.asyncio
async def test_run_command_async_success():
    res = await run_command_async("echo 'hello world'", timeout=10)
    assert res.success is True
    assert res.returncode == 0
    assert res.stdout == "hello world"


@pytest.mark.asyncio
async def test_run_command_async_invalid_timeout():
    res_zero = await run_command_async("echo 'test'", timeout=0)
    assert res_zero.success is False
    assert "positive integer" in res_zero.stderr

    res_neg = await run_command_async("echo 'test'", timeout=-5)
    assert res_neg.success is False
    assert "positive integer" in res_neg.stderr

    res_too_long = await run_command_async("echo 'test'", timeout=1000)
    assert res_too_long.success is False
    assert "900 seconds or less" in res_too_long.stderr


@pytest.mark.asyncio
async def test_run_command_async_timeout_cleanup():
    # Run a sleep command with a 1 second timeout
    res = await run_command_async("sleep 10", timeout=1)
    assert res.success is False
    assert "Command timed out after 1s" in res.stderr
    assert res.returncode == -1


@pytest.mark.asyncio
async def test_run_command_async_cancellation():
    task = asyncio.create_task(run_command_async("sleep 10", timeout=10))
    await asyncio.sleep(0.1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


def test_sync_run_command():
    res = run_command("echo 'sync test'", timeout=10)
    assert res.success is True
    assert res.stdout == "sync test"

    res_invalid = run_command("echo 'test'", timeout=0)
    assert res_invalid.success is False
