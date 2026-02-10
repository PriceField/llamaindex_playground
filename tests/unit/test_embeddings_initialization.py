"""Unit tests for embedding model initialization."""
import os
import pytest
from unittest.mock import patch, MagicMock

from main import DocumentIndexer


class TestEmbeddingsInitialization:
    """Test suite for embedding model creation."""

    @patch('config.load_dotenv')
    @patch('main.validate_environment')
    @patch('main.Settings')
    @patch('main.HuggingFaceEmbedding')
    @patch('main.CodeAwareNodeParser')
    def test_create_huggingface_embeddings_default(
        self, mock_parser, mock_hf_embed, mock_settings, mock_validate, mock_dotenv
    ):
        """Test HuggingFace embeddings with default model."""
        with patch.dict(os.environ, {
            "EMBED_MODEL_TYPE": "local"
        }, clear=True):
            indexer = DocumentIndexer("test", require_llm=False)

            # Verify HuggingFaceEmbedding was called
            mock_hf_embed.assert_called_once()
            call_kwargs = mock_hf_embed.call_args[1]
            assert call_kwargs["model_name"] == "BAAI/bge-large-en-v1.5"

    @patch('config.load_dotenv')
    @patch('main.validate_environment')
    @patch('main.Settings')
    @patch('main.HuggingFaceEmbedding')
    @patch('main.CodeAwareNodeParser')
    def test_create_huggingface_embeddings_custom(
        self, mock_parser, mock_hf_embed, mock_settings, mock_validate, mock_dotenv
    ):
        """Test HuggingFace embeddings with custom model."""
        with patch.dict(os.environ, {
            "EMBED_MODEL_TYPE": "local",
            "EMBED_MODEL_NAME": "sentence-transformers/all-MiniLM-L6-v2"
        }, clear=True):
            indexer = DocumentIndexer("test", require_llm=False)

            call_kwargs = mock_hf_embed.call_args[1]
            assert call_kwargs["model_name"] == "sentence-transformers/all-MiniLM-L6-v2"

    @patch('config.load_dotenv')
    @patch('main.validate_environment')
    @patch('main.Settings')
    @patch('main.CodeAwareNodeParser')
    def test_create_openai_embeddings_with_key(
        self, mock_parser, mock_settings, mock_validate, mock_dotenv
    ):
        """Test OpenAI embeddings with API key."""
        mock_openai_embed = MagicMock()

        with patch.dict(os.environ, {
            "EMBED_MODEL_TYPE": "openai",
            "EMBED_API_KEY": "sk-test-key-123"
        }, clear=True):
            with patch('llama_index.embeddings.openai.OpenAIEmbedding', mock_openai_embed):
                indexer = DocumentIndexer("test", require_llm=False)

                # Verify OpenAIEmbedding was called
                mock_openai_embed.assert_called_once()
                call_kwargs = mock_openai_embed.call_args[1]
                assert call_kwargs["api_key"] == "sk-test-key-123"
                assert call_kwargs["model"] == "text-embedding-ada-002"

    @patch('config.load_dotenv')
    @patch('main.validate_environment')
    @patch('main.Settings')
    @patch('main.CodeAwareNodeParser')
    @patch('main.HuggingFaceEmbedding')
    def test_create_openai_embeddings_missing_key_raises(
        self, mock_hf_embed, mock_parser, mock_settings, mock_validate, mock_dotenv
    ):
        """Test OpenAI embeddings without API key raises error."""
        with patch.dict(os.environ, {
            "EMBED_MODEL_TYPE": "openai"
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                DocumentIndexer("test", require_llm=False)

            assert "OpenAI embeddings require an API key" in str(exc_info.value)

    @patch('config.load_dotenv')
    @patch('main.validate_environment')
    @patch('main.Settings')
    @patch('main.CodeAwareNodeParser')
    def test_create_openai_embeddings_fallback_to_api_key(
        self, mock_parser, mock_settings, mock_validate, mock_dotenv
    ):
        """Test OpenAI embeddings fallback to API_KEY."""
        mock_openai_embed = MagicMock()

        with patch.dict(os.environ, {
            "EMBED_MODEL_TYPE": "openai",
            "API_KEY": "fallback-key-456"
        }, clear=True):
            with patch('llama_index.embeddings.openai.OpenAIEmbedding', mock_openai_embed):
                indexer = DocumentIndexer("test", require_llm=False)

                call_kwargs = mock_openai_embed.call_args[1]
                assert call_kwargs["api_key"] == "fallback-key-456"

    @patch('config.load_dotenv')
    @patch('main.validate_environment')
    @patch('main.Settings')
    @patch('main.CodeAwareNodeParser')
    def test_create_openai_embeddings_with_custom_base(
        self, mock_parser, mock_settings, mock_validate, mock_dotenv
    ):
        """Test OpenAI embeddings with custom API base."""
        mock_openai_embed = MagicMock()

        with patch.dict(os.environ, {
            "EMBED_MODEL_TYPE": "openai",
            "EMBED_API_KEY": "test-key",
            "EMBED_API_BASE": "https://custom.endpoint.com/v1"
        }, clear=True):
            with patch('llama_index.embeddings.openai.OpenAIEmbedding', mock_openai_embed):
                indexer = DocumentIndexer("test", require_llm=False)

                call_kwargs = mock_openai_embed.call_args[1]
                assert call_kwargs["api_base"] == "https://custom.endpoint.com/v1"

    @patch('config.load_dotenv')
    @patch('main.validate_environment')
    @patch('main.Settings')
    @patch('main.CodeAwareNodeParser')
    def test_create_openai_embeddings_custom_model(
        self, mock_parser, mock_settings, mock_validate, mock_dotenv
    ):
        """Test OpenAI embeddings with custom model name."""
        mock_openai_embed = MagicMock()

        with patch.dict(os.environ, {
            "EMBED_MODEL_TYPE": "openai",
            "EMBED_API_KEY": "test-key",
            "EMBED_OPENAI_MODEL": "text-embedding-3-small"
        }, clear=True):
            with patch('llama_index.embeddings.openai.OpenAIEmbedding', mock_openai_embed):
                indexer = DocumentIndexer("test", require_llm=False)

                call_kwargs = mock_openai_embed.call_args[1]
                assert call_kwargs["model"] == "text-embedding-3-small"

    @patch('config.load_dotenv')
    @patch('main.validate_environment')
    @patch('main.Settings')
    @patch('main.HuggingFaceEmbedding')
    @patch('main.CodeAwareNodeParser')
    def test_default_behavior_no_config(
        self, mock_parser, mock_hf_embed, mock_settings, mock_validate, mock_dotenv
    ):
        """Test default behavior when no embedding config is provided."""
        with patch.dict(os.environ, {}, clear=True):
            indexer = DocumentIndexer("test", require_llm=False)

            # Should default to HuggingFace with default model
            mock_hf_embed.assert_called_once()
            call_kwargs = mock_hf_embed.call_args[1]
            assert call_kwargs["model_name"] == "BAAI/bge-large-en-v1.5"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
