This penetration test assessed the security posture of the `polaris.local` domain, specifically focusing on the Domain Controller at `192.168.122.10` and the member server `192.168.122.5`.

### Findings & Accomplishments
* **Enumeration:** Successfully enumerated domain users and identified weak credentials (`saul.goodman:beTTer2caLL2me`).
* **Initial Access:** Gained access to the `ImportantNotes` and `SharingIsCaring` SMB shares using valid credentials.
* **Credential Harvesting:** Discovered further credentials (`skyler.white:Password123`) from information found on shares.
* **Vulnerability Analysis:**
    * Identified Kerberoastable accounts.
    * Identified AD CS vulnerabilities (ESC1, ESC2, ESC3, ESC8).
    * Discovered that `Authenticated Users` have `SeMachineAccountPrivilege`, allowing the addition of new computer accounts.
* **Exploitation:** Successfully added a new computer account `EVIL-PC$` to the domain.
* **AD CS Exploitation:** Successfully requested certificates using the ESC1 and ESC3 templates, although authentication with the resulting certificates was blocked by KDC policy.

### Conclusion
While significant domain-level reconnaissance and vulnerability assessment were performed, and domain user-level access was obtained, full Domain Administrator compromise was not achieved. The environment contains multiple dangerous misconfigurations, particularly in Active Directory Certificate Services (AD CS), which represent the most viable path to full domain takeover.

### Recommendations
* **Disable Unnecessary Shares:** Remove sensitive files (passwords, notes) from publicly accessible SMB shares.
* **Audit AD CS:** Remediation of AD CS vulnerabilities (ESC1-ESC8) is critical. Disable insecure templates and restrict enrollment permissions.
* **Patch/Harden:** Enforce SMB signing, disable SMBv1, and harden the configuration of the web enrollment interface.
* **Credential Hygiene:** Implement strong password policies and rotate all exposed credentials.
* **Least Privilege:** Remove excessive privileges like `SeMachineAccountPrivilege` from `Authenticated Users` and implement proper delegation restrictions.