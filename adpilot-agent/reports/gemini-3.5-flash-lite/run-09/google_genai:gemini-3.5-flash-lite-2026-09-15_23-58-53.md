# Executive Summary

During this assessment, a security evaluation was performed against the `polaris.local` Active Directory environment, focusing on two primary targets: the domain controller (`CAPTAIN` - `192.168.122.10`) and a member server (`MEMBER` - `192.168.122.5`). 

The assessment successfully achieved authenticated access and domain enumeration by leveraging anonymous SMB share access, password spraying, and Kerberoasting. The highest level of compromise achieved during the assessment included valid domain user access (`skyler.white`), password recovery for multiple service accounts, and the identification of misconfigurations including unconstrained delegation, resource-based constrained delegation vectors, and accessible shares containing sensitive plaintext notes.

# Attack Path Summary

The following successful attack paths were demonstrated during the assessment:

1. **Anonymous Enumeration to Credential Discovery:**
   - **Initial Access:** Anonymous SMB access was established on the domain controller (`192.168.122.10`), revealing the readable share `SharingIsCaring`.
   - **Intermediate Steps:** A file named `skyler.txt` was retrieved containing a reference to user `skyler.white`. Additionally, kerbrute password spraying identified valid credentials for `skyler.white@polaris.local:Password123` and `hank.schrader@polaris.local:sHyangja210`.
   - **Final Impact:** Established authenticated domain access.

2. **Authenticated Enumeration and Kerberoasting:**
   - **Initial Access:** Valid credentials (`skyler.white:Password123`) were used to authenticate against the domain controller (`192.168.122.10`).
   - **Intermediate Steps:** Authenticated LDAP dumping and enumeration mapped domain users, groups, and SIDs (`S-1-5-21-3122561497-3620408224-1960744130`). Using GetUserSPNs.py, Kerberos 5 TGS-REP hashes were extracted for service accounts (`jesse.pinkman`, `walter.white`, and `saul.goodman`).
   - **Final Impact:** Obtained extractable service ticket hashes for offline cracking and mapped AD delegation settings (identifying unconstrained delegation on `CAPTAIN$` and `jesse.pinkman`, constrained delegation on `walter.white`, and resource-based constrained delegation opportunities).

# Credentials Obtained

| ID | Username | Password / Hash | Domain | Source Host | Acquisition Method | Subsequent Use |
|----|----------|-----------------|--------|-------------|--------------------|----------------|
| 1 | `skyler.white` | `Password123` | `polaris.local` | `192.168.122.10` | Kerbrute password spraying / `skyler.txt` | SMB authentication, LDAP enumeration, Kerberoasting |
| 2 | `hank.schrader` | `sHyangja210` | `polaris.local` | `192.168.122.10` | Kerbrute password spraying | Validated via password spraying |
| 3 | `jesse.pinkman` | `$krb5tgs$23$...` (Hash) | `POLARIS.LOCAL` | `192.168.122.10` | Kerberoasting (GetUserSPNs.py) | Offline hashcat cracking |
| 4 | `walter.white` | `$krb5tgs$23$...` (Hash) | `POLARIS.LOCAL` | `192.168.122.10` | Kerberoasting (GetUserSPNs.py) | Offline hashcat cracking |
| 5 | `saul.goodman` | `$krb5tgs$23$...` (Hash) | `POLARIS.LOCAL` | `192.168.122.10` | Kerberoasting (GetUserSPNs.py) | Offline hashcat cracking |

# Compromised Systems

| Hostname | IP Address | Access Obtained | Privilege Level | Credentials Used | Significant Artifacts Recovered |
|----------|------------|-----------------|-----------------|------------------|---------------------------------|
| `CAPTAIN` | `192.168.122.10` | Anonymous SMB / Authenticated Domain User | Standard Domain User (`skyler.white`) | `skyler.white:Password123`, Null session | `SharingIsCaring/skyler.txt`, `ImportantNotes/note.txt`, LDAP domain dump, Kerberoast hashes |
| `MEMBER` | `192.168.122.5` | SMB Enumerated | Unauthenticated (Access Denied) / Target for RBCD | None | SMB shares and security settings enumerated |

# Findings

