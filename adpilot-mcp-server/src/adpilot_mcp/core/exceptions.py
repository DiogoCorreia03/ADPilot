class ADPilotError(Exception):
    """Base exception for ADPilot MCP Server."""
    pass


class ExecutionTimeoutError(ADPilotError):
    """Raised when a command times out."""
    def __init__(self, cmd: str, timeout: int):
        self.cmd = cmd
        self.timeout = timeout
        super().__init__(f"Command timed out after {timeout}s: {cmd}")


class ExecutionError(ADPilotError):
    """Raised when command fails to execute."""
    pass


class StateStoreError(ADPilotError):
    """Raised when loading or saving state fails."""
    pass
