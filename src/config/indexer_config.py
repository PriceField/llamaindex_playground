"""Legacy IndexerConfig bridge for backward compatibility.

DEPRECATED: This module exists only for backward compatibility during refactoring.
New code should use the focused configuration classes directly:
- ChunkingConfig for chunking settings
- ExtractionConfig for metadata extraction
- EmbeddingConfig for embedding models
- QueryConfig for query execution
- FileFilterConfig for file filtering

This module will be removed after main.py is migrated in Phase 4.
"""

from .chunking_config import ChunkingConfig
from .extraction_config import ExtractionConfig
from .embedding_config import EmbeddingConfig
from .query_config import QueryConfig
from .file_filter_config import FileFilterConfig
from .language_detector import LanguageDetector
from .file_categorizer import FileCategorizer


class IndexerConfig:
    """Backward-compatibility bridge for old IndexerConfig interface.

    This class aggregates the 5 new focused config classes and provides
    the old monolithic interface for legacy code. It uses the Adapter Pattern
    to delegate property access to the appropriate underlying config.

    DEPRECATED: New code should use focused config classes directly:
    - ChunkingConfig for chunking settings
    - ExtractionConfig for metadata extraction
    - EmbeddingConfig for embedding models
    - QueryConfig for query execution
    - FileFilterConfig for file filtering

    This class will be removed after main.py is migrated in Phase 4.

    Migration Example:
        # Old way (deprecated):
        config = IndexerConfig()
        chunk_size = config.code_chunk_size

        # New way (recommended):
        chunking = ChunkingConfig.from_env()
        chunk_size = chunking.code_chunk_size
    """

    def __init__(self) -> None:
        """Initialize by loading all config classes from environment.

        This creates instances of all 5 focused config classes and 2 utility
        classes, providing backward compatibility with the old monolithic config.
        """
        # Load all config components from environment
        self._chunking = ChunkingConfig.from_env()
        self._extraction = ExtractionConfig.from_env()
        self._embedding = EmbeddingConfig.from_env()
        self._query = QueryConfig.from_env()
        self._file_filter = FileFilterConfig.from_env()
        self._language_detector = LanguageDetector()
        self._file_categorizer = FileCategorizer()

    # -------------------------------------------------------------------------
    # Chunking Properties (delegated to ChunkingConfig)
    # -------------------------------------------------------------------------

    @property
    def code_chunk_size(self) -> int:
        """Maximum size for code chunks (in characters)."""
        return self._chunking.code_chunk_size

    @property
    def code_chunk_overlap(self) -> int:
        """Overlap between code chunks (in characters)."""
        return self._chunking.code_chunk_overlap

    @property
    def doc_chunk_size(self) -> int:
        """Maximum size for documentation chunks (in characters)."""
        return self._chunking.doc_chunk_size

    @property
    def doc_chunk_overlap(self) -> int:
        """Overlap between documentation chunks (in characters)."""
        return self._chunking.doc_chunk_overlap

    @property
    def preserve_code_structure(self) -> bool:
        """Whether to preserve function/class boundaries when chunking."""
        return self._chunking.preserve_code_structure

    @property
    def include_line_numbers(self) -> bool:
        """Whether to include line numbers in chunk metadata.

        Note: This property exists in both ChunkingConfig and ExtractionConfig.
        We delegate to ChunkingConfig as it's the primary consumer (used by
        CodeAwareNodeParser).
        """
        return self._chunking.include_line_numbers

    # -------------------------------------------------------------------------
    # Extraction Properties (delegated to ExtractionConfig)
    # -------------------------------------------------------------------------

    @property
    def extract_functions(self) -> bool:
        """Whether to extract function/method names from code."""
        return self._extraction.extract_functions

    @property
    def extract_classes(self) -> bool:
        """Whether to extract class names from code."""
        return self._extraction.extract_classes

    @property
    def extract_imports(self) -> bool:
        """Whether to extract import statements from code."""
        return self._extraction.extract_imports

    # -------------------------------------------------------------------------
    # Embedding Properties (delegated to EmbeddingConfig)
    # -------------------------------------------------------------------------

    @property
    def embed_model_type(self) -> str:
        """Type of embedding model ('local' or 'openai')."""
        return self._embedding.embed_model_type

    @property
    def embed_model_name(self) -> str:
        """HuggingFace model name for local embeddings."""
        return self._embedding.embed_model_name

    @property
    def embed_api_key(self) -> str:
        """API key for OpenAI embeddings."""
        return self._embedding.embed_api_key

    @property
    def embed_api_base(self) -> str:
        """Base URL for OpenAI API (optional)."""
        return self._embedding.embed_api_base

    @property
    def embed_openai_model(self) -> str:
        """OpenAI model name for embeddings (e.g., 'text-embedding-ada-002')."""
        return self._embedding.embed_openai_model

    # -------------------------------------------------------------------------
    # Query Properties (delegated to QueryConfig)
    # -------------------------------------------------------------------------

    @property
    def code_similarity_top_k(self) -> int:
        """Number of similar code chunks to retrieve during queries."""
        return self._query.code_similarity_top_k

    @property
    def use_metadata_filters(self) -> bool:
        """Whether to use metadata for filtering query results."""
        return self._query.use_metadata_filters

    @property
    def include_source_context(self) -> bool:
        """Whether to include source file context in query results."""
        return self._query.include_source_context

    # -------------------------------------------------------------------------
    # File Filter Properties (delegated to FileFilterConfig)
    # -------------------------------------------------------------------------

    @property
    def supported_languages(self) -> list[str]:
        """List of programming languages to index."""
        return self._file_filter.supported_languages

    @property
    def default_exclude_patterns(self) -> list[str]:
        """Patterns to exclude from indexing (directories, files)."""
        return self._file_filter.default_exclude_patterns

    # -------------------------------------------------------------------------
    # Language Detection (delegated to LanguageDetector)
    # -------------------------------------------------------------------------

    @property
    def language_extensions(self) -> dict[str, list[str]]:
        """Language-to-extensions mapping.

        Returns:
            Dictionary mapping language names to file extensions
            (e.g., {'python': ['.py', '.pyw']})
        """
        return self._language_detector.language_extensions

    def detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension.

        Args:
            file_path: Path to the file

        Returns:
            Language name (e.g., 'python', 'javascript') or 'unknown'
        """
        return self._language_detector.detect(file_path)

    # -------------------------------------------------------------------------
    # File Categorization (delegated to FileCategorizer)
    # -------------------------------------------------------------------------

    @property
    def file_categories(self) -> dict[str, list[str]]:
        """Category-to-extensions mapping.

        Returns:
            Dictionary mapping category names to file extensions
            (e.g., {'documentation': ['.md', '.rst']})
        """
        return self._file_categorizer.category_extensions

    def detect_category(self, file_path: str) -> str:
        """Detect file category from extension.

        Args:
            file_path: Path to the file

        Returns:
            Category name (e.g., 'code', 'documentation', 'configuration') or 'other'
        """
        return self._file_categorizer.categorize(file_path)

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def create_file_handler(self):
        """Create FileHandler with appropriate dependencies.

        This helper method addresses the constructor signature mismatch:
        - Old code: FileHandler(config)
        - New code: FileHandler(file_filter_config, language_detector, file_categorizer)

        Returns:
            FileHandler instance configured from this config

        Example:
            # Old way (won't work with new FileHandler):
            # file_handler = FileHandler(config)

            # Bridge way (works with both old and new code):
            file_handler = config.create_file_handler()
        """
        # Import here to avoid circular dependency
        from file_handlers import FileHandler

        return FileHandler(
            file_filter_config=self._file_filter,
            language_detector=self._language_detector,
            file_categorizer=self._file_categorizer,
        )
