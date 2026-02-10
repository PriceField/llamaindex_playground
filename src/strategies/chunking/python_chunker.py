"""Python code chunking strategy."""
import re
from domain.code_chunk import CodeChunk
from .base import LanguageChunker


class PythonChunker(LanguageChunker):
    """Chunk Python code while preserving function and class boundaries.

    This chunker:
    - Detects function (def, async def) and class definitions
    - Keeps entire functions/classes together in chunks
    - Uses indentation to determine block boundaries
    - Falls back to size-based chunking for non-structured code
    """

    @property
    def language(self) -> str:
        """Return language name."""
        return "python"

    @property
    def supported_extensions(self) -> list[str]:
        """Return supported file extensions."""
        return [".py", ".pyw"]

    def chunk(
        self,
        content: str,
        file_path: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> list[CodeChunk]:
        """Chunk Python code by functions and classes.

        Args:
            content: Python source code
            file_path: Path to the source file
            chunk_size: Target chunk size (soft limit)
            chunk_overlap: Overlap size (currently not used for structured chunking)

        Returns:
            List of CodeChunk objects
        """
        chunks = []
        lines = content.split('\n')

        # Track current chunk being built
        current_chunk_lines = []
        current_start_line = 1
        in_block = False
        block_indent = 0

        for i, line in enumerate(lines, 1):
            # Detect function or class definition (start of new block)
            if re.match(r'^(?:class|def|async\s+def)\s+', line):
                # Save previous chunk if it exists
                if current_chunk_lines:
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

                # Start new chunk
                current_chunk_lines = [line]
                current_start_line = i
                in_block = True
                block_indent = len(line) - len(line.lstrip())

            elif in_block:
                # Continue block if indented or empty line
                if line.strip():
                    line_indent = len(line) - len(line.lstrip())
                    if line_indent > block_indent:
                        current_chunk_lines.append(line)
                    else:
                        # Block ended - save it and start new chunk
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
                        current_chunk_lines = [line]
                        current_start_line = i
                        in_block = False
                else:
                    # Empty line within block
                    current_chunk_lines.append(line)

            else:
                # Not in a structured block
                current_chunk_lines.append(line)

                # Check if chunk is getting too large
                chunk_text = '\n'.join(current_chunk_lines)
                if len(chunk_text) > chunk_size * 2:
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

        # Add final chunk
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

        # Ensure at least one chunk (even if empty)
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
