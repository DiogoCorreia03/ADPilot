import asyncio
import json
import logging
import threading
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from adpilot_mcp.config import Settings, get_settings
from adpilot_mcp.core.security import safe_subpath
from adpilot_mcp.models.credentials import (
    CredentialEntry,
    CredentialListResult,
    CredentialQuery,
)

logger = logging.getLogger(__name__)


class StateStore:
    """Manages persistent state files and credentials for the pentest session."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.state_dir = self.settings.ad_state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.credentials_file = self.settings.credentials_file
        self._lock = threading.Lock()

    def load_json(self, path: Path) -> dict[str, Any]:
        """Safely load JSON from file. Returns empty dict on failure or missing file."""
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning(f"Failed to parse JSON file {path}: {e}")
                return {}
        return {}

    def save_json(self, path: Path, data: dict[str, Any]) -> None:
        """Safely save JSON to file with atomic write using unique temporary file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_name(f"{path.stem}_{uuid.uuid4().hex}.tmp")
        temp_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temp_path.replace(path)

    def add_credential(
        self,
        username: str,
        password: str,
        domain: str | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Store a credential (username + password) in the credentials file with thread-safety."""
        with self._lock:
            creds = self.load_json(self.credentials_file)
            numeric_ids = [int(k) for k in creds.keys() if k.isdigit()]
            cid = str(max(numeric_ids, default=0) + 1)
            entry = CredentialEntry(
                id=cid,
                username=username,
                password=password,
                domain=domain or "",
                notes=notes or "",
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            creds[cid] = entry.model_dump()
            self.save_json(self.credentials_file, creds)
            return {"status": "saved", "credential": entry.model_dump()}

    async def add_credential_async(
        self,
        username: str,
        password: str,
        domain: str | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Asynchronously store a credential without blocking the event loop."""
        return await asyncio.to_thread(
            self.add_credential, username, password, domain, notes
        )

    def get_credentials(
        self, query: CredentialQuery | None = None
    ) -> CredentialListResult:
        """Retrieve stored credentials, optionally filtered by username or domain substring."""
        with self._lock:
            creds = self.load_json(self.credentials_file)
        items: list[CredentialEntry] = []
        for v in creds.values():
            try:
                items.append(CredentialEntry(**v))
            except Exception as e:
                logger.warning(f"Error deserializing credential: {e}")

        if query:
            if query.username:
                u = query.username.lower()
                items = [c for c in items if u in c.username.lower()]
            if query.domain:
                d = query.domain.lower()
                items = [c for c in items if d in c.domain.lower()]

        return CredentialListResult(count=len(items), items=items)

    async def get_credentials_async(
        self, query: CredentialQuery | None = None
    ) -> CredentialListResult:
        """Asynchronously retrieve stored credentials without blocking the event loop."""
        return await asyncio.to_thread(self.get_credentials, query)

    def get_artifact_path(self, subpath: str | Path) -> Path:
        """Return and create target artifact path inside state directory, preventing traversal."""
        path = safe_subpath(self.state_dir, subpath)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_state_store() -> StateStore:
    """Singleton getter for StateStore."""
    return StateStore()

