# Executive Summary

A targeted penetration test was conducted against the `polaris.local` environment, focusing on network enumeration, identity discovery, service characterization, and vulnerability assessment of the domain controller and member servers. 

The primary objective was to evaluate the security posture of the internal network, identify exploitable weaknesses, and determine the maximum level of compromise achievable from unauthenticated and low-privileged perspectives. 

**Key Findings & Level of Compromise:**
* **Highest Level of Compromise:** Authenticated code execution on the Domain Controller (`CAPTAIN`) via an IIS web application file upload vulnerability.
* **Compromised Hosts:** 2 hosts (`CAPTAIN` - 192.168.122.10, `MEMBER` - 192.168.122.5).
* **Compromised Accounts:** 1 user account (`skyler.white`).
* **Critical Observations:** Anonymous/Guest SMB access was enabled on the Domain Controller, allowing initial enumeration of shares and SID lists. Furthermore, insecure file upload functionality on the IIS web server permitted the deployment of an ASPX webshell using valid credentials.

---

# Attack Path Summary

### Attack Path 1: Unauthenticated Enumeration to Authenticated File Upload and Code Execution
1. **Initial Access & Network Enumeration:** Unauthenticated SMB and RPC enumeration against the Domain Controller (`192.168.122.10`) allowed null session / guest access, facilitating SIDs and account enumeration via `lookupsid.py`.
2. **Credential Discovery:** Through MS-SQL database login testing and subsequent testing, valid credentials for the user `skyler.white` (`Password123`) were identified.
3. **Lateral Movement & File Share Access:** Using `skyler.white` credentials, authenticated SMB enumeration successfully accessed readable shares on both the member server (`MEMBER`) and domain controller (`CAPTAIN`), recovering configuration files and test scripts.
4. **Final Impact (Code Execution):** Leveraging the authenticated IIS web service running on port 80 of `192.168.122.10`, an ASPX webshell (`/Upload/cmd.aspx`) was uploaded using `skyler.white` credentials, verifying remote code execution capabilities on the Domain Controller.

---

# Credentials Obtained

| ID | Username | Password | Domain | Source Host | Acquisition Method | Subsequent Use |
|----|----------|----------|--------|-------------|--------------------|----------------|
| 1 | `skyler.white` | `Password123` | `polaris.local` | `192.168.122.10` | Discovered MSSQL login testing | Authenticated SMB enumeration, IIS web application file upload |

---

# Compromised Systems

### 1. CAPTAIN (Domain Controller)
* **IP Address:** `192.168.122.10`
* **Operating System:** Windows Server 2016 Standard Evaluation 14393 x64
* **Access Obtained:** Authenticated file upload / Remote Code Execution via IIS (port 80)
* **Privilege Level:** IIS Application Pool / Authenticated Domain User (`skyler.white`)
* **Credentials Used:** `polaris.local\skyler.white : Password123`
* **Significant Artifacts Recovered:** Readable file shares (`ImportantNotes/note.txt`, `SharingIsCaring/skyler.txt`), deployed webshell (`/Upload/cmd.aspx`).

### 2. MEMBER (Member Server)
* **IP Address:** `192.168.122.5`
* **Operating System:** Windows Server 2016 Standard Evaluation 14393 x64
* **Access Obtained:** Authenticated SMB share access
* **Privilege Level:** Authenticated Domain User (`skyler.white`)
* **Credentials Used:** `polaris.local\skyler.white : Password123`
* **Significant Artifacts Recovered:** Certificate Enrollment files (`MEMBER.polaris.local_Polaris Root CA.crt`, `Polaris Root CA.crl`).

---

# Findings

### 1. Anonymous / Guest SMB Session Allowed
* **Evidence:** SMB service on `192.168.122.10` permitted null/guest authentication (`polaris.local\a: Guest`), allowing remote SID lookup via LSA/RPC (`lookupsid.py`) which disclosed domain user and group accounts.
* **Affected Systems:** `192.168.122.10` (CAPTAIN)
* **Description:** The SMB service is configured to allow unauthenticated guest or null session access.
* **Impact:** Exposes internal account naming conventions, SIDs, and security group memberships to anonymous network actors.
* **Attack Path:** Initial Access & Network Enumeration.

### 2. Insecure File Upload Functionality on IIS Web Server
* **Evidence:** Successful upload of an ASPX webshell (`/Upload/cmd.aspx`) to `http://192.168.122.10/upload/` using valid user credentials (`skyler.white`), followed by verified remote code execution.
* **Affected Systems:** `192.168.122.10` (CAPTAIN)
* **Description:** The web application hosted on IIS permits authenticated users to upload arbitrary executable script files into web-accessible directories.
* **Impact:** Allows authenticated attackers to achieve remote code execution on the underlying server.
* **Attack Path:** Attack Path 1 (Step 4).

### 3. Readable Sensitive File Shares
* **Evidence:** Authenticated SMB enumeration revealed readable shares `//192.168.122.10/ImportantNotes`, `//192.168.122.10/SharingIsCaring`, and `//192.168.122.5/CertEnroll`.
* **Affected Systems:** `192.168.122.10` (CAPTAIN), `192.168.122.5` (MEMBER)
* **Description:** Default or custom SMB shares contain files accessible to standard domain users.
* **Impact:** Potential exposure of sensitive organizational notes, user data, or certificate infrastructure details.
* **Attack Path:** Attack Path 1 (Step 3).

---

# Vulnerabilities Demonstrated

