from typing import Literal
from fastmcp import FastMCP
from adpilot_mcp.models.phases import PentestPhase
from adpilot_mcp.services import kerberos as kerberos_service


def register(mcp: FastMCP) -> None:
    @mcp.tool(tags={PentestPhase.INITIAL_ACCESS, PentestPhase.INTERNAL_RECONNAISSANCE})
    async def run_getnpusers(
        domain: str,
        username: str | None = None,
        password: str | None = None,
        usersfile: str | None = None,
        dc_ip: str | None = None,
        extra_args: str | None = None,
        timeout: int = 120,
    ) -> str:
        """
        Run Impacket's GetNPUsers.py to list and get TGTs for users vulnerable to AS-REP roasting (that have pre-authentication disabled).
        For those users with such configuration, an output file will be generated so you can send it for cracking.
        If 'usersfile' is omitted, the script will automatically attempt to identify user accounts with pre-authentication disabled via LDAP using the provided credentials. If no 'usersfile' and credentials are provided, it will attempt to retrieve users through an RPC null session.

        :param domain: Target domain (e.g., 'corp.local').
        :param username: Username for authenticated bind (optional).
        :param password: Password for authentication (optional).
        :param usersfile: Path to file containing a list of usernames to test (optional). One username per line must be specified (just the username, no domain needed).
        :param dc_ip: Domain controller IP address (recommended). If omitted, the positional argument's domain part will be used (in that case, it must be a Fully-Qualified-Domain-Name (FQDN)).
        :param extra_args: Additional arguments for GetNPUsers.py.
        :param timeout: Max execution time in seconds.
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await kerberos_service.run_getnpusers(
            domain=domain,
            username=username,
            password=password,
            usersfile=usersfile,
            dc_ip=dc_ip,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(tags={PentestPhase.INITIAL_ACCESS, PentestPhase.INTERNAL_RECONNAISSANCE})
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
    ) -> str:
        """
        Run Impacket's GetUserSPNs.py to enumerate service accounts that have an SPN and obtain their password hash to perform Kerberoasting.
        The obtained password hashes will be saved to a provided output file.

        :param domain: Target domain (e.g., 'corp.local').
        :param username: Username for authentication.
        :param password: Password for authentication.
        :param dc_ip: Domain controller IP address. If omitted, the positional argument's domain part will be used (in that case, it must be a Fully-Qualified-Domain-Name (FQDN)).
        :param no_preauth: Option to indicate that the user with 'username' is vulnerable to AS-REP roasting and the Kerberoast attack should be performed without pre-authentication.
        :param use_kerberos: Use Kerberos authentication (-k). This option requires either a password or a hash to be provided.
        :param hash_: LM and/or NT hash to use for authentication. The format is as follows: [LMhash]:NThash (the LM hash is optional, the NT hash must be prepended with a colon (:)
        :param extra_args: Additional arguments for GetUserSPNs.py.
        :param timeout: Max execution time in seconds.
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await kerberos_service.run_getuserspns(
            domain=domain,
            username=username,
            password=password,
            dc_ip=dc_ip,
            no_preauth=no_preauth,
            use_kerberos=use_kerberos,
            hash_=hash_,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(
        tags={
            PentestPhase.EXTERNAL_RECONNAISSANCE,
            PentestPhase.INITIAL_ACCESS,
            PentestPhase.INTERNAL_RECONNAISSANCE,
            PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC,
        }
    )
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
    ) -> str:
        """
        Run kerbrute for Kerberos-based user enumeration and password spraying.
        Modes:
            - 'userenum'     : Enumerate valid usernames. This does not cause any login failures so it will not lock out any accounts.
            - 'passwordspray': Spray a single password against many users. This will increment the failed login count and lock out accounts if used excessively.
            - 'bruteforce'   : Bruteforce passwords for users. This will increment the failed login count and lock out accounts if used excessively.

        :param domain: Target domain (e.g., 'corp.local').
        :param dc_ip: Domain controller IP address. If blank, will lookup via DNS.
        :param mode: Kerbrute mode ('userenum', 'passwordspray', 'bruteforce').
        :param usersfile: Path to file containing usernames.
        :param bruteforcefile: Path to file containing username and password combinations (for bruteforce) in the format 'username:password'.
        :param password: Single password (for passwordspray).
        :param safe: Enable safe mode (avoid account lockouts). When this option is enabled, if an account comes back as locked out, it will abort all threads to stop locking out any other accounts. Default: False.
        :param extra_args: Additional kerbrute arguments.
        :param timeout: Max execution time in seconds. Default: 300 seconds.
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await kerberos_service.run_kerbrute(
            domain=domain,
            dc_ip=dc_ip,
            mode=mode,
            usersfile=usersfile,
            bruteforcefile=bruteforcefile,
            password=password,
            safe=safe,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(tags={PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC})
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
    ) -> str:
        """
        Run Impacket's getTGT.py to request a Kerberos Ticket Granting Ticket (TGT).

        :param domain: Target domain (e.g., 'corp.local').
        :param username: Username for authentication.
        :param password: Password for authentication.
        :param dc_ip: Domain controller IP.
        :param hashes: LM:NT hashes. The format is as follows: [LMhash]:NThash (the LM hash is optional, the NT hash must be prepended with a colon (:)).
        :param aes_key: AES key for Kerberos authentication (128 or 256 bits).
        :param use_kerberos: Use Kerberos authentication (-k). Requires either a password or a hash to be provided.
        :param extra_args: Additional arguments.
        :param timeout: Max execution time in seconds.
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await kerberos_service.run_gettgt(
            domain=domain,
            username=username,
            password=password,
            dc_ip=dc_ip,
            hashes=hashes,
            aes_key=aes_key,
            use_kerberos=use_kerberos,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(tags={PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC})
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
    ) -> str:
        """
        Run Impacket's getST.py to request Kerberos service tickets (TGS), including S4U-based impersonation (constrained delegation abuse).

        :param domain: Target domain (e.g., 'corp.local').
        :param username: Username for authentication.
        :param password: Password for authentication.
        :param spn: Service Principal Name (e.g., 'cifs/server.corp.local').
        :param impersonate: User to impersonate (S4U2Self / S4U2Proxy / Administrator).
        :param dc_ip: Domain controller IP address.
        :param hashes: LM:NT hashes. The format is as follows: [LMhash]:NThash (the LM hash is optional, the NT hash must be prepended with a colon (:)).
        :param aes_key: AES key for Kerberos auth.
        :param use_kerberos: Use Kerberos authentication (-k). Requires either a password or a hash to be provided.
        :param extra_args: Additional arguments.
        :param timeout: Max execution time in seconds.
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await kerberos_service.run_getst(
            domain=domain,
            username=username,
            password=password,
            spn=spn,
            impersonate=impersonate,
            dc_ip=dc_ip,
            hashes=hashes,
            aes_key=aes_key,
            use_kerberos=use_kerberos,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(tags={PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC})
    async def run_ticketer(
        domain: str,
        username: str,
        domain_sid: str,
        nthash: str | None = None,
        aes_key: str | None = None,
        extra_args: str | None = None,
        timeout: int = 120,
    ) -> str:
        """
        Run Impacket's ticketer.py to forge Kerberos tickets (Golden/Silver).

        :param domain: Target Fully Qualified Domain Name (e.g., 'corp.local').
        :param username: Username to impersonate.
        :param domain_sid: Domain SID of the target domain the ticker will be generated for.
        :param nthash: NT hash used for signing the ticket (KRBTGT for golden, service account for silver).
        :param aes_key: AES key used for signing the ticket (128 or 256 bits) (alternative to NT hash).
        :param extra_args: Additional arguments (e.g. -groups ..., -spn ..., -duration ..., -extra-sid ..., etc.).
        :param timeout: Max execution time.
        :return: Tool execution result.
        """
        result = await kerberos_service.run_ticketer(
            domain=domain,
            username=username,
            domain_sid=domain_sid,
            nthash=nthash,
            aes_key=aes_key,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(
        tags={PentestPhase.INITIAL_ACCESS, PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC}
    )
    async def run_hashcat(
        hash_file: str,
        hash_mode: int,
        outputfile: str,
        attack_mode: int = 0,
        wordlist: str | None = None,
        mask: str | None = None,
        extra_args: str | None = None,
        timeout: int = 600,
    ) -> str:
        """
        Run hashcat for password cracking.

        :param hash_file: File containing hashes.
        :param hash_mode: Hash type (-m), e.g. 18200 (AS-REP), 13100 (Kerberoast).
        :param attack_mode: Attack mode (-a), e.g. 0 (straight), 3 (mask).
        :param wordlist: Path to wordlist file (for -a 0).
        :param mask: Mask string (for -a 3), e.g. '?l?l?l?l?d?d'.
        :param outputfile: Output file for cracked hashes.
        :param extra_args: Additional hashcat arguments.
        :param timeout: Max execution time in seconds.
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await kerberos_service.run_hashcat(
            hash_file=hash_file,
            hash_mode=hash_mode,
            outputfile=outputfile,
            attack_mode=attack_mode,
            wordlist=wordlist,
            mask=mask,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()
