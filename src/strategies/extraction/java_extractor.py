"""Java metadata extraction strategy."""
import re
from domain.code_metadata import CodeMetadata
from .base import LanguageMetadataExtractor


class JavaMetadataExtractor(LanguageMetadataExtractor):
    """Extract metadata from Java source code.

    Extracts:
    - Import statements
    - Class and interface definitions with inheritance
    - Method declarations
    """

    @property
    def language(self) -> str:
        """Return language name."""
        return "java"

    @property
    def supported_extensions(self) -> list[str]:
        """Return supported file extensions."""
        return [".java"]

    def extract(
        self,
        content: str,
        extract_functions: bool = True,
        extract_classes: bool = True,
        extract_imports: bool = True,
    ) -> CodeMetadata:
        """Extract Java metadata.

        Args:
            content: Java source code
            extract_functions: Whether to extract method definitions
            extract_classes: Whether to extract class/interface definitions
            extract_imports: Whether to extract import statements

        Returns:
            CodeMetadata with extracted information
        """
        functions = []
        classes = []
        imports = []

        if extract_imports:
            imports = self._extract_imports(content)

        if extract_classes:
            classes = self._extract_classes(content)

        if extract_functions:
            functions = self._extract_functions(content)

        return CodeMetadata(
            functions=functions,
            classes=classes,
            imports=imports,
            language=self.language,
            category="code",
        )

    def _extract_imports(self, content: str) -> list[str]:
        """Extract import statements.

        Args:
            content: Java source code

        Returns:
            List of import statements
        """
        imports = []
        import_pattern = r'^import\s+(?:static\s+)?([^;]+);'

        for match in re.finditer(import_pattern, content, re.MULTILINE):
            imports.append(match.group(1).strip())

        return imports

    def _extract_classes(self, content: str) -> list[str]:
        """Extract class and interface definitions.

        Args:
            content: Java source code

        Returns:
            List of class/interface names with inheritance info
        """
        classes = []
        class_pattern = r'^(?:public\s+)?(?:abstract\s+)?(?:class|interface)\s+(\w+)(?:\s+extends\s+(\w+))?'

        for match in re.finditer(class_pattern, content, re.MULTILINE):
            class_name = match.group(1)
            extends = f" extends {match.group(2)}" if match.group(2) else ""
            classes.append(f"{class_name}{extends}")

        return classes

    def _extract_functions(self, content: str) -> list[str]:
        """Extract method declarations.

        Args:
            content: Java source code

        Returns:
            List of method signatures
        """
        functions = []
        method_pattern = r'(?:public|private|protected)\s+(?:static\s+)?(?:\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)'

        for match in re.finditer(method_pattern, content):
            func_name = match.group(1)
            params = match.group(2).strip()
            if params:
                functions.append(f"{func_name}({params})")
            else:
                functions.append(func_name)

        return functions
