class LLMError(Exception):
    """Base exception for all LLM-related errors."""


class EmptyLLMResponseError(LLMError):
    pass


class InvalidLLMResponseError(LLMError):
    pass