import json
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolExecutionResult:
    command: str | None = None
    stdout: str | None = None
    stderr: str | None = None
    returncode: int | None = None
    success: bool = True
    raw_output: str = ""
    is_json: bool = False
    elapsed_seconds: float = 0.0


def extract_text_from_tool_result(result: Any) -> str:
    """Extract raw text from various LangChain MCP tool result formats."""
    if isinstance(result, str):
        return result

    if isinstance(result, dict):
        if "text" in result:
            return str(result["text"])
        return json.dumps(result, indent=2)

    # Check content attribute (ToolMessage or MCP adapter response)
    content = getattr(result, "content", None)
    if content:
        if isinstance(content, str):
            return content
        if isinstance(content, list) and len(content) > 0:
            first = content[0]
            if isinstance(first, dict) and "text" in first:
                return str(first["text"])
            if hasattr(first, "text"):
                return str(first.text)
            return str(first)

    # Check list response
    if isinstance(result, list) and len(result) > 0:
        first = result[0]
        if isinstance(first, dict) and "text" in first:
            return str(first["text"])
        if hasattr(first, "text"):
            return str(first.text)
        return str(first)

    return str(result)


def parse_execution_result(raw_result: Any, elapsed: float = 0.0) -> ToolExecutionResult:
    """Parse MCP tool result into structured fields (command, stdout, stderr, returncode)."""
    raw_text = extract_text_from_tool_result(raw_result)
    res = ToolExecutionResult(raw_output=raw_text, elapsed_seconds=elapsed)

    try:
        data = json.loads(raw_text)
        if isinstance(data, dict):
            res.is_json = True
            res.command = data.get("command")
            res.stdout = data.get("stdout")
            res.stderr = data.get("stderr")

            # Check status code / return code
            rc = data.get("returncode")
            if rc is None:
                rc = data.get("status_code", data.get("status"))
            if isinstance(rc, int):
                res.returncode = rc

            # Determine success flag
            if "success" in data:
                res.success = bool(data["success"])
            elif res.returncode is not None:
                res.success = res.returncode == 0
            else:
                res.success = True
            return res
    except (json.JSONDecodeError, TypeError):
        pass

    # Non-JSON or plaintext output
    res.stdout = raw_text
    res.success = True
    return res


async def execute_tool(tool: Any, arguments: dict[str, Any]) -> ToolExecutionResult:
    """Execute a tool asynchronously and return structured execution results."""
    start_time = time.perf_counter()
    try:
        raw_result = await tool.ainvoke(arguments)
        elapsed = time.perf_counter() - start_time
        return parse_execution_result(raw_result, elapsed=elapsed)
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        return ToolExecutionResult(
            command=None,
            stdout="",
            stderr=f"Execution error: {type(e).__name__}: {e}",
            returncode=1,
            success=False,
            raw_output=str(e),
            is_json=False,
            elapsed_seconds=elapsed,
        )
