# Executive Summary

**Assessment Scope:** Polaris.local domain infrastructure, including hosts 192.168.122.5 and 192.168.122.10.
**Overall Objective:** Identify security weaknesses, test authentication controls, and evaluate lateral movement potential within the target environment.
**Highest Level of Compromise Achieved:** Authenticated domain user access (low-privileged).
**Number of Compromised Hosts:** 1 (192.168.122.10).
**Number of Compromised Accounts:** 4 (skyler.white, hank.schrader, walter.white, jesse.pinkman).
**Critical Observations:** The environment is susceptible to Kerberoasting, and weak password policies were identified. While domain users were compromised, full domain administrative access was not achieved.

---

# Attack Path Summary

1.  **Initial Access:** User enumeration via Kerbrute identified valid accounts. Password spraying and brute-force against the MSSQL service on 192.168.122.10 resulted in the compromise of the `skyler.white` account.
2.  **Privilege Escalation & Lateral Movement:** Using `skyler.white` credentials, Kerberoasting was performed against the domain controller, leading to the recovery of passwords for `walter.white` and `jesse.pinkman`.
3.  **Final Impact:** Successful authentication across various domain services using recovered credentials, though no escalation to Domain Admin or local administrator on target hosts was successful.

---

# Credentials Obtained

| Username | Password | Source Host | Acquisition Method |
| :--- | :--- | :--- | :--- |
| skyler.white | Password123 | 192.168.122.10 | MSSQL Brute-force |
| hank.schrader | sHyangja210 | 192.168.122.10 | Password Spraying |
| walter.white | Metho1o590oA | 192.168.122.10 | Kerberoasting / Hashcat |
| jesse.pinkman | Wang0Tang0! | 192.168.122.10 | Kerberoasting / Hashcat |

---

# Compromised Systems

**Hostname: CAPTAIN (192.168.122.10)**
* **Access Obtained:** Authenticated Domain User Access.
* **Privilege Level:** Standard User.
* **Credentials Used:** `skyler.white`, `walter.white`, `jesse.pinkman`, `hank.schrader`.
* **Significant Artifacts:** `note.txt`, `skyler.txt` (via SMB).

---

# Findings

### Kerberoastable Service Accounts
* **Evidence:** Successfully performed `GetUserSPNs.py` and captured TGS hashes for `jesse.pinkman`, `walter.white`, and `saul.goodman`.
* **Description:** Service accounts in the domain have SPNs registered, allowing for offline cracking of service ticket hashes.
* **Impact:** Compromise of service account passwords.

### Weak Password Policy
* **Evidence:** Multiple accounts (`skyler.white`, `hank.schrader`, `walter.white`, `jesse.pinkman`) were compromised via brute-force or password spraying.
* **Description:** Accounts utilize passwords susceptible to dictionary or pattern-based attacks.
* **Impact:** Unauthorized account access and potential lateral movement.

### SMB Null-Session Enabled
* **Evidence:** Null-session SMB enabled on 192.168.122.10.
* **Description:** Allows anonymous enumeration of domain information.
* **Impact:** Information disclosure regarding domain naming and structure.

---

# Vulnerabilities Demonstrated

* **Kerberoasting:** Demonstrated on 192.168.122.10; led to recovery of service account passwords.
* **Weak Password Policy:** Demonstrated by the success of password spraying and brute-force attacks against `skyler.white` and `hank.schrader`.

---

# Authentication & Identity Findings

* **Discovered Users:** saul.goodman, hank.schrader, skyler.white, jesse.pinkman, walter.white, Administrator, Guest, krbtgt.
* **Service Accounts:** jesse.pinkman, walter.white, saul.goodman.
* **Password Reuse:** Credentials `skyler.white:Password123` and others successfully used for both MSSQL and SMB access.

---

# Lateral Movement

* **Technique:** Credential-based SMB authentication.
* **Evidence:** Successfully enumerated shares `ImportantNotes` and `SharingIsCaring` on 192.168.122.10 using `skyler.white` credentials. Attempts to access 192.168.122.5 failed due to authentication errors.

---

# Privilege Escalation

* **Summary:** No privilege escalation to Domain Admin or local administrator was achieved. All attempts to use MSSQL `xp_cmdshell` or exploit high-privileged GPO settings failed due to insufficient permissions.

---

# Domain Compromise

* **Status:** **NOT ACHIEVED.**
* **Details:** No paths to Domain Admin were identified via BloodHound analysis, and attempts to leverage high-privilege operations were consistently denied.

---

# Failed Attack Paths

* **Anonymous SMB/LDAP Access:** Failed to extract significant data from 192.168.122.5.
* **MSSQL xp_cmdshell:** Failed due to lack of `sysadmin` privileges.
* **Lateral movement to 192.168.122.5:** All attempts failed with `NT_STATUS_LOGON_FAILURE`.

---

# Timeline of Compromise

1.  Enumerate domain via null-session (192.168.122.10).
2.  Enumerate users via Kerbrute.
3.  Brute-force MSSQL service; obtain `skyler.white` credentials.
4.  Authenticate via SMB using `skyler.white` credentials.
5.  Perform Kerberoasting; capture TGS hashes.
6.  Crack hashes; obtain `walter.white` and `jesse.pinkman` credentials.
7.  Perform password spraying; obtain `hank.schrader` credentials.

---

# Assessment Statistics

* **Hosts Discovered:** 2
* **Hosts Compromised:** 1
* **Accounts Compromised:** 4
* **Credentials Obtained:** 4
* **Hashes Recovered:** 3 (Kerberoast)
* **Successful Attack Paths:** 1 (Credential collection leading to authenticated access)
* **Failed Attack Paths:** 3
* **Privilege Escalations:** 0

---

# Recommendations

1.  **Enforce Password Complexity:** Update domain policy to require strong, complex passwords to mitigate brute-force and spraying attacks.
2.  **Implement Account Lockout:** Configure account lockout policies to prevent automated brute-force attempts.
3.  **Disable SMB Null-Sessions:** Restrict anonymous access to SMB shares and domain information.
4.  **Audit Service Accounts:** Periodically rotate passwords for service accounts identified as "Kerberoastable" and migrate to Group Managed Service Accounts (gMSA) where possible.
5.  **Restrict MSSQL Access:** Ensure service accounts are not granted excessive permissions and disable features like `xp_cmdshell` if not strictly required.