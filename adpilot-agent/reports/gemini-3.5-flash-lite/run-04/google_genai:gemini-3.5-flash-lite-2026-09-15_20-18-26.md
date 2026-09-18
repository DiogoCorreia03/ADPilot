# Penetration Testing Report

## Executive Summary

An authorized penetration test was performed against the `polaris.local` Active Directory environment, encompassing domain infrastructure and member servers within the 192.168.122.0/24 subnet. The primary objective of the assessment was to evaluate the security posture of the domain, identify exploitable misconfigurations, and determine the feasibility of unauthorized access and privilege escalation.

During the assessment, multiple valid user accounts and service principal names (SPNs) were discovered and compromised. Password spraying against the Domain Controller (`192.168.122.10`) yielded valid credentials for standard domain users (`hank.schrader` and `skyler.white`). Subsequent Kerberoasting against discovered service accounts allowed for the offline recovery of plaintext passwords for service accounts (`walter.white` and `jesse.pinkman`). Enumeration of Active Directory configurations revealed unconstrained delegation, constrained delegation, and resource-based constrained delegation misconfigurations, as well as publicly accessible file shares containing sensitive data and active Microsoft SQL Server database instances. 

While full Domain Administrator privileges were not achieved via successful domain-wide elevation or DCSync, multiple accounts, service principals, and network services were successfully compromised, demonstrating significant risk to internal data confidentiality and service integrity.

---

## Attack Path Summary

1. **Password Spraying and Credential Discovery Path:**
   * **Initial Access:** Enumerated valid domain usernames using Kerbrute (`skyler.white`, `hank.schrader`, `saul.goodman`).
   * **Credential Acquisition:** Performed password spraying against the Domain Controller, successfully obtaining valid credentials for `hank.schrader` (`sHyangja210`) and `skyler.white` (`Password123`).
   * **Privilege & Service Enumeration:** Utilized `hank.schrader`'s credentials to query Active Directory via LDAP, execute `lookupsid.py`, and enumerate accessible SMB shares (`ImportantNotes`, `SharingIsCaring`).

2. **Kerberoasting and Service Account Compromise Path:**
   * **Service Principal Enumeration:** Using valid user credentials (`hank.schrader`), requested service tickets (TGS) for SPNs registered across the domain (`HOST/jesse.pinkman.polaris.local`, `HTTP/walter.white.polaris.local`, `HOST/saul.goodman.polaris.local`).
   * **Offline Hash Cracking:** Performed offline password cracking (hashcat mode 13100) against recovered Kerberoast hashes.
   * **Credential Acquisition:** Successfully cracked passwords for service accounts `jesse.pinkman` (`Wang0Tang0!`) and `walter.white` (`Metho1o590oA$elry`).

3. **Resource-Based Constrained Delegation (RBCD) Preparation Path:**
   * **Delegation Enumeration:** Identified resource-based constrained delegation misconfigurations configured on `saul.goodman` pointing toward `MEMBER$`.
   * **Computer Account Creation:** Utilized valid credentials for `saul.goodman` via Impacket's `addcomputer.py` to create a new machine account (`ATTACKBOX$`) in preparation for RBCD abuse.

---

## Credentials Obtained

| ID | Username | Password | Domain | Source Host / Acquisition Method | Subsequent Use |
|---|---|---|---|---|---|
| 1 | `hank.schrader` | `sHyangja210` | *(Blank)* | Discovered via Kerbrute password spraying against `polaris.local` | LDAP queries, SMB share access, SQL Server enumeration |
| 2 | `skyler.white` | `Password123` | *(Blank)* | Discovered via Kerbrute password spraying against `polaris.local` | None demonstrated |
| 3 | `walter.white` | `Metho1o590oA$elry` | `POLARIS.LOCAL` | Kerberoasted service account ticket cracked via hashcat | Attempted S4U2Proxy delegation abuse |
| 4 | `jesse.pinkman` | `Wang0Tang0!` | `POLARIS.LOCAL` | Kerberoasted service account ticket cracked via hashcat | None demonstrated |
| 5 | `hank.schrader` | `sHyangja210` | `polaris.local` | Obtained from task context/evidence | Active Directory enumeration |
| 6 | `hank.schrader` | `sHyangja210` | `polaris.local` | Enumerated via `ldapsearch` | Domain group and user mapping |
| 7 | `hank.schrader` | `sHyangja210` | `polaris.local` | Discovered during `lookupsid.py` enumeration | SID translation |
| 8 | `hank.schrader` | `sHyangja210` | `polaris.local` | Obtained from task 3.1 enumeration | SMB share access |
| 9 | `hank.schrader` | `sHyangja210` | *(Blank)* | Valid credentials for Microsoft SQL Server enumeration | Database service enumeration |

---

## Compromised Systems

