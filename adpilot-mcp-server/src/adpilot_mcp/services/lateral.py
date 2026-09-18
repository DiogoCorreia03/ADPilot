from pathlib import Path
from typing import Literal

from adpilot_mcp.config import get_settings
from adpilot_mcp.core.executor import run_command_async
from adpilot_mcp.models.execution import CommandResult


def build_secretsdump_command(
    domain: str,
    target: str,
    username: str,
    password: str | None = None,
    dc_ip: str | None = None,
    hashes: str | None = None,
    aes_key: str | None = None,
    use_kerberos: bool = False,
    just_dc: bool = False,
    just_dc_ntlm: bool = False,
    just_dc_user: str | None = None,
    extra_args: str | None = None,
) -> str:
    cmd = f"secretsdump.py {domain}/{username}"
    if password:
        cmd += f":{password}"
    cmd += f"@{target}"
    if not password:
        cmd += " -no-pass"
    if hashes:
        cmd += f" -hashes '{hashes}'"
    if aes_key:
        cmd += f" -aesKey {aes_key}"
    if use_kerberos:
        cmd += " -k -no-pass"
    if dc_ip:
        cmd += f" -dc-ip {dc_ip}"
    if just_dc:
        cmd += " -just-dc"
    elif just_dc_ntlm:
        cmd += " -just-dc-ntlm"
    elif just_dc_user:
        cmd += f" -just-dc-user '{just_dc_user}'"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_secretsdump(
    domain: str,
    target: str,
    username: str,
    password: str | None = None,
    dc_ip: str | None = None,
    hashes: str | None = None,
    aes_key: str | None = None,
    use_kerberos: bool = False,
    just_dc: bool = False,
    just_dc_ntlm: bool = False,
    just_dc_user: str | None = None,
    ldap_filter: str | None = None,
    extra_args: str | None = None,
    timeout: int = 300,
) -> CommandResult:
    if ldap_filter:
        extra_args = f"-ldapfilter '{ldap_filter}' {extra_args or ''}".strip()
    cmd = build_secretsdump_command(
        domain,
        target,
        username,
        password,
        dc_ip,
        hashes,
        aes_key,
        use_kerberos,
        just_dc,
        just_dc_ntlm,
        just_dc_user,
        extra_args,
    )
    return await run_command_async(cmd, timeout=timeout)


