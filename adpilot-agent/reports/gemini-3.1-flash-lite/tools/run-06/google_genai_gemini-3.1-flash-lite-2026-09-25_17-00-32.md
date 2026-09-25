The Active Directory domain `polaris.local` (hosted on `192.168.122.10`) was assessed. The following findings were identified:

### Executive Summary
A domain user account (`skyler.white`) was compromised due to weak password policies, allowing for initial access to the domain. While limited access was initially obtained, further exploitation attempts, including `secretsdump` and `xp_cmdshell` for full domain compromise, were restricted by existing permissions.

### Attack Path Summary
1.  **Reconnaissance:** Initial scan identified `polaris.local` domain controller. Anonymous SMB access was confirmed, allowing share enumeration.
2.  **Initial Access:** A guest-accessible share `SharingIsCaring` contained `skyler.txt`, which suggested password changes. Using gathered credentials and password spraying/brute-forcing, the password `Password123` was successfully cracked/identified for user `skyler.white`.
3.  **Enumeration:** Authenticated with `skyler.white:Password123`, revealing AD user information and potential SPNs (`jesse.pinkman`, `walter.white`, `saul.goodman`).
4.  **Privilege Escalation Attempts:** Attempted to Kerberoast the discovered service accounts, but offline cracking failed against the wordlist. Attempted to dump `NTDS.dit` via `secretsdump` and use `xp_cmdshell` via MSSQL; both were denied due to insufficient privileges.

### Compromised Accounts
*   **Username:** `skyler.white`
*   **Password:** `Password123`
*   **Method:** Password identification based on contextual clues in the `SharingIsCaring` share and successful brute-force/spraying validation.

### Failed Attack Paths
*   **Domain Admin Compromise:** Attempted to use `secretsdump` (DRSUAPI/VSS) and MSSQL `xp_cmdshell` for full domain compromise, but all were blocked by `rpc_s_access_denied`.
*   **AD CS Abuse (ESC1):** Identified vulnerable certificate templates (ESC1, ESC2, ESC3, ESC4), but failed to successfully request a certificate due to RPC endpoint issues (`ept_s_not_registered`).

### Recommendations
*   **Enforce Strong Password Policies:** Disable the use of weak, common passwords (e.g., `Password123`).
*   **Restrict Anonymous/Guest Access:** Disable anonymous/guest SMB access and LDAP binds.
*   **Review Permissions:** Audit and restrict service account privileges and AD CS template enrollment rights.
*   **Update/Patch Services:** Ensure all services, especially MSSQL and AD CS, are hardened against unauthorized access and privilege escalation.