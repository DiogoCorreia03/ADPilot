import shlex
import pytest
from pathlib import Path
from adpilot_mcp.core.security import quote_arg, sanitize_env, safe_subpath


def test_quote_arg():
    assert quote_arg(None) == ""
    assert quote_arg("") == "''"
    assert quote_arg("simple") == "simple"
    assert quote_arg("with space") == "'with space'"
    assert quote_arg("user's password") == shlex.quote("user's password")
    assert quote_arg("P@ssw0rd!$") == "'P@ssw0rd!$'"



def test_sanitize_env():
    env = {"PORT": 8000, "HOST": "localhost", "EMPTY": None}
    sanitized = sanitize_env(env)
    assert sanitized == {"PORT": "8000", "HOST": "localhost"}
    assert sanitize_env(None) == {}


def test_safe_subpath(tmp_path: Path):
    base = tmp_path / "state"
    base.mkdir()

    # Valid relative subpaths
    p1 = safe_subpath(base, "logs/run.log")
    assert p1 == (base / "logs/run.log").resolve()

    # Path traversal attempts
    with pytest.raises(ValueError, match="Path traversal detected"):
        safe_subpath(base, "../evil.sh")

    with pytest.raises(ValueError, match="Path traversal detected"):
        safe_subpath(base, "../../etc/passwd")

    with pytest.raises(ValueError, match="Path traversal detected"):
        safe_subpath(base, "/etc/shadow")
