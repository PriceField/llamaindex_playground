"""Metadata extraction strategies."""
from .base import LanguageMetadataExtractor
from .python_extractor import PythonMetadataExtractor
from .javascript_extractor import JavaScriptMetadataExtractor
from .java_extractor import JavaMetadataExtractor
from .go_extractor import GoMetadataExtractor
from .registry import MetadataExtractorRegistry

__all__ = [
    "LanguageMetadataExtractor",
    "PythonMetadataExtractor",
    "JavaScriptMetadataExtractor",
    "JavaMetadataExtractor",
    "GoMetadataExtractor",
    "MetadataExtractorRegistry",
]
