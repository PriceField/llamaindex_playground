"""Unit tests for EnvParser utility."""
import os
import pytest
from unittest.mock import patch

from config import EnvParser


class TestParseInt:
    """Test suite for EnvParser.parse_int()."""

    @patch.dict(os.environ, {"TEST_INT": "256"}, clear=True)
    def test_parse_int_with_valid_value(self):
        """Test parsing integer from environment variable."""
        result = EnvParser.parse_int("TEST_INT", default=512)
        assert result == 256

    @patch.dict(os.environ, {"TEST_INT": "512 # default chunk size"}, clear=True)
    def test_parse_int_with_inline_comment(self):
        """Test parsing integer with inline comment stripped."""
        result = EnvParser.parse_int("TEST_INT", default=256)
        assert result == 512

    @patch.dict(os.environ, {"TEST_INT": "invalid_number"}, clear=True)
    def test_parse_int_with_invalid_value_returns_default(self):
        """Test that invalid integer values return default."""
        result = EnvParser.parse_int("TEST_INT", default=512)
        assert result == 512

    @patch.dict(os.environ, {}, clear=True)
    def test_parse_int_with_missing_var_returns_default(self):
        """Test that missing environment variable returns default."""
        result = EnvParser.parse_int("MISSING_VAR", default=1024)
        assert result == 1024

    @patch.dict(os.environ, {"TEST_INT": "0"}, clear=True)
    def test_parse_int_with_zero(self):
        """Test parsing zero value."""
        result = EnvParser.parse_int("TEST_INT", default=512)
        assert result == 0

    @patch.dict(os.environ, {"TEST_INT": "-100"}, clear=True)
    def test_parse_int_with_negative_value(self):
        """Test parsing negative integer."""
        result = EnvParser.parse_int("TEST_INT", default=512)
        assert result == -100


class TestParseBool:
    """Test suite for EnvParser.parse_bool()."""

    @patch.dict(os.environ, {"TEST_BOOL": "true"}, clear=True)
    def test_parse_bool_with_true_value(self):
        """Test parsing boolean true value."""
        result = EnvParser.parse_bool("TEST_BOOL", default=False)
        assert result is True

    @patch.dict(os.environ, {"TEST_BOOL": "false # disable extraction"}, clear=True)
    def test_parse_bool_with_inline_comment(self):
        """Test parsing boolean with inline comment stripped."""
        result = EnvParser.parse_bool("TEST_BOOL", default=True)
        assert result is False

    @patch.dict(os.environ, {"TEST_BOOL": "TRUE"}, clear=True)
    def test_parse_bool_with_uppercase_true(self):
        """Test parsing uppercase TRUE."""
        result = EnvParser.parse_bool("TEST_BOOL", default=False)
        assert result is True

    @patch.dict(os.environ, {"TEST_BOOL": "False"}, clear=True)
    def test_parse_bool_with_capitalized_false(self):
        """Test parsing capitalized False."""
        result = EnvParser.parse_bool("TEST_BOOL", default=True)
        assert result is False

    @patch.dict(os.environ, {"TEST_BOOL": "1"}, clear=True)
    def test_parse_bool_with_numeric_true(self):
        """Test parsing numeric 1 as true."""
        result = EnvParser.parse_bool("TEST_BOOL", default=False)
        assert result is True

    @patch.dict(os.environ, {"TEST_BOOL": "0"}, clear=True)
    def test_parse_bool_with_numeric_false(self):
        """Test parsing numeric 0 as false."""
        result = EnvParser.parse_bool("TEST_BOOL", default=True)
        assert result is False

    @patch.dict(os.environ, {"TEST_BOOL": "invalid"}, clear=True)
    def test_parse_bool_with_invalid_value_returns_default(self):
        """Test that invalid boolean values return default."""
        result = EnvParser.parse_bool("TEST_BOOL", default=True)
        assert result is True

    @patch.dict(os.environ, {}, clear=True)
    def test_parse_bool_with_missing_var_returns_default(self):
        """Test that missing environment variable returns default."""
        result = EnvParser.parse_bool("MISSING_VAR", default=False)
        assert result is False


class TestParseList:
    """Test suite for EnvParser.parse_list()."""

    @patch.dict(os.environ, {"TEST_LIST": "python,javascript # main languages"}, clear=True)
    def test_parse_list_with_inline_comment(self):
        """Test parsing comma-separated list with inline comment."""
        result = EnvParser.parse_list("TEST_LIST", default=[])
        assert "python" in result
        assert "javascript" in result
        assert len(result) == 2

    @patch.dict(os.environ, {"TEST_LIST": "python, javascript, typescript"}, clear=True)
    def test_parse_list_with_spaces(self):
        """Test parsing list with spaces around commas."""
        result = EnvParser.parse_list("TEST_LIST", default=[])
        assert result == ["python", "javascript", "typescript"]

    @patch.dict(os.environ, {"TEST_LIST": "single_item"}, clear=True)
    def test_parse_list_with_single_item(self):
        """Test parsing list with single item (no commas)."""
        result = EnvParser.parse_list("TEST_LIST", default=[])
        assert result == ["single_item"]

    @patch.dict(os.environ, {"TEST_LIST": ""}, clear=True)
    def test_parse_list_with_empty_string(self):
        """Test parsing empty string."""
        result = EnvParser.parse_list("TEST_LIST", default=["default"])
        assert result == ["default"]

    @patch.dict(os.environ, {}, clear=True)
    def test_parse_list_with_missing_var_returns_default(self):
        """Test that missing environment variable returns default."""
        result = EnvParser.parse_list("MISSING_VAR", default=["a", "b"])
        assert result == ["a", "b"]

    @patch.dict(os.environ, {"TEST_LIST": "a,b,,c"}, clear=True)
    def test_parse_list_filters_empty_strings(self):
        """Test that empty strings from consecutive commas are filtered."""
        result = EnvParser.parse_list("TEST_LIST", default=[])
        assert result == ["a", "b", "c"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
