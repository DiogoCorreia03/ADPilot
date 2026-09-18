import asyncio
import json
from fastmcp import FastMCP
from adpilot_mcp.services.state_store import get_state_store


def register(mcp: FastMCP) -> None:
    @mcp.resource("ad://state/credentials")
    async def get_credentials_resource() -> str:
        """Read active credential inventory stored during the pentest session."""
        store = get_state_store()
        res = await store.get_credentials_async()
        return json.dumps(
            {"count": res.count, "items": [c.model_dump() for c in res.items]}, indent=2
        )

    @mcp.resource("ad://state/summary")
    async def get_state_summary_resource() -> str:
        """Inspect available state files and logs in the AD pentest state directory."""
        store = get_state_store()

        def _scan_files() -> list[str]:
            return [
                str(p.relative_to(store.state_dir))
                for p in store.state_dir.glob("**/*")
                if p.is_file()
            ]

        files = await asyncio.to_thread(_scan_files)
        return json.dumps({"state_dir": str(store.state_dir), "files": files}, indent=2)

