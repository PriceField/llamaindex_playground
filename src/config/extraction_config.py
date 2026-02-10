"""Configuration for code metadata extraction."""

from dataclasses import dataclass
from .env_parser import EnvParser


@dataclass(frozen=True)
class ExtractionConfig:
    """Configuration for extracting code metadata.

    Follows Interface Segregation Principle - clients only depend on
    extraction-related settings.

    Attributes:
        extract_functions: Whether to extract function/method names
        extract_classes: Whether to extract class names
        extract_imports: Whether to extract import statements
        include_line_numbers: Whether to include line numbers in chunks
    """

    extract_functions: bool
    extract_classes: bool
    extract_imports: bool
    include_line_numbers: bool

    @property
    def should_extract(self) -> bool:
        """Check if any extraction is enabled."""
        return self.extract_functions or self.extract_classes or self.extract_imports

    @classmethod
    def from_env(cls) -> "ExtractionConfig":
        """Create configuration from environment variables.

        Returns:
            ExtractionConfig instance loaded from environment
        """
        return cls(
            extract_functions=EnvParser.parse_bool("EXTRACT_FUNCTIONS", True),
            extract_classes=EnvParser.parse_bool("EXTRACT_CLASSES", True),
            extract_imports=EnvParser.parse_bool("EXTRACT_IMPORTS", True),
            include_line_numbers=EnvParser.parse_bool("INCLUDE_LINE_NUMBERS", True),
        )

    @classmethod
    def default(cls) -> "ExtractionConfig":
        """Create configuration with default values.

        Returns:
            ExtractionConfig with default settings
        """
        return cls(
            extract_functions=True,
            extract_classes=True,
            extract_imports=True,
            include_line_numbers=True,
        )

    @classmethod
    def none(cls) -> "ExtractionConfig":
        """Create configuration with all extraction disabled.

        Returns:
            ExtractionConfig with no extraction
        """
        return cls(
            extract_functions=False,
            extract_classes=False,
            extract_imports=False,
            include_line_numbers=False,
        )
