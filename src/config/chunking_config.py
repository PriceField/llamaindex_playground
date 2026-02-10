"""Configuration for code and document chunking."""

from dataclasses import dataclass
from .env_parser import EnvParser


@dataclass(frozen=True)
class ChunkingConfig:
    """Configuration for chunking code and documentation.

    Follows Interface Segregation Principle - clients only depend on
    chunking-related settings.

    Attributes:
        code_chunk_size: Maximum size for code chunks (in characters)
        code_chunk_overlap: Overlap between code chunks (in characters)
        doc_chunk_size: Maximum size for documentation chunks (in characters)
        doc_chunk_overlap: Overlap between documentation chunks (in characters)
        preserve_code_structure: Whether to preserve function/class boundaries
        include_line_numbers: Whether to include line numbers in chunk metadata
    """

    code_chunk_size: int
    code_chunk_overlap: int
    doc_chunk_size: int
    doc_chunk_overlap: int
    preserve_code_structure: bool
    include_line_numbers: bool

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.code_chunk_size < 1:
            raise ValueError(f"code_chunk_size must be >= 1, got {self.code_chunk_size}")
        if self.code_chunk_overlap < 0:
            raise ValueError(f"code_chunk_overlap must be >= 0, got {self.code_chunk_overlap}")
        if self.code_chunk_overlap >= self.code_chunk_size:
            raise ValueError(
                f"code_chunk_overlap ({self.code_chunk_overlap}) must be < code_chunk_size ({self.code_chunk_size})"
            )

        if self.doc_chunk_size < 1:
            raise ValueError(f"doc_chunk_size must be >= 1, got {self.doc_chunk_size}")
        if self.doc_chunk_overlap < 0:
            raise ValueError(f"doc_chunk_overlap must be >= 0, got {self.doc_chunk_overlap}")
        if self.doc_chunk_overlap >= self.doc_chunk_size:
            raise ValueError(
                f"doc_chunk_overlap ({self.doc_chunk_overlap}) must be < doc_chunk_size ({self.doc_chunk_size})"
            )

    @classmethod
    def from_env(cls) -> "ChunkingConfig":
        """Create configuration from environment variables.

        Returns:
            ChunkingConfig instance loaded from environment
        """
        return cls(
            code_chunk_size=EnvParser.parse_int("CODE_CHUNK_SIZE", 512),
            code_chunk_overlap=EnvParser.parse_int("CODE_CHUNK_OVERLAP", 50),
            doc_chunk_size=EnvParser.parse_int("DOC_CHUNK_SIZE", 1024),
            doc_chunk_overlap=EnvParser.parse_int("DOC_CHUNK_OVERLAP", 20),
            preserve_code_structure=EnvParser.parse_bool("PRESERVE_CODE_STRUCTURE", True),
            include_line_numbers=EnvParser.parse_bool("INCLUDE_LINE_NUMBERS", True),
        )

    @classmethod
    def default(cls) -> "ChunkingConfig":
        """Create configuration with default values.

        Returns:
            ChunkingConfig with default settings
        """
        return cls(
            code_chunk_size=512,
            code_chunk_overlap=50,
            doc_chunk_size=1024,
            doc_chunk_overlap=20,
            preserve_code_structure=True,
            include_line_numbers=True,
        )
