import sys
import logging
import importlib
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))


def reload_logger():
    """Reload the logger module to apply environment changes."""
    import app.utils.logger as logger_module
    root = logging.getLogger()
    cap_handlers = [h for h in root.handlers if h.__class__.__name__ == "LogCaptureHandler"]
    for h in root.handlers[:]:
        root.removeHandler(h)
    module = importlib.reload(logger_module)
    for h in cap_handlers:
        root.addHandler(h)
    return module


def test_log_interaction(caplog):
    logger_mod = reload_logger()
    with caplog.at_level(logging.INFO):
        logger_mod.log_interaction("test-session", "Hello", "Hi there!")
    assert "[test-session] >> Hello" in caplog.text
    assert "[test-session] << Hi there!" in caplog.text


def test_log_interaction_masks_pii(caplog):
    logger_mod = reload_logger()
    with caplog.at_level(logging.INFO):
        logger_mod.log_interaction(
            "s1", "Email test@example.com", "Number 123456789"
        )
    text = caplog.text
    assert "test@example.com" not in text
    assert "123456789" not in text
    assert "<email>" in text


def test_logging_can_be_disabled(monkeypatch, caplog):
    monkeypatch.setenv("DISABLE_LOGGING", "true")
    logger_mod = reload_logger()
    with caplog.at_level(logging.INFO):
        logger_mod.log_interaction("s", "Hello", "World")
    assert caplog.text == ""
    monkeypatch.delenv("DISABLE_LOGGING", raising=False)
    reload_logger()


def test_clear_logs(tmp_path, monkeypatch):
    log_file = tmp_path / "app.log"
    monkeypatch.setenv("APP_LOG_FILE", str(log_file))
    logger_mod = reload_logger()
    logger_mod.log_interaction("s", "hi", "there")
    assert log_file.read_text() != ""
    logger_mod.clear_logs()
    assert log_file.read_text() == ""
    monkeypatch.delenv("APP_LOG_FILE", raising=False)
    reload_logger()
