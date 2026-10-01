# Penetration Testing Report: Polaris.local

## Executive Summary
The assessment of the `polaris.local` environment was conducted to identify security weaknesses and evaluate the potential for unauthorized access. The assessment achieved **full Domain Administrator compromise**. Two hosts (192.168.122.5 and 192.168.122.10) were evaluated, and multiple domain accounts were compromised. The primary attack vector involved anonymous service enumeration, credential harvesting through LDAP and share inspection, and exploitation of Active Directory Certificate Services (AD CS) misconfigurations.

## Attack Path Summary
1. **Initial Access:** Anonymous LDAP and SMB enumeration on 192.168.122.10 confirmed user naming conventions and permitted guest access to shares.
2. **Credential Discovery:** Valid accounts were identified via Kerberos user discovery. Credentials for `skyler.white` were validated. Further credentials (`saul.goodman`, `jesse.pinkman`) were recovered via LDAP attribute inspection and offline cracking of AS-REP hashes.
3. **Privilege Escalation:** AD CS template misconfigurations (ESC1) were identified. Using the `skyler.white` credentials, a certificate was requested for the `Administrator` account.
4. **Domain Dominance:** Authentication via the `Administrator` certificate provided full domain control, allowing for the extraction of the `NTDS.dit` database and all domain secrets.

## Credentials Obtained
| Username | Password | Source | Subsequent Use |
| :--- | :--- | :--- | :--- |
| `skyler.white` | `Password123` | Kerberos User Discovery | Share access, LDAP search, AD CS request |
| `jesse.pinkman` | `Wang0Tang0!` | AS-REP Roasting (Cracked) | Share access |
| `saul.goodman` | `beTTer2caLL2me` | LDAP attribute (description) | Share access |
| `hank.schrader` | `sHyangja210` | Password Spraying | Share access |

## Compromised Systems
| Hostname | IP Address | Access Level |
| :--- | :--- | :--- |
| `CAPTAIN` | 192.168.122.10 | Domain Administrator |
| `MEMBER` | 192.168.122.5 | Read access to shares |

## Findings
* **AD CS Vulnerability (ESC1):** Certificate templates were misconfigured to allow enrollment by low-privileged users with the ability to define the Subject Alternative Name (SAN). This enabled impersonation of the `Administrator` account.
* **Anonymous Guest Access:** The `SharingIsCaring` share on `CAPTAIN` allowed anonymous read/write access, facilitating the recovery of sensitive text files containing system information and password hints.
* **Sensitive Information in LDAP:** User `saul.goodman` contained a plaintext password in their account description field, readable by any authenticated domain user.

## Vulnerabilities Demonstrated
* **AD CS Misconfiguration (ESC1):** Affected `192.168.122.10`. Allowed full domain compromise.
* **Insecure Share Permissions:** Enabled anonymous enumeration and file exfiltration.

## Authentication & Identity Findings
* **AS-REP Roasting:** The `jesse.pinkman` account had Kerberos pre-authentication disabled, allowing offline brute-force of the user's password.
* **Password Reuse/Weakness:** Demonstrated by the recovery of passwords via simple LDAP attribute enumeration and guessing patterns.

## Lateral Movement
* **SMB Share Access:** Validated credentials were used to map network shares across the environment to identify configuration files and notes.

## Privilege Escalation
* **Technique:** AD CS Certificate Request (ESC1).
* **Evidence:** Certificate `administrator.pfx` generated and used for authentication.
* **Outcome:** Attained Domain Administrator privileges.

## Domain Compromise
Full domain compromise was achieved. Using the elevated certificate, the `secretsdump` tool was utilized to extract the `NTDS.dit` file, resulting in the acquisition of all domain account hashes, including `krbtgt` and `Administrator`.

## Failed Attack Paths
* **Null-session SMB Enumeration:** Repeated attempts failed due to restrictive policies, preventing broad enumeration of system shares without authentication.
* **Kerberoasting:** Attempted service hash extraction via `skyler.white` failed due to credential rejection, forcing a pivot to alternative attack vectors.

## Timeline of Compromise
1. **09-29 11:21:** Initial access via credential validation (`skyler.white`).
2. **09-29 11:23:** AS-REP roasting successful for `jesse.pinkman`.
3. **09-29 11:24:** Credentials for `saul.goodman` discovered via LDAP search.
4. **09-29 11:31:** AD CS misconfigurations identified.
5. **09-29 11:32:** Requested `Administrator` certificate.
6. **09-29 11:33:** Authenticated as Domain Administrator.
7. **09-29 11:34:** Extracted `NTDS.dit` domain secrets.

## Assessment Statistics
* **Hosts Compromised:** 2
* **Accounts Compromised:** 4
* **Privilege Escalations:** 1
* **Successful Attack Paths:** 1

## Recommendations
1. **Harden AD CS:** Disable or secure vulnerable certificate templates (ESC1). Remove permissions for low-privileged users to modify SAN.
2. **Disable Anonymous Access:** Restrict SMB guest access and anonymous LDAP binding.
3. **Audit LDAP Attributes:** Ensure sensitive information (passwords, notes) is not stored in object descriptions.
4. **Enforce Pre-Authentication:** Enable "Do not require Kerberos preauthentication" for all accounts to prevent AS-REP roasting.