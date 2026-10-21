import json
import logging
import time
from uuid import uuid4
from datetime import datetime, timezone
from contextvars import ContextVar

# ContextVar 用於在異步請求與執行緒間傳遞 trace_id
trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="")

class JsonLogFormatter(logging.Formatter):
    """結構化 JSON 日誌格式化器 (符合現代維運可觀測性標準)"""

    def format(self, record: logging.LogRecord) -> str:
        current_trace = trace_id_ctx.get() or getattr(record, "trace_id", None) or uuid4().hex
        log_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "trace_id": current_trace,
            "message": record.getMessage(),
            "file": record.filename,
            "line": record.lineno
        }
        if hasattr(record, "job_id"):
            log_payload["job_id"] = str(record.job_id)
        if hasattr(record, "step"):
            log_payload["step"] = str(record.step)
        if hasattr(record, "elapsed_ms"):
            log_payload["elapsed_ms"] = record.elapsed_ms
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_payload, ensure_ascii=False)

def setup_logger(name: str = "video_pipeline") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonLogFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
