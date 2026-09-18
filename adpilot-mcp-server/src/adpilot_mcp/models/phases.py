from enum import StrEnum


class PentestPhase(StrEnum):
    """
    Active Directory Pentesting Phases.
    String representations must match the ones expected by the MCP Client.
    """

    EXTERNAL_RECONNAISSANCE = "external_reconnaissance"
    INITIAL_ACCESS = "initial_access"
    INTERNAL_RECONNAISSANCE = "internal_reconnaissance"
    LATERAL_MOVEMENT_AND_PRIV_ESC = "lateral_movement_and_privilege_escalation"
    CHECK_RESULTS = "check_results"
    SHELL_ONLY = "shell_only"
