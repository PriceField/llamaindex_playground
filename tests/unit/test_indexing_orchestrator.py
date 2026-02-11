"""Unit tests for IndexingOrchestrator."""
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime

sys.path.insert(0, "src")

from indexing.indexing_orchestrator import IndexingOrchestrator, debug_log
from config.chunking_config import ChunkingConfig
from config.file_filter_config import FileFilterConfig
from config.query_config import QueryConfig
from embedding.embedding_factory import EmbeddingFactory
from file_handlers import FileHandler
from loading.document_loader import DocumentLoader
from llm.llm_configurer import LLMConfigurer
from strategies.chunking.registry import ChunkerRegistry


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_embedding_factory():
    """Create mock EmbeddingFactory."""
    factory = Mock(spec=EmbeddingFactory)
    factory.create.return_value = Mock()  # Mock embedding model
    return factory


@pytest.fixture
def mock_document_loader():
    """Create mock DocumentLoader."""
    loader = Mock(spec=DocumentLoader)
    return loader


@pytest.fixture
def mock_file_handler():
    """Create mock FileHandler."""
    handler = Mock(spec=FileHandler)
    handler.should_index_file.return_value = True
    return handler


@pytest.fixture
def chunking_config():
    """Create ChunkingConfig for testing."""
    return ChunkingConfig(
        code_chunk_size=512,
        code_chunk_overlap=50,
        doc_chunk_size=1024,
        doc_chunk_overlap=20,
        preserve_code_structure=True,
        include_line_numbers=True,
    )


@pytest.fixture
def file_filter_config():
    """Create FileFilterConfig for testing."""
    return FileFilterConfig(
        supported_languages=["python", "javascript", "markdown"],
        default_exclude_patterns=["*test*", "__pycache__", "node_modules"],
    )


@pytest.fixture
def mock_chunker_registry():
    """Create mock ChunkerRegistry."""
    return Mock(spec=ChunkerRegistry)


@pytest.fixture
def query_config():
    """Create QueryConfig for testing."""
    return QueryConfig(
        code_similarity_top_k=5,
        use_metadata_filters=True,
        include_source_context=True,
    )


@pytest.fixture
def mock_llm_configurer():
    """Create mock LLMConfigurer."""
    return Mock(spec=LLMConfigurer)


@pytest.fixture
def orchestrator(
    mock_embedding_factory,
    mock_document_loader,
    mock_file_handler,
    chunking_config,
    file_filter_config,
    query_config,
    mock_llm_configurer,
    mock_chunker_registry,
):
    """Create IndexingOrchestrator for testing."""
    return IndexingOrchestrator(
        index_name="test_index",
        embedding_factory=mock_embedding_factory,
        document_loader=mock_document_loader,
        file_handler=mock_file_handler,
        chunking_config=chunking_config,
        file_filter_config=file_filter_config,
        query_config=query_config,
        llm_configurer=mock_llm_configurer,
        chunker_registry=mock_chunker_registry,
    )


# ============================================================================
# Test: Initialization
# ============================================================================


