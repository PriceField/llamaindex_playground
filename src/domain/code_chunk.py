"""Domain object representing a code chunk."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CodeChunk:
    """Represents a chunk of code with location information.

    Replaces the primitive tuple[str, int, int] pattern for better
    type safety and self-documentation.

    Attributes:
        text: The actual code content
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (inclusive)
        language: Programming language (e.g., "python", "javascript")
        file_path: Optional path to the source file
    """

    text: str
    start_line: int
    end_line: int
    language: str
    file_path: str | None = None

    def __post_init__(self) -> None:
        """Validate chunk data."""
        if self.start_line < 1:
            raise ValueError(f"start_line must be >= 1, got {self.start_line}")
        if self.end_line < self.start_line:
            raise ValueError(
                f"end_line ({self.end_line}) must be >= start_line ({self.start_line})"
            )
        if not self.text.strip():
            raise ValueError("text cannot be empty or whitespace-only")
        if not self.language:
            raise ValueError("language cannot be empty")

    @property
    def line_count(self) -> int:
        """Number of lines in this chunk."""
        return self.end_line - self.start_line + 1

    @property
    def char_count(self) -> int:
        """Number of characters in this chunk."""
        return len(self.text)

    def to_tuple(self) -> tuple[str, int, int]:
        """Convert to legacy tuple format for backward compatibility.

        Returns:
            Tuple of (text, start_line, end_line)
        """
        return (self.text, self.start_line, self.end_line)

    @classmethod
    def from_tuple(
        cls,
        chunk_tuple: tuple[str, int, int],
        language: str,
        file_path: str | None = None
    ) -> "CodeChunk":
        """Create from legacy tuple format.

        Args:
            chunk_tuple: Tuple of (text, start_line, end_line)
            language: Programming language
            file_path: Optional file path

        Returns:
            CodeChunk instance
        """
        text, start_line, end_line = chunk_tuple
        return cls(
            text=text,
            start_line=start_line,
            end_line=end_line,
            language=language,
            file_path=file_path,
        )
