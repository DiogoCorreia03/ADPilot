# Executive Summary

An authorized penetration test was conducted against the target environment within the `polaris.local` domain, encompassing Domain Controller `192.168.122.10` (`CAPTAIN`) and member server `192.168.122.5` (`MEMBER`). The primary objective of the assessment was to evaluate the security posture of the Active Directory environment, identify potential attack paths, and determine the feasibility of domain compromise.

Throughout the assessment, enumeration procedures identified Active Directory structure, open services (LDAP, Kerberos, SMB, MSSQL), and valid user accounts. However, **no hosts or privileged accounts were successfully compromised**, and **domain compromise was not achieved**. Guest/null authentication supported limited session establishment on the Domain Controller, but direct share enumeration and access were blocked (`STATUS_ACCESS_DENIED`). Password spraying, Kerberoasting, AS-REP roasting, unauthenticated computer account creation, and credential validation attempts against discovered accounts yielded no successful authentications.

# Attack Path Summary

No successful attack paths leading to system compromise or privilege escalation were demonstrated during this assessment. All attempted attack chains were blocked or failed due to authentication restrictions and hardened service configurations.

# Credentials Obtained

No functional user passwords, NTLM hashes, or Kerberos tickets were successfully compromised or obtained during the assessment. 

*(Note: While user accounts were enumerated via Kerberos, no valid credentials were recovered or validated via authentication testing).*

# Compromised Systems

No systems were successfully compromised during the assessment. 

- **CAPTAIN (192.168.122.10)**: Windows Server 2016 Standard Evaluation (Domain Controller). Access attempted via SMB null sessions, LDAP, MSSQL, and credential validation; guest/null authentication allowed session setup, but resource access resulted in `STATUS_ACCESS_DENIED`.
- **MEMBER (192.168.122.5)**: Windows Server 2016 Standard Evaluation (Member Server). Access attempted via SMB; session setup failed with `NT_STATUS_ACCESS_DENIED` / `NT_STATUS_LOGON_FAILURE`.

# Findings

### 1. SMB v1 Protocol Enabled
- **Evidence**: Netexec identification of SMBv1 enabled on `192.168.122.5` (`MEMBER`) and `192.168.122.10` (`CAPTAIN`).
- **Affected Systems**: `192.168.122.5`, `192.168.122.10`
- **Description**: The legacy Server Message Block version 1 (SMBv1) protocol is enabled on the target Windows Server 2016 hosts.
- **Impact**: Exposes the systems to legacy protocol vulnerabilities (such as EternalBlue/MS17-010) and protocol downgrade attacks.
- **Attack Path**: None successfully exploited.

### 2. Unsigned SMB Communication Enabled
- **Evidence**: Netexec enumeration confirmed SMB Signing is set to `False` on both `192.168.122.5` and `192.168.122.10`.
- **Affected Systems**: `192.168.122.5`, `192.168.122.10`
- **Description**: SMB packet signing is not enforced on the target hosts.
- **Impact**: Increases risk of adversary-in-the-middle (AiTM) attacks and SMB relay attacks against the domain.
- **Attack Path**: None successfully exploited.

### 3. Null Session / Guest Authentication Allowed on Domain Controller
- **Evidence**: Netexec and `smbclient` connections to `192.168.122.10` (`CAPTAIN`) successfully authenticated via guest/null sessions (though share access was denied).
- **Affected Systems**: `192.168.122.10`
- **Description**: The Domain Controller permits unauthenticated guest/null session establishment.
- **Impact**: Allows anonymous or unauthenticated users to establish baseline network sessions with the domain controller, aiding initial reconnaissance.
- **Attack Path**: None successfully exploited beyond initial session check.

# Vulnerabilities Demonstrated

No software exploitation vulnerabilities (CVEs) or remote code execution flaws were demonstrated during the assessment.

# Authentication & Identity Findings

- **Discovered Domain Users**: 
  - `saul.goodman@polaris.local`
  - `skyler.white@polaris.local`
  - `hank.schrader@polaris.local`
