"""Go metadata extraction strategy."""
import re
from domain.code_metadata import CodeMetadata
from .base import LanguageMetadataExtractor


class GoMetadataExtractor(LanguageMetadataExtractor):
    """Extract metadata from Go source code.

    Extracts:
    - Import statements (single and multi-line)
    - Struct definitions (Go's equivalent to classes)
    - Function declarations (including methods)
    """

    @property
    def language(self) -> str:
        """Return language name."""
        return "go"

    @property
    def supported_extensions(self) -> list[str]:
        """Return supported file extensions."""
        return [".go"]

    def extract(
        self,
        content: str,
        extract_functions: bool = True,
        extract_classes: bool = True,
        extract_imports: bool = True,
    ) -> CodeMetadata:
        """Extract Go metadata.

        Args:
            content: Go source code
            extract_functions: Whether to extract function definitions
            extract_classes: Whether to extract struct definitions
            extract_imports: Whether to extract import statements

        Returns:
            CodeMetadata with extracted information
        """
        functions = []
        structs = []
        imports = []

        if extract_imports:
            imports = self._extract_imports(content)

        if extract_classes:
            structs = self._extract_structs(content)

        if extract_functions:
            functions = self._extract_functions(content)

        # Go uses "structs" field instead of "classes"
        return CodeMetadata(
            language=self.language,
            functions=functions,
            classes=structs,  # Note: mapping structs to classes field
            imports=imports,
        )

    def _extract_imports(self, content: str) -> list[str]:
        """Extract import statements.

        Args:
            content: Go source code

        Returns:
            List of imported packages
        """
        imports = []

        # Single import
        import_pattern = r'^import\s+"([^"]+)"'
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            imports.append(match.group(1))

        # Multi-line import block
        multi_import_pattern = r'import\s+\(([\s\S]*?)\)'
        for match in re.finditer(multi_import_pattern, content):
            import_block = match.group(1)
            for line in import_block.split('\n'):
                line = line.strip()
                if line and '"' in line:
                    pkg = re.search(r'"([^"]+)"', line)
                    if pkg:
                        imports.append(pkg.group(1))

        return imports

    def _extract_structs(self, content: str) -> list[str]:
        """Extract struct definitions.

        Args:
            content: Go source code

        Returns:
            List of struct names
        """
        structs = []
        struct_pattern = r'^type\s+(\w+)\s+struct'

        for match in re.finditer(struct_pattern, content, re.MULTILINE):
            structs.append(match.group(1))

        return structs

    def _extract_functions(self, content: str) -> list[str]:
        """Extract function declarations.

        Args:
            content: Go source code

        Returns:
            List of function signatures (including methods)
        """
        functions = []
        # Function pattern includes both regular functions and methods
        func_pattern = r'^func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(([^)]*)\)'

        for match in re.finditer(func_pattern, content, re.MULTILINE):
            func_name = match.group(1)
            params = match.group(2).strip()
            if params:
                functions.append(f"{func_name}({params})")
            else:
                functions.append(func_name)

        return functions
