import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.utils.logger import log_interaction


def test_log_interaction(capsys):
    log_interaction("test-session", "Hello", "Hi there!")
    captured = capsys.readouterr()
    assert "[test-session] >> Hello" in captured.out
    assert "[test-session] << Hi there!" in captured.out