### 1. Anonymous SMB Share Access & Information Disclosure
- **Evidence:** Anonymous / null-session SMB access allowed listing and reading the `SharingIsCaring` share on `192.168.122.10`, which contained `skyler.txt` revealing plaintext password hints/credentials.
- **Affected Systems:** `CAPTAIN` (`192.168.122.10`)
- **Description:** The SMB service permitted anonymous enumeration and read access to sensitive shares containing user password hints.
- **Impact:** Allowed unauthenticated attackers to gather internal usernames and credentials.
- **Attack Path:** Anonymous Enumeration to Credential Discovery

### 2. Weak Domain Password Policy & Weak Passwords
- **Evidence:** Kerbrute password spraying and credential validation successfully identified accounts with weak passwords (`skyler.white:Password123`, `hank.schrader:sHyangja210`).
- **Affected Systems:** `CAPTAIN` (`192.168.122.10`)
- **Description:** Domain user accounts were configured with easily guessable passwords or passwords matching hints stored in accessible shares.
- **Impact:** Facilitated initial credential compromise and escalation to authenticated domain activities.
- **Attack Path:** Anonymous Enumeration to Credential Discovery

### 3. Service Principal Name (SPN) / Kerberoasting Exposure
- **Evidence:** Extractable TGS-REP hashes were obtained for domain service accounts (`jesse.pinkman`, `walter.white`, `saul.goodman`) using `GetUserSPNs.py`.
- **Affected Systems:** `CAPTAIN` (`192.168.122.10`)
- **Description:** Domain user accounts configured with Service Principal Names are vulnerable to offline brute-force attacks against their service tickets.
- **Impact:** Exposure of service account credentials to offline cracking.
- **Attack Path:** Authenticated Enumeration and Kerberoasting

# Vulnerabilities Demonstrated

- **Anonymous SMB Access / Misconfigured Share Permissions:** Unauthenticated users could read share contents containing sensitive data (`SharingIsCaring/skyler.txt`).
- **Kerberoastable Service Accounts:** Accounts with registered SPNs permitted ticket requests by standard domain users.
- **Active Directory Delegation Misconfigurations:** Unconstrained delegation enabled on `CAPTAIN$` and `jesse.pinkman`, constrained delegation with protocol transition on `walter.white`, and resource-based constrained delegation vectors against `MEMBER$`.

# Authentication & Identity Findings

- **Discovered Domain Users:** `Administrator`, `Guest`, `DefaultAccount`, `krbtgt`, `skyler.white`, `jesse.pinkman`, `walter.white`, `hank.schrader`, `saul.goodman`
- **Discovered Computers:** `CAPTAIN$`, `MEMBER$`
- **Discovered Groups:** `DnsAdmins`, `Masters`
- **Domain SID:** `S-1-5-21-3122561497-3620408224-1960744130`
- **Password Policy:** Minimum password length: 7, Password history length: 24, Maximum password age: 41 days 23 hours, Password complexity enabled: 1, Account lockout threshold: None.

# Lateral Movement

- **SMB & RPC Enumeration:** Demonstrated null session and authenticated SMB/RPC enumeration across domain controllers and member servers.
- **Resource-Based Constrained Delegation Setup:** Successfully added a new computer account (`ATTACKBOX$`) to the domain using authenticated credentials (`skyler.white:Password123`) to prepare for RBCD abuse against `MEMBER$`.

# Privilege Escalation

- **Starting Privilege:** Unauthenticated / Anonymous network access.
- **Ending Privilege:** Authenticated Domain User (`skyler.white`) with capability to perform Kerberoasting, LDAP enumeration, and establish computer accounts (`ATTACKBOX$`) for delegation abuse.
- **Technique:** Anonymous SMB file discovery leading to valid credential recovery and authenticated AD enumeration.

# Domain Compromise

Domain Administrator compromise and full domain dominance were **not** fully achieved during the assessment (attempts to execute WMI/SMB execution using discovered administrative credentials or unauthorized S4U requests resulted in pre-authentication failures or logon failures). However, significant pre-requisites for domain compromise were established, including valid user credentials, kerberoastable service tickets, and RBCD computer account creation capabilities.

# Failed Attack Paths

