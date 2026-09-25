The Active Directory environment `polaris.local` (DC: 192.168.122.10) was thoroughly assessed. The following findings were obtained:

### Summary of Findings
1.  **Initial Access:** Successfully authenticated as user `skyler.white` with password `Password123` via Kerberos and SMB. Another user, `saul.goodman`, was found with a known password `beTTer2caLL2me` through internal enumerations.
2.  **Sensitive Information:** The `ImportantNotes` share contained a note identifying the administrator's frustration regarding desk chairs and CCTV. The `SharingIsCaring` share contained a note mentioning an easy-to-remember password change for `skyler.white`.
3.  **Vulnerabilities & Misconfigurations:**
    *   **AD CS (Active Directory Certificate Services):** Multiple vulnerabilities were identified, specifically **ESC1, ESC2, ESC3, and ESC4**.
    *   The `ESC1` template is particularly critical as it allows an enrollee to supply a subject, enabling potential escalation to Domain Administrator by requesting a certificate for the Administrator UPN.
4.  **Credential Access:**
    *   Credentials recovered: `skyler.white:Password123`, `saul.goodman:beTTer2caLL2me`.
5.  **Lateral Movement & Privilege Escalation:**
    *   Attempted to use `ESC1` via `certipy`, but faced RPC endpoint resolution issues.
    *   MSSQL server (`192.168.122.10:1433`) is running, but current privileges are insufficient to enable `xp_cmdshell`.
    *   User `saul.goodman` and `skyler.white` are not members of high-privileged groups (e.g., Domain Admins).

### Conclusion
While initial access and significant misconfigurations (specifically within AD CS) were identified, further exploitation was hindered by technical obstacles. The identified AD CS vulnerabilities remain the most viable path to full domain compromise if the RPC connectivity issues are resolved or alternative methods to request certificates (e.g., via web enrollment) are utilized.

### Recommendations
1.  **Remediate AD CS Vulnerabilities:** Disable or restrict the `ESC1` template and restrict enrollment rights to authorized accounts only. Disable HTTP web enrollment (`ESC8`) to mitigate NTLM relay attacks.
2.  **Credential Management:** Enforce a strong password policy and rotate all compromised passwords.
3.  **Least Privilege:** Audit and remove unnecessary permissions for user accounts in Active Directory to prevent the exploitation of dangerous ACLs.
4.  **System Hardening:** Disable SMBv1, enforce SMB signing, and ensure that service accounts have the minimum required privileges, particularly concerning MSSQL and other critical services.