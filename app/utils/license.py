from __future__ import annotations

"""Simple license key validation utilities."""

import os
from typing import Optional

from fastapi import HTTPException


class LicenseManager:
    """Validate license keys for premium features.

    A license key may be supplied either via the ``LICENSE_KEY`` environment
    variable or through the ``X-License-Key`` HTTP header. The expected license
    value is read from the ``LICENSE_KEY`` environment variable. When no license
    is configured the application operates in free mode and premium features are
    unavailable.
    """

    ENV_NAME = "LICENSE_KEY"
    HEADER_NAME = "X-License-Key"

    @classmethod
    def validate_license(cls, license_key: Optional[str] = None) -> bool:
        """Return ``True`` if the provided key matches the configured license."""
        expected = os.getenv(cls.ENV_NAME)
        if expected is None:
            return False
        if license_key is None:
            # If no key was provided explicitly, consider the presence of the
            # environment variable sufficient.
            return True
        return license_key == expected

    @classmethod
    def require_license(cls, license_key: Optional[str] = None) -> None:
        """Raise an HTTPException if a valid license is not supplied."""
        if not cls.validate_license(license_key):
            raise HTTPException(
                status_code=403,
                detail="A valid license key is required.",
            )
