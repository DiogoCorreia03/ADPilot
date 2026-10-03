The penetration test against `192.168.122.10` (CAPTAIN.polaris.local) was conducted, resulting in the successful identification of multiple user accounts and valid credentials.

### Summary of Assessment
*   **Target:** `192.168.122.10`
*   **Highest Privilege Achieved:** Domain User with potential for further escalation via password reuse and Kerberoasting.
*   **Primary Findings:**
    *   **Weak Credentials & Password Reuse:** Successfully identified passwords for several users (e.g., `skyler.white`, `jesse.pinkman`, `hank.schrader`, `walter.white`) through password spraying and credential harvesting from accessible shares.
    *   **Kerberoasting:** Identified Kerberoastable SPNs for `jesse.pinkman` and `walter.white`. Successfully cracked `jesse.pinkman`'s TGS hash.
    *   **SMB Misconfigurations:** Accessible shares (`ImportantNotes`, `SharingIsCaring`) contained sensitive information, including hints for user accounts and passwords.
    *   **Credential Exposure:** Plaintext passwords found in descriptions of Active Directory user objects (`saul.goodman`).

### Credentials Obtained
| Username | Password | Source/Method |
| :--- | :--- | :--- |
| `skyler.white` | `Password123` | Password Spraying |
| `saul.goodman` | `beTTer2caLL2me` | LDAP User Object Description |
| `jesse.pinkman` | `Wang0Tang0!` | Kerberoasting (Offline Crack) |
| `hank.schrader` | `sHyangja210` | Password Spraying |
| `walter.white` | `Metho1o590oA$elry` | Password Spraying / Credential Rotation |

### Recommendations
1.  **Enforce Password Policy:** Implement and enforce a robust password policy to prevent the use of weak, common, or predictable passwords.
2.  **Audit AD Descriptions:** Regularly audit Active Directory object descriptions to prevent the exposure of sensitive information like passwords.
3.  **Restrict Share Access:** Limit access to SMB shares based on the principle of least privilege. Remove sensitive files from shared network locations.
4.  **Disable Weak Protocols:** Disable SMBv1 as it is deprecated and insecure.
5.  **Kerberoasting Mitigation:** Identify accounts with SPNs, enforce long and complex passwords for these service accounts, and consider implementing Managed Service Accounts (MSAs).
6.  **Principle of Least Privilege:** Audit and prune unnecessary group memberships and permissions. Ensure users have only the minimum access required for their roles.