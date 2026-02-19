"""Unit tests for file_handlers module."""
import pytest
from pathlib import Path

from file_handlers import FileHandler


class TestFileHandler:
    """Test suite for FileHandler class."""

    def test_should_index_file_with_user_extensions_match(
        self, file_filter_config, language_detector, file_categorizer
    ):
        """Test that files matching user extensions are indexed."""
        handler = FileHandler(file_filter_config, language_detector, file_categorizer)

        result = handler.should_index_file("test.py", user_extensions=[".py", ".js"])

        assert result is True

    def test_should_index_file_with_user_extensions_no_match(
        self, file_filter_config, language_detector, file_categorizer
    ):
        """Test that files not matching user extensions are excluded."""
        handler = FileHandler(file_filter_config, language_detector, file_categorizer)

        result = handler.should_index_file("test.md", user_extensions=[".py", ".js"])

        assert result is False

    def test_should_index_file_exclude_default_patterns(
        self, file_filter_config, language_detector, file_categorizer
    ):
        """Test that default exclude patterns are applied."""
        handler = FileHandler(file_filter_config, language_detector, file_categorizer)

        # Test default exclusions (from fixture: node_modules, __pycache__, .git)
        assert handler.should_index_file("node_modules/package.js") is False
        assert handler.should_index_file("__pycache__/module.pyc") is False
        assert handler.should_index_file(".git/config") is False

    def test_should_index_file_exclude_user_patterns(
        self, file_filter_config, language_detector, file_categorizer
    ):
        """Test that user-provided exclude patterns are applied."""
        handler = FileHandler(file_filter_config, language_detector, file_categorizer)

        result = handler.should_index_file(
            "src/test.py",
            user_exclude=["*test*"]
        )

        assert result is False

    def test_should_index_file_user_patterns_combined_with_defaults(
        self, file_filter_config, language_detector, file_categorizer
    ):
        """Test that user exclude patterns are combined with defaults."""
        handler = FileHandler(file_filter_config, language_detector, file_categorizer)

        # User pattern should exclude
        assert handler.should_index_file("my_backup.py", user_exclude=["*backup*"]) is False

        # Default pattern should still work
        assert handler.should_index_file("node_modules/lib.js", user_exclude=["*backup*"]) is False

    def test_should_exclude_env_files(
        self, file_filter_config, language_detector, file_categorizer
    ):
        """Test that .env files are excluded (security critical)."""
        handler = FileHandler(file_filter_config, language_detector, file_categorizer)

        # .env files should be excluded to prevent indexing secrets
        assert handler.should_index_file(".env") is False
        assert handler.should_index_file("config/.env") is False
        assert handler.should_index_file(".env.local") is False
        assert handler.should_index_file("project/.env.production") is False

    def test_should_exclude_ide_directories(
        self, file_filter_config, language_detector, file_categorizer
    ):
        """Test that IDE configuration directories are excluded."""
        handler = FileHandler(file_filter_config, language_detector, file_categorizer)

        # VS Code
        assert handler.should_index_file(".vscode/settings.json") is False
        assert handler.should_index_file("project/.vscode/launch.json") is False

        # IntelliJ/PyCharm
        assert handler.should_index_file(".idea/workspace.xml") is False
        assert handler.should_index_file("project/.idea/modules.xml") is False

        # Vim swap files
        assert handler.should_index_file("main.py.swp") is False
        assert handler.should_index_file("config.json.swo") is False

    def test_should_exclude_claude_directory(
        self, file_filter_config, language_detector, file_categorizer
    ):
        """Test that .claude directory is excluded."""
        handler = FileHandler(file_filter_config, language_detector, file_categorizer)

        assert handler.should_index_file(".claude/config.json") is False
        assert handler.should_index_file("project/.claude/memory.md") is False

    def test_should_exclude_storage_directory(
        self, file_filter_config, language_detector, file_categorizer
    ):
        """Test that storage/ directory is excluded (prevents indexing the index)."""
        handler = FileHandler(file_filter_config, language_detector, file_categorizer)

        assert handler.should_index_file("storage/index.json") is False
        assert handler.should_index_file("project/storage/vectors.bin") is False

    def test_should_exclude_os_files(
        self, file_filter_config, language_detector, file_categorizer
    ):
        """Test that OS-specific files are excluded."""
        handler = FileHandler(file_filter_config, language_detector, file_categorizer)

        # macOS
        assert handler.should_index_file(".DS_Store") is False
        assert handler.should_index_file("folder/.DS_Store") is False

        # Windows
        assert handler.should_index_file("Thumbs.db") is False
        assert handler.should_index_file("images/Thumbs.db") is False

    def test_should_exclude_python_egg_info(
        self, file_filter_config, language_detector, file_categorizer
    ):
        """Test that Python .egg-info directories are excluded."""
        handler = FileHandler(file_filter_config, language_detector, file_categorizer)

        assert handler.should_index_file("mypackage.egg-info/PKG-INFO") is False
        assert handler.should_index_file("dist/mylib.egg-info/SOURCES.txt") is False

    def test_matches_pattern_with_wildcards(
        self, file_filter_config, language_detector, file_categorizer
    ):
        """Test pattern matching with glob wildcards."""
        handler = FileHandler(file_filter_config, language_detector, file_categorizer)

        assert handler._matches_pattern("test.pyc", "*.pyc") is True
        assert handler._matches_pattern("src/test.pyc", "*.pyc") is True
        assert handler._matches_pattern("test.py", "*.pyc") is False
        assert handler._matches_pattern("file.test.js", "*test*") is True

    def test_matches_pattern_with_substring(
        self, file_filter_config, language_detector, file_categorizer
    ):
        """Test pattern matching with substring (no wildcards)."""
        handler = FileHandler(file_filter_config, language_detector, file_categorizer)

        assert handler._matches_pattern("path/node_modules/file.js", "node_modules") is True
        assert handler._matches_pattern("path/src/file.js", "node_modules") is False
        assert handler._matches_pattern("__pycache__/module.pyc", "__pycache__") is True

    def test_get_file_metadata_python_file(
        self, file_filter_config, language_detector, file_categorizer
    ):
        """Test metadata extraction for Python files."""
        handler = FileHandler(file_filter_config, language_detector, file_categorizer)
        metadata = handler.get_file_metadata("src/main.py")

        assert "file_path" in metadata
        assert metadata["file_name"] == "main.py"
        assert metadata["file_extension"] == ".py"
        assert metadata["language"] == "python"
        assert metadata["category"] == "code"

    def test_get_file_metadata_documentation_file(
        self, file_filter_config, language_detector, file_categorizer
    ):
        """Test metadata extraction for documentation files."""
        handler = FileHandler(file_filter_config, language_detector, file_categorizer)
        metadata = handler.get_file_metadata("docs/README.md")

        assert metadata["file_name"] == "README.md"
        assert metadata["file_extension"] == ".md"
        assert metadata["language"] == "unknown"  # .md not in default language mappings
        assert metadata["category"] == "documentation"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
