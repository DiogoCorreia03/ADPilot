from adpilot_agent.util.config import get_settings
from adpilot_agent.util.models import get_model_for_caller


def test_get_model_for_caller_remote(monkeypatch):
    monkeypatch.setenv("MODEL_MODE", "remote")
    monkeypatch.setenv("REMOTE_MODEL", "gemini-2.5-flash")
    monkeypatch.setenv("REMOTE_API_KEY", "dummy-key")
    get_settings.cache_clear()

    model = get_model_for_caller("InitialPlan")
    assert model is not None


def test_get_model_for_caller_hybrid(monkeypatch):
    monkeypatch.setenv("MODEL_MODE", "hybrid")
    monkeypatch.setenv("REMOTE_MODEL", "gemini-2.5-flash")
    monkeypatch.setenv("REMOTE_API_KEY", "dummy-key")
    monkeypatch.setenv("LOCAL_MODEL", "qwen2.5")
    get_settings.cache_clear()

    remote_caller_model = get_model_for_caller("ExploitNode")
    local_caller_model = get_model_for_caller("CheckNode")
    assert remote_caller_model is not None
    assert local_caller_model is not None