| Hostname | IP Address | Access Obtained | Privilege Level | Credentials Used | Significant Artifacts Recovered |
|---|---|---|---|---|---|
| `CAPTAIN` (Domain Controller) | `192.168.122.10` | Authenticated network access (SMB, LDAP, MSSQL) | Standard Domain User (`hank.schrader`) | `hank.schrader:sHyangja210` | Accessible shares (`ImportantNotes`, `SharingIsCaring`), SQL databases (`master`, `model`, `msdb`, `tempdb`), SPN tickets |
| `MEMBER` | `192.168.122.5` | Target for Resource-Based Constrained Delegation | Unauthenticated / Restricted | N/A | Target machine account (`MEMBER$`) identified for RBCD |

---

## Findings

### 1. Weak Domain Password Policies and Password Spraying Vulnerability
* **Evidence:** Successful authentication via Kerbrute password spraying for `hank.schrader` (`sHyangja210`) and `skyler.white` (`Password123`).
* **Affected Systems:** `192.168.122.10` (`polaris.local`)
* **Description:** The domain permits weak passwords that align with standard common-password dictionaries, enabling attackers to perform high-speed password spraying against domain user accounts without triggering immediate account lockouts.
* **Impact:** Unauthorized access to domain user accounts, laying the groundwork for further internal reconnaissance and privilege escalation.
* **Attack Path:** Password Spraying and Credential Discovery Path.

### 2. Kerberoastable Service Principal Names (SPNs)
* **Evidence:** Retrieval of service tickets via `GetUserSPNs.py` for `HOST/jesse.pinkman.polaris.local`, `HTTP/walter.white.polaris.local`, and `HOST/saul.goodman.polaris.local`, followed by successful offline password cracking.
* **Affected Systems:** `192.168.122.10` (`polaris.local`)
* **Description:** Domain user accounts configured with Service Principal Names (SPNs) utilize weak passwords that can be requested by any authenticated domain user and cracked offline via brute-force dictionary attacks.
* **Impact:** Exposure of plaintext service account credentials (`jesse.pinkman`, `walter.white`), leading to potential lateral movement or delegation abuse.
* **Attack Path:** Kerberoasting and Service Account Compromise Path.

### 3. Unencrypted SMB Shares with Read/Write Permissions
* **Evidence:** Successful connection via `smbclient` to `ImportantNotes` and `SharingIsCaring` shares on `192.168.122.10` using `hank.schrader` credentials, revealing read/write access.
* **Affected Systems:** `192.168.122.10` (`polaris.local`)
* **Description:** Domain file shares are configured with overly permissive access controls allowing standard domain users read and write access to sensitive repositories.
* **Impact:** Risk of unauthorized data modification, file tampering, or sensitive data exfiltration.
* **Attack Path:** Password Spraying and Credential Discovery Path / File Share Abuse.

### 4. Risky Active Directory Delegation Configurations
* **Evidence:** Output of `findDelegation.py` showing `CAPTAIN$` and `jesse.pinkman` with unconstrained delegation, `walter.white` with constrained delegation with protocol transition, and `saul.goodman` with resource-based constrained delegation to `MEMBER$`.* **Affected Systems:** `192.168.122.10` (`polaris.local`), `192.168.122.5` (`member.polaris.local`)
* **Description:** Active Directory contains permissive delegation settings that allow users/computers to impersonate other users or delegate authentication across services.
* **Impact:** Potential complete domain compromise if delegation paths are successfully triggered.
* **Attack Path:** Resource-Based Constrained Delegation Preparation Path.

---

## Vulnerabilities Demonstrated

* **Weak User Passwords:** Accounts configured with easily guessable passwords (`Password123`, `sHyangja210`, `Wang0Tang0!`, `Metho1o590oA$elry`).
* **Kerberoasting (Service Principal Weak Authentication):** Service accounts mapped to weak passwords permitting offline brute-forcing of TGS-REP tickets.
* **Overly Permissive SMB Share Access:** Standard domain users granted read/write privileges on sensitive file shares (`ImportantNotes`, `SharingIsCaring`).
* **Insecure Delegation Settings:** Unconstrained delegation, constrained delegation, and resource-based constrained delegation assignments across user and computer objects.

---

## Authentication & Identity Findings

* **Discovered Users:** `Administrator`, `Guest`, `DefaultAccount`, `krbtgt`, `skyler.white`, `jesse.pinkman`, `walter.white`, `hank.schrader`, `saul.goodman`, `CAPTAIN$`, `MEMBER$`.
* **Privileged Groups Identified:** `Administrators`, `Domain Admins`, `Enterprise Admins`, `Masters`, `DnsAdmins`.
* **Service Accounts:** `jesse.pinkman`, `walter.white`, `saul.goodman`.
* **Guest / Anonymous Access:** Anonymous LDAP connection permitted (though search requests fail with `operationsError`); SMB null sessions return `STATUS_ACCESS_DENIED`.

---

## Lateral Movement

* **SMB Share Interaction:** Authenticated to SMB shares on the Domain Controller (`192.168.122.10`) using valid user credentials (`hank.schrader`).
* **Microsoft SQL Server:** Authenticated successfully to Microsoft SQL Server on port 1433 using valid user credentials (`hank.schrader`).

---

## Privilege Escalation

