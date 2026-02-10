"""Configuration for file filtering and selection."""

from dataclasses import dataclass
from .env_parser import EnvParser


@dataclass(frozen=True)
class FileFilterConfig:
    """Configuration for filtering files during indexing.

    Follows Interface Segregation Principle - clients only depend on
    file filtering settings.

    Attributes:
        supported_languages: List of programming languages to index
        default_exclude_patterns: Patterns to exclude from indexing (directories, files)
    """

    supported_languages: list[str]
    default_exclude_patterns: list[str]

    def __post_init__(self) -> None:
        """Validate configuration."""
        if not self.supported_languages:
            raise ValueError("supported_languages cannot be empty")

    def is_language_supported(self, language: str) -> bool:
        """Check if a language is supported.

        Args:
            language: Language name (e.g., "python", "javascript")

        Returns:
            True if language is supported
        """
        return language.lower() in [lang.lower() for lang in self.supported_languages]

    def should_exclude(self, path: str) -> bool:
        """Check if a path matches any exclude pattern.

        Args:
            path: File or directory path to check

        Returns:
            True if path should be excluded
        """
        path_lower = path.lower()
        for pattern in self.default_exclude_patterns:
            # Simple pattern matching (contains)
            if pattern.lower() in path_lower:
                return True
        return False

    @classmethod
    def from_env(cls) -> "FileFilterConfig":
        """Create configuration from environment variables.

        Returns:
            FileFilterConfig instance loaded from environment
        """
        return cls(
            supported_languages=EnvParser.parse_list(
                "SUPPORTED_LANGUAGES",
                "csharp,python,javascript,typescript,java,go,rust,cpp,c,ruby,php"
            ),
            default_exclude_patterns=EnvParser.parse_list(
                "DEFAULT_EXCLUDE_PATTERNS",
                "node_modules,__pycache__,.git,dist,build,target,.venv,venv,.pytest_cache,.mypy_cache,*.pyc,*.pyo,*.so,*.dll,*.exe"
            ),
        )

    @classmethod
    def default(cls) -> "FileFilterConfig":
        """Create configuration with default values.

        Returns:
            FileFilterConfig with default settings
        """
        return cls(
            supported_languages=[
                "csharp", "python", "javascript", "typescript",
                "java", "go", "rust", "cpp", "c", "ruby", "php"
            ],
            default_exclude_patterns=[
                "node_modules", "__pycache__", ".git", "dist", "build", "target",
                ".venv", "venv", ".pytest_cache", ".mypy_cache",
                "*.pyc", "*.pyo", "*.so", "*.dll", "*.exe"
            ],
        )
