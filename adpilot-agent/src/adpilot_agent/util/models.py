from collections.abc import Sequence
from functools import lru_cache
from typing import Any

from langchain.agents import create_agent
from langchain.chat_models import BaseChatModel, init_chat_model
from langgraph.graph.state import CompiledStateGraph

from .config import ModelMode, get_settings


@lru_cache
def _get_local_model() -> BaseChatModel:
    settings = get_settings()
    if not settings.LOCAL_MODEL:
        raise ValueError("LOCAL_MODEL is required when using local models.")
    return init_chat_model(settings.LOCAL_MODEL)


@lru_cache
def _get_remote_model() -> BaseChatModel:
    settings = get_settings()
    if not settings.REMOTE_MODEL:
        raise ValueError("REMOTE_MODEL is required when using remote models.")

    kwargs: dict[str, Any] = {}
    if settings.GCP_PROJECT:
        kwargs["project"] = settings.GCP_PROJECT
    if settings.REMOTE_API_KEY:
        kwargs["api_key"] = settings.REMOTE_API_KEY.get_secret_value()
    if settings.MODEL_PROVIDER:
        kwargs["model_provider"] = settings.MODEL_PROVIDER

    return init_chat_model(settings.REMOTE_MODEL, **kwargs)


def get_model_for_caller(caller_name: str) -> BaseChatModel:
    """Select the appropriate chat model depending on caller node and MODEL_MODE."""
    settings = get_settings()
    if settings.MODEL_MODE == ModelMode.REMOTE:
        return _get_remote_model()
    elif settings.MODEL_MODE == ModelMode.LOCAL:
        return _get_local_model()
    elif settings.MODEL_MODE == ModelMode.HYBRID:
        # In hybrid mode: use remote model for planning, exploitation and reporting; local model for fast extraction/checks
        if caller_name in ("InitialPlan", "ExploitNode", "UpdatePlan", "FinalReport"):
            return _get_remote_model()
        else:
            return _get_local_model()
    else:
        raise ValueError(f"Invalid MODEL_MODE: {settings.MODEL_MODE}")


def get_agent(caller_name: str = "", *, tools: Sequence[Any] | None = None) -> CompiledStateGraph:
    """Create a compiled agent graph for the specified caller with optional tools."""
    model = get_model_for_caller(caller_name)
    tool_list = list(tools) if tools is not None else []
    return create_agent(model=model, tools=tool_list)