class TestInitialization:
    """Test IndexingOrchestrator initialization."""

    def test_init_with_all_dependencies(
        self,
        mock_embedding_factory,
        mock_document_loader,
        mock_file_handler,
        chunking_config,
        file_filter_config,
        query_config,
        mock_llm_configurer,
        mock_chunker_registry,
    ):
        """Test initialization with all dependencies."""
        orchestrator = IndexingOrchestrator(
            index_name="my_index",
            embedding_factory=mock_embedding_factory,
            document_loader=mock_document_loader,
            file_handler=mock_file_handler,
            chunking_config=chunking_config,
            file_filter_config=file_filter_config,
            query_config=query_config,
            llm_configurer=mock_llm_configurer,
            chunker_registry=mock_chunker_registry,
        )

        assert orchestrator.index_name == "my_index"
        assert orchestrator.storage_dir == Path("storage") / "my_index"
        assert orchestrator.embedding_factory == mock_embedding_factory
        assert orchestrator.document_loader == mock_document_loader
        assert orchestrator.file_handler == mock_file_handler
        assert orchestrator.chunking_config == chunking_config
        assert orchestrator.file_filter_config == file_filter_config
        assert orchestrator.query_config == query_config
        assert orchestrator.llm_configurer == mock_llm_configurer
        assert orchestrator.chunker_registry == mock_chunker_registry
        assert orchestrator.index is None  # Not initialized yet

    def test_init_without_chunker_registry_creates_default(
        self,
        mock_embedding_factory,
        mock_document_loader,
        mock_file_handler,
        chunking_config,
        file_filter_config,
        query_config,
    ):
        """Test that default ChunkerRegistry is created if not provided."""
        orchestrator = IndexingOrchestrator(
            index_name="test_index",
            embedding_factory=mock_embedding_factory,
            document_loader=mock_document_loader,
            file_handler=mock_file_handler,
            chunking_config=chunking_config,
            file_filter_config=file_filter_config,
            query_config=query_config,
            llm_configurer=None,  # Optional
            chunker_registry=None,  # Not provided
        )

        # Should create a default ChunkerRegistry
        assert isinstance(orchestrator.chunker_registry, ChunkerRegistry)


# ============================================================================
# Test: Setup
# ============================================================================


class TestSetup:
    """Test setup methods."""

    @patch("indexing.indexing_orchestrator.Settings")
    @patch("indexing.indexing_orchestrator.CodeAwareNodeParser")
    def test_setup_embeddings_and_parser(
        self, mock_parser_class, mock_settings, orchestrator
    ):
        """Test setup_embeddings_and_parser configures Settings correctly."""
        # Setup mock parser
        mock_parser_instance = Mock()
        mock_parser_class.from_config.return_value = mock_parser_instance

        # Call setup
        orchestrator.setup_embeddings_and_parser()

        # Verify embedding factory was used
        orchestrator.embedding_factory.create.assert_called_once()

        # Verify Settings was configured
        assert mock_settings.embed_model == orchestrator.embedding_factory.create.return_value

        # Verify CodeAwareNodeParser was created with correct config
        mock_parser_class.from_config.assert_called_once_with(
            chunking_config=orchestrator.chunking_config,
            registry=orchestrator.chunker_registry,
        )
        assert mock_settings.node_parser == mock_parser_instance


# ============================================================================
# Test: Index Management
# ============================================================================


