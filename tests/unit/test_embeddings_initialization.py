"""Unit tests for embedding model initialization via EmbeddingFactory."""
import os
import pytest
from unittest.mock import patch, MagicMock

from config import EmbeddingConfig
from embedding import EmbeddingFactory


class TestEmbeddingFactory:
    """Test suite for EmbeddingFactory embedding model creation.

    Tests migrated from old DocumentIndexer to new architecture.
    """

    @patch('embedding.embedding_factory.HuggingFaceEmbedding')
    def test_create_huggingface_embeddings_default(self, mock_hf_embed):
        """Test HuggingFace embeddings with default model."""
        config = EmbeddingConfig.local_default()
        factory = EmbeddingFactory(config)

        factory.create()

        # Verify HuggingFaceEmbedding was called with default model
        mock_hf_embed.assert_called_once_with(model_name="BAAI/bge-large-en-v1.5")

    @patch('embedding.embedding_factory.HuggingFaceEmbedding')
    def test_create_huggingface_embeddings_custom(self, mock_hf_embed):
        """Test HuggingFace embeddings with custom model."""
        config = EmbeddingConfig(
            embed_model_type="local",
            embed_model_name="sentence-transformers/all-MiniLM-L6-v2",
            embed_api_key="",
            embed_api_base="",
            embed_openai_model=""
        )
        factory = EmbeddingFactory(config)

        factory.create()

        # Verify custom model name
        mock_hf_embed.assert_called_once_with(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    @patch('llama_index.embeddings.openai.OpenAIEmbedding')
    def test_create_openai_embeddings_with_key(self, mock_openai_embed):
        """Test OpenAI embeddings with API key."""
        config = EmbeddingConfig.openai(api_key="sk-test-key-123")
        factory = EmbeddingFactory(config)

        factory.create()

        # Verify OpenAIEmbedding was called with correct parameters
        mock_openai_embed.assert_called_once()
        call_kwargs = mock_openai_embed.call_args[1]
        assert call_kwargs["api_key"] == "sk-test-key-123"
        assert call_kwargs["model"] == "text-embedding-ada-002"

    def test_create_openai_embeddings_missing_key_raises(self):
        """Test OpenAI embeddings without API key raises error during config creation.

        Note: Validation now happens at config construction (EmbeddingConfig.__post_init__),
        which is more architecturally correct than validating at factory.create().
        """
        with pytest.raises(ValueError) as exc_info:
            EmbeddingConfig(
                embed_model_type="openai",
                embed_model_name="",
                embed_api_key="",  # Empty API key
                embed_api_base="",
                embed_openai_model="text-embedding-ada-002"
            )

        assert "embed_api_key is required" in str(exc_info.value)

    @patch.dict(os.environ, {
        "EMBED_MODEL_TYPE": "openai",
        "API_KEY": "fallback-key-456"
    }, clear=True)
    @patch('llama_index.embeddings.openai.OpenAIEmbedding')
    def test_create_openai_embeddings_fallback_to_api_key(self, mock_openai_embed):
        """Test OpenAI embeddings fallback to API_KEY when EMBED_API_KEY not set."""
        config = EmbeddingConfig.from_env()
        factory = EmbeddingFactory(config)

        factory.create()

        # Verify API_KEY was used as fallback
        call_kwargs = mock_openai_embed.call_args[1]
        assert call_kwargs["api_key"] == "fallback-key-456"

    @patch('llama_index.embeddings.openai.OpenAIEmbedding')
    def test_create_openai_embeddings_with_custom_base(self, mock_openai_embed):
        """Test OpenAI embeddings with custom API base."""
        config = EmbeddingConfig.openai(
            api_key="test-key",
            api_base="https://custom.endpoint.com/v1"
        )
        factory = EmbeddingFactory(config)

        factory.create()

        # Verify custom api_base was passed
        call_kwargs = mock_openai_embed.call_args[1]
        assert call_kwargs["api_base"] == "https://custom.endpoint.com/v1"

    @patch('llama_index.embeddings.openai.OpenAIEmbedding')
    def test_create_openai_embeddings_custom_model(self, mock_openai_embed):
        """Test OpenAI embeddings with custom model name."""
        config = EmbeddingConfig.openai(
            api_key="test-key",
            model="text-embedding-3-small"
        )
        factory = EmbeddingFactory(config)

        factory.create()

        # Verify custom model name
        call_kwargs = mock_openai_embed.call_args[1]
        assert call_kwargs["model"] == "text-embedding-3-small"

    @patch('embedding.embedding_factory.HuggingFaceEmbedding')
    def test_default_behavior_no_config(self, mock_hf_embed):
        """Test default behavior using local_default() factory method."""
        config = EmbeddingConfig.local_default()
        factory = EmbeddingFactory(config)

        factory.create()

        # Should use HuggingFace with default model
        mock_hf_embed.assert_called_once_with(model_name="BAAI/bge-large-en-v1.5")

    @patch.dict(os.environ, {}, clear=True)
    @patch('embedding.embedding_factory.HuggingFaceEmbedding')
    def test_from_env_defaults_to_local(self, mock_hf_embed):
        """Test that from_env() defaults to local embeddings when no env vars set."""
        config = EmbeddingConfig.from_env()
        factory = EmbeddingFactory(config)

        factory.create()

        # Should default to HuggingFace
        mock_hf_embed.assert_called_once_with(model_name="BAAI/bge-large-en-v1.5")

    def test_invalid_embedding_type_raises(self):
        """Test that invalid embedding type raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            EmbeddingConfig(
                embed_model_type="invalid_type",
                embed_model_name="some-model",
                embed_api_key="",
                embed_api_base="",
                embed_openai_model=""
            )

        assert "must be one of" in str(exc_info.value)

    @patch('llama_index.embeddings.openai.OpenAIEmbedding')
    def test_config_property_is_local(self, mock_openai_embed):
        """Test EmbeddingConfig.is_local property."""
        local_config = EmbeddingConfig.local_default()
        assert local_config.is_local is True
        assert local_config.is_openai is False

        openai_config = EmbeddingConfig.openai(api_key="test-key")
        assert openai_config.is_local is False
        assert openai_config.is_openai is True

    @patch('llama_index.embeddings.openai.OpenAIEmbedding')
    def test_factory_validates_openai_key_on_create(self, mock_openai_embed):
        """Test that factory validates API key exists when creating OpenAI embeddings.

        This is defensive validation in the factory layer (belt and suspenders).
        """
        # Create config directly to bypass __post_init__ validation
        # (This shouldn't normally happen, but tests the factory's defensive check)
        config = EmbeddingConfig.__new__(EmbeddingConfig)
        object.__setattr__(config, 'embed_model_type', 'openai')
        object.__setattr__(config, 'embed_model_name', '')
        object.__setattr__(config, 'embed_api_key', '')  # Empty key
        object.__setattr__(config, 'embed_api_base', '')
        object.__setattr__(config, 'embed_openai_model', 'text-embedding-ada-002')

        factory = EmbeddingFactory(config)

        with pytest.raises(ValueError) as exc_info:
            factory.create()

        assert "OpenAI embeddings require an API key" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
