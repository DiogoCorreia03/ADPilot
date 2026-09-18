from typing import Literal
from fastmcp import FastMCP
from adpilot_mcp.models.phases import PentestPhase
from adpilot_mcp.services import ad_enum as ad_service


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        tags={
            PentestPhase.EXTERNAL_RECONNAISSANCE,
            PentestPhase.INITIAL_ACCESS,
            PentestPhase.INTERNAL_RECONNAISSANCE,
            PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC,
        }
    )
    async def run_smbclient(
        target: str,
        service: str,
        username: str = "guest",
        password: str | None = None,
        command: str | None = "ls",
        extra_args: str | None = None,
        timeout: int = 120,
    ) -> str:
        """
        Run smbclient to connect to an SMB/CIFS server and optionally execute commands.
        Operations include things like getting files from the server to the local machine, putting files from the local machine to the server, retrieving directory information from the server and so on.

        :param target: The target IP address or NetBIOS name.
        :param service: The name of the SMB service to connect to (e.g. the name of a share or a printer).
        :param username: The username for authentication. If not provided, defaults to "guest".
        :param password: The password required to access the specified service on the specified server. If not provided, no password will be used ('-N' for anonymous access). If empty string "", forces an empty password via 'user%'. If a string is provided, uses that password.
        :param command: Semicolon-separated list of commands to be executed.
        :param extra_args: Additional arguments for smbclient (e.g. '-p 139').
        :param timeout: Maximum time in seconds that the command is allowed to run for (default is 120 seconds).
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await ad_service.run_smbclient(
            target=target,
            service=service,
            username=username,
            password=password,
            command=command,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(tags={PentestPhase.INTERNAL_RECONNAISSANCE})
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
    ) -> str:
        """
        Run ldapsearch against an LDAP server to enumerate directory data.

        :param target: The target IP address or hostname.
        :param base_dn: The base DN to search (e.g., 'DC=example,DC=com').
        :param search_filter: LDAP search filter to apply (default: '(objectClass=*)').
        :param attributes: Space-separated list of attributes to retrieve (e.g., 'cn mail memberOf').
        :param bind_dn: Bind DN for authentication (e.g., 'user@example.com' or 'CN=user,...'). If not provided, anonymous bind is attempted.
        :param password: Password for authentication. If not provided and bind_dn is set, will prompt-less fail.
        :param use_ssl: Whether to use LDAPS (True uses ldaps://).
        :param port: Optional port override (e.g., 389 or 636).
        :param extra_args: Additional arguments for ldapsearch.
        :param timeout: Maximum execution time in seconds.
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await ad_service.run_ldapsearch(
            target=target,
            base_dn=base_dn,
            search_filter=search_filter,
            attributes=attributes,
            bind_dn=bind_dn,
            password=password,
            use_ssl=use_ssl,
            port=port,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(tags={PentestPhase.INTERNAL_RECONNAISSANCE})
    async def run_ldap_dump(
        hostname: str,
        domain: str | None = None,
        username: str | None = None,
        password: str | None = None,
        timeout: int = 300,
    ) -> str:
        """
        Run ldapdomaindump against a domain controller with provided credentials.
        Domain information dumper via LDAP. Dumps users/computers/groups and
        OS/membership information to JSON output.
        If either domain, username or password is not provided, it will attempt an anonymous dump (which may yield limited results depending on DC configuration).

        :param hostname: Hostname/ip or ldap://host:port connection string to connect to (use ldaps:// to use SSL)
        :param domain: The target domain name (e.g. corp.local).
        :param username: The username for authentication.
        :param password: The password for authentication.
        :param timeout: Maximum time in seconds that the command is allowed to run for (default is 300 seconds).
        :return: stdout, stderr, returncode, and output_dir containing dumped data.
        """
        result = await ad_service.run_ldap_dump(
            hostname=hostname,
            domain=domain,
            username=username,
            password=password,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(
        tags={
            PentestPhase.EXTERNAL_RECONNAISSANCE,
            PentestPhase.INTERNAL_RECONNAISSANCE,
            PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC,
        }
    )
    async def run_netexec(
        protocol: Literal[
            "smb", "ldap", "ssh", "ftp", "wmi", "winrm", "rdp", "vnc", "mssql", "nfs"
        ],
        target: str,
        username: str = "",
        password: str = "",
        extra_args: str | None = None,
        timeout: int = 120,
    ) -> str:
        """
        Run a netexec (nxc) command.

        :param protocol: The protocol to use for execution (e.g. smb, ldap). To view a protocols options, run: 'nxc <protocol> --help'
        :param target: The target IP address, hostname, CIDR, IP range or file containing a list of targets.
        :param username: Optional username for authentication.
        :param password: Optional password for authentication.
        :param extra_args: Additional command-line arguments to pass to nxc (e.g. '--shares' when enumerating shares through SMB).
        :param timeout: Maximum time in seconds that the command is allowed to run for (default is 120 seconds).
        :return: A dictionary containing stdout, stderr, returncode.
        """
        result = await ad_service.run_netexec(
            protocol=protocol,
            target=target,
            username=username,
            password=password,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(tags={PentestPhase.INTERNAL_RECONNAISSANCE})
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
    ) -> str:
        """
        Run Impacket's GetADUsers.py to enumerate Active Directory users and attributes.

        :param domain: Target domain (e.g., 'corp.local').
        :param username: Username for authentication.
        :param password: Password for authentication.
        :param dc_ip: Domain controller IP address. If omitted, the positional argument's domain part will be used (in that case, it must be a Fully-Qualified-Domain-Name (FQDN)).
        :param dc_hostname: Domain controller hostname. If omitted, the FQDN of the domain controller will be used.
        :param use_kerberos: Use Kerberos authentication (-k). This option requires either a password or a hash to be provided.
        :param hash_: LM and/or NT hash to use for authentication. The format is as follows: [LMhash]:NThash (the LM hash is optional, the NT hash must be prepended with a colon (:)
        :param all_users: Retrieve all users (default True, uses -all), including those with no email addresses and disabled accounts.
        :param extra_args: Additional arguments for GetADUsers.py. (e.g. -aesKey 'hex key')
        :param timeout: Max execution time in seconds.
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await ad_service.run_getadusers(
            domain=domain,
            username=username,
            password=password,
            dc_ip=dc_ip,
            dc_hostname=dc_hostname,
            use_kerberos=use_kerberos,
            hash_=hash_,
            all_users=all_users,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(
        tags={
            PentestPhase.INTERNAL_RECONNAISSANCE,
            PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC,
        }
    )
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
    ) -> str:
        """
        Run Impacket's findDelegation.py to enumerate delegation settings in Active Directory.

        :param domain: Target domain (e.g., 'corp.local').
        :param username: Username for authentication.
        :param password: Password for authentication.
        :param dc_ip: Domain controller IP address.
        :param target_domain: Domain to query/request if different than the domain of the user. Allows for retrieving delegation info across trusts. (e.g., 'it.corp.local').
        :param hashes: LM:NT hashes. The format is as follows: [LMhash]:NThash (the LM hash is optional, the NT hash must be prepended with a colon (:)).
        :param aes_key: AES key for Kerberos authentication.
        :param use_kerberos: Use Kerberos authentication (-k). Requires either a password or a hash to be provided.
        :param extra_args: Additional arguments.
        :param timeout: Max execution time in seconds.
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await ad_service.run_finddelegation(
            domain=domain,
            username=username,
            password=password,
            target_domain=target_domain,
            dc_ip=dc_ip,
            hashes=hashes,
            aes_key=aes_key,
            use_kerberos=use_kerberos,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(
        tags={
            PentestPhase.INTERNAL_RECONNAISSANCE,
            PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC,
        }
    )
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
    ) -> str:
        """
        Run Impacket's lookupsid.py to enumerate SIDs and associated account names.

        :param domain: Target domain (e.g., 'corp.local').
        :param target: Target hostname or IP (targetName or address).
        :param username: Username for authentication.
        :param password: Password for authentication.
        :param max_rid: Maximum RID to check (default is 4000).
        :param dc_ip: Domain controller IP.
        :param hashes: LM:NT hashes. The format is as follows: [LMhash]:NThash (the LM hash is optional, the NT hash must be prepended with a colon (:)).
        :param use_kerberos: Use Kerberos authentication (-k). Requires either a password or a hash to be provided.
        :param domain_sids: Enumerate Domain SIDs (will likely forward requests to the DC). Default: False.
        :param extra_args: Additional arguments.
        :param timeout: Max execution time in seconds.
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await ad_service.run_lookupsid(
            domain=domain,
            target=target,
            username=username,
            password=password,
            max_rid=max_rid,
            dc_ip=dc_ip,
            hashes=hashes,
            use_kerberos=use_kerberos,
            domain_sids=domain_sids,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

