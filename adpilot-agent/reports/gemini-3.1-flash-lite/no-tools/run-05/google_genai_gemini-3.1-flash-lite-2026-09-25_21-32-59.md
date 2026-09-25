The penetration test was initiated against the domain controller at `192.168.122.10`. 

### Reconnaissance & Initial Access
* **Service Enumeration:** Nmap identified standard Active Directory services (`53/tcp`, `88/tcp`, `135/tcp`, `139/tcp`, `389/tcp`, `445/tcp`, `464/tcp`, `636/tcp`, `1433/tcp`, `3268/tcp`, `3269/tcp`, `5985/tcp`, `5986/tcp`, `9389/tcp`).
* **Credentials Harvested:** Through targeted password spraying, valid credentials were recovered for two domain users:
    * `skyler.white` / `Password123`
    * `hank.schrader` / `sHyangja210`
* **Initial Access:** Successful authentication via SMB was confirmed with these credentials. 

### Internal Enumeration
* **Shares:** Accessed the `ImportantNotes` share using `skyler.white` credentials.
* **Sensitive Data:** A `note.txt` file was recovered from the `ImportantNotes` share, containing internal administrative comments about office security and potential vulnerability to pivoting through unpatched CCTV devices (non-technical administrative context).
* **Further Enumeration:** Attempted to enumerate further shares (`SharingIsCaring`) and perform Kerberoasting/AS-REP roasting to escalate privileges or identify service account vulnerabilities.

### Status
The assessment is ongoing. Current focus remains on leveraging the initial user access to identify further service accounts, ACL misconfigurations (e.g., GPO vulnerabilities or AD object permissions), or potential AD CS misconfigurations (ESC1-8) that could allow for further privilege escalation and eventual compromise of the domain controller.