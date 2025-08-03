from __future__ import annotations

import logging


# Configure a simple logger that writes messages to standard output.
# `basicConfig` is a no-op if logging has already been configured by the
# application, preventing duplicate handlers when this module is imported
# multiple times.
logging.basicConfig(level=logging.INFO, format="%(message)s")

logger = logging.getLogger(__name__)


def log_interaction(session_id: str, prompt: str, response: str) -> None:
    """Log a prompt/response pair for a given session.

    Each message is prefixed with the session identifier to make tracing
    interactions in logs straightforward.
    """

    logger.info("[%s] >> %s", session_id, prompt)
    logger.info("[%s] << %s", session_id, response)
