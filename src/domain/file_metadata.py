"""Domain object representing file metadata."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileMetadata:
    """Represents metadata for a source file.

    Provides a structured alternative to using raw dictionaries
    for file information.

    Attributes:
        file_path: Path to the file
        language: Programming language
        category: File category (code, documentation, config, etc.)
        start_line: Optional starting line number for chunks
        end_line: Optional ending line number for chunks
        chunk_index: Optional index of this chunk in sequence
    """

    file_path: str
    language: str
    category: str
    start_line: int | None = None
    end_line: int | None = None
    chunk_index: int | None = None

    def __post_init__(self) -> None:
        """Validate metadata."""
        if not self.file_path:
            raise ValueError("file_path cannot be empty")
        if not self.language:
            raise ValueError("language cannot be empty")
        if not self.category:
            raise ValueError("category cannot be empty")

        # Validate line numbers if provided
        if self.start_line is not None and self.start_line < 1:
            raise ValueError(f"start_line must be >= 1, got {self.start_line}")
        if self.end_line is not None and self.start_line is not None:
            if self.end_line < self.start_line:
                raise ValueError(
                    f"end_line ({self.end_line}) must be >= start_line ({self.start_line})"
                )
        if self.chunk_index is not None and self.chunk_index < 0:
            raise ValueError(f"chunk_index must be >= 0, got {self.chunk_index}")

    @property
    def is_code(self) -> bool:
        """Check if this is a code file."""
        return self.category == "code"

    @property
    def is_documentation(self) -> bool:
        """Check if this is a documentation file."""
        return self.category == "documentation"

    @property
    def is_config(self) -> bool:
        """Check if this is a configuration file."""
        return self.category == "config"

    @property
    def has_line_info(self) -> bool:
        """Check if line information is available."""
        return self.start_line is not None and self.end_line is not None

    @property
    def line_count(self) -> int | None:
        """Number of lines if line info is available."""
        if self.has_line_info:
            return self.end_line - self.start_line + 1
        return None

    @property
    def path(self) -> Path:
        """Get file path as Path object."""
        return Path(self.file_path)

    @property
    def file_name(self) -> str:
        """Get just the filename without directory."""
        return Path(self.file_path).name

    @property
    def file_extension(self) -> str:
        """Get file extension including the dot (e.g., '.py')."""
        return Path(self.file_path).suffix

    def to_dict(self) -> dict[str, str | int]:
        """Convert to dictionary format for LlamaIndex compatibility.

        Returns:
            Dictionary with metadata fields
        """
        result = {
            "file_path": self.file_path,
            "language": self.language,
            "category": self.category,
        }

        if self.start_line is not None:
            result["start_line"] = self.start_line
        if self.end_line is not None:
            result["end_line"] = self.end_line
        if self.chunk_index is not None:
            result["chunk_index"] = self.chunk_index

        return result

    @classmethod
    def from_dict(cls, data: dict[str, str | int]) -> "FileMetadata":
        """Create from dictionary format.

        Args:
            data: Dictionary with metadata fields

        Returns:
            FileMetadata instance
        """
        return cls(
            file_path=str(data["file_path"]),
            language=str(data["language"]),
            category=str(data["category"]),
            start_line=int(data["start_line"]) if "start_line" in data else None,
            end_line=int(data["end_line"]) if "end_line" in data else None,
            chunk_index=int(data["chunk_index"]) if "chunk_index" in data else None,
        )

    def with_chunk_info(
        self,
        start_line: int,
        end_line: int,
        chunk_index: int
    ) -> "FileMetadata":
        """Create a new instance with chunk information added.

        Args:
            start_line: Starting line number
            end_line: Ending line number
            chunk_index: Chunk index

        Returns:
            New FileMetadata instance with chunk info
        """
        return FileMetadata(
            file_path=self.file_path,
            language=self.language,
            category=self.category,
            start_line=start_line,
            end_line=end_line,
            chunk_index=chunk_index,
        )
