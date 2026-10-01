# Penetration Testing Report: Polaris.local

## Executive Summary
This assessment evaluated the security posture of the `polaris.local` environment, specifically targeting hosts `192.168.122.5` and `192.168.122.10`. The objectives were to identify exploitable vulnerabilities, validate credential security, and test lateral movement capabilities. 

The assessment resulted in the successful compromise of the domain controller (`CAPTAIN`) and multiple domain accounts. The environment is highly susceptible to credential-based attacks due to weak password policies, Kerberoasting, and AS-REP roasting vulnerabilities. Full domain administrative control was not explicitly achieved, but significant access to the domain controller and sensitive service accounts was demonstrated.

*   **Hosts Compromised:** 1 (CAPTAIN - 192.168.122.10)
*   **Accounts Compromised:** 5 (skyler.white, jesse.pinkman, walter.white, saul.goodman, hank.schrader)
*   **Highest Privilege Level:** Domain User (with extensive service account access)

---

## Attack Path Summary
1.  **Initial Access:** Discovered `skyler.txt` via anonymous SMB on `CAPTAIN`, revealing the username "skyler". Password spraying confirmed `skyler.white:Password123`.
2.  **Service Account Compromise:** Using `skyler.white`, enumerated service accounts via `GetUserSPNs.py` (Kerberoasting). Cracked hashes for `jesse.pinkman` and `walter.white`.
3.  **Privilege/Identity Escalation:** Performed AS-REP Roasting against `jesse.pinkman`, confirming the previously cracked credentials.
4.  **Credential Discovery:** Identified a plaintext password hint for `saul.goodman` (`beTTer2caLL2me`) in the LDAP description field, which was validated against the domain.

---

## Credentials Obtained

| Username | Password | Source |
| :--- | :--- | :--- |
| skyler.white | Password123 | skyler.txt (SMB) |
| jesse.pinkman | Wang0Tang0! | Kerberoasting / AS-REP Roasting |
| walter.white | Metho1o590oA$elry | Kerberoasting |
| saul.goodman | beTTer2caLL2me | LDAP (Description) |

---

## Compromised Systems
*   **CAPTAIN (192.168.122.10):** Domain Controller. Accessed via SMB and LDAP using valid domain credentials (`jesse.pinkman`, `walter.white`, `saul.goodman`).

---

## Findings
*   **Sensitive Information in Public Shares:** `skyler.txt` containing cleartext password hints was readable anonymously.
*   **Weak Password Policy:** Multiple accounts used weak, predictable passwords easily susceptible to offline cracking or spraying.
*   **Kerberoastable Service Accounts:** Accounts `jesse.pinkman`, `walter.white`, and `saul.goodman` were vulnerable to TGS-REP extraction.
*   **AS-REP Roasting:** `jesse.pinkman` was configured without Kerberos pre-authentication, allowing offline hash extraction.
*   **Cleartext Password in LDAP:** `saul.goodman` account description contained the user's password.

---

## Vulnerabilities Demonstrated
*   **Insecure SMB Configuration:** Anonymous access enabled on `CAPTAIN` allowed initial reconnaissance.
*   **Weak Service Account Credentials:** Enabled offline cracking of service account hashes.
*   **LDAP Information Disclosure:** Anonymous LDAP binds provided internal domain structure and Naming Contexts.

---

## Authentication & Identity Findings
*   **Guest/Anonymous Access:** Enabled on `192.168.122.10`.
*   **Service Accounts:** `jesse.pinkman`, `walter.white`, and `saul.goodman` were identified as targets for Kerberoasting.
*   **Delegation Misconfigurations:** `CAPTAIN$` (Unconstrained), `walter.white` (Constrained w/ Protocol Transition), and `saul.goodman` (RBCD) present significant lateral movement risks.

---

## Timeline of Compromise
1.  **09-28-12:10:** Anonymous SMB enumeration reveals `skyler.txt`.
2.  **09-28-12:12:** Validated `skyler.white:Password123`.
3.  **09-28-12:15:** Kerberoasted service accounts; cracked hashes for `jesse.pinkman` and `walter.white`.
4.  **09-28-12:19:** AS-REP roasted `jesse.pinkman`.
5.  **09-28-12:21:** Enumerated LDAP; discovered `saul.goodman` password in description.

---

## Assessment Statistics
*   **Hosts Discovered:** 2
*   **Hosts Compromised:** 1
*   **Accounts Compromised:** 5
*   **Hashes Recovered:** 3 (TGS-REP) + 1 (AS-REP)
*   **Successful Attack Paths:** 1

---

## Recommendations
1.  **Disable Anonymous Access:** Disable guest access to all SMB shares and restrict anonymous LDAP bind.
2.  **Enforce Strong Password Policies:** Implement complexity and rotation requirements to prevent the use of weak passwords like "Password123".
3.  **Audit Service Accounts:** Periodically rotate passwords for service accounts and avoid assigning them highly privileged roles.
4.  **Remove Sensitive Metadata:** Ensure user objects (description fields) and shared files do not contain passwords or sensitive internal configuration details.
5.  **Disable Unnecessary Delegation:** Reconfigure accounts currently set to Unconstrained or Constrained delegation to follow the Principle of Least Privilege.