"""Test script to query the indexed repository."""
import sys
sys.path.insert(0, 'src')

from main import DocumentIndexer

def test_query():
    """Test querying the indexed repository."""
    print("=" * 70)
    print("Testing: Query indexed repository")
    print("=" * 70)

    try:
        # Create indexer and load existing index
        print("\n1. Loading indexer...")
        indexer = DocumentIndexer("go_test_index")

        if not indexer.load_existing_index():
            print("ERROR: No index found. Run test_index_go.py first.")
            return False

        # Test query
        print("\n2. Running test query...")
        indexer.query(
            question="What does the resource monitor do?",
            top_k=3
        )

        print("\n3. SUCCESS: Query completed")
        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_query()
    sys.exit(0 if success else 1)
