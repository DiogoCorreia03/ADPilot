# Executive Summary

An authorized penetration testing assessment was conducted against the `polaris.local` Active Directory environment, encompassing two primary targets: the Domain Controller `CAPTAIN` (`192.168.122.10`), running Windows Server 2016, and the member server `MEMBER` (`192.168.122.5`), also running Windows Server 2016. 

The primary objective of the assessment was to evaluate the security posture of the domain, identify reachable attack surfaces, and determine the feasibility of privilege escalation and lateral movement. Through a combination of unauthenticated enumeration, password spraying, Kerberoasting, and delegation analysis, the assessment successfully identified critical Active Directory misconfigurations. 

The assessment achieved significant access, compromising multiple domain user accounts, recovering valid credentials, and identifying high-value delegation misconfigurations (such as Resource-Based Constrained Delegation and Unconstrained Delegation). A total of 2 hosts were evaluated, 2 hosts exhibited vulnerabilities, 3 valid user accounts were compromised through spraying, and 2 service account hashes were successfully cracked.

---

# Attack Path Summary

The assessment demonstrated the following successful attack path leading from initial unauthenticated reconnaissance to authenticated domain credential harvesting and delegation mapping:

1. **Reconnaissance & User Enumeration**: Unauthenticated enumeration against the Domain Controller (`192.168.122.10`) via `kerbrute` using a potential users wordlist successfully identified valid domain accounts: `saul.goodman`, `skyler.white`, and `hank.schrader`.
2. **Password Spraying & Credential Harvesting**: Password spraying against the discovered accounts yielded valid credentials for `skyler.white` (`Password123`) and `hank.schrader` (`sHyangja210`).
3. **Authenticated Enumeration & Kerberoasting**: Using the valid credentials of `skyler.white`, comprehensive Active Directory enumeration was performed. This revealed domain users, group memberships, and Service Principal Names (SPNs). Kerberoasting against the domain identified three roastable service accounts (`jesse.pinkman`, `walter.white`, and `saul.goodman`).
4. **Credential Recovery via Hash Cracking**: Kerberoasting ticket hashes were cracked using `hashcat` and the `rockyou.txt` wordlist, recovering plaintext passwords for `jesse.pinkman` (`Wang0Tang0!`) and `walter.white` (`Metho1o590oA$elry`).
5. **Delegation Analysis**: Enumeration of Active Directory delegation configurations revealed multiple high-risk settings: unconstrained delegation on computer `CAPTAIN$` and user `jesse.pinkman`, constrained delegation with protocol transition on `walter.white`, and Resource-Based Constrained Delegation (RBCD) on `saul.goodman` permitting management of the member server account `MEMBER$`.

---

# Credentials Obtained

All credentials discovered, recovered, or validated during the assessment are detailed below:

| Username | Password | NTLM Hash / Ticket | Source Host | Acquisition Method | Subsequent Use |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `skyler.white` | `Password123` | - | `polaris.local` (192.168.122.10) | Kerbrute Password Spraying | Authenticated AD enumeration, SMB share access, MSSQL enumeration |
| `hank.schrader` | `sHyangja210` | - | `polaris.local` (192.168.122.10) | Kerbrute Password Spraying | None |
| `walter.white` | `Metho1o590oA$elry` | Kerberoast Hash | `polaris.local` (192.168.122.10) | Kerberoasting & Hashcat Cracking | Authentication / Delegation analysis |
| `jesse.pinkman` | `Wang0Tang0!` | Kerberoast Hash | `polaris.local` (192.168.122.10) | Kerberoasting & Hashcat Cracking | Authentication / Delegation analysis |
| `saul.goodman` | - | Kerberoast Hash | `polaris.local` (192.168.122.10) | Kerberoasting / Delegation mapping | RBCD configuration mapping against `MEMBER$` |

---

# Compromised Systems

