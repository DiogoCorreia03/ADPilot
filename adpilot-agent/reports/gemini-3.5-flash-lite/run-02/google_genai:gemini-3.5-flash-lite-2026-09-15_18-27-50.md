# Executive Summary

An external and internal penetration testing assessment was performed against the Windows Active Directory domain `polaris.local` (Domain Controller `CAPTAIN` at `192.168.122.10`, and member server `MEMBER` at `192.168.122.5`). The primary objective of the assessment was to evaluate the security posture of the domain, identify accessible services and misconfigurations, and determine the feasibility of privilege escalation and domain compromise.

Through a combination of anonymous enumeration, SMB information leakage, password spraying, Kerberoasting, and Active Directory permission analysis, the assessment achieved significant penetration of the target environment. A total of **2 hosts** were identified, with **1 host (`CAPTAIN`)** successfully accessed. **15 credentials/accounts** were discovered or recovered, of which valid domain user credentials and cracked service account passwords were successfully leveraged to authenticate against domain services and perform Kerberoasting.

### Key Metrics:
- **Scope:** `polaris.local` (`192.168.122.10`, `192.168.122.5`)
- **Hosts Compromised:** 1 (`CAPTAIN`)
- **Accounts Compromised:** 5 (`skyler.white`, `hank.schrader`, `jesse.pinkman`, `walter.white`, `saul.goodman`)
- **Highest Level of Compromise:** Authenticated Domain User & Kerberoasting Vector Exploitation (Access to multiple user service tickets and unconstrained delegation paths).

---

# Attack Path Summary

The primary successful attack path demonstrated during the assessment followed these chronological phases:

1. **Information Leakage via Anonymous SMB:** Anonymous enumeration of SMB shares on the Domain Controller (`192.168.122.10`) revealed the `SharingIsCaring` share containing a plaintext note disclosing user credentials (`skyler.white:Password123`).
2. **Credential Verification & Initial Access:** The discovered credential for `skyler.white` was verified against SMB, LDAP, Kerberos, and MSSQL services, granting authenticated domain access.
3. **Active Directory Enumeration & Kerberoasting:** Authenticated access via `skyler.white` enabled full enumeration of domain users, groups, and SPNs. Executing Kerberoasting (`GetUserSPNs.py`) extracted service tickets for `jesse.pinkman`, `walter.white`, and `saul.goodman`.
4. **Offline Hash Cracking:** Offline brute-forcing of the extracted Kerberoasting hashes using Hashcat and the `rockyou.txt` wordlist successfully recovered plaintext passwords for `jesse.pinkman` (`Wang0Tang0!`) and `walter.white` (`Metho1o590oA$elry`).
5. **Delegation Analysis:** Analysis of Active Directory delegation settings revealed that `CAPTAIN$` and `jesse.pinkman` possessed unconstrained delegation, and `walter.white` possessed constrained delegation with protocol transition.

---

# Credentials Obtained

All valid credentials discovered, recovered, or cracked during the assessment are detailed below:

| ID | Username | Password / Hash | Source Host | Acquisition Method | Subsequent Use / Validated Service |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `skyler.white` | (N/A - Username) | `192.168.122.10` | Kerbrute User Enumeration | Enumerated valid domain user |
| 2 | `saul.goodman` | (N/A - Username) | `192.168.122.10` | Kerbrute User Enumeration | Enumerated valid domain user |
| 3 | `hank.schrader` | (N/A - Username) | `192.168.122.10` | Kerbrute User Enumeration | Enumerated valid domain user |
| 4 | `hank.schrader` | `sHyangja210` | `192.168.122.10` | Kerbrute Password Spray | Validated via MSSQL / Domain services |
| 5 | `skyler.white` | `Password123` | `192.168.122.10` | Kerbrute Password Spray | Authenticated domain services / SMB / MSSQL |
| 6 | `skyler.white` | `Password123` | `192.168.122.10` | SMB Share Note (`SharingIsCaring`) | Confirmed valid account password |
| 7 | `jesse.pinkman` | `Wang0Tang0!` | `192.168.122.10` | Kerberoasting & Hashcat (`rockyou.txt`) | Recovered service account password |
| 8 | `walter.white` | `Metho1o590oA$elry` | `192.168.122.10` | Kerberoasting & Hashcat (`rockyou.txt`) | Recovered service account password |

---

# Compromised Systems

