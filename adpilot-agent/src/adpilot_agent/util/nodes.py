import logging
from typing import Any

from langchain.messages import AIMessage
from langchain_core.callbacks import get_usage_metadata_callback

from .config import get_settings
from .exceptions import EmptyLLMResponseError, InvalidLLMResponseError
from .execution_logger import log_execution_event
from .metrics import record_token_usage

# Set up logging
logger = logging.getLogger(__name__)


def _extract_token_usage(
    usage_metadata: dict[str, Any] | None,
    configured_model_name: str,
) -> dict[str, int] | None:
    """Extract and aggregate token usage across single and hybrid model configurations."""
    if not usage_metadata:
        return None

    # Handle "provider:model"
    model_name_split = configured_model_name.split(":")
    model_name = model_name_split[-1]

    if model_name in usage_metadata:
        return usage_metadata[model_name]
    elif len(usage_metadata) == 1:
        return next(iter(usage_metadata.values()))
    else:  # Hybrid or multi-model setups
        logger.debug("Hybrid/multi-model usage metadata detected: %s", usage_metadata)
        return {
            "input_tokens": sum(
                int(m.get("input_tokens", 0) or 0) for m in usage_metadata.values()
            ),
            "output_tokens": sum(
                int(m.get("output_tokens", 0) or 0) for m in usage_metadata.values()
            ),
            "total_tokens": sum(
                int(m.get("total_tokens", 0) or 0) for m in usage_metadata.values()
            ),
        }


def _extract_ai_message(result: Any) -> AIMessage:
    """Extract and validate the final AIMessage from agent execution result."""
    message = (
        result["messages"][-1]
        if isinstance(result, dict) and "messages" in result and result["messages"]
        else result
    )

    if not isinstance(message, AIMessage):
        raise InvalidLLMResponseError(
            f"Expected AIMessage, got {type(message).__name__}"
        )

    return message


def _extract_text_content(content: Any) -> str:
    """Extract and concatenate text from message content, ignoring internal thinking/reasoning blocks."""
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                if "text" in part and isinstance(part["text"], str):
                    parts.append(part["text"])
                elif part.get("type") in ("thinking", "thought"):
                    continue
                elif "content" in part and isinstance(part["content"], str):
                    parts.append(part["content"])
                else:
                    logger.warning(
                        "Skipping non-text content part in message: %s", part
                    )
            elif hasattr(part, "text") and isinstance(part.text, str):
                parts.append(part.text)
            else:
                logger.warning(
                    "Skipping unhandled content part type: %s", type(part).__name__
                )
        text = "".join(parts)
    else:
        raise InvalidLLMResponseError(
            f"Agent invocation returned invalid result: {content}"
        )

    cleaned = text.strip()
    if not cleaned:
        raise EmptyLLMResponseError("Agent invocation returned empty result.")

    return cleaned


async def invoke_agent_once(
    agent: Any,
    messages: list,
    *,
    metrics: dict[str, Any],
) -> str:
    """Execute a single agent invocation pass, record token metrics, and return extracted text content."""
    settings = get_settings()
    with get_usage_metadata_callback() as cb:
        result = await agent.ainvoke({"messages": messages})

    usage_data = _extract_token_usage(
        getattr(cb, "usage_metadata", None),
        settings.MODEL_NAME,
    )
    if usage_data:
        record_token_usage(
            metrics,
            usage_metadata=usage_data,
        )

    message = _extract_ai_message(result)
    response = _extract_text_content(message.content)

    messages = result.get("messages", []) if isinstance(result, dict) else messages
    prompts = [m for m in messages if not isinstance(m, AIMessage)]
    serialized_prompts = [
        {
            "role": getattr(m, "type", "user"),
            "content": _extract_text_content(getattr(m, "content", str(m))),
        }
        for m in prompts
    ]
    
    log_execution_event(
        event_type="llm_call",
        input=serialized_prompts,
        output=response,
    )

    return response
