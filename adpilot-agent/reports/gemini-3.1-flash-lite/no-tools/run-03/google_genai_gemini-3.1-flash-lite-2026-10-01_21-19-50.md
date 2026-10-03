The penetration test against the domain controller at `192.168.122.10` has been successfully completed.

### Assessment Overview
- **Domain:** `polaris.local`
- **Domain Controller:** `CAPTAIN` (`192.168.122.10`)
- **Compromise Status:** Full Domain Compromise achieved.
- **Initial Access:** Valid credentials for the `Administrator` account were identified via targeted password spraying against the `ldap` service.
- **Privilege Escalation & Lateral Movement:** Following `Administrator` compromise, `secretsdump.py` was used to extract all domain user hashes from the `NTDS.dit` file via the DRSUAPI method, confirming complete control over the Active Directory environment.

### Compromised Credentials
The following credentials were recovered through password spraying and offline cracking of captured NTLM hashes:

| Username | Plaintext Password | Method |
| :--- | :--- | :--- |
| `Administrator` | `Passw0rd` | Online Password Spray (LDAP) |
| `skyler.white` | `Password123` | Offline Cracking (NTLM) |
| `jesse.pinkman` | `Wang0Tang0!` | Offline Cracking (NTLM) |
| `walter.white` | `Metho1o590oA$elry` | Offline Cracking (NTLM) |

### Key Findings
1.  **Weak Password Policies:** The domain lacked enforced password complexity and lockout policies, allowing successful password spraying and offline cracking of weak user passwords.
2.  **Insecure SMB Configuration:** `SMBv1` is enabled on the domain controller, and SMB signing is not required, increasing vulnerability to NTLM relay and related attacks.
3.  **Sensitive Information Disclosure:** Sensitive information, including a note confirming potential security risks, was accessible via unauthenticated/low-privilege access to the `ImportantNotes` SMB share.
4.  **Domain Compromise:** Full control of the domain was obtained, including the `krbtgt` account hash, enabling the creation of Golden Tickets.

### Recommendations
- **Enforce Strong Password Policies:** Implement and enforce a complex password policy, including minimum length and history requirements.
- **Disable Legacy Protocols:** Disable `SMBv1` and ensure `SMB Signing` is mandatory for all communications.
- **Credential Management:** Audit and rotate all compromised passwords immediately. Implement Managed Service Accounts (MSAs) for services where applicable.
- **Restrict Access:** Properly configure SMB share permissions to restrict access to sensitive data and system files.
- **Ongoing Monitoring:** Implement robust logging and monitoring for abnormal authentication patterns, such as multiple failed login attempts or mass export of domain secrets.