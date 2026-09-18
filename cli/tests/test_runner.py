import json
from mcp_client.runner import extract_text_from_tool_result, parse_execution_result


def test_parse_execution_result_json_success():
    payload = {
        "command": "python dnstool.py -u admin -p pass --action query",
        "stdout": "Found DNS Record: dc01.corp.local -> 192.168.122.10",
        "stderr": "",
        "returncode": 0,
        "success": True,
    }
    raw = json.dumps(payload)
    result = parse_execution_result(raw, elapsed=1.25)

    assert result.is_json is True
    assert result.success is True
    assert result.returncode == 0
    assert result.command == payload["command"]
    assert "Found DNS Record" in result.stdout
    assert result.stderr == ""
    assert result.elapsed_seconds == 1.25


def test_parse_execution_result_json_failure():
    payload = {
        "command": "python dnstool.py --action add",
        "stdout": "",
        "stderr": "[-] Kerberos authentication failed",
        "returncode": 1,
        "success": False,
    }
    raw = json.dumps(payload)
    result = parse_execution_result(raw, elapsed=0.5)

    assert result.is_json is True
    assert result.success is False
    assert result.returncode == 1
    assert "Kerberos authentication failed" in result.stderr


def test_parse_execution_result_plaintext():
    text = "Nmap scan report for 192.168.122.10\nHost is up (0.001s latency)."
    result = parse_execution_result(text, elapsed=0.8)

    assert result.is_json is False
    assert result.success is True
    assert "Nmap scan report" in result.stdout


def test_extract_text_from_various_structures():
    # String
    assert extract_text_from_tool_result("hello") == "hello"

    # Dict with text
    assert extract_text_from_tool_result({"text": "world"}) == "world"

    # List of dicts (LangChain MCP format)
    assert extract_text_from_tool_result([{"type": "text", "text": "mcp response"}]) == "mcp response"
