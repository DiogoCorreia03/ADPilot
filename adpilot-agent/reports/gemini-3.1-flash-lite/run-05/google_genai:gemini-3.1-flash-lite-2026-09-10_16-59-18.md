# Penetration Testing Report: polaris.local

## Executive Summary
The penetration test of the `polaris.local` domain environment was conducted to identify security weaknesses and evaluate the potential for unauthorized access. The assessment resulted in full domain-level compromise, starting from anonymous share enumeration and escalating through Active Directory Certificate Services (AD CS) misconfigurations. 

- **Highest Level of Compromise:** Domain Administrator
- **Compromised Hosts:** 2 (CAPTAIN, MEMBER)
- **Compromised Accounts:** 4 (skyler.white, jesse.pinkman, walter.white, Administrator)
- **Critical Observations:** The environment suffered from weak password policies, insecure SMB configurations, and exploitable AD CS templates (ESC1, ESC3).

---

## Attack Path Summary
1. **Initial Access:** Anonymous SMB null-session enumeration on `192.168.122.10` (CAPTAIN) allowed retrieval of `skyler.txt`, which contained a plaintext password hint.
2. **Credential Discovery:** The user `skyler.white` was compromised via brute-forcing using the recovered hint.
3. **Lateral Movement & Enumeration:** Authenticated access was used to perform Kerberoasting, AS-REP roasting, and LDAP enumeration, yielding credentials for `jesse.pinkman` and `walter.white`.
4. **Privilege Escalation:** Exploitation of AD CS templates (ESC3 to obtain a certificate for `walter.white`, then ESC1 to impersonate `Administrator`).
5. **Final Impact:** Domain-level compromise was achieved by leveraging the `Administrator` certificate for LDAP Schannel authentication, bypassing KDC restrictions.

---

## Credentials Obtained
| Username | Password | Source |
| :--- | :--- | :--- |
| `skyler.white` | `Password123` | Recovered from `skyler.txt` on SMB share |
| `jesse.pinkman` | `Wang0Tang0!` | Cracking AS-REP hash |
| `walter.white` | `Metho1o590oA$elry` | Cracking TGS-REP hash |
| `Administrator` | N/A (Certificate) | AD CS ESC1 impersonation |

---

## Compromised Systems
- **CAPTAIN (192.168.122.10):** Windows Server 2016. Compromised via SMB/MSSQL and used as a pivot for AD CS exploitation.
- **MEMBER (192.168.122.5):** Windows Server. Compromised via credential reuse.

---

## Findings & Vulnerabilities
1. **AD CS Misconfiguration (ESC1/ESC3):** Certificate templates were misconfigured to allow enrollment by low-privilege domain users and permitted subject alternative name (SAN) manipulation. This allowed full account impersonation, including the `Administrator`.
2. **Insecure SMB Configuration:** SMB signing was disabled, and SMBv1 was enabled on both servers, facilitating potential relay and interception attacks.
3. **Weak Password Policy:** Multiple users utilized easily guessable passwords, leading to successful brute-force and password-spraying outcomes.
4. **Anonymous SMB Exposure:** The `SharingIsCaring` share allowed anonymous read access, exposing sensitive configuration information and credentials.

---

## Lateral Movement & Privilege Escalation
- **Lateral Movement:** Demonstrated via SMB and MSSQL authentication using valid credentials (`skyler.white`, `walter.white`).
- **Privilege Escalation:** Successfully escalated from `walter.white` to `Administrator` using AD CS certificate template abuse (ESC1).

---

## Domain Compromise
Full domain compromise was achieved. By requesting an `Administrator` certificate via the ESC1 template and utilizing it for LDAP Schannel authentication, the agent successfully bypassed Kerberos authentication restrictions to achieve total control over `polaris.local`.

---

## Timeline of Compromise
1. **2026-09-10 14:51:** Anonymous access to `SharingIsCaring` share; discovered `skyler.white` credentials.
2. **2026-09-10 15:30:** Kerberoasted service accounts; cracked `jesse.pinkman` and `walter.white`.
3. **2026-09-10 15:45:** Identified AD CS ESC1/ESC3 templates.
4. **2026-09-10 16:00:** Exploited ESC3 to get `walter.white` certificate.
5. **2026-09-10 16:15:** Exploited ESC1 to get `Administrator` certificate.
6. **2026-09-10 16:30:** Authenticated as Domain Admin via LDAP Schannel.

---

## Assessment Statistics
- **Hosts Discovered:** 2
- **Hosts Compromised:** 2
- **Accounts Compromised:** 4
- **Successful Attack Paths:** 1
- **Privilege Escalations:** 1

---

## Recommendations
1. **AD CS Hardening:** Disable vulnerable certificate templates (ESC1, ESC2, ESC3). Restrict enrollment permissions to only necessary administrative accounts.
2. **Disable SMBv1 & Enable Signing:** Globally disable SMBv1 and enforce SMB signing on all workstations and servers.
3. **Disable Anonymous Access:** Restrict anonymous access to SMB shares and LDAP services on Domain Controllers.
4. **Credential Management:** Enforce a strong password policy and implement Multi-Factor Authentication (MFA) for all domain-joined assets.