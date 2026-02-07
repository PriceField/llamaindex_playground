"""Centralized configuration management for document indexing."""
from pathlib import Path
from typing import List, Dict
import os
from dotenv import load_dotenv


class IndexerConfig:
    """Configuration for document indexer with code-specific settings."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        load_dotenv()

        # Chunking configuration
        self.code_chunk_size = self._parse_int("CODE_CHUNK_SIZE", 512)
        self.code_chunk_overlap = self._parse_int("CODE_CHUNK_OVERLAP", 50)
        self.doc_chunk_size = self._parse_int("DOC_CHUNK_SIZE", 1024)
        self.doc_chunk_overlap = self._parse_int("DOC_CHUNK_OVERLAP", 20)

        # Code extraction settings
        self.extract_functions = self._parse_bool("EXTRACT_FUNCTIONS", True)
        self.extract_classes = self._parse_bool("EXTRACT_CLASSES", True)
        self.extract_imports = self._parse_bool("EXTRACT_IMPORTS", True)
        self.include_line_numbers = self._parse_bool("INCLUDE_LINE_NUMBERS", True)
        self.preserve_code_structure = self._parse_bool("PRESERVE_CODE_STRUCTURE", True)

        # Language support
        self.supported_languages = self._parse_list(
            os.getenv("SUPPORTED_LANGUAGES", "csharp,python,javascript,typescript,java,go,rust,cpp,c,ruby,php")
        )

        # Default exclusions
        self.default_exclude_patterns = self._parse_list(
            os.getenv("DEFAULT_EXCLUDE_PATTERNS",
                     "node_modules,__pycache__,.git,dist,build,target,.venv,venv,.pytest_cache,.mypy_cache,*.pyc,*.pyo,*.so,*.dll,*.exe")
        )

        # Query settings
        self.code_similarity_top_k = self._parse_int("CODE_SIMILARITY_TOP_K", 5)
        self.use_metadata_filters = self._parse_bool("USE_METADATA_FILTERS", True)
        self.include_source_context = self._parse_bool("INCLUDE_SOURCE_CONTEXT", True)

        # File type mappings
        self.language_extensions = self._build_language_extensions()
        self.file_categories = self._build_file_categories()

    def _parse_int(self, key: str, default: int) -> int:
        """Parse integer from env var, stripping inline comments.

        Args:
            key: Environment variable key
            default: Default value if not found

        Returns:
            Parsed integer value
        """
        value = os.getenv(key, str(default))
        # Strip inline comments (everything after #)
        value = value.split('#')[0].strip()
        try:
            return int(value)
        except ValueError:
            return default

    def _parse_bool(self, key: str, default: bool) -> bool:
        """Parse boolean from env var, stripping inline comments.

        Args:
            key: Environment variable key
            default: Default value if not found

        Returns:
            Parsed boolean value
        """
        value = os.getenv(key, str(default))
        # Strip inline comments (everything after #)
        value = value.split('#')[0].strip()
        return value.lower() == "true"

    def _parse_list(self, value: str) -> List[str]:
        """Parse comma-separated list from env var, stripping inline comments.

        Args:
            value: Comma-separated string value

        Returns:
            List of parsed strings
        """
        # Strip inline comments (everything after #)
        value = value.split('#')[0].strip()
        return [item.strip() for item in value.split(",") if item.strip()]

    def _build_language_extensions(self) -> Dict[str, List[str]]:
        """Map languages to file extensions."""
        return {
            "csharp": [".cs"],
            "python": [".py", ".pyw"],
            "javascript": [".js", ".jsx", ".mjs"],
            "typescript": [".ts", ".tsx"],
            "java": [".java"],
            "go": [".go"],
            "rust": [".rs"],
            "cpp": [".cpp", ".cc", ".cxx", ".hpp", ".h", ".hxx"],
            "c": [".c", ".h"],
            "ruby": [".rb"],
            "php": [".php"],
            "swift": [".swift"],
            "kotlin": [".kt", ".kts"],
            "scala": [".scala"],
        }

    def _build_file_categories(self) -> Dict[str, List[str]]:
        """Categorize file types."""
        return {
            "documentation": [".md", ".rst", ".txt", ".adoc"],
            "configuration": [".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env"],
            "web": [".html", ".css", ".scss", ".sass", ".less"],
            "data": [".csv", ".xml", ".sql"],
        }

    def detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension.

        Args:
            file_path: Path to the file

        Returns:
            Language name (e.g., 'python', 'javascript') or 'unknown'
        """
        ext = Path(file_path).suffix.lower()
        for lang, extensions in self.language_extensions.items():
            if ext in extensions:
                return lang
        return "unknown"

    def detect_category(self, file_path: str) -> str:
        """Detect file category from extension.

        Args:
            file_path: Path to the file

        Returns:
            Category name (e.g., 'code', 'documentation', 'configuration') or 'other'
        """
        ext = Path(file_path).suffix.lower()

        # Check if it's code
        for lang, extensions in self.language_extensions.items():
            if ext in extensions:
                return "code"

        # Check other categories
        for category, extensions in self.file_categories.items():
            if ext in extensions:
                return category

        return "other"
