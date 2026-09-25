# Penetration Testing Report - Polaris Domain

## Executive Summary
The security assessment of the `polaris.local` domain controller (`192.168.122.10`) was conducted to identify vulnerabilities and potential attack paths. The assessment resulted in the discovery of multiple user accounts, the identification of a misconfigured SMB share, and the successful compromise of a domain user account via AS-REP roasting. While Domain Admin access was not achieved, the identified vulnerabilities represent a significant risk to the organization.

## Attack Path Summary
1.  **Initial Access:** An SMB NULL session allowed the enumeration of domain users and identified an exposed plaintext password for the `saul.goodman` account in the user description field.
2.  **Credential Harvesting:** Accessing the `ImportantNotes` and `SharingIsCaring` SMB shares using the `saul.goodman` credentials allowed for the discovery of internal notes, confirming insecure practices (password storage in shares).
3.  **Privilege Escalation (Account):** By performing AS-REP roasting against all enumerated domain users, an AS-REP hash was captured for `jesse.pinkman`. This hash was subsequently cracked offline, providing valid credentials for the `jesse.pinkman` user account.

## Credentials Obtained
| Username | Password (if recovered) | Method |
| :--- | :--- | :--- |
| saul.goodman | beTTer2caLL2me | Enumerated from SMB user description |
| jesse.pinkman | Wang0Tang0! | AS-REP roasting and offline cracking |

## Findings & Demonstrated Vulnerabilities
*   **NULL Session Enabled:** Anonymous SMB connections allowed the enumeration of domain users and system information.
*   **Plaintext Password Storage:** User passwords were found stored in plain text within AD user descriptions and accessible network shares.
*   **Kerberos AS-REP Roasting:** Lack of Kerberos pre-authentication enabled the extraction of hashes for domain users, leading to credential compromise.
*   **Insecure SMB Configuration:** The domain controller has SMBv1 enabled and signing disabled, which facilitates various man-in-the-middle and relay attacks.

## Recommendations
*   **Disable SMBv1:** Disable the deprecated and insecure SMBv1 protocol.
*   **Enforce SMB Signing:** Require SMB signing on all domain controllers and network shares.
*   **Secure AD Configurations:** Disable NULL sessions and anonymous LDAP binds.
*   **Implement Strong Password Policy:** Enforce password complexity requirements and regular rotation, and forbid storing passwords in insecure locations (e.g., AD description fields or cleartext files).
*   **Disable AS-REP Roasting Vulnerability:** Ensure all accounts have "Do not require Kerberos preauthentication" disabled (default setting).
*   **Audit Access Rights:** Regularly audit permissions for all file shares and Active Directory objects to follow the principle of least privilege.