# Executive Summary

During the penetration test assessment against the `polaris.local` domain environment, the testing team evaluated external and internal network security controls, Active Directory configurations, and host-level posture across target infrastructure. The assessment scope encompassed two primary hosts: `192.168.122.5` (`MEMBER.polaris.local`) and `192.168.122.10` (`CAPTAIN.polaris.local`, the Domain Controller).

Through structured enumeration, Kerberoasting, password spraying, and Active Directory analysis, the assessment achieved a significant level of compromise:
* **Compromised Hosts:** 2 hosts (`MEMBER` and `CAPTAIN`) had authenticated access established, with credential validation and remote session execution achieved across both systems.
* **Compromised Accounts:** Multiple domain user accounts and service accounts were compromised through password spraying and Kerberoasting ticket cracking.
* **Critical Observations:** The environment exhibited weak service account password complexity (permitting offline dictionary cracking of Kerberoastable tickets), cleartext credential hints stored in Active Directory object descriptions (`saul.goodman`), and complex Active Directory delegation configurations (including Resource-Based Constrained Delegation). While domain user and service account credentials were successfully obtained and validated across hosts, full Domain Administrator privilege escalation and DCSync operations were successfully restricted by existing access controls.

---

# Attack Path Summary

The assessment successfully executed the following chronological attack paths:

1. **Initial Reconnaissance and User Discovery:**
   * Enumerated DNS/SRV records and performed Kerberos user enumeration against the Domain Controller (`192.168.122.10`), identifying valid domain user accounts including `saul.goodman`, `hank.schrader`, and `skyler.white`.
2. **Password Spraying and Credential Discovery:**
   * Executed Kerbrute password spraying against valid domain users, successfully identifying valid credentials for `skyler.white` (`Password123`) and `hank.schrader` (`sHyangja210`).
3. **Authenticated Active Directory Enumeration and Kerberoasting:**
   * Utilized valid credentials (`skyler.white:Password123`) to query domain attributes, discovering an explicit plaintext password hint in the description attribute for `saul.goodman` (`DELETE LATER. Password:beTTer2caLL2me`).
   * Performed authenticated Kerberoasting (`GetUserSPNs.py`) using `skyler.white` credentials to extract TGS-REP service tickets for `jesse.pinkman`, `walter.white`, and `saul.goodman`.
4. **Offline Ticket Cracking:**
   * Cracked the extracted Kerberoastable service tickets using `hashcat` (mode 13100) against a potential passwords wordlist, recovering plain-text credentials for `walter.white` (`Metho1o590oA$elry`) and `jesse.pinkman` (`Wang0Tang0!`).
5. **Lateral Movement and Access Verification:**
   * Validated newly obtained credentials across domain targets via SMB and WMI protocols (`netexec`, `wmiexec`), verifying successful authentication and standard user/service session access on both `MEMBER` (`192.168.122.5`) and `CAPTAIN` (`192.168.122.10`).
6. **Delegation Analysis:**
   * Identified and verified Active Directory delegation relationships, notably discovering that `saul.goodman` possesses Resource-Based Constrained Delegation rights over the member computer account (`MEMBER$`).

---

# Credentials Obtained

All credentials discovered, sprayed, cracked, and validated during the assessment are cataloged below:

| ID | Username | Password / Hash | Domain | Source / Acquisition Method | Subsequent Use |
|----|----------|-----------------|--------|-----------------------------|----------------|
| 1 | `saul.goodman@polaris.local` | — | `polaris.local` | Kerbrute user enumeration | Validated user discovery |
| 2 | `hank.schrader@polaris.local` | — | `polaris.local` | Kerbrute user enumeration | Validated user discovery |
| 3 | `skyler.white@polaris.local` | — | `polaris.local` | Kerbrute user enumeration | Validated user discovery |
| 4 | `skyler.white` | `Password123` | `polaris.local` | Kerbrute password spraying | Authenticated LDAP / SMB queries / Kerberoasting |
| 5 | `hank.schrader` | `sHyangja210` | `polaris.local` | Kerbrute password spraying | Validated credentials |
| 6 | `skyler.white` | `Password123` | `polaris.local` | GetUserSPNs.py execution | Authenticated enumeration |
| 7 | `jesse.pinkman` | `Wang0Tang0!` | `POLARIS.LOCAL` | Kerberoasting hashcat mode 13100 | WMI / SMB credential validation |
| 8 | `walter.white` | `Metho1o590oA$elry` | `POLARIS.LOCAL` | Kerberoasting hashcat mode 13100 | WMI / SMB credential validation |
| 9 | `skyler.white` | `Password123` | `polaris.local` | Domain user credential store | Enumeration |
| 10 | `skyler.white` | `Password123` | `polaris.local` | Previous assessment tasks | Enumeration |
| 11 | `skyler.white` | `Password123` | `polaris.local` | LDAP search task 1.3 (Description hint discovery) | LDAP querying |
| 12 | `skyler.white` | `Password123` | — | Netexec SMB enumeration | SMB share enumeration |
| 13 | `walter.white` | `Metho1o590oA$elry` | `polaris.local` | Kerberoast ticket cracking | SMB / WMI access verification |
| 14 | `walter.white` | `Metho1o590oA$elry` | — | Cracked credentials | SMB / WMI access verification |
| 15 | `walter.white` | `Metho1o590oA$elry` | `polaris.local` | Validated via netexec SMB and WMI | WMI execution attempts |
| 16 | `jesse.pinkman` | `Wang0Tang0!` | `polaris.local` | Discovered credentials | WMI execution validation |

