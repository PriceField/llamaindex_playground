"""Extract code-specific metadata from source files (REFACTORED).

This module now uses the Strategy Pattern with MetadataExtractorRegistry.
The old hard-coded if/elif chains have been replaced with pluggable strategies.

See: strategies/extraction/ for language-specific implementations.

MIGRATION NOTE:
- Old implementation had 242 lines with hard-coded language extractors
- New implementation uses Strategy Pattern (OCP compliant)
- Adding new language = register strategy, no modifications to this file
"""
from typing import TYPE_CHECKING
from strategies.extraction.registry import MetadataExtractorRegistry

if TYPE_CHECKING:
    from config import IndexerConfig


class CodeMetadataExtractor:
    """Extract metadata from code files using strategy pattern.

    REFACTORED for SOLID compliance:
    - Open/Closed Principle: Adding new language = register strategy, no modifications
    - Single Responsibility: Delegates to language-specific strategies
    - Dependency Inversion: Depends on abstraction (LanguageMetadataExtractor)
    """

    def __init__(self, config: "IndexerConfig", registry: MetadataExtractorRegistry | None = None) -> None:
        """Initialize with configuration and strategy registry.

        Args:
            config: IndexerConfig instance
            registry: Optional MetadataExtractorRegistry (creates default if None)
        """
        self.config = config
        self.registry = registry if registry is not None else MetadataExtractorRegistry()

    def extract_metadata(self, file_path: str, content: str, language: str) -> dict[str, list[str]]:
        """Extract code metadata using appropriate language strategy.

        Args:
            file_path: Path to the file
            content: File content
            language: Programming language

        Returns:
            Dictionary containing extracted metadata (functions, classes, imports)
        """
        # Skip if all extraction flags are disabled
        if not self.config.extract_functions and not self.config.extract_classes and not self.config.extract_imports:
            return {}

        # Get appropriate strategy from registry
        extractor = self.registry.get_by_language(language)
        if not extractor:
            # No extractor for this language, return empty metadata
            return {}

        # Extract metadata using strategy
        code_metadata = extractor.extract(
            content=content,
            extract_functions=self.config.extract_functions,
            extract_classes=self.config.extract_classes,
            extract_imports=self.config.extract_imports,
        )

        # Convert CodeMetadata to dict for backward compatibility
        return code_metadata.to_dict()
