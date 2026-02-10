"""Unit tests for environment validation functionality."""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from main import validate_environment, DocumentIndexer


class TestValidateEnvironment:
    """Test suite for validate_environment() function."""

    def test_validate_environment_missing_api_key(self):
        """Test that missing API_KEY raises ValueError when require_llm=True."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                validate_environment(require_llm=True)

            assert "API_KEY is required" in str(exc_info.value)
            assert ".env" in str(exc_info.value)

    def test_validate_environment_missing_api_base(self):
        """Test that missing API_BASE raises ValueError when require_llm=True."""
        with patch.dict(os.environ, {"API_KEY": "test-key"}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                validate_environment(require_llm=True)

            assert "API_BASE is required" in str(exc_info.value)

    def test_validate_environment_all_required_present(self):
        """Test that validation passes when all required vars are present."""
        with patch.dict(os.environ, {
            "API_KEY": "test-key",
            "API_BASE": "https://api.example.com/v1"
        }, clear=True):
            # Should not raise any exception
            validate_environment(require_llm=True)

    def test_validate_environment_skip_when_not_required(self):
        """Test that validation is skipped when require_llm=False."""
        with patch.dict(os.environ, {}, clear=True):
            # Should not raise even though env vars are missing
            validate_environment(require_llm=False)


class TestDocumentIndexerInitialization:
    """Test suite for DocumentIndexer initialization with validation."""

    @patch('main.Settings')
    @patch('main.HuggingFaceEmbedding')
    @patch('main.CodeAwareNodeParser')
    @patch('main.CustomOpenAI')
    def test_indexer_init_with_valid_env(
        self,
        mock_openai,
        mock_parser,
        mock_embedding,
        mock_settings
    ):
        """Test DocumentIndexer initialization with valid environment."""
        with patch.dict(os.environ, {
            "API_KEY": "test-key",
            "API_BASE": "https://api.example.com/v1",
            "MODEL_NAME": "test-model"
        }, clear=True):
            indexer = DocumentIndexer("test_index")

            # Verify indexer was created successfully
            assert indexer.index_name == "test_index"
            assert indexer.require_llm is True

            # Verify LLM was configured
            mock_openai.assert_called_once()

    @patch('main.Settings')
    @patch('main.HuggingFaceEmbedding')
    @patch('main.CodeAwareNodeParser')
    def test_indexer_init_without_llm(
        self,
        mock_parser,
        mock_embedding,
        mock_settings
    ):
        """Test DocumentIndexer initialization in indexing-only mode."""
        with patch.dict(os.environ, {}, clear=True):
            # Should not raise even without API keys when require_llm=False
            indexer = DocumentIndexer("test_index", require_llm=False)

            # Verify indexer was created successfully
            assert indexer.index_name == "test_index"
            assert indexer.require_llm is False

    @patch('main.Settings')
    @patch('main.HuggingFaceEmbedding')
    @patch('main.CodeAwareNodeParser')
    def test_indexer_init_missing_api_key_fails(
        self,
        mock_parser,
        mock_embedding,
        mock_settings
    ):
        """Test that DocumentIndexer fails when API_KEY is missing and require_llm=True."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                DocumentIndexer("test_index", require_llm=True)

            assert "API_KEY is required" in str(exc_info.value)

    @patch('main.Settings')
    @patch('main.HuggingFaceEmbedding')
    @patch('main.CodeAwareNodeParser')
    def test_indexer_init_missing_api_base_fails(
        self,
        mock_parser,
        mock_embedding,
        mock_settings
    ):
        """Test that DocumentIndexer fails when API_BASE is missing."""
        with patch.dict(os.environ, {"API_KEY": "test-key"}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                DocumentIndexer("test_index", require_llm=True)

            assert "API_BASE is required" in str(exc_info.value)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
