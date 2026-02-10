"""JavaScript/TypeScript metadata extraction strategy."""
import re
from domain.code_metadata import CodeMetadata
from .base import LanguageMetadataExtractor


class JavaScriptMetadataExtractor(LanguageMetadataExtractor):
    """Extract metadata from JavaScript/TypeScript source code.

    Extracts:
    - Import statements (ES6 imports and require)
    - Class definitions with inheritance
    - Function declarations and arrow functions
    """

    @property
    def language(self) -> str:
        """Return language name."""
        return "javascript"

    @property
    def supported_extensions(self) -> list[str]:
        """Return supported file extensions."""
        return [".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"]

    def extract(
        self,
        content: str,
        extract_functions: bool = True,
        extract_classes: bool = True,
        extract_imports: bool = True,
    ) -> CodeMetadata:
        """Extract JavaScript/TypeScript metadata.

        Args:
            content: JavaScript/TypeScript source code
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
            content: JavaScript/TypeScript source code

        Returns:
            List of import statements
        """
        imports = []

        # ES6 imports
        import_pattern = r'^import\s+(?:{[^}]+}|\S+)\s+from\s+["\']([^"\']+)["\']'
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            imports.append(match.group(0))

        # Require statements
        require_pattern = r'require\(["\']([^"\']+)["\']\)'
        for match in re.finditer(require_pattern, content):
            imports.append(match.group(0))

        return imports

    def _extract_classes(self, content: str) -> list[str]:
        """Extract class definitions.

        Args:
            content: JavaScript/TypeScript source code

        Returns:
            List of class names with inheritance info
        """
        classes = []
        class_pattern = r'^(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?'

        for match in re.finditer(class_pattern, content, re.MULTILINE):
            class_name = match.group(1)
            extends = f" extends {match.group(2)}" if match.group(2) else ""
            classes.append(f"{class_name}{extends}")

        return classes

    def _extract_functions(self, content: str) -> list[str]:
        """Extract function definitions.

        Args:
            content: JavaScript/TypeScript source code

        Returns:
            List of function signatures
        """
        functions = []

        # Function declarations
        func_pattern = r'^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(func_pattern, content, re.MULTILINE):
            func_name = match.group(1)
            params = match.group(2).strip()
            if params:
                functions.append(f"{func_name}({params})")
            else:
                functions.append(func_name)

        # Arrow functions assigned to const/let/var
        arrow_pattern = r'^(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>'
        for match in re.finditer(arrow_pattern, content, re.MULTILINE):
            func_name = match.group(1)
            params = match.group(2).strip()
            if params:
                functions.append(f"{func_name}({params})")
            else:
                functions.append(func_name)

        return functions
