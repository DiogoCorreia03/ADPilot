The penetration test against the domain controller at `192.168.122.10` has been successfully completed. Initial reconnaissance identified a Windows Server 2016 domain controller within the `polaris.local` domain, with several services exposed, including SMB, LDAP, and MSSQL.

### Compromise Narrative
1.  **Reconnaissance**: Discovered active services and valid domain usernames (`skyler.white`, `hank.schrader`, `saul.goodman`) through `kerbrute`.
2.  **Initial Access**: A password spray/brute-force attempt identified a valid credential pair: `administrator` / `Passw0rd`.
3.  **Domain Compromise**: Using the compromised `administrator` credentials, full domain compromise was achieved by executing `secretsdump.py` against the domain controller, which successfully performed a DCSync to extract all NTDS.dit data, including NTLM hashes and Kerberos keys for all domain users and computer accounts.

### Credentials Obtained (Highlights)
*   **Administrator**: `Passw0rd` (Plaintext), `a87f3a337d73085c45f9416be5787d86` (NTLM)
*   **krbtgt**: `3bb183d552b48add82cbe2df0621ea45` (NTLM), `01c41628a0c61bc47e2e9da9c246f4201ba033136ef08a55c37688888614b33d` (AES256)
*   **skyler.white**: `58a478135a93ac3bf058a5ea0e8fdb71` (NTLM)
*   **jesse.pinkman**: `106d2a2df0019f0d8ea48f347545ca8f` (NTLM)
*   **walter.white**: `93bd3d67e83e52bcc0bd0c335cae3a47` (NTLM)
*   **hank.schrader**: `2007a8d98b2c2e00838573327b410e8c` (NTLM)
*   **saul.goodman**: `b218a7087535c8ac2518506bacb7343a` (NTLM)

### Findings
*   **Weak Password Policy**: The Domain Administrator account had a weak, guessable password (`Passw0rd`), allowing for simple credential discovery.
*   **DCSync Vulnerability**: Successful compromise of a Domain Administrator account led to full directory service compromise.
*   **SMBv1 Enabled**: SMBv1 is enabled on the domain controller, which is a legacy and insecure protocol.

### Recommendations
1.  **Immediate Credential Rotation**: Reset the passwords for all compromised accounts, particularly the Administrator account and KRBTGT.
2.  **Enforce Strong Password Policies**: Implement and enforce a robust password policy (complexity, length, rotation, history).
3.  **Disable Legacy Protocols**: Disable SMBv1 across the entire enterprise network.
4.  **Least Privilege Principle**: Review and restrict administrative permissions. Ensure that only necessary accounts have Domain Administrator or DCSync privileges.
5.  **Monitor for Anomalous Activity**: Audit logs for signs of DCSync and other suspicious administrative activity.