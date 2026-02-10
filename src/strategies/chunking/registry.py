"""Registry for code chunking strategies."""
from typing import Optional
from .base import LanguageChunker
from .python_chunker import PythonChunker
from .javascript_chunker import JavaScriptChunker
from .java_chunker import JavaChunker
from .go_chunker import GoChunker


class ChunkerRegistry:
    """Registry for language-specific code chunking strategies.

    This class manages all code chunkers and provides:
    - Strategy lookup by language name or file extension
    - Easy registration of new strategies (OCP compliance)
    - Centralized strategy management

    Follows Open/Closed Principle:
    - Adding new language = register() call, no code modifications
    - Existing code remains unchanged when extending
    """

    def __init__(self) -> None:
        """Initialize registry with default chunkers."""
        self._chunkers: dict[str, LanguageChunker] = {}
        self._extension_map: dict[str, str] = {}

        # Register default chunkers
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register built-in language chunkers."""
        default_chunkers = [
            PythonChunker(),
            JavaScriptChunker(),
            JavaChunker(),
            GoChunker(),
        ]

        for chunker in default_chunkers:
            self.register(chunker)

    def register(self, chunker: LanguageChunker) -> None:
        """Register a code chunker for a language.

        Args:
            chunker: Code chunker instance

        Raises:
            ValueError: If language already registered (prevents accidental override)
        """
        language = chunker.language

        if language in self._chunkers:
            raise ValueError(f"Chunker for '{language}' already registered")

        # Register chunker by language name
        self._chunkers[language] = chunker

        # Register file extension mappings
        for ext in chunker.supported_extensions:
            self._extension_map[ext.lower()] = language

    def get_by_language(self, language: str) -> Optional[LanguageChunker]:
        """Get chunker by language name.

        Args:
            language: Language name (e.g., "python", "javascript")

        Returns:
            Chunker instance or None if not found
        """
        return self._chunkers.get(language.lower())

    def get_by_extension(self, extension: str) -> Optional[LanguageChunker]:
        """Get chunker by file extension.

        Args:
            extension: File extension (e.g., ".py", ".js")

        Returns:
            Chunker instance or None if not found
        """
        ext = extension.lower()
        if not ext.startswith('.'):
            ext = f'.{ext}'

        language = self._extension_map.get(ext)
        if language:
            return self._chunkers.get(language)
        return None

    def get_supported_languages(self) -> list[str]:
        """Get list of all supported languages.

        Returns:
            List of language names
        """
        return list(self._chunkers.keys())

    def get_supported_extensions(self) -> list[str]:
        """Get list of all supported file extensions.

        Returns:
            List of file extensions
        """
        return list(self._extension_map.keys())
