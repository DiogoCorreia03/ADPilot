import pytest
from pathlib import Path
from adpilot_mcp.config import Settings
from adpilot_mcp.models.credentials import CredentialQuery
from adpilot_mcp.services.state_store import StateStore


@pytest.fixture
def temp_state_dir(tmp_path: Path):
    return tmp_path / "ad_state"


@pytest.fixture
def state_store(temp_state_dir: Path):
    settings = Settings(AD_STATE_DIR=temp_state_dir)
    return StateStore(settings=settings)


def test_state_store_credentials_lifecycle(state_store: StateStore):
    # Initial empty state
    res = state_store.get_credentials()
    assert res.count == 0
    assert len(res.items) == 0

    # Add credentials
    saved1 = state_store.add_credential(
        username="admin", password="SecretPassword1!", domain="CORP.LOCAL", notes="DA account"
    )
    assert saved1["status"] == "saved"
    assert saved1["credential"]["id"] == "1"
    assert saved1["credential"]["username"] == "admin"

    saved2 = state_store.add_credential(
        username="svc_sql", password="SqlPassword99", domain="CORP.LOCAL", notes="Service account"
    )
    assert saved2["credential"]["id"] == "2"

    # Query all
    all_creds = state_store.get_credentials()
    assert all_creds.count == 2

    # Query with username filter
    admin_filter = state_store.get_credentials(CredentialQuery(username="admin"))
    assert admin_filter.count == 1
    assert admin_filter.items[0].username == "admin"

    # Query with non-matching filter
    missing_filter = state_store.get_credentials(CredentialQuery(username="nonexistent"))
    assert missing_filter.count == 0
