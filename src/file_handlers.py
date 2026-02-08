"""Smart file type detection and handling."""
from pathlib import Path
import re


class FileHandler:
    """Handle file type detection and smart exclusions."""

    def __init__(self, config):
        """Initialize with configuration.

        Args:
            config: IndexerConfig instance
        """
        self.config = config

    def should_index_file(self, file_path: str,
                          user_extensions: list[str] | None = None,
                          user_exclude: list[str] | None = None) -> bool:
        """Determine if a file should be indexed.

        Args:
            file_path: Path to the file
            user_extensions: Optional list of file extensions to include (e.g., ['.py', '.md'])
            user_exclude: Optional list of exclude patterns to add to defaults

        Returns:
            True if file should be indexed, False otherwise
        """
        path = Path(file_path)

        # Check user-provided extensions filter
        if user_extensions:
            if path.suffix.lower() not in user_extensions:
                return False

        # Combine default and user exclude patterns
        exclude_patterns = self.config.default_exclude_patterns.copy()
        if user_exclude:
            exclude_patterns.extend(user_exclude)

        # Check if file matches any exclude pattern
        for pattern in exclude_patterns:
            if self._matches_pattern(str(path), pattern):
                return False

        return True

    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches exclude pattern.

        Args:
            path: File path to check
            pattern: Glob-like pattern (e.g., '*.pyc', '*test*', 'node_modules')

        Returns:
            True if path matches pattern, False otherwise
        """
        # Convert glob pattern to regex
        if '*' in pattern:
            regex = pattern.replace('.', r'\.').replace('*', '.*')
            return bool(re.search(regex, path))
        else:
            # Direct substring match
            return pattern in path

    def get_file_metadata(self, file_path: str) -> dict[str, str]:
        """Extract basic file metadata.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary containing file metadata:
                - file_path: Absolute path to the file
                - file_name: Name of the file
                - file_extension: File extension (lowercase)
                - language: Detected programming language
                - category: File category (code, documentation, etc.)
        """
        path = Path(file_path)

        return {
            "file_path": str(path.resolve()),
            "file_name": path.name,
            "file_extension": path.suffix.lower(),
            "language": self.config.detect_language(str(path)),
            "category": self.config.detect_category(str(path)),
        }
