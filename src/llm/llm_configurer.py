"""Configurer for LLM setup."""

import os
from dataclasses import dataclass

from llama_index.core import Settings

from .custom_openai import CustomOpenAI


@dataclass(frozen=True)
class LLMConfig:
    """Configuration for LLM setup.

    Attributes:
        api_key: API key for LLM service
        api_base: Base URL for API endpoint
        model_name: Model name to use
        temperature: Temperature for generation (0.0-1.0)
    """

    api_key: str
    api_base: str
    model_name: str
    temperature: float = 0.7

    def __post_init__(self) -> None:
        """Validate configuration."""
        if not self.api_key:
            raise ValueError("api_key cannot be empty")
        if not self.api_base:
            raise ValueError("api_base cannot be empty")
        if not self.model_name:
            raise ValueError("model_name cannot be empty")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError(f"temperature must be between 0.0 and 2.0, got {self.temperature}")

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Create configuration from environment variables.

        Returns:
            LLMConfig instance loaded from environment

        Raises:
            ValueError: If required environment variables are missing
        """
        api_key = os.getenv("API_KEY")
        if not api_key:
            raise ValueError(
                "API_KEY is required in .env file\n"
                "Copy .env.example to .env and add your API key"
            )

        api_base = os.getenv("API_BASE")
        if not api_base:
            raise ValueError(
                "API_BASE is required in .env file\n"
                "Copy .env.example to .env and configure your API endpoint"
            )

        model_name = os.getenv("MODEL_NAME", "claude-sonnet-4-5-20250929")
        temperature = float(os.getenv("TEMPERATURE", "0.7"))

        return cls(
            api_key=api_key,
            api_base=api_base,
            model_name=model_name,
            temperature=temperature,
        )


class LLMConfigurer:
    """Configures LLM for the indexer.

    Follows Single Responsibility Principle - only configures LLM.
    """

    def __init__(self, config: LLMConfig):
        """Initialize with configuration.

        Args:
            config: LLM configuration
        """
        self.config = config

    def configure(self) -> None:
        """Configure the global LLM settings.

        This sets up the LlamaIndex Settings.llm with CustomOpenAI.
        """
        print("\n[*] Setting up LLM...")

        Settings.llm = CustomOpenAI(
            api_key=self.config.api_key,
            api_base=self.config.api_base,
            model=self.config.model_name,
            temperature=self.config.temperature,
        )

        print(f"[OK] LLM configured: {self.config.model_name}")

    @staticmethod
    def skip_configuration() -> None:
        """Skip LLM configuration (indexing-only mode).

        This is used when running in indexing-only mode without LLM.
        """
        print("\n[*] Indexing-only mode: LLM not configured")
