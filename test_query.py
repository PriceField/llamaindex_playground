"""Test script to query the indexed repository."""
import sys
import os
sys.path.insert(0, 'src')

from main import DocumentIndexer

def test_query(index_name="go_test_index", question=None):
    """Test querying the indexed repository.

    Args:
        index_name: Name of the index to query
        question: Question to ask (uses default if None)
    """
    print("=" * 70)
    print(f"Testing: Query indexed repository '{index_name}'")
    print("=" * 70)

    try:
        # Create indexer and load existing index
        print(f"\n1. Loading indexer '{index_name}'...")
        indexer = DocumentIndexer(index_name)

        if not indexer.index_exists():
            print(f"\n[ERROR] No index found with name '{index_name}'")
            print(f"[INFO] Please run one of the following first:")
            print(f"  - python test_index_go.py")
            print(f"  - python src/main.py (interactive mode)")
            return False

        if not indexer.load_existing_index():
            print("[ERROR] Failed to load index.")
            return False

        # Get document count
        doc_count = len(indexer.index.docstore.docs) if indexer.index else 0
        print(f"[OK] Index loaded successfully with {doc_count} documents")

        # Use provided question or default
        if question is None:
            question = "What does this codebase do?"

        # Test query
        print(f"\n2. Running test query: '{question}'")
        print("-" * 70)
        indexer.query(
            question=question,
            top_k=3
        )
        print("-" * 70)

        print("\n3. SUCCESS: Query completed")
        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Parse command line arguments
    index_name = os.getenv("INDEX_NAME", "go_test_index")
    question = os.getenv("TEST_QUESTION", None)

    # Allow command line override
    if len(sys.argv) > 1:
        index_name = sys.argv[1]
    if len(sys.argv) > 2:
        question = " ".join(sys.argv[2:])

    print(f"[INFO] Index: {index_name}")
    if question:
        print(f"[INFO] Question: {question}")
    print()

    success = test_query(index_name=index_name, question=question)
    sys.exit(0 if success else 1)
