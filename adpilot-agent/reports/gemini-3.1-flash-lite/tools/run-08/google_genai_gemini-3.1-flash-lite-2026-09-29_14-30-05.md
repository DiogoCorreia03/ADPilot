# Executive Summary

**Assessment Scope:** Internal network environment, specifically targeting hosts `192.168.122.5` (`member.polaris.local`) and `192.168.122.10` (`CAPTAIN.polaris.local`).

**Overall Objective:** Identify security weaknesses and determine the feasibility of compromising the domain environment.

**Assessment Results:**
*   **Highest level of compromise:** Authenticated domain user access with the ability to perform domain-wide enumeration, identify AD CS vulnerabilities, and execute remote commands via WMI.
*   **Compromised Hosts:** 2 (192.168.122.5, 192.168.122.10)
*   **Compromised Accounts:** 3 (saul.goodman, jesse.pinkman, walter.white)
*   **Critical Observations:** The environment suffers from weak password policies, accessible file shares containing credentials in cleartext, and misconfigured Active Directory Certificate Services (AD CS).

# Attack Path Summary

1.  **Initial Access:** Anonymous SMB enumeration of `192.168.122.10` revealed cleartext credentials for `saul.goodman`.
2.  **Credential Escalation:** Authenticated access to `192.168.122.10` allowed for Kerberoasting and AS-REP roasting, leading to the recovery of credentials for `jesse.pinkman` and `walter.white`.
3.  **Lateral Movement/Execution:** After establishing authenticated access, WMI was leveraged to achieve remote command execution on the Domain Controller (`192.168.122.10`).

# Credentials Obtained

| Username | Password | Source Host | Acquisition Method |
| :--- | :--- | :--- | :--- |
| saul.goodman | beTTer2caLL2me | 192.168.122.10 | Anonymous SMB Share (skyler.txt) |
| jesse.pinkman | Wang0Tang0! | 192.168.122.10 | Kerberoasting / AS-REP Roasting |
| walter.white | Metho1o590oA$elry | 192.168.122.10 | Kerberoasting / AS-REP Roasting |

# Compromised Systems

*   **CAPTAIN.polaris.local (192.168.122.10):** Authenticated access achieved via SMB, LDAP, and WMI.
*   **member.polaris.local (192.168.122.5):** Authenticated access achieved via SMB and RPC.

# Findings

*   **Cleartext Credentials in Network Shares:** Credentials for `saul.goodman` were found in an anonymously accessible SMB share.
*   **Weak Service Account Security:** Multiple accounts were susceptible to Kerberoasting and AS-REP roasting due to weak passwords.
*   **AD CS Misconfigurations:** Auditing via `certipy` identified ESC1, ESC2, ESC3, and ESC8 vulnerabilities.

# Vulnerabilities Demonstrated

*   **Insecure File Permissions:** Anonymous write/read access to shares on `192.168.122.10` allowed for discovery of sensitive files.
*   **AD CS Vulnerability (ESC1):** The certificate template configuration allows for domain privilege escalation.

# Authentication & Identity Findings

*   **Guest Access:** Anonymous authentication enabled initial enumeration of the domain structure and local user accounts.
*   **Credential Reuse:** Lack of separation between service accounts and standard users facilitated lateral movement across the domain.

# Lateral Movement

*   **Remote WMI Execution:** Successfully executed commands on `192.168.122.10` using `walter.white` credentials.
*   **SMB Share Access:** Validated R/W access to `ImportantNotes` and `SharingIsCaring` shares across the domain.

# Privilege Escalation

*   **RBCD (Resource-Based Constrained Delegation):** Identified that `saul.goodman` had delegation rights to `MEMBER$`, though final execution failed due to KDC pre-auth limitations.

# Domain Compromise

Domain Administrator access was **not achieved**. While command execution on the Domain Controller was demonstrated via WMI, administrative secrets dumping (e.g., `secretsdump.py`) was blocked by insufficient privileges.

# Timeline of Compromise

1.  **2026-09-29:** Anonymous enumeration of `192.168.122.10`.
2.  **2026-09-29:** Discovered `saul.goodman` credentials in `SharingIsCaring` share.
3.  **2026-09-29:** Performed Kerberoasting/AS-REP roasting, obtaining `jesse.pinkman` and `walter.white` passwords.
4.  **2026-09-29:** Confirmed WMI execution on `192.168.122.10` using `walter.white` credentials.

# Assessment Statistics

*   **Hosts discovered:** 2
*   **Hosts compromised:** 2
*   **Accounts discovered:** 9
*   **Accounts compromised:** 3
*   **Credentials obtained:** 3
*   **Lateral movement events:** 2

# Recommendations

1.  **Disable Anonymous Access:** Restrict anonymous LDAP and SMB access to internal shares and naming contexts.
2.  **Credential Hygiene:** Audit and rotate all passwords for service accounts; implement strict password complexity policies.
3.  **Harden AD CS:** Review and remediate identified certificate templates (ESC1-ESC8) to prevent unauthorized certificate issuance.
4.  **Least Privilege:** Restrict administrative access to Domain Controllers and ensure that service accounts are not granted unnecessary privileges via delegation.