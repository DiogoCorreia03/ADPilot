from datetime import datetime
import json
import logging
from pathlib import Path
import time
from typing import Any

# Standard LogRecord attributes to ignore when extracting custom extra fields
STANDARD_RECORD_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "message",
    "module",
    "msecs",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "taskName",
    "thread",
    "threadName",
}


class JSONLFormatter(logging.Formatter):
    """
    Formats log records as JSON lines (JSONL).
    Each line emitted is a single valid JSON object.
    """

    def format(self, record: logging.LogRecord) -> str:
        # If msg is a dict or list (and no formatting args), preserve structure
        if isinstance(record.msg, (dict, list)) and not record.args:
            message: Any = record.msg
        else:
            message = record.getMessage()

        entry: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created
            ).astimezone().isoformat(),
            "name": record.name,
            "message": message,
        }

        # Include custom extra fields passed via extra={...}
        for key, value in record.__dict__.items():
            if key not in STANDARD_RECORD_ATTRS and not key.startswith("_"):
                entry[key] = value

        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            entry["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(entry, default=str, ensure_ascii=False)


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
