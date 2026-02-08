"""LlamaIndex developer tool for document indexing and querying with code-aware capabilities."""
import os
import sys
import json
import time
import signal
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from llama_index.core import (
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Document,
)
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Import code-aware modules
from config import IndexerConfig
from file_handlers import FileHandler
from code_extractors import CodeMetadataExtractor
from code_chunking import CodeAwareNodeParser
from code_query_engine import CodeQueryEngine

# Load environment variables
load_dotenv()

# Debug mode
DEBUG = os.getenv("APP_DEBUG", "False").lower() == "true"


def debug_log(message):
    """Print debug message if debug mode is enabled."""
    if DEBUG:
        print(f"[DEBUG] {message}")


def validate_environment(require_llm: bool = True):
    """Validate required environment variables.

    Args:
        require_llm: If True, validate API_KEY and API_BASE are set

    Raises:
        ValueError: If required environment variables are missing
    """
    if require_llm:
        api_key = os.getenv("API_KEY")
        if not api_key:
            raise ValueError(
                "API_KEY is required in .env file\n"
                "Copy .env.example to .env and add your API key\n"
                "Or run with --no-llm flag for indexing-only mode"
            )

        api_base = os.getenv("API_BASE")
        if not api_base:
            raise ValueError(
                "API_BASE is required in .env file\n"
                "Copy .env.example to .env and configure your API endpoint"
            )

        debug_log(f"Environment validated: API_KEY and API_BASE present")


class CustomOpenAI(OpenAI):
    """Custom OpenAI LLM that bypasses model validation for custom endpoints."""

    def __init__(self, *args, **kwargs):
        # Temporarily store the custom model name
        custom_model = kwargs.get('model', 'gpt-3.5-turbo')

        # Use a valid OpenAI model name for initialization to pass validation
        kwargs['model'] = 'gpt-3.5-turbo'

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Override with the actual custom model name after initialization
        self._model = custom_model
        debug_log(f"CustomOpenAI initialized with model: {custom_model}")


# ============================================================================
# CORE INDEXER CLASSES - Production Stable Code
# ============================================================================

class ProgressTracker:
    """Track indexing progress with resume capability."""

    def __init__(self, storage_dir: Path):
        """Initialize progress tracker.

        Args:
            storage_dir: Directory where progress.json will be saved
        """
        self.storage_dir = storage_dir
        self.progress_file = storage_dir / "progress.json"
        self.data: dict = self._create_empty_data()

    def _create_empty_data(self) -> dict:
        """Create empty progress data structure.

        Returns:
            Empty progress data dictionary
        """
        return {
            "version": "1.0",
            "status": "in_progress",
            "started_at": datetime.now().isoformat(),
            "last_updated": None,
            "config": {},
            "progress": {
                "total_files": 0,
                "processed_files": 0,
                "processed_file_paths": [],
                "last_batch_at": None,
                "error_files": []
            }
        }

    def load(self) -> dict:
        """Load existing progress or create new.

        Returns:
            Progress data dictionary
        """
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            debug_log(f"Loaded progress: {self.data['progress']['processed_files']} files processed")
        else:
            self.data = self._create_empty_data()
            debug_log("Created new progress tracker")
        return self.data

    def save(self):
        """Save current progress to disk."""
        self.data["last_updated"] = datetime.now().isoformat()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)
        debug_log(f"Progress saved: {self.data['progress']['processed_files']} files")

    def mark_processed(self, file_path: str):
        """Mark a file as processed.

        Args:
            file_path: Path of the processed file
        """
        if file_path not in self.data["progress"]["processed_file_paths"]:
            self.data["progress"]["processed_file_paths"].append(file_path)
            self.data["progress"]["processed_files"] += 1

    def is_processed(self, file_path: str) -> bool:
        """Check if file was already processed.

        Args:
            file_path: Path to check

        Returns:
            True if file was processed, False otherwise
        """
        return file_path in self.data["progress"]["processed_file_paths"]

    def mark_error(self, file_path: str, error: str):
        """Mark a file as having an error.

        Args:
            file_path: Path of the file with error
            error: Error message
        """
        self.data["progress"]["error_files"].append({
            "path": file_path,
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        })

    def mark_complete(self):
        """Mark indexing as complete."""
        self.data["status"] = "completed"
        self.data["progress"]["last_batch_at"] = datetime.now().isoformat()
        self.save()


