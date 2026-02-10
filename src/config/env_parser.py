"""Utility for parsing environment variables with comment stripping."""

import os
from typing import Any


class EnvParser:
    """Utility class for parsing environment variables.

    Handles parsing with inline comment stripping (values after #).
    Follows Single Responsibility Principle - only parses environment values.
    """

    @staticmethod
    def parse_int(key: str, default: int) -> int:
        """Parse integer from env var, stripping inline comments.

        Args:
            key: Environment variable key
            default: Default value if not found or parse fails

        Returns:
            Parsed integer value or default
        """
        value = os.getenv(key, str(default))
        # Strip inline comments (everything after #)
        value = value.split('#')[0].strip()
        try:
            return int(value)
        except ValueError:
            return default

    @staticmethod
    def parse_bool(key: str, default: bool) -> bool:
        """Parse boolean from env var, stripping inline comments.

        Args:
            key: Environment variable key
            default: Default value if not found

        Returns:
            Parsed boolean value (true/false case-insensitive)
        """
        value = os.getenv(key, str(default))
        # Strip inline comments (everything after #)
        value = value.split('#')[0].strip()
        return value.lower() == "true"

    @staticmethod
    def parse_list(key: str, default: str = "") -> list[str]:
        """Parse comma-separated list from env var, stripping inline comments.

        Args:
            key: Environment variable key
            default: Default comma-separated string value

        Returns:
            List of parsed, trimmed strings (empty items removed)
        """
        value = os.getenv(key, default)
        # Strip inline comments (everything after #)
        value = value.split('#')[0].strip()
        return [item.strip() for item in value.split(",") if item.strip()]

    @staticmethod
    def parse_str(key: str, default: str = "") -> str:
        """Parse string from env var, stripping inline comments.

        Args:
            key: Environment variable key
            default: Default string value

        Returns:
            Parsed string value or default
        """
        value = os.getenv(key, default)
        # Strip inline comments (everything after #)
        return value.split('#')[0].strip()

    @staticmethod
    def get_required(key: str) -> str:
        """Get required environment variable.

        Args:
            key: Environment variable key

        Returns:
            Environment variable value

        Raises:
            ValueError: If environment variable is not set or empty
        """
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value.split('#')[0].strip()