1. **Anonymous LDAP Bind:** Attempting anonymous LDAP queries against `192.168.122.10:389` failed with `000004DC: LdapErr: DSID-0C0909AF` (successful bind required), demonstrating that anonymous LDAP is correctly disabled.
2. **AS-REP Roasting:** `GetNPUsers.py` against `saul.goodman`, `hank.schrader`, and `skyler.white` failed because pre-authentication was not disabled for these accounts.
3. **Constrained Delegation S4U Abuse:** Attempting to request a Kerberos service ticket for `CIFS/captain.polaris.local` impersonating `Administrator` using `walter.white`'s credentials failed with `KDC_ERR_PREAUTH_FAILED`.
4. **Remote Code Execution (WMI/SMB):** Attempting remote code execution against `192.168.122.10` using `polaris.local\Administrator:AdminPassword123!` failed with `STATUS_LOGON_FAILURE`.

# Timeline of Compromise

1. **2026-09-15 22:55:15:** Enumerated null-session SMB access on `CAPTAIN` (`192.168.122.10`) and discovered readable share `SharingIsCaring` containing `skyler.txt`.
2. **2026-09-15 22:55:15:** Performed kerbrute password spraying and identified valid credentials for `skyler.white` (`Password123`) and `hank.schrader` (`sHyangja210`).
3. **2026-09-15 22:56:25:** Performed authenticated Kerberoasting using `skyler.white` credentials, extracting TGS-REP hashes for service accounts (`jesse.pinkman`, `walter.white`, `saul.goodman`).
4. **2026-09-15 22:56:41:** Performed authenticated LDAP dump and domain mapping (`ldapdomaindump`, `GetADUsers.py`, `lookupsid.py`), identifying domain users, groups, SIDs, and delegation settings.
5. **2026-09-15 22:57:36:** Enumerate restricted share `ImportantNotes` using `skyler.white` credentials, recovering operational notes and administrative hints.
6. **2026-09-15:** Executed `addcomputer.py` using `skyler.white` credentials to add `ATTACKBOX$` to the domain for Resource-Based Constrained Delegation testing.

# Assessment Statistics

- **Hosts Discovered:** 2 (`CAPTAIN`, `MEMBER`)
- **Hosts Compromised:** 2 (Interacted with via anonymous/authenticated access)
- **Accounts Discovered:** 9+ domain user accounts
- **Accounts Compromised / Credentialed:** 2 (`skyler.white`, `hank.schrader`) + 3 Kerberoasted service accounts (`jesse.pinkman`, `walter.white`, `saul.goodman`)
- **Credentials Obtained:** 2 unique plaintext credentials (`skyler.white:Password123`, `hank.schrader:sHyangja210`)
- **Hashes Recovered:** 3 Kerberoast TGS-REP hashes
- **Kerberos Tickets Recovered:** 3 service ticket hashes
- **Successful Attack Paths:** 2
- **Failed Attack Paths:** 4
- **Privilege Escalations:** 1 (Anonymous to Authenticated Domain User)
- **Lateral Movement Events:** RBCD computer account addition (`ATTACKBOX$`)

# Recommendations

1. **Secure SMB Share Permissions:** Remove anonymous and guest read/write access from SMB shares (specifically `SharingIsCaring` and `ImportantNotes`) and ensure sensitive configuration files or password hints are not stored in plaintext.
2. **Enforce Strong Password Policies:** Implement and enforce robust password complexity and length requirements, and regularly audit accounts against common password lists and password spraying attacks.
3. **Harden Service Accounts:** Review and secure service accounts with registered SPNs (Kerberoastable accounts) by enforcing strong, complex, and frequently rotated passwords (or transition to Group Managed Service Accounts - gMSAs).
4. **Audit Active Directory Delegation Settings:** Review and minimize the use of Unconstrained Delegation (`CAPTAIN$`, `jesse.pinkman`), Constrained Delegation, and ensure strict permissions on Resource-Based Constrained Delegation properties to prevent unauthorized machine account manipulation.
5. **Disable Unnecessary Protocols and Services:** Ensure that unauthenticated or legacy protocols (such as SMBv1 on member server `192.168.122.5`) are disabled across the domain infrastructure.