"""Document loader with code-aware metadata extraction."""

import os
from llama_index.core import Document

from file_handlers import FileHandler
from code_extractors import CodeMetadataExtractor


def debug_log(message: str) -> None:
    """Print debug message if debug mode is enabled."""
    debug = os.getenv("APP_DEBUG", "False").lower() == "true"
    if debug:
        print(f"[DEBUG] {message}")


class DocumentLoader:
    """Loads documents with enhanced code-aware metadata.

    Follows Single Responsibility Principle - only loads documents with metadata.
    Follows Dependency Inversion Principle - depends on injected components.
    """

    def __init__(
        self,
        file_handler: FileHandler,
        code_extractor: CodeMetadataExtractor
    ):
        """Initialize with dependencies.

        Args:
            file_handler: Handler for file metadata extraction
            code_extractor: Extractor for code-specific metadata
        """
        self.file_handler = file_handler
        self.code_extractor = code_extractor

    def load_document(self, file_path: str) -> Document | None:
        """Load a document with enhanced code-aware metadata.

        Args:
            file_path: Path to the file

        Returns:
            Document with metadata or None if error occurs
        """
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Get basic file metadata
            file_metadata = self.file_handler.get_file_metadata(file_path)

            # Extract code-specific metadata if it's a code file
            if file_metadata["category"] == "code":
                code_metadata = self.code_extractor.extract_metadata(
                    file_path, content, file_metadata["language"]
                )
                file_metadata.update(code_metadata)

            # Create document with metadata
            doc = Document(
                text=content,
                metadata=file_metadata,
            )

            return doc

        except Exception as e:
            debug_log(f"Error loading {file_path}: {e}")
            return None

    def load_documents(self, file_paths: list[str]) -> list[Document]:
        """Load multiple documents with metadata.

        Args:
            file_paths: List of file paths to load

        Returns:
            List of successfully loaded documents (failures are skipped)
        """
        documents = []
        for file_path in file_paths:
            doc = self.load_document(file_path)
            if doc is not None:
                documents.append(doc)
        return documents
