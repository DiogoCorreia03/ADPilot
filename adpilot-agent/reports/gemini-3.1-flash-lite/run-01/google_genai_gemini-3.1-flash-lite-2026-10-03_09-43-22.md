# Penetration Testing Report: Polaris.local

## Executive Summary
This assessment evaluated the security posture of the `polaris.local` domain. The primary objective was to identify vulnerabilities within the domain environment and demonstrate the potential for unauthorized access. The assessment achieved full domain dominance, compromising the Domain Administrator account and extracting the entire `NTDS.DIT` database. A total of 1 host (`CAPTAIN`) and 5 accounts were compromised during the engagement.

## Attack Path Summary
The assessment followed a path from external user enumeration to full domain compromise:
1. **Initial Access:** Kerbrute password spraying identified valid user credentials (`skyler.white`, `hank.schrader`).
2. **Credential Discovery:** Kerberoasting identified and cracked hashes for `jesse.pinkman` and `walter.white`.
3. **Privilege Escalation:** Utilizing the `skyler.white` account, the team identified and exploited the AD CS (Active Directory Certificate Services) ESC1 vulnerability.
4. **Domain Compromise:** By requesting a certificate for the `Administrator` account, the team obtained an NTLM hash and performed a `secretsdump` against the Domain Controller.

## Credentials Obtained
| Username | Password | Source Method | Subsequent Use |
| :--- | :--- | :--- | :--- |
| skyler.white | Password123 | Password Spraying | Domain escalation via ESC1 |
| hank.schrader | sHyangja210 | Password Spraying | N/A |
| jesse.pinkman | Wang0Tang0! | Kerberoasting | SMB Share access |
| walter.white | Metho1o590oA$elry | Kerberoasting | N/A |
| Administrator | N/A (NT Hash) | AD CS / Certipy | Full domain dumping |

## Compromised Systems
| Hostname | IP Address | Access Level | Notes |
| :--- | :--- | :--- | :--- |
| CAPTAIN | 192.168.122.10 | Domain Admin | Target of all successful exploits |

## Findings
### AD CS ESC1 Misconfiguration
* **Description:** The Certificate Template was configured to allow low-privileged users to request certificates with arbitrary Subject Alternative Names (SAN).
* **Evidence:** `Certipy find` confirmed ESC1 vulnerability on 192.168.122.10.
* **Impact:** Full domain privilege escalation.

### Weak Password Policies
* **Description:** Domain users utilized weak or guessable passwords, allowing successful Kerbrute password spraying and offline Kerberoasting.
* **Evidence:** Valid passwords obtained for `skyler.white`, `hank.schrader`, `jesse.pinkman`, and `walter.white`.

## Vulnerabilities Demonstrated
* **AD CS ESC1:** Allowed impersonation of the Domain Administrator.
* **Kerberoasting:** Allowed offline cracking of service account passwords.

## Authentication & Identity Findings
* **Password Reuse:** Multiple service accounts were identified with weak, crackable passwords.
* **Service Accounts:** Accounts such as `jesse.pinkman` and `walter.white` were found to be susceptible to Kerberoasting, providing a direct path to account compromise.

## Lateral Movement
* **SMB Access:** Used `jesse.pinkman` credentials to access `\\CAPTAIN\SharingIsCaring`, leading to the discovery of configuration files/hints.

## Privilege Escalation
* **Starting Privilege:** `skyler.white` (Domain User)
* **Ending Privilege:** `Administrator` (Domain Admin)
* **Technique:** Exploitation of AD CS ESC1 vulnerability via `certipy` to generate a certificate for the Domain Administrator, followed by NTLM authentication.

## Domain Compromise
* **Status:** Achieved.
* **Details:** Using the certificate obtained via ESC1, the team authenticated as `Administrator` and successfully executed `secretsdump` to extract the `NTDS.DIT` file and all domain hashes.

## Failed Attack Paths
* **MSSQL xp_cmdshell:** Access was denied due to insufficient privileges on `CAPTAIN\SQLEXPRESS`.
* **ESC4 Abuse:** Attempted exploitation failed due to RPC access restrictions to the certificate services.
* **WMI Execution:** Failed due to RPC_S_ACCESS_DENIED errors when attempting to run remote commands with `jesse.pinkman` credentials.

## Timeline of Compromise
1. **Enumeration:** Ran Kerbrute user enumeration and password spray.
2. **Credential Acquisition:** Successfully sprayed passwords and performed Kerberoasting.
3. **Data Exfiltration:** Accessed SMB shares to identify additional credentials.
4. **Escalation:** Exploited AD CS ESC1 to request an Administrator certificate.
5. **Finalization:** Authenticated as Administrator and dumped domain secrets.

## Assessment Statistics
* **Hosts Compromised:** 1
* **Accounts Compromised:** 5
* **Credentials/Hashes Obtained:** 4 plaintexts, 1 NTLM hash
* **Privilege Escalations:** 1 (User to Domain Admin)

## Recommendations
1. **Harden AD CS:** Disable ESC1-vulnerable templates and enforce strict access control on certificate template modification.
2. **Enforce Password Complexity:** Implement a robust password policy to mitigate the efficacy of password spraying and offline cracking.
3. **Account Monitoring:** Regularly audit for SPNs (Service Principal Names) associated with user accounts to identify potential Kerberoasting targets.
4. **Disable Insecure Defaults:** Audit and disable null session access where possible.