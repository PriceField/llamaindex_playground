"""Configuration for embedding models."""

from dataclasses import dataclass
from .env_parser import EnvParser
import os


@dataclass(frozen=True)
class EmbeddingConfig:
    """Configuration for embedding model setup.

    Follows Interface Segregation Principle - clients only depend on
    embedding-related settings.

    Attributes:
        embed_model_type: Type of embedding model ("local" or "openai")
        embed_model_name: HuggingFace model name for local embeddings
        embed_api_key: API key for OpenAI embeddings
        embed_api_base: Base URL for OpenAI API (optional)
        embed_openai_model: OpenAI model name for embeddings
    """

    embed_model_type: str
    embed_model_name: str
    embed_api_key: str
    embed_api_base: str
    embed_openai_model: str

    def __post_init__(self) -> None:
        """Validate configuration."""
        valid_types = ["local", "openai"]
        if self.embed_model_type not in valid_types:
            raise ValueError(
                f"embed_model_type must be one of {valid_types}, got '{self.embed_model_type}'"
            )

        if self.embed_model_type == "openai" and not self.embed_api_key:
            raise ValueError("embed_api_key is required when embed_model_type is 'openai'")

        if self.embed_model_type == "local" and not self.embed_model_name:
            raise ValueError("embed_model_name is required when embed_model_type is 'local'")

    @property
    def is_local(self) -> bool:
        """Check if using local embeddings."""
        return self.embed_model_type == "local"

    @property
    def is_openai(self) -> bool:
        """Check if using OpenAI embeddings."""
        return self.embed_model_type == "openai"

    @classmethod
    def from_env(cls) -> "EmbeddingConfig":
        """Create configuration from environment variables.

        Returns:
            EmbeddingConfig instance loaded from environment
        """
        embed_model_type = EnvParser.parse_str("EMBED_MODEL_TYPE", "local").lower()

        # Validate and default invalid types
        if embed_model_type not in ["local", "openai"]:
            print(f"[!] Invalid EMBED_MODEL_TYPE '{embed_model_type}', defaulting to 'local'")
            embed_model_type = "local"

        # Fallback to API_KEY if EMBED_API_KEY not set (single source of truth)
        embed_api_key = os.getenv("EMBED_API_KEY") or os.getenv("API_KEY", "")

        return cls(
            embed_model_type=embed_model_type,
            embed_model_name=EnvParser.parse_str("EMBED_MODEL_NAME", "BAAI/bge-large-en-v1.5"),
            embed_api_key=embed_api_key,
            embed_api_base=EnvParser.parse_str("EMBED_API_BASE", ""),
            embed_openai_model=EnvParser.parse_str("EMBED_OPENAI_MODEL", "text-embedding-ada-002"),
        )

    @classmethod
    def local_default(cls) -> "EmbeddingConfig":
        """Create configuration for local embeddings with defaults.

        Returns:
            EmbeddingConfig for local HuggingFace embeddings
        """
        return cls(
            embed_model_type="local",
            embed_model_name="BAAI/bge-large-en-v1.5",
            embed_api_key="",
            embed_api_base="",
            embed_openai_model="",
        )

    @classmethod
    def openai(
        cls,
        api_key: str,
        model: str = "text-embedding-ada-002",
        api_base: str = ""
    ) -> "EmbeddingConfig":
        """Create configuration for OpenAI embeddings.

        Args:
            api_key: OpenAI API key
            model: OpenAI embedding model name
            api_base: Optional custom API base URL

        Returns:
            EmbeddingConfig for OpenAI embeddings
        """
        return cls(
            embed_model_type="openai",
            embed_model_name="",
            embed_api_key=api_key,
            embed_api_base=api_base,
            embed_openai_model=model,
        )
