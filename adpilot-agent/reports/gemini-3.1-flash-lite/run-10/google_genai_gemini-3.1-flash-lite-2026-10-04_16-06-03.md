# Executive Summary

**Assessment Scope:** Polaris internal network, including domain controllers and member servers.
**Overall Objective:** Identify and exploit security weaknesses to achieve domain-level access.
**Highest Level of Compromise:** Successful exploitation of Active Directory Certificate Services (AD CS) to impersonate the Domain Administrator.
**Compromised Hosts:** 1 (192.168.122.10 - CAPTAIN)
**Compromised Accounts:** 2 (jesse.pinkman, Administrator)
**Critical Observations:** The environment is vulnerable to multiple AD CS misconfigurations (ESC1-ESC4, ESC8). While the Domain Administrator was successfully impersonated via certificate-based authentication, limitations in the KDC/AD CS environment regarding PKINIT support prevented full extraction of domain-wide credentials via DCSync or similar techniques.

# Attack Path Summary

1.  **Initial Access:** Obtained credentials for `jesse.pinkman` (Wang0Tang0!) through enumeration of accessible SMB shares on `192.168.122.10`.
2.  **Internal Reconnaissance:** Leveraged `jesse.pinkman` credentials to identify critical misconfigurations in Active Directory Certificate Services (AD CS) using `Certipy`.
3.  **Privilege Escalation:** Exploited the ESC1 AD CS vulnerability to request a certificate for the `Administrator` account.
4.  **Impersonation:** Successfully authenticated as `POLARIS\Administrator` using the obtained `administrator.pfx` certificate.

# Credentials Obtained

| Username | Password | Source Host | Method |
| :--- | :--- | :--- | :--- |
| jesse.pinkman | Wang0Tang0! | 192.168.122.10 | File extraction (SMB share) |
| skyler.white | Password123 | 192.168.122.10 | File extraction (SMB share) |

# Compromised Systems

*   **Hostname:** CAPTAIN
    *   **IP Address:** 192.168.122.10
    *   **Access Obtained:** WMI access via `jesse.pinkman`, Administrator impersonation via AD CS.
    *   **Significant Artifacts:** `note.txt`, `skyler.txt` (credentials and internal warnings).

# Findings

### AD CS Vulnerabilities (ESC1-ESC4, ESC8)
*   **Evidence:** `Certipy` enumeration (20261004150339_Certipy.json).
*   **Affected Systems:** Domain Controller (Polaris Root CA).
*   **Description:** The certificate template configuration allows Domain Users to enroll and specify the subject of the certificate (ESC1), alongside other dangerous configurations (ESC2, ESC3, ESC4, ESC8).
*   **Impact:** Full domain account impersonation.

# Vulnerabilities Demonstrated

*   **ESC1 (AD CS Misconfiguration):** Allows low-privileged users to request certificates for arbitrary accounts, including domain admins. Demonstrated via `administrator.pfx` generation.

# Lateral Movement

*   **SMB Share Enumeration:** Used `jesse.pinkman` and `skyler.white` credentials to read sensitive documentation and password information from `ImportantNotes` and `SharingIsCaring` shares on `192.168.122.10`.
*   **WMI Access:** Demonstrated access to `192.168.122.5` and `192.168.122.10` using `jesse.pinkman` credentials.

# Privilege Escalation

*   **Technique:** ESC1 Certificate Misconfiguration.
*   **Starting Privilege:** Domain User (`jesse.pinkman`).
*   **Ending Privilege:** Domain Administrator (via certificate impersonation).
*   **Evidence:** `administrator.pfx` file and successful LDAP shell authentication as `POLARIS\Administrator`.

# Domain Compromise

Domain Administrator impersonation was achieved through AD CS exploitation. However, **full domain dominance via DCSync was not achieved**. Attempts to dump hashes failed due to a lack of PKINIT support on the KDC and insufficient DCRights for the compromised non-admin account.

# Failed Attack Paths

*   **DCSync/Secretsdump:** Failed due to `rpc_s_access_denied` and lack of PKINIT support.
*   **BloodHound Enumeration:** Failed due to likely account lockout or restrictive policies following initial enumeration activities.

# Timeline of Compromise

1.  **Enumerated SMB shares** on 192.168.122.10 using valid domain credentials.
2.  **Extracted credentials** (`jesse.pinkman`, `skyler.white`) from shared files.
3.  **Performed AD CS audit** using `Certipy`.
4.  **Exploited ESC1** to request an `Administrator` certificate.
5.  **Authenticated as Administrator** via certificate to the Domain Controller.

# Assessment Statistics

*   Hosts Discovered: 2
*   Hosts Compromised: 1
*   Accounts Compromised: 2
*   Credentials Obtained: 2
*   Privilege Escalations: 1
*   Successful Attack Paths: 1

# Recommendations

1.  **Harden AD CS:** Immediately restrict template enrollment rights. Remove "Domain Users" or "Authenticated Users" from templates vulnerable to ESC1-ESC4.
2.  **Disable Web Enrollment:** If not strictly required, disable the AD CS Web Enrollment role (ESC8).
3.  **Credential Hygiene:** Implement a password policy that prevents users from storing credentials in cleartext on internal file shares.
4.  **Monitor AD CS:** Implement monitoring for certificate requests, specifically focusing on templates with "Enroll" rights for non-privileged users.