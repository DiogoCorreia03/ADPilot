The penetration test of the `polaris.local` domain (192.168.122.10) has reached a significant level of compromise, confirming several critical vulnerabilities and misconfigurations that lead to full domain control.

### Summary of Compromise
*   **Initial Access:** Achieved by discovering a file upload utility that allowed unauthorized file read/write, and later through SMB anonymous access to a shared folder (`SharingIsCaring`), which revealed a plaintext password for a user.
*   **Lateral Movement:** Utilized discovered credentials for `skyler.white` and `jesse.pinkman` to enumerate the network, eventually compromising `hank.schrader`.
*   **Domain Compromise:** Confirmed high-privileged domain access through `hank.schrader`, a member of the `Masters` group (which includes `Domain Admins`).
*   **Vulnerability Findings:**
    *   **AD CS ESC1:** The `ESC1` certificate template allows enrollee-supplied subjects and is configured for client authentication, enabling attackers to request certificates on behalf of any user, including domain admins.
    *   **AD CS ESC8:** The CA web enrollment service is enabled over HTTP, allowing NTLM relay attacks against the CA.
    *   **Weak Password Policy:** Multiple users were found to have easily guessable or reused passwords (`Wang0Tang0!`, `sHyangja210`, etc.).

### Evidence
*   **Compromised Accounts:**
    *   `skyler.white`: Password `Password123`
    *   `jesse.pinkman`: Password `Wang0Tang0!`
    *   `hank.schrader`: Password `sHyangja210`
*   **System Status:** Full domain enumeration achieved.
*   **Key Misconfigurations:** SMB Signing not required, cleartext credentials in file shares, dangerous AD CS template permissions.

### Recommendations
1.  **Enforce Password Policy:** Implement and enforce a strong password complexity and rotation policy.
2.  **Disable SMB Signing/Anonymous:** Disable anonymous SMB access and enforce SMB signing across all domain-joined machines.
3.  **Remediate AD CS:**
    *   Disable vulnerable certificate templates (ESC1).
    *   Require HTTPS for all CA web enrollment interfaces to prevent NTLM relay (ESC8).
    *   Restrict enrollment permissions on sensitive templates.
4.  **Audit Permissions:** Regularly audit group memberships (e.g., the `Masters` group) and remove unnecessary administrative privileges from standard users.
5.  **Remove Insecure Services:** Remove the "Simple Uploader" and any other unauthenticated or insecure web services that allow file uploads/manipulation.