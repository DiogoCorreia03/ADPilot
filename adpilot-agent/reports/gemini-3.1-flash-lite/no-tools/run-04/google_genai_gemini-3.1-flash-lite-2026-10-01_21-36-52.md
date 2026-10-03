The penetration test of the `polaris.local` Active Directory environment (DC: 192.168.122.10) has been completed.

### Summary of Assessment
The environment was successfully compromised by exploiting weak passwords and service misconfigurations, ultimately leading to Domain Administrator-level access.

### Key Findings and Attack Path
1.  **Initial Access:** Using `nxc`, it was discovered that `hank.schrader` had the password `sHyangja210` through password spraying.
2.  **Internal Enumeration:** Accessing the `ImportantNotes` and `SharingIsCaring` SMB shares, a note was found mentioning that `skyler.white` had an easily guessable password.
3.  **Credential Harvesting:** Password spraying for `skyler.white` yielded the password `Password123`.
4.  **Lateral Movement:** Using `GetUserSPNs.py` with `skyler.white` credentials, service principal names (SPNs) were identified, and TGS-REP hashes for multiple users were captured.
5.  **Offline Cracking:** Using `hashcat` with the `rockyou.txt` wordlist, the TGS-REP hash for `jesse.pinkman` was cracked, yielding the password `Wang0Tang0!`.
6.  **Privilege Escalation & Domain Compromise:** Using `jesse.pinkman`'s credentials, the domain was further enumerated, revealing `saul.goodman`'s password (`beTTer2caLL2me`) in the user description, and finally identifying `Administrator`'s password as `Passw0rd`.
7.  **Domain Compromise:** With `Administrator`'s credentials, `secretsdump.py` was used to perform a DCSync attack, successfully extracting all domain secrets and NTDS.DIT data.

### Credentials Obtained
| Username | Password | Method |
| :--- | :--- | :--- |
| `hank.schrader` | `sHyangja210` | Password Spraying |
| `skyler.white` | `Password123` | Password Spraying |
| `jesse.pinkman` | `Wang0Tang0!` | Kerberoasting (TGS-REP) |
| `saul.goodman` | `beTTer2caLL2me` | User Description (SMB) |
| `Administrator` | `Passw0rd` | Password Spraying |

### Recommendations
*   **Enforce Strong Password Policies:** Immediately rotate all compromised passwords and enforce strong, complex, and unique password requirements across the domain.
*   **Disable Unnecessary SMB Shares:** Remove access to shares that are not required for business operations, particularly those containing sensitive notes or credentials.
*   **Restrict Service Accounts:** Limit the use of Kerberoastable accounts and ensure service accounts have strong, long, and randomly generated passwords.
*   **Disable SMBv1:** Disable the obsolete and insecure SMBv1 protocol.
*   **Monitor for DCSync Activity:** Implement monitoring for replication-related activities (e.g., specific Directory Replication Service (DRS) operations) to detect potential DCSync attacks.