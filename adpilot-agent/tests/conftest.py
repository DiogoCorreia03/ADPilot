import pytest
from adpilot_agent.util.config import get_settings


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
