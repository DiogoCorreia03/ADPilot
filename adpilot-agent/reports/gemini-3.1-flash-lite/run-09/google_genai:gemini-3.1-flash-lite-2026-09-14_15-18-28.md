# Penetration Testing Report: Polaris.local

## Executive Summary
This assessment evaluated the security posture of the `polaris.local` Active Directory environment. The primary objective was to identify exploitable vulnerabilities and demonstrate potential attack paths leading to unauthorized system access. 

The assessment successfully compromised three user accounts and gained authenticated access to the domain controller (`CAPTAIN`). Despite successful identification of several Active Directory Certificate Services (AD CS) misconfigurations, full domain administrative control was not achieved due to RPC communication constraints and privilege limitations.

*   **Assessment Scope:** `polaris.local` Domain Controller (192.168.122.10) and secondary IIS server (192.168.122.5).
*   **Highest Level of Compromise:** Authenticated domain user access with read/write access to specific SMB shares.
*   **Compromised Hosts:** 1 (CAPTAIN - 192.168.122.10)
*   **Compromised Accounts:** 3 (skyler.white, hank.schrader, saul.goodman)
*   **Critical Observations:** Weak password policies, sensitive information leakage in SMB shares, and misconfigured AD CS templates.

---

## Attack Path Summary
1.  **Initial Access:** Anonymous guest access to the `SharingIsCaring` SMB share revealed cleartext information regarding a password change.
2.  **Credential Discovery:** Password spraying based on the hint in `skyler.txt` resulted in the compromise of `skyler.white` and `hank.schrader`.
3.  **Privilege Escalation & Enumeration:** Authenticated LDAP queries identified an additional credential for `saul.goodman` in his account description.
4.  **Service Exploitation:** The `saul.goodman` credentials were used to perform Kerberoasting against the `svc_sql` account, resulting in the recovery of the `svc_sql` password.
5.  **Lateral Movement:** The `skyler.white` account was successfully used to authenticate to the Domain Controller and interact with sensitive shares.

---

## Credentials Obtained
| Username | Password | Source | Method |
| :--- | :--- | :--- | :--- |
| `skyler.white` | `Password123` | Password Spray | Password Spraying |
| `hank.schrader` | `sHyangja210` | Password Spray | Password Spraying |
| `saul.goodman` | `beTTer2caLL2me` | LDAP User Description | Enumeration |
| `svc_sql` | `SQL_Backup_2023!` | Kerberoasting | TGS-REP cracking |

---

## Compromised Systems
*   **Hostname:** `CAPTAIN` (192.168.122.10)
    *   **Access Obtained:** Authenticated SMB, LDAP, and MSSQL access.
    *   **Privilege Level:** Standard Domain User.
    *   **Significant Artifacts:** `skyler.txt`, `note.txt`, and domain enumeration data.

---

## Findings
### Sensitive Data Exposure (SMB)
*   **Evidence:** `skyler.txt` found in `\\192.168.122.10\SharingIsCaring` containing password policy hints.
*   **Impact:** Provided context for successful password spraying.

### Weak Password Policy / Credential Exposure
*   **Evidence:** Users `skyler.white` and `hank.schrader` were compromised via password spraying; `saul.goodman` credential found in cleartext in LDAP metadata.
*   **Impact:** Allowed unauthorized access to the domain environment.

---

## Vulnerabilities Demonstrated
*   **Kerberoasting:** Successfully captured and cracked the TGS-REP hash for `svc_sql` service account.
*   **AD CS Misconfiguration (ESC4):** `skyler.white` had `Full Control` over the `ESC4` certificate template.
*   **SMB Share Guest Access:** Readable/Writable shares contained sensitive organizational documentation.

---

## Authentication & Identity Findings
*   **Discovered Users:** `saul.goodman`, `skyler.white`, `hank.schrader`, `walter.white`, `svc_sql`.
*   **Privileged Groups:** `Domain Admins`, `Enterprise Admins`, `Schema Admins`, `Administrators`.
*   **Guest Access:** Null authentication was permitted for connection to SMB shares, though file access was restricted to specific shares.

---

## Lateral Movement
*   **Credential Reuse:** Authenticated to the Domain Controller (192.168.122.10) using `skyler.white` credentials discovered via password spraying.
*   **Service Authentication:** Accessed the MSSQL service on 192.168.122.10 using `saul.goodman` credentials.

---

## Privilege Escalation
*   **Technique:** ACL abuse on AD CS templates.
*   **Evidence:** Successfully modified the `ESC4` template to include `Enroll` permissions using `skyler.white` account, though final exploitation was hindered by RPC/connectivity errors.

---

## Domain Compromise
Domain Admin compromise was **not achieved**. While domain user-level access was obtained, attempts to escalate to Domain Administrator via constrained delegation and AD CS exploitation failed due to RPC access denials and KDC communication errors.

---

## Failed Attack Paths
*   **Constrained Delegation Abuse:** Attempts to abuse `walter.white` delegation failed due to authentication errors (`KDC_ERR_PREAUTH_FAILED`).
*   **DCSync/Secretsdump:** Attempts to dump `NTDS.DIT` failed due to insufficient replication privileges.

---

## Timeline of Compromise
1.  **09-14 14:00:** Performed DNS enumeration and Kerbrute user enumeration.
2.  **09-14 14:05:** Identified and downloaded `skyler.txt` via SMB.
3.  **09-14 14:08:** Successfully performed password spray to compromise `skyler.white` and `hank.schrader`.
4.  **09-14 14:09:** Discovered `saul.goodman` credentials in LDAP.
5.  **09-14 14:10:** Conducted Kerberoasting against `svc_sql` and cracked the password.
6.  **09-14 14:15:** Enumerated AD CS vulnerabilities and modified `ESC4` template.

---

## Assessment Statistics
*   **Hosts Discovered:** 2
*   **Hosts Compromised:** 1
*   **Accounts Compromised:** 3
*   **Credentials Obtained:** 4 unique accounts
*   **Privilege Escalations:** 1 (Partial - AD CS Template Modification)

---

## Recommendations
1.  **Secure SMB Shares:** Disable guest access to SMB shares and enforce strict ACLs on `SharingIsCaring` and `ImportantNotes`.
2.  **Remediate Cleartext Credentials:** Remove sensitive password information from LDAP user descriptions.
3.  **Harden AD CS:** Remove unnecessary `Full Control` or `Write` permissions from non-administrative users on certificate templates.
4.  **Enforce Strong Password Policies:** Implement multi-factor authentication (MFA) and prevent the use of common or easily guessable passwords.
5.  **Audit Service Accounts:** Periodically change passwords for service accounts like `svc_sql` and rotate them frequently to mitigate the impact of Kerberoasting.