# Penetration Testing Report

## Executive Summary
The penetration testing assessment of the `polaris.local` environment successfully demonstrated complete compromise of the domain. Initial access was gained through Kerberoasting of service accounts, which provided credentials for further enumeration. The assessment identified critical misconfigurations in Active Directory Certificate Services (AD CS), enabling the escalation of privileges to the level of Domain Administrator. In total, 2 hosts were assessed, both were compromised, and 5 distinct domain accounts were compromised.

## Attack Path Summary
1.  **Initial Access:** Enumerated valid users via Kerberos. Performed Kerberoasting to extract service account tickets. Successfully cracked the password for `jesse.pinkman`.
2.  **Internal Enumeration:** Authenticated to the domain using `jesse.pinkman` credentials. Utilized BloodHound and LDAP enumeration to map the domain, identifying AD CS vulnerabilities (ESC1) and delegation configurations.
3.  **Privilege Escalation:** Exploited the ESC1 vulnerability on the certificate authority (192.168.122.5) to request a certificate as `Administrator@polaris.local`, effectively escalating to domain-level administrative privileges.
4.  **Lateral Movement:** Used validated credentials (`skyler.white`, `saul.goodman`) to access SMB shares and verify host-level access across the network.

## Credentials Obtained
| Username | Password | Acquisition Method | Subsequent Use |
| :--- | :--- | :--- | :--- |
| `jesse.pinkman` | `Wang0Tang0!` | Kerberoasting / Hashcat | LDAP/SMB access, AD Enumeration |
| `walter.white` | `Metho1o590oA$elry` | Kerberoasting / Hashcat | N/A |
| `skyler.white` | `Password123` | Kerbrute Bruteforce | SMB access to 192.168.122.5 |
| `saul.goodman` | `beTTer2caLL2me` | Null session discovery | SMB access to 192.168.122.10 |
| `hank.schrader` | `sHyangja210` | Kerbrute Bruteforce | N/A |

## Compromised Systems
*   **CAPTAIN (192.168.122.10):** Domain Controller / MSSQL. Compromised via service account credentials (`jesse.pinkman`).
*   **MEMBER (192.168.122.5):** AD Certificate Services host. Compromised via AD CS exploitation (ESC1).

## Findings
### AD CS ESC1 Vulnerability
*   **Description:** The certificate template was configured with `ENROLLEE_SUPPLIES_SUBJECT` and allowed client authentication, permitting any user to request a certificate as any other user.
*   **Evidence:** Successfully requested an `Administrator` certificate using the `ESC1` path.
*   **Impact:** Full domain compromise via impersonation.

### Weak Service Account Passwords
*   **Description:** Service accounts were susceptible to Kerberoasting and utilized weak passwords.
*   **Evidence:** Cracked `jesse.pinkman` hash.
*   **Impact:** Provided the initial authenticated foothold in the domain.

## Vulnerabilities Demonstrated
*   **AD CS Misconfiguration (ESC1):** Affected `192.168.122.5`. Enabled unauthorized impersonation of domain users.
*   **Unconstrained Delegation:** Affected `CAPTAIN` and `jesse.pinkman`. Though not fully exploited for pivot, it presented a significant lateral movement risk.

## Authentication & Identity Findings
*   **Password Reuse:** Evidence of common password patterns and reuse across user accounts.
*   **Null Sessions:** Enabled on `CAPTAIN` (192.168.122.10), leading to the discovery of `saul.goodman` credentials.
*   **Account Discovery:** Enumerated via Kerberos and LDAP, identifying several high-privilege groups including `Domain Admins` and `Enterprise Admins`.

## Lateral Movement
*   **SMB Access:** Used legitimate credentials to access `ImportantNotes` and `SharingIsCaring` shares, leading to the recovery of internal notes and credentials.

## Privilege Escalation
*   **Method:** AD CS Certificate Request (ESC1).
*   **Starting Privilege:** Standard User (`jesse.pinkman`).
*   **Ending Privilege:** Domain Administrator (via impersonation).

## Domain Compromise
*   **Status:** Full Domain Compromise achieved.
*   **Technique:** AD CS exploitation allowed generation of a valid Administrator certificate.

## Failed Attack Paths
*   **Unconstrained Delegation Pivot:** Attempts to leverage the unconstrained delegation configuration on `jesse.pinkman` failed due to KDC configuration restrictions.
*   **Secretsdump:** Remote SAM/SYSTEM dumping failed on `192.168.122.5` due to insufficient privileges.

## Timeline of Compromise
1.  **User Enumeration:** Identified valid users via Kerberos.
2.  **Kerberoasting:** Extracted and cracked service account credentials.
3.  **Authenticated Access:** Logged into domain shares using `jesse.pinkman`.
4.  **AD Mapping:** Performed BloodHound/LDAP enumeration.
5.  **ESC1 Exploitation:** Requested Administrator certificate on `192.168.122.5`.
6.  **Full Compromise:** Confirmed domain dominance.

## Assessment Statistics
*   Hosts Discovered: 2
*   Hosts Compromised: 2
*   Accounts Compromised: 5
*   Credentials Obtained: 6
*   Successful Attack Paths: 1 (Primary)

## Recommendations
1.  **Harden AD CS:** Disable templates configured with `ENROLLEE_SUPPLIES_SUBJECT` and remove unused EKU settings (ESC1-ESC8).
2.  **Disable Unconstrained Delegation:** Enforce constrained or resource-based constrained delegation where possible.
3.  **Credential Hygiene:** Implement strong password policies and rotate passwords for service accounts identified as compromised.
4.  **Restrict SMB Null Sessions:** Disable anonymous enumeration and null sessions on domain members.