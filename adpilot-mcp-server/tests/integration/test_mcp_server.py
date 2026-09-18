import json
import pytest
from pathlib import Path
from adpilot_mcp.config import Settings
from adpilot_mcp.mcp.server import create_server


@pytest.fixture
def test_server(tmp_path: Path, monkeypatch):
    test_state = tmp_path / "test_state"
    monkeypatch.setenv("AD_STATE_DIR", str(test_state))
    # Clear settings cache so new env var is loaded
    from adpilot_mcp.config import get_settings
    get_settings.cache_clear()
    return create_server()


@pytest.mark.asyncio
async def test_server_tools_registered(test_server):
    tools = await test_server.list_tools()
    tool_names = {t.name for t in tools}

    # Core recon and enum tools
    assert "run_curl" in tool_names
    assert "run_nmap_scan" in tool_names
    assert "run_smbclient" in tool_names
    assert "run_ldapsearch" in tool_names
    assert "run_netexec" in tool_names

    # Kerberos tools
    assert "run_getnpusers" in tool_names
    assert "run_getuserspns" in tool_names
    assert "run_kerbrute" in tool_names
    assert "run_gettgt" in tool_names
    assert "run_getst" in tool_names

    # Lateral movement tools
    assert "run_secretsdump" in tool_names
    assert "run_wmiexec" in tool_names
    assert "run_certipy" in tool_names

    # Credentials store
    assert "credentials_add" in tool_names
    assert "credentials_get" in tool_names


@pytest.mark.asyncio
async def test_credentials_tool_execution(test_server):
    # Test credentials_add
    add_res = await test_server.call_tool(
        "credentials_add",
        arguments={
            "username": "pentest_admin",
            "password": "Password123!",
            "domain": "LAB.LOCAL",
            "notes": "Domain admin found in SMB share",
        },
    )
    data = json.loads(add_res.content[0].text)
    assert data["status"] == "saved"
    assert data["credential"]["username"] == "pentest_admin"

    # Test credentials_get
    get_res = await test_server.call_tool(
        "credentials_get", arguments={"username": "pentest_admin"}
    )
    get_data = json.loads(get_res.content[0].text)
    assert get_data["count"] == 1
    assert get_data["items"][0]["username"] == "pentest_admin"


@pytest.mark.asyncio
async def test_server_filter_shell_only(test_server):
    from unittest.mock import patch

    with patch(
        "adpilot_mcp.mcp.middleware.get_http_headers",
        return_value={"pentest_phase": "shell_only"},
    ):
        tools = await test_server.list_tools()
        tool_names = [t.name for t in tools]
        assert tool_names == ["shell_exec"]

    with patch(
        "adpilot_mcp.mcp.middleware.get_http_headers",
        return_value={"pentest_phase": "shell_exec"},
    ):
        tools = await test_server.list_tools()
        tool_names = [t.name for t in tools]
        assert tool_names == ["shell_exec"]

