"""Abstract base class for language-specific code chunking."""
from abc import ABC, abstractmethod
from domain.code_chunk import CodeChunk


class LanguageChunker(ABC):
    """Abstract strategy for chunking source code into meaningful segments.

    This interface defines the contract for language-specific code chunkers.
    Each language implementation chunks code by preserving logical boundaries
    (functions, classes, methods) according to that language's syntax.

    Follows Strategy Pattern and Open/Closed Principle:
    - Adding new language = new class implementing this interface
    - No modifications to existing chunkers required
    """

    @abstractmethod
    def chunk(
        self,
        content: str,
        file_path: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> list[CodeChunk]:
        """Chunk source code while preserving logical boundaries.

        Args:
            content: Source code content
            file_path: Path to the source file
            chunk_size: Target chunk size in characters (soft limit)
            chunk_overlap: Number of overlapping characters between chunks

        Returns:
            List of CodeChunk objects with text, start_line, end_line

        Note:
            Implementations should respect chunk_size as a guideline but may
            exceed it to preserve logical boundaries (e.g., complete functions).
            Return at least one chunk even if content is empty or very small.
        """
        pass

    @property
    @abstractmethod
    def language(self) -> str:
        """Return the programming language this chunker handles.

        Returns:
            Language name (e.g., "python", "javascript", "java", "go")
        """
        pass

    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """Return file extensions supported by this chunker.

        Returns:
            List of file extensions (e.g., [".py", ".pyw"] for Python)
        """
        pass
