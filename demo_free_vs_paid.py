"""Demo script showing FREE vs PAID query modes."""
import sys
import os
sys.path.insert(0, 'src')

from main import DocumentIndexer

def demo_comparison():
    """Compare FREE vs PAID query modes."""
    print("=" * 70)
    print("DEMO: FREE vs PAID Query Modes")
    print("=" * 70)

    index_name = input("\nEnter index name to query (e.g., 'go_test_index'): ").strip()
    if not index_name:
        print("[X] No index name provided")
        return

    # Create indexer
    indexer = DocumentIndexer(index_name, require_llm=False)

    if not indexer.index_exists():
        print(f"[X] Index '{index_name}' does not exist")
        return

    indexer.load_existing_index()

    question = input("\nEnter your question: ").strip()
    if not question:
        question = "What does this codebase do?"

    print("\n" + "=" * 70)
    print("OPTION 1: FREE MODE (Retrieval Only)")
    print("=" * 70)
    print("✅ Advantages:")
    print("  - 100% FREE - no API costs")
    print("  - Uses local HuggingFace embeddings")
    print("  - Fast vector search")
    print("  - Shows relevant code chunks with metadata")
    print("❌ Disadvantages:")
    print("  - You must read and understand code yourself")
    print("  - No natural language explanation")
    print("  - No synthesis across multiple chunks")
    print("\nWould you like to try FREE mode? (y/n): ", end="")

    if input().strip().lower() == 'y':
        print("\n[FREE MODE DEMO]")
        indexer.free_query(question, top_k=3)

    print("\n" + "=" * 70)
    print("OPTION 2: AI MODE (with LLM Synthesis)")
    print("=" * 70)
    print("✅ Advantages:")
    print("  - Natural language explanations")
    print("  - Synthesizes information across chunks")
    print("  - Understands context and relationships")
    print("  - Can answer in any language (e.g., Traditional Chinese)")
    print("❌ Disadvantages:")
    print("  - 💰 Costs ~$0.01-0.05 per query")
    print("  - 💰 'compact' mode makes MULTIPLE LLM calls")
    print("  - Requires API_KEY and API_BASE configured")
    print("\n[!] This will cost money. Skip demo? (y/n): ", end="")

    if input().strip().lower() != 'y':
        # Need to create a new indexer with LLM enabled
        try:
            indexer_with_llm = DocumentIndexer(index_name, require_llm=True)
            indexer_with_llm.load_existing_index()

            print("\n[AI MODE DEMO]")
            print("💰 Note: This will make API calls and cost money!")
            indexer_with_llm.query(question, top_k=3)
        except Exception as e:
            print(f"[X] AI mode not available: {e}")
            print("[i] Make sure API_KEY and API_BASE are set in .env")

    print("\n" + "=" * 70)
    print("RECOMMENDATION:")
    print("=" * 70)
    print("For most code searches: Use FREE mode")
    print("  - Finding functions, classes, examples")
    print("  - Understanding code structure")
    print("  - Quick lookups")
    print("\nUse AI mode only when:")
    print("  - You need complex explanations")
    print("  - Connecting concepts across many files")
    print("  - Translating/explaining in natural language")
    print("=" * 70)

if __name__ == "__main__":
    demo_comparison()
