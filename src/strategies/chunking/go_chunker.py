"""Go code chunking strategy."""
from domain.code_chunk import CodeChunk
from .base import LanguageChunker
from .javascript_chunker import JavaScriptChunker


class GoChunker(LanguageChunker):
    """Chunk Go code while preserving function and struct boundaries.

    Go uses brace-based structure similar to JavaScript/C-family languages,
    so we delegate to JavaScriptChunker for the actual chunking logic.
    """

    @property
    def language(self) -> str:
        """Return language name."""
        return "go"

    @property
    def supported_extensions(self) -> list[str]:
        """Return supported file extensions."""
        return [".go"]

    def chunk(
        self,
        content: str,
        file_path: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> list[CodeChunk]:
        """Chunk Go code by functions and structs.

        Delegates to JavaScriptChunker since Go has similar
        brace-based structure.

        Args:
            content: Go source code
            file_path: Path to the source file
            chunk_size: Target chunk size (soft limit)
            chunk_overlap: Overlap size (currently not used)

        Returns:
            List of CodeChunk objects with language set to "go"
        """
        # Delegate to JavaScript chunker (same brace-based structure)
        js_chunker = JavaScriptChunker()
        chunks = js_chunker.chunk(content, file_path, chunk_size, chunk_overlap)

        # Update language to "go" for all chunks
        go_chunks = []
        for chunk in chunks:
            go_chunks.append(
                CodeChunk(
                    text=chunk.text,
                    start_line=chunk.start_line,
                    end_line=chunk.end_line,
                    language=self.language,
                    file_path=file_path,
                )
            )

        return go_chunks
