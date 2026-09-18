import time
from pathlib import Path
from typing import Literal

from adpilot_mcp.config import get_settings
from adpilot_mcp.core.executor import run_command_async
from adpilot_mcp.models.execution import CommandResult


def build_smbclient_command(
    target: str,
    service: str,
    username: str = "guest",
    password: str | None = None,
    command: str | None = "ls",
    extra_args: str | None = None,
) -> str:
    cmd = f"smbclient //{target}/{service}"
    if password is None:
        cmd += f" -U '{username}' -N"
    elif password == "":
        cmd += f" -U '{username}%'"
    else:
        cmd += f" -U '{username}%{password}'"

    if command:
        cmd += f" -c '{command}; exit'"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_smbclient(
    target: str,
    service: str,
    username: str = "guest",
    password: str | None = None,
    command: str | None = "ls",
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    cmd = build_smbclient_command(target, service, username, password, command, extra_args)
    return await run_command_async(cmd, timeout=timeout)


def build_ldapsearch_command(
    target: str,
    base_dn: str,
    search_filter: str = "(objectClass=*)",
    attributes: str | None = None,
    bind_dn: str | None = None,
    password: str | None = None,
    use_ssl: bool = False,
    port: int | None = None,
    extra_args: str | None = None,
) -> str:
    protocol = "ldaps" if use_ssl else "ldap"
    uri = f"{protocol}://{target}"
    if port:
        uri += f":{port}"

    cmd = f"ldapsearch -x -H '{uri}' -b '{base_dn}' '{search_filter}'"
    if attributes:
        cmd += f" {attributes}"

    if bind_dn:
        cmd += f" -D '{bind_dn}'"
        if password:
            cmd += f" -w '{password}'"
        else:
            cmd += " -w ''"

    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_ldapsearch(
    target: str,
    base_dn: str,
    search_filter: str = "(objectClass=*)",
    attributes: str | None = None,
    bind_dn: str | None = None,
    password: str | None = None,
    use_ssl: bool = False,
    port: int | None = None,
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    cmd = build_ldapsearch_command(
        target, base_dn, search_filter, attributes, bind_dn, password, use_ssl, port, extra_args
    )
    return await run_command_async(cmd, timeout=timeout)


def build_ldap_dump_command(
    hostname: str,
    out_dir: Path,
    domain: str | None = None,
    username: str | None = None,
    password: str | None = None,
) -> str:
    cmd = f"ldapdomaindump {hostname} --no-html --no-grep"
    if domain and username and password:
        cmd += f" -u '{domain}\\{username}' -p '{password}'"
    cmd += f" -o {out_dir} 2>&1"
    return cmd


async def run_ldap_dump(
    hostname: str,
    domain: str | None = None,
    username: str | None = None,
    password: str | None = None,
    timeout: int = 300,
) -> CommandResult:
    settings = get_settings()
    out_dir = settings.ad_state_dir / f"ldapdomaindump-{time.strftime('%Y%m%d-%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = build_ldap_dump_command(hostname, out_dir, domain, username, password)
    result = await run_command_async(cmd, timeout=timeout)
    result.extra["output_dir"] = str(out_dir)
    return result


def build_netexec_command(
    protocol: Literal[
        "smb", "ldap", "ssh", "ftp", "wmi", "winrm", "rdp", "vnc", "mssql", "nfs"
    ],
    target: str,
    username: str = "",
    password: str = "",
    extra_args: str | None = None,
) -> str:
    cmd = f"nxc {protocol} {target}"
    extra_args = extra_args or ""
    if "--shares" in extra_args:
        if not username:
            username = "a"
        if not password:
            password = " "

    if username:
        cmd += f" -u '{username}'"
        if password:
            cmd += f" -p '{password}'"

    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_netexec(
    protocol: Literal[
        "smb", "ldap", "ssh", "ftp", "wmi", "winrm", "rdp", "vnc", "mssql", "nfs"
    ],
    target: str,
    username: str = "",
    password: str = "",
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    cmd = build_netexec_command(protocol, target, username, password, extra_args)
    return await run_command_async(cmd, timeout=timeout)


def build_getadusers_command(
    domain: str,
    username: str | None = None,
    password: str | None = None,
    dc_ip: str | None = None,
    dc_hostname: str | None = None,
    use_kerberos: bool = False,
    hash_: str | None = None,
    all_users: bool = True,
    extra_args: str | None = None,
) -> str:
    target_str = domain
    if username:
        target_str += f"/{username}"
        if password:
            target_str += f":{password}"
    else:
        target_str += "/"

    cmd = f"GetADUsers.py {target_str}"
    if all_users:
        cmd += " -all"
    if dc_ip:
        cmd += f" -dc-ip {dc_ip}"
    if dc_hostname:
        cmd += f" -dc-host {dc_hostname}"
    if use_kerberos:
        cmd += " -k -no-pass"
    if hash_:
        cmd += f" -hashes {hash_}"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_getadusers(
    domain: str,
    username: str | None = None,
    password: str | None = None,
    dc_ip: str | None = None,
    dc_hostname: str | None = None,
    use_kerberos: bool = False,
    hash_: str | None = None,
    all_users: bool = True,
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    cmd = build_getadusers_command(
        domain, username, password, dc_ip, dc_hostname, use_kerberos, hash_, all_users, extra_args
    )
    return await run_command_async(cmd, timeout=timeout)


def build_finddelegation_command(
    domain: str,
    username: str,
    password: str | None = None,
    target_domain: str | None = None,
    dc_ip: str | None = None,
    hashes: str | None = None,
    aes_key: str | None = None,
    use_kerberos: bool = False,
    extra_args: str | None = None,
) -> str:
    target_str = f"{domain}/{username}"
    if password:
        target_str += f":{password}"
    else:
        target_str += " -no-pass"

    cmd = f"findDelegation.py {target_str}"
    if target_domain:
        cmd += f" -target-domain {target_domain}"
    if hashes:
        cmd += f" -hashes '{hashes}'"
    if aes_key:
        cmd += f" -aesKey {aes_key}"
    if use_kerberos:
        cmd += " -k -no-pass"
    if dc_ip:
        cmd += f" -dc-ip {dc_ip}"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_finddelegation(
    domain: str,
    username: str,
    password: str | None = None,
    target_domain: str | None = None,
    dc_ip: str | None = None,
    hashes: str | None = None,
    aes_key: str | None = None,
    use_kerberos: bool = False,
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    cmd = build_finddelegation_command(
        domain, username, password, target_domain, dc_ip, hashes, aes_key, use_kerberos, extra_args
    )
    return await run_command_async(cmd, timeout=timeout)


def build_lookupsid_command(
    domain: str,
    target: str,
    username: str,
    password: str | None = None,
    max_rid: int = 4000,
    dc_ip: str | None = None,
    hashes: str | None = None,
    use_kerberos: bool = False,
    domain_sids: bool = False,
    extra_args: str | None = None,
) -> str:
    cmd = f"lookupsid.py {domain}/{username}"
    if password:
        cmd += f":{password}"
    cmd += f"@{target} {max_rid}"
    if hashes:
        cmd += f" -hashes '{hashes}'"
    if use_kerberos:
        cmd += " -k -no-pass"
    elif not password:
        cmd += " -no-pass"
    if dc_ip:
        cmd += f" -dc-ip {dc_ip}"
    if domain_sids:
        cmd += " -domain-sids"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_lookupsid(
    domain: str,
    target: str,
    username: str,
    password: str | None = None,
    max_rid: int = 4000,
    dc_ip: str | None = None,
    hashes: str | None = None,
    use_kerberos: bool = False,
    domain_sids: bool = False,
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    cmd = build_lookupsid_command(
        domain, target, username, password, max_rid, dc_ip, hashes, use_kerberos, domain_sids, extra_args
    )
    return await run_command_async(cmd, timeout=timeout)



