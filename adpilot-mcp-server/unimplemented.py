# reject tool calls unauthorized in the active phase
async def on_call_tool(self, context: MiddlewareContext, call_next):
    settings = get_settings()
    headers = get_http_headers()
    phase = _extract_phase(headers, settings.agent_phase_header)

    if (
        phase is not None
        and context.fastmcp_context
        and getattr(context.fastmcp_context, "fastmcp", None)
    ):
        tool_name = getattr(context.message, "name", None)
        if tool_name:
            try:
                tool = await context.fastmcp_context.fastmcp.get_tool(tool_name)
                if tool and tool.tags and phase not in tool.tags:
                    raise ValueError(
                        f"Tool '{tool_name}' is not authorized during pentest phase '{phase.value}'."
                    )
            except Exception as e:
                if "not authorized" in str(e):
                    raise
                logger.debug(f"Could not verify phase tags for tool {tool_name}: {e}")

    return await call_next(context)


# -------------------------------------------------------------------------------------------------


def build_psexec_command(
    domain: str,
    username: str,
    password: str | None = None,
    command: str | None = None,
    dc_ip: str | None = None,
    hashes: str | None = None,
    aes_key: str | None = None,
    use_kerberos: bool = False,
    share: str | None = None,
    service_name: str | None = None,
    extra_args: str | None = None,
) -> str:
    target_str = f"{domain}/{username}"
    if password:
        target_str += f":{password}"
    else:
        target_str += " -no-pass"

    cmd = f"psexec.py {target_str}"
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
    if service_name:
        cmd += f" -service-name '{service_name}'"
    if command:
        cmd += f" '{command}'"
    else:
        cmd += " cmd.exe"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_psexec(
    domain: str,
    username: str,
    password: str | None = None,
    command: str | None = None,
    dc_ip: str | None = None,
    hashes: str | None = None,
    aes_key: str | None = None,
    use_kerberos: bool = False,
    share: str | None = None,
    service_name: str | None = None,
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    cmd = build_psexec_command(
        domain,
        username,
        password,
        command,
        dc_ip,
        hashes,
        aes_key,
        use_kerberos,
        share,
        service_name,
        extra_args,
    )
    return await run_command_async(cmd, timeout=timeout)


@mcp.tool(tags={PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC})
async def run_psexec(
    domain: str,
    username: str,
    password: str | None = None,
    command: str | None = None,
    dc_ip: str | None = None,
    hashes: str | None = None,
    aes_key: str | None = None,
    use_kerberos: bool = False,
    share: str | None = None,
    service_name: str | None = None,
    extra_args: str | None = None,
    timeout: int = 120,
) -> str:
    """
    Run Impacket's psexec.py for remote command execution over SMB.
    """
    result = await lateral_service.run_psexec(
        domain=domain,
        username=username,
        password=password,
        command=command,
        dc_ip=dc_ip,
        hashes=hashes,
        aes_key=aes_key,
        use_kerberos=use_kerberos,
        share=share,
        service_name=service_name,
        extra_args=extra_args,
        timeout=timeout,
    )
    return result.to_mcp_result()

# -------------------------------------------------------------------------------------------------

@mcp.tool(tags={PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC})
async def run_ntlmrelayx(
    targets: str | None = None,
    target_file: str | None = None,
    smb2support: bool = True,
    protocol: str | None = None,
    command: str | None = None,
    lootdir: str | None = None,
    interface_ip: str | None = None,
    port: int | None = None,
    adcs: bool = False,
    template: str | None = None,
    no_http_server: bool = False,
    no_smb_server: bool = False,
    no_wcf_server: bool = False,
    no_raw_server: bool = False,
    extra_args: str | None = None,
    timeout: int = 120,
) -> str:
    """
    Run ntlmrelayx.py for NTLM relay attacks.
    """
    result = await lateral_service.run_ntlmrelayx(
        targets=targets,
        target_file=target_file,
        smb2support=smb2support,
        protocol=protocol,
        command=command,
        lootdir=lootdir,
        interface_ip=interface_ip,
        port=port,
        adcs=adcs,
        template=template,
        no_http_server=no_http_server,
        no_smb_server=no_smb_server,
        no_wcf_server=no_wcf_server,
        no_raw_server=no_raw_server,
        extra_args=extra_args,
        timeout=timeout,
    )
    return result.to_mcp_result()

def build_ntlmrelayx_command(
    targets: str | None = None,
    target_file: str | None = None,
    smb2support: bool = True,
    protocol: str | None = None,
    command: str | None = None,
    lootdir: str | None = None,
    interface_ip: str | None = None,
    port: int | None = None,
    adcs: bool = False,
    template: str | None = None,
    no_http_server: bool = False,
    no_smb_server: bool = False,
    no_wcf_server: bool = False,
    no_raw_server: bool = False,
    extra_args: str | None = None,
) -> str:
    cmd = "ntlmrelayx.py"
    if targets:
        cmd += f" -t '{targets}'"
    if target_file:
        cmd += f" -tf '{target_file}'"
    if smb2support:
        cmd += " -smb2support"
    if command:
        cmd += f" -c '{command}'"
    if lootdir:
        cmd += f" -l '{lootdir}'"
    if interface_ip:
        cmd += f" -ip {interface_ip}"
    if port:
        cmd += f" -port {port}"
    if adcs:
        cmd += " --adcs"
        if template:
            cmd += f" --template '{template}'"
    if no_http_server:
        cmd += " --no-http-server"
    if no_smb_server:
        cmd += " --no-smb-server"
    if no_wcf_server:
        cmd += " --no-wcf-server"
    if no_raw_server:
        cmd += " --no-raw-server"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_ntlmrelayx(
    targets: str | None = None,
    target_file: str | None = None,
    smb2support: bool = True,
    protocol: str | None = None,
    command: str | None = None,
    lootdir: str | None = None,
    interface_ip: str | None = None,
    port: int | None = None,
    adcs: bool = False,
    template: str | None = None,
    no_http_server: bool = False,
    no_smb_server: bool = False,
    no_wcf_server: bool = False,
    no_raw_server: bool = False,
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:

    cmd = build_ntlmrelayx_command(
        targets,
        target_file,
        smb2support,
        protocol,
        command,
        lootdir,
        interface_ip,
        port,
        adcs,
        template,
        no_http_server,
        no_smb_server,
        no_wcf_server,
        no_raw_server,
        extra_args,
    )
    return await run_command_async(cmd, timeout=timeout)

# -------------------------------------------------------------------------------------------------

@mcp.tool(tags={PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC})
async def run_printerbug(
    domain: str,
    username: str,
    target: str,
    listener: str,
    password: str | None = None,
    dc_ip: str | None = None,
    hashes: str | None = None,
    kerberos: bool = False,
    no_pass: bool = False,
    extra_args: str | None = None,
    timeout: int = 60,
) -> str:
    """
    Run krbrelayx's printerbug (MS-RPRN abuse) to coerce a target machine to authenticate.
    """
    result = await lateral_service.run_printerbug(
        domain=domain,
        username=username,
        target=target,
        listener=listener,
        password=password,
        dc_ip=dc_ip,
        hashes=hashes,
        kerberos=kerberos,
        no_pass=no_pass,
        extra_args=extra_args,
        timeout=timeout,
    )
    return result.to_mcp_result()

def build_printerbug_command(
    domain: str,
    username: str,
    target: str,
    listener: str,
    password: str | None = None,
    dc_ip: str | None = None,
    hashes: str | None = None,
    kerberos: bool = False,
    no_pass: bool = False,
    extra_args: str | None = None,
) -> str:
    cred_str = f"{domain}/{username}"
    if password:
        cred_str += f":{password}"
    else:
        cred_str += ":"
    cred_str += f"@{target}"

    cmd = f"printerbug.py {cred_str} {listener}"
    if hashes:
        cmd += f" -hashes '{hashes}'"
    if kerberos:
        cmd += " -k"
    if no_pass:
        cmd += " -no-pass"
    if dc_ip:
        cmd += f" -dc-ip {dc_ip}"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_printerbug(
    domain: str,
    username: str,
    target: str,
    listener: str,
    password: str | None = None,
    dc_ip: str | None = None,
    hashes: str | None = None,
    kerberos: bool = False,
    no_pass: bool = False,
    extra_args: str | None = None,
    timeout: int = 60,
) -> CommandResult:
    cmd = build_printerbug_command(
        domain,
        username,
        target,
        listener,
        password,
        dc_ip,
        hashes,
        kerberos,
        no_pass,
        extra_args,
    )
    return await run_command_async(cmd, timeout=timeout)

# -------------------------------------------------------------------------------------------------

@mcp.tool(tags={PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC})
async def run_krbrelayx(
    target: str | None = None,
    target_file: str | None = None,
    interface_ip: str | None = None,
    listen_port: int | None = None,
    lootdir: str | None = None,
    adcs: bool = False,
    template: str | None = None,
    no_http: bool = False,
    no_smb: bool = False,
    no_dns: bool = False,
    delegate_access: bool = False,
    escalate_user: str | None = None,
    extra_args: str | None = None,
    timeout: int = 120,
) -> str:
    """
    Run krbrelayx.py for Kerberos relay attacks.
    """
    result = await lateral_service.run_krbrelayx(
        target=target,
        target_file=target_file,
        interface_ip=interface_ip,
        listen_port=listen_port,
        lootdir=lootdir,
        adcs=adcs,
        template=template,
        no_http=no_http,
        no_smb=no_smb,
        no_dns=no_dns,
        delegate_access=delegate_access,
        escalate_user=escalate_user,
        extra_args=extra_args,
        timeout=timeout,
    )
    return result.to_mcp_result()

def build_krbrelayx_command(
    target: str | None = None,
    target_file: str | None = None,
    interface_ip: str | None = None,
    listen_port: int | None = None,
    lootdir: str | None = None,
    adcs: bool = False,
    template: str | None = None,
    no_http: bool = False,
    no_smb: bool = False,
    no_dns: bool = False,
    delegate_access: bool = False,
    escalate_user: str | None = None,
    extra_args: str | None = None,
) -> str:
    cmd = "krbrelayx.py"
    if target:
        cmd += f" -t '{target}'"
    if target_file:
        cmd += f" -tf '{target_file}'"
    if interface_ip:
        cmd += f" -ip {interface_ip}"
    if listen_port:
        cmd += f" -p {listen_port}"
    if lootdir:
        cmd += f" -l '{lootdir}'"
    if adcs:
        cmd += " --adcs"
        if template:
            cmd += f" --template '{template}'"
    if delegate_access:
        cmd += " --delegate-access"
    if escalate_user:
        cmd += f" --escalate-user '{escalate_user}'"
    if no_http:
        cmd += " --no-http"
    if no_smb:
        cmd += " --no-smb"
    if no_dns:
        cmd += " --no-dns"
    if extra_args:
        cmd += f" {extra_args}"
    return cmd


async def run_krbrelayx(
    target: str | None = None,
    target_file: str | None = None,
    interface_ip: str | None = None,
    listen_port: int | None = None,
    lootdir: str | None = None,
    adcs: bool = False,
    template: str | None = None,
    no_http: bool = False,
    no_smb: bool = False,
    no_dns: bool = False,
    delegate_access: bool = False,
    escalate_user: str | None = None,
    extra_args: str | None = None,
    timeout: int = 120,
) -> CommandResult:
    cmd = build_krbrelayx_command(
        target,
        target_file,
        interface_ip,
        listen_port,
        lootdir,
        adcs,
        template,
        no_http,
        no_smb,
        no_dns,
        delegate_access,
        escalate_user,
        extra_args,
    )
    return await run_command_async(cmd, timeout=timeout)

# -------------------------------------------------------------------------------------------------

@mcp.tool(tags={PentestPhase.INTERNAL_RECONNAISSANCE})
async def bloodhound_collect(
    dc_ip: str,
    domain: str,
    username: str,
    password: str = "",
    hash_: str = "",
    collection_method: str = "All",
    timeout: int = 600,
) -> str:
    """
    Run BloodHound data collection (bloodhound-python). Saves output to state dir.
    """
    result = await ad_service.bloodhound_collect(
        dc_ip=dc_ip,
        domain=domain,
        username=username,
        password=password,
        hash_=hash_,
        collection_method=collection_method,
        timeout=timeout,
    )
    return result.to_mcp_result()

def build_bloodhound_command(
    dc_ip: str,
    domain: str,
    username: str,
    out_dir: Path,
    password: str = "",
    hash_: str = "",
    collection_method: str = "All",
) -> str:
    auth = f"--hashes '{hash_}'" if hash_ else f"-p '{password}'"
    return (
        f"bloodhound-python -u '{username}' {auth} "
        f"-d '{domain}' -dc '{dc_ip}' -ns {dc_ip} "
        f"-c {collection_method} --zip -o {out_dir} 2>&1"
    )


async def bloodhound_collect(
    dc_ip: str,
    domain: str,
    username: str,
    password: str = "",
    hash_: str = "",
    collection_method: str = "All",
    timeout: int = 600,
) -> CommandResult:
    settings = get_settings()
    out_dir = settings.ad_state_dir / "bloodhound"
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = build_bloodhound_command(
        dc_ip, domain, username, out_dir, password, hash_, collection_method
    )
    result = await run_command_async(cmd, timeout=timeout)
    result.extra["output_dir"] = str(out_dir)
    return result

# -------------------------------------------------------------------------------------------------

@mcp.tool(
    tags={PentestPhase.INITIAL_ACCESS, PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC}
)
async def responder_start(interface: str, flags: str = "-wF") -> str:
    """
    Start Responder in the background on the specified interface with given flags.
    """
    result = await lateral_service.responder_start(interface=interface, flags=flags)
    return result.to_mcp_result()

async def responder_start(interface: str, flags: str = "-wF") -> CommandResult:
    settings = get_settings()
    log_dir = settings.ad_state_dir / "responder_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "responder.log"
    cmd = f"nohup responder -I {interface} {flags} > {log_file} 2>&1 & echo $!"
    result = await run_command_async(cmd, timeout=10)
    result.extra["log_file"] = str(log_file)
    result.extra["note"] = f"Monitor with: tail -f {log_file}"
    return result

@mcp.tool(
    tags={PentestPhase.INITIAL_ACCESS, PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC}
)
async def responder_stop() -> str:
    """
    Stop all running Responder instances.
    """
    result = await lateral_service.responder_stop()
    return result.to_mcp_result()

async def responder_stop() -> CommandResult:
    cmd = "pkill -f 'responder -I' 2>&1"
    return await run_command_async(cmd, timeout=10)

# -------------------------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_server_resources_and_prompts(test_server):
    resources = await test_server.list_resources()
    resource_uris = {str(r.uri) for r in resources}
    assert "ad://state/credentials" in resource_uris
    assert "ad://state/summary" in resource_uris

    prompts = await test_server.list_prompts()
    prompt_names = {p.name for p in prompts}
    assert "ad_phase_playbook" in prompt_names

# -------------------------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_run_command_async_output_truncation():
    # Produce output larger than 50,000 characters
    cmd = "python3 -c \"print('A' * 60000)\""
    res = await run_command_async(cmd, timeout=10)
    assert res.success is True
    assert len(res.stdout) < 60000
    assert "Output truncated" in res.stdout

# -------------------------------------------------------------------------------------------------

def test_extract_phase_case_insensitivity_and_variants():
    # standard
    assert _extract_phase({"pentest_phase": "initial_access"}, "pentest_phase") == PentestPhase.INITIAL_ACCESS
    # hyphenated
    assert _extract_phase({"pentest-phase": "initial_access"}, "pentest_phase") == PentestPhase.INITIAL_ACCESS
    # uppercase
    assert _extract_phase({"PENTEST-PHASE": "check_results"}, "pentest_phase") == PentestPhase.CHECK_RESULTS
    # x- prefix
    assert _extract_phase({"x-pentest-phase": "external_reconnaissance"}, "pentest_phase") == PentestPhase.EXTERNAL_RECONNAISSANCE
    # invalid
    assert _extract_phase({"pentest-phase": "invalid_phase"}, "pentest_phase") is None
    # empty
    assert _extract_phase({}, "pentest_phase") is None

# -------------------------------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tool_filter_middleware_on_call_tool_enforcement():
    middleware = ToolFilterMiddleware()
    mcp = FastMCP("test_server")

    @mcp.tool(tags={PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC})
    def dump_secrets():
        return "secrets"

    # Mock context with fastmcp and message
    mock_context = MagicMock()
    mock_context.fastmcp_context = MagicMock()
    mock_context.fastmcp_context.fastmcp = mcp
    mock_context.message = MagicMock()
    mock_context.message.name = "dump_secrets"

    async def call_next(ctx):
        return "called successfully"

    # When phase is EXTERNAL_RECONNAISSANCE, calling dump_secrets must raise ValueError
    with patch(
        "adpilot_mcp.mcp.middleware.get_http_headers",
        return_value={"pentest-phase": "external_reconnaissance"},
    ):
        with pytest.raises(ValueError, match="not authorized during pentest phase"):
            await middleware.on_call_tool(mock_context, call_next)

    # When phase is LATERAL_MOVEMENT_AND_PRIV_ESC, calling dump_secrets must succeed
    with patch(
        "adpilot_mcp.mcp.middleware.get_http_headers",
        return_value={"pentest-phase": "lateral_movement_and_privilege_escalation"},
    ):
        result = await middleware.on_call_tool(mock_context, call_next)
        assert result == "called successfully"

# -------------------------------------------------------------------------------------------------



# -------------------------------------------------------------------------------------------------

