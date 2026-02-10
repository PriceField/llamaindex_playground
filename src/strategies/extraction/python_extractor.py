"""Python metadata extraction strategy."""
import re
from domain.code_metadata import CodeMetadata
from .base import LanguageMetadataExtractor


class PythonMetadataExtractor(LanguageMetadataExtractor):
    """Extract metadata from Python source code.

    Extracts:
    - Import statements (import X, from X import Y)
    - Class definitions with inheritance
    - Function definitions (including async functions)
    """

    @property
    def language(self) -> str:
        """Return language name."""
        return "python"

    @property
    def supported_extensions(self) -> list[str]:
        """Return supported file extensions."""
        return [".py", ".pyw"]

    def extract(
        self,
        content: str,
        extract_functions: bool = True,
        extract_classes: bool = True,
        extract_imports: bool = True,
    ) -> CodeMetadata:
        """Extract Python metadata.

        Args:
            content: Python source code
            extract_functions: Whether to extract function definitions
            extract_classes: Whether to extract class definitions
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
            language=self.language,
            functions=functions,
            classes=classes,
            imports=imports,
        )

    def _extract_imports(self, content: str) -> list[str]:
        """Extract import statements.

        Args:
            content: Python source code

        Returns:
            List of import statements
        """
        imports = []
        import_pattern = r'^(?:from\s+(\S+)\s+)?import\s+(.+)$'

        for match in re.finditer(import_pattern, content, re.MULTILINE):
            if match.group(1):
                imports.append(f"from {match.group(1)} import {match.group(2)}")
            else:
                imports.append(f"import {match.group(2)}")

        return imports

    def _extract_classes(self, content: str) -> list[str]:
        """Extract class definitions.

        Args:
            content: Python source code

        Returns:
            List of class names with inheritance info
        """
        classes = []
        class_pattern = r'^class\s+(\w+)(?:\(([^)]*)\))?:'

        for match in re.finditer(class_pattern, content, re.MULTILINE):
            class_name = match.group(1)
            base_classes = match.group(2) if match.group(2) else ""
            if base_classes:
                classes.append(f"{class_name}({base_classes})")
            else:
                classes.append(class_name)

        return classes

    def _extract_functions(self, content: str) -> list[str]:
        """Extract function definitions.

        Args:
            content: Python source code

        Returns:
            List of function signatures
        """
        functions = []
        func_pattern = r'^(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\)'

        for match in re.finditer(func_pattern, content, re.MULTILINE):
            func_name = match.group(1)
            params = match.group(2).strip()
            if params:
                functions.append(f"{func_name}({params})")
            else:
                functions.append(func_name)

        return functions
