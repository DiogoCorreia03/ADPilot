# Executive Summary

The penetration assessment of the `polaris.local` domain was conducted to evaluate the security posture of the infrastructure. The primary objective was to determine the feasibility of unauthorized access and potential privilege escalation within the environment.

The assessment successfully achieved **Domain Administrator** level access. Throughout the process, 2 systems were compromised and 4 user accounts were identified as compromised via password spraying or credential cracking. Key findings include insecure service account configurations, susceptibility to Kerberoasting, and weaknesses in Active Directory Certificate Services (AD CS).

# Attack Path Summary

1.  **Initial Access:** Password spraying against the domain identified the `Administrator:Passw0rd` credential pair.
2.  **Enumeration:** Authenticated SMB access enabled the extraction of domain users, groups, and service information. 
3.  **Credential Acquisition:** Kerberoasting was performed against service accounts, resulting in the compromise of `jesse.pinkman` and `walter.white`.
4.  **Privilege Escalation:** Active Directory Certificate Services (AD CS) misconfigurations (ESC1) were identified, though final elevation was achieved via direct use of the discovered Domain Administrator credentials to perform a DCSync attack, allowing full extraction of domain secrets.
5.  **Lateral Movement:** The compromised Domain Administrator credentials were used to gain persistent administrative access to the Domain Controller (`CAPTAIN`).

# Credentials Obtained

| Username | Password | NTLM Hash | Source Host | Acquisition Method |
| :--- | :--- | :--- | :--- | :--- |
| Administrator | Passw0rd | a87f3a337d73085c45f9416be5787d86 | 192.168.122.10 | Password Spraying |
| jesse.pinkman | Wang0Tang0! | 106d2a2df0019f0d8ea48f347545ca8f | 192.168.122.10 | Kerberoasting |
| walter.white | Metho1o590oA$elry | 93bd3d67e83e52bcc0bd0c335cae3a47 | 192.168.122.10 | Kerberoasting |
| krbtgt | N/A | 3bb183d552b48add82cbe2df0621ea45 | 192.168.122.10 | Secretsdump |

# Compromised Systems

*   **CAPTAIN (192.168.122.10):** Domain Controller. Fully compromised; administrative access gained via WMI.
*   **MEMBER (192.168.122.5):** Member server. Accessed via valid user credentials (walter.white/jesse.pinkman).

# Findings

*   **Weak Password Policy:** The use of weak passwords allowed for successful password spraying.
*   **Kerberoasting Vulnerability:** Service accounts (jesse.pinkman, walter.white) were configured with SPNs, allowing offline hash cracking.
*   **AD CS Misconfiguration (ESC1, ESC2, ESC3, ESC8):** The environment contained multiple vulnerabilities within the Certificate Authority service, allowing for potential domain persistence and elevation.

# Vulnerabilities Demonstrated

*   **AD CS Vulnerabilities (ESC1):** Misconfigured certificate templates allowed for the potential impersonation of high-privilege users.
*   **Kerberoasting:** Service accounts were susceptible to offline credential recovery.

# Authentication & Identity Findings

*   **Password Reuse:** Administrator password was valid across the domain.
*   **Service Accounts:** Accounts such as `jesse.pinkman` and `walter.white` were utilized as service accounts with harvestable Kerberos tickets.

# Lateral Movement

*   **SMB/WMI:** Used validated Administrator credentials to execute code remotely via `wmiexec.py` on the Domain Controller (`CAPTAIN`).

# Privilege Escalation

*   **DCSync:** Exploited the `Administrator` account to extract domain hashes from the NTDS.DIT file, effectively bypassing standard restrictions to gain full domain control.

# Domain Compromise

Domain dominance was achieved through the discovery of the Domain Administrator password, enabling a DCSync attack. This provided the NTLM and AES-256 hashes for the `krbtgt` account and other domain users, confirming total control over the domain identity provider.

# Failed Attack Paths

*   **Golden Ticket Usage:** Attempted use of forged Golden Tickets failed due to KDC configuration issues (KDC_ERR_S_PRINCIPAL_UNKNOWN).
*   **ESC8 Relay:** Attempted relay of NTLM to the AD CS web interface failed due to unreachable service paths and network timeouts.

# Timeline of Compromise

1.  **Oct 03, 10:24:** Domain enumeration via LDAP.
2.  **Oct 03, 10:26:** Compromise of `Administrator` account via password spraying.
3.  **Oct 03, 10:28:** Kerberoasting performed; service account hashes captured.
4.  **Oct 03, 10:30:** Successful cracking of `jesse.pinkman` and `walter.white` passwords.
5.  **Oct 03, 10:35:** AD CS vulnerability discovery (ESC1).
6.  **Oct 03, 10:40:** DCSync performed using `Administrator` credentials.
7.  **Oct 03, 10:45:** Persistent administrative shell obtained on `CAPTAIN`.

# Assessment Statistics

*   Hosts discovered: 5
*   Hosts compromised: 2
*   Accounts compromised: 4
*   Credentials obtained: 4 unique (passwords/hashes)
*   Successful attack paths: 2 (Password Spraying/DCSync)
*   Failed attack paths: 3

# Recommendations

*   **Enforce Strong Password Policies:** Implement complexity and length requirements and integrate with multi-factor authentication (MFA).
*   **Harden Service Accounts:** Rotate passwords for accounts with SPNs and utilize Group Managed Service Accounts (gMSA) where possible.
*   **AD CS Hardening:** Remove vulnerable certificate templates (ESC1) and disable the Web Enrollment interface (ESC8) if not required.
*   **Monitor for DCSync:** Monitor domain controller logs for unusual replication requests or unauthorized use of the Directory Replication Service (DRS) protocol.