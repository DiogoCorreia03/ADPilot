# Penetration Testing Report: Polaris.local

## Executive Summary
The penetration test of the `polaris.local` environment focused on identifying security weaknesses in Active Directory authentication and service configuration. The assessment successfully identified multiple valid domain accounts via password spraying and Kerberoasting. While lateral movement was achieved across the network, full domain administrator compromise (DCSync or equivalent) was not demonstrated. 

*   **Assessment Scope:** Internal network (192.168.122.5, 192.168.122.10)
*   **Highest Level of Compromise:** Domain User / File share access
*   **Compromised Hosts:** 2 (MEMBER, CAPTAIN)
*   **Compromised Accounts:** 4 (skyler.white, hank.schrader, jesse.pinkman, walter.white)
*   **Critical Observations:** Weak password policies and service account configurations facilitated successful password spraying and Kerberoasting attacks.

---

## Attack Path Summary
1.  **Initial Access:** Enumerated valid users via Kerberos user discovery. 
2.  **Credential Acquisition:** Performed password spraying to obtain `skyler.white` and `hank.schrader` credentials.
3.  **Lateral Movement:** Used obtained credentials to access sensitive SMB shares (`ImportantNotes`, `SharingIsCaring`) on `CAPTAIN` (192.168.122.10).
4.  **Credential Escalation:** Performed Kerberoasting and AS-REP roasting, leading to the successful cracking of passwords for `jesse.pinkman` and `walter.white`.

---

## Credentials Obtained
| Username | Password | Source/Method |
| :--- | :--- | :--- |
| skyler.white | Password123 | Password Spraying |
| hank.schrader | sHyangja210 | Password Spraying |
| jesse.pinkman | Wang0Tang0! | Kerberoasting/AS-REP Roasting |
| walter.white | Metho1o590oA$elry | Kerberoasting/AS-REP Roasting |

---

## Compromised Systems
*   **CAPTAIN (192.168.122.10):** Windows Server 2016. Accessed via SMB using valid user credentials. Recovered sensitive files (`note.txt`, `skyler.txt`).
*   **MEMBER (192.168.122.5):** Windows Member Server. Accessed via SMB using valid user credentials.

---

## Findings
*   **Weak Password Policy:** Password spraying successfully compromised multiple user accounts.
*   **Kerberoastable Service Accounts:** Multiple accounts (jesse.pinkman, walter.white, saul.goodman) were susceptible to Kerberoasting.
*   **AS-REP Roasting Vulnerability:** Account `jesse.pinkman` did not require Kerberos pre-authentication, allowing for offline hash cracking.
*   **Sensitive Information Disclosure:** File shares `ImportantNotes` and `SharingIsCaring` contained internal notes accessible to standard domain users.

---

## Vulnerabilities Demonstrated
*   **Insecure Kerberos Configuration:** Accounts identified without pre-authentication (AS-REP roasting).
*   **Service Principal Name (SPN) Weakness:** Kerberoasting allowed the extraction and cracking of service account credentials.

---

## Lateral Movement
Lateral movement was primarily performed via SMB. Valid domain credentials were used to authenticate to share resources on `CAPTAIN` (192.168.122.10) and `MEMBER` (192.168.122.5), allowing for file retrieval and domain enumeration.

---

## Privilege Escalation
No vertical privilege escalation (e.g., to Local or Domain Admin) was successfully demonstrated. Attempts to leverage Kerberos delegation (S4U2Self/S4U2Proxy) and DCSync were unsuccessful due to access denials.

---

## Domain Compromise
Full domain compromise was **not achieved**. The assessment team was unable to gain Domain Administrative privileges or extract the `NTDS.dit` file.

---

## Failed Attack Paths
*   **RCE via IIS:** The identified "Simple Uploader" on 192.168.122.10 did not allow for executable file uploads to a reachable location.
*   **Constrained Delegation Abuse:** Attempts to impersonate the Administrator via `walter.white` failed due to pre-authentication errors.
*   **RBCD Abuse:** Attempts to configure `saul.goodman` for Resource-Based Constrained Delegation failed due to authentication errors.

---

## Timeline of Compromise
1.  **2026-09-10 12:30:** Initial user enumeration.
2.  **2026-09-10 12:32:** Password spray success (skyler.white, hank.schrader).
3.  **2026-09-10 12:35:** AS-REP roast identified (jesse.pinkman).
4.  **2026-09-10 12:40:** Kerberoasting executed.
5.  **2026-09-10 12:41:** Cracked additional passwords (jesse.pinkman, walter.white).
6.  **2026-09-10 12:46:** Final share intelligence gathering.

---

## Assessment Statistics
*   **Hosts Discovered:** 2
*   **Hosts Compromised:** 2
*   **Accounts Compromised:** 4
*   **Credentials Obtained:** 4 Unique (6 total records)
*   **Privilege Escalations:** 0
*   **Successful Attack Paths:** 1 (User Credential -> Lateral Movement -> Information Gathering)

---

## Recommendations
1.  **Enforce Password Complexity:** Implement a robust password policy to mitigate password spraying risks.
2.  **Disable Kerberos Pre-Authentication:** Audit accounts for "Do not require Kerberos pre-authentication" and disable it for all standard users.
3.  **Rotate Compromised Passwords:** Immediately force a password reset for all four identified compromised accounts.
4.  **Restrict Share Permissions:** Audit `ImportantNotes` and `SharingIsCaring` share permissions and restrict access to authorized personnel only.
5.  **Monitor SPNs:** Periodically audit accounts with SPNs and ensure associated passwords are long, complex, and unique.