During the assessment of the `polaris.local` domain, I successfully performed reconnaissance, service discovery, and credential harvesting.

### Key Findings
1.  **Enumerated Users:** Valid users including `saul.goodman`, `hank.schrader`, `skyler.white`, `walter.white`, and `jesse.pinkman` were identified.
2.  **Credential Harvest:**
    *   `skyler.white`: Found `Password123` via password spraying.
    *   `saul.goodman`: Found `beTTer2caLL2me` in the `description` field of his AD user account (discovered via `ldapdomaindump`).
    *   `jesse.pinkman`: Found `Wang0Tang0!` via offline cracking of an AS-REP response (`GetNPUsers.py` + `hashcat`).
3.  **Vulnerabilities & Misconfigurations:**
    *   **SMBv1:** Enabled on domain controllers and member servers, which is inherently insecure.
    *   **AD CS (AD CS ESC1):** Certificate templates were found to be misconfigured, allowing for potential privilege escalation (though attempts were hindered by RPC access issues).
    *   **Weak Password Management:** Plaintext passwords were found in AD user descriptions and test files on public shares.
    *   **Delegation Misconfigurations:** Found users with Unconstrained and Constrained delegation settings.
4.  **Database Access:** Accessed the `master` database on the MSSQL instance (`CAPTAIN\SQLEXPRESS`) using the `saul.goodman` credentials.

### Accomplishments
*   Achieved authenticated access to the domain using multiple service and standard user accounts.
*   Successfully performed reconnaissance and domain mapping.
*   Identified paths for potential domain privilege escalation via AD CS and Kerberos delegation abuse.
*   Identified that administrative credentials/NTDS.DIT could not be dumped directly due to RPC access restrictions (`rpc_s_access_denied`).

### Recommendations
*   **Disable SMBv1:** Immediately decommission SMBv1 across the entire network as it is obsolete and insecure.
*   **Rotate Credentials:** Immediately rotate all passwords identified in plaintext (e.g., `saul.goodman`) and conduct an audit of password storage practices.
*   **Remediate AD CS Misconfigurations:** Review and tighten certificate template permissions to prevent ESC1-style privilege escalation, and disable web enrollment over insecure channels.
*   **Enforce Least Privilege:** Limit user access to sensitive information shares (e.g., `ImportantNotes`) and restrict SQL server service account permissions.
*   **Audit Kerberos Delegation:** Review and restrict unconstrained and constrained delegation permissions to prevent lateral movement and credential theft.