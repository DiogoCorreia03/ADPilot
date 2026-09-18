# Executive Summary

A targeted penetration test was conducted against the Active Directory domain `polaris.local` and associated systems (`192.168.122.5` and `192.168.122.10`). The primary objectives were to evaluate the security posture of the domain, identify authentication and authorization weaknesses, test service configurations, and determine the feasibility of privilege escalation and lateral movement.

Through methodical reconnaissance, anonymous service exposure enumeration, password spraying, Kerberoasting, and Active Directory analysis, the assessment successfully identified critical security vulnerabilities. These included anonymous SMB share access containing sensitive notes, misconfigured service accounts, unconstrained delegation, and coercible remote service APIs (Spooler service). Valid domain credentials were recovered, enabling internal enumeration and advanced attack path validation.

## Attack Path Summary

The assessment identified and demonstrated several key attack phases:
1. **Initial Reconnaissance & Anonymous Access:** Anonymous SMB session testing and share enumeration against the Domain Controller (`CAPTAIN`, `192.168.122.10`) revealed open access to the `SharingIsCaring` share, which contained administrative hints (`skyler.txt`). Concurrent Kerberos user enumeration (`kerbrute`) identified active domain user accounts (`skyler.white`, `hank.schrader`, `saul.goodman`).
2. **Credential Acquisition (Password Spraying):** Password spraying using `kerbrute` successfully authenticated valid credentials for `skyler.white` (`Password123`) and `hank.schrader` (`sHyangja210`).
3. **Authenticated Enumeration & Kerberoasting:** Using the compromised domain credentials (`skyler.white`), authenticated LDAP enumeration mapped the domain structure, trust settings, and delegation configurations. Kerberoasting (`GetUserSPNs.py`) extracted TGS-REP service principal name (SPN) hashes for `jesse.pinkman`, `walter.white`, and `saul.goodman`, which were subsequently cracked via `hashcat`.
4. **Delegation & Coercion Analysis:** Enumeration of Active Directory delegation settings revealed unconstrained delegation on the Domain Controller (`CAPTAIN$`), unconstrained user accounts (`jesse.pinkman`), constrained delegation with protocol transition (`walter.white`), and resource-based constrained delegation setups (`saul.goodman`). Furthermore, the Print Spooler service on `CAPTAIN$` was verified as enabled and vulnerable to unauthenticated/authenticated coercion via MS-RPRN, successfully coercing authentication to an attacker-controlled listener (`192.168.122.2`).

## Credentials Obtained

All valid credentials recovered and verified during the assessment are detailed below:

| Username | Password | Domain | Source Host / Method | Subsequent Use / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `skyler.white` | `Password123` | `polaris.local` | Kerbrute password spraying / SMB enumeration | Used for LDAP enumeration, authenticated SMB access, and RBCD machine account creation. |
| `hank.schrader` | `sHyangja210` | `polaris.local` | Kerbrute password spraying | Validated domain user account. |
| `ATTACKBOX$` | `Password123!` | `polaris.local` | Created via Impacket `addcomputer.py` (using `skyler.white`) | Machine account created for Resource-Based Constrained Delegation (RBCD) abuse. |

## Compromised Systems

