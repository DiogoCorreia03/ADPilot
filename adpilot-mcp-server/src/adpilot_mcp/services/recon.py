from typing import Literal
from adpilot_mcp.core.executor import run_command_async
from adpilot_mcp.models.execution import CommandResult


def build_curl_command(
    url: str,
    method: str = "GET",
    headers: str | None = None,
    data: str | None = None,
    extra_args: str | None = None,
) -> str:
    """Construct a curl command string."""
    cmd = f"curl -X {method} '{url}'"
    if headers:
        cmd += f' -H "{headers}"'
    if data:
        cmd += f" -d '{data}'"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_curl(
    url: str,
    method: str = "GET",
    headers: str | None = None,
    data: str | None = None,
    extra_args: str | None = None,
    timeout: int = 60,
) -> CommandResult:
    """Execute curl command asynchronously."""
    cmd = build_curl_command(url, method, headers, data, extra_args)
    return await run_command_async(cmd, timeout=timeout)


def build_nmap_command(target: str, flags: str = "-sV --open -T4") -> str:
    """Construct an nmap command string."""
    return f"nmap {flags} {target}"


async def run_nmap_scan(
    target: str, flags: str = "-sV --open -T4", timeout: int = 300
) -> CommandResult:
    """Execute nmap scan asynchronously."""
    cmd = build_nmap_command(target, flags)
    return await run_command_async(cmd, timeout=timeout)


def build_nslookup_command(
    query: str,
    record_type: Literal["A", "AAAA", "MX", "NS", "SRV", "TXT", "PTR"] | None = None,
    extra_args: str | None = None,
) -> str:
    """Construct an nslookup command string."""
    cmd = "nslookup"
    if record_type:
        cmd += f" -type={record_type}"
    if extra_args:
        cmd += f" {extra_args}"
    cmd += f" {query}"
    return cmd


async def run_nslookup(
    query: str,
    record_type: Literal["A", "AAAA", "MX", "NS", "SRV", "TXT", "PTR"] | None = None,
    extra_args: str | None = None,
    timeout: int = 60,
) -> CommandResult:
    """Execute nslookup asynchronously."""
    cmd = build_nslookup_command(query, record_type, extra_args)
    return await run_command_async(cmd, timeout=timeout)
