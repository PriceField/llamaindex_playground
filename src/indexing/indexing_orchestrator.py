"""Orchestrator for document indexing workflow.

This module provides the main orchestrator that coordinates the indexing process.
Follows SOLID principles:
- SRP: Only responsible for coordinating workflow
- OCP: Extensible via dependency injection
- DIP: Depends on abstractions (injected dependencies)
"""

import os
import shutil
import time
from datetime import datetime
from pathlib import Path

from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)

from config.chunking_config import ChunkingConfig
from config.file_filter_config import FileFilterConfig
from config.query_config import QueryConfig
from embedding.embedding_factory import EmbeddingFactory
from file_handlers import FileHandler
from code_chunking import CodeAwareNodeParser
from code_query_engine import CodeQueryEngine
from free_query_mode import FreeQueryEngine
from loading.document_loader import DocumentLoader
from llm.llm_configurer import LLMConfigurer
from strategies.chunking.registry import ChunkerRegistry


def debug_log(message: str) -> None:
    """Print debug message if debug mode is enabled."""
    debug = os.getenv("APP_DEBUG", "False").lower() == "true"
    if debug:
        print(f"[DEBUG] {message}")


class IndexingOrchestrator:
    """Orchestrates the document indexing workflow.

    Coordinates index management, batch processing, and progress tracking.
    Uses dependency injection for all components (DIP).
    Focused solely on orchestration (SRP).

    This class is the "thin coordinator" that replaces the DocumentIndexer god class.
    It delegates actual work to specialized components.
    """

    def __init__(
        self,
        index_name: str,
        embedding_factory: EmbeddingFactory,
        document_loader: DocumentLoader,
        file_handler: FileHandler,
        chunking_config: ChunkingConfig,
        file_filter_config: FileFilterConfig,
        query_config: QueryConfig,
        llm_configurer: LLMConfigurer | None = None,
        chunker_registry: ChunkerRegistry | None = None,
    ):
        """Initialize orchestrator with dependencies.

        Args:
            index_name: Name for this index (used for storage directory)
            embedding_factory: Factory for creating embeddings
            document_loader: Loader for documents with metadata
            file_handler: Handler for file operations
            chunking_config: Configuration for code chunking
            file_filter_config: Configuration for file filtering
            query_config: Configuration for query execution
            llm_configurer: Optional LLM configurer (required for AI query mode)
            chunker_registry: Optional registry for chunking strategies (Phase 2)
        """
        self.index_name = index_name
        self.storage_dir = Path("storage") / index_name

        # Injected dependencies (DIP compliance)
        self.embedding_factory = embedding_factory
        self.document_loader = document_loader
        self.file_handler = file_handler
        self.chunking_config = chunking_config
        self.file_filter_config = file_filter_config
        self.query_config = query_config
        self.llm_configurer = llm_configurer
        self.chunker_registry = chunker_registry if chunker_registry is not None else ChunkerRegistry()

        # Index state
        self.index: VectorStoreIndex | None = None
        self._llm_configured = False  # Track if LLM has been configured

    def setup_embeddings_and_parser(self) -> None:
        """Setup embeddings and code-aware node parser in LlamaIndex Settings.

        This configures the global Settings object used by LlamaIndex.
        """
        print("\n[*] Setting up embeddings and parser...")

        # Setup embeddings using factory
        Settings.embed_model = self.embedding_factory.create()

        # Setup code-aware node parser with chunking registry (Phase 2)
        Settings.node_parser = CodeAwareNodeParser.from_config(
            chunking_config=self.chunking_config,
            registry=self.chunker_registry,
        )
        print("[OK] Code-aware chunking enabled with strategy pattern")

    # ========================================================================
    # Index Management
    # ========================================================================

    def index_exists(self) -> bool:
        """Check if an index already exists.

        Returns:
            True if index exists, False otherwise
        """
        return self.storage_dir.exists() and (self.storage_dir / "docstore.json").exists()

    def load_existing_index(self) -> bool:
        """Load existing index from storage.

        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.index_exists():
            print(f"[i] No existing index found at {self.storage_dir}")
            return False

        print(f"\n[...] Loading existing index from {self.storage_dir}...")
        try:
            storage_context = StorageContext.from_defaults(persist_dir=str(self.storage_dir))
            loaded_index = load_index_from_storage(storage_context)

            # Type guard: ensure we loaded a VectorStoreIndex
            if isinstance(loaded_index, VectorStoreIndex):
                self.index = loaded_index
                print("[OK] Index loaded successfully")

                # Get index stats
                doc_count = len(self.index.docstore.docs)
                print(f"[#] Index contains {doc_count} documents")
                return True
            else:
                print("[X] Loaded index is not a VectorStoreIndex")
                return False

        except Exception as e:
            print(f"[X] Failed to load index: {e}")
            return False

    def create_new_index(self) -> None:
        """Create a new empty index.

        This initializes a new VectorStoreIndex with empty documents list.
        """
        print("\n[*] Creating new index...")
        self.index = VectorStoreIndex.from_documents([])
        print("[OK] Index created")

    def save_index(self) -> None:
        """Persist index to storage.

        Raises:
            AssertionError: If index is not initialized
        """
        assert self.index is not None, "Index must be initialized before saving"

        self.index.storage_context.persist(persist_dir=str(self.storage_dir))
        debug_log(f"Index saved to {self.storage_dir}")

    def delete_index(self) -> None:
        """Delete the index from storage.

        Prompts for confirmation before deletion.
        """
        if not self.index_exists():
            print(f"[i] No index to delete at {self.storage_dir}")
            return

        response = input(
            f"\n[!] Delete index at {self.storage_dir}? (y/n): "
        ).strip().lower()

        if response != 'y':
            print("[X] Aborted")
            return

        try:
            shutil.rmtree(self.storage_dir)
            self.index = None
            print("[OK] Index deleted")
        except Exception as e:
            print(f"[X] Failed to delete index: {e}")

    # ========================================================================
    # Directory Scanning
    # ========================================================================

    def scan_directory(
        self,
        directory_path: Path,
        recursive: bool,
        file_extensions: list[str] | None,
        exclude_patterns: list[str] | None,
    ) -> list[str]:
        """Scan directory for files matching criteria.

        Args:
            directory_path: Path to directory to scan
            recursive: Whether to search recursively
            file_extensions: List of extensions to include (e.g., ['.py', '.md'])
            exclude_patterns: Patterns to exclude (e.g., ['*test*', '__pycache__'])

        Returns:
            List of absolute file paths (sorted for determinism)
        """
        # Use SimpleDirectoryReader to scan
        reader = SimpleDirectoryReader(
            input_dir=str(directory_path),
            recursive=recursive,
            required_exts=file_extensions,
            exclude=exclude_patterns or [],
        )

        # Get all file paths and normalize them
        all_file_paths = sorted(
            set(str(Path(f).resolve()) for f in reader.input_files)
        )

        return all_file_paths

    # ========================================================================
    # Batch Processing
    # ========================================================================

    def process_file_batch(
        self,
        batch_files: list[str],
        file_extensions: list[str] | None,
        exclude_patterns: list[str] | None,
        processed_callback=None,
        error_callback=None,
    ) -> None:
        """Process a single batch of files.

        Args:
            batch_files: List of file paths in this batch
            file_extensions: Extensions to include (for filtering)
            exclude_patterns: Patterns to exclude (for filtering)
            processed_callback: Optional callback(file_path) when file processed successfully
            error_callback: Optional callback(file_path, error_message) when file fails

        Raises:
            AssertionError: If index is not initialized
        """
        assert self.index is not None, "Index must be initialized before processing batches"

        # Process each file in the batch
        for file_path in batch_files:
            try:
                # Check if file should be indexed
                if not self.file_handler.should_index_file(
                    file_path, file_extensions, exclude_patterns
                ):
                    debug_log(f"Skipped (filtered): {file_path}")
                    continue

                # Load document with enhanced metadata
                doc = self.document_loader.load_document(file_path)

                if doc:
                    # Insert into index
                    self.index.insert(doc)
                    debug_log(f"Processed: {file_path}")

                    # Notify callback
                    if processed_callback:
                        processed_callback(file_path)

            except Exception as e:
                print(f"\n[!] Error processing {Path(file_path).name}: {e}")
                debug_log(f"Error on {file_path}: {e}")

                # Notify error callback
                if error_callback:
                    error_callback(file_path, str(e))

        # Save index after batch
        self.save_index()

    # ========================================================================
    # High-Level Indexing Workflow
    # ========================================================================

    def index_directory(
        self,
        directory: str,
        file_extensions: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        recursive: bool = True,
        batch_size: int = 10,
        autosave_interval: int = 60,
        progress_tracker=None,
    ) -> None:
        """Index documents from a directory with batch processing.

        This is the main entry point for indexing a directory.

        Args:
            directory: Path to directory to index
            file_extensions: List of extensions to include (e.g., ['.py', '.md'])
            exclude_patterns: Patterns to exclude (e.g., ['*test*', '__pycache__'])
            recursive: Whether to search recursively
            batch_size: Number of files to process per batch
            autosave_interval: Seconds between auto-saves (unused in this impl, kept for compatibility)
            progress_tracker: Optional progress tracker instance

        Raises:
            ValueError: If directory does not exist
        """
        directory_path = Path(directory).resolve()

        if not directory_path.exists():
            raise ValueError(f"Directory not found: {directory_path}")

        # Print configuration
        self._print_indexing_config(
            directory_path, recursive, batch_size, autosave_interval,
            file_extensions, exclude_patterns
        )

        # Scan for files
        print("\n[...] Scanning directory...")
        all_file_paths = self.scan_directory(
            directory_path, recursive, file_extensions, exclude_patterns
        )

        # Filter already processed files (if progress tracker provided)
        if progress_tracker:
            pending_files = [
                f for f in all_file_paths if not progress_tracker.is_processed(f)
            ]
        else:
            pending_files = all_file_paths

        total_files = len(all_file_paths)
        pending_count = len(pending_files)

        print(f"[#] Found {total_files} files ({pending_count} pending)")

        if not pending_files:
            print("[i] No files to process")
            return

        # Initialize or load index
        if self.index is None:
            if self.index_exists():
                self.load_existing_index()
            else:
                self.create_new_index()

        # Process files in batches
        total_batches = (pending_count + batch_size - 1) // batch_size

        for batch_num, i in enumerate(range(0, pending_count, batch_size), start=1):
            batch_files = pending_files[i : i + batch_size]

            print(f"\n[...] Processing batch {batch_num}/{total_batches}...")

            # Define callbacks for progress tracking
            def on_processed(file_path: str) -> None:
                if progress_tracker:
                    progress_tracker.mark_processed(file_path)

            def on_error(file_path: str, error_msg: str) -> None:
                if progress_tracker:
                    progress_tracker.mark_error(file_path, error_msg)

            # Process the batch
            self.process_file_batch(
                batch_files,
                file_extensions,
                exclude_patterns,
                processed_callback=on_processed,
                error_callback=on_error,
            )

            # Update progress tracker
            if progress_tracker:
                progress_tracker.data["progress"]["last_batch_at"] = datetime.now().isoformat()
                progress_tracker.save()

            # Show progress
            processed_so_far = (
                progress_tracker.data["progress"]["processed_files"]
                if progress_tracker
                else (batch_num * batch_size)
            )
            print(f"   Batch {batch_num}/{total_batches} complete ({processed_so_far}/{total_files} files)")

        print("\n[OK] Indexing complete!")
        print(f"[#] Total files: {total_files}")
        print(f"[#] Storage: {self.storage_dir}")

    def _print_indexing_config(
        self,
        directory_path: Path,
        recursive: bool,
        batch_size: int,
        autosave_interval: int,
        file_extensions: list[str] | None,
        exclude_patterns: list[str] | None,
    ) -> None:
        """Print indexing configuration summary.

        Args:
            directory_path: Directory being indexed
            recursive: Whether scanning recursively
            batch_size: Files per batch
            autosave_interval: Autosave interval in seconds
            file_extensions: File extensions filter
            exclude_patterns: Exclusion patterns
        """
        print(f"\n[DIR] Indexing directory: {directory_path}")
        print(f"   Recursive: {recursive}")
        print(f"   Batch size: {batch_size} files")
        print(f"   Auto-save: every {autosave_interval} seconds")
        if file_extensions:
            print(f"   File types: {', '.join(file_extensions)}")
        if exclude_patterns:
            print(f"   Excluding: {', '.join(exclude_patterns)}")

    # ========================================================================
    # Query Interface
    # ========================================================================

    def query(
        self,
        question: str,
        top_k: int | None = None,
        language: str | None = None,
        category: str | None = None,
    ) -> None:
        """Query the index with code-aware search using LLM.

        This method uses LLM for response generation (AI mode).
        Requires LLM configuration (llm_configurer must be provided).

        Args:
            question: Question to ask
            top_k: Number of relevant documents to retrieve (uses config default if None)
            language: Optional filter by programming language (e.g., 'python', 'javascript')
            category: Optional filter by category (e.g., 'code', 'documentation')

        Raises:
            AssertionError: If index is not loaded
            ValueError: If LLM is not configured
        """
        # Ensure index is loaded
        if self.index is None:
            if not self.load_existing_index():
                print("[X] No index available. Please index documents first.")
                return

        assert self.index is not None, "Index must be loaded"

        # Ensure LLM is configured for AI mode
        if self.llm_configurer is None:
            raise ValueError(
                "LLM configuration required for AI query mode. "
                "Use free_query() for retrieval-only mode (no LLM)."
            )

        # Configure LLM once
        if not self._llm_configured:
            self.llm_configurer.configure()
            self._llm_configured = True

        # Determine top_k
        top_k_value: int = top_k if top_k is not None else self.query_config.code_similarity_top_k

        print(f"\n[?] Query: {question}")
        if language:
            print(f"   Language filter: {language}")
        if category:
            print(f"   Category filter: {category}")
        print(f"   Retrieving top {top_k_value} relevant sources...")

        try:
            # Create code-aware query engine
            code_query_engine = CodeQueryEngine(self.index, self.query_config)
            query_engine = code_query_engine.create_query_engine(
                similarity_top_k=top_k_value,
                language_filter=language,
                category_filter=category,
            )

            print("\n... Thinking...")
            response = query_engine.query(question)

            # Format and display response with enhanced sources
            formatted = code_query_engine.format_response_with_sources(response, top_k_value)
            print(f"\n{formatted}\n")

        except Exception as e:
            print(f"\n[X] Query failed: {e}")
            debug_log(f"Error details: {str(e)}")
            raise

    def free_query(self, question: str, top_k: int | None = None) -> None:
        """Query the index with FREE retrieval-only mode (no LLM costs).

        This method uses only local vector search with embeddings.
        No LLM API calls are made, so there are ZERO costs.

        Args:
            question: Question to search for
            top_k: Number of relevant documents to retrieve (uses config default if None)

        Raises:
            AssertionError: If index is not loaded
        """
        # Ensure index is loaded
        if self.index is None:
            if not self.load_existing_index():
                print("[X] No index available. Please index documents first.")
                return

        assert self.index is not None, "Index must be loaded"

        # Determine top_k
        top_k_value: int = top_k if top_k is not None else self.query_config.code_similarity_top_k

        print(f"\n[?] Query (FREE MODE): {question}")
        print(f"   Retrieving top {top_k_value} relevant sources...")
        print(f"   💰 Cost: $0.00 (No LLM calls)")

        try:
            # Create FREE query engine (no LLM)
            # Note: FreeQueryEngine expects IndexerConfig, but we pass query_config
            # which has the required code_similarity_top_k attribute
            free_engine = FreeQueryEngine(self.index, self.query_config)  # type: ignore

            print("\n... Searching vector database...")
            results = free_engine.query(question, top_k_value)

            # Format and display results
            formatted = free_engine.format_results(results)
            print(f"\n{formatted}\n")

        except Exception as e:
            print(f"\n[X] Query failed: {e}")
            debug_log(f"Error details: {str(e)}")
            raise
