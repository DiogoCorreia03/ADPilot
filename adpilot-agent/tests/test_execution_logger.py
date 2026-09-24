import json
import logging
from pathlib import Path

import pytest

from adpilot_agent.util.execution_logger import JSONLFormatter, setup_execution_logger


def test_jsonl_formatter_basic():
    formatter = JSONLFormatter()
    record = logging.LogRecord(
        name="execution",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Task completed successfully.",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    assert "\n" not in formatted
    data = json.loads(formatted)
    assert data["name"] == "execution"
    assert data["level"] == "INFO"
    assert data["message"] == "Task completed successfully."
    assert "timestamp" in data


def test_jsonl_formatter_args_formatting():
    formatter = JSONLFormatter()
    record = logging.LogRecord(
        name="execution",
        level=logging.INFO,
        pathname=__file__,
        lineno=20,
        msg="Tool %s called with %s arguments",
        args=("nmap", 3),
        exc_info=None,
    )
    formatted = formatter.format(record)
    data = json.loads(formatted)
    assert data["message"] == "Tool nmap called with 3 arguments"


def test_jsonl_formatter_multiline_prompt_response():
    formatter = JSONLFormatter()
    multiline_msg = "=== PROMPT ===\nLine 1\nLine 2\n=== RESPONSE ===\nDone."
    record = logging.LogRecord(
        name="execution",
        level=logging.INFO,
        pathname=__file__,
        lineno=30,
        msg=multiline_msg,
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    # Crucial property of JSONL: each record must be strictly on a single line
    assert "\n" not in formatted
    data = json.loads(formatted)
    assert data["message"] == multiline_msg


def test_jsonl_formatter_structured_dict_message():
    formatter = JSONLFormatter()
    msg_dict = {"tool": "crackmapexec", "target": "192.168.1.10", "success": True}
    record = logging.LogRecord(
        name="execution",
        level=logging.INFO,
        pathname=__file__,
        lineno=40,
        msg=msg_dict,
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    data = json.loads(formatted)
    assert data["message"] == msg_dict


def test_jsonl_formatter_extra_fields():
    formatter = JSONLFormatter()
    record = logging.LogRecord(
        name="execution",
        level=logging.INFO,
        pathname=__file__,
        lineno=50,
        msg="Testing extra attributes",
        args=(),
        exc_info=None,
    )
    record.phase = "internal_recon"
    record.tool_name = "smbclient"

    formatted = formatter.format(record)
    data = json.loads(formatted)
    assert data["phase"] == "internal_recon"
    assert data["tool_name"] == "smbclient"


def test_jsonl_formatter_with_exception():
    formatter = JSONLFormatter()
    try:
        raise ValueError("Simulated tool crash")
    except ValueError:
        import sys
        exc_info = sys.exc_info()

    record = logging.LogRecord(
        name="execution",
        level=logging.ERROR,
        pathname=__file__,
        lineno=60,
        msg="Tool failed",
        args=(),
        exc_info=exc_info,
    )
    formatted = formatter.format(record)
    assert "\n" not in formatted
    data = json.loads(formatted)
    assert data["level"] == "ERROR"
    assert "Simulated tool crash" in data["exception"]


def test_setup_execution_logger_file_output(tmp_path: Path):
    log_file = tmp_path / "subdir" / "execution-test.jsonl"
    logger, handler = setup_execution_logger(log_file)

    try:
        logger.info("First line")
        logger.warning("Second line with args: %s", "warning_arg")
        logger.info("Third multiline:\nLine A\nLine B")

        # Flush handler to be sure contents are on disk
        handler.flush()

        assert log_file.exists()
        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 3

        entry1 = json.loads(lines[0])
        assert entry1["message"] == "First line"
        assert entry1["level"] == "INFO"

        entry2 = json.loads(lines[1])
        assert entry2["message"] == "Second line with args: warning_arg"
        assert entry2["level"] == "WARNING"

        entry3 = json.loads(lines[2])
        assert entry3["message"] == "Third multiline:\nLine A\nLine B"
        assert entry3["level"] == "INFO"
    finally:
        logger.removeHandler(handler)
        handler.close()


def test_setup_execution_logger_avoids_duplicate_handlers(tmp_path: Path):
    log_file1 = tmp_path / "execution-1.jsonl"
    log_file2 = tmp_path / "execution-2.jsonl"

    logger1, handler1 = setup_execution_logger(log_file1)
    logger2, handler2 = setup_execution_logger(log_file2)

    assert logger1 is logger2
    assert handler1 not in logger2.handlers
    assert handler2 in logger2.handlers

    try:
        logger2.info("Testing handler replacement")
        handler2.flush()

        lines2 = log_file2.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines2) == 1
    finally:
        logger2.removeHandler(handler2)
        handler2.close()


def test_log_execution_event_llm_call(tmp_path: Path):
    from adpilot_agent.util.execution_logger import log_execution_event

    log_file = tmp_path / "execution-llm.jsonl"
    logger, handler = setup_execution_logger(log_file)

    try:
        prompts = [
            {"role": "system", "content": "You are a pentest planner."},
            {"role": "human", "content": "Plan reconnaissance for 192.168.1.0/24."},
        ]
        response = "1. Scan subnet with Nmap."
        token_usage = {"input_tokens": 250, "output_tokens": 40, "total_tokens": 290}

        log_execution_event(
            event_type="llm_call",
            caller="Planner",
            phase="external_recon",
            input=prompts,
            output=response,
            model="gemini-2.5-flash",
            token_usage=token_usage,
        )
        handler.flush()

        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1

        entry = json.loads(lines[0])
        assert entry["event_type"] == "llm_call"
        assert entry["caller"] == "Planner"
        assert entry["phase"] == "external_recon"
        assert entry["input"] == prompts
        assert entry["output"] == response
        assert entry["model"] == "gemini-2.5-flash"
        assert entry["token_usage"] == token_usage
        assert "timestamp" in entry
    finally:
        logger.removeHandler(handler)
        handler.close()


def test_log_execution_event_tool_call_and_result(tmp_path: Path):
    from adpilot_agent.util.execution_logger import log_execution_event

    log_file = tmp_path / "execution-tools.jsonl"
    logger, handler = setup_execution_logger(log_file)

    try:
        # Tool call
        log_execution_event(
            event_type="tool_call",
            caller="Executor",
            phase="external_recon",
            input={"command": "nmap -sV 192.168.1.10"},
            output=None,
            tool="shell_exec",
        )
        # Tool result
        log_execution_event(
            event_type="tool_result",
            caller="Executor",
            phase="external_recon",
            input={"command": "nmap -sV 192.168.1.10"},
            output="Starting Nmap... 80/tcp open http",
            tool="shell_exec",
        )
        handler.flush()

        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2

        call_entry = json.loads(lines[0])
        assert call_entry["event_type"] == "tool_call"
        assert call_entry["caller"] == "Executor"
        assert call_entry["input"] == {"command": "nmap -sV 192.168.1.10"}
        assert call_entry["tool"] == "shell_exec"

        res_entry = json.loads(lines[1])
        assert res_entry["event_type"] == "tool_result"
        assert res_entry["caller"] == "Executor"
        assert "80/tcp open http" in res_entry["output"]
    finally:
        logger.removeHandler(handler)
        handler.close()


def test_log_execution_event_phase_transition(tmp_path: Path):
    from adpilot_agent.util.execution_logger import log_execution_event

    log_file = tmp_path / "execution-phase.jsonl"
    logger, handler = setup_execution_logger(log_file)

    try:
        log_execution_event(
            event_type="phase_transition",
            caller="PhaseTransition",
            phase="external_recon",
            input="external_recon",
            output="initial_access",
        )
        handler.flush()

        lines = log_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1

        entry = json.loads(lines[0])
        assert entry["event_type"] == "phase_transition"
        assert entry["caller"] == "PhaseTransition"
        assert entry["phase"] == "external_recon"
        assert entry["input"] == "external_recon"
        assert entry["output"] == "initial_access"
    finally:
        logger.removeHandler(handler)
        handler.close()