class TestIndexManagement:
    """Test index management methods."""

    def test_index_exists_when_storage_dir_exists(self, orchestrator, tmp_path):
        """Test index_exists returns True when storage directory and docstore.json exist."""
        # Create temporary storage directory
        storage_dir = tmp_path / "storage" / "test_index"
        storage_dir.mkdir(parents=True)
        (storage_dir / "docstore.json").touch()

        orchestrator.storage_dir = storage_dir

        assert orchestrator.index_exists() is True

    def test_index_exists_when_storage_dir_missing(self, orchestrator, tmp_path):
        """Test index_exists returns False when storage directory doesn't exist."""
        orchestrator.storage_dir = tmp_path / "nonexistent"

        assert orchestrator.index_exists() is False

    def test_index_exists_when_docstore_missing(self, orchestrator, tmp_path):
        """Test index_exists returns False when docstore.json is missing."""
        storage_dir = tmp_path / "storage" / "test_index"
        storage_dir.mkdir(parents=True)
        # Don't create docstore.json

        orchestrator.storage_dir = storage_dir

        assert orchestrator.index_exists() is False

    @patch("indexing.indexing_orchestrator.load_index_from_storage")
    @patch("indexing.indexing_orchestrator.StorageContext")
    def test_load_existing_index_success(
        self, mock_storage_context_class, mock_load_index, orchestrator, tmp_path
    ):
        """Test load_existing_index successfully loads an index."""
        # Setup storage directory
        storage_dir = tmp_path / "storage" / "test_index"
        storage_dir.mkdir(parents=True)
        (storage_dir / "docstore.json").touch()
        orchestrator.storage_dir = storage_dir

        # Setup mocks
        mock_storage_context = Mock()
        mock_storage_context_class.from_defaults.return_value = mock_storage_context

        # Import real VectorStoreIndex for isinstance check
        from llama_index.core import VectorStoreIndex

        # Create mock index that passes isinstance check
        mock_index = MagicMock()
        mock_index.__class__ = VectorStoreIndex
        mock_index.docstore.docs = {"doc1": Mock(), "doc2": Mock()}
        mock_load_index.return_value = mock_index

        # Load index
        result = orchestrator.load_existing_index()

        # Verify
        assert result is True
        assert orchestrator.index == mock_index
        mock_storage_context_class.from_defaults.assert_called_once_with(
            persist_dir=str(storage_dir)
        )
        mock_load_index.assert_called_once_with(mock_storage_context)

    def test_load_existing_index_when_no_index_exists(self, orchestrator, tmp_path):
        """Test load_existing_index returns False when index doesn't exist."""
        orchestrator.storage_dir = tmp_path / "nonexistent"

        result = orchestrator.load_existing_index()

        assert result is False
        assert orchestrator.index is None

    @patch("indexing.indexing_orchestrator.load_index_from_storage")
    @patch("indexing.indexing_orchestrator.StorageContext")
    def test_load_existing_index_failure(
        self, mock_storage_context_class, mock_load_index, orchestrator, tmp_path
    ):
        """Test load_existing_index handles loading errors."""
        # Setup storage directory
        storage_dir = tmp_path / "storage" / "test_index"
        storage_dir.mkdir(parents=True)
        (storage_dir / "docstore.json").touch()
        orchestrator.storage_dir = storage_dir

        # Setup mocks to raise exception
        mock_load_index.side_effect = Exception("Load failed")

        # Load index
        result = orchestrator.load_existing_index()

        # Verify
        assert result is False
        assert orchestrator.index is None

    @patch("indexing.indexing_orchestrator.VectorStoreIndex")
    def test_create_new_index(self, mock_vector_store_index_class, orchestrator):
        """Test create_new_index creates a new empty index."""
        mock_index = Mock()
        mock_vector_store_index_class.from_documents.return_value = mock_index

        orchestrator.create_new_index()

        # Verify index was created with empty documents
        mock_vector_store_index_class.from_documents.assert_called_once_with([])
        assert orchestrator.index == mock_index

    def test_save_index_success(self, orchestrator, tmp_path):
        """Test save_index persists the index."""
        orchestrator.storage_dir = tmp_path / "storage" / "test_index"

        # Create mock index
        mock_index = Mock()
        mock_storage_context = Mock()
        mock_index.storage_context = mock_storage_context
        orchestrator.index = mock_index

        # Save index
        orchestrator.save_index()

        # Verify persist was called
        mock_storage_context.persist.assert_called_once_with(
            persist_dir=str(orchestrator.storage_dir)
        )

    def test_save_index_raises_when_index_not_initialized(self, orchestrator):
        """Test save_index raises AssertionError when index is None."""
        orchestrator.index = None

        with pytest.raises(AssertionError, match="Index must be initialized"):
            orchestrator.save_index()

    def test_delete_index_when_exists_and_confirmed(
        self, orchestrator, tmp_path, monkeypatch
    ):
        """Test delete_index removes storage directory when confirmed."""
        # Setup storage directory
        storage_dir = tmp_path / "storage" / "test_index"
        storage_dir.mkdir(parents=True)
        (storage_dir / "docstore.json").touch()
        orchestrator.storage_dir = storage_dir
        orchestrator.index = Mock()

        # Mock user input to confirm
        monkeypatch.setattr("builtins.input", lambda _: "y")

        # Delete index
        orchestrator.delete_index()

        # Verify directory was deleted
        assert not storage_dir.exists()
        assert orchestrator.index is None

    def test_delete_index_when_not_confirmed(
        self, orchestrator, tmp_path, monkeypatch
    ):
        """Test delete_index aborts when user doesn't confirm."""
        # Setup storage directory
        storage_dir = tmp_path / "storage" / "test_index"
        storage_dir.mkdir(parents=True)
        (storage_dir / "docstore.json").touch()
        orchestrator.storage_dir = storage_dir

        # Mock user input to decline
        monkeypatch.setattr("builtins.input", lambda _: "n")

        # Delete index
        orchestrator.delete_index()

        # Verify directory was not deleted
        assert storage_dir.exists()

    def test_delete_index_when_no_index_exists(self, orchestrator, tmp_path):
        """Test delete_index handles case when index doesn't exist."""
        orchestrator.storage_dir = tmp_path / "nonexistent"

        # Should not raise, just print message
        orchestrator.delete_index()

        # No assertion needed, just verify no exception was raised