*(Note: Additional discovered credentials for `saul.goodman` (`beTTer2caLL2me`) were obtained via LDAP description attribute inspection and validated during WMI/SMB checks).*

---

# Compromised Systems

| Hostname | IP Address | Operating System | Access Obtained | Privilege Level | Credentials Used | Significant Artifacts / Shares |
|----------|------------|------------------|-----------------|-----------------|------------------|--------------------------------|
| `MEMBER` | `192.168.122.5` | Windows Server 2016 Standard 14393 x64 | SMB / Network Authentication | Standard User / Delegated RBCD target | `skyler.white`, `walter.white`, `hank.schrader` | CertEnroll (READ), IPC$ (READ) |
| `CAPTAIN` | `192.168.122.10` | Windows Server 2016 Standard 14393 x64 (DC) | SMB / WMI / LDAP Authentication | Domain User (Non-Admin) | `skyler.white`, `walter.white`, `jesse.pinkman`, `saul.goodman` | ImportantNotes (READ/WRITE), SharingIsCaring (READ/WRITE), SYSVOL, NETLOGON |

---

# Findings

### 1. Plaintext Password Stored in Active Directory User Description
* **Evidence:** LDAP search query executed using `skyler.white` credentials revealed the description attribute for user `saul.goodman` contained: `DELETE LATER. Password:beTTer2caLL2me`.
* **Affected Systems:** `192.168.122.10` (`CAPTAIN.polaris.local`)
* **Description:** Administrative users or automation scripts incorrectly stored active account credentials within the standard LDAP `description` user attribute.
* **Impact:** Any authenticated domain user can read standard user attribute metadata, immediately compromising the `saul.goodman` account without requiring password cracking or spraying.
* **Attack Path:** Authenticated LDAP Enumeration -> Description Attribute Extraction -> Credential Reuse.

### 2. Weak Service Account Passwords Enabling Kerberoasting
* **Evidence:** Extraction of Kerberoastable TGS tickets using `GetUserSPNs.py` followed by successful offline password cracking via `hashcat` (mode 13100) against `potential_passwords.txt`, recovering cleartext passwords for `walter.white` (`Metho1o590oA$elry`) and `jesse.pinkman` (`Wang0Tang0!`).
* **Affected Systems:** `192.168.122.10` (`CAPTAIN.polaris.local`)
* **Description:** Domain user accounts configured with Service Principal Names (SPNs) utilized weak or dictionary-based passwords.
* **Impact:** Attackers with standard domain user access can request TGS service tickets for SPN-enabled accounts and perform offline brute-force/dictionary attacks to recover plaintext credentials.
* **Attack Path:** Authenticated Domain Enumeration -> Kerberoasting -> Offline Hash Cracking -> Credential Acquisition.

### 3. Weak Domain Password Policy and Password Spraying Exposure
* **Evidence:** Successful execution of `kerbrute` password spraying against domain users, resulting in valid authentication for `skyler.white` (`Password123`) and `hank.schrader` (`sHyangja210`).
* **Affected Systems:** `192.168.122.10` (`CAPTAIN.polaris.local`)
* **Description:** Domain users utilized predictable or commonly reused passwords that succumbed to password spraying techniques against Kerberos (port 88).
* **Impact:** Initial foothold establishment within the Active Directory domain without requiring prior internal access or phishing vectors.
* **Attack Path:** Kerberos User Enumeration -> Password Spraying -> Valid Credential Acquisition.

### 4. Over-Permissive SMB Share Permissions
* **Evidence:** Netexec SMB enumeration utilizing discovered valid credentials (`skyler.white`, `walter.white`) demonstrated read and write access to `ImportantNotes` and `SharingIsCaring` shares on `CAPTAIN` (`192.168.122.10`).
* **Affected Systems:** `192.168.122.10` (`CAPTAIN.polaris.local`)
* **Description:** Domain shares on the Domain Controller permitted authenticated domain users read and write access.
* **Impact:** Potential risk of unauthorized file modification, data exfiltration, or placement of malicious files in accessible network shares.
* **Attack Path:** Credential Validation -> SMB Share Enumeration -> Access Verification.

