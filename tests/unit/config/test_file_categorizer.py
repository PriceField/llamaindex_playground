"""Unit tests for FileCategorizer utility."""
import pytest

from config import FileCategorizer


class TestFileCategorizer:
    """Test suite for FileCategorizer class."""

    def test_categorize_code_files(self):
        """Test category detection for code files."""
        categorizer = FileCategorizer()
        assert categorizer.categorize("test.py") == "code"
        assert categorizer.categorize("app.js") == "code"
        assert categorizer.categorize("Main.java") == "code"
        assert categorizer.categorize("main.rs") == "code"
        assert categorizer.categorize("script.ts") == "code"
        assert categorizer.categorize("main.go") == "code"

    def test_categorize_documentation_files(self):
        """Test category detection for documentation files."""
        categorizer = FileCategorizer()
        assert categorizer.categorize("README.md") == "documentation"
        assert categorizer.categorize("guide.rst") == "documentation"
        assert categorizer.categorize("notes.txt") == "documentation"
        assert categorizer.categorize("CHANGELOG.md") == "documentation"
        assert categorizer.categorize("docs.adoc") == "documentation"

    def test_categorize_configuration_files(self):
        """Test category detection for configuration files."""
        categorizer = FileCategorizer()
        assert categorizer.categorize("package.json") == "configuration"
        assert categorizer.categorize("config.yaml") == "configuration"
        assert categorizer.categorize("settings.toml") == "configuration"
        assert categorizer.categorize("app.yml") == "configuration"
        assert categorizer.categorize("setup.cfg") == "configuration"

    def test_categorize_unknown_file(self):
        """Test category detection for unknown file types."""
        categorizer = FileCategorizer()
        assert categorizer.categorize("file.xyz") == "other"
        assert categorizer.categorize("unknown") == "other"
        assert categorizer.categorize("data.bin") == "other"

    def test_categorize_case_insensitive(self):
        """Test that categorization is case-insensitive."""
        categorizer = FileCategorizer()
        assert categorizer.categorize("TEST.PY") == "code"
        assert categorizer.categorize("README.MD") == "documentation"
        assert categorizer.categorize("CONFIG.YAML") == "configuration"

    def test_categorize_with_full_path(self):
        """Test categorization works with full file paths."""
        categorizer = FileCategorizer()
        assert categorizer.categorize("/path/to/script.py") == "code"
        assert categorizer.categorize("C:\\Users\\test\\README.md") == "documentation"
        assert categorizer.categorize("../relative/config.json") == "configuration"

    def test_custom_categories(self):
        """Test categorizer with custom categories."""
        custom_categories = {
            "test": [".test", ".spec"],
            "data": [".csv", ".json"],
        }
        categorizer = FileCategorizer(category_extensions=custom_categories)
        assert categorizer.categorize("file.test") == "test"
        assert categorizer.categorize("data.spec") == "test"
        assert categorizer.categorize("users.csv") == "data"
        assert categorizer.categorize("config.json") == "data"
        # Should still support default categories
        assert categorizer.categorize("script.py") == "code"

    def test_custom_category_overrides_default(self):
        """Test that custom categories can override default ones."""
        custom_categories = {
            "custom_code": [".py", ".js"],  # Override default code category
        }
        categorizer = FileCategorizer(category_extensions=custom_categories)
        assert categorizer.categorize("script.py") == "custom_code"
        assert categorizer.categorize("app.js") == "custom_code"
        # Other code files should still be in default code category
        assert categorizer.categorize("Main.java") == "code"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
