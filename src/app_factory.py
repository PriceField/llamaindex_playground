"""Application factory for dependency injection.

This module provides a central factory for creating application components
with proper dependency injection.

Follows SOLID principles:
- SRP: Only responsible for object creation and wiring
- DIP: Wires together abstractions via constructor injection
- OCP: Can be extended with new creation methods
"""

from pathlib import Path

from config.chunking_config import ChunkingConfig
from config.embedding_config import EmbeddingConfig
from config.extraction_config import ExtractionConfig
from config.file_filter_config import FileFilterConfig
from config.query_config import QueryConfig
from config.language_detector import LanguageDetector
from config.file_categorizer import FileCategorizer
from embedding.embedding_factory import EmbeddingFactory
from file_handlers import FileHandler
from code_extractors import CodeMetadataExtractor
from loading.document_loader import DocumentLoader
from indexing.indexing_orchestrator import IndexingOrchestrator
from llm.llm_configurer import LLMConfig, LLMConfigurer
from config import IndexerConfig
from strategies.extraction.registry import MetadataExtractorRegistry
from strategies.chunking.registry import ChunkerRegistry


class AppFactory:
    """Factory for creating application components with dependency injection.

    This class centralizes the creation and wiring of all application components,
    making it easy to:
    - Create production instances with real dependencies
    - Create test instances with mock dependencies
    - Swap implementations without modifying client code

    Follows the Factory pattern and Dependency Injection pattern.
    """

    @staticmethod
    def create_indexing_orchestrator(
        index_name: str = "default",
        require_llm: bool = True,
    ) -> IndexingOrchestrator:
        """Create a fully-wired IndexingOrchestrator for production use.

        This method creates all necessary dependencies and wires them together
        using constructor injection.

        Args:
            index_name: Name for the index (used for storage directory)
            require_llm: Whether LLM is required (for validation)

        Returns:
            IndexingOrchestrator with all dependencies wired

        Raises:
            ValueError: If required environment variables are missing
        """
        # Validate environment (will raise if missing required vars)
        from environment import validate_environment
        validate_environment(require_llm=require_llm)

        # ====================================================================
        # Create Configuration Objects
        # ====================================================================

        # Load configurations from environment
        chunking_config = ChunkingConfig.from_env()
        embedding_config = EmbeddingConfig.from_env()
        extraction_config = ExtractionConfig.from_env()
        file_filter_config = FileFilterConfig.from_env()
        query_config = QueryConfig.from_env()

        # Create utility components
        language_detector = LanguageDetector.default()
        file_categorizer = FileCategorizer.default()

        # Create strategy registries (Phase 2 refactoring)
        metadata_extractor_registry = MetadataExtractorRegistry()
        chunker_registry = ChunkerRegistry()

        # ====================================================================
        # Create Service Components
        # ====================================================================

        # Create embedding factory
        embedding_factory = EmbeddingFactory(embedding_config)

        # Create file handler (depends on language detector and categorizer)
        # Note: FileHandler currently uses IndexerConfig, will migrate later
        legacy_config = IndexerConfig()  # Temporary bridge
        file_handler = legacy_config.create_file_handler()

        # Create code extractor with strategy registry (REFACTORED in Phase 2)
        # Note: CodeMetadataExtractor still uses IndexerConfig for extraction flags
        code_extractor = CodeMetadataExtractor(
            config=legacy_config,
            registry=metadata_extractor_registry,
        )

        # Create document loader (depends on file handler and code extractor)
        document_loader = DocumentLoader(
            file_handler=file_handler,
            code_extractor=code_extractor,
        )

        # Create LLM configurer if required (for query operations)
        llm_configurer: LLMConfigurer | None = None
        if require_llm:
            try:
                llm_config = LLMConfig.from_env()
                llm_configurer = LLMConfigurer(llm_config)
            except ValueError as e:
                print(f"[!] LLM configuration failed: {e}")
                print("[*] Query operations will use free mode only (no LLM)")

        # ====================================================================
        # Create Orchestrator
        # ====================================================================

        orchestrator = IndexingOrchestrator(
            index_name=index_name,
            embedding_factory=embedding_factory,
            document_loader=document_loader,
            file_handler=file_handler,
            chunking_config=chunking_config,
            file_filter_config=file_filter_config,
            query_config=query_config,
            llm_configurer=llm_configurer,
            chunker_registry=chunker_registry,  # Phase 2: inject chunking registry
        )

        # ====================================================================
        # Setup Global Settings
        # ====================================================================

        # Note: LLM configuration is deferred to query time (when actually needed)
        # This allows indexing-only mode without LLM validation

        # Setup embeddings and parser (configures Settings.embed_model and Settings.node_parser)
        orchestrator.setup_embeddings_and_parser()

        return orchestrator

    @staticmethod
    def create_orchestrator_with_custom_deps(
        index_name: str,
        embedding_factory: EmbeddingFactory,
        document_loader: DocumentLoader,
        file_handler: FileHandler,
        chunking_config: ChunkingConfig,
        file_filter_config: FileFilterConfig,
        query_config: QueryConfig,
        llm_configurer: LLMConfigurer | None = None,
        chunker_registry: ChunkerRegistry | None = None,
    ) -> IndexingOrchestrator:
        """Create IndexingOrchestrator with custom dependencies.

        This is useful for testing with mock dependencies or for custom configurations.

        Args:
            index_name: Name for the index
            embedding_factory: Custom embedding factory
            document_loader: Custom document loader
            file_handler: Custom file handler
            chunking_config: Custom chunking configuration
            file_filter_config: Custom file filter configuration
            query_config: Custom query configuration
            llm_configurer: Optional custom LLM configurer
            chunker_registry: Optional custom chunker registry (Phase 2)

        Returns:
            IndexingOrchestrator with injected dependencies
        """
        return IndexingOrchestrator(
            index_name=index_name,
            embedding_factory=embedding_factory,
            document_loader=document_loader,
            file_handler=file_handler,
            chunking_config=chunking_config,
            file_filter_config=file_filter_config,
            query_config=query_config,
            llm_configurer=llm_configurer,
            chunker_registry=chunker_registry,
        )

    @staticmethod
    def create_llm_configurer(require_llm: bool = True) -> LLMConfigurer | None:
        """Create LLM configurer from environment.

        Args:
            require_llm: Whether LLM is required

        Returns:
            LLMConfigurer instance or None if not required

        Raises:
            ValueError: If require_llm=True but configuration is missing
        """
        if not require_llm:
            return None

        llm_config = LLMConfig.from_env()
        return LLMConfigurer(llm_config)

    @staticmethod
    def create_embedding_factory() -> EmbeddingFactory:
        """Create embedding factory from environment.

        Returns:
            EmbeddingFactory instance configured from environment

        Raises:
            ValueError: If embedding configuration is invalid
        """
        embedding_config = EmbeddingConfig.from_env()
        return EmbeddingFactory(embedding_config)

    @staticmethod
    def create_document_loader() -> DocumentLoader:
        """Create document loader with default dependencies.

        Returns:
            DocumentLoader with file handler and code extractor

        Note:
            Currently uses legacy IndexerConfig as bridge.
            Will be updated when FileHandler and CodeMetadataExtractor are migrated.
        """
        # Temporary bridge using legacy config
        legacy_config = IndexerConfig()
        file_handler = legacy_config.create_file_handler()
        code_extractor = CodeMetadataExtractor(legacy_config)

        return DocumentLoader(
            file_handler=file_handler,
            code_extractor=code_extractor,
        )


