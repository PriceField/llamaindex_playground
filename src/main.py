"""LlamaIndex developer tool for document indexing and querying with code-aware capabilities."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Debug mode
DEBUG = os.getenv("APP_DEBUG", "False").lower() == "true"


def debug_log(message: str) -> None:
    """Print debug message if debug mode is enabled."""
    if DEBUG:
        print(f"[DEBUG] {message}")


# ============================================================================
# SIMPLE TEST FUNCTIONS - For Debugging and Future Testing
# ============================================================================

def example_simple_query() -> None:
    """Example: Simple query to Claude via LlamaIndex (for testing LLM)."""
    from llm.custom_openai import CustomOpenAI

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


def example_document_query() -> None:
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
    # Default: Run main menu via CLI
    from cli.indexer_cli import IndexerCLI
    cli = IndexerCLI()
    cli.main_menu()

    # To run test functions instead, comment above and uncomment below:
    # example_simple_query()
    # example_document_query()
