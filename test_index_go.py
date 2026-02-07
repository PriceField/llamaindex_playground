"""Test script to index go-test-ground repository."""
import sys
import os
from pathlib import Path
sys.path.insert(0, 'src')

from main import DocumentIndexer

def test_index_go_repo(auto_confirm=True):
    """Index the go-test-ground repository.

    Args:
        auto_confirm: If True, automatically confirm prompts (for automated testing)
    """
    print("=" * 70)
    print("Testing: Index go-test-ground repository")
    print("=" * 70)

    try:
        # Determine directory to index
        test_dir = r"C:\Git\go-test-ground"

        # Check if directory exists
        if not os.path.exists(test_dir):
            print(f"\n[WARNING] {test_dir} not found")
            # Try test_data as fallback
            test_dir = os.path.join(os.getcwd(), "test_data")
            if not os.path.exists(test_dir):
                print(f"[ERROR] No test directory found. Checked:")
                print(f"  - C:\\Git\\go-test-ground")
                print(f"  - {test_dir}")
                print("\n[INFO] Please create test_data directory or specify TEST_DIR environment variable")
                return False
            print(f"[OK] Using fallback directory: {test_dir}")

        print(f"\n1. Creating indexer for directory: {test_dir}")
        indexer = DocumentIndexer("go_test_index")

        # Temporarily mock input if auto_confirm is True
        if auto_confirm:
            import builtins
            original_input = builtins.input
            builtins.input = lambda prompt: 'y'
            print("[TEST MODE] Auto-confirming all prompts")

        try:
            # Index the repository
            print("\n2. Starting indexing...")
            indexer.index_directory(
                directory=test_dir,
                file_extensions=['.go', '.md', '.py'],  # Added .py as fallback
                exclude_patterns=['vendor', 'node_modules', '__pycache__', '.git'],
                recursive=True,
                batch_size=5,
                autosave_interval=30
            )

            print("\n3. SUCCESS: Indexing completed")

        finally:
            # Restore original input
            if auto_confirm:
                builtins.input = original_input

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    # Check for command line argument to disable auto-confirm
    auto_confirm = '--no-auto-confirm' not in sys.argv

    if auto_confirm:
        print("[INFO] Running in auto-confirm mode. Use --no-auto-confirm for manual mode.\n")

    success = test_index_go_repo(auto_confirm=auto_confirm)
    sys.exit(0 if success else 1)
