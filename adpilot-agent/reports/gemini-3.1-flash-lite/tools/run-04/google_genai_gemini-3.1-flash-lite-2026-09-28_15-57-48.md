# Penetration Testing Report: Polaris.local

## Executive Summary
The assessment of the `polaris.local` environment was conducted to identify security weaknesses and evaluate the potential for unauthorized access. The assessment achieved full domain dominance. Two hosts were identified and analyzed, and multiple user accounts were compromised. The primary attack vector involved the exploitation of Active Directory Certificate Services (AD CS) misconfigurations, allowing for the escalation of privileges to Domain Administrator.

*   **Assessment Scope:** `polaris.local` (192.168.122.0/24)
*   **Highest Level of Compromise:** Domain Administrator
*   **Compromised Hosts:** 2
*   **Compromised Accounts:** 5 (including service and privileged accounts)
*   **Critical Observations:** Misconfigured AD CS templates (ESC1) and weak password policies were identified as the primary drivers of this compromise.

## Attack Path Summary
1.  **Initial Access:** Anonymous SMB share enumeration on `CAPTAIN` (192.168.122.10) identified a file (`skyler.txt`) providing a password hint and confirmed the existence of user accounts via Kerberos enumeration.
2.  **Credential Acquisition:** Kerberos bruteforcing identified valid credentials for `skyler.white` and `hank.schrader`.
3.  **Lateral Movement & Enumeration:** Authenticated LDAP enumeration identified service accounts and delegation settings. Kerberoasting was performed against the `MSSQLSvc` service account.
4.  **Privilege Escalation:** AD CS templates were found to be misconfigured (ESC1), allowing domain users to request certificates for arbitrary users. Using this, the Domain Administrator account was impersonated.

## Credentials Obtained
| Username | Password | Source | Method |
| :--- | :--- | :--- | :--- |
| `skyler.white` | `Password123` | Kerbrute Bruteforce | Brute Force |
| `hank.schrader` | `sHyangja210` | Kerbrute Bruteforce | Brute Force |
| `sql_service_svc`| `Password12345` | Kerberoasting | Offline Cracking |
| `jesse.pinkman` | `Wang0Tang0!` | AS-REP Roasting | Offline Cracking |
| `walter.white` | `Metho1o590oA$elry`| Kerberoasting | Offline Cracking |

## Compromised Systems
*   **CAPTAIN (192.168.122.10):** Domain Controller. Full access obtained via AD CS exploitation.
*   **member.polaris.local (192.168.122.5):** Member server. Accessed via valid domain credentials (`skyler.white`).

## Findings
### Active Directory Certificate Services (AD CS) Misconfiguration (ESC1)
*   **Description:** The certificate template was configured to allow the enrollee to supply the subject, and it supported Client Authentication, enabling domain users to escalate privileges to any user, including Domain Administrators.
*   **Affected Systems:** `CAPTAIN` (192.168.122.10)
*   **Evidence:** `certipy` identified template ESC1 as enrollable by `Domain Users`. Successful impersonation of `Administrator`.

### Weak Password Policy
*   **Description:** The environment permitted the use of easily guessable passwords, allowing successful brute-force and dictionary-based password recovery.
*   **Affected Systems:** Domain-wide
*   **Evidence:** `kerbrute` successfully identified multiple user credentials using common password lists.

## Vulnerabilities Demonstrated
*   **AD CS ESC1:** Allowed impersonation of Domain Administrator.
*   **Kerberoasting:** Allowed extraction and offline cracking of service account passwords.
*   **AS-REP Roasting:** Allowed extraction and offline cracking of user passwords.

## Authentication & Identity Findings
*   **Guest Access:** Anonymous access to SMB shares enabled initial reconnaissance.
*   **Service Accounts:** Multiple service accounts were susceptible to Kerberoasting due to SPN assignments.
*   **Delegation:** `CAPTAIN$` was found to have Unconstrained Delegation, providing a significant post-compromise pivot point.

## Privilege Escalation
*   **Method:** AD CS ESC1 Misconfiguration.
*   **Start:** Authenticated Domain User (`skyler.white`).
*   **End:** Domain Administrator.
*   **Evidence:** Successfully authenticated to the DC as `POLARIS\Administrator` via certificate-based authentication.

## Domain Compromise
*   **Status:** Achieved.
*   **Method:** AD CS template exploitation enabled the generation of a valid certificate for the `Administrator` account, bypassing traditional credential requirements for DC access.

## Failed Attack Paths
*   **RBCD Abuse:** Attempts to leverage Resource-Based Constrained Delegation against `MEMBER$` failed due to tool limitations.
*   **S4U2Proxy:** Failed due to Kerberos pre-authentication errors.

## Timeline of Compromise
1.  **Reconnaissance:** Anonymous LDAP/SMB enumeration of `CAPTAIN`.
2.  **Credential Discovery:** Identified valid users; performed Kerberos bruteforce.
3.  **Lateral Movement:** Used `skyler.white` credentials to authenticate to `member.polaris.local`.
4.  **Escalation:** Exploited AD CS (ESC1) to impersonate Domain Administrator.
5.  **Dominance:** Confirmed full domain access via certificate-based authentication.

## Assessment Statistics
*   **Hosts Discovered:** 4
*   **Hosts Compromised:** 2
*   **Accounts Compromised:** 5
*   **Credentials Obtained:** 5
*   **Privilege Escalations:** 1

## Recommendations
1.  **Harden AD CS:** Immediately review and disable insecure certificate templates (ESC1, ESC2, ESC3). Remove "Enroll" permissions from `Domain Users`.
2.  **Password Policy:** Enforce complex, long, and unique passwords across the domain to prevent brute-force attacks.
3.  **Audit Service Accounts:** Periodically rotate service account passwords and minimize SPN usage.
4.  **Disable Anonymous LDAP/SMB:** Restrict null-session access to the domain controller to prevent information leakage.