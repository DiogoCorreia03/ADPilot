# Executive Summary

This penetration testing assessment evaluated the security posture of the `polaris.local` Active Directory environment. The primary objective was to identify vulnerabilities and assess the potential for unauthorized access and privilege escalation. 

The assessment resulted in a full compromise of the domain. Attackers successfully enumerated valid domain users, performed credential spraying to gain initial access, exploited MSSQL services for remote command execution, and ultimately dumped the NTDS.dit file from the Domain Controller to achieve full domain dominance. Two hosts were targeted, both of which were successfully compromised.

# Attack Path Summary

1.  **Initial Access:** Valid user accounts were identified via `kerbrute` user enumeration. A password spray attack successfully yielded credentials for multiple accounts, including `Administrator` and several standard users.
2.  **Service Exploitation:** Using the compromised `Administrator` credentials, the MSSQL service on `192.168.122.10` was accessed. The `xp_cmdshell` feature was enabled, allowing for remote command execution under the context of `nt service\mssql$sqlexpress`.
3.  **Privilege Escalation & Domain Dominance:** Utilizing the `Administrator` credentials, `wmiexec` was used to establish a session as `NT AUTHORITY\SYSTEM` on the Domain Controller. Finally, `secretsdump.py` was executed to extract the `NTDS.dit` database, resulting in the compromise of all domain account hashes.

# Credentials Obtained

| Username | Password | Source Host | Acquisition Method |
| :--- | :--- | :--- | :--- |
| Administrator | Passw0rd | 192.168.122.10 | Password Spray |
| skyler.white | Password123 | 192.168.122.10 | Password Spray |
| jesse.pinkman | Wang0Tang0! | 192.168.122.10 | Password Spray/Kerberoasting |
| walter.white | Metho1o590oA$elry | 192.168.122.10 | Password Spray/Kerberoasting |
| hank.schrader | sHyangja210 | 192.168.122.10 | Password Spray |

# Compromised Systems

*   **CAPTAIN (192.168.122.10):** Domain Controller. Full system compromise achieved via `wmiexec` using `Administrator` credentials. `NTDS.dit` extracted.
*   **MEMBER (192.168.122.5):** Identified as an internal domain member. Successfully accessed/scanned during initial enumeration.

# Findings

### Weak Password Policy / Credential Spraying
*   **Evidence:** `kerbrute` password spray identified five valid account/password combinations.
*   **Affected Systems:** Domain-wide.
*   **Description:** The domain environment lacks lockout protections or complexity enforcement sufficient to prevent successful password spraying against known usernames.

### Excessive MSSQL Privileges
*   **Evidence:** `Administrator` account retained `sysadmin` role on the MSSQL instance, allowing the enabling of `xp_cmdshell`.
*   **Affected Systems:** 192.168.122.10
*   **Description:** The ability to enable administrative MSSQL features from a standard domain account facilitated remote code execution.

# Vulnerabilities Demonstrated

*   **Insecure MSSQL Configuration:** `xp_cmdshell` enabled via `sysadmin` privileges leading to remote code execution.
*   **Kerberoasting:** Accounts `jesse.pinkman`, `walter.white`, and `saul.goodman` were identified as having Service Principal Names (SPNs) susceptible to ticket extraction and offline cracking.
*   **AD CS Misconfigurations:** `ESC1-ESC4` and `ESC8` templates were identified on the domain, indicating significant certificate authority vulnerabilities.

# Authentication & Identity Findings

*   **User Enumeration:** Null session enumeration via `lookupsid.py` successfully retrieved a full list of domain accounts.
*   **Service Accounts:** Multiple accounts were identified as Kerberoastable, allowing for password recovery via offline cracking.

# Lateral Movement

*   **Remote Execution:** Used `wmiexec` with `Administrator` credentials to gain a shell on the Domain Controller.
*   **MSSQL Execution:** Used `mssqlclient` to enable and execute `xp_cmdshell` on the target database server.

# Privilege Escalation

*   **Starting Privilege:** Domain User (via password spray)
*   **Ending Privilege:** `NT AUTHORITY\SYSTEM` (Domain Admin/Full Control)
*   **Technique:** Use of high-privileged service account credentials (`Administrator`) to execute commands via WMI.

# Domain Compromise

Full domain compromise was achieved by extracting the `NTDS.dit` file using `secretsdump.py`. This granted access to all domain hashes, including the `krbtgt` account, providing persistent and total control over the `polaris.local` domain.

# Failed Attack Paths

*   **Anonymous LDAP Enumeration:** Disabled by security configuration.
*   **Certipy ESC1 Exploitation:** Failed due to RPC communication issues between the test host and the CA.

# Timeline of Compromise

1.  **Enumeration:** Performed `kerbrute` and `lookupsid` to map domain users.
2.  **Access:** Performed password spray to obtain valid credentials.
3.  **Analysis:** Identified AD CS vulnerabilities and Kerberoastable accounts using valid credentials.
4.  **Database Access:** Connected to MSSQL as `Administrator`.
5.  **Execution:** Enabled `xp_cmdshell` to confirm remote execution capability.
6.  **Full Compromise:** Gained SYSTEM shell via WMI and extracted domain secrets via `secretsdump`.

# Assessment Statistics

*   Hosts Discovered: 2
*   Hosts Compromised: 2
*   Accounts Compromised: 5
*   Privilege Escalations: 1
*   Failed Attack Paths: 2

# Recommendations

1.  **Enforce Strong Password Policies:** Implement complexity requirements and account lockout policies to thwart spraying attacks.
2.  **Audit MSSQL Permissions:** Remove `sysadmin` privileges from non-essential accounts and disable `xp_cmdshell` globally.
3.  **Harden AD CS:** Review and remediate identified `ESC` template misconfigurations.
4.  **Disable Null Sessions:** Restrict anonymous LDAP/SMB enumeration to prevent information leakage.
5.  **Rotate Compromised Credentials:** Immediately reset passwords for all accounts identified in this report.