# ============================================================================
# Test: Directory Scanning
# ============================================================================


class TestDirectoryScanning:
    """Test directory scanning methods."""

    @patch("indexing.indexing_orchestrator.SimpleDirectoryReader")
    def test_scan_directory_basic(self, mock_reader_class, orchestrator, tmp_path):
        """Test scan_directory returns sorted file paths."""
        # Setup mock reader
        mock_reader = Mock()
        mock_reader.input_files = [
            str(tmp_path / "file2.py"),
            str(tmp_path / "file1.py"),
            str(tmp_path / "file3.md"),
        ]
        mock_reader_class.return_value = mock_reader

        # Scan directory
        result = orchestrator.scan_directory(
            directory_path=tmp_path,
            recursive=True,
            file_extensions=[".py", ".md"],
            exclude_patterns=["*test*"],
        )

        # Verify SimpleDirectoryReader was called correctly
        mock_reader_class.assert_called_once_with(
            input_dir=str(tmp_path),
            recursive=True,
            required_exts=[".py", ".md"],
            exclude=["*test*"],
        )

        # Verify results are sorted and normalized
        assert len(result) == 3
        assert result == sorted(result)  # Verify sorting

    @patch("indexing.indexing_orchestrator.SimpleDirectoryReader")
    def test_scan_directory_with_no_exclusions(
        self, mock_reader_class, orchestrator, tmp_path
    ):
        """Test scan_directory with no exclusion patterns."""
        mock_reader = Mock()
        mock_reader.input_files = [str(tmp_path / "file.py")]
        mock_reader_class.return_value = mock_reader

        orchestrator.scan_directory(
            directory_path=tmp_path,
            recursive=False,
            file_extensions=[".py"],
            exclude_patterns=None,  # No exclusions
        )

        # Verify exclude was set to empty list
        call_kwargs = mock_reader_class.call_args[1]
        assert call_kwargs["exclude"] == []


# ============================================================================
# Test: Batch Processing
# ============================================================================


