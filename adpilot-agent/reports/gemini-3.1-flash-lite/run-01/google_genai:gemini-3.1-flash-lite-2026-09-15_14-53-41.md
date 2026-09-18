# Penetration Testing Report: Polaris.local

## Executive Summary
*   **Assessment Scope:** Polaris.local domain infrastructure, including 192.168.122.5 (member.polaris.local) and 192.168.122.10 (CAPTAIN - Domain Controller).
*   **Overall Objective:** Assess the security posture of the domain environment through enumeration, credential harvesting, and lateral movement.
*   **Highest Level of Compromise:** Domain User access achieved.
*   **Compromised Hosts:** 1 (192.168.122.10 - CAPTAIN).
*   **Compromised Accounts:** 4 (hank.schrader, skyler.white, jesse.pinkman, walter.white).
*   **Critical Observations:** The environment is susceptible to Kerberoasting and AS-REP roasting due to weak service account configurations and user account security settings.

---

## Attack Path Summary
1.  **Initial Access:** Identified valid usernames via Kerberos user enumeration. Successfully performed password spraying to obtain initial credentials for `hank.schrader` and `skyler.white`.
2.  **Information Gathering:** Used valid `hank.schrader` credentials to enumerate SMB shares, identifying sensitive files in `//192.168.122.10/ImportantNotes/`.
3.  **Credential Harvesting:** Performed AS-REP roasting against `jesse.pinkman` and Kerberoasting against service accounts (`jesse.pinkman`, `walter.white`, `saul.goodman`).
4.  **Lateral Movement/Privilege Escalation:** Successfully cracked hashes for `jesse.pinkman` and `walter.white`, further validating access to `polaris.local`.

---

## Credentials Obtained
| Username | Password | Source | Method |
| :--- | :--- | :--- | :--- |
| hank.schrader | sHyangja210 | Spraying | Password Spraying |
| skyler.white | Password123 | Spraying | Password Spraying |
| jesse.pinkman | Wang0Tang0! | AS-REP/TGS | Kerberoasting / AS-REP Roasting |
| walter.white | Metho1o590oA$elry | TGS-REP | Kerberoasting |

---

## Compromised Systems
*   **CAPTAIN (192.168.122.10):** Domain User access via `hank.schrader`, `skyler.white`, `jesse.pinkman`, `walter.white`. Confirmed SMB read/write access to specific shares.

---

## Findings
*   **Weak Password Policy:** Password spraying successfully compromised multiple user accounts.
*   **Kerberoasting:** Multiple service accounts were identified with SPNs and compromised via TGS-REP hash cracking.
*   **AS-REP Roasting:** The account `jesse.pinkman` did not require Kerberos pre-authentication, allowing for offline hash cracking.
*   **Sensitive Information Exposure:** Cleartext notes containing internal operational details were found on accessible SMB shares.

---

## Vulnerabilities Demonstrated
*   **Kerberos AS-REP Roasting:** Enabled offline brute-forcing of `jesse.pinkman`.
*   **Kerberos TGS Roasting:** Allowed recovery of service account passwords for `jesse.pinkman` and `walter.white`.
*   **Weak Authentication:** Password spraying identified multiple valid user credentials.

---

## Authentication & Identity Findings
*   **Guest Access:** Anonymous authentication to the DC (192.168.122.10) was successful for domain info discovery, though share access was restricted.
*   **Password Reuse:** Confirmed across multiple accounts through successful spraying and validation.

---

## Lateral Movement
*   **SMB Access:** Used legitimate user credentials to access `//192.168.122.10/ImportantNotes` and `//192.168.122.10/SharingIsCaring`.

---

## Domain Compromise
*   **Status:** Full Domain Administrator compromise was **NOT** achieved.

---

## Failed Attack Paths
*   **MS-SQL Command Execution:** Attempted `xp_cmdshell` via authenticated SMB access; failed due to configuration restrictions.
*   **Constrained Delegation Abuse:** Failed to leverage `walter.white` and `saul.goodman` for service ticket requests (KDC_ERR_PREAUTH_FAILED).
*   **DCSync/Secrets Dumping:** Failed due to lack of administrative privileges.

---

## Timeline of Compromise
1.  **2026-09-15:** Identified domain info and valid users via Kerberos discovery.
2.  **2026-09-15:** Successfully performed password spraying.
3.  **2026-09-15:** Discovered sensitive information via SMB enumeration.
4.  **2026-09-15:** Conducted AS-REP and Kerberoasting attacks.
5.  **2026-09-15:** Cracked hashes and validated additional credentials.

---

## Assessment Statistics
*   **Hosts discovered:** 2
*   **Hosts compromised:** 1
*   **Accounts discovered:** 3+
*   **Accounts compromised:** 4
*   **Credentials obtained:** 4 unique sets
*   **Successful attack paths:** 1 (Credential Harvesting & Access)
*   **Failed attack paths:** 4 (Delegation abuse, SQL execution, DCSync, Local Admin enumeration)

---

## Recommendations
*   **Enforce Strong Password Policies:** Implement complexity and length requirements to prevent password spraying.
*   **Disable AS-REP Roasting:** Enable "Do not require Kerberos pre-authentication" for all user accounts unless specifically required.
*   **Service Account Management:** Implement long, complex, and periodically rotated passwords for all service accounts to mitigate Kerberoasting.
*   **Restrict SMB Shares:** Implement Principle of Least Privilege (PoLP) on file shares to remove sensitive operational notes.