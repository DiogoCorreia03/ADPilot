The penetration test against the `polaris.local` Active Directory network has been completed. 

### Summary of Findings
* **Initial Access:** Multiple low-privilege domain user accounts were compromised through password spraying and offline cracking of AS-REP roasted hashes.
    * `skyler.white` (Password123)
    * `saul.goodman` (beTTer2caLL2me)
    * `jesse.pinkman` (Wang0Tang0!)
    * `hank.schrader` (sHyangja210)
* **Enumeration:** Successfully enumerated domain users, groups, and AD CS template configurations.
* **Vulnerabilities Identified:**
    * **AD CS Misconfigurations (ESC1, ESC2, ESC3, ESC4, ESC8):** Identified multiple vulnerable certificate templates.
    * **Share Misconfigurations:** Sensitive information found in network shares (`ImportantNotes`, `SharingIsCaring`), including a cleartext password.
    * **Lack of Principle of Least Privilege:** Domain users had excessive permissions on AD objects.
* **Compromise:** While authenticated access to the network was achieved, Domain Administrator or SYSTEM-level compromise was not attained due to robust defensive controls and lack of further exploitable paths with the discovered credentials.

### Accomplished Objectives
* Enumerated all reachable hosts and services.
* Discovered multiple valid domain accounts.
* Harvested credentials and validated them against multiple services.
* Mapped AD structure, groups, and AD CS templates.

### Recommendations
1.  **Enforce Password Policy:** Implement and enforce a strong password policy to prevent the use of weak, easily guessable, or shared passwords.
2.  **Audit AD CS Templates:** Remove dangerous permissions (e.g., allow "Enroll" only to authorized users, remove "Enrollee Supplies Subject" flag) and disable vulnerable certificate templates (ESC1-ESC8).
3.  **Restrict Share Permissions:** Conduct an audit of network share permissions; remove unnecessary read/write access for low-privileged domain users.
4.  **Implement Principle of Least Privilege:** Review and limit excessive permissions granted to users over AD objects (e.g., WriteDacl, GenericAll) to prevent further privilege escalation attempts.
5.  **Audit Service Accounts:** Periodically check for and remediate misconfigured service accounts with unnecessary privileges or delegations.