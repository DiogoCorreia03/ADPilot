# Penetration Testing Report

---

## Executive Summary

During this assessment, a security evaluation was performed against the Active Directory domain `polaris.local` and its associated hosts (`192.168.122.10` and `192.168.122.5`). The primary objective was to evaluate the security posture of the environment, identify vulnerabilities, and determine the extent of potential unauthorized access.

The assessment achieved unauthorized access to valid user credentials via anonymous file share enumeration, allowing for subsequent Active Directory enumeration, Kerberoasting hash extraction, and Active Directory delegation configuration analysis. 

### Key Assessment Statistics
* **Hosts Discovered:** 2 (`192.168.122.10` [CAPTAIN], `192.168.122.5` [MEMBER])
* **Hosts Compromised:** 1 (Access via valid user credentials)
* **Accounts Discovered:** 9 domain user/computer accounts
* **Credentials Obtained:** Valid credentials for `skyler.white`, a created machine account (`WORKSTATION01$`), and multiple service ticket hashes via Kerberoasting.
* **Highest Level of Compromise:** Domain User access with configured Active Directory delegation paths (Unconstrained Delegation on `CAPTAIN$` and `jesse.pinkman`, Constrained Delegation on `walter.white`, and Resource-Based Constrained Delegation on `MEMBER$`).

---

## Attack Path Summary

### Attack Path 1: Anonymous Information Disclosure to Domain User Access
1. **Initial Access / Reconnaissance:** Anonymous SMB enumeration against `192.168.122.10` (CAPTAIN) revealed that null sessions and guest access were permitted.
2. **Information Disclosure:** Anonymous connection to the `SharingIsCaring` share revealed a text file (`skyler.txt`) containing the plaintext credential note: *"Hey Skyler. I've changed your password to something really easy to remember this time. I hope you won't forget this one, I'm tired of this. Love, admin."* combined with password validation confirming `skyler.white:Password123`.
3. **Domain Enumeration:** Using the discovered credentials (`skyler.white:Password123`), full LDAP enumeration, user mapping (`GetADUsers.py`, `lookupsid.py`), and SMB share enumeration were performed against the domain controller.
4. **Kerberoasting:** Utilizing valid user credentials, Service Principal Names (SPNs) were queried via `GetUserSPNs.py`, resulting in the extraction of Kerberos service ticket hashes for multiple accounts (including `walter.white`, `jesse.pinkman`, and `saul.goodman`).
5. **Delegation Abuse Preparation:** Utilizing domain user privileges, Resource-Based Constrained Delegation (RBCD) was configured by adding a machine account (`WORKSTATION01$`) and granting it delegation rights over `MEMBER$`.

---

## Credentials Obtained

| Username | Password | NTLM Hash | Kerberos Ticket / Hash | Source Host | Acquisition Method | Subsequent Use |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `skyler.white` | `Password123` | - | - | `192.168.122.10` | Anonymous SMB share file read (`SharingIsCaring/skyler.txt`) | LDAP enumeration, SMB share enumeration, MSSQL enumeration, Kerberoasting, RBCD configuration |
| `walter.white` | - | - | `$krb5tgs$23$*walter.white...` | `192.168.122.10` | Kerberoasting (`GetUserSPNs.py`) | Cracked via hashcat (`Password123`) |
| `WORKSTATION01$` | `P@ssword123!` | - | - | `192.168.122.10` | Impacket `addcomputer.py` using `skyler.white:Password123` | Configured for Resource-Based Constrained Delegation against `MEMBER$` |

---

## Compromised Systems

### 1. CAPTAIN (Domain Controller)
* **IP Address:** `192.168.122.10`
* **OS:** Windows 10 / Server 2016 Build 14393 (Microsoft-IIS/10.0, SQL Server 2019)
* **Access Obtained:** Authenticated Domain User (`skyler.white`) via exposed credentials in anonymous share.
* **Credentials Used:** `skyler.white:Password123`
* **Artifacts Recovered:** `SharingIsCaring/skyler.txt`, `ImportantNotes/note.txt`, Kerberoasting ticket hashes.

---

## Findings

### 1. Anonymous SMB Share Access & Information Disclosure
* **Affected Systems:** `192.168.122.10` (`CAPTAIN`)
* **Description:** The SMB service permitted anonymous null session connections and guest access to the `SharingIsCaring` share.
* **Impact:** An attacker could read sensitive files containing plaintext credentials, leading directly to valid user authentication.
* **Evidence:** Anonymous smbclient connection to `192.168.122.10` successfully listed shares and retrieved `SharingIsCaring/skyler.txt`.

### 2. Weak Domain Password Policy / Credential Exposure
* **Affected Systems:** Domain `polaris.local` (`skyler.white`)
* **Description:** Domain user accounts utilized easily guessable passwords that were exposed via file shares and validated via Kerbrute / SMB.
* **Impact:** Compromise of standard user accounts enabling further Active Directory enumeration and Kerberoasting.
* **Evidence:** Discovery of `skyler.white:Password123`.

