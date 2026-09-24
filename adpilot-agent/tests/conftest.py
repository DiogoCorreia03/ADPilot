import pytest
from unittest.mock import MagicMock
from adpilot_agent.util.config import get_settings
from adpilot_agent.util.state import CheckVerdict, PentestState
from adpilot_agent.util.metrics import new_run_metrics


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Ensure tests have standard dummy environment variables without relying on local .env."""
    monkeypatch.setenv("NETWORK", "192.168.122.0/24")
    monkeypatch.setenv("DC_IP", "192.168.122.10")
    monkeypatch.setenv("ATTACKER_MACHINE_AUTH_TOKEN", "user:password")
    monkeypatch.setenv("ATTACKER_MACHINE_URL", "http://127.0.0.1:8080/mcp")
    monkeypatch.setenv("LOCAL_MODEL", "qwen2.5")
    monkeypatch.setenv("REMOTE_MODEL", "gemini-2.0-flash")
    monkeypatch.setenv("REMOTE_API_KEY", "dummy-api-key")
    monkeypatch.setenv("MODEL_MODE", "remote")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def base_state() -> PentestState:
    return {
        "dc_ip": "192.168.122.10",
        "network": "192.168.122.0/24",
        "initial_scan_results": "Dummy scan output",
        "tools": "Tool A, Tool B",
        "scan_results": "Dummy scan output",
        "scenario": "",
        "plan": "1. Task A\n2. Task B",
        "next_task": "1. Task A",
        "task_result": "Success finding info",
        "check_count": 0,
        "check_output": "VERDICT: [SUCCESS]",
        "check_verdict": CheckVerdict.SUCCESS,
        "run_metrics": new_run_metrics(),
    }
