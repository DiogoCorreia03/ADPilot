The penetration test of the `polaris.local` domain (192.168.122.10) has been completed. The assessment successfully identified several critical vulnerabilities and misconfigurations that allowed for the compromise of multiple user accounts.

### Executive Summary
*   **Target:** `polaris.local` (192.168.122.10)
*   **Highest Level of Access:** Domain User (with potential certificate-based privilege escalation).
*   **Compromised Accounts:** `skyler.white`, `walter.white`, `jesse.pinkman`, `hank.schrader`, `saul.goodman`.
*   **Critical Observations:**
    *   Passwords were found stored in cleartext in user descriptions (e.g., `Saul Goodman`).
    *   Kerberoasting was successfully performed, revealing plaintext passwords for `Walter White` and `Jesse Pinkman`.
    *   The domain is vulnerable to AD CS misconfigurations (ESC1), allowing domain users to potentially elevate privileges by requesting certificates as other users.

### Attack Path Summary
1.  **Reconnaissance:** Initial scan revealed domain services. Anonymous SMB access was restricted but user enumeration was possible.
2.  **Credential Harvesting:** Password spraying identified `skyler.white` with the password `Password123`.
3.  **Credential Harvesting:** Kerberoasting was used to obtain TGS hashes for service accounts. Offline cracking revealed passwords for `Walter White` and `Jesse Pinkman`.
4.  **Internal Mapping:** Further enumeration of user descriptions revealed `Saul Goodman`'s password stored in plain text.
5.  **AD CS Misconfiguration:** AD CS audit identified ESC1 vulnerability. Although automated exploitation failed, the template is confirmed to be vulnerable.

### Credentials Obtained
| Username | Plaintext Password | Source |
| :--- | :--- | :--- |
| `skyler.white` | `Password123` | Password Spraying |
| `walter.white` | `Metho1o590oA$elry` | Kerberoasting |
| `jesse.pinkman` | `Wang0Tang0!` | Kerberoasting |
| `hank.schrader` | `sHyangja210` | Password Spraying |
| `saul.goodman` | `beTTer2caLL2me` | User Description (LDAP) |

### Findings & Vulnerabilities
*   **Cleartext Passwords in LDAP:** User descriptions (specifically Saul Goodman) contained plain-text passwords.
*   **Kerberoasting:** Multiple service accounts had weak or crackable passwords.
*   **AD CS Misconfiguration (ESC1):** The template `ESC1` allows domain users to request certificates and supply their own Subject Alternate Name (SAN), enabling impersonation of privileged users.

### Recommendations
1.  **Password Policy:** Enforce a strong password policy and ensure regular password rotation.
2.  **Audit AD CS:** Immediately disable vulnerable certificate templates (ESC1, ESC2, ESC3) and restrict enrollment permissions.
3.  **User Descriptions:** Periodically audit Active Directory objects for sensitive information stored in cleartext within fields like `description`.
4.  **Kerberos Security:** Monitor for Kerberoasting activity and consider using group managed service accounts (gMSAs) to manage service account passwords.