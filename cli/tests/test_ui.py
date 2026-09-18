from unittest.mock import MagicMock
from mcp_client.runner import ToolExecutionResult
from mcp_client.ui import (
    display_args_preview,
    display_execution_result,
    display_tool_details,
    display_tools_table,
    print_banner,
    prompt_help,
)


def test_ui_renders_without_exceptions():
    # Test banner
    print_banner(server_url="http://127.0.0.1:8080/mcp", network="10.0.0.0/24", dc_ip="10.0.0.1")
    print_banner(server_url="http://127.0.0.1:8080/mcp", network="10.0.0.0/24", dc_ip="10.0.0.1", pentest_phase="shell_only")

    # Mock tool
    mock_tool = MagicMock()
    mock_tool.name = "run_dnstool"
    mock_tool.description = "Run dnstool.py"
    mock_tool.args = {
        "hostname": {"type": "string", "description": "DC hostname"},
        "timeout": {"type": "integer", "default": 120},
    }

    # Test tools table
    display_tools_table([mock_tool])
    display_tools_table([mock_tool], filter_query="dns")
    display_tools_table([mock_tool], filter_query="nonexistent")

    # Test tool details
    display_tool_details(mock_tool)

    # Test args preview
    display_args_preview("run_dnstool", {"hostname": "dc01.corp.local", "timeout": 60})

    # Test execution result display (success & failure)
    succ_res = ToolExecutionResult(
        command="dnstool.py ...",
        stdout="Success",
        stderr="",
        returncode=0,
        success=True,
        elapsed_seconds=0.5,
    )
    display_execution_result(succ_res)

    fail_res = ToolExecutionResult(
        command="dnstool.py ...",
        stdout="",
        stderr="Error message",
        returncode=1,
        success=False,
        elapsed_seconds=1.0,
    )
    display_execution_result(fail_res)

    # Test help
    prompt_help()
