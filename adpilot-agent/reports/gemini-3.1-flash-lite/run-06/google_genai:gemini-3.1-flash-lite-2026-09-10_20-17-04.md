# Penetration Testing Report: Polaris.local

## Executive Summary
The security assessment of the `polaris.local` environment focused on identifying vulnerabilities within Active Directory services and associated network infrastructure. The assessment successfully identified several valid user accounts, recovered multiple passwords through Kerberoasting and AS-REP roasting, and identified a critical misconfiguration in Active Directory Certificate Services (AD CS). While the assessment demonstrated a pathway to request high-privileged certificates, full domain dominance via DCSync or credential dumping was not achieved due to environmental restrictions.

*   **Scope:** 192.168.122.5 (MEMBER), 192.168.122.10 (CAPTAIN)
*   **Overall Objective:** Identify and exploit vulnerabilities to compromise Active Directory.
*   **Highest Level of Compromise:** Authenticated domain user access with the ability to request certificates for privileged users.
*   **Compromised Hosts:** 1 (192.168.122.10)
*   **Compromised Accounts:** 5
*   **Critical Observations:** Weak password policies, permissive share access, and exploitable AD CS templates.

## Attack Path Summary
1.  **Initial Access:** Obtained credentials for `skyler.white` and `hank.schrader` via anonymous access to the "SharingIsCaring" SMB share.
2.  **Enumeration:** Authenticated to LDAP using `skyler.white` and `saul.goodman` (discovered via LDAP enumeration) to map the domain structure.
3.  **Privilege Escalation & Credential Harvesting:** Performed Kerberoasting and AS-REP roasting using `saul.goodman` credentials, resulting in the compromise of `jesse.pinkman` and `walter.white`.
4.  **Exploitation:** Identified an ESC1 misconfiguration in AD CS. Successfully requested an Administrator certificate, though downstream authentication using this certificate was restricted by KDC configuration.

## Credentials Obtained
| Username | Password | Source |
| :--- | :--- | :--- |
| skyler.white | Password123 | SMB Share (SharingIsCaring) |
| hank.schrader | sHyangja210 | SMB Share (SharingIsCaring) |
| saul.goodman | beTTer2caLL2me | LDAP Enumeration |
| jesse.pinkman | Wang0Tang0! | Offline Cracking (AS-REP Roast) |
| walter.white | Metho1o590oA$elry | Offline Cracking (Kerberoast) |

## Compromised Systems
*   **CAPTAIN (192.168.122.10):** Domain Controller. Accessed via SMB and authenticated LDAP queries.
*   **MEMBER (192.168.122.5):** Member Server. Accessed via SMB (CertEnroll share).

## Findings
### 1. Insecure SMB Share Permissions
*   **Evidence:** "SharingIsCaring" share on 192.168.122.10 allowed anonymous read/write access.
*   **Impact:** Disclosure of plaintext passwords and internal communications.
### 2. Weak Password Policies
*   **Evidence:** Account passwords were recovered via offline cracking and information disclosure.
*   **Impact:** High susceptibility to brute force and dictionary attacks.
### 3. AD CS ESC1 Misconfiguration
*   **Evidence:** 'ESC1' template allows enrollment with full domain control.
*   **Impact:** Ability to forge certificates for any domain user, including Domain Administrators.

## Vulnerabilities Demonstrated
*   **AD CS Template Misconfiguration (ESC1):** The 'ESC1' certificate template was found to be misconfigured, allowing for potential privilege escalation via certificate forgery.
*   **Kerberoasting:** Demonstrated by requesting service tickets for service accounts and cracking them offline.
*   **AS-REP Roasting:** Demonstrated by capturing and cracking the pre-authentication hash for `jesse.pinkman`.

## Authentication & Identity Findings
*   **Discovered Users:** Administrator, Guest, DefaultAccount, krbtgt, skyler.white, jesse.pinkman, walter.white, hank.schrader, saul.goodman.
*   **Password Policy:** Minimum length 7, Max age ~42 days. No account lockout threshold.
*   **Delegation:** `CAPTAIN$` has Unconstrained Delegation; `walter.white` has Constrained Delegation w/ Protocol Transition.

## Lateral Movement
*   **SMB:** Successfully accessed shares on 192.168.122.10 and 192.168.122.5 using validated user credentials.

## Privilege Escalation
*   **Starting Privilege:** Standard Domain User (`skyler.white`)
*   **Ending Privilege:** Ability to request administrative certificates (via AD CS ESC1).

## Domain Compromise
Domain dominance was not achieved. Attempts to perform `secretsdump` or access NTDS.dit failed due to KDC-level restrictions and authentication errors.

## Timeline of Compromise
1.  **Enumerated SMB:** Discovered "SharingIsCaring" on 192.168.122.10.
2.  **Identified Users:** Performed Kerberos user enumeration.
3.  **Authentication:** Accessed shares; gathered credentials for `skyler.white` and `hank.schrader`.
4.  **LDAP Mapping:** Enumerated domain users; found `saul.goodman` credentials.
5.  **Offline Attacks:** Performed Kerberoasting/AS-REP roasting; cracked `jesse.pinkman` and `walter.white`.
6.  **AD CS Abuse:** Identified ESC1; requested Administrator certificate.

## Assessment Statistics
*   **Hosts Discovered:** 2
*   **Accounts Compromised:** 5
*   **Credentials Obtained:** 5
*   **Successful Attack Paths:** 1 (AD CS escalation)

## Recommendations
1.  **Restrict SMB Access:** Remove anonymous read/write permissions from the "SharingIsCaring" share.
2.  **Enforce Strong Passwords:** Implement a more stringent password policy (length and complexity) and rotate all compromised credentials.
3.  **Harden AD CS:** Review and modify certificate templates; disable enrollment for insecure templates like ESC1.
4.  **Audit Delegation:** Review and restrict Unconstrained and Constrained delegation settings where not explicitly required by business functions.