---

# Vulnerabilities Demonstrated

* **Kerberoastable Service Accounts with Weak Passwords:** Demonstrated via `GetUserSPNs.py` and `hashcat` against service accounts `walter.white` and `jesse.pinkman`.
* **Password Spraying Vulnerability:** Demonstrated via `kerbrute` against Kerberos authentication services, successfully identifying user passwords (`skyler.white`, `hank.schrader`).
* **Insecure Storage of Sensitive Data in LDAP Attributes:** Demonstrated via `ldapsearch` exposing plaintext credentials within the `description` field of user `saul.goodman`.
* **Resource-Based Constrained Delegation Configuration:** Demonstrated via `findDelegation.py`, identifying that `saul.goodman` holds RBCD rights over computer object `MEMBER$`.

---

# Authentication & Identity Findings

* **Discovered Users:** `saul.goodman`, `hank.schrader`, `skyler.white`, `jesse.pinkman`, `walter.white`, `Administrator`, `Guest`, `DefaultAccount`, `krbtgt`.
* **Service Accounts / SPN Accounts:** Accounts with associated SPNs identified during Kerberoasting (`jesse.pinkman`, `walter.white`, `saul.greenman/saul.goodman`).
* **Delegation Findings:**
  * `CAPTAIN$` (Computer): Unconstrained Delegation.
  * `jesse.pinkman` (Person): Unconstrained Delegation (No SPN).
  * `walter.white` (Person): Constrained Delegation w/ Protocol Transition (`CIFS/captain.polaris.local`).
  * `saul.goodman` (Person): Resource-Based Constrained Delegation over `MEMBER$`.
* **Domain SID:** `S-1-5-21-3122561497-3620408224-1960744130`
* **Local Groups of Note:** `Masters`, `DnsAdmins`, `Domain Admins`, `Domain Users`.

---

# Lateral Movement

Lateral movement activities during the assessment focused on credential validation and remote command execution across domain systems:
* **SMB / WMI Authentication:** Validated discovered and cracked credentials (`skyler.white`, `walter.white`, `jesse.pinkman`, `saul.goodman`, `hank.schrader`) against SMB (`445/TCP`) and WMI services across `MEMBER` (`192.168.122.5`) and `CAPTAIN` (`192.168.122.10`).
* **Execution Results:** Successful remote execution and session validation were achieved under standard user privileges. Administrative lateral movement attempts (such as `wmiexec` or `secretsdump` requiring local administrator or Domain Administrator privileges) failed with `STATUS_LOGON_FAILURE`, `rpc_s_access_denied`, or WBEM access errors (`0x80041003`), confirming that standard user accounts lacked administrative control over remote operating systems.

---

# Privilege Escalation

* **Starting Privilege:** Unauthenticated external network posture / valid standard domain user account (`skyler.white`).
* **Ending Privilege:** Authenticated domain user with cracked service account credentials (`walter.white`, `jesse.pinkman`), exposed user description credentials (`saul.goodman`), and Resource-Based Constrained Delegation configuration rights over `MEMBER$`.
* **Technique:** Credential discovery via LDAP attributes, Kerberoasting with offline dictionary attack, and Active Directory delegation enumeration.
* **Evidence:** Successful extraction of TGS hashes, offline cracking results, and `findDelegation.py` output showing RBCD rights.

---

# Domain Compromise

* **Status:** Domain Administrator compromise and DCSync operations were **NOT** achieved during this assessment.
* **Details:** While multiple domain user accounts, service account credentials, and delegation paths (such as Resource-Based Constrained Delegation on `saul.goodman` targeting `MEMBER$`) were successfully identified and validated, attempts to execute DCSync (`secretsdump.py`) or administrative command execution using non-privileged or constrained credentials failed due to insufficient access rights (`STATUS_LOGON_FAILURE`).

---

# Failed Attack Paths

1. **AS-REP Roasting:**
   * *Attempt:* Executed `GetNPUsers.py` against discovered users on `192.168.122.10`.
   * *Result:* No accounts had pre-authentication disabled (`UF_DONT_REQUIRE_PREAUTH`), yielding zero AS-REP roastable hashes.
2. **Unauthenticated Kerberoasting:**
   * *Attempt:* Executed `GetUserSPNs.py` unauthenticated (null session).
   * *Result:* Failed due to Active Directory requiring authentication for SPN ticket requests.
3. **Constrained Delegation Abuse (`walter.white`):**
   * *Attempt:* Attempted to abuse constrained delegation configured for `walter.white` targeting `CIFS/captain.polaris.local` using `getST.py`.
   * *Result:* Failed with `KDC_ERR_PREAUTH_FAILED` (Kerberos pre-authentication failure for the account during S4U operations).