### 3. Active Directory Misconfigurations: Kerberoastable Service Accounts & Delegation Settings
* **Affected Systems:** Domain `polaris.local` (`CAPTAIN`, `MEMBER`)
* **Description:** Multiple user accounts had Service Principal Names (SPNs) registered, allowing offline brute-forcing of service tickets (Kerberoasting). Additionally, insecure delegation configurations were identified (Unconstrained Delegation on `CAPTAIN$` and `jesse.pinkman`, Constrained Delegation on `walter.white`, and Resource-Based Constrained Delegation opportunities).
* **Impact:** Potential escalation of privilege or lateral movement paths across the domain infrastructure.
* **Evidence:** Successful extraction of Kerberos ticket hashes via `GetUserSPNs.py` and identification of delegation settings via `findDelegation.py`.

---

## Vulnerabilities Demonstrated

* **Anonymous SMB Share Read Access:** Verified on `192.168.122.10` allowing unauthenticated file retrieval.
* **Kerberoasting:** Verified by requesting and extracting TGS service ticket hashes for domain service accounts using valid user credentials.
* **Active Directory Delegation Misconfigurations:** Unconstrained and Constrained delegation settings identified via LDAP enumeration.

---

## Authentication & Identity Findings

### Discovered Users
* `Administrator`
* `Guest`
* `DefaultAccount`
* `krbtgt`
* `skyler.white`
* `jesse.pinkman`
* `walter.white`
* `hank.schrader`
* `saul.goodman`

### Domain Groups & Significant Objects
* `Domain Admins`
* `Domain Users`
* `CAPTAIN$` (Computer, Unconstrained Delegation)
* `MEMBER$` (Computer)
* `DnsAdmins`
* `Masters`
* `WORKSTATION01$` (Machine account added during assessment)

---

## Lateral Movement

* **SMB / Network Authentication:** Validated domain user credentials (`skyler.white:Password123`) across SMB services on both `192.168.122.10` and `192.168.122.5`.
* **Resource-Based Constrained Delegation Configuration:** Configured `WORKSTATION01$` to delegate access to `MEMBER$`.

---

## Privilege Escalation

* **Starting Privilege:** Unauthenticated network access / Anonymous guest access.
* **Ending Privilege:** Authenticated Domain User (`skyler.white`) with capability to perform Kerberoasting, configure RBCD, and enumerate domain objects.

---

## Domain Compromise

Full Domain Administrator compromise (DCSync / NTDS.DIT extraction) was **not achieved** during the assessment. Although valid user credentials and Kerberoastable hashes were obtained, attempts to authenticate with specific high-privilege ticket requests or execute `secretsdump` with intermediate credentials encountered logon failures (`KDC_ERR_PREAUTH_FAILED` / `STATUS_LOGON_FAILURE`).

---

## Failed Attack Paths

1. **Anonymous LDAP Enumeration:** Unauthenticated LDAP binding against `192.168.122.10` failed due to Active Directory hardening policies (`000004DC: LdapErr: DSID-0C0909AF, comment: In order to perform this operation a successful bind must be completed`).
2. **AS-REP Roasting:** Checked all enumerated users (`hank.schrader`, `skyler.white`, `saul.goodman`) for pre-authentication disabled (`UF_DONT_REQUIRE_PREAUTH`); none were vulnerable.
3. **Constrained Delegation Ticket Request (S4U):** Attempted to request a service ticket using `walter.white` impersonating `Administrator` against `cifs/captain.polaris.local`, which resulted in `KDC_ERR_PREAUTH_FAILED`.
4. **RBCD Ticket Request:** Attempted to request a service ticket from `WORKSTATION01$` impersonating `Administrator` against `cifs/member.polaris.local`, resulting in `KDC_ERR_BADOPTION` because the machine account lacked necessary delegation rights.
5. **Remote Secretsdump Execution:** Execution of `secretsdump.py` using `walter.white:Password123` failed due to logon failure restrictions.

---

## Timeline of Compromise

1. **SMB Reconnaissance:** Performed anonymous SMB share enumeration against `192.168.122.10`.
2. **Credential Discovery:** Accessed the `SharingIsCaring` share anonymously and read `skyler.txt`, yielding `skyler.white:Password123`.
3. **Credential & Domain Validation:** Validated credentials via Kerbrute, SMB, and LDAP; enumerated domain users, groups, SIDs, and delegation settings.
4. **Kerberoasting:** Queried SPNs using `GetUserSPNs.py` and extracted Kerberos service ticket hashes.
5. **Delegation Abuse:** Added machine account `WORKSTATION01$` and configured Resource-Based Constrained Delegation on `MEMBER$`.

---

## Recommendations

1. **Disable Anonymous SMB Access:** Restrict null session connections and guest access on all Windows shares to prevent unauthorized file reading and information disclosure.
2. **Enforce Strong Password Policies:** Ensure domain users do not use easily guessable or weak passwords (such as `Password123`).
3. **Audit and Secure Service Principal Names (SPNs):** Review service accounts configured with SPNs and enforce strong, complex passwords resistant to offline Kerberoasting attacks.
4. **Review Active Directory Delegation Settings:** Audit and minimize the use of Unconstrained Delegation (`CAPTAIN$`, `jesse.pinkman`) and restrict unnecessary computer account creation permissions that enable Resource-Based Constrained Delegation abuse.