- **Service Accounts**: None enumerated or compromised.
- **Privileged Accounts**: None compromised.
- **Groups / Trusts / Guest Access**: Null authentication is permitted on the Domain Controller (`CAPTAIN`), though direct share access and IPC$/ADMIN$ enumeration are blocked.
- **Password Reuse / Credential Reuse**: Not applicable (no credentials compromised).

# Lateral Movement

No lateral movement was demonstrated during the assessment as no initial footholds or credentials were established.

# Privilege Escalation

No privilege escalation was performed or demonstrated during the assessment.

# Domain Compromise

Domain compromise was **not achieved**. 
- DCSync: Not performed (insufficient privileges).
- Secretsdump: Not performed (no credentials).
- KRBTGT compromise: Not achieved.
- Full domain dominance: Not achieved.

# Failed Attack Paths

1. **Anonymous SMB Share Access (`MEMBER` and `CAPTAIN`)**: Attempted unauthenticated/guest share enumeration and connection using `netexec` and `smbclient`. Failed with `NT_STATUS_ACCESS_DENIED` / `NT_STATUS_LOGON_FAILURE`.
2. **AS-REP Roasting**: Checked discovered user accounts (`saul.goodman`, `skyler.white`, `hank.schrader`) for pre-authentication disabled status (`UF_DONT_REQUIRE_PREAUTH`). Failed as pre-authentication was enforced on all accounts.
3. **Kerberoasting**: Attempted SPN enumeration and ticket extraction against `192.168.122.10`. Failed due to lack of valid authenticated user credentials.
4. **Password Spraying / Credential Validation**: Tested discovered usernames against Kerberos, SMB (port 445), and LDAP (port 389) using password wordlists and potential default credentials (`tryme`). Failed with `invalidCredentials (52e)`.
5. **Unauthenticated Machine Account Creation**: Attempted to add a computer account (`ATTACKBOX$`) via MS-SAMR/LDAP on `192.168.122.10` using Impacket's `addcomputer.py`. Failed with `STATUS_ACCESS_DENIED`.
6. **MSSQL Authentication**: Attempted unauthenticated and Windows/guest authentication against MSSQL (port 1433) on `192.168.122.10`. Failed due to lack of valid credentials.

# Timeline of Compromise

Due to the defensive posture of the target environment, no compromise timeline applies. The assessment progression followed a structured reconnaissance and validation sequence:
1. Performed DNS SRV record queries and domain enumeration against `192.168.122.10`.
2. Enudumerated SMB signing, protocol versions, and null session status on `192.168.122.5` and `192.168.122.10`.
3. Performed LDAP reconnaissance and anonymous bind assessments against `192.168.122.10`.
4. Executed Kerberos user enumeration (`kerbrute`), discovering three valid user accounts.
5. Tested AS-REP roasting and Kerberoasting against discovered users (both failed).
6. Executed password spraying and credential validation attempts against SMB, LDAP, and Kerberos (all failed).
7. Assessed AD CS templates, machine account creation restrictions, and MSSQL service access (all restricted/failed).

# Assessment Statistics

- **Hosts Discovered**: 2
- **Hosts Compromised**: 0
- **Accounts Discovered**: 3
- **Accounts Compromised**: 0
- **Credentials Obtained**: 0
- **Hashes Recovered**: 0
- **Kerberos Tickets Recovered**: 0
- **Successful Attack Paths**: 0
- **Failed Attack Paths**: 6
- **Privilege Escalations**: 0
- **Lateral Movement Events**: 0

# Recommendations

1. **Disable SMBv1**: Disable the legacy SMBv1 protocol across all domain controllers and member servers to mitigate protocol downgrade and legacy exploit risks.
   - *Addressing Finding*: SMB v1 Protocol Enabled
2. **Enforce SMB Signing**: Enable and enforce SMB packet signing on `192.168.122.5` (`MEMBER`) and `192.168.122.10` (`CAPTAIN`) to prevent potential adversary-in-the-middle and relay attacks.
   - *Addressing Finding*: Unsigned SMB Communication Enabled
3. **Restrict Anonymous/Guest Sessions**: Disable null session authentication and restrict anonymous LDAP/SMB binding capabilities on Domain Controllers where business requirements permit.
   - *Addressing Finding*: Null Session / Guest Authentication Allowed on Domain Controller