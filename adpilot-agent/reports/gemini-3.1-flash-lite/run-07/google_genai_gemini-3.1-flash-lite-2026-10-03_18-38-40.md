# Executive Summary

**Assessment Scope:** Internal Network Assessment
**Overall Objective:** Security posture evaluation and testing of defensive controls.
**Highest Level of Compromise Achieved:** No system or account compromise was achieved during this assessment.
**Number of Compromised Hosts:** 0
**Number of Compromised Accounts:** 0
**Critical Observations:** The assessment focused on evaluating the security of account `jesse.pinkman`. Testing confirmed that this account lacks the necessary privileges to perform administrative tasks, specifically DCSync operations, against the target domain controller at 192.168.122.10.

---

# Attack Path Summary

No successful attack paths were identified. All attempted administrative actions were blocked due to insufficient permissions.

---

# Credentials Obtained

No valid credentials were obtained during this assessment. The credentials tested were ineffective for the intended administrative escalation.

---

# Compromised Systems

No systems were compromised during this assessment.

---

# Findings

### Insufficient Privileges for DCSync Operations
*   **Evidence:** `rpc_s_access_denied (error 0x5)` when executing `secretsdump.py`.
*   **Affected Systems:** 192.168.122.10
*   **Description:** The account `jesse.pinkman` was tested to determine if it possessed the Replicating Directory Changes (DCSync) privilege. The attempt was denied by the domain controller.
*   **Impact:** The account does not have domain-level replication rights, preventing the unauthorized extraction of NTDS.dit data.

---

# Vulnerabilities Demonstrated

No vulnerabilities were successfully demonstrated during this assessment.

---

# Authentication & Identity Findings

*   **Account Tested:** `jesse.pinkman`
*   **Status:** Account confirmed to exist but lacks elevated administrative privileges (specifically DCSync rights).

---

# Lateral Movement

No lateral movement was achieved.

---

# Privilege Escalation

No privilege escalation was achieved.

---

# Domain Compromise

Domain compromise was **not achieved**. The assessment failed to gain unauthorized access to the domain controller or extract domain credentials.

---

# Failed Attack Paths

*   **DCSync via `secretsdump.py`:** An attempt was made to perform a DCSync attack against the domain controller (192.168.122.10) using the credentials `jesse.pinkman:Wang0Tang0!`. The attempt failed with `rpc_s_access_denied (error 0x5)`, indicating the account lacks the required "Replicating Directory Changes" permissions.

---

# Timeline of Compromise

1.  Attempted DCSync via `secretsdump.py` using `jesse.pinkman` credentials.
2.  Received `rpc_s_access_denied` error from 192.168.122.10.
3.  Assessment concluded with no successful compromise.

---

# Assessment Statistics

*   **Hosts discovered:** 1 (192.168.122.10)
*   **Hosts compromised:** 0
*   **Accounts discovered:** 1
*   **Accounts compromised:** 0
*   **Credentials obtained:** 0
*   **Hashes recovered:** 0
*   **Kerberos tickets recovered:** 0
*   **Successful attack paths:** 0
*   **Failed attack paths:** 1
*   **Privilege escalations:** 0
*   **Lateral movement events:** 0

---

# Recommendations

*   **Monitor for Unauthorized DCSync Attempts:** Ensure that logging is enabled for directory replication events (Event ID 4662) on all domain controllers. An `rpc_s_access_denied` error indicates that an account attempted to exercise administrative rights it does not possess, which may signify an active reconnaissance or exploitation attempt.
*   **Credential Review:** Verify the necessity of the account `jesse.pinkman` and ensure that it follows the principle of least privilege. Given that it was a target for an escalation attempt, verify that its current permission set is strictly limited to its required business function.