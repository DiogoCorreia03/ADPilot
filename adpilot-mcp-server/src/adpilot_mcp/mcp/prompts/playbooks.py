from fastmcp import FastMCP
from adpilot_mcp.models.phases import PentestPhase


def register(mcp: FastMCP) -> None:
    @mcp.prompt()
    def ad_phase_playbook(phase: str) -> str:
        """
        Provides standardized Active Directory pentesting methodology and tool recommendations
        for the given phase (e.g. external_reconnaissance, initial_access, internal_reconnaissance,
        lateral_movement_and_privilege_escalation, check_results).
        """
        playbooks = {
            PentestPhase.EXTERNAL_RECONNAISSANCE.value: (
                "## External Reconnaissance Playbook\n"
                "1. Map network perimeters with `run_nmap_scan` (focus on SMB 445, LDAP 389/636, Kerberos 88, DNS 53, HTTP 80/443).\n"
                "2. Perform DNS enumeration with `run_nslookup` looking for SRV records (`_ldap._tcp.dc._msdcs.<domain>`).\n"
                "3. Enumerate valid user accounts anonymously or via Kerberos with `run_kerbrute` (userenum mode)."
            ),
            PentestPhase.INITIAL_ACCESS.value: (
                "## Initial Access Playbook\n"
                "1. Test for AS-REP Roasting using `run_getnpusers` without pre-auth or with enumerated user list.\n"
                "2. Test Kerberoasting with `run_getuserspns` if domain credentials are discovered.\n"
                "3. Perform password spraying with `run_kerbrute` (passwordspray mode, observe lockout policies).\n"
                "4. Crack obtained hashes using `run_hashcat`."
            ),
            PentestPhase.INTERNAL_RECONNAISSANCE.value: (
                "## Internal Reconnaissance Playbook\n"
                "1. Perform full directory dump with `run_ldap_dump` or targeted queries via `run_ldapsearch`.\n"
                "2. Enumerate domain users and groups with `run_getadusers`.\n"
                "3. Check for unconstrained and constrained delegation with `run_finddelegation`.\n"
                "4. Enumerate domain SIDs with `run_lookupsid`.\n"
                "5. Run BloodHound collection via `bloodhound_collect`."
            ),
            PentestPhase.LATERAL_MOVEMENT_AND_PRIV_ESC.value: (
                "## Lateral Movement & Privilege Escalation Playbook\n"
                "1. If local admin or high privileges are gained, dump credentials with `run_secretsdump`.\n"
                "2. Execute commands remotely via `run_wmiexec`, `run_psexec`, or `run_mssqlclient`.\n"
                "3. Inspect and abuse AD CS (Certificate Services) with `run_certipy`.\n"
                "4. Abuse constrained delegation via `run_getst` and Kerberos tickets.\n"
                "5. Check for relay opportunities with `run_printerbug`, `run_ntlmrelayx`, or `run_krbrelayx`."
            ),
            PentestPhase.CHECK_RESULTS.value: (
                "## Check Results Playbook\n"
                "1. Review captured credentials with `credentials_get`.\n"
                "2. Retrieve user flag artifacts using `get_user_flag`.\n"
                "3. Ensure all newly captured credentials are saved with `credentials_add`."
            ),
            PentestPhase.SHELL_ONLY.value: (
                "## Shell Only Playbook\n"
                "1. Execute arbitrary shell commands and scripts directly using `shell_exec`.\n"
                "2. Use standard command-line tools installed in the environment."
            ),
            PentestPhase.SHELL_EXEC.value: (
                "## Shell Only Playbook\n"
                "1. Execute arbitrary shell commands and scripts directly using `shell_exec`.\n"
                "2. Use standard command-line tools installed in the environment."
            ),
        }

        return playbooks.get(
            phase,
            f"Active Directory Pentest Playbook for phase '{phase}': Follow standard PTES and WAD methodology.",
        )
