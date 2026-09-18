from datetime import datetime, timezone
from pydantic import BaseModel, Field


class CredentialEntry(BaseModel):
    """Represents an enumerated or captured credential."""
    id: str
    username: str
    password: str
    domain: str = ""
    notes: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CredentialQuery(BaseModel):
    """Filters for retrieving credentials."""
    username: str | None = None
    domain: str | None = None


class CredentialListResult(BaseModel):
    """Structured list result for credentials query."""
    count: int
    items: list[CredentialEntry]
