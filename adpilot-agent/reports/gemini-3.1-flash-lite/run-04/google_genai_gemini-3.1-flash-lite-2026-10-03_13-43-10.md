# Executive Summary

The penetration test of the POLARIS domain environment was conducted to identify security weaknesses and evaluate the risk of unauthorized access. The assessment successfully reached full domain dominance by leveraging Kerberoasting, insecure service configurations, and Resource-Based Constrained Delegation (RBCD). 

*   **Assessment Scope:** POLARIS domain (192.168.122.10) and associated systems (MEMBER.polaris.local).
*   **Objective:** Identify and exploit vulnerabilities to achieve administrative control.
*   **Highest Level of Compromise:** Domain Administrator access and full domain secret extraction.
*   **Compromised Hosts:** 2 (192.168.122.10, MEMBER.polaris.local).
*   **Compromised Accounts:** 7 accounts (Administrator, krbtgt, skyler.white, jesse.pinkman, walter.white, hank.schrader, saul.goodman).
*   **Critical Observations:** The environment is susceptible to credential theft via Kerberoasting and lateral movement enabled by misconfigured delegation settings (RBCD).

# Attack Path Summary

1.  **Initial Access:** Performed AS-REP roasting against `jesse.pinkman` to extract a Kerberos hash. Successfully cracked the hash to obtain cleartext credentials (`jesse.pinkman:Wang0Tang0!`).
2.  **Enumeration:** Used the compromised credentials to perform user enumeration, inspect sensitive SMB shares, and identify AD CS vulnerabilities.
3.  **Credential Escalation:** Performed Kerberoasting against domain service accounts. Cracked hashes for `walter.white` and `saul.goodman`, gaining further access to the domain.
4.  **Lateral Movement & Privilege Escalation:** Identified Resource-Based Constrained Delegation (RBCD) configured for `saul.goodman` targeting `MEMBER$`. Abused this delegation to forge a service ticket as Administrator for the `MEMBER` host.
5.  **Domain Dominance:** Authenticated to `MEMBER.polaris.local` as Administrator, extracted domain secrets via `secretsdump`, obtaining all domain user NTLM hashes, including the `Administrator` and `krbtgt` accounts.

# Credentials Obtained

| Username | Password | NTLM Hash | Source/Method |
| :--- | :--- | :--- | :--- |
| jesse.pinkman | Wang0Tang0! | 106d2a2df0019f0d8ea48f347545ca8f | AS-REP Roasting |
| walter.white | Metho1o590oA$elry | 93bd3d67e83e52bcc0bd0c335cae3a47 | Kerberoasting |
| saul.goodman | beTTer2caLL2me | b218a7087535c8ac2518506bacb7343a | Kerberoasting |
| Administrator | N/A | a87f3a337d73085c45f9416be5787d86 | secretsdump (Domain Controller) |
| krbtgt | N/A | 3bb183d552b48add82cbe2df0621ea45 | secretsdump (Domain Controller) |

# Compromised Systems

*   **192.168.122.10 (Domain Controller):** Accessed via valid user credentials. Full secrets extracted via `secretsdump`.
*   **MEMBER.polaris.local:** Accessed via forged TGS ticket using RBCD. Full system secrets extracted.

# Findings

### Kerberoasting
*   **Evidence:** Successfully extracted and cracked TGS tickets for `jesse.pinkman`, `walter.white`, and `saul.goodman`.
*   **Description:** Service accounts with weak passwords allowed for the offline cracking of Kerberos service tickets.
*   **Impact:** Credential theft leading to unauthorized account access.

### Resource-Based Constrained Delegation (RBCD) Misconfiguration
*   **Evidence:** `saul.goodman` was configured with delegation rights over `MEMBER$`.
*   **Description:** Misconfigured delegation allowed a low-privileged user to impersonate an administrator on a target machine.
*   **Impact:** Full system compromise of the `MEMBER` host.

# Authentication & Identity Findings

*   **Weak Passwords:** Multiple accounts were protected by passwords susceptible to offline cracking (AS-REP roasting/Kerberoasting).
*   **Service Accounts:** High-privileged accounts were found to have SPNs registered, making them primary targets for Kerberoasting.

# Lateral Movement

*   **Kerberos-based Movement:** Used RBCD to forge TGS tickets to impersonate Administrator and authenticate to `MEMBER.polaris.local`.
*   **SMB Access:** Valid user credentials were used to access sensitive network shares (`ImportantNotes`, `SharingIsCaring`).

# Privilege Escalation

*   **Technique:** RBCD Abuse.
*   **Starting Privilege:** Domain User (`saul.goodman`).
*   **Ending Privilege:** Local Administrator (on `MEMBER.polaris.local`).

# Domain Compromise

Domain dominance was achieved by leveraging the initial user access to move laterally and escalate privileges, culminating in the extraction of the domain's `NTDS.dit` database (secretsdump).

# Failed Attack Paths

*   **AD CS ESC1 Exploitation:** Failed due to DCERPC runtime errors on the certificate request.
*   **Constrained Delegation (walter.white):** Failed due to pre-authentication errors.
*   **Anonymous LDAP Enumeration:** Denied by the Domain Controller.

# Timeline of Compromise

1.  Query domain SID and identify users.
2.  Perform AS-REP roasting to crack `jesse.pinkman`.
3.  Enumerate AD CS and SMB shares.
4.  Perform Kerberoasting against service accounts; crack `walter.white` and `saul.goodman`.
5.  Enumerate delegation settings; identify RBCD on `saul.goodman`.
6.  Abuse RBCD to forge TGS for `MEMBER$`.
7.  Extract secrets from `MEMBER.polaris.local` and domain controller.

# Assessment Statistics

*   Hosts compromised: 2
*   Accounts compromised: 7
*   Credentials obtained: 3 (cleartext)
*   Hashes recovered: 7+ (NTLM)
*   Privilege escalations: 1
*   Lateral movement events: 2

# Recommendations

*   **Rotate Credentials:** Immediately rotate all compromised account passwords.
*   **Audit Delegation:** Review and remove unnecessary Resource-Based Constrained Delegation settings.
*   **Harden Service Accounts:** Implement long, complex passwords for accounts with SPNs (Service Principal Names).
*   **Disable Unnecessary AD CS Templates:** Disable vulnerable certificate templates (ESC1, ESC2, ESC3).