def build_wmiexec_command(
    domain: str,
    target: str,
    username: str,
    password: str | None = None,
    command: str | None = "whoami",
    dc_ip: str | None = None,
    hashes: str | None = None,
    aes_key: str | None = None,
    use_kerberos: bool = False,
    share: str | None = None,
    extra_args: str | None = None,
) -> str:
    target_str = f"{domain}/{username}"
    if password:
        target_str += f":{password}"
    target_str += f"@{target}"

    cmd = f"wmiexec.py {target_str}"
    if hashes:
        cmd += f" -hashes '{hashes}'"
    if aes_key:
        cmd += f" -aesKey {aes_key}"
    if use_kerberos:
        cmd += " -k -no-pass"
    if dc_ip:
        cmd += f" -dc-ip {dc_ip}"
    if share:
        cmd += f" -share '{share}'"
    if command:
        cmd += f" '{command}'"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_wmiexec(
    domain: str,
    target: str,
    username: str,
    password: str | None = None,
    command: str | None = "whoami",
    dc_ip: str | None = None,
    hashes: str | None = None,
    aes_key: str | None = None,
    use_kerberos: bool = False,
    share: str | None = None,
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    cmd = build_wmiexec_command(
        domain,
        target,
        username,
        password,
        command,
        dc_ip,
        hashes,
        aes_key,
        use_kerberos,
        share,
        extra_args,
    )
    return await run_command_async(cmd, timeout=timeout)


def build_mssqlclient_command(
    domain: str,
    target: str,
    username: str,
    password: str | None = None,
    commands: str | None = "enum_logins",
    windows_auth: bool = True,
    hashes: str | None = None,
    aes_key: str | None = None,
    use_kerberos: bool = False,
    db: str | None = None,
    extra_args: str | None = None,
) -> str:
    target_str = f"{domain}/{username}"
    if password:
        target_str += f":{password}"
    target_str += f"@{target}"

    cmd = f"mssqlclient.py {target_str}"
    if windows_auth:
        cmd += " -windows-auth"
    if hashes:
        cmd += f" -hashes '{hashes}'"
    if aes_key:
        cmd += f" -aesKey {aes_key}"
    if use_kerberos:
        cmd += " -k -no-pass"
    elif not password:
        cmd += " -no-pass"
    if db:
        cmd += f" -db '{db}'"
    if commands:
        cmd += f' -command "{commands}"'
    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_mssqlclient(
    domain: str,
    target: str,
    username: str,
    password: str | None = None,
    commands: str | None = "enum_logins",
    windows_auth: bool = True,
    hashes: str | None = None,
    aes_key: str | None = None,
    use_kerberos: bool = False,
    db: str | None = None,
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    cmd = build_mssqlclient_command(
        domain,
        target,
        username,
        password,
        commands,
        windows_auth,
        hashes,
        aes_key,
        use_kerberos,
        db,
        extra_args,
    )
    return await run_command_async(cmd, timeout=timeout)


def build_addcomputer_command(
    domain: str,
    computer_name: str,
    computer_password: str,
    username: str,
    password: str | None = None,
    dc_ip: str | None = None,
    dc_hostname: str | None = None,
    method: Literal["SAMR", "LDAPS"] = "SAMR",
    hashes: str | None = None,
    aes_key: str | None = None,
    use_kerberos: bool = False,
    extra_args: str | None = None,
) -> str:
    if not computer_name.endswith("$"):
        computer_name += "$"

    target_str = f"{domain}/{username}"
    if password:
        target_str += f":{password}"
    else:
        target_str += " -no-pass"

    cmd = f"addcomputer.py {target_str} -computer-name '{computer_name}' -computer-pass '{computer_password}'"
    if method:
        cmd += f" -method {method}"
    if hashes:
        cmd += f" -hashes '{hashes}'"
    if aes_key:
        cmd += f" -aesKey {aes_key}"
    if use_kerberos:
        cmd += " -k -no-pass"
    if dc_ip:
        cmd += f" -dc-ip {dc_ip}"
    if dc_hostname:
        cmd += f" -dc-host {dc_hostname}"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_addcomputer(
    domain: str,
    computer_name: str,
    computer_password: str,
    username: str,
    password: str | None = None,
    dc_ip: str | None = None,
    dc_hostname: str | None = None,
    method: Literal["SAMR", "LDAPS"] = "SAMR",
    hashes: str | None = None,
    aes_key: str | None = None,
    use_kerberos: bool = False,
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    cmd = build_addcomputer_command(
        domain,
        computer_name,
        computer_password,
        username,
        password,
        dc_ip,
        dc_hostname,
        method,
        hashes,
        aes_key,
        use_kerberos,
        extra_args,
    )
    return await run_command_async(cmd, timeout=timeout)


def build_rename_machine_command(
    domain: str,
    current_name: str,
    new_name: str,
    username: str,
    password: str | None = None,
    dc_ip: str | None = None,
    hashes: str | None = None,
    use_kerberos: bool = False,
    extra_args: str | None = None,
) -> str:
    if not current_name.endswith("$"):
        current_name += "$"
    if not new_name.endswith("$"):
        new_name += "$"

    cmd = f"python3 /root/samaccountname_scripts/renameMachine.py {domain}/{username}"
    if password:
        cmd += f":{password}"
    else:
        cmd += " -no-pass"

    cmd += f" -current-name '{current_name}' -new-name '{new_name}'"
    if hashes:
        cmd += f" -hashes '{hashes}'"
    if use_kerberos:
        cmd += " -k -no-pass"
    if dc_ip:
        cmd += f" -dc-ip {dc_ip}"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_rename_machine(
    domain: str,
    current_name: str,
    new_name: str,
    username: str,
    password: str | None = None,
    dc_ip: str | None = None,
    hashes: str | None = None,
    use_kerberos: bool = False,
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    cmd = build_rename_machine_command(
        domain,
        current_name,
        new_name,
        username,
        password,
        dc_ip,
        hashes,
        use_kerberos,
        extra_args,
    )
    return await run_command_async(cmd, timeout=timeout)


def build_certipy_command(
    action: Literal[
        "account",
        "auth",
        "ca",
        "cert",
        "find",
        "forge",
        "ptt",
        "relay",
        "req",
        "shadow",
        "template",
    ],
    domain: str | None = None,
    username: str | None = None,
    password: str | None = None,
    target: str | None = None,
    dc_ip: str | None = None,
    ca: str | None = None,
    template: str | None = None,
    upn: str | None = None,
    use_kerberos: bool = False,
    hashes: str | None = None,
    extra_args: str | None = None,
) -> tuple[str | None, str | None]:
    cmd = f"certipy {action}"
    if username and domain:
        cmd += f" -u '{username}@{domain}'"
    if password:
        cmd += f" -p '{password}'"
    else:
        cmd += " -no-pass"
    if hashes:
        cmd += f" -hashes '{hashes}'"
    if use_kerberos:
        cmd += " -k -no-pass"
    if target:
        cmd += f" -target '{target}'"
    if dc_ip:
        cmd += f" -dc-ip {dc_ip}"

    if action == "find":
        cmd += " -vulnerable"
    elif action == "req":
        if not ca or not template:
            return None, "req action requires 'ca' and 'template'"
        cmd += f" -ca '{ca}' -template '{template}'"
        if upn:
            cmd += f" -upn '{upn}'"

    if extra_args:
        cmd += f" {extra_args}"
    return cmd, None


async def run_certipy(
    action: Literal[
        "account",
        "auth",
        "ca",
        "cert",
        "find",
        "forge",
        "ptt",
        "relay",
        "req",
        "shadow",
        "template",
    ],
    domain: str | None = None,
    username: str | None = None,
    password: str | None = None,
    target: str | None = None,
    dc_ip: str | None = None,
    ca: str | None = None,
    template: str | None = None,
    upn: str | None = None,
    use_kerberos: bool = False,
    hashes: str | None = None,
    extra_args: str | None = None,
    timeout: int = 300,
) -> CommandResult:
    cmd, err = build_certipy_command(
        action,
        domain,
        username,
        password,
        target,
        dc_ip,
        ca,
        template,
        upn,
        use_kerberos,
        hashes,
        extra_args,
    )
    if err:
        return CommandResult(
            command=f"certipy {action}",
            stdout="",
            stderr=err,
            returncode=-1,
            success=False,
        )
    return await run_command_async(cmd, timeout=timeout)  # pyright: ignore[reportArgumentType]


def build_dnstool_command(
    hostname: str,
    action: Literal["add", "modify", "query", "remove", "ressurrect", "ldapdelete"],
    username: str,
    password: str,
    zone: str | None = None,
    record: str | None = None,
    record_data: str | None = None,
    use_kerberos: bool = False,
    extra_args: str | None = None,
) -> str:
    cmd = f"python3 /root/krbrelayx/dnstool.py {hostname} -u '{username}'"
    if password:
        cmd += f" -p '{password}'"
    cmd += f" -a {action}"
    if action == "add":
        cmd += " -t A"
    if record:
        cmd += f" -r '{record}'"
    if zone:
        cmd += f" -z '{zone}'"
    if record_data:
        cmd += f" -d '{record_data}'"
    if use_kerberos:
        cmd += " -k"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_dnstool(
    hostname: str,
    action: Literal["add", "modify", "query", "remove", "ressurrect", "ldapdelete"],
    username: str,
    password: str,
    zone: str | None = None,
    record: str | None = None,
    record_data: str | None = None,
    use_kerberos: bool = False,
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    cmd = build_dnstool_command(
        hostname,
        action,
        username,
        password,
        zone,
        record,
        record_data,
        use_kerberos,
        extra_args,
    )
    return await run_command_async(cmd, timeout=timeout)


def build_addspn_command(
    hostname: str,
    username: str,
    password: str | None = None,
    action: Literal["add", "remove", "clear", "query"] = "add",
    spn: str | None = None,
    target: str | None = None,
    target_type: Literal["hostname", "samname"] | None = None,
    use_kerberos: bool = False,
    dc_ip: str | None = None,
    extra_args: str | None = None,
) -> tuple[str | None, str | None]:
    cmd = f"python3 /root/krbrelayx/addspn.py {hostname} -u '{username}'"
    if password:
        cmd += f" -p '{password}'"

    if action == "add":
        pass
    elif action == "remove":
        cmd += " -r"
    elif action == "clear":
        cmd += " -c"
    elif action == "query":
        cmd += " -q"
    else:
        return (
            None,
            f"Invalid action '{action}'. Valid actions are: 'add', 'remove', 'clear', 'query'.",
        )

    if action in ["add", "remove"]:
        if not spn:
            return None, f"'{action}' action requires 'spn' argument."
        cmd += f" -s '{spn}'"

    if target:
        cmd += f" -t '{target}'"
    if target_type:
        cmd += f" -T '{target_type}'"
    if use_kerberos:
        cmd += " -k"
    if dc_ip:
        cmd += f" -dc-ip {dc_ip}"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd, None


async def run_addspn(
    hostname: str,
    username: str,
    password: str | None = None,
    action: Literal["add", "remove", "clear", "query"] = "add",
    spn: str | None = None,
    target: str | None = None,
    target_type: Literal["hostname", "samname"] | None = None,
    use_kerberos: bool = False,
    dc_ip: str | None = None,
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    cmd, err = build_addspn_command(
        hostname,
        username,
        password,
        action,
        spn,
        target,
        target_type,
        use_kerberos,
        dc_ip,
        extra_args,
    )
    if err:
        return CommandResult(
            command="addspn.py",
            stdout="",
            stderr=err,
            returncode=-1,
            success=False,
        )
    return await run_command_async(cmd, timeout=timeout)  # pyright: ignore[reportArgumentType]






