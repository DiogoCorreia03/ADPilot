# Executive Summary

**Assessment Scope:** This penetration test focused on the security posture of the provided network environment, specifically targeting the domain controller located at 192.168.122.10.

**Overall Objective:** To evaluate the security of domain-level authentication mechanisms and identify potential pathways for unauthorized credential retrieval.

**Highest Level of Compromise:** No domain-level compromise or successful data extraction was achieved. 

**Assessment Result:** The assessment concluded without achieving unauthorized access to privileged domain credentials or compromising the target host.

---

# Attack Path Summary

No successful attack paths were identified. An attempt to extract credentials via `secretsdump.py` against the domain controller was performed using the credentials `hank.schrader:sHyangja210`, but this operation failed due to a protocol-level error.

---

# Credentials Obtained

No valid credentials were recovered during this assessment beyond those provided for testing purposes.

---

# Compromised Systems

No systems were compromised during this assessment.

---

# Findings

### Failed DCSync Attempt
* **Evidence:** `DRSR SessionError: code: 0x20f7 - ERROR_DS_DRA_BAD_DN`
* **Affected Systems:** 192.168.122.10
* **Description:** An attempt to perform an authenticated `secretsdump.py` operation using the `hank.schrader` account failed. The error `ERROR_DS_DRA_BAD_DN` indicates that the request failed to map the distinguished name (DN) of the target account (Administrator) correctly or lacked the requisite permissions to perform a directory replication service (DRS) request.
* **Impact:** The confidentiality of domain secrets remained intact during this operation.

---

# Vulnerabilities Demonstrated

No vulnerabilities were successfully exploited during this assessment.

---

# Authentication & Identity Findings

* **Account Usage:** The account `hank.schrader` was tested against the target domain infrastructure but lacked the necessary permissions to perform administrative data extraction (DCSync).

---

# Lateral Movement

No lateral movement was demonstrated.

---

# Privilege Escalation

No privilege escalation was demonstrated.

---

# Domain Compromise

Domain compromise was **not achieved**.

---

# Failed Attack Paths

* **Credential-based Secret Extraction:** An attempt to utilize `secretsdump.py` to extract the Administrator's NT hash from 192.168.122.10 failed. The error suggests that the account `hank.schrader` does not have the "Replicating Directory Changes" or "Replicating Directory Changes All" permissions required to perform a DCSync attack.

---

# Timeline of Compromise

1. **Attempted Credentials-based DCSync:** Executed `secretsdump.py` against 192.168.122.10 using `hank.schrader:sHyangja210`.
2. **Failure:** Operation terminated due to `DRSR SessionError: code: 0x20f7`.

---

# Assessment Statistics

* **Hosts discovered:** 1
* **Hosts compromised:** 0
* **Accounts compromised:** 0
* **Credentials obtained:** 0
* **Hashes recovered:** 0
* **Kerberos tickets recovered:** 0
* **Successful attack paths:** 0
* **Failed attack paths:** 1
* **Privilege escalations:** 0
* **Lateral movement events:** 0

---

# Recommendations

* **Audit Directory Replication Permissions:** The failure of the `secretsdump` attempt suggests that standard domain users are correctly prevented from executing DCSync operations. Ensure that non-administrative accounts remain restricted from performing Directory Replication Service (DRS) actions.
* **Monitor for Unauthorized DCSync Activity:** While the attack failed, attempts to perform DCSync operations by non-privileged accounts should be monitored via Security Event Logs (e.g., Event ID 4662 or 4624) to identify potentially malicious internal actors or compromised accounts.