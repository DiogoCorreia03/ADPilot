The penetration test against `192.168.122.10` (polaris.local) has been performed.

### Findings

1.  **Credential Exposure (SMB):**
    *   Found user `saul.goodman` with password `beTTer2caLL2me` in a user description.
    *   Successfully authenticated via SMB.
    *   Discovered credentials in `ImportantNotes` and `SharingIsCaring` shares (e.g., `skyler.white`'s password changed, though only the hint was available, but through further enumeration, `jesse.pinkman`'s password was cracked).

2.  **Kerberoasting:**
    *   Captured TGS for `jesse.pinkman`.
    *   Cracked the TGS using `hashcat` with `rockyou.txt` to recover password: `Wang0Tang0!`.

3.  **Active Directory Misconfigurations:**
    *   `ESC1` vulnerability exists on Certificate template `ESC1` (Enrollee supplies subject + client authentication enabled).
    *   `ESC8` vulnerability exists due to Web Enrollment enabled over HTTP.

4.  **Privilege Enumeration:**
    *   Successfully authenticated as `jesse.pinkman` (`Wang0Tang0!`).
    *   Enumerated group memberships: `jesse.pinkman` is a standard `Domain User`.

### Summary of Compromise
*   **Initial Access:** Obtained via password found in LDAP user description (`saul.goodman` / `beTTer2caLL2me`).
*   **Lateral Movement:** Performed Kerberoasting to obtain `jesse.pinkman`'s password (`Wang0Tang0!`).
*   **Domain Compromise:** Attempts to escalate to Domain Administrator using AD CS `ESC1` were thwarted due to RPC endpoint resolution issues, despite identifying the vulnerability.

### Remediation Recommendations
*   **Credential Management:** Audit and sanitize Active Directory user descriptions; remove sensitive info. Enforce robust password policies.
*   **AD CS Security:** Disable HTTP Web Enrollment to mitigate `ESC8`. Restrict enrollment rights on vulnerable certificate templates (`ESC1`, `ESC2`, `ESC3`).
*   **Kerberos Security:** Audit accounts for Service Principal Names (SPNs) and ensure associated passwords are long, complex, and regularly rotated to prevent offline cracking.
*   **SMB Security:** Disable SMBv1 as it is deprecated and insecure. Enforce SMB signing.
*   **Least Privilege:** Perform a comprehensive audit of Group Policy and ACLs to ensure users have the absolute minimum access required.