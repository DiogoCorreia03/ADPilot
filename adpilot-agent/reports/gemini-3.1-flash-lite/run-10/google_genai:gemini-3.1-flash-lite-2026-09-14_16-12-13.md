# Executive Summary

This assessment evaluated the security posture of the `polaris.local` environment. The objective was to identify security weaknesses through authenticated and unauthenticated testing. The assessment resulted in the full compromise of one member server (`member.polaris.local`) and the identification of multiple valid user credentials. While full domain dominance was not achieved, the ability to escalate privileges to local administrator on a member server highlights significant risks related to resource-based delegation and credential management.

*   **Scope:** 192.168.122.5 (member.polaris.local), 192.168.122.10 (captain.polaris.local)
*   **Highest Compromise:** Local Administrator access on 192.168.122.5
*   **Compromised Hosts:** 1 (192.168.122.5)
*   **Compromised Accounts:** 4 (saul.goodman, jesse.pinkman, walter.white, skyler.white)

# Attack Path Summary

1.  **Initial Access:** Anonymous SMB null-session enumeration on 192.168.122.10 revealed the credential `saul.goodman:beTTer2caLL2me`.
2.  **Privilege Escalation & Lateral Movement:** Using the `saul.goodman` account, the attacker identified a Resource-Based Constrained Delegation (RBCD) misconfiguration. By requesting a service ticket for `saul.goodman` and utilizing `getST.py`, the attacker impersonated the `Administrator` account to access the CIFS service on 192.168.122.5.
3.  **Final Impact:** Administrative access on 192.168.122.5 was confirmed via `wmiexec.py`, followed by credential dumping using `secretsdump.py`.

# Credentials Obtained

| Username | Password | Source | Subsequent Use |
| :--- | :--- | :--- | :--- |
| saul.goodman | beTTer2caLL2me | Anonymous SMB Enumeration | Kerberoasting, LDAP, RBCD Attack |
| jesse.pinkman | Wang0Tang0! | Kerberoasting | LDAP, WMI, SMB |
| walter.white | Metho1o590oA | Kerberoasting | N/A (Login failure) |
| skyler.white | Password123 | Password Spraying | LDAP, SMB |

# Compromised Systems

*   **Hostname:** member.polaris.local (192.168.122.5)
    *   **Access:** Local Administrator (via RBCD exploitation)
    *   **Credentials Used:** saul.goodman (TGT/ST impersonation)
    *   **Artifacts:** NTDS/SAM hashes extracted via `secretsdump.py`

# Findings

### Resource-Based Constrained Delegation (RBCD) Misconfiguration
*   **Evidence:** `findDelegation.py` showed `saul.goodman` has rights to the `MEMBER$` account.
*   **Impact:** Allowed impersonation of the domain `Administrator` on the target host.
*   **Affected Systems:** 192.168.122.5

### Weak Password Policies
*   **Evidence:** Multiple account passwords were recovered via Kerberoasting and spraying (e.g., `Password123`, `Wang0Tang0!`).
*   **Impact:** Enables unauthorized access to domain resources and potential lateral movement.

# Vulnerabilities Demonstrated

*   **Insecure Delegation:** Resource-Based Constrained Delegation (RBCD) was configured to allow the `saul.goodman` account to act as a computer account (`MEMBER$`), facilitating privilege escalation.
*   **Kerberoastable Service Accounts:** Multiple accounts (jesse.pinkman, walter.white) were susceptible to Kerberoasting due to high-privilege service principal names (SPNs).
*   **Password Spraying Susceptibility:** Lack of aggressive account lockout or monitoring allowed for the discovery of the `skyler.white` password.

# Authentication & Identity Findings

*   **Guest Access:** Anonymous SMB null-sessions were successful on 192.168.122.10.
*   **Credential Reuse:** While `saul.goodman` was used across multiple services, lateral movement to 192.168.122.5 was strictly successful through delegation abuse rather than password reuse.

# Lateral Movement

*   **Kerberos-based:** Successfully used RBCD to move from a standard user context to `Administrator` on 192.168.122.5.
*   **SMB/WMI:** Authenticated sessions were used for file listing and command execution post-exploitation.

# Privilege Escalation

*   **Technique:** Resource-Based Constrained Delegation Abuse.
*   **Starting Privilege:** Domain User (`saul.goodman`)
*   **Ending Privilege:** Local Administrator on 192.168.122.5.

# Domain Compromise

*   **Status:** Not achieved. The assessment stopped at local administrative compromise of a member server.

# Failed Attack Paths

*   **Password Spraying against 192.168.122.5:** Failed due to logon restrictions.
*   **Constrained Delegation (Walter White):** Failed due to pre-authentication errors.
*   **Computer Account Creation:** Denied due to insufficient permissions.

# Timeline of Compromise

1.  **14:55:** Initial anonymous SMB enumeration on 192.168.122.10 (Credential: `saul.goodman`).
2.  **14:56:** Password spraying identified `skyler.white:Password123`.
3.  **14:57:** LDAP domain dumping performed.
4.  **14:59:** Kerberoasting performed; successful cracking of `jesse.pinkman` and `walter.white`.
5.  **15:00:** RBCD exploitation initiated against 192.168.122.5.
6.  **15:05:** Administrative access confirmed on 192.168.122.5.

# Assessment Statistics

*   **Hosts Discovered:** 2
*   **Hosts Compromised:** 1
*   **Accounts Compromised:** 4
*   **Credentials Obtained:** 3 (Unique pairings)
*   **Privilege Escalations:** 1

# Recommendations

1.  **Audit Delegation Rights:** Review all `msDS-AllowedToActOnBehalfOfOtherIdentity` attributes on computer objects to ensure only necessary accounts hold delegation rights.
2.  **Enforce Strong Password Policies:** Implement and enforce a password complexity policy that rejects common strings found in lists like `rockyou.txt`.
3.  **Audit Service Accounts:** Periodically rotate passwords for all service accounts and restrict the use of SPNs for non-service accounts.
4.  **Disable Null Sessions:** Restrict anonymous SMB access via GPO to prevent low-level enumeration of user accounts and shares.