from datetime import datetime
import json
import logging
from pathlib import Path
import time
from typing import Any


class JSONLFormatter(logging.Formatter):
    """
    Formats log records as JSON lines (JSONL).
    Each line emitted is a single valid JSON object structured for machine and LLM ingestion.
    """

    def format(self, record: logging.LogRecord) -> str:
        event_type = getattr(record, "event_type", None)
        caller = getattr(record, "caller", None)
        phase = getattr(record, "phase", None)
        inp = getattr(record, "input", None)
        out = getattr(record, "output", None)

        if isinstance(record.msg, (dict, list)) and not record.args:
            if isinstance(record.msg, dict):
                event_type = event_type or record.msg.get("event_type")
                caller = caller or record.msg.get("caller")
                phase = phase or record.msg.get("phase")
                if inp is None:
                    inp = record.msg.get("input")
                if out is None:
                    out = record.msg.get("output")
                message = record.msg.get("message", record.msg)
            else:
                message = record.msg
        else:
            message = record.getMessage()

        entry: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created
            ).astimezone().isoformat(),
            "phase": phase,
            "caller": caller,
            "event_type": event_type or "log",
            "input": inp,
            "output": out,
            "message": message,
        }

        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            entry["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(entry, default=str, ensure_ascii=False)


def log_execution_event(
    event_type: str,
    *,
    caller: str | None = None,
    phase: Any = None,
    input: Any = None,
    output: Any = None,
    message: str | None = "",
    level: int = logging.INFO,
    logger: logging.Logger | None = None,
    **extra: Any,
) -> None:
    """
    Emits a structured event to the execution logger for analysis and LLM ingestion.
    """
    if hasattr(phase, "value"):
        phase_str = str(phase.value)
    elif phase is not None:
        phase_str = str(phase)
    else:
        phase_str = None

    target_logger = logger or logging.getLogger("execution")
    payload = {
        "event_type": event_type,
        "caller": caller,
        "phase": phase_str,
        "input": input,
        "output": output,
        **extra,
    }
    target_logger.log(level, message, extra=payload)


def setup_execution_logger(
    log_file: Path | str | None = None,
    level: int = logging.INFO,
) -> tuple[logging.Logger, logging.FileHandler]:
    """
    Configures and returns the execution logger with a JSONL FileHandler.
    """
    logger = logging.getLogger("execution")
    logger.setLevel(level)

    # Avoid adding duplicate handlers if setup is called multiple times
    for handler in list(logger.handlers):
        if getattr(handler, "_is_execution_handler", False):
            logger.removeHandler(handler)
            handler.close()

    if log_file is None:
        base_dir = Path(__file__).resolve().parent.parent.parent
        executions_dir = base_dir / "executions"
        executions_dir.mkdir(exist_ok=True)
        t = time.strftime("%Y-%m-%d_%H-%M-%S")
        file_path = executions_dir / f"execution-{t}.jsonl"
    else:
        file_path = Path(log_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(file_path, mode="w", encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(JSONLFormatter())
    setattr(handler, "_is_execution_handler", True)

    logger.addHandler(handler)
    return logger, handler
