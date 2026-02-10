"""Custom OpenAI LLM implementation."""

import os
from llama_index.llms.openai import OpenAI


def debug_log(message: str) -> None:
    """Print debug message if debug mode is enabled."""
    debug = os.getenv("APP_DEBUG", "False").lower() == "true"
    if debug:
        print(f"[DEBUG] {message}")


class CustomOpenAI(OpenAI):
    """Custom OpenAI LLM that bypasses model validation for custom endpoints.

    This allows using custom API endpoints (like self-hosted models)
    that may not have standard OpenAI model names.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize with custom model name support.

        Args:
            *args: Positional arguments for OpenAI
            **kwargs: Keyword arguments for OpenAI
        """
        # Temporarily store the custom model name
        custom_model = kwargs.get('model', 'gpt-3.5-turbo')  # type: ignore

        # Use a valid OpenAI model name for initialization to pass validation
        kwargs['model'] = 'gpt-3.5-turbo'  # type: ignore

        # Initialize parent class
        super().__init__(*args, **kwargs)  # type: ignore

        # Override with the actual custom model name after initialization
        self._model = custom_model
        debug_log(f"CustomOpenAI initialized with model: {custom_model}")
