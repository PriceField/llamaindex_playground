"""Utility for categorizing files by type."""

from pathlib import Path
from .language_detector import LanguageDetector


class FileCategorizer:
    """Categorizes files into documentation, config, code, etc.

    Follows Single Responsibility Principle - only handles file categorization.
    """

    def __init__(
        self,
        language_detector: LanguageDetector | None = None,
        category_extensions: dict[str, list[str]] | None = None
    ):
        """Initialize with optional custom categorization rules.

        Args:
            language_detector: Optional language detector for code detection.
                              Defaults to new LanguageDetector() if None.
            category_extensions: Optional custom category mappings.
                                Defaults to built-in mappings if None.
        """
        self.language_detector = language_detector or LanguageDetector()
        self.category_extensions = category_extensions or self._build_default_categories()

    @staticmethod
    def _build_default_categories() -> dict[str, list[str]]:
        """Build default category-to-extensions mapping.

        Returns:
            Dictionary mapping category names to file extensions
        """
        return {
            "documentation": [".md", ".rst", ".txt", ".adoc"],
            "configuration": [".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env"],
            "web": [".html", ".css", ".scss", ".sass", ".less"],
            "data": [".csv", ".xml", ".sql"],
        }

    def categorize(self, file_path: str) -> str:
        """Detect file category from extension.

        Args:
            file_path: Path to the file

        Returns:
            Category name (e.g., 'code', 'documentation', 'configuration') or 'other'
        """
        ext = Path(file_path).suffix.lower()

        # Check if it's code (highest priority)
        if self.language_detector.is_code_file(file_path):
            return "code"

        # Check other categories
        for category, extensions in self.category_extensions.items():
            if ext in extensions:
                return category

        return "other"

    def is_documentation(self, file_path: str) -> bool:
        """Check if file is documentation.

        Args:
            file_path: Path to the file

        Returns:
            True if file is categorized as documentation
        """
        return self.categorize(file_path) == "documentation"

    def is_configuration(self, file_path: str) -> bool:
        """Check if file is configuration.

        Args:
            file_path: Path to the file

        Returns:
            True if file is categorized as configuration
        """
        return self.categorize(file_path) == "configuration"

    def is_code(self, file_path: str) -> bool:
        """Check if file is code.

        Args:
            file_path: Path to the file

        Returns:
            True if file is categorized as code
        """
        return self.categorize(file_path) == "code"

    def add_category(self, category: str, extensions: list[str]) -> None:
        """Add or update category mapping.

        Note: This creates a new instance variable since the class may use
        a default shared dictionary. For thread safety, create separate
        instances instead of mutating shared state.

        Args:
            category: Category name
            extensions: List of file extensions (including dots)
        """
        # Create a copy to avoid mutating shared default
        if self.category_extensions is self._build_default_categories():
            self.category_extensions = self.category_extensions.copy()

        self.category_extensions[category.lower()] = [
            ext if ext.startswith('.') else f'.{ext}'
            for ext in extensions
        ]
