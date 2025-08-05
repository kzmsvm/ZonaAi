from __future__ import annotations

import logging
import logging.handlers
import os
import re


# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

LOG_FILE = os.getenv("APP_LOG_FILE")
MAX_BYTES = int(os.getenv("APP_LOG_MAX_BYTES", "1048576"))
BACKUP_COUNT = int(os.getenv("APP_LOG_BACKUP_COUNT", "3"))

handlers: list[logging.Handler] = []
if LOG_FILE:
    handlers.append(
        logging.handlers.RotatingFileHandler(
            LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT
        )
    )
else:
    handlers.append(logging.StreamHandler())

logging.basicConfig(level=logging.INFO, format="%(message)s", handlers=handlers)

logger = logging.getLogger(__name__)


def logging_enabled() -> bool:
    """Return ``True`` if logging is enabled via environment configuration."""

    return os.getenv("DISABLE_LOGGING", "false").lower() not in {"1", "true", "yes"}


def sanitize(text: str) -> str:
    """Mask obvious personally identifiable information in ``text``.

    Currently masks e-mail addresses and long digit sequences (e.g. phone
    numbers or IDs) by replacing them with placeholders.
    """

    text = re.sub(
        r"[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9-.]+",
        "<email>",
        text,
    )
    text = re.sub(
        r"\b\d{5,}\b",
        lambda m: f"{m.group(0)[:2]}***{m.group(0)[-2:]}",
        text,
    )
    return text


def log_interaction(session_id: str, prompt: str, response: str) -> None:
    """Log a prompt/response pair for a given session.

    Each message is prefixed with the session identifier to make tracing
    interactions in logs straightforward.  Personally identifiable information
    is masked before logging.
    """

    if not logging_enabled():
        return

    logger.info("[%s] >> %s", session_id, sanitize(prompt))
    logger.info("[%s] << %s", session_id, sanitize(response))


def clear_logs() -> None:
    """Remove existing log files, if any.

    When a rotating file handler is used, this truncates the current log file
    and any backups so that subsequent log entries start fresh.
    """

    if not LOG_FILE:
        return

    base = os.path.abspath(LOG_FILE)
    files = [base] + [f"{base}.{i}" for i in range(1, BACKUP_COUNT + 1)]
    for path in files:
        try:
            if os.path.exists(path):
                open(path, "w").close()
        except Exception:
            pass
