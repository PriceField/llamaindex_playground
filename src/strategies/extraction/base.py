"""Abstract base class for language-specific metadata extraction."""
from abc import ABC, abstractmethod
from domain.code_metadata import CodeMetadata


class LanguageMetadataExtractor(ABC):
    """Abstract strategy for extracting metadata from source code.

    This interface defines the contract for language-specific metadata extractors.
    Each language implementation extracts functions, classes, imports, etc.
    according to that language's syntax.

    Follows Strategy Pattern and Open/Closed Principle:
    - Adding new language = new class implementing this interface
    - No modifications to existing extractors required
    """

    @abstractmethod
    def extract(
        self,
        content: str,
        extract_functions: bool = True,
        extract_classes: bool = True,
        extract_imports: bool = True,
    ) -> CodeMetadata:
        """Extract metadata from source code.

        Args:
            content: Source code content
            extract_functions: Whether to extract function definitions
            extract_classes: Whether to extract class definitions
            extract_imports: Whether to extract import statements

        Returns:
            CodeMetadata object containing extracted metadata

        Note:
            Implementations should return empty lists for disabled extractions,
            not None. This ensures consistent behavior across all strategies.
        """
        pass

    @property
    @abstractmethod
    def language(self) -> str:
        """Return the programming language this extractor handles.

        Returns:
            Language name (e.g., "python", "javascript", "java", "go")
        """
        pass

    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """Return file extensions supported by this extractor.

        Returns:
            List of file extensions (e.g., [".py", ".pyw"] for Python)
        """
        pass
