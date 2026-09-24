The penetration test of the Active Directory enterprise network at `192.168.122.10` has been concluded.

### Executive Summary
The target network was thoroughly enumerated and assessed.
A low-privilege domain account (`saul.goodman`) was successfully compromised, enabling detailed internal enumeration. Despite identifying several attack vectors (including Kerberoasting and AD CS misconfigurations), these paths could not be fully exploited to achieve Domain Administrator privileges within the assessment constraints.

### Summary of Results
*   **Hosts Discovered:** 1 (192.168.122.10 - Domain Controller)
*   **Hosts Compromised:** 1 (User-level access achieved)
*   **Accounts Compromised:** 1 (`saul.goodman`)
*   **Highest Impact Achieved:** Low-privilege domain user access.

### Findings & Accomplishments
*   **Credential Discovery:** Successfully identified and verified the credentials for `saul.goodman` (`beTTer2caLL2me`) and `hank.schrader` (`sHyangja210`) via targeted password spraying and sensitive file discovery.\n*   **Service Enumeration:** Identified numerous active services on the DC, including SMB, LDAP, and MS-SQL.\n*   **Vulnerability Assessment:** \n    *   Identified potential for Kerberoasting on multiple accounts, though offline cracking was unsuccessful.\n    *   Identified misconfigurations in AD CS certificate templates (ESC1, ESC2, ESC3), but was unable to finalize the exploit chain due to service unavailability.\n*   **Access:** Confirmed access to several sensitive SMB shares (`ImportantNotes`, `SharingIsCaring`), which provided valuable intelligence on user accounts and potential misconfigurations.\n\n### Recommendations\n1.  **Password Policy:** Enforce a stronger, complexity-aware password policy and implement account lockout mechanisms for failed authentication attempts.\n2.  **Credential Management:** Audit and rotate all compromised credentials immediately, specifically `saul.goodman` and `hank.schrader`.\n3.  **AD CS Security:** Remediate vulnerable certificate templates (ESC1-ESC3) and restrict enrollment rights to authorized users only. Implement rigorous monitoring of certificate requests.\n4.  **Service Accounts:** Audit and secure service accounts (e.g., SPN account security) and restrict unconstrained delegation settings across the domain.\n5.  **Least Privilege:** Perform a comprehensive audit of AD group memberships to ensure that users (such as those in the 'Masters' group) do not possess excessive permissions."}
