# Executive Summary

This assessment evaluated the security posture of the `polaris.local` domain, specifically focusing on the host `192.168.122.10` (MEMBER.polaris.local). The objective was to identify potential attack vectors, escalate privileges, and assess lateral movement capabilities within the domain environment. 

The assessment successfully achieved low-to-medium privilege access to the target domain through password spraying and Kerberoasting. While several advanced escalation paths were identified (including AD CS misconfigurations and constrained delegation), full domain administrative control was not achieved due to service-level restrictions and hardening.

*   **Hosts Compromised:** 1
*   **Accounts Compromised:** 4
*   **Highest Level of Compromise:** Domain User / Service Account (Remote Code Execution)

# Attack Path Summary

The primary attack path followed this sequence:
1.  **Initial Access:** Password spraying against the domain identified valid user credentials (`hank.schrader` and `skyler.white`).
2.  **Enumeration:** Valid credentials were used to enumerate AD objects, identifying multiple vulnerable service accounts.
3.  **Lateral Movement/Escalation:** Kerberoasting was performed on service accounts. Cracking these hashes yielded credentials for `jesse.pinkman` and `walter.white`.
4.  **Remote Execution:** Credentials for `jesse.pinkman` were used to establish a WMI session on `192.168.122.10`, confirming Remote Code Execution (RCE).

# Credentials Obtained

| Username | Password | Source | Method |
| :--- | :--- | :--- | :--- |
| hank.schrader | sHyangja210 | polaris.local | Password Spray |
| skyler.white | Password123 | polaris.local | Password Spray |
| jesse.pinkman | Wang0Tang0! | polaris.local | Kerberoasting |
| walter.white | Metho1o590oA$elry | polaris.local | Kerberoasting |

# Compromised Systems

*   **Hostname:** MEMBER.polaris.local (192.168.122.10)
*   **Access Obtained:** Remote Code Execution (RCE) via WMI.
*   **Privilege Level:** User / Service Account.
*   **Significant Artifacts:** `note.txt`, `skyler.txt`.

# Findings

### Weak Password Policies / Password Spraying
*   **Evidence:** Successful authentication for `hank.schrader` and `skyler.white` via `Kerbrute`.
*   **Description:** The domain environment permitted a password spray attack, indicating a lack of account lockout policies or ineffective monitoring of authentication failures.
*   **Impact:** Unauthorized access to domain user accounts.

### Kerberoastable Service Accounts
*   **Evidence:** `GetUserSPNs.py` identified `jesse.pinkman`, `walter.white`, and `saul.goodman` as targets. 
*   **Description:** Service accounts with Service Principal Names (SPNs) set allow for the extraction of service tickets which can be cracked offline.
*   **Impact:** Exposure of service account passwords, leading to unauthorized access and potential escalation.

# Vulnerabilities Demonstrated

*   **Weak Password Policy:** Validated by successful password spray.
*   **Kerberoasting:** Validated by offline cracking of service account tickets for `jesse.pinkman` and `walter.white`.
*   **AD CS Misconfiguration (Potential):** Identified ESC1, ESC2, ESC3, and ESC8 via `Certipy`. *Note: Attempts to exploit these were unsuccessful due to environment restrictions.*

# Authentication & Identity Findings

*   **Discovered Users:** Administrator, Guest, DefaultAccount, krbtgt, skyler.white, jesse.pinkman, walter.white, hank.schrader, saul.goodman.
*   **Service Accounts:** `jesse.pinkman` (Unconstrained Delegation), `walter.white` (Constrained Delegation).

# Lateral Movement

*   **Technique:** Remote Code Execution (RCE) via WMI using `jesse.pinkman` credentials.
*   **Outcome:** Successfully accessed shares (`ImportantNotes`, `SharingIsCaring`) and executed commands on `192.168.122.10`.

# Privilege Escalation

*   **Starting Privilege:** Standard User (via Password Spray).
*   **Ending Privilege:** Service Account (via Kerberoasting).
*   **Evidence:** Successfully authenticated as `jesse.pinkman` and `walter.white` to perform service-level tasks.

# Domain Compromise

Domain Administrator compromise was **NOT** achieved. Attempts to abuse constrained delegation and AD CS (ESC1) were unsuccessful.

# Failed Attack Paths

*   **Constrained Delegation Abuse:** Attempts to impersonate the Administrator on `captain.polaris.local` using `walter.white` credentials failed due to `KDC_ERR_PREAUTH_FAILED`.
*   **AD CS (ESC1) Abuse:** Attempts to request a certificate as the Domain Administrator failed due to RPC access errors (`ept_s_not_registered`).
*   **AD CS (ESC8) Abuse:** Web Enrollment was not reachable/accessible; attack vector deemed non-viable.

# Timeline of Compromise

1.  **User Enumeration:** Identified valid users via `Kerbrute`.
2.  **Password Spray:** Gained initial access as `hank.schrader` and `skyler.white`.
3.  **Service Discovery:** Identified Kerberoastable accounts via `GetUserSPNs.py`.
4.  **Cracking:** Obtained passwords for `jesse.pinkman` and `walter.white` via `hashcat`.
5.  **Lateral Movement:** Executed commands via WMI using `jesse.pinkman` credentials.
6.  **Escalation Attempts:** Failed attempts to leverage AD CS and Kerberos delegation for domain escalation.

# Assessment Statistics

*   **Hosts Discovered:** 2 (192.168.122.5, 192.168.122.10)
*   **Hosts Compromised:** 1
*   **Accounts Compromised:** 4
*   **Credentials Obtained:** 4
*   **Kerberos Hashes Recovered:** 3
*   **Successful Attack Paths:** 1 (Password Spray -> Kerberoasting -> WMI)
*   **Failed Attack Paths:** 3 (Delegation Abuse, ESC1, ESC8)

# Recommendations

1.  **Enforce Password Complexity and Lockout:** Implement and enforce a strong password policy and account lockout threshold to prevent password spraying.
2.  **Rotate Service Account Passwords:** Rotate the passwords for all accounts vulnerable to Kerberoasting (specifically `jesse.pinkman`, `walter.white`, and `saul.goodman`) to long, complex, random strings.
3.  **Disable Unnecessary Delegation:** Remove unconstrained delegation from `jesse.pinkman` and audit constrained delegation settings on `walter.white`.
4.  **Harden AD CS:** If AD CS is not in use, disable the service. If required, restrict access to enrollment interfaces and patch misconfigured templates.