| Hostname | IP Address | OS / Service | Access Level Achieved | Credentials Used | Recovered Artifacts |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CAPTAIN` | `192.168.122.10` | Windows Server 2016 Standard / IIS, SMB, LDAP, Kerberos, MSSQL | Authenticated User / Database Access / Unconstrained Delegation | `skyler.white:Password123`, `hank.schrader:sHyangja210` | SMB shares (`SharingIsCaring`, `ImportantNotes`), AD domain database dump, Kerberoastable tickets |
| `MEMBER` | `192.168.122.5` | Windows Server 2016 Standard / IIS | Enumerated (Access Restricted) | None | Default IIS welcome page |

---

# Findings

### 1. Anonymous SMB Read Access and Sensitive Data Exposure
- **Evidence:** Anonymous/Null session login successfully permitted listing of SMB shares on `192.168.122.10`. Access to the `SharingIsCaring` share revealed a file (`skyler.txt`) containing plaintext credentials: *"Hey Skyler. I've changed your password to something really easy to remember this time. I hope you won't forget this one, I'm tired of this. Love, admin."* (`skyler.white:Password123`).
- **Affected Systems:** `192.168.122.10` (`CAPTAIN`)
- **Description:** Anonymous SMB connections allowed unauthenticated users to read directory shares and recover sensitive operational notes containing plaintext user credentials.
- **Impact:** Direct compromise of user `skyler.white`, providing initial authenticated access to the Active Directory domain.
- **Attack Path:** Information Leakage via Anonymous SMB -> Credential Discovery -> Authenticated Domain Access.

### 2. Weak User Account Passwords & Kerberoastable Service Accounts
- **Evidence:** Running Impacket's `GetUserSPNs.py` against `polaris.local` identified multiple accounts with Service Principal Names (SPNs), including `jesse.pinkman`, `walter.white`, and `saul.goodman`. Cracking the extracted ticket hashes using Hashcat (mode 13100) and `rockyou.txt` successfully recovered weak plaintext passwords (`Wang0Tang0!` and `Metho1o590oA$elry`).
- **Affected Systems:** `192.168.122.10` (`CAPTAIN`)
- **Description:** Service accounts assigned weak passwords generated Kerberos service tickets that could be requested by any authenticated domain user and subsequently cracked offline.
- **Impact:** Exposure of service account credentials, leading to broader access and potential lateral movement vectors.
- **Attack Path:** Kerberoasting -> Hashcat Brute-Forcing -> Service Account Credential Recovery.

### 3. Unconstrained Kerberos Delegation
- **Evidence:** Impacket's `findDelegation.py` identified that the computer object `CAPTAIN$` and user account `jesse.pinkman` are configured with unconstrained delegation.
- **Affected Systems:** `192.168.122.10` (`CAPTAIN`)
- **Description:** Accounts configured with unconstrained delegation cause the Kerberos Key Distribution Center (KDC) to cache Service Granting Tickets (TGTs) of users authenticating to them in memory.
- **Impact:** If an administrative user interacts with a service running under unconstrained delegation, their TGT can be captured and reused to impersonate them across the domain.
- **Attack Path:** Active Directory Delegation Enumeration -> Unconstrained Delegation Identification.

---

# Vulnerabilities Demonstrated

- **SMB Anonymous Share Enumeration:** Unauthenticated access to file shares containing plaintext credentials.
- **Weak Domain Password Policies:** Service accounts (`jesse.pinkman`, `walter.white`) protected by weak passwords vulnerable to offline dictionary cracking (Kerberoasting).
- **Unconstrained Kerberos Delegation:** Domain accounts configured to cache TGTs, increasing lateral movement and domain takeover risks.

---

# Authentication & Identity Findings

- **Discovered Users (Kerbrute Enumeration):**
  - `skyler.white@polaris.local`
  - `saul.goodman@polaris.local`
  - `hank.schrader@polaris.local`
- **Full Domain User List (Authenticated LDAP Enumeration):**
  - `Administrator`, `Guest`, `DefaultAccount`, `krbtgt`, `skyler.white`, `jesse.pinkman`, `walter.white`, `hank.schrader`, `saul.goodman`, `CAPTAIN$`, `MEMBER$`
- **Kerberoastable Accounts:**
  - `jesse.pinkman` (Service ticket successfully cracked: `Wang0Tang0!`)
  - `walter.white` (Service ticket successfully cracked: `Metho1o590oA$elry`)
  - `saul.goodman` (Service ticket obtained, uncracked with `rockyou.txt`)
- **Delegation Configurations:**
  - **Unconstrained Delegation:** `CAPTAIN$`, `jesse.pinkman`
  - **Constrained Delegation with Protocol Transition:** `walter.white` (CIFS/captain.polaris.local)
  - **Resource-Based Constrained Delegation (RBCD):** `saul.goodman` configured against `MEMBER$`

---

# Lateral Movement

- **SMB Share Access:** Utilized valid credentials (`skyler.white:Password123`) to access sensitive shares (`ImportantNotes`, `SharingIsCaring`, `NETLOGON`, `SYSVOL`) across domain controllers.
- **MSSQL Authentication:** Validated domain credentials (`skyler.white:Password123`, `hank.schrader:sHyangja210`) against the Microsoft SQL Server 2019 instance running on port 1433 of `CAPTAIN`.

---

# Privilege Escalation

- **Starting Privilege:** Unauthenticated external observer / Anonymous SMB user.
- **Ending Privilege:** Authenticated Domain User (`skyler.white`, `hank.schrader`) with database access and recovered service account credentials (`jesse.pinkman`, `walter.white`).
- **Techniques Used:** Anonymous share harvesting, password spraying, Kerberoasting, and offline hash cracking.

---

# Domain Compromise

Full Domain Administrator compromise or DCSync was not achieved during this assessment. However, high-value service account credentials were compromised via Kerberoasting, and dangerous delegation configurations (`CAPTAIN$` and `jesse.pinkman` with unconstrained delegation) were identified, presenting significant theoretical paths to domain escalation if administrative interaction occurs.

---

# Failed Attack Paths

- **AS-REP Roasting:** Tested domain user accounts against `GetNPUsers.py` to check for pre-authentication disabled (`UF_DONT_REQUIRE_PREAUTH`). All tested accounts required pre-authentication; no AS-REP roasting vulnerabilities were found.
- **Constrained Delegation Abuse (Protocol Transition):** Attempted to abuse `walter.white`'s constrained delegation using `getST.py` to impersonate `Administrator` for CIFS on `captain.polaris.local`. The attempt failed due to Kerberos pre-authentication errors (`KDC_ERR_PREAUTH_FAILED`).
- **Resource-Based Constrained Delegation (RBCD):** Attempted to create a machine account (`ATTACKBOX$`) using authenticated credentials and configure RBCD against `MEMBER$`. Ticket requests using the created machine account failed with `KDC_ERR_C_PRINCIPAL_UNKNOWN` (Client not found in Kerberos database).

---

# Timeline of Compromise

- **2026-09-15 17:17:** Performed Kerbrute user enumeration and discovered valid usernames (`skyler.white`, `saul.goodman`, `hank.schrader`).
- **2026-09-15 17:19:** Inspected HTTP services (IIS Simple Uploader and default IIS welcome page).
- **2026-09-15 17:20:** Enumerated SMB shares anonymously on `CAPTAIN` (`192.168.122.10`), discovering plaintext credentials in the `SharingIsCaring` share.
- **2026-09-15 17:21:** Performed password spraying and successfully validated credentials for `skyler.white` (`Password123`) and `hank.schrader` (`sHyangja210`).
- **2026-09-15 17:22:** Tested validated credentials against MSSQL and SMB services successfully.
- **2026-09-15 17:23:** Performed authenticated LDAP enumeration, SID lookups, and extracted Kerberoastable service tickets (`jesse.pinkman`, `walter.white`, `saul.goodman`).
- **2026-09-15 17:23:** Enumerated Active Directory delegation settings, identifying unconstrained and constrained delegation targets.
- **2026-09-15 17:26:** Cracked Kerberoastable ticket hashes using Hashcat and `rockyou.txt`, recovering passwords for `jesse.pinkman` and `walter.white`.
- **2026-09-15 17:27:** Attempted constrained delegation and RBCD attack paths (failed due to protocol/principal errors).

---

# Assessment Statistics

- **Hosts Discovered:** 2
- **Hosts Compromised:** 1 (`CAPTAIN`)
- **Accounts Discovered:** 11 unique domain objects
- **Accounts Compromised:** 5 (`skyler.white`, `hank.schrader`, `jesse.pinkman`, `walter.white`, `saul.goodman`)
- **Credentials Obtained:** 15 recorded credential entries (including spray/SMB/cracked results)
- **Hashes Recovered:** 3 Kerberoast service ticket hashes
- **Kerberos Tickets Recovered:** TGT for `skyler.white`, Service tickets for Kerberoastable accounts
- **Successful Attack Paths:** 1 (Anonymous SMB -> Credential Discovery -> Authenticated Access -> Kerberoasting -> Hash Cracking)
- **Failed Attack Paths:** 4 (AS-REP Roasting, Constrained Delegation Protocol Transition, RBCD ticket generation, Saul Goodman ticket cracking)
- **Privilege Escalations:** Initial access to authenticated user & service account credential recovery
- **Lateral Movement Events:** SMB share access, MSSQL authentication

---

# Recommendations

1. **Disable Anonymous/Null SMB Access:**
   - Restrict anonymous and guest access to SMB shares on all domain controllers and member servers. Ensure group policy settings (`Network access: Let Everyone permissions apply to anonymous users`) are disabled.
2. **Eliminate Plaintext Credential Storage:**
   - Remove sensitive operational notes, scripts, or files containing plaintext passwords from shared network locations. Implement regular automated file-share auditing.
3. **Enforce Strong Password Policies for Service Accounts:**
   - Ensure service accounts utilize complex, high-entropy passwords (at least 25+ characters) to mitigate offline dictionary attacks against Kerberoastable SPNs.
4. **Audit and Restrict Kerberos Delegation:**
   - Review accounts configured with unconstrained delegation (`CAPTAIN$`, `jesse.pinkman`) and migrate to more secure models such as constrained delegation or Resource-Based Constrained Delegation (RBCD) where strictly necessary.
5. **Implement Account Monitoring and Rate Limiting:**
   - Monitor for abnormal Kerberos ticket requests (Kerberoasting activity - Event ID 4769) and implement account lockout policies to protect against password spraying and brute-force attempts.