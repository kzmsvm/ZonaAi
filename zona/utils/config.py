from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


@dataclass
class Settings:
    """Application configuration derived from environment variables."""

    use_firestore: bool
    firestore_project_id: str | None
    license_key: str | None
    database_url: str | None


def load_config() -> Settings:
    """Load and validate configuration from environment variables.

    A missing ``.env`` file is logged as a warning so deployments that forget
    to copy ``.env.template`` do not fail silently.  Additional validation is
    performed for Firestore support, ensuring that ``FIRESTORE_PROJECT_ID`` is
    present when ``USE_FIRESTORE`` is enabled.
    """

    if not Path(".env").exists():
        logging.warning(".env file not found; environment variables may be missing")

    use_firestore = os.getenv("USE_FIRESTORE", "false").lower() in {"1", "true", "yes"}
    firestore_project_id = os.getenv("FIRESTORE_PROJECT_ID")
    license_key = os.getenv("LICENSE_KEY")
    database_url = os.getenv("DATABASE_URL")

    if use_firestore and not firestore_project_id:
        raise ConfigError("USE_FIRESTORE is enabled but FIRESTORE_PROJECT_ID is not set")

    return Settings(
        use_firestore=use_firestore,
        firestore_project_id=firestore_project_id,
        license_key=license_key,
        database_url=database_url,
    )


__all__ = ["ConfigError", "Settings", "load_config"]
