"""Unit tests for config module."""
import os
import pytest
from unittest.mock import patch

from config import IndexerConfig


class TestIndexerConfig:
    """Test suite for IndexerConfig class."""

    @patch.dict(os.environ, {"CODE_CHUNK_SIZE": "256"}, clear=True)
    def test_parse_int_with_valid_value(self):
        """Test parsing integer from environment variable."""
        config = IndexerConfig()

        assert config.code_chunk_size == 256

    @patch.dict(os.environ, {"CODE_CHUNK_SIZE": "512 # default chunk size"}, clear=True)
    def test_parse_int_with_inline_comment(self):
        """Test parsing integer with inline comment stripped."""
        config = IndexerConfig()

        assert config.code_chunk_size == 512

    @patch.dict(os.environ, {"CODE_CHUNK_SIZE": "invalid_number"}, clear=True)
    def test_parse_int_with_invalid_value_returns_default(self):
        """Test that invalid integer values return default."""
        config = IndexerConfig()

        # Should use default value (512)
        assert config.code_chunk_size == 512

    @patch.dict(os.environ, {"EXTRACT_FUNCTIONS": "true"}, clear=True)
    def test_parse_bool_with_true_value(self):
        """Test parsing boolean true value."""
        config = IndexerConfig()

        assert config.extract_functions is True

    @patch.dict(os.environ, {"EXTRACT_FUNCTIONS": "false # disable extraction"}, clear=True)
    def test_parse_bool_with_inline_comment(self):
        """Test parsing boolean with inline comment stripped."""
        config = IndexerConfig()

        assert config.extract_functions is False

    @patch.dict(os.environ, {}, clear=True)
    def test_detect_language_known_extension(self):
        """Test language detection for known file extensions."""
        config = IndexerConfig()

        assert config.detect_language("test.py") == "python"
        assert config.detect_language("app.js") == "javascript"
        assert config.detect_language("Main.java") == "java"
        assert config.detect_language("main.go") == "go"
        assert config.detect_language("script.ts") == "typescript"

    @patch.dict(os.environ, {}, clear=True)
    def test_detect_language_unknown_extension(self):
        """Test language detection for unknown file extensions."""
        config = IndexerConfig()

        assert config.detect_language("file.xyz") == "unknown"
        assert config.detect_language("README") == "unknown"

    @patch.dict(os.environ, {}, clear=True)
    def test_detect_category_code_file(self):
        """Test category detection for code files."""
        config = IndexerConfig()

        assert config.detect_category("test.py") == "code"
        assert config.detect_category("app.js") == "code"
        assert config.detect_category("Main.java") == "code"
        assert config.detect_category("main.rs") == "code"

    @patch.dict(os.environ, {}, clear=True)
    def test_detect_category_documentation_file(self):
        """Test category detection for documentation files."""
        config = IndexerConfig()

        assert config.detect_category("README.md") == "documentation"
        assert config.detect_category("guide.rst") == "documentation"
        assert config.detect_category("notes.txt") == "documentation"

    @patch.dict(os.environ, {}, clear=True)
    def test_detect_category_configuration_file(self):
        """Test category detection for configuration files."""
        config = IndexerConfig()

        assert config.detect_category("package.json") == "configuration"
        assert config.detect_category("config.yaml") == "configuration"
        assert config.detect_category("settings.toml") == "configuration"

    @patch.dict(os.environ, {}, clear=True)
    def test_detect_category_unknown_file(self):
        """Test category detection for unknown file types."""
        config = IndexerConfig()

        assert config.detect_category("file.xyz") == "other"
        assert config.detect_category("unknown") == "other"

    @patch.dict(os.environ, {"SUPPORTED_LANGUAGES": "python,javascript # main languages"}, clear=True)
    def test_parse_list_with_inline_comment(self):
        """Test parsing comma-separated list with inline comment."""
        config = IndexerConfig()

        assert "python" in config.supported_languages
        assert "javascript" in config.supported_languages
        assert len(config.supported_languages) == 2


