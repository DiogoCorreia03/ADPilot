The penetration test on the domain controller at `192.168.122.10` (`CAPTAIN.polaris.local`) has been completed.

### Executive Summary
The domain was successfully compromised, leading to Domain Administrator access. The primary attack vector involved exploiting guest credentials on an SMB share to discover a plaintext password, followed by privilege escalation through a combination of misconfigured group memberships (`Masters` group) and the ability to add users to privileged groups.

### Attack Path Summary
1.  **Reconnaissance**: Discovered SMB null-session/guest access, which led to the discovery of a plaintext password ("Passw0rd") associated with multiple accounts in the `polaris.local` domain, including `john.mayer`.
2.  **Initial Access**: Authenticated as `john.mayer` using the discovered password via SMB.
3.  **Data Discovery**: Discovered a file `skyler.txt` on the `SharingIsCaring` SMB share, which hinted at `skyler.white` having a simple password.
4.  **Credential Harvesting**: Performed password spraying for `skyler.white`, successfully identifying her password as `Password123`.
5.  **Lateral Movement & Privilege Escalation**:
    *   `skyler.white` was identified as having membership in the `Masters` group.
    *   By exploiting this membership, it was discovered that `skyler.white` had sufficient permissions to add users to the `Domain Admins` group.
    *   Successfully added `skyler.white` to `Domain Admins` using `net group` commands via `smbexec`.
6.  **Full Compromise**: With `Domain Admins` membership, full control over the Active Directory domain was achieved.

### Credentials Obtained
| Username | Password | Method |
| :--- | :--- | :--- |
| `john.mayer` | `Passw0rd` | Found in SMB share/Brute force |
| `skyler.white` | `Password123` | Password Spraying |
| `hank.schrader`| `sHyangja210`| Password Spraying |
| `jesse.pinkman`| `Wang0Tang0!` | Kerberoasting |
| `walter.white` | `Metho1o590oA$elry`| Kerberoasting |

### Compromised Systems
*   **Host**: `CAPTAIN.polaris.local` (192.168.122.10)
*   **Privilege**: Domain Administrator (SYSTEM)

### Findings & Demonstrated Vulnerabilities
1.  **Excessive SMB Access/Guest Auth**: Guest access was enabled on several shares, allowing unauthorized enumeration of files and sensitive information.
2.  **Weak Password Policy**: The domain allowed easily guessable passwords (e.g., `Password123`, `Passw0rd`).
3.  **Insecure Group Permissions**: The `Masters` group was misconfigured, granting its members excessive permissions, including the ability to manage domain memberships, which allowed for trivial escalation to `Domain Admins`.
4.  **Kerberoasting**: Multiple service accounts were vulnerable to Kerberoasting due to weak SPN configurations.

### Recommendations
*   **Disable Guest/Anonymous Access**: Configure SMB shares to require authenticated, authorized access.
*   **Enforce Strong Password Policies**: Implement a stringent password complexity and rotation policy.
*   **Audit Active Directory ACLs**: Regularly audit group permissions and ACLs to ensure least-privilege access, particularly for powerful groups like `Masters` or `Domain Admins`.
*   **Patch & Harden**: Ensure the server is fully patched and remove legacy protocols like SMBv1.