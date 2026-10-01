# Penetration Testing Report: Polaris.local

## Executive Summary
The penetration test of the `polaris.local` domain focused on identifying security weaknesses in network authentication, file share access, and service configurations. The engagement resulted in the successful compromise of multiple domain user accounts and the extraction of sensitive internal information via SMB shares. While full Domain Administrator compromise was not achieved, the assessment confirmed significant weaknesses in password management and service account security.

*   **Scope:** `192.168.122.5`, `192.168.122.10`
*   **Highest Level of Compromise:** Authenticated User (Domain User level)
*   **Compromised Hosts:** 1 (192.168.122.10)
*   **Compromised Accounts:** 4 (skyler.white, hank.schrader, walter.white, jesse.pinkman)
*   **Critical Observations:** Weak password policies, vulnerable Kerberoasting service accounts, and sensitive information disclosure via SMB shares.

## Attack Path Summary
1.  **Initial Access:** Enumerate domain users via Kerberos and identify `skyler.white` via password spraying.
2.  **Information Gathering:** Access `ImportantNotes` and `SharingIsCaring` SMB shares using `skyler.white`, retrieving context that enabled further credential discovery.
3.  **Lateral/Credential Expansion:** Perform Kerberoasting against domain controller `192.168.122.10` to extract and crack TGT hashes for `walter.white` and `jesse.pinkman`.
4.  **Service Access:** Utilize discovered credentials to authenticate against MSSQL (1433) and various SMB shares.

## Credentials Obtained
| Username | Password | Source Method |
| :--- | :--- | :--- |
| skyler.white | Password123 | Password Spraying |
| hank.schrader | sHyangja210 | Targeted Password Spraying |
| walter.white | Metho1o590oA$elry | Kerberoasting / Hash Cracking |
| jesse.pinkman | Wang0Tang0! | Kerberoasting / Hash Cracking |

## Compromised Systems
*   **192.168.122.10 (CAPTAIN):** Accessed via SMB and MSSQL using compromised domain user accounts. No administrative privilege was achieved. Sensitive notes regarding internal physical security and password habits were recovered.

## Findings
### 1. Insecure Password Policies
*   **Description:** Domain users utilized weak, predictable passwords easily susceptible to spraying and cracking.
*   **Evidence:** `skyler.white` used "Password123"; `hank.schrader` password was derived from discovered context.
*   **Impact:** Rapid account compromise.

### 2. Service Account Kerberoasting
*   **Description:** Service accounts with SPNs set were susceptible to offline brute-force attacks.
*   **Evidence:** Successfully extracted and cracked TGT hashes for `walter.white` and `jesse.pinkman`.
*   **Impact:** Exposure of service account credentials.

### 3. Sensitive Information Disclosure
*   **Description:** SMB shares contained plain-text files revealing internal security concerns and password change patterns.
*   **Evidence:** `note.txt` and `skyler.txt` retrieved from writable shares.
*   **Impact:** Facilitated lateral movement and further credential discovery.

## Authentication & Identity Findings
*   **Discovered Users:** saul.goodman, hank.schrader, skyler.white, jesse.pinkman, walter.white, Administrator, Guest, krbtgt.
*   **Groups Identified:** Domain Admins, Domain Users, Enterprise Admins, DnsAdmins, Masters.
*   **Guest Access:** Null session access was successful on `192.168.122.10`, though share listing was restricted.

## Lateral Movement
*   **SMB:** Used to traverse shares and retrieve files.
*   **MSSQL:** Authenticated access confirmed using multiple domain accounts; however, attempts to execute code (xp_cmdshell) failed due to lack of `sysadmin` privileges.

## Privilege Escalation
*   **Status:** No successful privilege escalation to local or domain administrator was achieved during this assessment.

## Domain Compromise
*   **Status:** Not achieved.

## Failed Attack Paths
*   **MSSQL Code Execution:** Multiple attempts to enable `xp_cmdshell` failed due to lack of `sysadmin` rights.
*   **Constrained Delegation Abuse:** Attempts to use `walter.white` and `saul.goodman` for delegation abuse failed due to invalid credentials or KDC errors.
*   **AS-REP Roasting:** No users identified with `UF_DONT_REQUIRE_PREAUTH` flag.

## Timeline of Compromise
1.  **15:05:** Performed Kerberos user enumeration.
2.  **15:08:** Compromised `skyler.white` via password spray.
3.  **15:10:** Performed Kerberoasting; cracked credentials for `walter.white` and `jesse.pinkman`.
4.  **15:36:** Enumerate SMB shares and contents using `hank.schrader`.
5.  **15:44:** Finalized SMB enumeration and MSSQL authentication testing.

## Assessment Statistics
*   **Hosts Discovered:** 2
*   **Hosts Compromised:** 1
*   **Accounts Compromised:** 4
*   **Successful Attack Paths:** 1 (User Account -> SMB/MSSQL Access)
*   **Failed Attack Paths:** 6 (RCE, Delegation abuse, AS-REP)

## Recommendations
*   **Password Policy:** Enforce a complex password policy and implement multi-factor authentication (MFA).
*   **Service Accounts:** Rotate passwords for service accounts used in Kerberoasting; use Group Managed Service Accounts (gMSA) where possible.
*   **Share Permissions:** Remove broad "Write" access to sensitive SMB shares.
*   **Least Privilege:** Audit MSSQL permissions to ensure non-administrative users cannot access or interact with system-level configurations.