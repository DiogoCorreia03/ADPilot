import pytest
from pydantic import ValidationError
from adpilot_agent.util.config import Settings, ModelMode, get_settings


def test_settings_remote_mode(monkeypatch):
    monkeypatch.setenv("NETWORK", "10.0.0.0/24")
    monkeypatch.setenv("DC_IP", "10.0.0.1")
    monkeypatch.setenv("ATTACKER_MACHINE_AUTH_TOKEN", "token")
    monkeypatch.setenv("ATTACKER_MACHINE_URL", "http://127.0.0.1:8080/mcp")
    monkeypatch.setenv("REMOTE_MODEL", "gemini-2.5-flash")
    monkeypatch.setenv("REMOTE_API_KEY", "secret-key")
    monkeypatch.setenv("MODEL_MODE", "remote")
    get_settings.cache_clear()

    settings = get_settings()
    assert settings.MODEL_MODE == ModelMode.REMOTE
    assert "gemini-2.5-flash" in settings.MODEL_NAME
    assert settings.IGNORED_HOSTS_PROMPT != ""


def test_settings_local_mode_without_remote_key(monkeypatch):
    monkeypatch.setenv("NETWORK", "10.0.0.0/24")
    monkeypatch.setenv("DC_IP", "10.0.0.1")
    monkeypatch.setenv("ATTACKER_MACHINE_AUTH_TOKEN", "token")
    monkeypatch.setenv("ATTACKER_MACHINE_URL", "http://127.0.0.1:8080/mcp")
    monkeypatch.setenv("LOCAL_MODEL", "qwen2.5")
    monkeypatch.delenv("REMOTE_API_KEY", raising=False)
    monkeypatch.delenv("REMOTE_MODEL", raising=False)
    monkeypatch.setenv("MODEL_MODE", "local")

    settings = Settings(_env_file=None)  # pyright: ignore[reportCallIssue]
    assert settings.MODEL_MODE == ModelMode.LOCAL
    assert settings.MODEL_NAME == "ollama:qwen2.5"
    assert settings.REMOTE_API_KEY is None


def test_settings_remote_mode_missing_key_raises(monkeypatch):
    monkeypatch.setenv("NETWORK", "10.0.0.0/24")
    monkeypatch.setenv("DC_IP", "10.0.0.1")
    monkeypatch.setenv("ATTACKER_MACHINE_AUTH_TOKEN", "token")
    monkeypatch.setenv("ATTACKER_MACHINE_URL", "http://127.0.0.1:8080/mcp")
    monkeypatch.delenv("REMOTE_API_KEY", raising=False)
    monkeypatch.delenv("GCP_PROJECT", raising=False)
    monkeypatch.setenv("REMOTE_MODEL", "gemini-2.5-flash")
    monkeypatch.setenv("MODEL_MODE", "remote")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)  # pyright: ignore[reportCallIssue]


def test_settings_remote_mode_with_gcp_project_without_api_key(monkeypatch):
    monkeypatch.setenv("NETWORK", "10.0.0.0/24")
    monkeypatch.setenv("DC_IP", "10.0.0.1")
    monkeypatch.setenv("ATTACKER_MACHINE_AUTH_TOKEN", "token")
    monkeypatch.setenv("ATTACKER_MACHINE_URL", "http://127.0.0.1:8080/mcp")
    monkeypatch.delenv("REMOTE_API_KEY", raising=False)
    monkeypatch.setenv("GCP_PROJECT", "my-gcp-project")
    monkeypatch.setenv("REMOTE_MODEL", "gemini-2.5-flash")
    monkeypatch.setenv("MODEL_MODE", "remote")

    settings = Settings(_env_file=None)  # pyright: ignore[reportCallIssue]
    assert settings.MODEL_MODE == ModelMode.REMOTE
    assert settings.GCP_PROJECT == "my-gcp-project"
    assert settings.REMOTE_API_KEY is None


def test_settings_ignored_hosts_string_parsing(monkeypatch):
    monkeypatch.setenv("NETWORK", "10.0.0.0/24")
    monkeypatch.setenv("DC_IP", "10.0.0.1")
    monkeypatch.setenv("ATTACKER_MACHINE_AUTH_TOKEN", "token")
    monkeypatch.setenv("ATTACKER_MACHINE_URL", "http://127.0.0.1:8080/mcp")
    monkeypatch.setenv("LOCAL_MODEL", "qwen2.5")
    monkeypatch.setenv("MODEL_MODE", "local")
    monkeypatch.setenv("IGNORED_HOSTS", "10.0.0.2, 10.0.0.3; 10.0.0.4")

    settings = Settings(_env_file=None)  # pyright: ignore[reportCallIssue]
    assert settings.IGNORED_HOSTS == ["10.0.0.2", "10.0.0.3", "10.0.0.4"]
    assert settings.IGNORED_HOSTS_NMAP_EXCLUDE == "10.0.0.2,10.0.0.3,10.0.0.4"
    assert settings.IGNORED_HOSTS_PROMPT == "10.0.0.2; 10.0.0.3; 10.0.0.4"
