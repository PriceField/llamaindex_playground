"""Unit tests for config module."""
import os
import sys
import pytest
from unittest.mock import patch

# Add src to path
sys.path.insert(0, 'src')

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


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