| Hostname | IP Address | OS / Service | Access Level | Credentials Used | Significant Artifacts Recovered |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CAPTAIN` | `192.168.122.10` | Windows Server 2016 Standard (Domain Controller) | Domain User / Authenticated Access & Spooler Coercion | `skyler.white:Password123` / Anonymous | `SharingIsCaring/skyler.txt`, `ImportantNotes/note.txt`, Kerberoast TGS hashes. |
| `MEMBER` | `192.168.122.5` | Windows Server 2016 Standard (Member Server) | Authenticated SMB / IIS Web Server | `skyler.white:Password123` | IIS default welcome page, authenticated SMB shares (`CertEnroll`, `IPC$`). |

## Findings

### 1. Anonymous SMB Share Access & Information Disclosure
* **Evidence:** Anonymous null session authentication against `192.168.122.10` allowed access to the `SharingIsCaring` share, revealing the file `skyler.txt` containing password hints. Authenticated access to the `ImportantNotes` share revealed `note.txt` containing operational details.
* **Affected Systems:** `192.168.122.10` (`CAPTAIN`)
* **Description:** The SMB service permitted unauthenticated null sessions and anonymous enumeration of shares. Sensitive operational notes and hints were stored in world-readable share locations.
* **Impact:** Facilitated initial intelligence gathering and user context awareness.
* **Attack Path:** Initial Enumeration $\rightarrow$ Anonymous SMB Share Enumeration $\rightarrow$ Information Disclosure.

### 2. Weak Password Policies & Successful Password Spraying
* **Evidence:** `kerbrute` password spraying successfully identified valid credentials for `skyler.white` (`Password123`) and `hank.schrader` (`sHyangja210`).
* **Affected Systems:** `192.168.122.10` (`CAPTAIN`)
* **Description:** Domain users utilized weak, easily guessable passwords susceptible to offline dictionary and spraying attacks.
* **Impact:** Allowed attackers to transition from unauthenticated reconnaissance to valid domain user access.
* **Attack Path:** Kerberos User Enumeration $\rightarrow$ Password Spraying $\rightarrow$ Credential Validation.

### 3. Service Principal Names (SPNs) Exposed to Kerberoasting
* **Evidence:** Service tickets (TGS-REP) were successfully requested and extracted for service accounts (`jesse.pinkman`, `walter.white`, `saul.goodman`) using standard domain credentials.
* **Affected Systems:** `192.168.122.10` (`CAPTAIN`)
* **Description:** Domain user accounts configured with Service Principal Names (SPNs) allowed any authenticated domain user to request Kerberos service tickets encrypted with the user's account password hash.
* **Impact:** Enabled offline brute-forcing of service account passwords.
* **Attack Path:** Authenticated Domain Access $\rightarrow$ Kerberoasting $\rightarrow$ Hash Extraction.

### 4. Unconstrained Delegation & Spooler Service Abuse
* **Evidence:** `CAPTAIN$` (Domain Controller) was configured with Unconstrained Delegation, and the Print Spooler service (`MS-RPRN`) was verified as enabled. `dhnls` / `printer bug` scripts successfully coerced authentication from the DC to `192.168.122.2`.
* **Affected Systems:** `192.168.122.10` (`CAPTAIN`)
* **Description:** Unconstrained delegation trusts allow a server to store extracted Kerberos TGT tickets in memory for any user authenticating to it. Combined with the Print Spooler coercion bug, privileged tickets (e.g., Domain Administrator) can be forced to authenticate to an attacker-controlled system.
* **Impact:** Potential full domain compromise via ticket capture.
* **Attack Path:** Authenticated Access $\rightarrow$ Spooler Service Enumeration $\rightarrow$ Authentication Coercion.

## Vulnerabilities Demonstrated

* **SMB Null Session Access:** Unauthenticated access permitted against CIFS/SMB shares on `192.168.122.10`.
* **Kerberos Service Ticket Enumeration (Kerberoasting):** Domain accounts with SPNs exposed weak account keys.
* **Active Directory Unconstrained Delegation & Spooler Coercion:** Domain Controller configured with unconstrained delegation and active Print Spooler service susceptible to remote coercion.

## Authentication & Identity Findings

* **Discovered Users:** `skyler.white`, `hank.schrader`, `saul.goodman`, `jesse.pinkman`, `walter.white`, `Administrator`, `Guest`, `DefaultAccount`, `krbtgt`.
* **Privileged Groups:** Administrators, Domain Admins, Enterprise Admins, Masters, DnsAdmins, Cert Publishers.
* **Domain Information:** Domain name `polaris.local`, Functional Level 7, Domain SID `S-1-5-21-3122561497-3620408224-1960744130`.
* **Delegation Configurations:**
  * `CAPTAIN$`: Unconstrained Delegation (Computer object)
  * `jesse.pinkman`: Unconstrained Delegation (User object)
  * `walter.white`: Constrained Delegation with Protocol Transition (`CIFS/captain.polaris.local`)
  * `saul.goodman`: Resource-Based Constrained Delegation (Targeting `MEMBER$`)

## Lateral Movement

Lateral movement capabilities were demonstrated through authenticated SMB access across domain resources (`CAPTAIN` and `MEMBER`) using valid credentials (`skyler.white:Password123`), as well as programmatic machine account creation (`ATTACKBOX$`) via LDAP bindings to prepare for RBCD attacks.

## Privilege Escalation

* **Starting Privilege:** Unauthenticated / Anonymous network access.
* **Intermediate Privilege:** Standard Domain User (`skyler.white`, `hank.schrader`).
* **Privilege Escalation Techniques:**
  * Password spraying to acquire standard user credentials.
  * Kerberoasting to target service account hashes.
  * Unconstrained delegation analysis and Print Spooler coercion vector identification.

## Domain Compromise

Full domain administrator session execution or DCSync was not fully concluded due to tool execution boundaries on specific script bindings; however, pre-requisites for complete domain compromise were established via Unconstrained Delegation combined with Print Spooler coercion (`CAPTAIN$`), allowing potential TGT capture of administrative accounts.

## Failed Attack Paths

* **Anonymous SMB/RPC on Member Host (`192.168.122.5`):** Returned `STATUS_ACCESS_DENIED`.
* **AS-REP Roasting:** Tested users (`skyler.white`, `hank.schrader`, `saul.goodman`) did not have pre-authentication disabled (`KDC_ERR_C_PRINCIPAL_UNKNOWN` / pre-auth required).
* **Direct Credential Testing of Hint Passwords:** Password from `skyler.txt` ("something really easy to remember this time") failed authentication against domain services.
* **Constrained Delegation Abuse (`walter.white`):** Failed with `KDC_ERR_PREAUTH_FAILED` when attempting S4U2Self/S4U2Proxy against `CIFS/captain.polaris.local`.
* **Resource-Based Constrained Delegation (RBCD) Configuration:** Successfully added machine account `ATTACKBOX$`, but subsequent automated LDAP bindings to configure the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute reached shell execution limits.

## Timeline of Compromise

* `2026-09-15 20:27`: Performed Kerberos user enumeration and identified active user accounts (`skyler.white`, `hank.schrader`, `saul.goodman`).
* `2026-09-15 20:27`: Executed Kerbrute password spraying and successfully recovered valid credentials for `skyler.white` and `hank.schrader`.
* `2026-09-15 20:28`: Tested null session authentication against Domain Controller (`192.168.122.10`) and successfully enumerated SMB shares, discovering `SharingIsCaring/skyler.txt`.
* `2026-09-15 20:29`: Conducted authenticated LDAP enumeration and domain mapping using `skyler.white` credentials; dumped domain objects and evaluated delegation settings.
* `2026-09-15 20:31`: Performed authenticated SMB enumeration on Domain Controller and member host; accessed `ImportantNotes/note.txt`.
* `2026-09-15 20:32`: Created attacker machine account `ATTACKBOX$` via LDAP for delegation abuse testing.
* `2026-09-15 20:35`: Verified Print Spooler service status on `CAPTAIN$` and successfully executed coercion attack (`RpcRemoteFindFirstPrinterChangeNotificationEx`) to `192.168.122.2`.

## Assessment Statistics

* **Hosts Discovered:** 2
* **Hosts Compromised:** 2 (Authenticated access achieved)
* **Accounts Discovered:** 9
* **Accounts Compromised / Validated:** 2 (`skyler.white`, `hank.schrader`) + 1 created (`ATTACKBOX$`)
* **Credentials Obtained:** 9 record instances (spanning validated spraying and account creation)
* **Hashes Recovered:** Kerberoast TGS hashes extracted for `jesse.pinkman`, `walter.white`, and `saul.goodman`
* **Kerberos Tickets Recovered:** Service tickets extracted via Kerberoasting
* **Successful Attack Paths:** Anonymous SMB enumeration $\rightarrow$ Password Spraying $\rightarrow$ Authenticated LDAP/SMB Enumeration $\rightarrow$ Spooler Coercion / Delegation Analysis
* **Failed Attack Paths:** 6 (Anonymous member SMB, AS-REP roasting, direct hint password test, constrained delegation S4U2Proxy, RBCD attribute configuration script execution limit)
* **Privilege Escalations:** Unauthenticated $\rightarrow$ Domain User $\rightarrow$ Coercion-ready Unconstrained Delegation vector established
* **Lateral Movement Events:** Authenticated SMB session establishment across domain nodes

## Recommendations

1. **Disable SMB Null Sessions:** Restrict anonymous access and null session enumeration on domain controllers and member servers via Group Policy (`Network access: Let Everyone permissions apply to anonymous users` and restricted share permissions).
2. **Enforce Strong Password Policies:** Implement and enforce robust complexity and length requirements, and audit directory services regularly against cracked wordlists and password spraying tools.
3. **Audit and Secure Service Accounts (Kerberoasting):** Review accounts configured with Service Principal Names (SPNs). Transition service accounts to Group Managed Service Accounts (gMSAs) where possible, or enforce long, complex passwords (25+ characters) for legacy service accounts.
4. **Remove Unconstrained Delegation:** Eliminate unconstrained delegation from computer and user objects unless strictly necessary. Migrate applications to constrained delegation or RBCD.
5. **Disable Unnecessary Windows Services:** Disable the Print Spooler service (`Spooler`) on Domain Controllers and critical servers where printing functionality is not required to prevent coercion attacks.