class TestBatchProcessing:
    """Test batch processing methods."""

    def test_process_file_batch_success(self, orchestrator):
        """Test process_file_batch processes files successfully."""
        # Setup mock index
        mock_index = Mock()
        orchestrator.index = mock_index

        # Setup mock document
        mock_doc = Mock()
        orchestrator.document_loader.load_document.return_value = mock_doc

        # Setup callbacks
        processed_callback = Mock()
        error_callback = Mock()

        # Process batch
        batch_files = ["file1.py", "file2.py"]
        orchestrator.process_file_batch(
            batch_files=batch_files,
            file_extensions=[".py"],
            exclude_patterns=None,
            processed_callback=processed_callback,
            error_callback=error_callback,
        )

        # Verify files were checked for indexing
        assert orchestrator.file_handler.should_index_file.call_count == 2

        # Verify documents were loaded
        assert orchestrator.document_loader.load_document.call_count == 2

        # Verify documents were inserted into index
        assert mock_index.insert.call_count == 2

        # Verify callbacks were called
        assert processed_callback.call_count == 2
        assert error_callback.call_count == 0

    def test_process_file_batch_with_filtered_files(self, orchestrator):
        """Test process_file_batch skips filtered files."""
        mock_index = Mock()
        orchestrator.index = mock_index

        # Mock file_handler to filter out file2
        def should_index_side_effect(file_path, *args):
            return "file2" not in file_path

        orchestrator.file_handler.should_index_file.side_effect = should_index_side_effect

        # Setup mock document
        mock_doc = Mock()
        orchestrator.document_loader.load_document.return_value = mock_doc

        # Process batch
        batch_files = ["file1.py", "file2_test.py"]
        orchestrator.process_file_batch(
            batch_files=batch_files,
            file_extensions=[".py"],
            exclude_patterns=["*test*"],
        )

        # Verify only file1 was loaded
        orchestrator.document_loader.load_document.assert_called_once_with("file1.py")
        mock_index.insert.assert_called_once()

    def test_process_file_batch_handles_errors(self, orchestrator):
        """Test process_file_batch handles processing errors."""
        mock_index = Mock()
        orchestrator.index = mock_index

        # Make document_loader raise an error for file2
        def load_document_side_effect(file_path):
            if "file2" in file_path:
                raise ValueError("Cannot load file2")
            return Mock()

        orchestrator.document_loader.load_document.side_effect = load_document_side_effect

        # Setup callbacks
        processed_callback = Mock()
        error_callback = Mock()

        # Process batch
        batch_files = ["file1.py", "file2.py"]
        orchestrator.process_file_batch(
            batch_files=batch_files,
            file_extensions=[".py"],
            exclude_patterns=None,
            processed_callback=processed_callback,
            error_callback=error_callback,
        )

        # Verify file1 succeeded, file2 failed
        assert processed_callback.call_count == 1
        assert error_callback.call_count == 1

        # Verify error callback was called with correct arguments
        error_callback.assert_called_once()
        call_args = error_callback.call_args[0]
        assert "file2.py" in call_args[0]
        assert "Cannot load file2" in call_args[1]

    def test_process_file_batch_raises_when_index_not_initialized(self, orchestrator):
        """Test process_file_batch raises AssertionError when index is None."""
        orchestrator.index = None

        with pytest.raises(AssertionError, match="Index must be initialized"):
            orchestrator.process_file_batch(
                batch_files=["file.py"],
                file_extensions=[".py"],
                exclude_patterns=None,
            )


# ============================================================================
# Test: High-Level Workflow
# ============================================================================


