"""Unit tests for ExtractionConfig."""
import os
import pytest
from unittest.mock import patch

from config import ExtractionConfig


class TestExtractionConfig:
    """Test suite for ExtractionConfig class."""

    @patch.dict(os.environ, {"EXTRACT_FUNCTIONS": "true"}, clear=True)
    def test_from_env_with_functions_enabled(self):
        """Test ExtractionConfig.from_env() with EXTRACT_FUNCTIONS=true."""
        config = ExtractionConfig.from_env()
        assert config.extract_functions is True

    @patch.dict(os.environ, {"EXTRACT_FUNCTIONS": "false"}, clear=True)
    def test_from_env_with_functions_disabled(self):
        """Test ExtractionConfig.from_env() with EXTRACT_FUNCTIONS=false."""
        config = ExtractionConfig.from_env()
        assert config.extract_functions is False

    @patch.dict(os.environ, {"EXTRACT_CLASSES": "true"}, clear=True)
    def test_from_env_with_classes_enabled(self):
        """Test ExtractionConfig.from_env() with EXTRACT_CLASSES=true."""
        config = ExtractionConfig.from_env()
        assert config.extract_classes is True

    @patch.dict(os.environ, {"EXTRACT_CLASSES": "false"}, clear=True)
    def test_from_env_with_classes_disabled(self):
        """Test ExtractionConfig.from_env() with EXTRACT_CLASSES=false."""
        config = ExtractionConfig.from_env()
        assert config.extract_classes is False

    @patch.dict(os.environ, {"EXTRACT_IMPORTS": "true"}, clear=True)
    def test_from_env_with_imports_enabled(self):
        """Test ExtractionConfig.from_env() with EXTRACT_IMPORTS=true."""
        config = ExtractionConfig.from_env()
        assert config.extract_imports is True

    @patch.dict(os.environ, {"EXTRACT_IMPORTS": "false"}, clear=True)
    def test_from_env_with_imports_disabled(self):
        """Test ExtractionConfig.from_env() with EXTRACT_IMPORTS=false."""
        config = ExtractionConfig.from_env()
        assert config.extract_imports is False

    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_with_defaults(self):
        """Test ExtractionConfig.from_env() uses defaults when env vars not set."""
        config = ExtractionConfig.from_env()
        assert config.extract_functions is True
        assert config.extract_classes is True
        assert config.extract_imports is True

    def test_default_factory_method(self):
        """Test ExtractionConfig.default() factory method."""
        config = ExtractionConfig.default()
        assert config.extract_functions is True
        assert config.extract_classes is True
        assert config.extract_imports is True

    def test_config_is_frozen(self):
        """Test that ExtractionConfig instances are immutable."""
        config = ExtractionConfig.default()
        with pytest.raises(Exception):  # Frozen dataclass raises FrozenInstanceError
            config.extract_functions = False

    def test_all_extraction_disabled(self):
        """Test creating config with all extraction disabled."""
        config = ExtractionConfig(
            extract_functions=False,
            extract_classes=False,
            extract_imports=False,
            include_line_numbers=False,
        )
        assert config.extract_functions is False
        assert config.extract_classes is False
        assert config.extract_imports is False
        assert config.include_line_numbers is False

    @patch.dict(
        os.environ,
        {
            "EXTRACT_FUNCTIONS": "false # disable",
            "EXTRACT_CLASSES": "true # enable",
            "EXTRACT_IMPORTS": "false",
        },
        clear=True,
    )
    def test_from_env_strips_inline_comments(self):
        """Test that from_env() strips inline comments from values."""
        config = ExtractionConfig.from_env()
        assert config.extract_functions is False
        assert config.extract_classes is True
        assert config.extract_imports is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
