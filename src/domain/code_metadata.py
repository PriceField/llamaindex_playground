"""Domain object representing extracted code metadata."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CodeMetadata:
    """Represents metadata extracted from source code.

    Replaces the primitive dict[str, list[str]] pattern for better
    type safety and explicit structure.

    Attributes:
        language: Programming language (e.g., "python", "javascript", "go")
        functions: List of function/method names with signatures
        classes: List of class names with inheritance info
        imports: List of import statements
        structs: List of struct names (for languages like Go)
        interfaces: List of interface names (for languages like Java, Go, TypeScript)
    """

    language: str
    functions: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    structs: list[str] = field(default_factory=list)
    interfaces: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate metadata."""
        if not self.language:
            raise ValueError("language cannot be empty")

    @property
    def has_functions(self) -> bool:
        """Check if any functions were extracted."""
        return len(self.functions) > 0

    @property
    def has_classes(self) -> bool:
        """Check if any classes were extracted."""
        return len(self.classes) > 0

    @property
    def has_imports(self) -> bool:
        """Check if any imports were extracted."""
        return len(self.imports) > 0

    @property
    def has_structs(self) -> bool:
        """Check if any structs were extracted."""
        return len(self.structs) > 0

    @property
    def has_interfaces(self) -> bool:
        """Check if any interfaces were extracted."""
        return len(self.interfaces) > 0

    @property
    def is_empty(self) -> bool:
        """Check if no metadata was extracted."""
        return not any([
            self.functions,
            self.classes,
            self.imports,
            self.structs,
            self.interfaces,
        ])

    def to_dict(self) -> dict[str, list[str]]:
        """Convert to legacy dict format for backward compatibility.

        Only includes non-empty lists to match original behavior.

        Returns:
            Dictionary with metadata lists
        """
        result = {}
        if self.functions:
            result["functions"] = self.functions
        if self.classes:
            result["classes"] = self.classes
        if self.imports:
            result["imports"] = self.imports
        if self.structs:
            result["structs"] = self.structs
        if self.interfaces:
            result["interfaces"] = self.interfaces
        return result

    @classmethod
    def from_dict(cls, data: dict[str, list[str]], language: str) -> "CodeMetadata":
        """Create from legacy dict format.

        Args:
            data: Dictionary with metadata lists
            language: Programming language

        Returns:
            CodeMetadata instance
        """
        return cls(
            language=language,
            functions=data.get("functions", []),
            classes=data.get("classes", []),
            imports=data.get("imports", []),
            structs=data.get("structs", []),
            interfaces=data.get("interfaces", []),
        )

    @classmethod
    def empty(cls, language: str) -> "CodeMetadata":
        """Create empty metadata for a language.

        Args:
            language: Programming language

        Returns:
            Empty CodeMetadata instance
        """
        return cls(language=language)
