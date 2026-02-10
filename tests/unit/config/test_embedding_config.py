"""Unit tests for EmbeddingConfig."""
import os
import pytest
from unittest.mock import patch

from config import EmbeddingConfig


class TestEmbeddingConfig:
    """Test suite for EmbeddingConfig class."""

    @patch.dict(os.environ, {"EMBED_MODEL_TYPE": "local"}, clear=True)
    def test_from_env_with_local_type(self):
        """Test EmbeddingConfig.from_env() with EMBED_MODEL_TYPE=local."""
        config = EmbeddingConfig.from_env()
        assert config.embed_model_type == "local"

    @patch.dict(os.environ, {"EMBED_MODEL_TYPE": "openai", "EMBED_API_KEY": "test-key"}, clear=True)
    def test_from_env_with_openai_type(self):
        """Test EmbeddingConfig.from_env() with EMBED_MODEL_TYPE=openai."""
        config = EmbeddingConfig.from_env()
        assert config.embed_model_type == "openai"

    @patch.dict(os.environ, {"EMBED_MODEL_NAME": "sentence-transformers/all-MiniLM-L6-v2"}, clear=True)
    def test_from_env_with_custom_huggingface_model(self):
        """Test custom HuggingFace model name."""
        config = EmbeddingConfig.from_env()
        assert config.embed_model_name == "sentence-transformers/all-MiniLM-L6-v2"

    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_default_huggingface_model(self):
        """Test default HuggingFace model name."""
        config = EmbeddingConfig.from_env()
        # Default should be local with BAAI model
        assert config.embed_model_type == "local"
        assert config.embed_model_name == "BAAI/bge-large-en-v1.5"

    @patch.dict(os.environ, {"EMBED_OPENAI_MODEL": "text-embedding-3-small"}, clear=True)
    def test_from_env_with_custom_openai_model(self):
        """Test custom OpenAI model name."""
        config = EmbeddingConfig.from_env()
        assert config.embed_openai_model == "text-embedding-3-small"

    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_default_openai_model(self):
        """Test default OpenAI model name."""
        config = EmbeddingConfig.from_env()
        assert config.embed_openai_model == "text-embedding-ada-002"

    @patch.dict(os.environ, {"EMBED_MODEL_TYPE": "INVALID"}, clear=True)
    def test_from_env_with_invalid_type_defaults_to_local(self, capsys):
        """Test invalid EMBED_MODEL_TYPE defaults to local with warning."""
        config = EmbeddingConfig.from_env()
        assert config.embed_model_type == "local"

    @patch.dict(os.environ, {"EMBED_API_KEY": "test-key-123"}, clear=True)
    def test_from_env_with_api_key(self):
        """Test EMBED_API_KEY is stored."""
        config = EmbeddingConfig.from_env()
        assert config.embed_api_key == "test-key-123"

    @patch.dict(os.environ, {"API_KEY": "fallback-key-456"}, clear=True)
    def test_from_env_api_key_fallback_to_api_key(self):
        """Test EMBED_API_KEY falls back to API_KEY when not set."""
        config = EmbeddingConfig.from_env()
        assert config.embed_api_key == "fallback-key-456"

    @patch.dict(os.environ, {"EMBED_API_KEY": "embed-key", "API_KEY": "api-key"}, clear=True)
    def test_from_env_api_key_takes_precedence(self):
        """Test EMBED_API_KEY takes precedence over API_KEY."""
        config = EmbeddingConfig.from_env()
        assert config.embed_api_key == "embed-key"

    @patch.dict(os.environ, {"EMBED_API_BASE": "https://custom.api.com"}, clear=True)
    def test_from_env_with_api_base(self):
        """Test EMBED_API_BASE is stored."""
        config = EmbeddingConfig.from_env()
        assert config.embed_api_base == "https://custom.api.com"

    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_default_api_key_empty(self):
        """Test EMBED_API_KEY defaults to empty string when neither is set."""
        config = EmbeddingConfig.from_env()
        assert config.embed_api_key == ""

    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_default_api_base_empty(self):
        """Test EMBED_API_BASE defaults to empty string."""
        config = EmbeddingConfig.from_env()
        assert config.embed_api_base == ""

    def test_default_factory_method(self):
        """Test EmbeddingConfig.default() factory method."""
        config = EmbeddingConfig.default()
        assert config.embed_model_type == "local"
        assert config.embed_model_name == "BAAI/bge-large-en-v1.5"
        assert config.embed_model_dimension == 1024

    def test_config_is_frozen(self):
        """Test that EmbeddingConfig instances are immutable."""
        config = EmbeddingConfig.default()
        with pytest.raises(Exception):  # Frozen dataclass raises FrozenInstanceError
            config.embed_model_type = "openai"

    @patch.dict(os.environ, {"EMBED_MODEL_DIMENSION": "384"}, clear=True)
    def test_from_env_with_custom_dimension(self):
        """Test custom embedding dimension."""
        config = EmbeddingConfig.from_env()
        assert config.embed_model_dimension == 384


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
