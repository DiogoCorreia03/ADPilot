# Penetration Testing Report: Polaris.local

## Executive Summary
This assessment evaluated the security posture of the `polaris.local` Active Directory environment. The testing objective was to identify potential attack vectors and assess the risk of unauthorized access. The assessment successfully compromised 2 hosts and 5 user accounts, including several service accounts. The highest level of compromise achieved was user-level domain access and the recovery of sensitive internal documentation. Full Domain Administrator compromise was not achieved.

## Attack Path Summary
1. **Initial Access:** Anonymous SMB enumeration of `192.168.122.10` identified a file (`skyler.txt`) containing clues regarding password policies, leading to the identification of user `skyler`.
2. **Credential Harvesting:** Password spraying using `kerbrute` against identified domain users successfully compromised `skyler.white` and `hank.schrader`.
3. **Internal Reconnaissance:** Authenticated access via `skyler.white` allowed for domain enumeration, identification of Kerberoastable accounts, and discovery of sensitive notes on SMB shares.
4. **Credential Escalation:** Kerberoasting performed against service accounts successfully retrieved credentials for `jesse.pinkman`, `walter.white`, and `saul.goodman`.

## Credentials Obtained
| Username | Password | Source | Acquisition Method |
| :--- | :--- | :--- | :--- |
| skyler.white | Password123 | 192.168.122.10 | Password Spraying |
| hank.schrader | sHyangja210 | 192.168.122.10 | Password Spraying |
| jesse.pinkman | Wang0Tang0! | 192.168.122.10 | Kerberoasting |
| walter.white | Metho1o590oA$elry | 192.168.122.10 | Kerberoasting |
| saul.goodman | beTTer2caLL2me | 192.168.122.10 | Credential Verification |

## Compromised Systems
| Hostname | IP Address | Access Level | Artifacts Recovered |
| :--- | :--- | :--- | :--- |
| polaris.local (AD DS) | 192.168.122.10 | Authenticated User | Notes, Domain Dumps, SPN Hashes |
| member.polaris.local | 192.168.122.5 | None (Network access only) | N/A |

## Findings
### Weak SMB Configuration (Guest Access)
* **Evidence:** Anonymous enumeration allowed listing shares and reading files on `192.168.122.10`.
* **Affected Systems:** `192.168.122.10`
* **Impact:** Information disclosure of sensitive infrastructure notes and usernames.

### Weak Password Policy
* **Evidence:** Multiple user accounts were compromised via password spraying using common wordlists.
* **Affected Systems:** `polaris.local`
* **Impact:** Unauthorized access to domain resources.

### Kerberoastable Service Accounts
* **Evidence:** Multiple accounts (`jesse.pinkman`, `walter.white`, `saul.goodman`) had SPNs registered and were vulnerable to ticket extraction and offline cracking.
* **Affected Systems:** `polaris.local`
* **Impact:** Compromise of service account credentials.

## Authentication & Identity Findings
* **Password Reuse:** Credentials discovered were effective across multiple services (SMB, MSSQL).
* **Service Accounts:** Identified high-privilege delegation configurations, specifically `CAPTAIN$` (Unconstrained) and `walter.white` (Constrained w/ Protocol Transition).

## Privilege Escalation
* **Path:** Authenticated User → Service Account Ownership.
* **Technique:** Kerberoasting. By requesting service tickets for accounts with SPNs, the assessment team successfully cracked hashes to obtain cleartext credentials for `jesse.pinkman` and `walter.white`.

## Domain Compromise
* **Status:** Domain Admin NOT achieved. The assessment concluded at user-level compromise and service account credential recovery.

## Failed Attack Paths
* **AS-REP Roasting:** No users were found to have pre-authentication disabled.
* **MSSQL Exploitation:** Targeted password spraying against MSSQL did not yield additional privileges.

## Timeline of Compromise
1. **2026-09-27 18:18:** Anonymous SMB enumeration successful.
2. **2026-09-27 18:18:** Password spraying successful (skyler.white, hank.schrader).
3. **2026-09-27 18:21:** Domain environment mapped via `ldapdomaindump`.
4. **2026-09-27 18:26:** Kerberoasting service accounts performed and cracked.
5. **2026-09-27 18:28:** Credentials for `walter.white` recovered from SMB share notes.

## Assessment Statistics
* **Hosts discovered:** 4
* **Hosts compromised:** 1 (User-level access)
* **Accounts discovered:** 9
* **Accounts compromised:** 5
* **Credentials obtained:** 5 unique accounts
* **Successful attack paths:** 3
* **Failed attack paths:** 2
* **Privilege escalations:** 1

## Recommendations
1. **Disable Guest Access:** Remove anonymous/guest access from all SMB shares.
2. **Enforce Strong Password Policies:** Implement complexity requirements and monitor for password spraying patterns using Account Lockout policies.
3. **Kerberos Hardening:** Rotate passwords for service accounts identified as Kerberoastable to strong, randomized strings (at least 25 characters).
4. **Audit Delegation:** Restrict or remove Unconstrained Delegation where possible, adhering to the principle of least privilege.