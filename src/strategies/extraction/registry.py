"""Registry for metadata extraction strategies."""
from typing import Optional
from .base import LanguageMetadataExtractor
from .python_extractor import PythonMetadataExtractor
from .javascript_extractor import JavaScriptMetadataExtractor
from .java_extractor import JavaMetadataExtractor
from .go_extractor import GoMetadataExtractor


class MetadataExtractorRegistry:
    """Registry for language-specific metadata extraction strategies.

    This class manages all metadata extractors and provides:
    - Strategy lookup by language name or file extension
    - Easy registration of new strategies (OCP compliance)
    - Centralized strategy management

    Follows Open/Closed Principle:
    - Adding new language = register() call, no code modifications
    - Existing code remains unchanged when extending
    """

    def __init__(self) -> None:
        """Initialize registry with default extractors."""
        self._extractors: dict[str, LanguageMetadataExtractor] = {}
        self._extension_map: dict[str, str] = {}

        # Register default extractors
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register built-in language extractors."""
        default_extractors = [
            PythonMetadataExtractor(),
            JavaScriptMetadataExtractor(),
            JavaMetadataExtractor(),
            GoMetadataExtractor(),
        ]

        for extractor in default_extractors:
            self.register(extractor)

    def register(self, extractor: LanguageMetadataExtractor) -> None:
        """Register a metadata extractor for a language.

        Args:
            extractor: Metadata extractor instance

        Raises:
            ValueError: If language already registered (prevents accidental override)
        """
        language = extractor.language

        if language in self._extractors:
            raise ValueError(f"Extractor for '{language}' already registered")

        # Register extractor by language name
        self._extractors[language] = extractor

        # Register file extension mappings
        for ext in extractor.supported_extensions:
            self._extension_map[ext.lower()] = language

    def get_by_language(self, language: str) -> Optional[LanguageMetadataExtractor]:
        """Get extractor by language name.

        Args:
            language: Language name (e.g., "python", "javascript")

        Returns:
            Extractor instance or None if not found
        """
        return self._extractors.get(language.lower())

    def get_by_extension(self, extension: str) -> Optional[LanguageMetadataExtractor]:
        """Get extractor by file extension.

        Args:
            extension: File extension (e.g., ".py", ".js")

        Returns:
            Extractor instance or None if not found
        """
        ext = extension.lower()
        if not ext.startswith('.'):
            ext = f'.{ext}'

        language = self._extension_map.get(ext)
        if language:
            return self._extractors.get(language)
        return None

    def get_supported_languages(self) -> list[str]:
        """Get list of all supported languages.

        Returns:
            List of language names
        """
        return list(self._extractors.keys())

    def get_supported_extensions(self) -> list[str]:
        """Get list of all supported file extensions.

        Returns:
            List of file extensions
        """
        return list(self._extension_map.keys())
