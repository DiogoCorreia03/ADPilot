The penetration test against the domain controller at `192.168.122.10` has been initiated.

### Summary of Findings
1.  **Reconnaissance:**
    *   Identified `192.168.122.10` as `CAPTAIN.polaris.local`, running Windows Server 2016.
    *   Open services include: DNS, HTTP (IIS 10.0), Kerberos, LDAP, SMB, MSRPC, and MSSQL 2019.
2.  **Authentication/Enumeration:**
    *   SMB NULL sessions are allowed, but share enumeration is denied.
    *   Anonymous LDAP bind is allowed, but directory search is not permitted without authenticated access.
    *   Password spraying and user enumeration attempts using provided wordlists have not yielded valid credentials or confirmed user accounts yet.
    *   No vulnerable certificate templates or obvious configuration exploits were identified via initial scans.

### Current Status
The assessment is at a preliminary stage. Initial automated enumeration and credential harvesting attempts against the provided wordlists have not yielded successful authentication or user discovery.

### Plan
Given the lack of successful authentication, further steps will focus on:
*   Attempting to enumerate users more effectively through other protocols or by analyzing the IIS web application for potential information leakage.
*   Re-evaluating the provided `potential_users.txt` and `potential_passwords.txt` for any potential patterns.
*   Checking for additional entry points via the web server or other services if any misconfigurations become apparent.

*Due to the current inability to gain initial access, the testing remains in the reconnaissance and enumeration phase.*