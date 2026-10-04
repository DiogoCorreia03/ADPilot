# Penetration Testing Report: Polaris.local Assessment

## Executive Summary
The assessment of the `polaris.local` domain environment was conducted to identify security weaknesses and evaluate the risk of unauthorized access. The objective was successfully achieved, resulting in full domain compromise. The assessment identified 1 compromised host and 5 compromised user accounts, including the Domain Administrator. The primary attack vectors utilized were anonymous LDAP enumeration, password spraying, and Kerberoasting.

*   **Assessment Scope:** `polaris.local` domain (192.168.122.10)
*   **Highest Level of Compromise:** Domain Administrator / Full Domain Dominance
*   **Compromised Hosts:** 1 (CAPTAIN)
*   **Compromised Accounts:** 5
*   **Critical Observations:** The environment permitted anonymous LDAP queries, enabling full domain reconnaissance. Weak password policies facilitated successful password spraying, leading to initial access.

## Attack Path Summary
1.  **Initial Access:** Anonymous LDAP binding allowed for user enumeration. A password spray attack against the identified users resulted in the compromise of the `skyler.white` account.
2.  **Privilege Escalation & Lateral Movement:** Authenticated access via `skyler.white` allowed for further domain enumeration and Kerberoasting. 
3.  **Domain Compromise:** Continued password spraying with a comprehensive wordlist yielded credentials for the `Administrator` account, which was used to perform a secrets dump (DCSync) of the `NTDS.DIT` database, granting full domain control.

## Credentials Obtained
| Username | Password | Source | Method |
| :--- | :--- | :--- | :--- |
| skyler.white | Password123 | polaris.local | Password Spraying |
| Administrator | Passw0rd | polaris.local | Password Spraying |
| jesse.pinkman | Wang0Tang0! | polaris.local | Password Spraying |
| walter.white | Metho1o590oA$elry | polaris.local | Password Spraying |
| hank.schrader | sHyangja210 | polaris.local | Password Spraying |

## Compromised Systems
*   **Hostname:** CAPTAIN (192.168.122.10)
*   **Access Obtained:** Administrative (System)
*   **Privilege Level:** Domain Administrator
*   **Credentials Used:** `Administrator:Passw0rd`
*   **Artifacts Recovered:** `NTDS.DIT` database, SAM secrets, Krbtgt NTLM hash.

## Findings
### Anonymous LDAP Information Disclosure
*   **Evidence:** Successful anonymous LDAP bind against 192.168.122.10.
*   **Impact:** Attackers can perform full domain reconnaissance, including mapping users, computers, groups, and policies, without authentication.

### Weak Password Policy
*   **Evidence:** Multiple account passwords were recovered via password spraying (e.g., `Password123`, `Passw0rd`).
*   **Impact:** Facilitated rapid unauthorized access to multiple high-privilege accounts.

## Vulnerabilities Demonstrated
*   **Insecure LDAP Configuration:** Anonymous binds enabled. Enabled attackers to enumerate the domain environment.
*   **Weak Password Security:** Users employed easily guessable passwords, allowing for successful password spraying.

## Authentication & Identity Findings
*   **Discovered Users:** Administrator, skyler.white, jesse.pinkman, walter.white, hank.schrader, saul.goodman, krbtgt.
*   **Privileged Groups:** Domain Admins, Enterprise Admins, Schema Admins, Administrators, Group Policy Creator Owners.
*   **Service Accounts:** Potential service accounts identified via Kerberoasting (`jesse.pinkman`, `walter.white`, `saul.goodman`).

## Lateral Movement
*   **SMB Access:** Initial shares (`ADMIN$`, `C$`, `ImportantNotes`) were accessed using the `skyler.white` account.
*   **Domain-Wide Access:** Utilized `Administrator` credentials to access `C$` and `ADMIN$` shares, followed by credential dumping.

## Privilege Escalation
*   **Technique:** Password Spraying.
*   **Result:** Transitioned from a standard domain user (`skyler.white`) to Domain Administrator (`Administrator`).

## Domain Compromise
Full domain dominance was achieved via the compromise of the `Administrator` account. The `NTDS.DIT` file and `KRBTGT` hash were extracted, allowing for the generation of silver or golden tickets for long-term persistence.

## Failed Attack Paths
*   **AS-REP Roasting:** Failed due to the absence of the `UF_DONT_REQUIRE_PREAUTH` flag on target accounts.
*   **Kerberoast Cracking:** Failed to recover cleartext passwords from TGS hashes using provided wordlists.

## Timeline of Compromise
1.  **Reconnaissance:** Anonymous LDAP enumeration of `polaris.local`.
2.  **Exploitation:** Successful password spray against `skyler.white`.
3.  **Discovery:** Authenticated LDAP dump and SMB share enumeration.
4.  **Targeting:** Kerberoasting performed; failed to crack hashes.
5.  **Escalation:** Successfull password spray against `Administrator` account.
6.  **Full Compromise:** Secrets dumping via `Administrator` credentials.

## Assessment Statistics
*   **Hosts Discovered:** 1
*   **Hosts Compromised:** 1
*   **Accounts Discovered:** 7
*   **Accounts Compromised:** 5
*   **Credentials Obtained:** 5 unique user credentials
*   **Hashes Recovered:** Administrator (NTLM), Krbtgt (NTLM)
*   **Successful Attack Paths:** 1
*   **Failed Attack Paths:** 3
*   **Privilege Escalations:** 1

## Recommendations
*   **Disable Anonymous LDAP:** Restrict LDAP binds to authenticated users only.
*   **Enforce Strong Password Policies:** Implement complexity and length requirements via Group Policy to prevent password spraying.
*   **Implement MFA:** Require Multi-Factor Authentication for all domain-joined accounts.
*   **Monitor Service Accounts:** Periodically rotate passwords for service accounts and monitor for unusual Kerberos TGS requests.