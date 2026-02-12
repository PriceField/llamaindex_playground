"""Tests for IndexerConfig backward-compatibility bridge.

This test file ensures the legacy IndexerConfig class maintains exact
backward compatibility with the old interface while delegating to the
new focused config classes.
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import IndexerConfig
from config.chunking_config import ChunkingConfig
from config.extraction_config import ExtractionConfig
from config.embedding_config import EmbeddingConfig
from config.query_config import QueryConfig
from config.file_filter_config import FileFilterConfig
from file_handlers import FileHandler


# ==============================================================================
# Category 1: Construction Tests (3 tests)
# ==============================================================================

def test_indexer_config_zero_argument_constructor():
    """Test IndexerConfig can be constructed with no arguments."""
    config = IndexerConfig()
    assert config is not None
    assert hasattr(config, '_chunking')
    assert hasattr(config, '_extraction')
    assert hasattr(config, '_embedding')
    assert hasattr(config, '_query')
    assert hasattr(config, '_file_filter')
    assert hasattr(config, '_language_detector')
    assert hasattr(config, '_file_categorizer')


def test_indexer_config_internal_configs_initialized():
    """Test all internal config objects are properly initialized."""
    config = IndexerConfig()
    assert isinstance(config._chunking, ChunkingConfig)
    assert isinstance(config._extraction, ExtractionConfig)
    assert isinstance(config._embedding, EmbeddingConfig)
    assert isinstance(config._query, QueryConfig)
    assert isinstance(config._file_filter, FileFilterConfig)


def test_indexer_config_no_exceptions_on_valid_environment():
    """Test construction succeeds with valid environment variables."""
    # Should not raise any exceptions
    config = IndexerConfig()
    assert config.code_chunk_size > 0
    assert config.code_similarity_top_k > 0


# ==============================================================================
# Category 2: Property Delegation Tests (22 tests)
# ==============================================================================

# Chunking Properties (6 tests)

def test_code_chunk_size_delegates_to_chunking():
    """Test code_chunk_size property delegates to ChunkingConfig."""
    config = IndexerConfig()
    assert config.code_chunk_size == config._chunking.code_chunk_size


def test_code_chunk_overlap_delegates_to_chunking():
    """Test code_chunk_overlap property delegates to ChunkingConfig."""
    config = IndexerConfig()
    assert config.code_chunk_overlap == config._chunking.code_chunk_overlap


def test_doc_chunk_size_delegates_to_chunking():
    """Test doc_chunk_size property delegates to ChunkingConfig."""
    config = IndexerConfig()
    assert config.doc_chunk_size == config._chunking.doc_chunk_size


def test_doc_chunk_overlap_delegates_to_chunking():
    """Test doc_chunk_overlap property delegates to ChunkingConfig."""
    config = IndexerConfig()
    assert config.doc_chunk_overlap == config._chunking.doc_chunk_overlap


def test_preserve_code_structure_delegates_to_chunking():
    """Test preserve_code_structure property delegates to ChunkingConfig."""
    config = IndexerConfig()
    assert config.preserve_code_structure == config._chunking.preserve_code_structure


def test_include_line_numbers_delegates_to_chunking_not_extraction():
    """Test include_line_numbers delegates to ChunkingConfig (not ExtractionConfig).

    This is critical: include_line_numbers exists in both ChunkingConfig and
    ExtractionConfig. We must delegate to ChunkingConfig as it's the primary
    consumer (used by CodeAwareNodeParser).
    """
    config = IndexerConfig()
    assert config.include_line_numbers == config._chunking.include_line_numbers
    # Verify it's NOT using ExtractionConfig (they should be the same, but verify delegation)
    assert config.include_line_numbers is config._chunking.include_line_numbers


# Extraction Properties (3 tests)

def test_extract_functions_delegates_to_extraction():
    """Test extract_functions property delegates to ExtractionConfig."""
    config = IndexerConfig()
    assert config.extract_functions == config._extraction.extract_functions


def test_extract_classes_delegates_to_extraction():
    """Test extract_classes property delegates to ExtractionConfig."""
    config = IndexerConfig()
    assert config.extract_classes == config._extraction.extract_classes


def test_extract_imports_delegates_to_extraction():
    """Test extract_imports property delegates to ExtractionConfig."""
    config = IndexerConfig()
    assert config.extract_imports == config._extraction.extract_imports


# Embedding Properties (5 tests)

def test_embed_model_type_delegates_to_embedding():
    """Test embed_model_type property delegates to EmbeddingConfig."""
    config = IndexerConfig()
    assert config.embed_model_type == config._embedding.embed_model_type


def test_embed_model_name_delegates_to_embedding():
    """Test embed_model_name property delegates to EmbeddingConfig."""
    config = IndexerConfig()
    assert config.embed_model_name == config._embedding.embed_model_name


def test_embed_api_key_delegates_to_embedding():
    """Test embed_api_key property delegates to EmbeddingConfig."""
    config = IndexerConfig()
    assert config.embed_api_key == config._embedding.embed_api_key


def test_embed_api_base_delegates_to_embedding():
    """Test embed_api_base property delegates to EmbeddingConfig."""
    config = IndexerConfig()
    assert config.embed_api_base == config._embedding.embed_api_base


def test_embed_openai_model_delegates_to_embedding():
    """Test embed_openai_model property delegates to EmbeddingConfig."""
    config = IndexerConfig()
    assert config.embed_openai_model == config._embedding.embed_openai_model


# Query Properties (3 tests)

def test_code_similarity_top_k_delegates_to_query():
    """Test code_similarity_top_k property delegates to QueryConfig."""
    config = IndexerConfig()
    assert config.code_similarity_top_k == config._query.code_similarity_top_k


def test_use_metadata_filters_delegates_to_query():
    """Test use_metadata_filters property delegates to QueryConfig."""
    config = IndexerConfig()
    assert config.use_metadata_filters == config._query.use_metadata_filters


def test_include_source_context_delegates_to_query():
    """Test include_source_context property delegates to QueryConfig."""
    config = IndexerConfig()
    assert config.include_source_context == config._query.include_source_context


# File Filter Properties (2 tests)

def test_supported_languages_delegates_to_file_filter():
    """Test supported_languages property delegates to FileFilterConfig."""
    config = IndexerConfig()
    assert config.supported_languages == config._file_filter.supported_languages


def test_default_exclude_patterns_delegates_to_file_filter():
    """Test default_exclude_patterns property delegates to FileFilterConfig."""
    config = IndexerConfig()
    assert config.default_exclude_patterns == config._file_filter.default_exclude_patterns


# Internal Data Structures (3 tests - language_extensions, file_categories tested separately)

def test_language_extensions_returns_dict():
    """Test language_extensions property returns correct dict structure."""
    config = IndexerConfig()
    assert isinstance(config.language_extensions, dict)
    assert 'python' in config.language_extensions
    assert '.py' in config.language_extensions['python']


def test_file_categories_returns_dict():
    """Test file_categories property returns correct dict structure."""
    config = IndexerConfig()
    assert isinstance(config.file_categories, dict)
    assert 'documentation' in config.file_categories
    assert '.md' in config.file_categories['documentation']


# ==============================================================================
# Category 3: Method Delegation Tests (2 tests)
# ==============================================================================

def test_detect_language_delegates_to_language_detector():
    """Test detect_language() method delegates to LanguageDetector.detect()."""
    config = IndexerConfig()

    # Test with known file extensions
    assert config.detect_language("test.py") == "python"
    assert config.detect_language("test.js") == "javascript"
    assert config.detect_language("test.go") == "go"
    assert config.detect_language("test.unknown") == "unknown"


def test_detect_category_delegates_to_file_categorizer():
    """Test detect_category() method delegates to FileCategorizer.categorize()."""
    config = IndexerConfig()

    # Test with known file extensions
    assert config.detect_category("README.md") == "documentation"
    assert config.detect_category("config.json") == "configuration"
    assert config.detect_category("test.py") == "code"
    assert config.detect_category("unknown.xyz") == "other"


# ==============================================================================
# Category 4: Backward Compatibility Tests (5 tests)
# ==============================================================================

def test_works_with_code_metadata_extractor():
    """Test IndexerConfig works with CodeMetadataExtractor (code_extractors.py usage)."""
    from code_extractors import CodeMetadataExtractor

    config = IndexerConfig()
    extractor = CodeMetadataExtractor(config=config)

    assert extractor is not None
    # CodeMetadataExtractor should be able to access extraction flags
    assert hasattr(extractor, 'config')


def test_create_file_handler_returns_correct_instance():
    """Test create_file_handler() helper method returns FileHandler instance."""
    config = IndexerConfig()
    file_handler = config.create_file_handler()

    assert isinstance(file_handler, FileHandler)
    assert file_handler.file_filter_config is config._file_filter
    assert file_handler.language_detector is config._language_detector
    assert file_handler.file_categorizer is config._file_categorizer


def test_language_extensions_property_backward_compatible():
    """Test language_extensions property maintains backward compatible structure."""
    config = IndexerConfig()
    extensions = config.language_extensions

    # Old code expected this structure
    assert isinstance(extensions, dict)
    assert all(isinstance(k, str) for k in extensions.keys())
    assert all(isinstance(v, list) for v in extensions.values())
    assert all(
        all(isinstance(ext, str) for ext in v)
        for v in extensions.values()
    )


def test_file_categories_property_backward_compatible():
    """Test file_categories property maintains backward compatible structure."""
    config = IndexerConfig()
    categories = config.file_categories

    # Old code expected this structure
    assert isinstance(categories, dict)
    assert all(isinstance(k, str) for k in categories.keys())
    assert all(isinstance(v, list) for v in categories.values())
    assert all(
        all(isinstance(ext, str) for ext in v)
        for v in categories.values()
    )


def test_all_expected_properties_exist():
    """Test all 22 properties from old IndexerConfig exist and are accessible."""
    config = IndexerConfig()

    # Chunking properties (6)
    assert hasattr(config, 'code_chunk_size')
    assert hasattr(config, 'code_chunk_overlap')
    assert hasattr(config, 'doc_chunk_size')
    assert hasattr(config, 'doc_chunk_overlap')
    assert hasattr(config, 'preserve_code_structure')
    assert hasattr(config, 'include_line_numbers')

    # Extraction properties (3)
    assert hasattr(config, 'extract_functions')
    assert hasattr(config, 'extract_classes')
    assert hasattr(config, 'extract_imports')

    # Embedding properties (5)
    assert hasattr(config, 'embed_model_type')
    assert hasattr(config, 'embed_model_name')
    assert hasattr(config, 'embed_api_key')
    assert hasattr(config, 'embed_api_base')
    assert hasattr(config, 'embed_openai_model')

    # Query properties (3)
    assert hasattr(config, 'code_similarity_top_k')
    assert hasattr(config, 'use_metadata_filters')
    assert hasattr(config, 'include_source_context')

    # File filter properties (2)
    assert hasattr(config, 'supported_languages')
    assert hasattr(config, 'default_exclude_patterns')

    # Internal data structures (2)
    assert hasattr(config, 'language_extensions')
    assert hasattr(config, 'file_categories')

    # Methods (2)
    assert hasattr(config, 'detect_language')
    assert hasattr(config, 'detect_category')

    # Helper method (1)
    assert hasattr(config, 'create_file_handler')


# ==============================================================================
# Category 5: Integration Tests (2 tests)
# ==============================================================================

def test_full_workflow_with_indexer_config():
    """Test full workflow: construct, access properties, call methods, create components."""
    # Step 1: Construct
    config = IndexerConfig()

    # Step 2: Access various properties
    chunk_size = config.code_chunk_size
    extract_fns = config.extract_functions
    top_k = config.code_similarity_top_k
    languages = config.supported_languages

    assert chunk_size > 0
    assert isinstance(extract_fns, bool)
    assert top_k > 0
    assert isinstance(languages, list)

    # Step 3: Call methods
    lang = config.detect_language("test.py")
    category = config.detect_category("README.md")

    assert lang == "python"
    assert category == "documentation"

    # Step 4: Create components
    file_handler = config.create_file_handler()

    assert isinstance(file_handler, FileHandler)


def test_no_regressions_in_property_values():
    """Test that property values match expected defaults from environment."""
    config = IndexerConfig()

    # These values should match the defaults in EnvParser
    assert config.code_chunk_size == 512
    assert config.code_chunk_overlap == 50
    assert config.doc_chunk_size == 1024
    assert config.doc_chunk_overlap == 20
    assert config.preserve_code_structure is True
    assert config.include_line_numbers is True
    assert config.extract_functions is True
    assert config.extract_classes is True
    assert config.extract_imports is True
    assert config.code_similarity_top_k == 5
    assert config.use_metadata_filters is True
    assert config.include_source_context is True
    assert config.embed_model_type == "local"
    # Note: Default embed_model_name in code is "BAAI/bge-large-en-v1.5"
    # but .env.example may have different value
    assert isinstance(config.embed_model_name, str) and len(config.embed_model_name) > 0

    # Verify supported_languages and exclude_patterns are not empty
    assert len(config.supported_languages) > 0
    assert "python" in config.supported_languages
    assert len(config.default_exclude_patterns) > 0
    assert "node_modules" in config.default_exclude_patterns
