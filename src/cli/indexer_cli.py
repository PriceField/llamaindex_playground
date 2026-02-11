"""Command-line interface for document indexing."""

import json
import os
from pathlib import Path

from app_factory import AppFactory
from indexing.indexing_orchestrator import IndexingOrchestrator


def debug_log(message: str) -> None:
    """Print debug message if debug mode is enabled."""
    debug = os.getenv("APP_DEBUG", "False").lower() == "true"
    if debug:
        print(f"[DEBUG] {message}")


class IndexerCLI:
    """Interactive CLI for managing document indexes."""

    def __init__(self):
        """Initialize CLI (stateless)."""
        pass

    # ===== Index Discovery Methods =====

    def list_available_indexes(self) -> list[str]:
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

    def select_index_by_number(self, available_indexes: list[str]) -> str | None:
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

    def show_all_indexes_info(self) -> None:
        """Display detailed information about all available indexes."""
        available_indexes = self.list_available_indexes()

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

    # ===== User Input Prompts =====

    def prompt_for_filters(self, current_language: str | None = None,
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

    def prompt_for_indexing_config(self) -> dict:
        """Prompt for indexing configuration (directory, extensions, etc).

        Returns:
            Dictionary with indexing configuration parameters
        """
        # Folder path
        folder = input("\nFolder path to index: ").strip()
        if not folder:
            print("[X] No folder specified")
            return {}

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

        return {
            'directory': folder,
            'extensions': extensions,
            'exclude_patterns': exclude_patterns,
            'recursive': recursive,
            'batch_size': batch_size,
            'autosave_interval': autosave_interval
        }

    # ===== Menu Systems =====

    def query_mode(self, orchestrator: IndexingOrchestrator) -> None:
        """Enter continuous query mode with persistent filter settings.

        Args:
            orchestrator: IndexingOrchestrator instance to query
        """
        # Check if index exists
        if not orchestrator.index_exists():
            print("\n[X] Cannot enter query mode: Index does not exist")
            print("[i] Please index some documents first")
            return

        # Load index if needed
        if orchestrator.index is None:
            if not orchestrator.load_existing_index():
                print("\n[X] Failed to load index")
                return

        print("\n" + "=" * 70)
        print(f"QUERY MODE - Index: {orchestrator.index_name}")
        print("=" * 70)

        # Choose query mode (FREE vs PAID)
        print("\n[MODE SELECTION]")
        print("  1. FREE mode - Retrieval only, no LLM (💰 $0.00 per query)")
        print("  2. AI mode - LLM synthesis (💰 ~$0.01-0.05 per query)")
        mode_choice = input("\nYour choice (1/2, default: 1): ").strip()

        use_free_mode = mode_choice != "2"

        if use_free_mode:
            print("\n[OK] Using FREE mode - No LLM costs!")
            print("[i] Commands: 'back' or 'exit' to return")
            print()

            # Simple loop for free mode
            while True:
                question = input("\nYour question: ").strip()

                if question.lower() in ['back', 'exit']:
                    print("[OK] Exiting query mode...")
                    break

                if not question:
                    print("[X] No question specified")
                    continue

                # Get top_k
                top_k_input = input("Number of results (default: 5): ").strip()
                top_k = int(top_k_input) if top_k_input.isdigit() else 5

                try:
                    orchestrator.free_query(question, top_k)
                except Exception as e:
                    print(f"\n[X] Query failed: {e}")
                    debug_log(f"Query error: {str(e)}")

            return

        # AI mode (original behavior)
        print("\n[OK] Using AI mode - LLM will synthesize answers")
        print("[i] Commands: 'back' or 'exit' to return, '/filter' to change filters")
        print()

        # Prompt for filters once
        language, category, top_k = self.prompt_for_filters()

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
                language, category, top_k = self.prompt_for_filters(language, category, top_k)
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
                orchestrator.query(question, top_k, language, category)
            except Exception as e:
                print(f"\n[X] Query failed: {e}")
                debug_log(f"Query error: {str(e)}")

    def index_workspace(self, index_name: str) -> None:
        """Index workspace menu - operations on selected index.

        Args:
            index_name: Name of the index to work with
        """
        # Create orchestrator for all operations (Phase B: unified architecture)
        try:
            orchestrator = AppFactory.create_indexing_orchestrator(
                index_name=index_name,
                require_llm=True  # Allow AI query mode
            )
        except ValueError:
            # If LLM config fails, create without LLM (free mode only)
            print("[!] LLM configuration not available - only FREE query mode will work")
            orchestrator = AppFactory.create_indexing_orchestrator(
                index_name=index_name,
                require_llm=False
            )

        # Load existing index if available
        if orchestrator.index_exists():
            print(f"\n[OK] Selected index: {index_name}")
            orchestrator.load_existing_index()
        else:
            print(f"\n[OK] New index '{index_name}' will be created when you index documents")

        while True:
            print("\n" + "=" * 70)
            print(f"INDEX WORKSPACE: {index_name}")
            print("=" * 70)
            print("OPTIONS:")
            print("  1. Ask questions (query mode)")
            print("  2. Index a folder")
            print("  3. Show index info")
            print("  4. Back to main menu")
            print("=" * 70)

            choice = input("\nYour choice: ").strip()

            if choice == "1":
                # Enter query mode (uses IndexingOrchestrator)
                self.query_mode(orchestrator)

            elif choice == "2":
                # Index a folder (uses IndexingOrchestrator)
                self.handle_index_folder(index_name)

            elif choice == "3":
                # Show info for current index
                print(f"\n[INFO] Current Index: {index_name}")
                if orchestrator.index_exists():
                    print(f"[OK] Index exists at: {orchestrator.storage_dir}")
                    if orchestrator.index is None:
                        orchestrator.load_existing_index()

                    # Try to show document count
                    if orchestrator.index is not None:
                        doc_count = len(orchestrator.index.docstore.docs)
                        print(f"[OK] Documents: {doc_count}")
                else:
                    print(f"[i] No index found at: {orchestrator.storage_dir}")

            elif choice == "4":
                # Back to main menu
                print("[OK] Returning to main menu...")
                break

            else:
                print("[X] Invalid choice")

    def main_menu(self) -> None:
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
                available_indexes = self.list_available_indexes()
                print("\n[FOLDER] Select or create an index for your folder:")
                index_name = self.select_index_by_number(available_indexes)

                if index_name:
                    # Use new architecture for indexing
                    self.handle_index_folder(index_name)

            elif choice == "2":
                # Query an index - select index then enter query mode
                available_indexes = self.list_available_indexes()

                if not available_indexes:
                    print("\n[i] No indexes available. Please index a folder first.")
                    continue

                print("\n[QUERY] Select an index to query:")
                index_name = self.select_index_by_number(available_indexes)

                if index_name:
                    # Use DocumentIndexer temporarily for queries (Phase A)
                    self.handle_query(index_name)

            elif choice == "3":
                # Work with an index - full workspace mode
                available_indexes = self.list_available_indexes()
                index_name = self.select_index_by_number(available_indexes)

                if index_name:
                    # Enter index workspace
                    self.index_workspace(index_name)

            elif choice == "4":
                # Show all indexes
                self.show_all_indexes_info()

            elif choice == "5":
                # Delete an index
                available_indexes = self.list_available_indexes()

                if not available_indexes:
                    print("\n[i] No indexes to delete")
                    continue

                print("\nSelect index to delete:")
                index_name = self.select_index_by_number(available_indexes)

                if index_name:
                    # Use new architecture for deletion
                    self.handle_delete_index(index_name)

            elif choice == "6":
                # Exit
                print("\n[BYE] Goodbye!")
                break

            else:
                print("[X] Invalid choice")

    # ===== Operation Handlers (NEW - uses IndexingOrchestrator) =====

    def handle_index_folder(self, index_name: str) -> None:
        """Handle folder indexing operation using IndexingOrchestrator.

        Args:
            index_name: Name of the index to use
        """
        # Prompt for indexing config
        config = self.prompt_for_indexing_config()

        if not config:
            # User cancelled
            return

        try:
            # Create orchestrator with AppFactory (NEW!)
            orchestrator = AppFactory.create_indexing_orchestrator(
                index_name=index_name,
                require_llm=False  # Indexing doesn't need LLM
            )

            # Delegate to orchestrator
            orchestrator.index_directory(
                directory=config['directory'],
                file_extensions=config['extensions'],
                exclude_patterns=config['exclude_patterns'],
                recursive=config['recursive'],
                batch_size=config['batch_size'],
                autosave_interval=config['autosave_interval']
            )
        except Exception as e:
            print(f"\n[X] Indexing failed: {e}")
            debug_log(f"Indexing error: {str(e)}")

    def handle_query(self, index_name: str) -> None:
        """Handle query operation using IndexingOrchestrator.

        Args:
            index_name: Name of the index to query
        """
        # Create orchestrator for query operations (Phase B: complete)
        try:
            orchestrator = AppFactory.create_indexing_orchestrator(
                index_name=index_name,
                require_llm=True  # Allow AI query mode
            )
        except ValueError:
            # If LLM config fails, create without LLM (free mode only)
            print("[!] LLM configuration not available - only FREE query mode will work")
            orchestrator = AppFactory.create_indexing_orchestrator(
                index_name=index_name,
                require_llm=False
            )

        self.query_mode(orchestrator)

    def handle_delete_index(self, index_name: str) -> None:
        """Handle index deletion using IndexingOrchestrator.

        Args:
            index_name: Name of the index to delete
        """
        try:
            # Create orchestrator (NEW!)
            orchestrator = AppFactory.create_indexing_orchestrator(
                index_name=index_name,
                require_llm=False
            )

            # Delegate to orchestrator
            orchestrator.delete_index()
        except Exception as e:
            print(f"\n[X] Deletion failed: {e}")
            debug_log(f"Deletion error: {str(e)}")
