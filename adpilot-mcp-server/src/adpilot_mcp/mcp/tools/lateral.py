from typing import Literal
from fastmcp import FastMCP
from adpilot_mcp.models.phases import PentestPhase
from adpilot_mcp.services import lateral as lateral_service


def register(mcp: FastMCP) -> None:
    @mcp.tool(tags={PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC})
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
    ) -> str:
        """
        Run Impacket's secretsdump.py to extract credentials from a target.

        :param domain: Target domain (e.g., 'corp.local').
        :param target: Target hostname or IP (targetName or address).
        :param username: Username for authentication.
        :param password: Password for authentication.
        :param dc_ip: Domain controller IP. If omitted it will use the domain part (FQDN) specified in the target parameter.
        :param hashes: LM:NT hashes. The format is as follows: [LMhash]:NThash (the LM hash is optional, the NT hash must be prepended with a colon (:)).
        :param aes_key: AES key for Kerberos authentication (128 or 256 bits).
        :param use_kerberos: Use Kerberos authentication (-k). Requires either a password or a hash to be provided.
        :param just_dc: Extract only NTDS.DIT data (NTLM hashes and Kerberos keys).
        :param just_dc_ntlm: Extract only NTDS.DIT data (NTLM hashes only).
        :param just_dc_user: Username of the specific domain user to dump, extract only NTDS.DIT data for the user specified.
        :param ldap_filter: Custom LDAP filter to select objects to dump (e.g. '(sAMAccountName=Administrator)').
        :param extra_args: Additional arguments.
        :param timeout: Max execution time (default extended).
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await lateral_service.run_secretsdump(
            domain=domain,
            target=target,
            username=username,
            password=password,
            dc_ip=dc_ip,
            hashes=hashes,
            aes_key=aes_key,
            use_kerberos=use_kerberos,
            just_dc=just_dc,
            just_dc_ntlm=just_dc_ntlm,
            just_dc_user=just_dc_user,
            ldap_filter=ldap_filter,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(tags={PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC})
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
    ) -> str:
        """
        Run Impacket's wmiexec.py for remote command execution via WMI.

        :param domain: Target domain (e.g., 'corp.local').
        :param target: Target hostname or IP (targetName or address).
        :param username: Username for authentication.
        :param password: Password for authentication.
        :param command: Command to execute (e.g., 'whoami').
        :param dc_ip: IP Address of the domain controller. If ommited it use the domain part (FQDN) specified in the target parameter.
        :param hashes: LM:NT hashes. The format is as follows: [LMhash]:NThash (the LM hash is optional, the NT hash must be prepended with a colon (:)).
        :param aes_key: AES key for Kerberos authentication (128 or 256 bits).
        :param use_kerberos: Use Kerberos authentication (-k).
        :param share: SMB share (used for output retrieval, default ADMIN$).
        :param extra_args: Additional arguments.
        :param timeout: Max execution time in seconds.
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await lateral_service.run_wmiexec(
            domain=domain,
            target=target,
            username=username,
            password=password,
            command=command,
            dc_ip=dc_ip,
            hashes=hashes,
            aes_key=aes_key,
            use_kerberos=use_kerberos,
            share=share,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(tags={PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC})
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
    ) -> str:
        """
        Run Impacket's mssqlclient.py for MSSQL interaction and command execution.

        :param domain: Target domain (e.g., 'corp.local').
        :param target: Target MSSQL server (targetName or address).
        :param username: Username for authentication.
        :param password: Password for authentication.
        :param commands: Commands to execute in the SQL shell. Multiple commands can be passed.
        :param windows_auth: Whether or not to use Windows authentication (-windows-auth).
        :param hashes: LM:NT hashes. The format is as follows: [LMhash]:NThash (the LM hash is optional, the NT hash must be prepended with a colon (:)).
        :param aes_key: AES key for Kerberos authentication. (128 or 256 bits)
        :param use_kerberos: Use Kerberos authentication (-k). Requires either a password or a hash to be provided.
        :param db: Database to connect to.
        :param extra_args: Additional arguments.
        :param timeout: Max execution time in seconds. (e.g. -port, -dc-ip, etc.)
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await lateral_service.run_mssqlclient(
            domain=domain,
            target=target,
            username=username,
            password=password,
            commands=commands,
            windows_auth=windows_auth,
            hashes=hashes,
            aes_key=aes_key,
            use_kerberos=use_kerberos,
            db=db,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(tags={PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC})
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
    ) -> str:
        """
        Run Impacket's addcomputer.py to add a machine account to Active Directory.

        :param domain: Target domain (e.g., 'corp.local').
        :param computer_name: Name of the new computer (e.g., 'ATTACKBOX$'). Must end with a '$'.
        :param computer_password: Password for the new computer account.
        :param username: Username for authentication.
        :param password: Password for authentication.
        :param dc_ip: Domain controller IP.
        :param dc_hostname: Domain controller hostname. If omitted, the FQDN of the domain controller will be used.
        :param method: Method to use ('SAMR' or 'LDAPS').
        :param hashes: LM:NT hashes. The format is as follows: [LMhash]:NThash (the LM hash is optional, the NT hash must be prepended with a colon (:)).
        :param aes_key: AES key for Kerberos authentication (128 or 256 bits).
        :param use_kerberos: Use Kerberos authentication (-k). Requires either a password or a hash to be provided.
        :param extra_args: Additional arguments. (e.g. -no-add, -delete, etc.)
        :param timeout: Max execution time in seconds.
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await lateral_service.run_addcomputer(
            domain=domain,
            computer_name=computer_name,
            computer_password=computer_password,
            username=username,
            password=password,
            dc_ip=dc_ip,
            dc_hostname=dc_hostname,
            method=method,
            hashes=hashes,
            aes_key=aes_key,
            use_kerberos=use_kerberos,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(tags={PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC})
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
    ) -> str:
        """
        Run impacket's renameMachine.py to rename a machine account in Active Directory.

        :param domain: Target domain (e.g., 'corp.local').
        :param current_name: Current sAMAccountName of the object to edit (e.g., 'OLDNAME$').
        :param new_name: New sAMAccountName to set for the target object (e.g., 'NEWNAME$').
        :param username: Username for authentication.
        :param password: Password for authentication.
        :param dc_ip: Domain controller or KDC IP. If omitted it will use the domain part (FQDN) specified in the target parameter.
        :param hashes: LM:NT hashes. The format is as follows: [LMhash]:NThash (the LM hash is optional, the NT hash must be prepended with a colon (:)).
        :param use_kerberos: Use Kerberos authentication (-k). Requires either a password or a hash to be provided.
        :param extra_args: Additional arguments. (e.g. -use-ldaps, -aesKey ..., etc.)
        :param timeout: Max execution time in seconds.
        :return: Tool execution result.
        """
        result = await lateral_service.run_rename_machine(
            domain=domain,
            current_name=current_name,
            new_name=new_name,
            username=username,
            password=password,
            dc_ip=dc_ip,
            hashes=hashes,
            use_kerberos=use_kerberos,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(tags={PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC})
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
    ) -> str:
        """
        Run Certipy for Active Directory Certificate Services (AD CS) enumeration and abuse.

        Common actions:
            - 'find' : Enumerate AD CS configuration and vulnerable templates
            - 'req'  : Request a certificate
            - 'auth' : Authenticate using a certificate
            - 'relay': NTLM relay to AD CS (advanced usage)

        :param action: Certipy subcommand (e.g., 'find', 'req', 'auth').
        :param domain: Target domain (e.g., 'corp.local').
        :param username: Username for authentication.
        :param password: Password for authentication.
        :param target: DNS Name or IP Address of the target machine. Required for Kerberos or SSPI authentication.
        :param dc_ip: Domain controller IP. If omitted it will use the domain part (FQDN) specified in the target parameter.
        :param ca: Certificate Authority name (for req).
        :param template: Certificate template name.
        :param upn: UPN to request certificate for (e.g., admin@corp.local).
        :param use_kerberos: Use Kerberos authentication (-k). This option requires either a password or a hash to be provided.
        :param hashes: LM and/or NT hash to use for authentication. The format is as follows: [LMhash:]NThash (the LM hash is optional).
        :param extra_args: Additional certipy arguments. (e.g. -on-behalf-of ... or -save-old or -pfx ...)
        :param timeout: Max execution time in seconds.
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await lateral_service.run_certipy(
            action=action,
            domain=domain,
            username=username,
            password=password,
            target=target,
            dc_ip=dc_ip,
            ca=ca,
            template=template,
            upn=upn,
            use_kerberos=use_kerberos,
            hashes=hashes,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(tags={PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC})
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
    ) -> str:
        """
        Run krbrelayx's dnstool.py to manage AD-integrated DNS records.
        If adding records, record type to be added will only be 'A'.

        :param hostname: Hostname/ip or ldap://host:port connection string to connect to (e.g., 'host.corp.local').
        :param action: Action to perform.
        :param username: Domain\\username for authentication. (e.g., 'corp.local\\admin')
        :param password: Password or LM:NTLM hash for authentication.
        :param zone: DNS zone to search in (if different than the current domain).
        :param record: DNS record to target FQDN (e.g., 'user1.corp.local').
        :param record_data: Record value (e.g., IP address).
        :param use_kerberos: Use Kerberos authentication (-k).
        :param extra_args: Additional arguments. (e.g. -aesKey ..., -dc-ip ..., etc.)
        :param timeout: Max execution time in seconds.
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await lateral_service.run_dnstool(
            hostname=hostname,
            action=action,
            username=username,
            password=password,
            zone=zone,
            record=record,
            record_data=record_data,
            use_kerberos=use_kerberos,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(tags={PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC})
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
    ) -> str:
        """
        Run krbrelayx's addspn.py to manage Service Principal Names.
        Actions:
        - add: Add an SPN to an account
        - remove: Remove an SPN from an account
        - clear: Clear all SPNs from an account
        - query: Query SPNs for an account

        :param hostname: Hostname or LDAP connection string to connect to (e.g., 'host.corp.local' or 'ldap://host:port').
        :param username: Domain\\username for authentication. (e.g., 'corp.local\\admin').
        :param password: Password or LM:NTLM hash for authentication.
        :param action: SPN action ('add', 'remove', 'clear', 'query').
        :param spn: SPN value (e.g., 'cifs/server.corp.local').
        :param target: Computername or username to target (FQDN or COMPUTER$ name, if unspecified user with 'username' is target).
        :param target_type: Type of the target (hostname or samname). If unspecified, will assume it's a hostname if there is a . in the name and a SAM name otherwise.
        :param use_kerberos: Use Kerberos authentication. Requires either a password or a hash to be provided.
        :param dc_ip: Domain controller IP. If omitted it will use the domain part (FQDN) specified in the target parameter.
        :param extra_args: Additional arguments. (e.g. -a, -aesKey ..., etc.)
        :param timeout: Max execution time in seconds.
        :return: Tool execution result.
        """
        result = await lateral_service.run_addspn(
            hostname=hostname,
            username=username,
            password=password,
            action=action,
            spn=spn,
            target=target,
            target_type=target_type,
            use_kerberos=use_kerberos,
            dc_ip=dc_ip,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    

    
