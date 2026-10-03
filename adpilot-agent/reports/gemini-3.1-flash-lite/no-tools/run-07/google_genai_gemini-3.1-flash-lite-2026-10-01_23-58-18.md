# Penetration Testing Report - Domain: polaris.local

## Executive Summary
The security assessment of the `polaris.local` Active Directory environment (DC: 192.168.122.10) was successfully conducted. The environment was compromised, achieving full Domain Administrator access. The primary attack vector involved exploiting weak credential management (plaintext passwords in LDAP descriptions and password reuse) and utilizing these credentials to perform lateral movement and eventually compromise the Domain Controller.

*   **Initial Entry Point:** Anonymous SMB read access and password disclosure in LDAP description.
*   **Final Impact:** Full Domain compromise (Domain Administrator).
*   **Compromised Systems:** 1/1 (CAPTAIN).
*   **Compromised Accounts:** All domain users and the domain administrator account.

## Attack Path Summary
1.  **Initial Access:** Discovered anonymous SMB share `SharingIsCaring` on 192.168.122.10.
2.  **Credential Harvesting:** Found a note containing account info, leading to the discovery of user `skyler.white` and their credential (`Password123`) found through password spraying and context from `skyler.txt`.
3.  **Privilege Escalation & Mapping:** Using valid `skyler.white` credentials, performed LDAP enumeration and identified `saul.goodman` with his password (`beTTer2caLL2me`) stored in cleartext within his LDAP `description` attribute.
4.  **Lateral Movement:** Used `saul.goodman` credentials to query for Kerberoastable accounts. Attempted (and failed) to crack the hashes offline, however, decided to proceed with password spraying across known users.
5.  **Domain Compromise:** Successfully sprayed passwords and compromised the `Administrator` account with the password `Passw0rd`. Used the `Administrator` credentials with `secretsdump.py` to extract all domain hashes (DCSync).

## Credentials Obtained
*   **skyler.white**: `Password123`
*   **jesse.pinkman**: `Wang0Tang0!`
*   **walter.white**: `Metho1o590oA$elry`
*   **hank.schrader**: `sHyangja210`
*   **saul.goodman**: `beTTer2caLL2me`
*   **Administrator**: `Passw0rd`

## Findings
1.  **Cleartext Passwords in Active Directory:** User descriptions contained cleartext passwords.
2.  **Insecure SMB Configuration:** Anonymous access enabled on SMB shares allowed for initial information gathering.
3.  **Weak Password Policy:** Passwords like `Passw0rd` and `Password123` were easily compromised.
4.  **Password Reuse:** Credential reuse across multiple users facilitated the compromise.

## Recommendations
*   **Remediate Cleartext Passwords:** Immediately remove all passwords from LDAP `description` fields and enforce a password change policy.
*   **Enforce Strong Password Policy:** Implement complex password requirements and forbid common/weak passwords.
*   **Disable Anonymous Access:** Disable anonymous/guest access to SMB shares and restrict access to authenticated users only.
*   **Implement Monitoring:** Monitor for suspicious activity such as DCSync operations and anomalous LDAP queries.
*   **Rotate Credentials:** Perform a full domain-wide credential reset, especially for all administrative and service accounts.