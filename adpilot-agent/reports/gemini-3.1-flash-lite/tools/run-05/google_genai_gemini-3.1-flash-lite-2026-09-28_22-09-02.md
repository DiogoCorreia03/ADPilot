# Penetration Testing Report: polaris.local

## Executive Summary
The penetration test of the `polaris.local` domain was conducted to evaluate the security posture of the infrastructure. The primary objective was to assess the resilience of the domain against credential-based attacks and internal privilege escalation. The assessment achieved lateral movement to member systems and successful impersonation of domain-level administrative rights via Resource-Based Constrained Delegation (RBCD). A total of 2 hosts were identified and accessed, with 5 unique user accounts compromised.

## Attack Path Summary
1.  **Initial Access:** Credential harvesting via `kerbrute` password spraying identified valid domain user accounts.
2.  **Service Account Compromise:** Kerberoasting performed against service accounts allowed for the cracking of hashes to obtain valid credentials for `jesse.pinkman` and `walter.white`.
3.  **Lateral Movement & Privilege Escalation:** Using the `saul.goodman` account (discovered via SMB share enumeration), the team identified an RBCD misconfiguration. By leveraging this, the team successfully impersonated the Domain Administrator to gain access to `MEMBER.polaris.local` (192.168.122.5).

## Credentials Obtained
| Username | Password | Source | Subsequent Use |
| :--- | :--- | :--- | :--- |
| `hank.schrader` | `sHyangja210` | Kerbrute password spray | Authentication validation |
| `skyler.white` | `Password123` | Kerbrute password spray | Authentication validation |
| `jesse.pinkman` | `Wang0Tang0!` | Kerberoasting | SMB access, LDAP enumeration |
| `walter.white` | `Metho1o590oA$elry` | Kerberoasting | SMB access |
| `saul.goodman` | `beTTer2caLL2me` | Manual LDAP/Share enumeration | RBCD privilege escalation |

## Compromised Systems
*   **CAPTAIN.polaris.local (192.168.122.10):** Domain Controller. Accessed via SMB/LDAP services using valid user credentials.
*   **MEMBER.polaris.local (192.168.122.5):** Member Server. Accessed via impersonated Domain Administrator ticket using RBCD.

## Findings
### Resource-Based Constrained Delegation (RBCD) Misconfiguration
*   **Evidence:** `saul.goodman` possessed rights to manipulate delegation attributes, allowing for the creation and configuration of a trust relationship with a controlled account.
*   **Affected Systems:** `CAPTAIN.polaris.local`
*   **Impact:** Allowed for the impersonation of the Domain Administrator and lateral movement to member servers.

### Weak Service Account Passwords
*   **Evidence:** Kerberoasting results yielded hashes that were successfully cracked via `hashcat`.
*   **Affected Systems:** `polaris.local` (Service accounts `jesse.pinkman`, `walter.white`)
*   **Impact:** Provided high-privilege credentials enabling further internal reconnaissance and lateral movement.

## Vulnerabilities Demonstrated
*   **Kerberoasting:** Exploited by requesting service tickets for accounts with SPNs, facilitating offline dictionary attacks.
*   **AD CS Misconfiguration (ESC1):** Potential for certificate-based impersonation; while full PKINIT support was limited, the vulnerability was confirmed via template assessment.

## Authentication & Identity Findings
*   **Password Spraying Success:** Identified multiple valid accounts using a simple password policy (`Password123`, `sHyangja210`).
*   **Credential Reuse:** Multiple service accounts used passwords that were susceptible to common wordlist attacks.

## Lateral Movement
*   **SMB Access:** Used `jesse.pinkman` and `walter.white` credentials to access `ImportantNotes` and `SharingIsCaring` shares.
*   **RBCD Impersonation:** Used the `saul.goodman` account to perform S4U2Self/S4U2Proxy operations, resulting in an `Administrator` service ticket for the CIFS service on `MEMBER.polaris.local`.

## Privilege Escalation
*   **Technique:** Resource-Based Constrained Delegation.
*   **Starting Privilege:** Standard User (`saul.goodman`).
*   **Ending Privilege:** Domain Administrator (via impersonation).
*   **Evidence:** Obtained `Administrator@cifs_MEMBER.polaris.local@POLARIS.LOCAL.ccache` ticket.

## Domain Compromise
Domain dominance was achieved in a functional sense via RBCD impersonation, allowing full administrative command execution on member servers using the `Administrator` identity. Attempts to perform a full `DCSync` on the DC were restricted by security policies, preventing total extraction of the NTDS.dit file.

## Failed Attack Paths
*   **NTLM Relay (ESC8):** Attempts to relay to AD CS Web Enrollment failed due to persistent network timeouts.
*   **DCSync/Secretsdump:** Failed due to lack of direct Administrative/DCSync privileges on the Domain Controller.

## Timeline of Compromise
1.  **2026-09-28 19:53:** Successfully sprayed passwords and identified 2 valid accounts.
2.  **2026-09-28 19:54:** Performed Kerberoasting; cracked credentials for 2 service accounts.
3.  **2026-09-28 20:12:** Escalated reconnaissance; identified sensitive notes in SMB shares.
4.  **2026-09-28 20:21:** Discovered `saul.goodman` credentials and identified RBCD path.
5.  **2026-09-28 20:27:** Executed RBCD impersonation; gained Domain Administrator access to member host.

## Assessment Statistics
*   **Hosts Discovered:** 2
*   **Hosts Compromised:** 2
*   **Accounts Compromised:** 5
*   **Privilege Escalations:** 1 (RBCD)
*   **Lateral Movement Events:** 2 (SMB Access, RBCD Impersonation)

## Recommendations
*   **Disable/Restrict RBCD:** Audit all `msDS-AllowedToActOnBehalfOfOtherIdentity` attributes to ensure only authorized service principals are present.
*   **Password Policy:** Enforce complex, non-sequential passwords to mitigate password spraying and dictionary attacks.
*   **Service Account Management:** Implement Managed Service Accounts (gMSA) to automate password management and rotate credentials.
*   **Restrict Delegation:** Review and audit account delegation settings across the domain; remove unnecessary Protocol Transition rights.