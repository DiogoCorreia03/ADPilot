from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic import (
    Field,
    HttpUrl,
    SecretStr,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class ModelMode(str, Enum):
    LOCAL = "local"
    REMOTE = "remote"
    HYBRID = "hybrid"


class Settings(BaseSettings):
    DEBUG: bool = False

    LANGSMITH_TRACING: bool = False
    LANGSMITH_ENDPOINT: HttpUrl | None = None
    LANGSMITH_API_KEY: SecretStr | None = None
    LANGSMITH_PROJECT: str | None = None

    NETWORK: str
    DC_IP: str

    ATTACKER_MACHINE_AUTH_TOKEN: SecretStr
    ATTACKER_MACHINE_URL: HttpUrl
    EXPLOIT_MAX_TOOL_CALLS: int = 10
    EXPLOIT_MAX_SAME_TOOL_CALLS_IN_A_ROW: int = 5
    IGNORED_HOSTS: list[str] | str = Field(
        default_factory=lambda: ["192.168.122.1", "192.168.122.2", "192.168.122.57"]
    )

    LOCAL_MODEL: str | None = None
    REMOTE_MODEL: str | None = None
    MODEL_PROVIDER: str = ""
    REMOTE_API_KEY: SecretStr | None = None
    GCP_PROJECT: str | None = None

    MODEL_MODE: ModelMode = ModelMode.REMOTE

    # LLM Retry and Execution parameters
    LLM_RETRY_MAX_ATTEMPTS: int = 3
    LLM_RETRY_BASE_DELAY: float = 1.0
    LLM_RETRY_MAX_DELAY: float = 30.0
    CHECK_MAX_RETRIES: int = 3

    # Operational settings
    ENABLE_INTERACTIVE_CLI: bool = True

    @model_validator(mode="after")
    def validate_langsmith_settings(self):
        if self.LANGSMITH_TRACING and not (
            self.LANGSMITH_ENDPOINT
            and self.LANGSMITH_API_KEY
            and self.LANGSMITH_PROJECT
        ):
            raise ValueError(
                "LANGSMITH_ENDPOINT, LANGSMITH_API_KEY and LANGSMITH_PROJECT are required when LANGSMITH_TRACING is True"
            )
        return self

    @field_validator("LOCAL_MODEL", mode="before")
    @classmethod
    def validate_local_model(cls, v: str | None) -> str | None:
        if not v:
            return v
        # Allow users to specify local models without the "ollama:" prefix
        return v if v.startswith("ollama:") else f"ollama:{v}"

    @field_validator("REMOTE_MODEL", mode="before")
    @classmethod
    def validate_remote_model(cls, v: str | None) -> str | None:
        if not v:
            return v
        # Allow users to specify Google models without the "google_genai:" prefix
        # This is needed so we dont have to setup Google's ADC and can just use API key for auth
        if "gemini" not in v:
            return v
        return v if v.startswith(("google_genai:", "google_vertexai:")) else f"google_genai:{v}"

    @field_validator("EXPLOIT_MAX_TOOL_CALLS")
    @classmethod
    def validate_exploit_max_tool_calls(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("EXPLOIT_MAX_TOOL_CALLS must be greater than 0.")
        return v

    @field_validator("EXPLOIT_MAX_SAME_TOOL_CALLS_IN_A_ROW")
    @classmethod
    def validate_exploit_max_same_tool_calls_in_a_row(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("EXPLOIT_MAX_SAME_TOOL_CALLS_IN_A_ROW must be greater than 0.")
        return v

    @field_validator("IGNORED_HOSTS", mode="before")
    @classmethod
    def validate_ignored_hosts(cls, v):
        if isinstance(v, str):
            normalized = v.replace(";", ",").replace(" ", ",")
            return [host for host in normalized.split(",") if host]
        if isinstance(v, list):
            return [str(host).strip() for host in v if str(host).strip()]
        return v

    @model_validator(mode="after")
    def validate_model_mode(self):
        # Ensure that the model mode is valid
        if (self.MODEL_MODE == ModelMode.LOCAL or self.MODEL_MODE == ModelMode.HYBRID) and not self.LOCAL_MODEL:
            raise ValueError("LOCAL_MODEL is required when MODEL_MODE is LOCAL/HYBRID.")
        if self.MODEL_MODE in (ModelMode.REMOTE, ModelMode.HYBRID):
            if not self.REMOTE_MODEL:
                raise ValueError("REMOTE_MODEL is required when MODEL_MODE is REMOTE/HYBRID.")
            if not (self.REMOTE_API_KEY or self.GCP_PROJECT):
                raise ValueError(
                    "Either REMOTE_API_KEY or GCP_PROJECT is required when MODEL_MODE is REMOTE/HYBRID."
                )
        return self

    @computed_field
    @property
    def MODEL_NAME(self) -> str:
        if self.MODEL_MODE == ModelMode.REMOTE:
            return self.REMOTE_MODEL or ""
        if self.MODEL_MODE == ModelMode.LOCAL:
            return self.LOCAL_MODEL or ""
        return f"{self.REMOTE_MODEL or ''} + {self.LOCAL_MODEL or ''}"

    @property
    def IGNORED_HOSTS_NMAP_EXCLUDE(self) -> str:
        return ",".join(self.IGNORED_HOSTS)

    @property
    def IGNORED_HOSTS_PROMPT(self) -> str:
        return "; ".join(self.IGNORED_HOSTS)

    model_config = SettingsConfigDict(env_file=ENV_FILE)


# Cache settings to avoid reloading from disk multiple times
@lru_cache
def get_settings() -> Settings:
    try:
        return Settings()  # pyright: ignore[reportCallIssue]
    except Exception as e:
        print(f"Error loading settings: {e}")
        raise
