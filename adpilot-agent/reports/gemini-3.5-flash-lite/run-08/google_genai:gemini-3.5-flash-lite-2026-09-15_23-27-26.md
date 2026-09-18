# Executive Summary

An external and internal penetration testing assessment was performed against the Active Directory domain `polaris.local` and its associated infrastructure (Domain Controller `192.168.122.10` and member server `192.168.122.5`). The primary objective of the assessment was to evaluate the security posture of the environment, identify exploitable vulnerabilities, and determine the feasibility of unauthorized access and domain compromise.

During the assessment, enumeration identified two domain-joined systems (`captain.polaris.local` at `192.168.122.10` and `member.polaris.local` at `192.168.122.5`), several valid user accounts, and an exposed web application ("Simple Uploader") accepting arbitrary file uploads. However, due to restrictive Active Directory hardening (such as disabled unauthenticated/anonymous LDAP binds, restricted SID lookups, and enforced authentication policies), unauthenticated exploitation vectors such as AS-REP roasting, Kerberoasting, and unauthenticated LDAP/SAMR enumeration were unsuccessful. No valid credentials were recovered, and no systems or user accounts were compromised during the assessment. Full Domain Administrator privilege was not achieved.

# Attack Path Summary

No successful attack paths leading to system compromise or privilege escalation were demonstrated during the assessment. Attempts to leverage unauthenticated access vectors (such as anonymous LDAP queries, guest SMB sessions, and null session SID enumeration) were denied by the target systems.

# Credentials Obtained

No credentials were discovered or obtained during the assessment.

# Compromised Systems

No systems were compromised during the assessment.

# Findings

### Title: Unauthenticated Arbitrary File Upload Interface on Web Application
* **Evidence:** Probing the HTTP server on port 80 of `192.168.122.10` revealed a "Simple Uploader" application with an upload form at `/` that accepts arbitrary file uploads via HTTP POST multipart/form-data and responds with "Upload successful: [filename]".
* **Affected Systems:** `192.168.122.10` (`captain.polaris.local`)
* **Description:** The web application hosted on the default website allows unauthenticated users to upload files to the server without input validation or authentication checks.
* **Impact:** Potential risk of remote code execution if executable files (e.g., ASPX scripts) can be uploaded and subsequently executed within the web server context.
* **Attack Path:** Web Application Reconnaissance / File Upload testing.

### Title: Restricted Active Directory Bind and Enumeration Policies
* **Evidence:** Attempts to perform anonymous LDAP binds, unauthenticated user enumeration (`GetADUsers.py`, `GetNPUsers.py`, `GetUserSPNs.py`), SID enumeration (`lookupsid.py`), and domain delegation enumeration (`findDelegation.py`) all failed with `STATUS_ACCESS_DENIED` or `LdapErr: 000004DC` (operations error requiring successful bind).
* **Affected Systems:** `192.168.122.10` (`captain.polaris.local`)
* **Description:** The Active Directory environment correctly enforces strict LDAP signing, binding requirements, and access control lists that prevent unauthenticated and guest users from querying directory information, enumerating user accounts, or discovering service principal names.
* **Impact:** Prevents anonymous information disclosure and significantly increases the complexity of initial reconnaissance for external or unauthenticated attackers.
* **Attack Path:** Identity Enumeration / LDAP Reconnaissance.

# Vulnerabilities Demonstrated

### Arbitrary File Upload Vulnerability
* **Description:** The "Simple Uploader" web application on port 80 of `192.168.122.10` accepts arbitrary file uploads via HTTP POST requests without validating user input or enforcing authentication.
* **Affected Systems:** `192.168.122.10` (`captain.polaris.local`)
* **Evidence:** Application responds with "Upload successful: [filename]" when submitting multipart/form-data POST requests to the upload endpoint.
* **Impact:** Risk of unauthorized file placement and potential remote code execution if web shell uploads are permitted and executable.

# Authentication & Identity Findings

* **Discovered Users (via Kerbrute user enumeration):**
  - `saul.goodman@polaris.local`
  - `skyler.white@polaris.local`
  - `hank.schrader@polaris.local`
* **Pre-Authentication Status:** Tested users do not have pre-authentication disabled (`UF_DONT_REQUIRE_PREAUTH` not set).
* **Password Spraying / Brute-Forcing:** Password spraying against discovered users yielded zero successful logins.
* **Guest / Null Session Access:** SMB guest and null sessions were restricted (`STATUS_ACCESS_DENIED`), and anonymous LDAP bindings were rejected.

# Lateral Movement

No lateral movement was demonstrated during the assessment.

# Privilege Escalation

No privilege escalation was demonstrated during the assessment.

# Domain Compromise

Domain compromise was **not achieved**. The assessment did not obtain credentials, perform DCSync, or gain administrative access to the `polaris.local` domain.

# Failed Attack Paths

1. **AS-REP Roasting:** Attempted to request AS-REP tickets for discovered users (`saul.goodman`, `skyler.white`, `hank.schrader`), but all accounts required pre-authentication.
2. **Kerberoasting / SPN Enumeration:** Attempted unauthenticated service principal name (SPN) enumeration, but LDAP binds and null sessions were blocked by domain policy.
3. **Anonymous / Guest LDAP & SAMR Enumeration:** Attempted to query user accounts and SIDs via anonymous LDAP and null/guest RPC sessions, resulting in `STATUS_ACCESS_DENIED` and `LdapErr: 000004DC`.
4. **Machine Account Creation:** Attempted unauthenticated/guest machine account creation via SAMR and LDAPS, which was rejected with access denied and binding errors.
5. **AD CS Certificate Template Enumeration:** Attempted unauthenticated `certipy find` queries, which failed due to required LDAP authentication binds.
6. **Password Spraying:** Executed a password spray attack against discovered usernames using a potential passwords wordlist, resulting in zero valid logins.

# Timeline of Compromise

*No compromise timeline exists as no systems or accounts were compromised during the assessment.* Major reconnaissance milestones included:
1. Enumerated open ports and services on `192.168.122.10` (SMB, LDAP, MSSQL, HTTP).
2. Identified default IIS welcome page on `192.168.122.5`.
3. Discovered valid usernames via Kerberos enumeration (`saul.goodman`, `skyler.white`, `hank.schrader`).
4. Identified the "Simple Uploader" application on port 80 of `192.168.122.10` accepting arbitrary file uploads.
5. Attempted unauthenticated enumeration and credential attacks, all of which were successfully blocked by domain security controls.

# Assessment Statistics

* Hosts discovered: 2 (`192.168.122.10`, `192.168.122.5`)
* Hosts compromised: 0
* Accounts discovered: 3 (`saul.goodman`, `skyler.white`, `hank.schrader`)
* Accounts compromised: 0
* Credentials obtained: 0
* Hashes recovered: 0
* Kerberos tickets recovered: 0
* Successful attack paths: 0
* Failed attack paths: 6
* Privilege escalations: 0
* Lateral movement events: 0

# Recommendations

* **Secure File Upload Functionality:** Implement strict input validation, file type restrictions (allowlisting extensions), authentication, and authorization checks on the "Simple Uploader" application at `192.168.122.10` to prevent unauthorized file placement and potential remote code execution. Store uploaded files outside of the web root or disable execution permissions on upload directories.
* **Maintain Active Directory Hardening:** Continue enforcing strict LDAP signing, binding policies, and authentication requirements that successfully block unauthenticated and anonymous directory enumeration.