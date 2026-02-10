"""JavaScript/TypeScript code chunking strategy."""
import re
from domain.code_chunk import CodeChunk
from .base import LanguageChunker


class JavaScriptChunker(LanguageChunker):
    """Chunk JavaScript/TypeScript code while preserving function and class boundaries.

    This chunker:
    - Detects function and class definitions
    - Tracks brace depth to determine block boundaries
    - Keeps entire functions/classes together in chunks
    """

    @property
    def language(self) -> str:
        """Return language name."""
        return "javascript"

    @property
    def supported_extensions(self) -> list[str]:
        """Return supported file extensions."""
        return [".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"]

    def chunk(
        self,
        content: str,
        file_path: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> list[CodeChunk]:
        """Chunk JavaScript/TypeScript code by functions and classes.

        Args:
            content: JavaScript/TypeScript source code
            file_path: Path to the source file
            chunk_size: Target chunk size (soft limit)
            chunk_overlap: Overlap size (currently not used for structured chunking)

        Returns:
            List of CodeChunk objects
        """
        chunks = []
        lines = content.split('\n')

        # Track current chunk and brace depth
        current_chunk_lines = []
        current_start_line = 1
        brace_depth = 0
        in_function = False

        for i, line in enumerate(lines, 1):
            # Detect function or class start
            if re.search(r'(?:class|function)\s+\w+|const\s+\w+\s*=\s*(?:async\s+)?\(', line):
                # Save previous chunk if at depth 0
                if current_chunk_lines and brace_depth == 0:
                    chunk_text = '\n'.join(current_chunk_lines)
                    if chunk_text.strip():
                        chunks.append(
                            CodeChunk(
                                text=chunk_text,
                                start_line=current_start_line,
                                end_line=i - 1,
                                language=self.language,
                                file_path=file_path,
                            )
                        )
                    current_chunk_lines = []
                    current_start_line = i

                in_function = True

            current_chunk_lines.append(line)

            # Track braces
            brace_depth += line.count('{') - line.count('}')

            # End of function/class (back to depth 0 after having braces)
            if in_function and brace_depth == 0 and '{' in '\n'.join(current_chunk_lines):
                chunk_text = '\n'.join(current_chunk_lines)
                if chunk_text.strip():
                    chunks.append(
                        CodeChunk(
                            text=chunk_text,
                            start_line=current_start_line,
                            end_line=i,
                            language=self.language,
                            file_path=file_path,
                        )
                    )
                current_chunk_lines = []
                current_start_line = i + 1
                in_function = False

        # Add remaining content
        if current_chunk_lines:
            chunk_text = '\n'.join(current_chunk_lines)
            if chunk_text.strip():
                chunks.append(
                    CodeChunk(
                        text=chunk_text,
                        start_line=current_start_line,
                        end_line=len(lines),
                        language=self.language,
                        file_path=file_path,
                    )
                )

        # Ensure at least one chunk
        if not chunks:
            chunks.append(
                CodeChunk(
                    text=content,
                    start_line=1,
                    end_line=len(lines),
                    language=self.language,
                    file_path=file_path,
                )
            )

        return chunks
