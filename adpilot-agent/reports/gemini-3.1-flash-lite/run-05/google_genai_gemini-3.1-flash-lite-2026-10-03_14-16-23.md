# Executive Summary

**Assessment Scope:** Polaris Domain (polaris.local)
**Overall Objective:** Security assessment of domain identity and authentication services.
**Highest Level of Compromise:** Access to domain-joined hosts and service account compromise via Kerberoasting. Domain Administrator compromise was NOT achieved.
**Compromised Hosts:** 1 (CAPTAIN/192.168.122.10)
**Compromised Accounts:** 4 (skyler.white, hank.schrader, jesse.pinkman, walter.white)
**Critical Observations:** The environment exhibits weak password policies leading to successful credential spraying and Kerberoasting. Multiple AD CS (Active Directory Certificate Services) misconfigurations were identified, though exploitation was hindered by environmental constraints.

---

# Attack Path Summary

1.  **Initial Access:** Password spraying against the domain (`polaris.local`) resulted in the compromise of `skyler.white` and `hank.schrader`.
2.  **Service Account Compromise:** Using discovered credentials, Kerberoasting was performed against `192.168.122.10`, leading to the recovery of credentials for `jesse.pinkman` and `walter.white`.
3.  **Lateral Movement:** Authenticated access was established to the domain controller (`CAPTAIN`) using `jesse.pinkman` credentials, allowing read/write access to sensitive SMB shares (`ImportantNotes`, `SharingIsCaring`).

---

# Credentials Obtained

| Username | Password | Source Host | Acquisition Method | Subsequent Use |
| :--- | :--- | :--- | :--- | :--- |
| skyler.white | Password123 | 192.168.122.10 | Password Spraying | LDAP Dump, SMB Enumeration |
| hank.schrader | sHyangja210 | 192.168.122.10 | Password Spraying | LDAP Dump, SMB Enumeration |
| jesse.pinkman | Wang0Tang0! | 192.168.122.10 | Kerberoasting | SMB Access |
| walter.white | Metho1o590oA$elry | 192.168.122.10 | Kerberoasting | Attempted Lateral Movement |

---

# Compromised Systems

*   **Hostname:** CAPTAIN (192.168.122.10)
    *   **Access:** Authenticated SMB/LDAP
    *   **Privilege Level:** Domain User
    *   **Credentials Used:** skyler.white, jesse.pinkman
    *   **Significant Artifacts:** Read/Write access to `ImportantNotes` and `SharingIsCaring` shares containing sensitive internal communications.

---

# Findings

**Title: Weak Password Policy**
*   **Evidence:** Successful password spraying identified valid credentials for multiple users.
*   **Affected Systems:** polaris.local
*   **Impact:** Unauthorized access to domain user accounts.

**Title: Kerberoastable Service Accounts**
*   **Evidence:** `GetUserSPNs.py` identified accounts with SPNs, allowing the extraction and cracking of service account tickets.
*   **Affected Systems:** polaris.local (Domain Controller)
*   **Impact:** Compromise of service account credentials (`jesse.pinkman`, `walter.white`).

**Title: Sensitive Information Disclosure**
*   **Evidence:** Writable SMB shares (`ImportantNotes`, `SharingIsCaring`) on the Domain Controller contained internal notes and password hints.
*   **Affected Systems:** CAPTAIN (192.168.122.10)
*   **Impact:** Exposure of administrative intent and potential password policies.

---

# Vulnerabilities Demonstrated

*   **AD CS Misconfiguration (ESC1-ESC4, ESC8):** Audit via `certipy` identified templates allowing enrollee-supplied subjects, dangerous permissions, and HTTP enrollment.
*   **Unconstrained Delegation:** Account `CAPTAIN$` identified with unconstrained delegation.
*   **Resource-Based Constrained Delegation (RBCD):** Configured on `MEMBER$`.

---

# Authentication & Identity Findings

*   **Discovered Users:** Administrator, Guest, krbtgt, DefaultAccount, CAPTAIN$, skyler.white, jesse.pinkman, walter.white, hank.schrader, saul.goodman, MEMBER$.
*   **Service Accounts:** krbtgt, jesse.pinkman, walter.white, saul.goodman, CAPTAIN$.
*   **Delegation Settings:** 
    *   `walter.white`: Constrained Delegation (Protocol Transition) to CIFS/captain.polaris.local
    *   `saul.goodman`: Resource-Based Constrained Delegation to MEMBER$
    *   `CAPTAIN$`: Unconstrained Delegation

---

# Lateral Movement

*   **SMB:** Used `jesse.pinkman` credentials to access `\\192.168.122.10\ImportantNotes` and `\\192.168.122.10\SharingIsCaring`.

---

# Domain Compromise

Domain Administrator compromise was **not achieved**. The assessment concluded with domain user-level access.

---

# Failed Attack Paths

*   **ESC1/ESC8 Exploitation:** Attempts to exploit AD CS failed due to RPC errors and lack of NTLM triggers.
*   **RBCD/Delegation Exploitation:** Failed due to authentication/session errors and misconfigured SPNs.

---

# Timeline of Compromise

1.  **Enumeration:** Performed `lookupsid` and Kerberos user enumeration.
2.  **Initial Access:** Successfully performed password spray (obtained `skyler.white`, `hank.schrader`).
3.  **Credential Escalation:** Performed Kerberoasting; cracked credentials for `jesse.pinkman` and `walter.white`.
4.  **Domain Mapping:** Conducted `ldapdomaindump` and `certipy` audit.
5.  **Data Exfiltration:** Accessed writable shares on the Domain Controller.

---

# Assessment Statistics

*   Hosts discovered: 2
*   Hosts compromised: 1
*   Accounts discovered: 11
*   Accounts compromised: 4
*   Credentials obtained: 4 unique pairs
*   Hashes recovered: 2 (via Kerberoasting)
*   Successful attack paths: 1
*   Failed attack paths: 6+

---

# Recommendations

1.  **Enforce Password Complexity:** Implement and enforce a strong password policy (complexity, length, and history) to prevent spraying.
2.  **Audit SPNs:** Review service account privileges and remove unnecessary SPNs. Use Managed Service Accounts (gMSAs) where possible.
3.  **Harden AD CS:** Disable unused templates and move Web Enrollment (ESC8) to HTTPS with explicit authentication requirements.
4.  **Remove Sensitive Data from Shares:** Restrict access to and sanitize contents of SMB shares on domain controllers.