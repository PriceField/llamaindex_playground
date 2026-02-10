"""Code-aware chunking strategies."""
from llama_index.core import Document
from llama_index.core.node_parser import NodeParser
from llama_index.core.schema import BaseNode, TextNode
from llama_index.core.node_parser import SentenceSplitter
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from config import IndexerConfig
    from config.chunking_config import ChunkingConfig


class CodeAwareNodeParser(NodeParser):
    """Custom node parser that preserves code structure."""

    def __init__(self, config: "IndexerConfig", **kwargs: Any) -> None:
        """Initialize with configuration.

        Args:
            config: IndexerConfig instance
            **kwargs: Additional arguments for base NodeParser
        """
        super().__init__(**kwargs)
        # Use object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, '_config', config)

    @property
    def config(self) -> "IndexerConfig":
        """Get configuration."""
        return getattr(self, '_config', None)

    @classmethod
    def from_config(cls, chunking_config: "ChunkingConfig", **kwargs: Any) -> "CodeAwareNodeParser":
        """Create CodeAwareNodeParser from ChunkingConfig.

        This factory method allows creating the parser with the new ChunkingConfig
        instead of the legacy IndexerConfig.

        Args:
            chunking_config: ChunkingConfig instance with chunking settings
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
        return cls(minimal_config, **kwargs)  # type: ignore

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
        """Chunk code preserving function/class boundaries.

        Args:
            document: Document to chunk
            language: Programming language

        Returns:
            List of TextNodes
        """
        content = document.text
        chunks = []

        if language == "python":
            chunks = self._chunk_python(content)
        elif language in ["javascript", "typescript"]:
            chunks = self._chunk_javascript(content)
        elif language == "java":
            chunks = self._chunk_java(content)
        else:
            # Fallback to generic chunking
            return self._chunk_generic(document)

        # Convert chunks to TextNodes
        nodes = []
        for i, (chunk_text, start_line, end_line) in enumerate(chunks):
            metadata = document.metadata.copy()
            if self.config.include_line_numbers:
                metadata["start_line"] = start_line
                metadata["end_line"] = end_line
                metadata["chunk_index"] = i

            node = TextNode(
                text=chunk_text,
                metadata=metadata,
            )
            nodes.append(node)

        return nodes

    def _chunk_python(self, content: str) -> list[tuple[str, int, int]]:
        """Chunk Python code by functions and classes.

        Args:
            content: Python source code

        Returns:
            List of tuples (chunk_text, start_line, end_line)
        """
        chunks = []
        lines = content.split('\n')

        # Find function and class boundaries
        current_chunk = []
        current_start_line = 1
        in_block = False
        block_indent = 0

        for i, line in enumerate(lines, 1):
            # Detect function or class definition
            if re.match(r'^(?:class|def|async\s+def)\s+', line):
                # Save previous chunk if exists
                if current_chunk:
                    chunk_text = '\n'.join(current_chunk)
                    if chunk_text.strip():
                        chunks.append((chunk_text, current_start_line, i - 1))

                # Start new chunk
                current_chunk = [line]
                current_start_line = i
                in_block = True
                block_indent = len(line) - len(line.lstrip())
            elif in_block:
                # Continue block if indented
                line_indent = len(line) - len(line.lstrip()) if line.strip() else block_indent + 1
                if line.strip() == '' or line_indent > block_indent:
                    current_chunk.append(line)
                else:
                    # Block ended
                    chunk_text = '\n'.join(current_chunk)
                    if chunk_text.strip():
                        chunks.append((chunk_text, current_start_line, i - 1))
                    current_chunk = [line]
                    current_start_line = i
                    in_block = False
            else:
                current_chunk.append(line)

                # Check if chunk is getting too large
                chunk_text = '\n'.join(current_chunk)
                if len(chunk_text) > self.config.code_chunk_size * 2:
                    chunks.append((chunk_text, current_start_line, i))
                    current_chunk = []
                    current_start_line = i + 1

        # Add final chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            if chunk_text.strip():
                chunks.append((chunk_text, current_start_line, len(lines)))

        return chunks if chunks else [(content, 1, len(lines))]

    def _chunk_javascript(self, content: str) -> list[tuple[str, int, int]]:
        """Chunk JavaScript/TypeScript code by functions and classes.

        Args:
            content: JavaScript/TypeScript source code

        Returns:
            List of tuples (chunk_text, start_line, end_line)
        """
        chunks = []
        lines = content.split('\n')

        # Track brace depth
        current_chunk = []
        current_start_line = 1
        brace_depth = 0
        in_function = False

        for i, line in enumerate(lines, 1):
            # Detect function or class start
            if re.search(r'(?:class|function)\s+\w+|const\s+\w+\s*=\s*(?:async\s+)?\(', line):
                if current_chunk and brace_depth == 0:
                    chunk_text = '\n'.join(current_chunk)
                    if chunk_text.strip():
                        chunks.append((chunk_text, current_start_line, i - 1))
                    current_chunk = []
                    current_start_line = i
                in_function = True

            current_chunk.append(line)

            # Track braces
            brace_depth += line.count('{') - line.count('}')

            # End of function/class
            if in_function and brace_depth == 0 and '{' in '\n'.join(current_chunk):
                chunk_text = '\n'.join(current_chunk)
                if chunk_text.strip():
                    chunks.append((chunk_text, current_start_line, i))
                current_chunk = []
                current_start_line = i + 1
                in_function = False

        # Add remaining
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            if chunk_text.strip():
                chunks.append((chunk_text, current_start_line, len(lines)))

        return chunks if chunks else [(content, 1, len(lines))]

    def _chunk_java(self, content: str) -> list[tuple[str, int, int]]:
        """Chunk Java code by methods and classes.

        Args:
            content: Java source code

        Returns:
            List of tuples (chunk_text, start_line, end_line)
        """
        # Reuse JavaScript chunking logic (similar brace-based structure)
        return self._chunk_javascript(content)

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
