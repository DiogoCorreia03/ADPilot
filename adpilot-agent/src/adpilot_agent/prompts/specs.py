from dataclasses import dataclass
from ..util.state import Phase


@dataclass(frozen=True)
class PhaseSpec:
    phase: Phase
    name: str
    objective: str
    scope: str
    forbidden_categories: str
    allowed_categories: str
    generation_rules: str
    planning_principle_examples: str = ""


PHASE_SPECS: dict[Phase, PhaseSpec] = {
    Phase.EXTERNAL_RECON: PhaseSpec(
        phase=Phase.EXTERNAL_RECON,
        name="External Reconnaissance and Enumeration",
        objective="Analyze reconnaissance findings, identify externally observable attack surface, prioritize enumeration activities and collect and preserve information useful for later phases, like valid usernames.",
        scope="""The goal of this phase is to identify and characterize:
* reachable hosts
* exposed services
* authentication surfaces
* externally accessible shares
* externally accessible directory services
* externally observable Active Directory information
* potential identity sources, usernames, and anonymous access

The goal is to collect evidence and generate leads for the Initial Access phase.
Do NOT attempt to achieve access during this phase.""",
        forbidden_categories="""* credential validation
* password spraying or guessing
* exploitation
* authenticated enumeration or access
* privilege escalation
* lateral movement
* persistence
* post-exploitation
* internal reconnaissance
* ticket abuse
* hash cracking
* domain compromise

Those activities belong to later phases and must not appear in this plan.""",
        allowed_categories="""* network reconnaissance
* service enumeration
* SMB enumeration
* LDAP enumeration
* Kerberos enumeration
* username discovery
* anonymous AD reconnaissance
* etc.

Focus on answering questions such as:
* What hosts are reachable?
* What services are exposed?
* Is anonymous access possible?
* What AD information is externally visible?
* Are usernames discoverable?
* Are shares accessible?
* What authentication mechanisms exist?

Do not plan how to exploit findings.
Focus on Windows Active Directory.

Examples of valid task categories:

### Network Reconnaissance

Examples:
* Enumerate SMB hosts
* Enumerate LDAP exposure
* Enumerate Kerberos services
* Validate service versions

### Anonymous Active Directory Reconnaissance

Examples:
* Anonymous SMB enumeration
* Anonymous share enumeration
* Anonymous LDAP enumeration
* Null-session testing
* Domain information gathering

### User Enumeration

Examples:
* Kerberos username discovery
* Username validation against exposed identity services
* Enumeration of publicly discoverable identities

### Service Characterization

Examples:
* Collect SMB metadata
* Collect LDAP metadata
* Collect Kerberos metadata

You operate ONLY inside External Reconnaissance.""",
        planning_principle_examples="""Example:

If SMB is exposed:
create SMB enumeration tasks.

If LDAP is not exposed:
do not create LDAP tasks.""",
        generation_rules="""Generate follow-up tasks only for newly discovered:
* hosts
* services
* domains
* usernames
* shares
* authentication mechanisms

Credentials should be preserved but must not be used.

## ALLOWED FOLLOW-UP TASK TYPES

### New host discovered
Evidence: Host: dc02.corp.local
Allowed task: Enumerate exposed services on dc02.corp.local

### New SMB share discovered
Evidence: Share: PUBLIC
Allowed task: Enumerate contents and permissions of PUBLIC share anonymously

### Anonymous access discovered
Evidence: Anonymous LDAP bind permitted
Allowed task: Enumerate directory information through anonymous LDAP access

## FORBIDDEN FOLLOW-UP TASKS
Evidence: Credential: svc_sql : Password123!
Forbidden task: Attempt authentication using svc_sql
Reason: Initial Access phase.

Evidence: TGS hash discovered
Forbidden task: Crack TGS hash
Reason: Initial Access phase.

Evidence: Potential vulnerability identified
Forbidden task: Exploit vulnerability
Reason: Initial Access phase.""",
    ),
    Phase.INITIAL_ACCESS: PhaseSpec(
        phase=Phase.INITIAL_ACCESS,
        name="Gaining Initial Access",
        objective="Obtain the first authenticated foothold within the authorized environment.",
        scope="Password discovery, authentication opportunities, credential usage, controlled validation of exposed attack paths.",
        forbidden_categories="""* internal network enumeration
* privilege escalation
* lateral movement
* persistence""",
        allowed_categories="""* credential validation
* authentication testing
* password spraying
* password reuse testing
* AS-REP roasting
* Kerberoasting
* LLMNR poisoning
* certificate abuse validation
* exposed service authentication

Focus on Windows Active Directory.""",
        planning_principle_examples="""Example:
If valid usernames are discovered:
create password spraying tasks against those usernames. Or AS-REP roasting tasks. Or Kerberoasting tasks.""",
        generation_rules="""Generate follow-up tasks only for discovered:
* credentials
* hashes
* tickets
* authenticated sessions
* accessible hosts

Do not generate internal reconnaissance tasks.
Preserve foothold evidence only.""",
    ),
    Phase.INTERNAL_RECON: PhaseSpec(
        phase=Phase.INTERNAL_RECON,
        name="Internal Reconnaissance and Enumeration",
        objective="Map the internal environment available from the established foothold. Identify internally observable attack surface, prioritize enumeration activities and collect and preserve information useful for later phases.",
        scope="Discovery of systems, trust relationships, permissions, shares, users and administrative boundaries.",
        forbidden_categories="""* privilege escalation
* lateral movement
* persistence""",
        allowed_categories="""* host enumeration
* user enumeration
* AD enumeration
* share enumeration
* group enumeration
* permission enumeration
* trust enumeration
* session enumeration
* local administrator discovery
* GPO enumeration
* certificate services enumeration
* LDAP enumeration
* collect details about users, group memberships, ACLs, etc.""",
        planning_principle_examples="",
        generation_rules="""Generate follow-up tasks only for newly discovered:
* hosts
* users
* groups
* trusts
* permissions
* sessions
* administrative relationships

Do not generate privilege escalation tasks.
Do not generate lateral movement tasks.""",
    ),
    Phase.LATERAL_PRIVESC: PhaseSpec(
        phase=Phase.LATERAL_PRIVESC,
        name="Lateral Movement and Privilege Escalation",
        objective="Validate paths that increase privileges and expand access within the authorized environment. Potentially achieve domain compromise and persistent access.",
        scope="Privilege escalation, delegated access abuse, lateral movement and domain-level access validation.",
        forbidden_categories="None",
        allowed_categories="""* privilege escalation validation
* delegated access abuse
* local administrator abuse
* lateral movement
* ticket abuse
* trust abuse
* ACL abuse
* certificate abuse
* administrative access validation""",
        planning_principle_examples="",
        generation_rules="""Generate follow-up tasks only for newly discovered:
* elevated privileges
* administrative access
* delegated permissions
* new trust paths
* new lateral movement opportunities

Prefer the shortest evidence-supported path toward high-value administrative access.

Avoid speculative escalation chains.""",
    ),
}


def get_phase_spec(phase: Phase) -> PhaseSpec:
    spec = PHASE_SPECS.get(phase)
    if spec is None:
        raise ValueError(f"Unknown or unsupported phase: {phase}")
    return spec
