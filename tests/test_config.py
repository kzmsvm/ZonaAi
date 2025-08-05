import os
import sys
from pathlib import Path

import pytest

# Ensure project root is in sys.path for imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

from zona.utils.config import ConfigError, load_config


def test_firestore_requires_project_id(monkeypatch):
    monkeypatch.setenv("USE_FIRESTORE", "true")
    monkeypatch.delenv("FIRESTORE_PROJECT_ID", raising=False)
    with pytest.raises(ConfigError):
        load_config()


def test_load_config_defaults(monkeypatch):
    monkeypatch.delenv("USE_FIRESTORE", raising=False)
    monkeypatch.delenv("FIRESTORE_PROJECT_ID", raising=False)
    settings = load_config()
    assert settings.use_firestore is False
    assert settings.firestore_project_id is None
