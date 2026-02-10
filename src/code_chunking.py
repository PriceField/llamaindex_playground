"""Code-aware chunking strategies (REFACTORED).

This module now uses the Strategy Pattern with ChunkerRegistry.
The old hard-coded if/elif chains have been replaced with pluggable strategies.

See: strategies/chunking/ for language-specific implementations.

MIGRATION NOTE:
- Old implementation had 288 lines with hard-coded language chunkers
- New implementation uses Strategy Pattern (OCP compliant)
- Adding new language = register strategy, no modifications to this file
"""
from llama_index.core import Document
from llama_index.core.node_parser import NodeParser
from llama_index.core.schema import BaseNode, TextNode
from llama_index.core.node_parser import SentenceSplitter
from typing import TYPE_CHECKING, Any
from strategies.chunking.registry import ChunkerRegistry

if TYPE_CHECKING:
    from config import IndexerConfig
    from config.chunking_config import ChunkingConfig


class CodeAwareNodeParser(NodeParser):
    """Custom node parser that preserves code structure using strategy pattern.

    REFACTORED for SOLID compliance:
    - Open/Closed Principle: Adding new language = register strategy, no modifications
    - Single Responsibility: Delegates to language-specific chunkers
    - Dependency Inversion: Depends on abstraction (LanguageChunker)
    """

    def __init__(
        self,
        config: "IndexerConfig",
        registry: ChunkerRegistry | None = None,
        **kwargs: Any
    ) -> None:
        """Initialize with configuration and chunker registry.

        Args:
            config: IndexerConfig instance
            registry: Optional ChunkerRegistry (creates default if None)
            **kwargs: Additional arguments for base NodeParser
        """
        super().__init__(**kwargs)
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, '_config', config)
        object.__setattr__(self, '_registry', registry if registry is not None else ChunkerRegistry())

    @property
    def config(self) -> "IndexerConfig":
        """Get configuration."""
        return getattr(self, '_config', None)

    @property
    def registry(self) -> ChunkerRegistry:
        """Get chunker registry."""
        return getattr(self, '_registry', None)

    @classmethod
    def from_config(
        cls,
        chunking_config: "ChunkingConfig",
        registry: ChunkerRegistry | None = None,
        **kwargs: Any
    ) -> "CodeAwareNodeParser":
        """Create CodeAwareNodeParser from ChunkingConfig.

        This factory method allows creating the parser with the new ChunkingConfig
        instead of the legacy IndexerConfig.

        Args:
            chunking_config: ChunkingConfig instance with chunking settings
            registry: Optional ChunkerRegistry (creates default if None)
            **kwargs: Additional arguments for base NodeParser

        Returns:
            CodeAwareNodeParser instance

        Note:
            This creates a temporary config object that only contains chunking-related
            attributes. This is a bridge during refactoring.
        """
        # Create a minimal config object with just the chunking attributes
        # This avoids needing the full IndexerConfig
        class MinimalConfig:
            """Minimal config with only chunking attributes."""

            def __init__(self, chunking_config: "ChunkingConfig"):
                self.code_chunk_size = chunking_config.code_chunk_size
                self.code_chunk_overlap = chunking_config.code_chunk_overlap
                self.doc_chunk_size = chunking_config.doc_chunk_size
                self.doc_chunk_overlap = chunking_config.doc_chunk_overlap
                self.preserve_code_structure = chunking_config.preserve_code_structure
                self.include_line_numbers = chunking_config.include_line_numbers

        minimal_config = MinimalConfig(chunking_config)
        return cls(minimal_config, registry=registry, **kwargs)  # type: ignore

    def _parse_nodes(
        self,
        nodes: list[BaseNode],
        show_progress: bool = False,
        **kwargs
    ) -> list[BaseNode]:
        """Parse nodes with code-aware chunking.

        Args:
            nodes: List of nodes to parse
            show_progress: Whether to show progress
            **kwargs: Additional arguments

        Returns:
            List of parsed nodes
        """
        all_nodes = []

        for node in nodes:
            if isinstance(node, Document):
                # Get metadata
                language = node.metadata.get("language", "unknown")
                category = node.metadata.get("category", "other")

                # Choose chunking strategy based on category
                if category == "code" and self.config.preserve_code_structure:
                    parsed = self._chunk_code(node, language)
                else:
                    parsed = self._chunk_generic(node)

                all_nodes.extend(parsed)
            else:
                all_nodes.append(node)

        return all_nodes

    def _chunk_code(self, document: Document, language: str) -> list[TextNode]:
        """Chunk code using appropriate language strategy.

        Args:
            document: Document to chunk
            language: Programming language

        Returns:
            List of TextNodes
        """
        content = document.text
        file_path = document.metadata.get("file_path", "unknown")

        # Get appropriate chunker from registry
        chunker = self.registry.get_by_language(language)
        if not chunker:
            # No chunker for this language, fall back to generic chunking
            return self._chunk_generic(document)

        # Chunk using strategy
        code_chunks = chunker.chunk(
            content=content,
            file_path=file_path,
            chunk_size=self.config.code_chunk_size,
            chunk_overlap=self.config.code_chunk_overlap,
        )

        # Convert CodeChunk objects to TextNodes
        nodes = []
        for i, code_chunk in enumerate(code_chunks):
            metadata = document.metadata.copy()
            if self.config.include_line_numbers:
                metadata["start_line"] = code_chunk.start_line
                metadata["end_line"] = code_chunk.end_line
                metadata["chunk_index"] = i

            node = TextNode(
                text=code_chunk.text,
                metadata=metadata,
            )
            nodes.append(node)

        return nodes

    def _chunk_generic(self, document: Document) -> list[TextNode]:
        """Generic chunking for non-code files.

        Args:
            document: Document to chunk

        Returns:
            List of TextNodes
        """
        # Use larger chunk size for documentation
        chunk_size = self.config.doc_chunk_size if document.metadata.get("category") == "documentation" else self.config.code_chunk_size
        chunk_overlap = self.config.doc_chunk_overlap if document.metadata.get("category") == "documentation" else self.config.code_chunk_overlap

        splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        return splitter.get_nodes_from_documents([document])
