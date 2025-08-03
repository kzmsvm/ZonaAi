import sys
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.utils.logger import log_interaction


def test_log_interaction(caplog):
    with caplog.at_level(logging.INFO):
        log_interaction("test-session", "Hello", "Hi there!")

    assert "[test-session] >> Hello" in caplog.text
    assert "[test-session] << Hi there!" in caplog.text