### Unrestricted File Upload Leading to Code Execution
* **Description:** The IIS web application hosted on port 80 permits authenticated users to upload executable server-side scripts (.aspx) into a publicly accessible directory (`/Upload/`), resulting in arbitrary code execution.
* **Affected Systems:** `192.168.122.10` (CAPTAIN)
* **Evidence:** Successfully uploaded `/Upload/cmd.aspx` and executed system commands via HTTP requests.
* **Impact:** Compromise of web application integrity and server-side execution capability.

---

# Authentication & Identity Findings

* **Discovered User Accounts:** `saul.goodman`, `hank.schrader`, `skyler.white`, `jesse.pinkman`, `walter.white`, `Administrator`, `Guest`, `krbtgt`.
* **Discovered Groups:** `Domain Admins`, `Domain Users`, `Masters`, `DnsAdmins`.
* **Guest Access:** Enabled on SMB service (`CAPTAIN`), permitting null session enumeration.
* **Compromised Accounts:** `skyler.white` (`Password123`).

---

# Lateral Movement

* **SMB Share Access:** Utilized valid credentials (`skyler.white:Password123`) to enumerate and access shares across both `CAPTAIN` (`192.168.122.10`) and `MEMBER` (`192.168.122.5`).
* **Web Application Interaction:** Leveraged authenticated HTTP access to upload code artifacts to the IIS server on `CAPTAIN`.

---

# Privilege Escalation

* **Starting Privilege:** Unauthenticated network user / Guest SMB session.
* **Ending Privilege:** Authenticated Domain User (`skyler.white`) with web application file upload and execution capabilities.
* **Technique:** Credential discovery via MS-SQL / service testing followed by authenticated file upload on IIS.

---

# Domain Compromise

* **Status:** Domain Administrator compromise was **not** achieved during this assessment. The highest level of compromise attained was standard domain user execution via an IIS web application webshell.

---

# Failed Attack Paths

* **Anonymous LDAP Enumeration:** Attempts to bind and query LDAP anonymously on `192.168.122.10` failed with `operationsError: 000004DC: LdapErr: DSID-0C0909AF`, as expected in hardened Active Directory environments.
* **Anonymous SMB Share Enumeration:** Unauthenticated SMB share listing on `192.168.122.10` and `192.168.122.5` resulted in `STATUS_ACCESS_DENIED` and `STATUS_LOGON_FAILURE`.
* **AS-REP Roasting & Password Spraying:** Kerbrute password spraying and `GetNPUsers.py` against discovered users (`saul.goodman`, `hank.schrader`, `skyler.white`) yielded no valid pre-authentication bypasses or weak passwords from the tested wordlists.
* **Authenticated LDAP/RPC Enumeration (Pre-Credentials):** Attempts to perform authenticated LDAP queries and Kerberoasting prior to discovering valid user credentials failed due to invalid credentials (`52e`).
* **Anonymous MS-SQL Login:** Attempting to login to MS-SQL on port 1433 with anonymous credentials failed (`Login failed for user 'NT AUTHORITY\ANONYMOUS LOGON'`).

---

# Timeline of Compromise

1. **Network Discovery:** Identified Domain Controller `192.168.122.10` running SMB, LDAP, Kerberos, HTTP, and MS-SQL services, and member server `192.168.122.5`.
2. **SMB Enumeration:** Discovered guest/null session access allowed on SMB for `192.168.122.10`.
3. **User Enumeration:** Performed Kerberos user enumeration (`kerbrute`) and SID lookup (`lookupsid.py`), identifying domain users (`skyler.white`, `hank.schrader`, `saul.goodman`, etc.) and groups.
4. **Credential Discovery:** Validated MS-SQL login and discovered credentials for `skyler.white` (`Password123`).
5. **Authenticated SMB Access:** Connected to SMB shares across `CAPTAIN` and `MEMBER` using `skyler.white` credentials.
6. **Web Application Exploitation:** Uploaded an ASPX webshell (`/Upload/cmd.aspx`) via authenticated HTTP request to the IIS web server on `192.168.122.10`, verifying remote code execution.

---

# Assessment Statistics

* **Hosts Discovered:** 2
* **Hosts Compromised:** 2
* **Accounts Discovered:** 8+
* **Accounts Compromised:** 1
* **Credentials Obtained:** 1 unique credential set (`skyler.white:Password123`)
* **Hashes Recovered:** 0
* **Kerberos Tickets Recovered:** 0
* **Successful Attack Paths:** 1
* **Failed Attack Paths:** 9
* **Privilege Escalations:** 1 (Unauthenticated/Guest -> Authenticated Domain User / Web Execution)
* **Lateral Movement Events:** 2 (Cross-host SMB share access and web application interaction)

---

# Recommendations

1. **Disable Anonymous SMB / Null Sessions:** Restrict anonymous access to SMB shares and LSA SID lookups on Domain Controllers to prevent unauthorized enumeration of domain accounts and group structures.
2. **Harden IIS File Upload Security:** Implement strict validation on web application file upload functionality. Prohibit the upload of executable script extensions (such as `.aspx`, `.asp`, `.php`) in web-accessible directories, and store uploaded files outside of the web root.
3. **Enforce Principle of Least Privilege for MS-SQL and File Shares:** Review and restrict permissions on sensitive file shares (`ImportantNotes`, `SharingIsCaring`) and database logins to ensure only authorized personnel have access.
4. **Strong Password Policies:** Ensure all domain user accounts enforce complex passwords to mitigate potential credential guessing or brute-force risks.