"""Unit tests for ChunkingConfig."""
import os
import pytest
from unittest.mock import patch

from config import ChunkingConfig


class TestChunkingConfig:
    """Test suite for ChunkingConfig class."""

    @patch.dict(os.environ, {"CODE_CHUNK_SIZE": "256"}, clear=True)
    def test_from_env_with_custom_code_chunk_size(self):
        """Test ChunkingConfig.from_env() with custom CODE_CHUNK_SIZE."""
        config = ChunkingConfig.from_env()
        assert config.code_chunk_size == 256

    @patch.dict(os.environ, {"CODE_CHUNK_OVERLAP": "100"}, clear=True)
    def test_from_env_with_custom_code_chunk_overlap(self):
        """Test ChunkingConfig.from_env() with custom CODE_CHUNK_OVERLAP."""
        config = ChunkingConfig.from_env()
        assert config.code_chunk_overlap == 100

    @patch.dict(os.environ, {"DOC_CHUNK_SIZE": "2048"}, clear=True)
    def test_from_env_with_custom_doc_chunk_size(self):
        """Test ChunkingConfig.from_env() with custom DOC_CHUNK_SIZE."""
        config = ChunkingConfig.from_env()
        assert config.doc_chunk_size == 2048

    @patch.dict(os.environ, {"DOC_CHUNK_OVERLAP": "200"}, clear=True)
    def test_from_env_with_custom_doc_chunk_overlap(self):
        """Test ChunkingConfig.from_env() with custom DOC_CHUNK_OVERLAP."""
        config = ChunkingConfig.from_env()
        assert config.doc_chunk_overlap == 200

    @patch.dict(os.environ, {"INCLUDE_LINE_NUMBERS": "false"}, clear=True)
    def test_from_env_with_line_numbers_disabled(self):
        """Test ChunkingConfig.from_env() with INCLUDE_LINE_NUMBERS=false."""
        config = ChunkingConfig.from_env()
        assert config.include_line_numbers is False

    @patch.dict(os.environ, {"PRESERVE_CODE_STRUCTURE": "false"}, clear=True)
    def test_from_env_with_structure_preservation_disabled(self):
        """Test ChunkingConfig.from_env() with PRESERVE_CODE_STRUCTURE=false."""
        config = ChunkingConfig.from_env()
        assert config.preserve_code_structure is False

    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_with_defaults(self):
        """Test ChunkingConfig.from_env() uses defaults when env vars not set."""
        config = ChunkingConfig.from_env()
        assert config.code_chunk_size == 512
        assert config.code_chunk_overlap == 50
        assert config.doc_chunk_size == 1024
        assert config.doc_chunk_overlap == 20
        assert config.include_line_numbers is True
        assert config.preserve_code_structure is True

    def test_default_factory_method(self):
        """Test ChunkingConfig.default() factory method."""
        config = ChunkingConfig.default()
        assert config.code_chunk_size == 512
        assert config.code_chunk_overlap == 50
        assert config.doc_chunk_size == 1024
        assert config.doc_chunk_overlap == 20
        assert config.include_line_numbers is True
        assert config.preserve_code_structure is True

    def test_config_is_frozen(self):
        """Test that ChunkingConfig instances are immutable."""
        config = ChunkingConfig.default()
        with pytest.raises(Exception):  # Frozen dataclass raises FrozenInstanceError
            config.code_chunk_size = 1024

    def test_validation_code_chunk_size_positive(self):
        """Test that code_chunk_size must be positive."""
        with pytest.raises(ValueError, match="code_chunk_size must be >= 1"):
            ChunkingConfig(
                code_chunk_size=0,
                code_chunk_overlap=50,
                doc_chunk_size=1024,
                doc_chunk_overlap=20,
                preserve_code_structure=True,
                include_line_numbers=True,
            )

    def test_validation_code_chunk_overlap_non_negative(self):
        """Test that code_chunk_overlap must be non-negative."""
        with pytest.raises(ValueError, match="code_chunk_overlap must be >= 0"):
            ChunkingConfig(
                code_chunk_size=512,
                code_chunk_overlap=-10,
                doc_chunk_size=1024,
                doc_chunk_overlap=20,
                preserve_code_structure=True,
                include_line_numbers=True,
            )

    def test_validation_doc_chunk_size_positive(self):
        """Test that doc_chunk_size must be positive."""
        with pytest.raises(ValueError, match="doc_chunk_size must be >= 1"):
            ChunkingConfig(
                code_chunk_size=512,
                code_chunk_overlap=50,
                doc_chunk_size=-100,
                doc_chunk_overlap=20,
                preserve_code_structure=True,
                include_line_numbers=True,
            )

    def test_validation_doc_chunk_overlap_non_negative(self):
        """Test that doc_chunk_overlap must be non-negative."""
        with pytest.raises(ValueError, match="doc_chunk_overlap must be >= 0"):
            ChunkingConfig(
                code_chunk_size=512,
                code_chunk_overlap=50,
                doc_chunk_size=1024,
                doc_chunk_overlap=-5,
                preserve_code_structure=True,
                include_line_numbers=True,
            )

    @patch.dict(os.environ, {"CODE_CHUNK_SIZE": "512 # default size"}, clear=True)
    def test_from_env_strips_inline_comments(self):
        """Test that from_env() strips inline comments from values."""
        config = ChunkingConfig.from_env()
        assert config.code_chunk_size == 512


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