class TestEmbeddingConfig:
    """Test suite for embedding configuration in IndexerConfig."""

    @patch.dict(os.environ, {"EMBED_MODEL_TYPE": "local"}, clear=True)
    def test_embed_type_local(self):
        """Test EMBED_MODEL_TYPE=local."""
        config = IndexerConfig()
        assert config.embed_model_type == "local"

    @patch('config.load_dotenv')
    @patch.dict(os.environ, {"EMBED_MODEL_TYPE": "openai"}, clear=True)
    def test_embed_type_openai(self, mock_dotenv):
        """Test EMBED_MODEL_TYPE=openai."""
        config = IndexerConfig()
        assert config.embed_model_type == "openai"

    @patch.dict(os.environ, {"EMBED_MODEL_NAME": "sentence-transformers/all-MiniLM-L6-v2"}, clear=True)
    def test_custom_huggingface_model(self):
        """Test custom HuggingFace model name."""
        config = IndexerConfig()
        assert config.embed_model_name == "sentence-transformers/all-MiniLM-L6-v2"

    @patch('config.load_dotenv')
    @patch.dict(os.environ, {}, clear=True)
    def test_default_huggingface_model(self, mock_dotenv):
        """Test default HuggingFace model name."""
        config = IndexerConfig()
        assert config.embed_model_name == "BAAI/bge-large-en-v1.5"

    @patch.dict(os.environ, {"EMBED_OPENAI_MODEL": "text-embedding-3-small"}, clear=True)
    def test_custom_openai_model(self):
        """Test custom OpenAI model name."""
        config = IndexerConfig()
        assert config.embed_openai_model == "text-embedding-3-small"

    @patch.dict(os.environ, {}, clear=True)
    def test_default_openai_model(self):
        """Test default OpenAI model name."""
        config = IndexerConfig()
        assert config.embed_openai_model == "text-embedding-ada-002"

    @patch('config.load_dotenv')
    @patch.dict(os.environ, {"EMBED_MODEL_TYPE": "INVALID"}, clear=True)
    def test_invalid_embed_type_defaults_to_local(self, mock_dotenv, capsys):
        """Test invalid EMBED_MODEL_TYPE defaults to local with warning."""
        config = IndexerConfig()
        assert config.embed_model_type == "local"
        # Check that warning was printed
        captured = capsys.readouterr()
        assert "[!] Invalid EMBED_MODEL_TYPE" in captured.out

    @patch.dict(os.environ, {"EMBED_API_KEY": "test-key-123"}, clear=True)
    def test_embed_api_key(self):
        """Test EMBED_API_KEY is stored."""
        config = IndexerConfig()
        assert config.embed_api_key == "test-key-123"

    @patch('config.load_dotenv')
    @patch.dict(os.environ, {"API_KEY": "fallback-key-456"}, clear=True)
    def test_embed_api_key_fallback_to_api_key(self, mock_dotenv):
        """Test EMBED_API_KEY falls back to API_KEY when not set."""
        config = IndexerConfig()
        assert config.embed_api_key == "fallback-key-456"

    @patch('config.load_dotenv')
    @patch.dict(os.environ, {"EMBED_API_KEY": "embed-key", "API_KEY": "api-key"}, clear=True)
    def test_embed_api_key_takes_precedence_over_api_key(self, mock_dotenv):
        """Test EMBED_API_KEY takes precedence over API_KEY."""
        config = IndexerConfig()
        assert config.embed_api_key == "embed-key"

    @patch.dict(os.environ, {"EMBED_API_BASE": "https://custom.api.com"}, clear=True)
    def test_embed_api_base(self):
        """Test EMBED_API_BASE is stored."""
        config = IndexerConfig()
        assert config.embed_api_base == "https://custom.api.com"

    @patch('config.load_dotenv')
    @patch.dict(os.environ, {}, clear=True)
    def test_default_embed_api_key_empty(self, mock_dotenv):
        """Test EMBED_API_KEY defaults to empty string when neither is set."""
        config = IndexerConfig()
        assert config.embed_api_key == ""

    @patch('config.load_dotenv')
    @patch.dict(os.environ, {}, clear=True)
    def test_default_embed_api_base_empty(self, mock_dotenv):
        """Test EMBED_API_BASE defaults to empty string."""
        config = IndexerConfig()
        assert config.embed_api_base == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
