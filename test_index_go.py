"""Test script to index go-test-ground repository."""
import sys
sys.path.insert(0, 'src')

from main import DocumentIndexer

def test_index_go_repo():
    """Index the go-test-ground repository."""
    print("=" * 70)
    print("Testing: Index go-test-ground repository")
    print("=" * 70)

    try:
        # Create indexer
        print("\n1. Creating indexer...")
        indexer = DocumentIndexer("go_test_index")

        # Index the repository
        print("\n2. Starting indexing...")
        indexer.index_directory(
            directory=r"C:\Git\go-test-ground",
            file_extensions=['.go', '.md'],
            exclude_patterns=['vendor', 'node_modules'],
            recursive=True,
            batch_size=5,
            autosave_interval=30
        )

        print("\n3. SUCCESS: Indexing completed")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = test_index_go_repo()
    sys.exit(0 if success else 1)
