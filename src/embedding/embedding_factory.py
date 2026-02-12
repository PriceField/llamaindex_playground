"""Factory for creating embedding models."""

from typing import TYPE_CHECKING

from llama_index.core.embeddings import BaseEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

if TYPE_CHECKING:
    from llama_index.embeddings.openai import OpenAIEmbedding

from config import EmbeddingConfig


class EmbeddingFactory:
    """Factory for creating embedding models.

    Follows Single Responsibility Principle - only creates embeddings.
    Follows Open/Closed Principle - can be extended via strategy pattern later.
    """

    def __init__(self, config: EmbeddingConfig):
        """Initialize factory with configuration.

        Args:
            config: Embedding configuration
        """
        self.config = config

    def create(self) -> BaseEmbedding:
        """Create embedding model based on configuration.

        Returns:
            BaseEmbedding: Configured embedding model (HuggingFace or OpenAI)

        Raises:
            ValueError: If configuration is invalid
        """
        if self.config.is_openai:
            return self._create_openai()
        elif self.config.is_local:
            return self._create_huggingface()
        else:
            raise ValueError(f"Unknown embedding type: {self.config.embed_model_type}")

    def _create_huggingface(self) -> HuggingFaceEmbedding:
        """Create HuggingFace embedding model.

        Returns:
            HuggingFaceEmbedding: Configured HuggingFace embeddings
        """
        model_name = self.config.embed_model_name
        device = self.config.embed_device

        # Validate GPU availability if GPU requested
        if device.startswith("cuda"):
            try:
                import torch
                if not torch.cuda.is_available():
                    print(f"[!] CUDA not available, falling back to CPU")
                    device = "cpu"
                else:
                    print(f"[OK] Using GPU: {torch.cuda.get_device_name(0)}")
            except ImportError:
                print(f"[!] PyTorch not found, falling back to CPU")
                device = "cpu"

        print(f"[OK] Embeddings configured: HuggingFace - {model_name} (device: {device})")

        # Models requiring trust_remote_code
        trust_remote_models = [
            "nomic-ai/nomic-embed-text-v1.5",
            "nomic-ai/nomic-embed-text-v1",
            "nomic-ai/nomic-bert-2048"
        ]

        # Check if model requires trust_remote_code
        trust_remote_code = any(model in model_name for model in trust_remote_models)

        return HuggingFaceEmbedding(
            model_name=model_name,
            device=device,
            trust_remote_code=trust_remote_code
        )

    def _create_openai(self) -> "OpenAIEmbedding":
        """Create OpenAI embedding model.

        Returns:
            OpenAIEmbedding: Configured OpenAI embeddings

        Raises:
            ValueError: If API key is not configured
        """
        from llama_index.embeddings.openai import OpenAIEmbedding

        # Validate API key
        if not self.config.embed_api_key:
            raise ValueError(
                "OpenAI embeddings require an API key.\n"
                "Set EMBED_API_KEY or API_KEY in your .env file"
            )

        # Build kwargs for OpenAIEmbedding
        kwargs = {
            "api_key": self.config.embed_api_key,
            "model": self.config.embed_openai_model,
        }

        # Add api_base if configured
        if self.config.embed_api_base:
            kwargs["api_base"] = self.config.embed_api_base

        print(f"[OK] Embeddings configured: OpenAI - {self.config.embed_openai_model}")
        if self.config.embed_api_base:
            print(f"    Using custom endpoint: {self.config.embed_api_base}")

        return OpenAIEmbedding(**kwargs)
