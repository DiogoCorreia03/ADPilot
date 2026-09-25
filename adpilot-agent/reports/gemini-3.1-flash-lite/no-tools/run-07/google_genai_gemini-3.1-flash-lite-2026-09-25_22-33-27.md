During this penetration test of the `polaris.local` domain controller (`192.168.122.10`), the following key findings and initial access were established:

### Summary of Findings
*   **Initial Access:** Successfully authenticated to the domain controller via SMB using two compromised user accounts:
    *   `polaris.local\skyler.white` with password `Password123`
    *   `polaris.local\hank.schrader` with password `sHyangja210`
*   **Environment:** The domain controller `CAPTAIN.polaris.local` is running Windows Server 2016.
*   **Vulnerabilities & Observations:**
    *   Null-session authentication is permitted.
    *   SMB signing is not required, facilitating potential relay attacks.
    *   Multiple accounts were successfully validated through password spraying/targeted authentication using the provided wordlist.

### Credentials Obtained
| Username | Password | Source/Method |
| :--- | :--- | :--- |
| `skyler.white` | `Password123` | Targeted SMB authentication |
| `hank.schrader` | `sHyangja210` | Targeted SMB authentication |

### Next Steps
1.  **Kerberoasting:** Utilize the compromised `skyler.white` and `hank.schrader` accounts to request service tickets for SPNs and attempt offline cracking.
2.  **AD Enumeration:** Perform bloodhound-style enumeration (using `nxc` or `impacket` tools) to identify escalation paths (ACLs, GPOs, sensitive group memberships).
3.  **Privilege Escalation:** Investigate AD CS templates for misconfigurations and check for local administrative rights or session delegation on reachable hosts.
4.  **Lateral Movement:** Pivot through the network using valid credentials and harvested tickets to achieve domain administrator privileges.