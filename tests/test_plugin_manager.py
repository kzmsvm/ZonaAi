import sys
from pathlib import Path
import re

# Ensure project root is in sys.path for imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

from zona.plugin_manager import handle_plugin_command


def test_handle_plugin_command_hello():
    result = handle_plugin_command("!hello")
    assert result == "\U0001F44B Hello from Zona Plugin!"


def test_handle_plugin_command_time():
    result = handle_plugin_command("!time")
    assert result.startswith("\U0001F552 Current server time is ")
    assert re.match(r"\U0001F552 Current server time is \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", result)


def test_handle_plugin_command_math():
    result = handle_plugin_command("!math 2+2")
    assert result == "\U0001F9EE Result: 4"
