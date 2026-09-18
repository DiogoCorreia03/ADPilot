# Executive Summary

This assessment evaluated the security posture of the `polaris.local` Active Directory environment. The primary objective was to identify vulnerabilities and assess the potential for unauthorized access, lateral movement, and privilege escalation.

The assessment resulted in a **full domain compromise**. Attackers successfully transitioned from initial password spraying to service account exploitation, eventually gaining Domain Administrator privileges via Resource-Based Constrained Delegation (RBCD) and secrets dumping. Two hosts (CAPTAIN and a Member server) were fully compromised.

**Key Metrics:**
*   **Hosts Compromised:** 2
*   **Accounts Compromised:** 5
*   **Outcome:** Full Domain Administrative Control

---

# Attack Path Summary

1.  **Initial Access:** Performed password spraying against the domain controller, identifying valid credentials for `skyler.white` and `hank.schrader`.
2.  **Service Account Exploitation:** Authenticated via SMB to identify service accounts. Performed Kerberoasting to extract hashes for `jesse.pinkman` and `walter.white`. Cracked hashes to obtain cleartext credentials.
3.  **Lateral Movement & Privilege Escalation:** Used `walter.white` credentials to perform remote command execution on `192.168.122.5` and `192.168.122.10`.
4.  **Full Domain Compromise:** Utilized RBCD misconfigurations (via `saul.goodman`) to elevate privileges on `192.168.122.5`. Executed `secretsdump.py` against the Domain Controller (`192.168.122.10`) to extract all domain hashes, including `KRBTGT`.

---

# Credentials Obtained

| Username | Password | Source | Method |
| :--- | :--- | :--- | :--- |
| skyler.white | Password123 | DC (192.168.122.10) | Password Spraying |
| hank.schrader | sHyangja210 | DC (192.168.122.10) | Password Spraying |
| jesse.pinkman | Wang0Tang0! | Service Account | Kerberoasting / Cracking |
| walter.white | Metho1o590oA$elry | Service Account | Kerberoasting / Cracking |
| saul.goodman | beTTer2caLL2me | ACL/BloodHound | Enumeration |

---

# Compromised Systems

*   **CAPTAIN (192.168.122.10):** Domain Controller. Fully compromised via service account abuse and subsequent credential extraction.
*   **MEMBER (192.168.122.5):** Windows Server 2016. Compromised via RBCD abuse and remote command execution.

---

# Findings & Vulnerabilities

### 1. Insecure SMB Configuration
*   **Evidence:** SMB Signing disabled; SMBv1 enabled on both targets.
*   **Impact:** Vulnerable to SMB relay attacks and potential man-in-the-middle exploitation.

### 2. Weak Password Policy / Password Spraying Success
*   **Evidence:** Valid credentials found for `skyler.white` and `hank.schrader`.
*   **Impact:** Unauthorized access to network resources and service account enumeration.

### 3. Kerberoastable Service Accounts
*   **Evidence:** Service accounts (`jesse.pinkman`, `walter.white`) possessed weak passwords allowing offline cracking.
*   **Impact:** Exposure of service account credentials, leading to broader network access.

### 4. Resource-Based Constrained Delegation (RBCD) Misconfiguration
*   **Evidence:** `saul.goodman` maintained RBCD rights to the Member server, facilitating privilege escalation.
*   **Impact:** Unauthorized impersonation of accounts and elevation of privileges.

---

# Timeline of Compromise

1.  **Reconnaissance:** Identified `polaris.local` domain and DC/Member host roles.
2.  **User Enumeration:** Identified `saul.goodman`, `skyler.white`, `hank.schrader`.
3.  **Authentication Testing:** Successfully performed password spraying for `skyler.white` and `hank.schrader`.
4.  **Kerberoasting:** Identified and cracked `jesse.pinkman` and `walter.white`.
5.  **Lateral Movement:** Remote command execution achieved on domain hosts.
6.  **Privilege Escalation:** Exploited RBCD to gain administrative control on Member server.
7.  **Final Compromise:** Executed `secretsdump.py` against the Domain Controller, achieving Domain Dominance.

---

# Recommendations

*   **Disable SMBv1:** Immediately deprecate SMBv1 across the domain.
*   **Enforce SMB Signing:** Require SMB signing for all network communications to prevent relay attacks.
*   **Password Policies:** Implement complex password requirements and account lockout policies to defeat password spraying.
*   **Audit RBCD:** Review `msDS-AllowedToActOnBehalfOfOtherIdentity` attributes on computer objects to identify and remove unauthorized delegation paths.
*   **Service Account Management:** Rotate service account passwords to high-entropy strings and monitor for Kerberoasting activity.