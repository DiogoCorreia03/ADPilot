The assessment of the `polaris.local` network (DC at `192.168.122.10`) has been conducted.

### Summary of Findings & Compromise
*   **Initial Access:** Achieved by password spraying the domain using `kerbrute` and a list of common passwords against validated domain usernames (`skyler.white` and `saul.goodman`).
*   **Compromised Accounts:** 
    *   `skyler.white` (Password: `Password123`)
    *   `saul.goodman` (Password: `beTTer2caLL2me`)
    *   `jesse.pinkman` (Kerberoasted hash cracked to: `Wang0Tang0!`)
*   **Vulnerabilities:**
    *   **Kerberoasting:** Recovered hashes for multiple accounts enabled offline cracking.
    *   **AD CS (ESC1):** Vulnerable template discovered. However, exploitation via RPC was blocked by network-level/endpoint restrictions (`rpc_s_access_denied`).
    *   **Weak Credentials:** Multiple user accounts utilized weak, easily crackable passwords.
    *   **MSSQL:** SQL Server 2019 is running on the Domain Controller.

### Attack Path
1.  **Reconnaissance:** Identified domain `polaris.local` and DC `192.168.122.10`.
2.  **User Enumeration:** Discovered valid accounts using `kerbrute`.
3.  **Initial Access:** Sprayed `Password123` against discovered accounts, gaining `skyler.white`.
4.  **Enumeration:** Dumped domain data, identified SPNs for Kerberoasting.
5.  **Lateral Movement:** Kerberoasted `jesse.pinkman`, cracked password (`Wang0Tang0!`), and authenticated successfully.
6.  **Failed Escalation:** Attempted `secretsdump` for DCSync (RPC/DRSUAPI access denied) and AD CS abuse (RPC access denied to Certificate Authority endpoints).

### Recommendations
1.  **Immediate Credential Rotation:** Rotate passwords for all domain users, especially `saul.goodman`, `skyler.white`, and `jesse.pinkman`, enforcing strong password complexity policies.
2.  **Disable Vulnerable Services/AD CS:** Disable or secure vulnerable certificate templates (ESC1).
3.  **Restrict Administrative Access:** Limit permissions for non-administrative users to modify AD object properties and interact with sensitive services (like MSSQL/AD CS).
4.  **Strengthen Kerberos:** Implement hardened policies against Kerberoasting and enforce Account Lockout policies.
5.  **Audit SMB/MSSQL:** Disable SMBv1 and enforce SMB signing; audit and restrict access to SQL Server instances on domain-critical systems.