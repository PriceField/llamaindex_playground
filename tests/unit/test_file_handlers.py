"""Unit tests for file_handlers module."""
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, 'src')

from file_handlers import FileHandler


class TestFileHandler:
    """Test suite for FileHandler class."""

    def test_should_index_file_with_user_extensions_match(self, mock_config):
        """Test that files matching user extensions are indexed."""
        handler = FileHandler(mock_config)

        result = handler.should_index_file("test.py", user_extensions=[".py", ".js"])

        assert result is True

    def test_should_index_file_with_user_extensions_no_match(self, mock_config):
        """Test that files not matching user extensions are excluded."""
        handler = FileHandler(mock_config)

        result = handler.should_index_file("test.md", user_extensions=[".py", ".js"])

        assert result is False

    def test_should_index_file_exclude_default_patterns(self, mock_config):
        """Test that default exclude patterns are applied."""
        handler = FileHandler(mock_config)

        # Test default exclusions
        assert handler.should_index_file("node_modules/package.js") is False
        assert handler.should_index_file("__pycache__/module.pyc") is False
        assert handler.should_index_file(".git/config") is False

    def test_should_index_file_exclude_user_patterns(self, mock_config):
        """Test that user-provided exclude patterns are applied."""
        handler = FileHandler(mock_config)

        result = handler.should_index_file(
            "src/test.py",
            user_exclude=["*test*"]
        )

        assert result is False

    def test_should_index_file_user_patterns_combined_with_defaults(self, mock_config):
        """Test that user exclude patterns are combined with defaults."""
        handler = FileHandler(mock_config)

        # User pattern should exclude
        assert handler.should_index_file("my_backup.py", user_exclude=["*backup*"]) is False

        # Default pattern should still work
        assert handler.should_index_file("node_modules/lib.js", user_exclude=["*backup*"]) is False

    def test_matches_pattern_with_wildcards(self, mock_config):
        """Test pattern matching with glob wildcards."""
        handler = FileHandler(mock_config)

        assert handler._matches_pattern("test.pyc", "*.pyc") is True
        assert handler._matches_pattern("src/test.pyc", "*.pyc") is True
        assert handler._matches_pattern("test.py", "*.pyc") is False
        assert handler._matches_pattern("file.test.js", "*test*") is True

    def test_matches_pattern_with_substring(self, mock_config):
        """Test pattern matching with substring (no wildcards)."""
        handler = FileHandler(mock_config)

        assert handler._matches_pattern("path/node_modules/file.js", "node_modules") is True
        assert handler._matches_pattern("path/src/file.js", "node_modules") is False
        assert handler._matches_pattern("__pycache__/module.pyc", "__pycache__") is True

    def test_get_file_metadata_python_file(self, mock_config):
        """Test metadata extraction for Python files."""
        mock_config.detect_language.return_value = "python"
        mock_config.detect_category.return_value = "code"

        handler = FileHandler(mock_config)
        metadata = handler.get_file_metadata("src/main.py")

        assert "file_path" in metadata
        assert metadata["file_name"] == "main.py"
        assert metadata["file_extension"] == ".py"
        assert metadata["language"] == "python"
        assert metadata["category"] == "code"

        # Verify config methods were called
        mock_config.detect_language.assert_called_once()
        mock_config.detect_category.assert_called_once()

    def test_get_file_metadata_documentation_file(self, mock_config):
        """Test metadata extraction for documentation files."""
        mock_config.detect_language.return_value = "unknown"
        mock_config.detect_category.return_value = "documentation"

        handler = FileHandler(mock_config)
        metadata = handler.get_file_metadata("docs/README.md")

        assert metadata["file_name"] == "README.md"
        assert metadata["file_extension"] == ".md"
        assert metadata["language"] == "unknown"
        assert metadata["category"] == "documentation"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
