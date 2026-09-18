import json
from typing import Any
from pydantic import BaseModel, Field


class CommandResult(BaseModel):
    """Structured result of a shell or tool execution."""
    command: str
    stdout: str = ""
    stderr: str = ""
    returncode: int
    success: bool
    extra: dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = {
            "command": self.command,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "returncode": self.returncode,
            "success": self.success,
        }
        data.update(self.extra)
        return data

    def to_mcp_result(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def format_tool_result(data: dict | str | BaseModel) -> str:
    """Format data into JSON string or raw string for MCP tool response."""
    if isinstance(data, str):
        return data
    if isinstance(data, BaseModel):
        if hasattr(data, "to_mcp_result"):
            return data.to_mcp_result()
        return data.model_dump_json(indent=2)
    return json.dumps(data, indent=2)
