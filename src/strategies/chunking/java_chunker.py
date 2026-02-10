"""Java code chunking strategy."""
from domain.code_chunk import CodeChunk
from .base import LanguageChunker
from .javascript_chunker import JavaScriptChunker


class JavaChunker(LanguageChunker):
    """Chunk Java code while preserving method and class boundaries.

    Java uses brace-based structure similar to JavaScript/TypeScript,
    so we delegate to JavaScriptChunker for the actual chunking logic.
    """

    @property
    def language(self) -> str:
        """Return language name."""
        return "java"

    @property
    def supported_extensions(self) -> list[str]:
        """Return supported file extensions."""
        return [".java"]

    def chunk(
        self,
        content: str,
        file_path: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> list[CodeChunk]:
        """Chunk Java code by methods and classes.

        Delegates to JavaScriptChunker since Java has similar
        brace-based structure.

        Args:
            content: Java source code
            file_path: Path to the source file
            chunk_size: Target chunk size (soft limit)
            chunk_overlap: Overlap size (currently not used)

        Returns:
            List of CodeChunk objects with language set to "java"
        """
        # Delegate to JavaScript chunker (same brace-based structure)
        js_chunker = JavaScriptChunker()
        chunks = js_chunker.chunk(content, file_path, chunk_size, chunk_overlap)

        # Update language to "java" for all chunks
        java_chunks = []
        for chunk in chunks:
            java_chunks.append(
                CodeChunk(
                    text=chunk.text,
                    start_line=chunk.start_line,
                    end_line=chunk.end_line,
                    language=self.language,
                    file_path=file_path,
                )
            )

        return java_chunks
