"""Configuration module for document indexer.

This module provides focused configuration classes following SOLID principles:
- Each config class has a single responsibility (SRP)
- Clients only depend on what they need (ISP)
- All configs are immutable frozen dataclasses (DIP)
"""

from dotenv import load_dotenv

from .chunking_config import ChunkingConfig
from .extraction_config import ExtractionConfig
from .embedding_config import EmbeddingConfig
from .query_config import QueryConfig
from .file_filter_config import FileFilterConfig
from .env_parser import EnvParser
from .language_detector import LanguageDetector
from .file_categorizer import FileCategorizer
from .indexer_config import IndexerConfig  # Legacy bridge - Phase 4 migration target

# Load environment variables once at module import
load_dotenv()

__all__ = [
    "ChunkingConfig",
    "ExtractionConfig",
    "EmbeddingConfig",
    "QueryConfig",
    "FileFilterConfig",
    "EnvParser",
    "LanguageDetector",
    "FileCategorizer",
    "IndexerConfig",  # Legacy bridge - Phase 4 migration target
]
