import json
import logging
from fastmcp import FastMCP
from adpilot_mcp.models.credentials import CredentialQuery
from adpilot_mcp.models.phases import PentestPhase
from adpilot_mcp.services.state_store import get_state_store

logger = logging.getLogger(__name__)


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        tags={
            PentestPhase.CHECK_RESULTS,
        }
    )
    async def credentials_add(
        username: str,
        password: str,
        domain: str | None = None,
        notes: str | None = None,
    ) -> str:
        """
        Store a credential (username + password) in the server state directory.

        :param username: Username to store.
        :param password: Password to store.
        :param domain: Optional domain or service identifier.
        :param notes: Optional freeform notes.
        :return: Status and saved entry.
        """
        try:
            store = get_state_store()
            res = await store.add_credential_async(username, password, domain, notes)
            return json.dumps(res, indent=2)
        except Exception as e:
            logger.error(f"Error adding credential: {e}")
            return json.dumps({"status": "error", "error": str(e)}, indent=2)

    @mcp.tool(
        tags={
            PentestPhase.CHECK_RESULTS,
        }
    )
    async def credentials_get(
        username: str | None = None, domain: str | None = None
    ) -> str:
        """
        Retrieve stored credentials. Optionally filter by username substring or domain substring.

        :param username: Optional username substring to filter.
        :param domain: Optional domain substring to filter.
        :return: Count and list of matching credential entries.
        """
        try:
            store = get_state_store()
            res = await store.get_credentials_async(
                CredentialQuery(username=username, domain=domain)
            )
            return json.dumps(
                {"count": res.count, "items": [c.model_dump() for c in res.items]},
                indent=2,
            )
        except Exception as e:
            logger.error(f"Error retrieving credentials: {e}")
            return json.dumps({"count": 0, "items": [], "error": str(e)}, indent=2)
