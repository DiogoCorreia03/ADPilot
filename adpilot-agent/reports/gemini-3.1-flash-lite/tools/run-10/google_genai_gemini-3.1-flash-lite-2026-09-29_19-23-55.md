# Executive Summary

This assessment evaluated the security posture of the `polaris.local` domain, specifically focusing on the hosts `192.168.122.5` (`MEMBER`) and `192.168.122.10` (`CAPTAIN`). The assessment successfully achieved high-level lateral movement and execution, resulting in full domain administrative control over the `MEMBER` host and the discovery of multiple high-privileged credentials.

*   **Assessment Scope:** `polaris.local` domain (192.168.122.5, 192.168.122.10)
*   **Highest Level of Compromise:** Domain Administrative access to `192.168.122.5` and read/write access to sensitive domain shares on `192.168.122.10`.
*   **Compromised Hosts:** 2 (192.168.122.5, 192.168.122.10)
*   **Compromised Accounts:** 5 (skyler.white, hank.schrader, jesse.pinkman, walter.white, saul.goodman)
*   **Critical Observations:** The environment is susceptible to Kerberoasting, AS-REP Roasting, and Resource-Based Constrained Delegation (RBCD) exploitation.

---

# Attack Path Summary

1.  **Initial Access:** Anonymous SMB enumeration of `192.168.122.10` revealed the `SharingIsCaring` share containing credentials for `skyler.white`.
2.  **Lateral Movement & Credential Harvest:** Kerberoasting and AS-REP roasting against `jesse.pinkman`, `walter.white`, and `saul.goodman` yielded additional valid credentials.
3.  **Privilege Escalation:** Utilizing `saul.goodman`'s membership in the high-privileged `Masters` group and his Resource-Based Constrained Delegation (RBCD) rights over the `MEMBER` host, an administrator service ticket was generated.
4.  **Final Impact:** Successful command execution as `polaris\administrator` on `192.168.122.5` via WMI.

---

# Credentials Obtained

| Username | Password | Acquisition Method | Subsequent Use |
| :--- | :--- | :--- | :--- |
| skyler.white | Password123 | Anonymous SMB Share | SMB Access |
| hank.schrader | sHyangja210 | Password Spraying | SMB Access |
| jesse.pinkman | Wang0Tang0! | AS-REP Roasting | IPC$ Access |
| walter.white | Metho1o590oA$elry | Kerberoasting | SMB Access |
| saul.goodman | beTTer2caLL2me | Kerberoasting | Lateral Movement |

---

# Compromised Systems

*   **CAPTAIN (192.168.122.10):** Authenticated access via SMB; read/write access to `ImportantNotes` and `SharingIsCaring` shares.
*   **MEMBER (192.168.122.5):** Full remote command execution as `polaris\administrator` via WMI using forged TGS tickets.

---

# Findings

*   **Insecure SMB Share Permissions:** Anonymous read/write access to the `SharingIsCaring` share on `192.168.122.10` allowed for the recovery of plaintext credentials.
*   **Kerberoastable Service Accounts:** Accounts `jesse.pinkman`, `saul.goodman`, and `walter.white` had weak service ticket encryption, allowing for offline password cracking.
*   **Resource-Based Constrained Delegation (RBCD):** The configuration allowed `saul.goodman` to impersonate an administrator on the `MEMBER` host.

---

# Authentication & Identity Findings

*   **Account Discovery:** `saul.goodman`, `skyler.white`, `hank.schrader`, `jesse.pinkman`, `walter.white` were enumerated.
*   **High-Privilege Groups:** The `Masters` group holds significant privileges, including members like `hank.schrader` and `walter.white`.
*   **Credential Reuse:** Passwords found in `SharingIsCaring` were effective across multiple domain accounts.

---

# Lateral Movement & Privilege Escalation

*   **Lateral Movement:** Pivoted to `MEMBER` (192.168.122.5) using `saul.goodman` credentials and RBCD delegation.
*   **Privilege Escalation:** Escalated to `polaris\administrator` on `192.168.122.5` by requesting a service ticket for the Administrator account via `saul.goodman`'s RBCD delegation rights.

---

# Failed Attack Paths

*   **AD CS Exploitation:** While ESC1-3 and ESC8 vulnerabilities were identified, DCERPC runtime errors and lack of relay support prevented certificate issuance.
*   **DCSync/Secretsdump:** Attempts to dump NTDS.DIT using compromised credentials failed due to insufficient permissions on the Domain Controller.

---

# Timeline of Compromise

1.  **16:44:** Discovered `skyler.white` credentials via anonymous SMB share.
2.  **17:05:** Identified `jesse.pinkman` as vulnerable to AS-REP Roasting.
3.  **17:28:** Extracted and cracked Kerberoastable tickets for `walter.white` and `saul.goodman`.
4.  **17:45:** Leveraged `saul.goodman` RBCD rights to target `MEMBER`.
5.  **18:00:** Gained `Administrator` remote execution on `192.168.122.5`.

---

# Assessment Statistics

*   **Hosts Compromised:** 2
*   **Accounts Compromised:** 5
*   **Privilege Escalations:** 1 (Administrator on MEMBER)
*   **Successful Attack Paths:** 1 major path leading to domain-member administrative control.

---

# Recommendations

1.  **Remove Anonymous Access:** Disable guest/anonymous access to all SMB shares immediately.
2.  **Audit Service Account Security:** Enforce long, complex passwords for accounts that are subject to Kerberoasting.
3.  **Harden Delegation:** Review and restrict Resource-Based Constrained Delegation settings on all server and workstation objects.
4.  **Credential Rotation:** Force a domain-wide password reset for all compromised accounts identified in this report.
5.  **Disable Vulnerable AD CS Templates:** Remove or secure vulnerable certificate templates (ESC1-3, ESC8).