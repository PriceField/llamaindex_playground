"""Enhanced query engine for code search."""
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.prompts import PromptTemplate

from config import QueryConfig


class CodeQueryEngine:
    """Enhanced query engine with code-specific features.

    Follows Dependency Injection Principle - takes QueryConfig for query settings.
    """

    def __init__(self, index: VectorStoreIndex, config: QueryConfig) -> None:
        """Initialize with index and query configuration.

        Args:
            index: VectorStoreIndex to query
            config: QueryConfig instance
        """
        self.index = index
        self.config = config

    def create_query_engine(
        self,
        similarity_top_k: int | None = None,
        language_filter: str | None = None,
        category_filter: str | None = None,
        file_pattern: str | None = None,
    ) -> RetrieverQueryEngine:
        """Create query engine with optional metadata filters.

        Args:
            similarity_top_k: Number of top results to retrieve
            language_filter: Filter by programming language (e.g., 'python')
            category_filter: Filter by category (e.g., 'code', 'documentation')
            file_pattern: Filter by file pattern (not implemented yet)

        Returns:
            Configured query engine
        """
        top_k = similarity_top_k or self.config.code_similarity_top_k

        # Create retriever
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=top_k,
        )

        # Create post-processors
        postprocessors = [
            SimilarityPostprocessor(similarity_cutoff=0.5),
        ]

        # Custom prompt for code queries
        qa_prompt_template = self._get_code_qa_prompt()

        # Create response synthesizer
        response_synthesizer = get_response_synthesizer(
            response_mode="compact",
            text_qa_template=qa_prompt_template,
        )

        # Create query engine
        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
            node_postprocessors=postprocessors,
        )

        return query_engine

    def _get_code_qa_prompt(self) -> PromptTemplate:
        """Get custom QA prompt for code queries.

        Returns:
            PromptTemplate configured for code search
        """
        if self.config.include_source_context:
            template = (
                "Context information is below.\n"
                "---------------------\n"
                "{context_str}\n"
                "---------------------\n"
                "Given the context information about code and documentation, "
                "answer the query. When referencing code, always mention:\n"
                "1. The file path\n"
                "2. Line numbers if available\n"
                "3. The function or class name if relevant\n"
                "4. The programming language\n\n"
                "Provide code examples when helpful.\n\n"
                "Query: {query_str}\n"
                "Answer: "
            )
        else:
            template = (
                "Context information is below.\n"
                "---------------------\n"
                "{context_str}\n"
                "---------------------\n"
                "Given the context information, answer the query.\n\n"
                "Query: {query_str}\n"
                "Answer: "
            )

        return PromptTemplate(template)

    def format_response_with_sources(self, response: object, top_k: int = 5) -> str:
        """Format response with enhanced source information.

        Args:
            response: Query response object
            top_k: Number of sources to display

        Returns:
            Formatted response string
        """
        output = []

        # Main response
        output.append("=" * 60)
        output.append("ANSWER:")
        output.append("=" * 60)
        output.append(str(response))
        output.append("")

        # Sources with enhanced metadata
        if hasattr(response, 'source_nodes') and response.source_nodes:
            output.append("=" * 60)
            output.append("SOURCES:")
            output.append("=" * 60)

            for i, node in enumerate(response.source_nodes[:top_k]):
                metadata = node.metadata
                score = node.score if hasattr(node, 'score') else 0.0

                output.append(f"\n{i+1}. {metadata.get('file_name', 'unknown')}")
                output.append(f"   Path: {metadata.get('file_path', 'unknown')}")

                if 'start_line' in metadata and 'end_line' in metadata:
                    output.append(f"   Lines: {metadata['start_line']}-{metadata['end_line']}")

                if 'language' in metadata and metadata['language'] != 'unknown':
                    output.append(f"   Language: {metadata['language']}")

                if 'category' in metadata:
                    output.append(f"   Type: {metadata['category']}")

                output.append(f"   Relevance: {score:.3f}")

                # Show code snippet preview if available
                if node.text and len(node.text) < 500:
                    preview = node.text[:200] + "..." if len(node.text) > 200 else node.text
                    output.append(f"   Preview: {preview}")

        return "\n".join(output)