class DocumentIndexer:
    """Index documents from folders/repos with progress tracking and persistence."""

    def __init__(self, index_name: str = "default", require_llm: bool = True):
        """Initialize the indexer.

        Args:
            index_name: Name for this index (for storage)
            require_llm: If True, validate and require LLM configuration (default: True)
                        Set to False for indexing-only mode
        """
        self.index_name = index_name
        self.storage_dir = Path("storage") / index_name
        self.index: VectorStoreIndex | None = None
        self.require_llm = require_llm

        # Validate environment variables before proceeding
        validate_environment(require_llm=require_llm)

        # Initialize code-aware components
        self.config = IndexerConfig()
        self.file_handler = FileHandler(self.config)
        self.code_extractor = CodeMetadataExtractor(self.config)

        self._setup_llm_and_embeddings()

    def _setup_llm_and_embeddings(self):
        """Setup LLM and embeddings from environment."""
        print("\n[*] Setting up LLM and embeddings...")

        # Setup LLM if required (validation already ensured API_KEY is present)
        if self.require_llm:
            api_token = os.getenv("API_KEY")
            api_base = os.getenv("API_BASE", "https://api.rdsec.trendmicro.com/prod/aiendpoint/v1")
            model = os.getenv("MODEL_NAME", "claude-sonnet-4-5-20250929")

            Settings.llm = CustomOpenAI(
                api_key=api_token,
                api_base=api_base,
                model=model,
                temperature=0.7,
            )
            print(f"[OK] LLM configured: {model}")
        else:
            print("[*] Indexing-only mode: LLM not configured")

        # Always use local embeddings for reliability
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )
        print("[OK] Embeddings configured: BAAI/bge-small-en-v1.5")

        # Setup code-aware node parser
        Settings.node_parser = CodeAwareNodeParser(self.config)
        print("[OK] Code-aware chunking enabled")

    def _load_document_with_metadata(self, file_path: str) -> Document | None:
        """Load a document with enhanced code-aware metadata.

        Args:
            file_path: Path to the file

        Returns:
            Document with metadata or None if error
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Get basic file metadata
            file_metadata = self.file_handler.get_file_metadata(file_path)

            # Extract code-specific metadata if it's a code file
            if file_metadata["category"] == "code":
                code_metadata = self.code_extractor.extract_metadata(
                    file_path, content, file_metadata["language"]
                )
                file_metadata.update(code_metadata)

            # Create document with metadata
            doc = Document(
                text=content,
                metadata=file_metadata,
            )

            return doc

        except Exception as e:
            debug_log(f"Error loading {file_path}: {e}")
            return None

    def index_exists(self) -> bool:
        """Check if an index already exists."""
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
                print(f"[X] Loaded index is not a VectorStoreIndex")
                return False
        except Exception as e:
            print(f"[X] Failed to load index: {e}")
            return False

    def _print_indexing_config(
        self,
        directory_path: Path,
        recursive: bool,
        batch_size: int,
        autosave_interval: int,
        file_extensions: list[str] | None,
        exclude_patterns: list[str] | None
    ) -> None:
        """Print indexing configuration."""
        print(f"\n[DIR] Indexing directory: {directory_path}")
        print(f"   Recursive: {recursive}")
        print(f"   Batch size: {batch_size} files")
        print(f"   Auto-save: every {autosave_interval} seconds")
        if file_extensions:
            print(f"   File types: {', '.join(file_extensions)}")
        if exclude_patterns:
            print(f"   Excluding: {', '.join(exclude_patterns)}")

    def _save_config_to_tracker(
        self,
        tracker: ProgressTracker,
        directory_path: Path,
        file_extensions: list[str] | None,
        exclude_patterns: list[str] | None,
        recursive: bool,
        batch_size: int,
        autosave_interval: int
    ) -> None:
        """Save configuration to progress tracker."""
        tracker.data["config"] = {
            "directory": str(directory_path),
            "file_extensions": file_extensions,
            "exclude_patterns": exclude_patterns,
            "recursive": recursive,
            "batch_size": batch_size,
            "autosave_interval": autosave_interval
        }

    def _print_completion_summary(
        self,
        tracker: ProgressTracker,
        total_files: int
    ) -> None:
        """Print indexing completion summary."""
        print("\n[OK] Indexing complete!")
        print(f"[#] Index stats:")
        print(f"   Total files: {total_files}")
        print(f"   Processed: {tracker.data['progress']['processed_files']}")
        if tracker.data['progress']['error_files']:
            print(f"   Errors: {len(tracker.data['progress']['error_files'])}")
        print(f"   Storage: {self.storage_dir}")

    def _scan_files(
        self,
        directory_path: Path,
        recursive: bool,
        file_extensions: list[str] | None,
        exclude_patterns: list[str] | None,
        tracker: ProgressTracker
    ) -> tuple[list[str], list[str]]:
        """Scan directory for files and filter out already processed ones.

        Returns:
            Tuple of (all_file_paths, pending_files)
        """
        # Scan directory for all matching files
        reader = SimpleDirectoryReader(
            input_dir=str(directory_path),
            recursive=recursive,
            required_exts=file_extensions,
            exclude=exclude_patterns or [],
        )

        # Get all file paths
        all_file_paths = []
        for file_path in reader.iter_data():
            all_file_paths.append(file_path[0] if isinstance(file_path, tuple) else file_path)

        # Sort for deterministic ordering
        all_file_paths = sorted(set(str(Path(f).resolve()) for f in reader.input_files))

        # Filter out already processed files
        pending_files = [f for f in all_file_paths if not tracker.is_processed(f)]

        # Update totals
        tracker.data["progress"]["total_files"] = len(all_file_paths)
        tracker.save()

        return all_file_paths, pending_files

    def _confirm_indexing(
        self,
        all_file_count: int,
        pending_file_count: int,
        processed_count: int
    ) -> bool:
        """Prompt user to confirm indexing operation.

        Returns:
            True if user confirms, False if user aborts
        """
        print(f"[OK] Found {all_file_count} total files")

        if processed_count > 0:
            print(f"[OK] Already indexed: {processed_count} files")
            print(f"[OK] Pending: {pending_file_count} files")

            if pending_file_count > 0:
                response = input("\n[>] Resume from checkpoint? (y/n): ").strip().lower()
                if response != 'y':
                    print("[X] Aborted")
                    return False
            else:
                print("[i] No files to index")
                return False
        else:
            if pending_file_count == 0:
                print("[i] No files to index")
                return False

            response = input(f"\n[>] Start indexing {pending_file_count} files? (y/n): ").strip().lower()
            if response != 'y':
                print("[X] Aborted")
                return False

        return True

    def _setup_signal_handler(self, tracker: ProgressTracker) -> None:
        """Setup SIGINT handler for graceful shutdown on Ctrl+C.

        Side effects:
            Registers signal handler that will sys.exit(0) on SIGINT
        """
        def signal_handler(sig, frame):
            print("\n\n[PAUSE]  Interrupted by user")
            print("[SAVE] Saving progress...")
            if self.index is not None:
                self.index.storage_context.persist(persist_dir=str(self.storage_dir))
            tracker.save()
            print(f"[OK] Progress saved! {tracker.data['progress']['processed_files']}/{tracker.data['progress']['total_files']} files indexed")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

    def _process_file_batch(
        self,
        batch_files: list[str],
        batch_num: int,
        total_batches: int,
        total_files: int,
        file_extensions: list[str] | None,
        exclude_patterns: list[str] | None,
        tracker: ProgressTracker,
        last_save_time: float,
        autosave_interval: int
    ) -> float:
        """Process a single batch of files.

        Returns:
            Updated last_save_time
        """
        assert self.index is not None, "Index must be initialized before processing batches"

        # Process each file in the batch
        for file_path in batch_files:
            try:
                # Check if file should be indexed
                if not self.file_handler.should_index_file(file_path, file_extensions, exclude_patterns):
                    debug_log(f"Skipped (filtered): {file_path}")
                    continue

                # Load document with enhanced metadata
                doc = self._load_document_with_metadata(file_path)

                if doc:
                    # Insert into index
                    self.index.insert(doc)

                    # Mark as processed
                    tracker.mark_processed(file_path)
                    debug_log(f"Processed: {file_path}")

            except Exception as e:
                print(f"\n[!]  Error processing {Path(file_path).name}: {e}")
                tracker.mark_error(file_path, str(e))
                debug_log(f"Error on {file_path}: {e}")

        # Auto-save after batch
        self.index.storage_context.persist(persist_dir=str(self.storage_dir))
        tracker.data["progress"]["last_batch_at"] = datetime.now().isoformat()
        tracker.save()

        # Show progress
        print(f"   Batch {batch_num}/{total_batches} complete ({tracker.data['progress']['processed_files']}/{total_files} files)")

        # Time-based auto-save check
        current_time = time.time()
        if current_time - last_save_time > autosave_interval:
            tracker.save()
            last_save_time = current_time
            debug_log("Time-based auto-save triggered")

        return last_save_time

    def index_directory(
        self,
        directory: str,
        file_extensions: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        recursive: bool = True,
        batch_size: int = 10,
        autosave_interval: int = 60,
    ):
        """Index documents from a directory with batch processing and auto-save.

        Args:
            directory: Path to directory to index
            file_extensions: List of extensions to include (e.g., ['.py', '.md'])
            exclude_patterns: Patterns to exclude (e.g., ['*test*', '__pycache__'])
            recursive: Whether to search recursively
            batch_size: Number of files to process per batch
            autosave_interval: Seconds between auto-saves
        """
        directory_path = Path(directory).resolve()

        if not directory_path.exists():
            print(f"[X] Directory not found: {directory_path}")
            return

        self._print_indexing_config(
            directory_path, recursive, batch_size, autosave_interval,
            file_extensions, exclude_patterns
        )

        # Initialize progress tracker
        tracker = ProgressTracker(self.storage_dir)
        tracker.load()

        # Save configuration
        self._save_config_to_tracker(
            tracker, directory_path, file_extensions, exclude_patterns,
            recursive, batch_size, autosave_interval
        )

        print("\n[?] Scanning for files...")

        try:
            # Scan directory for all matching files
            all_file_paths, pending_files = self._scan_files(
                directory_path, recursive, file_extensions, exclude_patterns, tracker
            )

            # Show status and confirm
            processed_count = tracker.data["progress"]["processed_files"]
            if not self._confirm_indexing(len(all_file_paths), len(pending_files), processed_count):
                return

            # Load or create index
            if self.index_exists() and self.index is None:
                self.load_existing_index()

            if self.index is None:
                # Create empty index for incremental insertion
                self.index = VectorStoreIndex(nodes=[], show_progress=False)
                debug_log("Created new empty index")

            # Type assertion: index must be non-None at this point
            assert self.index is not None, "Index must be initialized"

            # Setup signal handler for graceful Ctrl+C
            self._setup_signal_handler(tracker)

            # Process files in batches
            print("\n[*] Indexing in progress...")
            total_batches = (len(pending_files) + batch_size - 1) // batch_size
            last_save_time = time.time()

            for batch_idx in range(0, len(pending_files), batch_size):
                batch_files = pending_files[batch_idx:batch_idx + batch_size]
                batch_num = (batch_idx // batch_size) + 1
                last_save_time = self._process_file_batch(
                    batch_files, batch_num, total_batches, len(all_file_paths),
                    file_extensions, exclude_patterns, tracker, last_save_time, autosave_interval
                )

            # Mark complete
            tracker.mark_complete()

            # Show summary
            self._print_completion_summary(tracker, len(all_file_paths))

        except Exception as e:
            print(f"\n[X] Error during indexing: {e}")
            debug_log(f"Error details: {str(e)}")
            # Save progress before exiting
            if 'tracker' in locals():
                tracker.save()
            raise

    def query(self, question: str, top_k: int | None = None,
              language: str | None = None,
              category: str | None = None):
        """Query the index with code-aware search.

        Args:
            question: Question to ask
            top_k: Number of relevant documents to retrieve (uses config default if None)
            language: Optional filter by programming language (e.g., 'python', 'javascript')
            category: Optional filter by category (e.g., 'code', 'documentation')
        """
        if self.index is None:
            if not self.load_existing_index():
                print("[X] No index available. Please index documents first.")
                return

        # Type assertion: index must be non-None at this point
        assert self.index is not None, "Index must be loaded"

        # Ensure top_k is an int
        top_k_value: int = top_k if top_k is not None else self.config.code_similarity_top_k

        print(f"\n[?] Query: {question}")
        if language:
            print(f"   Language filter: {language}")
        if category:
            print(f"   Category filter: {category}")
        print(f"   Retrieving top {top_k_value} relevant sources...")

        try:
            # Create code-aware query engine
            code_query_engine = CodeQueryEngine(self.index, self.config)
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

    def delete_index(self):
        """Delete the index from storage."""
        if not self.index_exists():
            print(f"[i] No index to delete at {self.storage_dir}")
            return

        response = input(f"\n[!]  Delete index at {self.storage_dir}? (y/n): ").strip().lower()
        if response != 'y':
            print("[X] Aborted")
            return

        try:
            shutil.rmtree(self.storage_dir)
            self.index = None
            print("[OK] Index deleted")
        except Exception as e:
            print(f"[X] Failed to delete index: {e}")


# ============================================================================
# INTERACTIVE MODE - Main Entry Point
# ============================================================================

def list_available_indexes() -> list[str]:
    """List all available index names in the storage directory.

    Returns:
        List of index names
    """
    storage_path = Path("storage")
    if not storage_path.exists():
        return []

    indexes = []
    for item in storage_path.iterdir():
        if item.is_dir() and (item / "docstore.json").exists():
            indexes.append(item.name)

    return sorted(indexes)


def select_index_by_number(available_indexes: list[str]) -> str | None:
    """Display numbered list of indexes and let user select or create new.

    Args:
        available_indexes: List of existing index names

    Returns:
        Selected or created index name, or None if cancelled
    """
    if available_indexes:
        print("\nAvailable indexes:")
        for idx, name in enumerate(available_indexes, 1):
            print(f"  {idx}. {name}")
        print(f"  {len(available_indexes) + 1}. Create new index")
    else:
        print("\n[i] No existing indexes found")
        print("  1. Create new index")

    choice = input("\nYour choice (number or name): ").strip()

    # Check if user entered a number
    if choice.isdigit():
        choice_num = int(choice)
        if 1 <= choice_num <= len(available_indexes):
            return available_indexes[choice_num - 1]
        elif choice_num == len(available_indexes) + 1:
            # Create new index
            new_name = input("\nNew index name: ").strip()
            if not new_name:
                print("[X] No name provided")
                return None
            confirm = input(f"Create index '{new_name}'? (y/n): ").strip().lower()
            if confirm == 'y':
                return new_name
            else:
                print("[X] Cancelled")
                return None
        else:
            print("[X] Invalid choice")
            return None
    else:
        # User typed a name directly
        if not choice:
            print("[X] No name provided")
            return None
        if choice in available_indexes:
            return choice
        # New index name
        confirm = input(f"Create new index '{choice}'? (y/n): ").strip().lower()
        if confirm == 'y':
            return choice
        else:
            print("[X] Cancelled")
            return None


def prompt_for_filters(current_language: str | None = None,
                      current_category: str | None = None,
                      current_top_k: int | None = None) -> tuple[str | None, str | None, int | None]:
    """Prompt user for query filters with current values shown.

    Args:
        current_language: Current language filter
        current_category: Current category filter
        current_top_k: Current top_k value

    Returns:
        Tuple of (language, category, top_k)
    """
    print("\n[FILTER SETTINGS]")

    # Language filter
    lang_prompt = f"Filter by language (current: {current_language or 'all'}): "
    language_input = input(lang_prompt).strip()
    language = language_input if language_input else current_language

    # Category filter
    cat_prompt = f"Filter by category (current: {current_category or 'all'}): "
    category_input = input(cat_prompt).strip()
    category = category_input if category_input else current_category

    # Top K
    top_k_prompt = f"Number of sources (current: {current_top_k or 5}): "
    top_k_input = input(top_k_prompt).strip()
    if top_k_input and top_k_input.isdigit():
        top_k = int(top_k_input)
    else:
        top_k = current_top_k

    return (language, category, top_k)


def show_all_indexes_info() -> None:
    """Display detailed information about all available indexes."""
    available_indexes = list_available_indexes()

    if not available_indexes:
        print("\n[i] No indexes found")
        return

    print("\n" + "=" * 70)
    print("ALL INDEXES")
    print("=" * 70)

    for idx_name in available_indexes:
        storage_dir = Path("storage") / idx_name
        print(f"\n[{idx_name}]")
        print(f"  Path: {storage_dir}")

        # Try to get document count
        try:
            docstore_file = storage_dir / "docstore.json"
            if docstore_file.exists():
                with open(docstore_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    doc_count = len(data.get('docstore/data', {}))
                    print(f"  Documents: {doc_count}")
            else:
                print(f"  Status: Empty/Invalid")
        except Exception as e:
            print(f"  Status: Error reading ({e})")

    print("=" * 70)


def index_folder_handler(indexer: DocumentIndexer) -> None:
    """Handle folder indexing with all configuration prompts.

    Args:
        indexer: DocumentIndexer instance to use for indexing
    """
    # Folder path
    folder = input("\nFolder path to index: ").strip()
    if not folder:
        print("[X] No folder specified")
        return

    # File types
    file_types = input("File extensions (comma-separated, e.g., .py,.md) or Enter for all: ").strip()
    extensions = [ext.strip() for ext in file_types.split(",")] if file_types else None

    # Recursive
    recursive = input("Recursive? (y/n, default: y): ").strip().lower() != 'n'

    # Exclude patterns
    exclude = input("Exclude patterns (comma-separated, e.g., *test*,__pycache__) or Enter for none: ").strip()
    exclude_patterns = [p.strip() for p in exclude.split(",")] if exclude else None

    # Batch configuration
    batch_size_str = input(f"Batch size (files per batch, default: 10): ").strip()
    if batch_size_str and batch_size_str.isdigit():
        batch_size = int(batch_size_str)
    else:
        try:
            batch_size = int(os.getenv('BATCH_SIZE', '10'))
        except (ValueError, TypeError):
            batch_size = 10

    autosave_str = input(f"Auto-save interval (seconds, default: 60): ").strip()
    if autosave_str and autosave_str.isdigit():
        autosave_interval = int(autosave_str)
    else:
        try:
            autosave_interval = int(os.getenv('AUTOSAVE_INTERVAL', '60'))
        except (ValueError, TypeError):
            autosave_interval = 60

    # Perform indexing
    indexer.index_directory(folder, extensions, exclude_patterns, recursive, batch_size, autosave_interval)


def query_mode(indexer: DocumentIndexer) -> None:
    """Enter continuous query mode with persistent filter settings.

    Args:
        indexer: DocumentIndexer instance to query
    """
    # Check if index exists
    if not indexer.index_exists():
        print("\n[X] Cannot enter query mode: Index does not exist")
        print("[i] Please index some documents first")
        return

    # Load index if needed
    if indexer.index is None:
        if not indexer.load_existing_index():
            print("\n[X] Failed to load index")
            return

    print("\n" + "=" * 70)
    print(f"QUERY MODE - Index: {indexer.index_name}")
    print("=" * 70)
    print("[i] Commands: 'back' or 'exit' to return, '/filter' to change filters")
    print()

    # Prompt for filters once
    language, category, top_k = prompt_for_filters()

    print("\n[OK] Filter settings saved for this session")
    print(f"   Language: {language or 'all'}")
    print(f"   Category: {category or 'all'}")
    print(f"   Top K: {top_k or 5}")
    print()

    # Continuous question loop
    while True:
        question = input("\nYour question: ").strip()

        # Check for exit commands (case-insensitive)
        if question.lower() in ['back', 'exit']:
            print("[OK] Exiting query mode...")
            break

        # Check for filter change command
        if question.lower() == '/filter':
            language, category, top_k = prompt_for_filters(language, category, top_k)
            print("\n[OK] Filter settings updated")
            print(f"   Language: {language or 'all'}")
            print(f"   Category: {category or 'all'}")
            print(f"   Top K: {top_k or 5}")
            continue

        if not question:
            print("[X] No question specified")
            continue

        # Execute query with persistent filters
        try:
            indexer.query(question, top_k, language, category)
        except Exception as e:
            print(f"\n[X] Query failed: {e}")
            debug_log(f"Query error: {str(e)}")


def index_workspace(indexer: DocumentIndexer) -> None:
    """Index workspace menu - operations on selected index.

    Args:
        indexer: DocumentIndexer instance for the selected index
    """
    while True:
        print("\n" + "=" * 70)
        print(f"INDEX WORKSPACE: {indexer.index_name}")
        print("=" * 70)
        print("OPTIONS:")
        print("  1. Ask questions (query mode)")
        print("  2. Index a folder")
        print("  3. Show index info")
        print("  4. Back to main menu")
        print("=" * 70)

        choice = input("\nYour choice: ").strip()

        if choice == "1":
            # Enter query mode
            query_mode(indexer)

        elif choice == "2":
            # Index a folder
            index_folder_handler(indexer)

        elif choice == "3":
            # Show info for current index
            print(f"\n[INFO] Current Index: {indexer.index_name}")
            if indexer.index_exists():
                print(f"[OK] Index exists at: {indexer.storage_dir}")
                if indexer.index is None:
                    indexer.load_existing_index()

                # Try to show document count
                if indexer.index is not None:
                    doc_count = len(indexer.index.docstore.docs)
                    print(f"[OK] Documents: {doc_count}")
            else:
                print(f"[i] No index found at: {indexer.storage_dir}")

        elif choice == "4":
            # Back to main menu
            print("[OK] Returning to main menu...")
            break

        else:
            print("[X] Invalid choice")


def main_menu() -> None:
    """Main menu - index selection and management with direct access to common operations."""
    print("=" * 70)
    print("[BOOK] LLAMAINDEX DEVELOPER TOOL")
    print("=" * 70)

    while True:
        print("\n" + "=" * 70)
        print("MAIN MENU")
        print("=" * 70)
        print("OPTIONS:")
        print("  1. Index a folder (create new or add to existing)")
        print("  2. Query an index (ask questions)")
        print("  3. Work with an index (full workspace)")
        print("  4. Show all indexes")
        print("  5. Delete an index")
        print("  6. Exit")
        print("=" * 70)

        choice = input("\nYour choice: ").strip()

        if choice == "1":
            # Index a folder - select/create index then index
            available_indexes = list_available_indexes()
            print("\n[FOLDER] Select or create an index for your folder:")
            index_name = select_index_by_number(available_indexes)

            if index_name:
                indexer = DocumentIndexer(index_name)

                # Load existing index if available
                if indexer.index_exists():
                    print(f"\n[OK] Using existing index: {index_name}")
                    indexer.load_existing_index()
                else:
                    print(f"\n[OK] Creating new index: {index_name}")

                # Index folder
                index_folder_handler(indexer)

        elif choice == "2":
            # Query an index - select index then enter query mode
            available_indexes = list_available_indexes()

            if not available_indexes:
                print("\n[i] No indexes available. Please index a folder first.")
                continue

            print("\n[QUERY] Select an index to query:")
            index_name = select_index_by_number(available_indexes)

            if index_name:
                indexer = DocumentIndexer(index_name)
                query_mode(indexer)

        elif choice == "3":
            # Work with an index - full workspace mode
            available_indexes = list_available_indexes()
            index_name = select_index_by_number(available_indexes)

            if index_name:
                indexer = DocumentIndexer(index_name)

                # Load existing index if available
                if indexer.index_exists():
                    print(f"\n[OK] Selected index: {index_name}")
                    indexer.load_existing_index()
                else:
                    print(f"\n[OK] New index '{index_name}' will be created when you index documents")

                # Enter index workspace
                index_workspace(indexer)

        elif choice == "4":
            # Show all indexes
            show_all_indexes_info()

        elif choice == "5":
            # Delete an index
            available_indexes = list_available_indexes()

            if not available_indexes:
                print("\n[i] No indexes to delete")
                continue

            print("\nSelect index to delete:")
            index_name = select_index_by_number(available_indexes)

            if index_name:
                indexer = DocumentIndexer(index_name)
                indexer.delete_index()

        elif choice == "6":
            # Exit
            print("\n[BYE] Goodbye!")
            break

        else:
            print("[X] Invalid choice")




# ============================================================================
# SIMPLE TEST FUNCTIONS - For Debugging and Future Testing
# ============================================================================

def example_simple_query():
    """Example: Simple query to Claude via LlamaIndex (for testing LLM)."""
    print("\n" + "=" * 60)
    print("TEST: Simple LLM Query")
    print("=" * 60)

    api_token = os.getenv("API_KEY")
    api_base = os.getenv("API_BASE", "https://api.rdsec.trendmicro.com/prod/aiendpoint/v1")
    model = os.getenv("MODEL_NAME", "claude-sonnet-4-5-20250929")

    if not api_token:
        print("[X] API_KEY not set in .env")
        return

    print(f"Setting up LLM: {model}")
    llm = CustomOpenAI(
        api_key=api_token,
        api_base=api_base,
        model=model,
        temperature=0.7,
    )

    query = "Explain LlamaIndex in one sentence."
    print(f"Query: {query}")
    print("... Sending request...")

    try:
        response = llm.complete(query)
        print(f"\n[OK] Response:\n{response}\n")
    except Exception as e:
        print(f"\n[X] Failed: {e}")


def example_document_query():
    """Example: Query indexed documents (placeholder for future tests)."""
    print("\n" + "=" * 60)
    print("TEST: Document Query")
    print("=" * 60)
    print("Use interactive mode (option 2) to query indexed documents")
    print("Or add custom test logic here for automated testing")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Default: Run main menu
    main_menu()

    # To run test functions instead, comment above and uncomment below:
    # example_simple_query()
    # example_document_query()
