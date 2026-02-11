"""Enhanced query engine for code search."""
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.schema import QueryBundle
from llama_index.core.base.response.schema import Response

from config import QueryConfig


class CustomQueryEngine:
    """Custom query engine that manually handles retrieval and synthesis.

    This bypasses LlamaIndex's response_synthesizer which has compatibility issues
    with custom OpenAI endpoints.
    """

    def __init__(self, retriever: VectorIndexRetriever, prompt_template: str):
        """Initialize with retriever and prompt template.

        Args:
            retriever: VectorIndexRetriever for document retrieval
            prompt_template: Prompt template string with {context_str} and {query_str} placeholders
        """
        self.retriever = retriever
        self.prompt_template = prompt_template

    def query(self, query_str: str) -> Response:
        """Execute query with manual synthesis.

        Args:
            query_str: Query string

        Returns:
            Response object with answer and source nodes
        """
        # 1. Retrieve nodes
        nodes = self.retriever.retrieve(QueryBundle(query_str=query_str))

        # 2. Build context from retrieved nodes
        context_parts = [node.text for node in nodes]
        context_str = "\n\n".join(context_parts)

        # 3. Build prompt
        prompt = self.prompt_template.format(
            context_str=context_str,
            query_str=query_str
        )

        # 4. Call LLM directly
        llm_response = Settings.llm.complete(prompt)

        # 5. Create Response object
        return Response(
            response=llm_response.text,
            source_nodes=nodes,
            metadata={"query_str": query_str}
        )


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
    ) -> CustomQueryEngine:
        """Create query engine with optional metadata filters.

        Args:
            similarity_top_k: Number of top results to retrieve
            language_filter: Filter by programming language (e.g., 'python')
            category_filter: Filter by category (e.g., 'code', 'documentation')
            file_pattern: Filter by file pattern (not implemented yet)

        Returns:
            Configured custom query engine
        """
        top_k = similarity_top_k or self.config.code_similarity_top_k

        # Create retriever with explicit embed_model from index
        retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=top_k,
            embed_model=self.index._embed_model,
        )

        # Get prompt template
        prompt_template = self._get_code_qa_prompt_string()

        # Return custom query engine
        return CustomQueryEngine(retriever, prompt_template)

    def _get_code_qa_prompt_string(self) -> str:
        """Get custom QA prompt template string for code queries.

        Returns:
            Prompt template string with {context_str} and {query_str} placeholders
        """
        if self.config.include_source_context:
            return (
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
            return (
                "Context information is below.\n"
                "---------------------\n"
                "{context_str}\n"
                "---------------------\n"
                "Given the context information, answer the query.\n\n"
                "Query: {query_str}\n"
                "Answer: "
            )

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
        # Use response.response attribute which contains the actual LLM response text
        # Fall back to str(response) if the attribute doesn't exist
        response_text = response.response if hasattr(response, 'response') else str(response)
        output.append(response_text)
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
