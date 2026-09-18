from contextlib import asynccontextmanager
from unittest.mock import MagicMock, patch

import pytest

from mcp_client.app import get_pentest_phase, run_interactive_session


def test_get_pentest_phase_from_settings():
    settings = MagicMock()
    settings.PENTEST_PHASE = "shell_only"
    assert get_pentest_phase(settings) == "shell_only"


def test_get_pentest_phase_from_env_var(monkeypatch):
    monkeypatch.setenv("PENTEST_PHASE", "initial_access")
    assert get_pentest_phase() == "initial_access"

    monkeypatch.delenv("PENTEST_PHASE", raising=False)
    monkeypatch.setenv("pentest_phase", "external_recon")
    assert get_pentest_phase() == "external_recon"


def test_get_pentest_phase_empty(monkeypatch):
    monkeypatch.delenv("PENTEST_PHASE", raising=False)
    monkeypatch.delenv("pentest_phase", raising=False)
    assert get_pentest_phase() is None
    assert get_pentest_phase(MagicMock(spec=[])) is None


@pytest.mark.asyncio
async def test_run_interactive_session_passes_extra_headers(monkeypatch):
    captured_kwargs = {}

    @asynccontextmanager
    async def mock_mcp_tool_session(**kwargs):
        captured_kwargs.update(kwargs)
        yield []

    monkeypatch.setenv("PENTEST_PHASE", "shell_only")

    mock_settings = MagicMock()
    mock_settings.ATTACKER_MACHINE_URL = "http://127.0.0.1:8080/mcp"
    mock_settings.NETWORK = "192.168.122.0/24"
    mock_settings.DC_IP = "192.168.122.10"

    with (
        patch("mcp_client.app.get_settings", return_value=mock_settings),
        patch("mcp_client.app.mcp_tool_session", side_effect=mock_mcp_tool_session),
        patch("mcp_client.app.Prompt.ask", side_effect=KeyboardInterrupt),
        patch("mcp_client.app.display_tools_table"),
        patch("mcp_client.app.prompt_help"),
    ):
        await run_interactive_session()

    assert captured_kwargs.get("extra_headers") == {"pentest_phase": "shell_only"}
    assert captured_kwargs.get("phase") == "shell_only"


@pytest.mark.asyncio
async def test_run_interactive_session_no_extra_headers_when_unset(monkeypatch):
    captured_kwargs = {}

    @asynccontextmanager
    async def mock_mcp_tool_session(**kwargs):
        captured_kwargs.update(kwargs)
        yield []

    monkeypatch.delenv("PENTEST_PHASE", raising=False)
    monkeypatch.delenv("pentest_phase", raising=False)

    mock_settings = MagicMock(spec=["ATTACKER_MACHINE_URL", "NETWORK", "DC_IP"])
    mock_settings.ATTACKER_MACHINE_URL = "http://127.0.0.1:8080/mcp"
    mock_settings.NETWORK = "192.168.122.0/24"
    mock_settings.DC_IP = "192.168.122.10"

    with (
        patch("mcp_client.app.get_settings", return_value=mock_settings),
        patch("mcp_client.app.mcp_tool_session", side_effect=mock_mcp_tool_session),
        patch("mcp_client.app.Prompt.ask", side_effect=KeyboardInterrupt),
        patch("mcp_client.app.display_tools_table"),
        patch("mcp_client.app.prompt_help"),
    ):
        await run_interactive_session()

    assert captured_kwargs.get("extra_headers") is None
    assert captured_kwargs.get("phase") is None


@pytest.mark.asyncio
async def test_run_interactive_session_dynamic_phase_switch(monkeypatch):
    sessions_captured = []

    @asynccontextmanager
    async def mock_mcp_tool_session(**kwargs):
        sessions_captured.append(dict(kwargs))
        yield []

    monkeypatch.delenv("PENTEST_PHASE", raising=False)
    monkeypatch.delenv("pentest_phase", raising=False)

    mock_settings = MagicMock(spec=["ATTACKER_MACHINE_URL", "NETWORK", "DC_IP"])
    mock_settings.ATTACKER_MACHINE_URL = "http://127.0.0.1:8080/mcp"
    mock_settings.NETWORK = "192.168.122.0/24"
    mock_settings.DC_IP = "192.168.122.10"

    # User interactions:
    # 1. First session asks for command -> 'phase' (inspect)
    # 2. 'phase shell_only' -> resets connection
    # 3. In second session asks for command -> 'exit'
    prompts = ["phase", "phase shell_only", "exit"]

    with (
        patch("mcp_client.app.get_settings", return_value=mock_settings),
        patch("mcp_client.app.mcp_tool_session", side_effect=mock_mcp_tool_session),
        patch("mcp_client.app.Prompt.ask", side_effect=prompts),
        patch("mcp_client.app.display_tools_table"),
        patch("mcp_client.app.prompt_help"),
    ):
        await run_interactive_session()

    assert len(sessions_captured) == 2
    # First session was started without phase
    assert sessions_captured[0].get("extra_headers") is None
    assert sessions_captured[0].get("phase") is None

    # Second session was reset with the new phase
    assert sessions_captured[1].get("extra_headers") == {"pentest_phase": "shell_only"}
    assert sessions_captured[1].get("phase") == "shell_only"


@pytest.mark.asyncio
async def test_run_interactive_session_dynamic_phase_reset(monkeypatch):
    sessions_captured = []

    @asynccontextmanager
    async def mock_mcp_tool_session(**kwargs):
        sessions_captured.append(dict(kwargs))
        yield []

    monkeypatch.setenv("PENTEST_PHASE", "initial_access")

    mock_settings = MagicMock(spec=["ATTACKER_MACHINE_URL", "NETWORK", "DC_IP"])
    mock_settings.ATTACKER_MACHINE_URL = "http://127.0.0.1:8080/mcp"
    mock_settings.NETWORK = "192.168.122.0/24"
    mock_settings.DC_IP = "192.168.122.10"

    # Interactions: 'phase none' to clear phase, then 'exit'
    prompts = ["phase none", "exit"]

    with (
        patch("mcp_client.app.get_settings", return_value=mock_settings),
        patch("mcp_client.app.mcp_tool_session", side_effect=mock_mcp_tool_session),
        patch("mcp_client.app.Prompt.ask", side_effect=prompts),
        patch("mcp_client.app.display_tools_table"),
        patch("mcp_client.app.prompt_help"),
    ):
        await run_interactive_session()

    assert len(sessions_captured) == 2
    assert sessions_captured[0].get("extra_headers") == {"pentest_phase": "initial_access"}
    assert sessions_captured[1].get("extra_headers") is None
    assert sessions_captured[1].get("phase") is None