class TestAppFactory(AppFactory):
    """Extended factory for creating test instances with mock dependencies.

    This subclass provides additional methods for creating components
    with mock dependencies for testing purposes.

    Example usage:
        >>> from unittest.mock import Mock
        >>> factory = TestAppFactory()
        >>> mock_embedding_factory = Mock(spec=EmbeddingFactory)
        >>> mock_document_loader = Mock(spec=DocumentLoader)
        >>> orchestrator = factory.create_test_orchestrator(
        ...     embedding_factory=mock_embedding_factory,
        ...     document_loader=mock_document_loader,
        ... )
    """

    @staticmethod
    def create_test_orchestrator(
        index_name: str = "test-index",
        embedding_factory=None,
        document_loader=None,
        file_handler=None,
        chunking_config=None,
        file_filter_config=None,
        query_config=None,
        llm_configurer=None,
    ) -> IndexingOrchestrator:
        """Create orchestrator for testing with optional mock dependencies.

        Any non-provided dependencies will use default/mock implementations.

        Args:
            index_name: Name for test index
            embedding_factory: Optional mock embedding factory
            document_loader: Optional mock document loader
            file_handler: Optional mock file handler
            chunking_config: Optional mock chunking config
            file_filter_config: Optional mock file filter config
            query_config: Optional mock query config
            llm_configurer: Optional mock LLM configurer

        Returns:
            IndexingOrchestrator suitable for testing
        """
        from unittest.mock import Mock

        # Create default mocks if not provided
        if embedding_factory is None:
            embedding_factory = Mock(spec=EmbeddingFactory)

        if document_loader is None:
            document_loader = Mock(spec=DocumentLoader)

        if file_handler is None:
            file_handler = Mock(spec=FileHandler)

        if chunking_config is None:
            chunking_config = ChunkingConfig.default()

        if file_filter_config is None:
            file_filter_config = FileFilterConfig.default()

        if query_config is None:
            query_config = QueryConfig.default()

        return AppFactory.create_orchestrator_with_custom_deps(
            index_name=index_name,
            embedding_factory=embedding_factory,
            document_loader=document_loader,
            file_handler=file_handler,
            chunking_config=chunking_config,
            file_filter_config=file_filter_config,
            query_config=query_config,
            llm_configurer=llm_configurer,
        )