| Hostname | IP Address | Access Obtained | Privilege Level | Credentials Used | Significant Artifacts Recovered |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CAPTAIN` | `192.168.122.10` | Authenticated Domain Access & Share Read/Write | Domain User (`skyler.white`), SQL User (Impersonation capability to `sa`) | `skyler.white:Password123` | Accessible SMB shares (`ImportantNotes`, `SharingIsCaring`), AD users/groups, SPNs, delegation configurations |
| `MEMBER` | `192.168.122.5` | Target of RBCD from `saul.goodman` | Member Server | `saul.goodman` (Managed via RBCD) | Target machine account for delegation abuse |

---

# Findings

### 1. Weak Domain Password Policy Leading to Account Compromise
* **Evidence**: Valid credentials were recovered for `skyler.white` (`Password123`) and `hank.schrader` (`sHyangja210`) via password spraying.
* **Affected Systems**: `polaris.local` (192.168.122.10)
* **Description**: The domain permits weak user passwords that match common wordlist entries, allowing automated password spraying attacks to successfully compromise multiple accounts.
* **Impact**: Unauthorized access to domain user privileges, enabling internal enumeration and further attack path progression.
* **Attack Path**: Password Spraying -> Credential Harvesting -> Authenticated Enumeration.

### 2. Kerberoastable Service Principal Names (SPNs)
* **Evidence**: Service tickets were requested and extracted for `jesse.pinkman`, `walter.white`, and `saul.goodman`. Plaintext passwords were subsequently cracked for `jesse.pinkman` (`Wang0Tang0!`) and `walter.white` (`Metho1o590oA$elry`).
* **Affected Systems**: `polaris.local` (192.168.122.10)
* **Description**: Domain user accounts configured with Service Principal Names (SPNs) utilize weak passwords that can be requested by any authenticated domain user and brute-forced offline.
* **Impact**: Compromise of service account credentials and potential escalation paths depending on account privileges.
* **Attack Path**: Authenticated Enumeration -> Kerberoasting -> Offline Hash Cracking.

### 3. High-Risk Active Directory Delegation Configurations
* **Evidence**: `findDelegation.py` identified unconstrained delegation on `CAPTAIN$` and `jesse.pinkman`, constrained delegation with protocol transition on `walter.white`, and Resource-Based Constrained Delegation (RBCD) granting `saul.goodman` control over `MEMBER$`.
* **Affected Systems**: `polaris.local` (192.168.122.10), `member.polaris.local` (192.168.122.5)
* **Description**: Excessive trust and delegation rights are assigned to computer and user objects within the domain.
* **Impact**: Potential ticket-granting abuse, impersonation of arbitrary users, and unauthorized control of member servers from domain user contexts.
* **Attack Path**: Authenticated Delegation Enumeration -> Delegation Abuse.

---

# Vulnerabilities Demonstrated

* **Weak Password Policies / Password Spraying Vulnerability**: Demonstrated via `kerbrute` password spraying against `polaris.local`, resulting in valid credentials for `skyler.white` and `hank.schrader`.
* **Kerberoasting**: Demonstrated via `GetUserSPNs.py` and `hashcat` (mode 13100), recovering passwords for `jesse.pinkman` and `walter.white`.
* **Insecure Active Directory Delegation**: Demonstrated via `findDelegation.py`, identifying unconstrained delegation, protocol transition, and Resource-Based Constrained Delegation configurations.

---

# Authentication & Identity Findings

* **Discovered Users**: `saul.goodman`, `skyler.white`, `hank.schrader`, `jesse.pinkman`, `walter.white`, `Administrator`, `Guest`, `DefaultAccount`, `krbtgt`.
* **Service Accounts / Kerberoastable Accounts**: `jesse.pinkman`, `walter.white`, `saul.goodman`.
* **Delegation Findings**:
  * `CAPTAIN$` (Computer) - Unconstrained Delegation
  * `jesse.pinkman` (Person) - Unconstrained Delegation
  * `walter.white` (Person) - Constrained Delegation with Protocol Transition to `CIFS/captain.polaris.local`
  * `saul.goodman` (Person) - Resource-Based Constrained Delegation to `MEMBER$`

---

# Lateral Movement

* Demonstrated lateral movement planning and mapping via Resource-Based Constrained Delegation where `saul.goodman` holds management rights over the `MEMBER$` computer account.
* Authenticated SMB share discovery and access achieved on the Domain Controller (`CAPTAIN`) using `skyler.white` credentials, exposing readable/writable shares (`ImportantNotes`, `SharingIsCaring`).

---

# Privilege Escalation

* **Database Impersonation Mapping**: Enumeration of MSSQL on `CAPTAIN` revealed that domain user `skyler.white` possesses permissions to impersonate the `sa` (sysadmin) role within the database context, though direct OS command execution via `xp_cmdshell` was constrained by server-level role membership (`IS_SRVROLEMEMBER('sysadmin') = 0`).
* **Credential Escalation**: Escalated access from unauthenticated enumeration to valid domain user credentials (`skyler.white`), followed by offline cracking of service account credentials (`jesse.pinkman`, `walter.white`).

---

# Domain Compromise

Full Domain Administrator compromise (DCSync / NTDS.DIT extraction) was **not achieved** during this assessment. Attempts to extract the `NTDS.DIT` database using `secretsdump.py` with compromised non-admin accounts (`jesse.pinkman`, `skyler.white`, `walter.white`) failed due to insufficient privileges (`rpc_s_access_denied` / `ERROR_DS_DRA_BAD_DN`).

---

# Failed Attack Paths

* **Anonymous SMB Share Enumeration**: Failed on both `CAPTAIN` and `MEMBER` with `STATUS_ACCESS_DENIED`, confirming proper restrictions on anonymous share browsing.
* **AS-REP Roasting**: Tested against discovered users (`saul.goodman`, `skyler.white`, `hank.schrader`), but failed as accounts did not have pre-authentication disabled (`UF_DONT_REQUIRE_PREAUTH` not set).
* **MSSQL OS Command Execution**: Attempted command execution on `CAPTAIN` via MSSQL impersonation using `skyler.white`, but failed because the user lacked the `sysadmin` server role and permissions to run `RECONFIGURE` or `xp_cmdshell`.
* **Constrained Delegation Ticket Generation (`getST.py`)**: Attempted to request a service ticket for `walter.white` to impersonate `Administrator` via protocol transition, which failed due to principal lookup errors (`KDC_ERR_S_PRINCIPAL_UNKNOWN`).
* **NTDS.DIT Secret Dumping**: Attempted domain secret extraction via `secretsdump.py` using non-administrative credentials (`jesse.pinkman`, `skyler.white`, `walter.white`), which failed due to lack of replication/administrator privileges.

---

# Timeline of Compromise

1. **Service Characterization**: Characterized SMB, LDAP, MSSQL, and web services across `CAPTAIN` (`192.168.122.10`) and `MEMBER` (`192.168.122.5`).
2. **User Enumeration**: Performed Kerberos user enumeration via `kerbrute`, discovering valid accounts (`saul.goodman`, `skyler.white`, `hank.schrader`).
3. **Password Spraying**: Executed password spraying against `polaris.local`, recovering valid credentials for `skyler.white` (`Password123`) and `hank.schrader` (`sHyangja210`).
4. **Authenticated AD Enumeration**: Used `skyler.white` credentials to enumerate domain users, groups, SIDs, and SPNs.
5. **Kerberoasting & Cracking**: Extracted Kerberoastable service tickets for `jesse.pinkman`, `walter.white`, and `saul.goodman`, and cracked hashes via `hashcat` to recover plaintext passwords (`Wang0Tang0!`, `Metho1o590oA$elry`).
6. **Delegation Analysis**: Mapped domain delegation configurations, uncovering unconstrained delegation, protocol transition, and RBCD attack paths.
7. **Share & Database Enumeration**: Performed authenticated SMB share enumeration and MSSQL permission checks on the Domain Controller.

---

# Assessment Statistics

* **Hosts Discovered**: 2
* **Hosts Compromised (Authenticated Access)**: 2 (`CAPTAIN`, `MEMBER` via delegation mapping)
* **Accounts Discovered**: 9+
* **Accounts Compromised**: 5 (`skyler.white`, `hank.schrader`, `jesse.pinkman`, `walter.white`, `saul.goodman`)
* **Credentials Obtained**: 5 unique active credentials
* **Hashes Recovered**: 3 Kerberoast service hashes
* **Kerberos Tickets Recovered**: 3
* **Successful Attack Paths**: Reconnaissance -> Password Spraying -> Authenticated Enumeration -> Kerberoasting -> Credential Cracking -> Delegation Mapping
* **Failed Attack Paths**: 6 (Anonymous shares, AS-REP roasting, MSSQL cmd exec, direct `getST.py` abuse, non-admin secretsdump)
* **Privilege Escalations**: Database impersonation analysis and service credential recovery
* **Lateral Movement Events**: RBCD trust mapping to member server

---

# Recommendations

1. **Enforce Strong Password Policies**: Implement and enforce complex password requirements and regular password rotation to prevent successful password spraying attacks (as demonstrated with `skyler.white` and `hank.schrader`).
2. **Harden Service Accounts (Kerberoasting Mitigation)**: Review accounts configured with Service Principal Names (SPNs). Ensure service accounts utilize strong, long, and complex passwords (125+ characters) or migrate to Group Managed Service Accounts (gMSAs) where applicable.
3. **Audit and Restrict Active Directory Delegation**:
   * Remove unconstrained delegation from computer and user objects (`CAPTAIN$`, `jesse.pinkman`) unless strictly required.
   * Review and restrict constrained delegation and Resource-Based Constrained Delegation (RBCD) permissions to prevent unauthorized host control (e.g., `saul.goodman` managing `MEMBER$`).
4. **Review Database Permissions**: Audit SQL Server login mappings and role assignments to ensure non-administrative domain users cannot impersonate privileged roles such as `sa`.
5. **Implement Monitoring and Logging**: Enable advanced auditing for Kerberos ticket requests (Event ID 4769), unusual service ticket requests, and delegation modifications to detect lateral movement and reconnaissance attempts early.