class TestHighLevelWorkflow:
    """Test high-level indexing workflow."""

    def test_index_directory_raises_when_directory_not_exists(self, orchestrator):
        """Test index_directory raises ValueError when directory doesn't exist."""
        with pytest.raises(ValueError, match="Directory not found"):
            orchestrator.index_directory(directory="/nonexistent/path")

    @patch("indexing.indexing_orchestrator.SimpleDirectoryReader")
    @patch("indexing.indexing_orchestrator.VectorStoreIndex")
    def test_index_directory_creates_new_index_when_not_exists(
        self, mock_vector_store_index_class, mock_reader_class, orchestrator, tmp_path
    ):
        """Test index_directory creates new index when it doesn't exist."""
        # Setup directory
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # Setup mock reader
        mock_reader = Mock()
        mock_reader.input_files = [str(test_dir / "file1.py")]
        mock_reader_class.return_value = mock_reader

        # Setup mock index
        mock_index = Mock()
        mock_index.docstore.docs = {}
        mock_vector_store_index_class.from_documents.return_value = mock_index

        # Setup document loader
        orchestrator.document_loader.load_document.return_value = Mock()

        # Index directory
        orchestrator.index_directory(
            directory=str(test_dir),
            file_extensions=[".py"],
            batch_size=10,
        )

        # Verify new index was created
        mock_vector_store_index_class.from_documents.assert_called_once_with([])
        assert orchestrator.index == mock_index

    @patch("indexing.indexing_orchestrator.SimpleDirectoryReader")
    @patch("indexing.indexing_orchestrator.load_index_from_storage")
    @patch("indexing.indexing_orchestrator.StorageContext")
    def test_index_directory_loads_existing_index(
        self, mock_storage_context_class, mock_load_index, mock_reader_class, orchestrator, tmp_path
    ):
        """Test index_directory loads existing index when it exists."""
        # Setup directory and storage
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        storage_dir = tmp_path / "storage" / "test_index"
        storage_dir.mkdir(parents=True)
        (storage_dir / "docstore.json").touch()
        orchestrator.storage_dir = storage_dir

        # Setup mock reader
        mock_reader = Mock()
        mock_reader.input_files = [str(test_dir / "file1.py")]
        mock_reader_class.return_value = mock_reader

        # Import real VectorStoreIndex for isinstance check
        from llama_index.core import VectorStoreIndex

        # Setup mock existing index that passes isinstance check
        mock_index = MagicMock()
        mock_index.__class__ = VectorStoreIndex
        mock_index.docstore.docs = {"doc1": Mock()}
        mock_index.storage_context.persist = Mock()  # Need this for save_index
        mock_load_index.return_value = mock_index

        # Setup document loader
        orchestrator.document_loader.load_document.return_value = Mock()

        # Index directory
        orchestrator.index_directory(
            directory=str(test_dir),
            file_extensions=[".py"],
            batch_size=10,
        )

        # Verify existing index was loaded
        mock_load_index.assert_called_once()
        assert orchestrator.index == mock_index

    @patch("indexing.indexing_orchestrator.SimpleDirectoryReader")
    def test_index_directory_with_no_files(
        self, mock_reader_class, orchestrator, tmp_path
    ):
        """Test index_directory handles case with no files to process."""
        # Setup directory
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # Setup mock reader with no files
        mock_reader = Mock()
        mock_reader.input_files = []
        mock_reader_class.return_value = mock_reader

        # Index directory
        orchestrator.index_directory(
            directory=str(test_dir),
            file_extensions=[".py"],
            batch_size=10,
        )

        # Verify no index was created (no files to process)
        assert orchestrator.index is None


# ============================================================================
# Test: Query Interface
# ============================================================================


class TestQueryInterface:
    """Test query interface."""

    def test_query_requires_llm_configurer(self, orchestrator):
        """Test query raises ValueError when LLM not configured."""
        orchestrator.index = Mock()  # Initialize index
        orchestrator.llm_configurer = None  # No LLM configured

        with pytest.raises(ValueError, match="LLM configuration required"):
            orchestrator.query(question="What does this code do?")

    def test_free_query_loads_index_if_not_loaded(self, orchestrator, capsys):
        """Test free_query loads index automatically if not loaded."""
        orchestrator.index = None
        orchestrator.index_exists = Mock(return_value=False)

        # Should print error and return early
        orchestrator.free_query(question="What does this code do?")

        captured = capsys.readouterr()
        assert "[X] No index available" in captured.out


# ============================================================================
# Test: Utility Functions
# ============================================================================


class TestUtilityFunctions:
    """Test utility functions."""

    def test_debug_log_when_enabled(self, monkeypatch, capsys):
        """Test debug_log prints message when APP_DEBUG=True."""
        monkeypatch.setenv("APP_DEBUG", "true")

        debug_log("Test message")

        captured = capsys.readouterr()
        assert "[DEBUG] Test message" in captured.out

    def test_debug_log_when_disabled(self, monkeypatch, capsys):
        """Test debug_log doesn't print when APP_DEBUG=False."""
        monkeypatch.setenv("APP_DEBUG", "false")

        debug_log("Test message")

        captured = capsys.readouterr()
        assert captured.out == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
