The penetration test on the Windows Active Directory domain `polaris.local` (Domain Controller: `192.168.122.10`) was conducted to identify vulnerabilities and potential paths for domain compromise.

### Summary of Findings
1.  **Reconnaissance & User Enumeration:** Initial reconnaissance revealed an Active Directory environment with SMB signing disabled and null authentication enabled. Several valid usernames were enumerated, including `skyler.white`, `jesse.pinkman`, `hank.schrader`, `walter.white`, and `saul.goodman`.
2.  **Credential Harvesting:** Through targeted password spraying and offline cracking of captured TGS tickets, the following credentials were confirmed:
    *   `skyler.white:Password123`
    *   `hank.schrader:sHyangja210`
    *   `jesse.pinkman:Wang0Tang0!`
    *   `walter.white:Metho1o590oA$elry`
3.  **Vulnerabilities & Attack Paths:**
    *   **SMB Misconfigurations:** SMBv1 is enabled and null authentication is allowed, facilitating reconnaissance.
    *   **Kerberoasting:** Valid TGS tickets for `saul.goodman`, `jesse.pinkman`, and `walter.white` were obtained and attempted to be cracked.
    *   **AD CS (ESC1):** The AD Certificate Services configuration is vulnerable to ESC1, as the `ESC1` certificate template allows for subject name specification by the enrollee, which could theoretically allow for privilege escalation. However, exploitation was hindered by RPC communication issues.
    *   **MSSQL Misconfiguration:** An MSSQL server (`CAPTAIN\SQLEXPRESS`) is running, but access was restricted for the compromised accounts.
4.  **Lateral Movement & Privilege Escalation:** While low-privilege access was achieved, attempts to perform DCSync (`secretsdump.py`) or remote code execution via WMI/WinRM failed due to insufficient privileges or restricted access.

### Recommendations
*   **Disable SMBv1:** Immediately disable SMBv1 across the network.
*   **Enforce SMB Signing:** Configure SMB signing to prevent relay attacks.
*   **Rotate Credentials:** Immediately rotate all passwords for compromised accounts (`skyler.white`, `hank.schrader`, `jesse.pinkman`, `walter.white`).
*   **Harden AD CS:** Review and modify the `ESC1` template (and other vulnerable templates like `ESC2`, `ESC3`, `ESC4`) to remove dangerous permissions, enforce manager approval, and restrict who can enroll. Disable web enrollment if not required.
*   **Restrict Administrative Access:** Limit the use of privileged accounts and ensure accounts have only the necessary permissions for their roles. Review group memberships, specifically for the `Masters` group, to ensure least-privilege principles are followed.
*   **Patching:** Ensure all systems are fully patched and security baseline configurations (e.g., CIS benchmarks) are implemented.