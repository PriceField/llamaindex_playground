"""Utility for detecting programming language from file extensions."""

from pathlib import Path


class LanguageDetector:
    """Detects programming language from file extensions.

    Follows Single Responsibility Principle - only handles language detection.
    """

    def __init__(self, language_extensions: dict[str, list[str]] | None = None):
        """Initialize with language-to-extensions mapping.

        Args:
            language_extensions: Optional custom language mappings.
                                Defaults to built-in mappings if None.
        """
        self.language_extensions = language_extensions or self._build_default_extensions()

    @staticmethod
    def _build_default_extensions() -> dict[str, list[str]]:
        """Build default language-to-extensions mapping.

        Returns:
            Dictionary mapping language names to file extensions
        """
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

    def detect(self, file_path: str) -> str:
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

    def is_code_file(self, file_path: str) -> bool:
        """Check if file is a recognized code file.

        Args:
            file_path: Path to the file

        Returns:
            True if file extension matches a known language
        """
        return self.detect(file_path) != "unknown"

    def get_extensions_for_language(self, language: str) -> list[str]:
        """Get file extensions for a specific language.

        Args:
            language: Language name (e.g., "python")

        Returns:
            List of extensions (e.g., [".py", ".pyw"]) or empty list if unknown
        """
        return self.language_extensions.get(language.lower(), [])

    def add_language(self, language: str, extensions: list[str]) -> None:
        """Add or update language mapping.

        Note: This creates a new instance variable since the class may use
        a default shared dictionary. For thread safety, create separate
        instances instead of mutating shared state.

        Args:
            language: Language name
            extensions: List of file extensions (including dots)
        """
        # Create a copy to avoid mutating shared default
        if self.language_extensions is self._build_default_extensions():
            self.language_extensions = self.language_extensions.copy()

        self.language_extensions[language.lower()] = [
            ext if ext.startswith('.') else f'.{ext}'
            for ext in extensions
        ]
