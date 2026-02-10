"""Unit tests for LanguageDetector utility."""
import pytest

from config import LanguageDetector


class TestLanguageDetector:
    """Test suite for LanguageDetector class."""

    def test_detect_python_extension(self):
        """Test language detection for Python files."""
        detector = LanguageDetector()
        assert detector.detect("test.py") == "python"
        assert detector.detect("script.pyw") == "python"

    def test_detect_javascript_extension(self):
        """Test language detection for JavaScript files."""
        detector = LanguageDetector()
        assert detector.detect("app.js") == "javascript"
        assert detector.detect("App.jsx") == "javascript"
        assert detector.detect("module.mjs") == "javascript"
        assert detector.detect("config.cjs") == "javascript"

    def test_detect_typescript_extension(self):
        """Test language detection for TypeScript files."""
        detector = LanguageDetector()
        assert detector.detect("script.ts") == "typescript"
        assert detector.detect("Component.tsx") == "typescript"

    def test_detect_java_extension(self):
        """Test language detection for Java files."""
        detector = LanguageDetector()
        assert detector.detect("Main.java") == "java"
        assert detector.detect("Controller.java") == "java"

    def test_detect_go_extension(self):
        """Test language detection for Go files."""
        detector = LanguageDetector()
        assert detector.detect("main.go") == "go"
        assert detector.detect("server.go") == "go"

    def test_detect_rust_extension(self):
        """Test language detection for Rust files."""
        detector = LanguageDetector()
        assert detector.detect("main.rs") == "rust"
        assert detector.detect("lib.rs") == "rust"

    def test_detect_cpp_extension(self):
        """Test language detection for C++ files."""
        detector = LanguageDetector()
        assert detector.detect("main.cpp") == "cpp"
        assert detector.detect("header.hpp") == "cpp"
        assert detector.detect("code.cc") == "cpp"

    def test_detect_c_extension(self):
        """Test language detection for C files."""
        detector = LanguageDetector()
        assert detector.detect("main.c") == "c"
        assert detector.detect("header.h") == "c"

    def test_detect_unknown_extension(self):
        """Test language detection for unknown file extensions."""
        detector = LanguageDetector()
        assert detector.detect("file.xyz") == "unknown"
        assert detector.detect("README") == "unknown"
        assert detector.detect("data.bin") == "unknown"

    def test_detect_case_insensitive(self):
        """Test that detection is case-insensitive."""
        detector = LanguageDetector()
        assert detector.detect("TEST.PY") == "python"
        assert detector.detect("App.JS") == "javascript"
        assert detector.detect("Main.JAVA") == "java"

    def test_detect_with_full_path(self):
        """Test detection works with full file paths."""
        detector = LanguageDetector()
        assert detector.detect("/path/to/script.py") == "python"
        assert detector.detect("C:\\Users\\test\\app.js") == "javascript"
        assert detector.detect("../relative/path/main.go") == "go"

    def test_custom_language_mapping(self):
        """Test detector with custom language mappings."""
        custom_mappings = {
            "custom_lang": [".custom"],
            "special_lang": [".special"],
        }
        detector = LanguageDetector(custom_mappings)
        assert detector.detect("file.custom") == "custom_lang"
        assert detector.detect("test.special") == "special_lang"
        # Should still support default mappings
        assert detector.detect("script.py") == "python"

    def test_custom_mapping_overrides_default(self):
        """Test that custom mappings can override default ones."""
        custom_mappings = {
            "python3": [".py"],  # Override default python
        }
        detector = LanguageDetector(custom_mappings)
        assert detector.detect("script.py") == "python3"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
