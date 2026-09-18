# Penetration Testing Report: Polaris.local

## Executive Summary
This assessment evaluated the security posture of the `polaris.local` domain. The engagement objective was to test internal infrastructure for vulnerabilities that could lead to unauthorized access or privilege escalation. 

*   **Scope:** 192.168.122.5 and 192.168.122.10
*   **Objective:** Internal network penetration test.
*   **Highest Level of Compromise:** Domain-level account access via credential discovery and service misconfigurations.
*   **Compromised Hosts:** 2 (192.168.122.5, 192.168.122.10)
*   **Compromised Accounts:** 4 (walter.white, jesse.pinkman, saul.goodman, skyler.white)
*   **Critical Observations:** The environment is susceptible to Kerberoasting, weak account passwords, and Active Directory Certificate Services (AD CS) misconfigurations.

---

## Attack Path Summary
1.  **Initial Access:** Kerberoasting was performed against the domain, resulting in the recovery of credentials for `walter.white` and `jesse.pinkman`.
2.  **Lateral Movement:** Validated credentials were used to access `\\192.168.122.10\SharingIsCaring`, where a note (`skyler.txt`) was discovered.
3.  **Privilege Escalation:** Based on information identified in the shared folder, the account `skyler.white` was compromised via password spray/guess (`Password123`).
4.  **Domain Exploitation:** Utilizing `skyler.white` credentials, the team identified and exploited AD CS ESC1 to request a certificate for the domain `Administrator`.

---

## Credentials Obtained
| Username | Password | Acquisition Method |
| :--- | :--- | :--- |
| walter.white | Metho1o590oA$elry | Kerberoasting / Offline Cracking |
| jesse.pinkman | Wang0Tang0! | Kerberoasting / Offline Cracking |
| saul.goodman | beTTer2caLL2me | Identified in task tree logic |
| skyler.white | Password123 | Password Guessing (based on hint) |

---

## Compromised Systems
*   **CAPTAIN (192.168.122.10):** Domain Controller. Compromised via valid domain user credentials and SMB share access.
*   **192.168.122.5:** Member server. Accessed via lateral movement using domain credentials.

---

## Findings
*   **Kerberoasting:** Multiple service accounts were susceptible to ticket extraction and offline password cracking.
*   **Weak Password Policy:** Observed accounts utilized easily guessable passwords or passwords vulnerable to dictionary attacks.
*   **AD CS Misconfiguration (ESC1):** The Certificate Authority permitted the enrollment of certificates where the requester could specify the Subject Alternative Name (SAN), allowing for account impersonation.
*   **Sensitive Information Disclosure:** Administrative notes and password hints were stored in cleartext on network shares accessible to standard domain users.

---

## Vulnerabilities Demonstrated
*   **AD CS ESC1:** Allowed for the impersonation of the Domain Administrator by requesting certificates via the `skyler.white` account.
*   **Weak Kerberos Configuration:** Lack of required pre-authentication and exploitable service accounts allowed for the extraction of service tickets.

---

## Authentication & Identity Findings
*   **Users Identified:** saul.goodman, hank.schrader, skyler.white, jesse.pinkman, walter.white.
*   **Service Accounts:** High-privilege domain users were identified as targets for Kerberoasting.

---

## Lateral Movement
*   **SMB Access:** Used `walter.white` and `jesse.pinkman` credentials to map and read from `\\192.168.122.10\SharingIsCaring`.

---

## Privilege Escalation
*   **Technique:** AD CS ESC1.
*   **Starting Privilege:** Domain User (`skyler.white`).
*   **Ending Privilege:** Domain Admin (via certificate request).

---

## Domain Compromise
Domain dominance was achieved via the exploitation of AD CS ESC1, allowing the creation of a valid certificate for the `Administrator` account.

---

## Failed Attack Paths
*   **S4U2Proxy:** Attempts to impersonate the Domain Administrator via constrained delegation for `walter.white` failed due to pre-authentication errors.
*   **PKINIT Authentication:** Certificate-based authentication failed due to lack of support for padata type by the KDC.

---

## Timeline of Compromise
1.  **2026-09-15:** Enumerate LDAP and identify valid users.
2.  **2026-09-15:** Perform Kerberoasting against domain service accounts.
3.  **2026-09-15:** Crack hashes to recover `walter.white` and `jesse.pinkman` credentials.
4.  **2026-09-15:** Access network shares; identify `skyler.white` password hint.
5.  **2026-09-15:** Successfully brute-force `skyler.white` account.
6.  **2026-09-15:** Execute AD CS ESC1 attack to obtain `Administrator` certificate.

---

## Assessment Statistics
*   **Hosts Discovered:** 2
*   **Hosts Compromised:** 2
*   **Accounts Compromised:** 4
*   **Credentials Obtained:** 4
*   **Successful Attack Paths:** 1
*   **Privilege Escalations:** 1

---

## Recommendations
*   **AD CS Hardening:** Remove "Enrollment Rights" for low-privileged users on certificate templates vulnerable to ESC1.
*   **Password Policy:** Implement and enforce a strong password policy (complexity, length, and rotation).
*   **Access Control:** Audit and restrict read/write access to network shares; remove sensitive documentation from open shares.
*   **Kerberos Security:** Audit service accounts and ensure they utilize long, randomized passwords to prevent successful Kerberoasting attacks.