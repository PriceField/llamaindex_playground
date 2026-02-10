"""Configuration for query execution."""

from dataclasses import dataclass
from .env_parser import EnvParser


@dataclass(frozen=True)
class QueryConfig:
    """Configuration for query execution.

    Follows Interface Segregation Principle - clients only depend on
    query-related settings.

    Attributes:
        code_similarity_top_k: Number of similar code chunks to retrieve
        use_metadata_filters: Whether to use metadata for filtering results
        include_source_context: Whether to include source file context in results
    """

    code_similarity_top_k: int
    use_metadata_filters: bool
    include_source_context: bool

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.code_similarity_top_k < 1:
            raise ValueError(
                f"code_similarity_top_k must be >= 1, got {self.code_similarity_top_k}"
            )

    @classmethod
    def from_env(cls) -> "QueryConfig":
        """Create configuration from environment variables.

        Returns:
            QueryConfig instance loaded from environment
        """
        return cls(
            code_similarity_top_k=EnvParser.parse_int("CODE_SIMILARITY_TOP_K", 5),
            use_metadata_filters=EnvParser.parse_bool("USE_METADATA_FILTERS", True),
            include_source_context=EnvParser.parse_bool("INCLUDE_SOURCE_CONTEXT", True),
        )

    @classmethod
    def default(cls) -> "QueryConfig":
        """Create configuration with default values.

        Returns:
            QueryConfig with default settings
        """
        return cls(
            code_similarity_top_k=5,
            use_metadata_filters=True,
            include_source_context=True,
        )
