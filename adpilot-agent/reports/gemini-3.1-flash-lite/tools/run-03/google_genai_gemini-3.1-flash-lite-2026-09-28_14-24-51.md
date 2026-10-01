# Penetration Testing Report: polaris.local

## Executive Summary
This assessment evaluated the security posture of the `polaris.local` Active Directory environment. The testing identified multiple security weaknesses, including weak password policies, Kerberoasting opportunities, and over-privileged service accounts. While user-level access was successfully obtained across multiple accounts and authenticated access was gained to domain shares, full domain compromise (Domain Admin) was not achieved.

*   **Assessment Scope:** `192.168.122.5` (MEMBER) and `192.168.122.10` (CAPTAIN/Domain Controller).
*   **Highest Level of Compromise:** Authenticated domain user access; successful extraction of credentials.
*   **Compromised Hosts:** 2
*   **Compromised Accounts:** 4
*   **Critical Observations:** Insecure password management and service account configurations allowed for the mass enumeration and offline cracking of domain service account credentials.

---

## Attack Path Summary
1.  **Initial Access:** Anonymous SMB access to `//192.168.122.10/SharingIsCaring/skyler.txt` revealed a password hint, facilitating the discovery of `skyler.white:Password123` via password spraying.
2.  **Credential Escalation:** Using `skyler.white` credentials, service principal names (SPNs) were enumerated via `GetUserSPNs.py`. Offline cracking of these tickets yielded valid credentials for `jesse.pinkman` and `walter.white`.
3.  **Lateral Movement:** Confirmed authenticated access to SMB shares and WMI access to `MEMBER.polaris.local` using the compromised credentials.

---

## Credentials Obtained
| Username | Password | Source | Method |
| :--- | :--- | :--- | :--- |
| `skyler.white` | `Password123` | SMB Share (Hint) | Password Spraying |
| `hank.schrader` | `sHyangja210` | Domain Enumeration | Kerbrute |
| `jesse.pinkman` | `Wang0Tang0!` | Kerberoast | Offline Cracking |
| `walter.white` | `Metho1o590oA$elry` | Kerberoast | Offline Cracking |

---

## Compromised Systems
*   **CAPTAIN (192.168.122.10):** Domain Controller. Accessed via SMB shares (`ImportantNotes`, `SharingIsCaring`) using `skyler.white`.
*   **MEMBER (192.168.122.5):** Member Server. Accessed via WMI using `walter.white` and `saul.goodman` credentials.

---

## Findings
### 1. Weak Password Policy
*   **Evidence:** Multiple accounts (skyler.white, hank.schrader) were compromised using common passwords.
*   **Impact:** Unauthorized access to domain resources.

### 2. Kerberoastable Service Accounts
*   **Evidence:** `jesse.pinkman`, `walter.white`, and `saul.goodman` had SPNs registered, allowing for ticket requests.
*   **Impact:** Offline password cracking of service account credentials.

### 3. Excessive Delegation Permissions
*   **Evidence:** `CAPTAIN$` and `jesse.pinkman` were configured for Unconstrained Delegation.
*   **Impact:** Potential for full account takeover if administrative sessions are captured.

---

## Vulnerabilities Demonstrated
*   **Kerberoasting:** Permitted the recovery of cleartext passwords for service accounts by requesting TGS tickets.
*   **Unconstrained Delegation:** Misconfigured delegation settings present a critical risk to identity security.

---

## Lateral Movement
*   **SMB:** Successful enumeration and file access on `CAPTAIN` using multiple valid domain credentials.
*   **WMI:** Confirmed WMI access to `MEMBER` using `walter.white` and `saul.goodman` credentials.

---

## Privilege Escalation
*   **Status:** No successful privilege escalation to Local System or Domain Admin occurred. Attempts to use `xp_cmdshell` on MSSQL and create computer accounts via SAMR were denied due to insufficient permissions.

---

## Domain Compromise
*   **Status:** Not achieved. Attempts at DCSync, secretsdump, and Silver Ticket generation failed due to lack of administrative privileges.

---

## Failed Attack Paths
*   **MSSQL Exploitation:** `skyler.white` lacked `sysadmin` privileges to execute `xp_cmdshell`.
*   **RBCD/Delegation Abuse:** Attempts to impersonate users via S4U2Self/S4U2Proxy failed due to pre-authentication errors and lack of object creation permissions.

---

## Timeline of Compromise
1.  **13:00:** Anonymous SMB share discovery on `CAPTAIN`.
2.  **13:03:** Password sprayed `skyler.white:Password123`.
3.  **13:03:** Enumerated SPNs and performed Kerberoasting.
4.  **13:04:** Cracked credentials for `jesse.pinkman` and `walter.white`.
5.  **13:05:** LDAP domain dump and BloodHound enumeration.
6.  **13:09:** Identified delegation misconfigurations.
7.  **13:22:** Confirmed WMI access on `MEMBER`.

---

## Assessment Statistics
*   **Hosts discovered:** 2
*   **Hosts compromised:** 2
*   **Accounts compromised:** 4
*   **Credentials obtained:** 5 (unique password sets for 4 users)
*   **Successful attack paths:** 2
*   **Failed attack paths:** 7

---

## Recommendations
1.  **Enforce Strong Password Policies:** Implement complexity and rotation requirements to prevent password spraying.
2.  **Audit Service Accounts:** Periodically change passwords for all service accounts and migrate away from legacy SPN configurations where possible.
3.  **Disable Unconstrained Delegation:** Transition to Constrained or Resource-Based Constrained Delegation (RBCD) to limit lateral movement vectors.
4.  **Remove Privileged Access:** Audit the `skyler.white` and `walter.white` accounts to ensure they do not have permissions beyond their operational necessity.