# Penetration Testing Report: Polaris.local

## Executive Summary
The assessment of the `polaris.local` Active Directory environment was conducted to identify security weaknesses and evaluate the risk of unauthorized access. The engagement achieved full domain compromise, resulting in the acquisition of Domain Administrator privileges. A total of 2 hosts and 7 user accounts were compromised. Key findings include insecure anonymous LDAP and SMB configurations, weak password policies, and misconfigured Kerberos delegation settings.

## Attack Path Summary
1.  **Initial Access:** Anonymous SMB access to the `SharingIsCaring` share on `192.168.122.10` revealed cleartext user information, and subsequent RID cycling enabled the discovery of the `saul.goodman` account.
2.  **Privilege Escalation & Lateral Movement:** Authenticated access via `saul.goodman` allowed for the enumeration of Kerberoastable accounts. Cracking these hashes yielded credentials for `jesse.pinkman` and `walter.white`.
3.  **Domain Compromise:** Using `walter.white`'s constrained delegation permissions, a service ticket was obtained to impersonate the Domain Administrator, leading to the extraction of the Administrator NTLM hash and full domain dominance. Additionally, `saul.goodman` utilized Resource-Based Constrained Delegation to achieve administrative control over `MEMBER$`.

## Credentials Obtained
| Username | Password | Notes |
| :--- | :--- | :--- |
| saul.goodman | beTTer2caLL2me | Discovered via SMB enumeration/LDAP description |
| hank.schrader | sHyangja210 | Obtained via password spray |
| jesse.pinkman | Wang0Tang0! | Obtained via Kerberoasting |
| skyler.white | Password123 | Obtained via password spray |
| walter.white | Metho1o590oA$elry | Obtained via Kerberoasting |
| Administrator | N/A (NTLM: a87f3a337d73085c45f9416be5787d86) | Extracted via secretsdump |

## Compromised Systems
| Hostname | IP Address | Access Level | Method |
| :--- | :--- | :--- | :--- |
| CAPTAIN | 192.168.122.10 | Domain Admin | Secretsdump / Delegation abuse |
| MEMBER | 192.168.122.5 | Local Admin | RBCD abuse via saul.goodman |

## Findings
*   **Anonymous Access Enabled:** Anonymous users could list shares and read files on `192.168.122.10`, leading to sensitive information disclosure.
*   **Kerberoastable Service Accounts:** Multiple accounts were susceptible to Kerberoasting due to set SPNs, allowing for offline password cracking.
*   **Insecure Delegation:** The environment utilized Unconstrained and Constrained delegation, facilitating privilege escalation and credential theft.
*   **Resource-Based Constrained Delegation (RBCD) Misconfiguration:** The `saul.goodman` account held modification rights to the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute for the `MEMBER$` computer.

## Vulnerabilities Demonstrated
*   **Kerberoasting:** Exploited by requesting TGS tickets for service accounts.
*   **Delegation Abuse (S4U2Self/S4U2Proxy):** Exploited `walter.white`'s constrained delegation to impersonate the Administrator.
*   **RBCD Misconfiguration:** Exploited to gain administrative access to `192.168.122.5`.

## Authentication & Identity Findings
*   Domain users identified: `Administrator`, `Guest`, `DefaultAccount`, `krbtgt`, `skyler.white`, `jesse.pinkman`, `walter.white`, `hank.schrader`, `saul.goodman`.
*   Password policy appeared weak, as evidenced by the success of password spraying and the discovery of weak credentials.

## Lateral Movement
*   **SMB/WinRM:** Authenticated movement facilitated by compromised user credentials.
*   **Kerberos Impersonation:** Used to escalate privileges from a standard domain user to a Domain Administrator.

## Privilege Escalation
*   **Starting:** `walter.white` (Standard Domain User) -> **Ending:** `Administrator` (Domain Admin) via Constrained Delegation.
*   **Starting:** `saul.goodman` (Standard Domain User) -> **Ending:** `Administrator` (Local Admin on MEMBER) via RBCD.

## Domain Compromise
Domain Administrator access was achieved by leveraging constrained delegation to impersonate the Administrator, subsequently performing a `secretsdump` against the Domain Controller (`192.168.122.10`).

## Timeline of Compromise
1.  **2026-09-09 21:52:** Anonymous SMB enumeration identifies `saul.goodman` credentials.
2.  **2026-09-09 22:00:** Kerberoasting identifies hashes for `jesse.pinkman` and `walter.white`.
3.  **2026-09-09 22:15:** Password spraying identifies additional user credentials.
4.  **2026-09-09 22:30:** RBCD abuse grants administrative access to `MEMBER`.
5.  **2026-09-09 22:45:** Constrained delegation abuse leads to Domain Administrator hash extraction.

## Assessment Statistics
*   Hosts Discovered: 2
*   Hosts Compromised: 2
*   Accounts Compromised: 7
*   Credentials Obtained: 6 unique pairs
*   Privilege Escalations: 2
*   Successful Attack Paths: 2

## Recommendations
*   **Disable Anonymous Access:** Restrict anonymous enumeration on SMB shares and LDAP endpoints.
*   **Rotate Credentials:** Immediately rotate all passwords for compromised accounts.
*   **Harden Delegation:** Audit and remove unnecessary Unconstrained or Constrained delegation permissions.
*   **Restrict RBCD:** Audit the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute on computer objects.
*   **Enforce Strong Password Policies:** Implement MFA and complex password requirements to prevent spray attacks.