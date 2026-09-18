import shlex
from pathlib import Path
from typing import Any


def quote_arg(val: Any) -> str:
    """
    Safely quote a shell argument using POSIX shell quoting.
    Returns empty string for None.
    """
    if val is None:
        return ""
    s = str(val)
    return shlex.quote(s)


def sanitize_env(env_extra: dict[str, Any] | None) -> dict[str, str]:
    """Ensure all environment variable values are strings."""
    if not env_extra:
        return {}
    return {k: str(v) for k, v in env_extra.items() if v is not None}


def safe_subpath(base_dir: Path, subpath: str | Path) -> Path:
    """
    Ensure subpath resolves strictly inside base_dir to prevent directory traversal.
    Raises ValueError if subpath is absolute or traverses outside base_dir.
    """
    base = base_dir.resolve()
    raw_path = Path(subpath)
    if raw_path.is_absolute() or str(subpath).startswith(("/", "\\")):
        raise ValueError(f"Path traversal detected: absolute path {subpath} is not allowed")

    target = (base / raw_path).resolve()
    try:
        target.relative_to(base)
    except ValueError:
        raise ValueError(f"Path traversal detected: {subpath} escapes {base_dir}")
    return target

