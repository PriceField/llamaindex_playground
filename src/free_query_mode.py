"""Free query mode - 100% local, no LLM costs."""
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config import IndexerConfig


class FreeQueryEngine:
    """Retrieval-only query engine - no LLM calls, no costs."""

    def __init__(self, index: VectorStoreIndex, config: "IndexerConfig") -> None:
        """Initialize with index and configuration.

        Args:
            index: VectorStoreIndex to query
            config: IndexerConfig instance
        """
        self.index = index
        self.config = config

    def query(
        self,
        question: str,
        top_k: int | None = None,
    ) -> list[dict]:
        """Query the index and return raw retrieved chunks.

        This method is 100% FREE - no LLM API calls.
        Uses only local vector search with HuggingFace embeddings.

        Args:
            question: Question to search for
            top_k: Number of results to retrieve

        Returns:
            List of retrieved chunks with metadata
        """
        top_k_value = top_k or self.config.code_similarity_top_k

        # Create retriever (uses local embeddings only)
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=top_k_value,
        )

        # Retrieve relevant chunks (FREE - no LLM call)
        nodes = retriever.retrieve(question)

        # Format results
        results = []
        for node in nodes:
            metadata = node.metadata
            results.append({
                "file_path": metadata.get("file_path", "unknown"),
                "file_name": metadata.get("file_name", "unknown"),
                "start_line": metadata.get("start_line"),
                "end_line": metadata.get("end_line"),
                "language": metadata.get("language", "unknown"),
                "category": metadata.get("category", "unknown"),
                "score": node.score if hasattr(node, "score") else 0.0,
                "text": node.text,
            })

        return results

    def format_results(self, results: list[dict]) -> str:
        """Format retrieval results for display.

        Args:
            results: List of result dictionaries

        Returns:
            Formatted string for display
        """
        if not results:
            return "No results found."

        output = []
        output.append("=" * 70)
        output.append("🔍 SEARCH RESULTS (FREE MODE - No LLM used)")
        output.append("=" * 70)

        for i, result in enumerate(results, 1):
            output.append(f"\n[{i}] {result['file_name']}")
            output.append(f"    Path: {result['file_path']}")

            if result['start_line'] and result['end_line']:
                output.append(f"    Lines: {result['start_line']}-{result['end_line']}")

            if result['language'] != 'unknown':
                output.append(f"    Language: {result['language']}")

            if result['category']:
                output.append(f"    Type: {result['category']}")

            output.append(f"    Relevance: {result['score']:.3f}")

            # Show code content
            output.append(f"\n    Content:")
            output.append("    " + "-" * 66)
            for line in result['text'].split('\n'):
                output.append(f"    {line}")
            output.append("    " + "-" * 66)

        output.append("\n" + "=" * 70)
        output.append(f"💡 TIP: Read the code above to find your answer (FREE!)")
        output.append(f"💰 COST: $0.00 (No LLM calls made)")
        output.append("=" * 70)

        return "\n".join(output)