* **Starting Privilege:** Unauthenticated network access.
* **Ending Privilege:** Standard Domain User (`hank.schrader`, `skyler.white`) and compromised Service Account privileges (`jesse.pinkman`, `walter.white`).
* **Technique:** Kerbrute password spraying and Kerberoasting followed by offline hash cracking.

---

## Domain Compromise

* **Domain Administrator Compromise:** Not achieved.
* **DCSync:** Not performed / not authorized due to lack of Domain Administrator privileges.
* **KRBTGT Compromise:** Not achieved.
* **Assessment Conclusion:** While multiple service accounts and standard user credentials were compromised, domain dominance (Domain Administrator / DCSync capability) was not reached during the assessment window.

---

## Failed Attack Paths

1. **AS-REP Roasting:** `GetNPUsers.py` was executed against all discovered users (`skyler.white`, `hank.schrader`, `saul.goodman`). No accounts had "Do not require Kerberos preauthentication" enabled, resulting in no hashes retrieved.
2. **Kerberos Constrained Delegation Abuse (S4U2Proxy):** Attempted to request a service ticket using Impacket's `getST.py` for `walter.white` to impersonate the Domain Administrator against `cifs/captain.polaris.local`. The attempt failed with `KDC_ERR_PREAUTH_FAILED` (Pre-authentication information was invalid).
3. **SMB Authentication to Member Server:** Authentication attempts against member server `192.168.122.5` (`MEMBER`) using `hank.schrader` failed with `STATUS_NO_LOGON_SERVERS`.

---

## Timeline of Compromise

1. **Reconnaissance:** Enumerated SMB, LDAP, Microsoft SQL Server, and DNS services on `192.168.122.10` and `192.168.122.5`.
2. **User Discovery:** Performed Kerberos user enumeration (`kerbrute`), discovering valid user accounts (`skyler.white`, `hank.schrader`, `saul.goodman`).
3. **Credential Harvesting:** Executed password spraying against the Domain Controller, successfully obtaining valid credentials for `hank.schrader` and `skyler.white`.
4. **Domain Enumeration:** Used `hank.schrader` credentials to enumerate Active Directory users, groups, SIDs, delegation settings, and accessible SMB shares (`ImportantNotes`, `SharingIsCaring`).
5. **Kerberoasting:** Enumerated Kerberoastable service accounts and retrieved TGS tickets for `jesse.pinkman`, `walter.white`, and `saul.goodman`.
6. **Credential Cracking:** Cracked Kerberoast tickets via hashcat, recovering plaintext passwords for `jesse.pinkman` and `walter.white`.
7. **Delegation Abuse Preparation:** Utilized `saul.goodman` credentials to create a new computer account (`ATTACKBOX$`) in preparation for Resource-Based Constrained Delegation abuse against `MEMBER$`.
8. **Database Enumeration:** Connected to Microsoft SQL Server on port 1433 using `hank.schrader` credentials to inspect accessible databases.

---

## Assessment Statistics

* **Hosts Discovered:** 2 (`192.168.122.10`, `192.168.122.5`)
* **Hosts Compromised:** 1 (`192.168.122.10` - Authenticated Access)
* **Accounts Discovered:** 11 (including computer accounts)
* **Accounts Compromised:** 4 (`hank.schrader`, `skyler.white`, `walter.white`, `jesse.pinkman`)
* **Credentials Obtained:** 9 credential instances (across 4 unique user/service accounts)
* **Hashes Recovered:** 3 Kerberoast service tickets
* **Kerberos Tickets Recovered:** 3 TGS tickets
* **Successful Attack Paths:** 3 (Password Spraying, Kerberoasting, RBCD Preparation)
* **Failed Attack Paths:** 3 (AS-REP Roasting, S4U2Proxy Delegation Abuse, Member Server SMB Login)
* **Privilege Escalations:** Standard user credential acquisition and service account credential recovery
* **Lateral Movement Events:** 2 (SMB share access and MSSQL authentication)

---

## Recommendations

1. **Enforce Strong Password Policies:**
   * Implement and enforce complex password requirements and minimum length policies across the domain to prevent successful password spraying and dictionary attacks.
   * Prohibit the use of weak, common passwords.

2. **Harden Service Accounts (Kerberoasting Mitigation):**
   * Review all accounts configured with Service Principal Names (SPNs). Ensure service accounts utilize strong, complex passwords (125+ characters) or transition to Group Managed Service Accounts (gMSAs) where supported.

3. **Review and Restrict File Share Permissions:**
   * Audit SMB share permissions on `ImportantNotes` and `SharingIsCaring`. Remove write and read access for standard domain users where business justification does not exist.

4. **Audit and Clean Up Active Directory Delegation:**
   * Review accounts configured with unconstrained delegation (`CAPTAIN$`, `jesse.pinkman`), constrained delegation (`walter.white`), and resource-based constrained delegation (`saul.goodman`). Remove unnecessary delegation rights to prevent potential escalation vectors.

5. **Monitor Authentication and Network Logs:**
   * Implement monitoring for anomalous authentication patterns, such as high volumes of Kerberos TGS requests (Kerberoasting) or rapid failed/successful login attempts from single source IPs (password spraying).