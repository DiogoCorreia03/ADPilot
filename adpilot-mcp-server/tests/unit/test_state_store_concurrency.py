import asyncio
import pytest
from pathlib import Path
from adpilot_mcp.config import Settings
from adpilot_mcp.services.state_store import StateStore


@pytest.fixture
def temp_state_dir(tmp_path: Path):
    return tmp_path / "concurrent_state"


@pytest.fixture
def state_store(temp_state_dir: Path):
    settings = Settings(AD_STATE_DIR=temp_state_dir)
    return StateStore(settings=settings)


@pytest.mark.asyncio
async def test_state_store_concurrent_writes(state_store: StateStore):
    num_writers = 50

    async def write_cred(i: int):
        return await state_store.add_credential_async(
            username=f"user_{i}",
            password=f"pass_{i}",
            domain="CORP.LOCAL",
            notes=f"Discovered {i}",
        )

    results = await asyncio.gather(*(write_cred(i) for i in range(num_writers)))
    assert len(results) == num_writers

    # Verify all 50 credentials exist and no data was lost or overwritten
    creds_result = await state_store.get_credentials_async()
    assert creds_result.count == num_writers
    assert len(creds_result.items) == num_writers

    usernames = {c.username for c in creds_result.items}
    expected_usernames = {f"user_{i}" for i in range(num_writers)}
    assert usernames == expected_usernames


def test_state_store_artifact_path_traversal_protection(state_store: StateStore):
    # Safe path
    p = state_store.get_artifact_path("reports/summary.txt")
    assert p.is_relative_to(state_store.state_dir)

    # Path traversal attack
    with pytest.raises(ValueError, match="Path traversal detected"):
        state_store.get_artifact_path("../../etc/shadow")