4. **Remote Administrative Execution & DCSync (`secretsdump.py` / `wmiexec.py`):**
   * *Attempt:* Attempted remote execution and DCSync secret extraction using `walter.white` and `hank.schrader` credentials against `CAPTAIN` and `MEMBER`.
   * *Result:* Failed with `STATUS_LOGON_FAILURE` and `WBEM_E_ACCESS_DENIED` due to lack of local/domain administrator privileges.

---

# Timeline of Compromise

* **2026-09-15 18:30:16:** Performed Kerberos user enumeration against `192.168.122.10`, discovering valid accounts (`saul.goodman`, `hank.schrader`, `skyler.white`).
* **2026-09-15 18:32:23:** Executed AS-REP roasting checks (no vulnerable accounts identified).
* **2026-09-15 18:33:05:** Executed Kerbrute password spraying, successfully identifying valid credentials for `skyler.white` and `hank.schrader`.
* **2026-09-15 18:33:14:** Performed authenticated Kerberoasting using `skyler.white:Password123`, extracting TGS hashes for service accounts.
* **2026-09-15 18:34:13:** Cracked Kerberoastable hashes using `hashcat`, recovering plaintext passwords for `walter.white` and `jesse.pinkman`.
* **2026-09-15 18:34:36:** Executed authenticated Active Directory enumeration (`GetADUsers.py`, `ldapdomaindump`, `ldapsearch`), discovering plaintext password hint in `saul.goodman` description attribute.
* **2026-09-15 18:35:00:** Performed delegation and SID enumeration (`findDelegation.py`, `lookupsid.py`), identifying Resource-Based Constrained Delegation rights for `saul.goodman` over `MEMBER$`.
* **2026-09-15 18:36:00:** Validated discovered and cracked credentials across domain shares and WMI services via `netexec` and `wmiexec`.
* **2026-09-15 18:37:36:** Attempted administrative secret extraction (`secretsdump.py`), which failed due to lack of administrative privileges.

---

# Assessment Statistics

* **Hosts Discovered:** 2 (`192.168.122.5`, `192.168.122.10`)
* **Hosts Compromised:** 2 (Authenticated access verified on both)
* **Accounts Discovered:** 13+ unique domain accounts
* **Accounts Compromised:** 5 (`skyler.white`, `hank.schrader`, `walter.white`, `jesse.pinkman`, `saul.goodman`)
* **Credentials Obtained:** 16 credential instances recorded / validated
* **Hashes Recovered:** 3 Kerberoastable TGS hashes (`jesse.pinkman`, `walter.white`, `saul.goodman`)
* **Kerberos Tickets Recovered:** TGS tickets for Kerberoastable accounts
* **Successful Attack Paths:** 4 major paths (User Enum -> Spraying -> Kerberoasting -> Cracking -> Attribute/Delegation Discovery)
* **Failed Attack Paths:** 4 paths (AS-REP Roasting, Unauthenticated Kerberoasting, S4U Delegation abuse, DCSync secret dumping)
* **Privilege Escalations:** 0 (Full Domain Administrator privilege escalation not achieved; standard user/service credential tier access demonstrated)
* **Lateral Movement Events:** Multiple successful SMB/WMI credential validation and session verification events across domain hosts.

---

# Recommendations

1. **Eliminate Stored Passwords in LDAP Attributes:**
   * Conduct an immediate audit of all Active Directory user and computer object attributes (such as `description`, `info`, and `comment`) to remove any plaintext or cleartext password hints. Enforce strict change management controls.
2. **Strengthen Service Account Password Complexity:**
   * Enforce robust password length and complexity requirements (minimum 25+ random characters) for all service accounts configured with Service Principal Names (SPNs) to mitigate offline Kerberoasting dictionary attacks.
3. **Implement Strong Password Policies and Monitoring:**
   * Enforce organization-wide complexity policies, disable predictable password patterns, and monitor authentication logs (Event ID 4625 / 4771) for indicators of password spraying and brute-force activity.
4. **Audit and Restrict Active Directory Delegation Settings:**
   * Review all accounts configured with Unconstrained Delegation (`CAPTAIN$`, `jesse.pinkman`), Constrained Delegation (`walter.white`), and Resource-Based Constrained Delegation (`saul.goodman` over `MEMBER$`). Migrate services to constrained delegation with protocol transition only when strictly necessary, or remove unneeded delegation permissions.
5. **Harden Network Share Permissions:**
   * Review Access Control Lists (ACLs) on sensitive SMB shares (such as `ImportantNotes` and `SharingIsCaring` on `CAPTAIN`) to ensure that write permissions are restricted strictly to authorized administrative groups rather than general domain users.