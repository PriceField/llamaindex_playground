"""Environment validation utilities."""

import os


def validate_environment(require_llm: bool = True) -> None:
    """Validate required environment variables.

    Args:
        require_llm: If True, validate API_KEY and API_BASE are set

    Raises:
        ValueError: If required environment variables are missing
    """
    if require_llm:
        api_key = os.getenv("API_KEY")
        if not api_key:
            raise ValueError(
                "API_KEY is required in .env file\n"
                "Copy .env.example to .env and add your API key\n"
                "Or run with --no-llm flag for indexing-only mode"
            )

        api_base = os.getenv("API_BASE")
        if not api_base:
            raise ValueError(
                "API_BASE is required in .env file\n"
                "Copy .env.example to .env and configure your API endpoint"
            )

        debug = os.getenv("APP_DEBUG", "False").lower() == "true"
        if debug:
            print(f"[DEBUG] Environment validated: API_KEY and API_BASE present")
