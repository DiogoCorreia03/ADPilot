# Penetration Testing Report: Polaris.local

## Executive Summary
This assessment evaluated the security posture of the `polaris.local` Active Directory environment. The primary objective was to identify vulnerabilities leading to unauthorized access and privilege escalation. The assessment successfully compromised multiple domain user accounts and achieved lateral movement across domain-joined infrastructure. While full domain administrative compromise was not achieved, significant internal access was demonstrated through service account exploitation, constrained delegation abuse, and Resource-Based Constrained Delegation (RBCD) techniques.

*   **Assessment Scope:** `192.168.122.5`, `192.168.122.10`
*   **Highest Level of Compromise:** Domain User Access / Lateral Movement
*   **Compromised Hosts:** 2 (`192.168.122.5`, `192.168.122.10`)
*   **Compromised Accounts:** 4 (skyler.white, hank.schrader, saul.goodman, jesse.pinkman, walter.white)

---

## Attack Path Summary
1.  **Initial Access:** MSSQL service authentication on `192.168.122.10` using credentials recovered from public enumeration (`skyler.white`, `hank.schrader`).
2.  **Credential Harvesting:** Enumeration of LDAP attributes revealed `saul.goodman`'s password stored in a description field.
3.  **Lateral Movement (Service Accounts):** AS-REP roasting of `jesse.pinkman` and Kerberoasting of `walter.white` provided additional service account credentials.
4.  **Privilege Escalation/Delegation:** 
    *   Utilized Constrained Delegation with Protocol Transition via `walter.white` to access the Domain Controller.
    *   Leveraged RBCD on a member machine (`MEMBER$`) via a newly added machine account (`ATTACKBOX$`) using `saul.goodman` credentials to execute remote commands.

---

## Credentials Obtained
| Username | Password | Source | Method |
| :--- | :--- | :--- | :--- |
| `skyler.white` | `Password123` | Enum/Service | Credential Spraying/MSSQL |
| `hank.schrader` | `sHyangja210` | Enum/Service | Credential Spraying/MSSQL |
| `saul.goodman` | `beTTer2caLL2me` | LDAP | Description Attribute |
| `jesse.pinkman`| `Wang0Tang0!` | AD User | AS-REP Roasting |
| `walter.white` | `Metho1o590oA` | Service Account | Kerberoasting |

---

## Compromised Systems
*   **CAPTAIN (192.168.122.10):** Domain Controller. Accessed via SMB and authenticated service account sessions.
*   **MEMBER$ (192.168.122.X):** Member server. Accessed via WMI execution after configuring RBCD.

---

## Findings & Vulnerabilities
*   **Cleartext Credentials in LDAP Attributes:** The `saul.goodman` account description contained a cleartext password. This facilitated further authenticated access to the domain.
*   **AS-REP/Kerberoasting Susceptibility:** Domain accounts `jesse.pinkman` and `walter.white` were susceptible to roasting, allowing offline password recovery.
*   **Insecure Delegation Settings:** The environment utilized Constrained Delegation and allowed RBCD, enabling impersonation of domain users and remote code execution.
*   **ADCS Misconfiguration (ESC1):** Identified templates (`ESC1`) allowed for potentially vulnerable certificate enrollment, though full utilization was limited by KDC trust issues.

---

## Lateral Movement & Privilege Escalation
*   **Delegation Abuse:** Demonstrated successful impersonation of `Administrator` via `walter.white` using Constrained Delegation.
*   **RBCD:** Configured `MEMBER$` to trust a self-added `ATTACKBOX$` machine account, enabling `wmiexec` remote code execution.

---

## Timeline of Compromise
1.  **Recon:** Performed web enumeration on `192.168.122.10` (Simple Uploader).
2.  **Auth:** Successfully authenticated to MSSQL using `skyler.white`.
3.  **Enumeration:** Extracted domain users and discovered `saul.goodman` credentials in LDAP.
4.  **Roasting:** Performed AS-REP and Kerberoasting, recovering passwords for `jesse.pinkman` and `walter.white`.
5.  **Persistence/Movement:** Configured RBCD on a member machine to gain remote execution.

---

## Assessment Statistics
*   **Hosts Discovered:** 2
*   **Hosts Compromised:** 2
*   **Accounts Compromised:** 5
*   **Credentials Obtained:** 5 unique sets
*   **Successful Attack Paths:** 3
*   **Privilege Escalations:** 2 (Delegation/RBCD)

---

## Recommendations
1.  **Cleartext Passwords:** Audit all LDAP attributes (especially `description`, `info`, and `comment` fields) to identify and remove cleartext passwords.
2.  **Account Auditing:** Disable pre-authentication for service accounts (to prevent AS-REP roasting) and enforce strong password policies.
3.  **Delegation Hardening:** Review and restrict the use of Unconstrained and Constrained delegation. Disable RBCD where not strictly required for business operations.
4.  **ADCS Security:** Revoke or restrict enrollment permissions for highly permissive certificate templates (e.g., ESC1).