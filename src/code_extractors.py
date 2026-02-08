"""Extract code-specific metadata from source files."""
import re


class CodeMetadataExtractor:
    """Extract metadata from code files (functions, classes, imports)."""

    def __init__(self, config):
        """Initialize with configuration.

        Args:
            config: IndexerConfig instance
        """
        self.config = config

    def extract_metadata(self, file_path: str, content: str, language: str) -> dict:
        """Extract code metadata based on language.

        Args:
            file_path: Path to the file
            content: File content
            language: Programming language

        Returns:
            Dictionary containing extracted metadata (functions, classes, imports)
        """
        metadata = {}

        if not self.config.extract_functions and not self.config.extract_classes and not self.config.extract_imports:
            return metadata

        # Dispatch to language-specific extractors
        if language == "python":
            metadata = self._extract_python_metadata(content)
        elif language in ["javascript", "typescript"]:
            metadata = self._extract_javascript_metadata(content)
        elif language == "java":
            metadata = self._extract_java_metadata(content)
        elif language == "go":
            metadata = self._extract_go_metadata(content)
        # Add more languages as needed

        return metadata

    def _extract_python_metadata(self, content: str) -> dict:
        """Extract Python-specific metadata.

        Args:
            content: Python source code

        Returns:
            Dictionary with imports, classes, and functions
        """
        metadata = {}

        if self.config.extract_imports:
            # Extract imports
            imports = []
            import_pattern = r'^(?:from\s+(\S+)\s+)?import\s+(.+)$'
            for match in re.finditer(import_pattern, content, re.MULTILINE):
                if match.group(1):
                    imports.append(f"from {match.group(1)} import {match.group(2)}")
                else:
                    imports.append(f"import {match.group(2)}")
            if imports:
                metadata["imports"] = imports

        if self.config.extract_classes:
            # Extract class definitions
            classes = []
            class_pattern = r'^class\s+(\w+)(?:\(([^)]*)\))?:'
            for match in re.finditer(class_pattern, content, re.MULTILINE):
                class_name = match.group(1)
                base_classes = match.group(2) if match.group(2) else ""
                classes.append(f"{class_name}({base_classes})" if base_classes else class_name)
            if classes:
                metadata["classes"] = classes

        if self.config.extract_functions:
            # Extract function definitions
            functions = []
            func_pattern = r'^(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\)'
            for match in re.finditer(func_pattern, content, re.MULTILINE):
                func_name = match.group(1)
                params = match.group(2).strip()
                functions.append(f"{func_name}({params})" if params else func_name)
            if functions:
                metadata["functions"] = functions

        return metadata

    def _extract_javascript_metadata(self, content: str) -> dict:
        """Extract JavaScript/TypeScript metadata.

        Args:
            content: JavaScript/TypeScript source code

        Returns:
            Dictionary with imports, classes, and functions
        """
        metadata = {}

        if self.config.extract_imports:
            imports = []
            # ES6 imports
            import_pattern = r'^import\s+(?:{[^}]+}|\S+)\s+from\s+["\']([^"\']+)["\']'
            for match in re.finditer(import_pattern, content, re.MULTILINE):
                imports.append(match.group(0))
            # Require statements
            require_pattern = r'require\(["\']([^"\']+)["\']\)'
            for match in re.finditer(require_pattern, content):
                imports.append(match.group(0))
            if imports:
                metadata["imports"] = imports

        if self.config.extract_classes:
            classes = []
            class_pattern = r'^(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?'
            for match in re.finditer(class_pattern, content, re.MULTILINE):
                class_name = match.group(1)
                extends = f" extends {match.group(2)}" if match.group(2) else ""
                classes.append(f"{class_name}{extends}")
            if classes:
                metadata["classes"] = classes

        if self.config.extract_functions:
            functions = []
            # Function declarations
            func_pattern = r'^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)'
            for match in re.finditer(func_pattern, content, re.MULTILINE):
                func_name = match.group(1)
                params = match.group(2).strip()
                functions.append(f"{func_name}({params})" if params else func_name)
            # Arrow functions assigned to const/let/var
            arrow_pattern = r'^(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>'
            for match in re.finditer(arrow_pattern, content, re.MULTILINE):
                func_name = match.group(1)
                params = match.group(2).strip()
                functions.append(f"{func_name}({params})" if params else func_name)
            if functions:
                metadata["functions"] = functions

        return metadata

    def _extract_java_metadata(self, content: str) -> dict:
        """Extract Java metadata.

        Args:
            content: Java source code

        Returns:
            Dictionary with imports, classes, and functions
        """
        metadata = {}

        if self.config.extract_imports:
            imports = []
            import_pattern = r'^import\s+(?:static\s+)?([^;]+);'
            for match in re.finditer(import_pattern, content, re.MULTILINE):
                imports.append(match.group(1).strip())
            if imports:
                metadata["imports"] = imports

        if self.config.extract_classes:
            classes = []
            class_pattern = r'^(?:public\s+)?(?:abstract\s+)?(?:class|interface)\s+(\w+)(?:\s+extends\s+(\w+))?'
            for match in re.finditer(class_pattern, content, re.MULTILINE):
                class_name = match.group(1)
                extends = f" extends {match.group(2)}" if match.group(2) else ""
                classes.append(f"{class_name}{extends}")
            if classes:
                metadata["classes"] = classes

        if self.config.extract_functions:
            functions = []
            # Method declarations
            method_pattern = r'(?:public|private|protected)\s+(?:static\s+)?(?:\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)'
            for match in re.finditer(method_pattern, content):
                func_name = match.group(1)
                params = match.group(2).strip()
                functions.append(f"{func_name}({params})" if params else func_name)
            if functions:
                metadata["functions"] = functions

        return metadata

    def _extract_go_metadata(self, content: str) -> dict:
        """Extract Go metadata.

        Args:
            content: Go source code

        Returns:
            Dictionary with imports, functions, and structs
        """
        metadata = {}

        if self.config.extract_imports:
            imports = []
            # Single import
            import_pattern = r'^import\s+"([^"]+)"'
            for match in re.finditer(import_pattern, content, re.MULTILINE):
                imports.append(match.group(1))
            # Multi-line import
            multi_import_pattern = r'import\s+\(([\s\S]*?)\)'
            for match in re.finditer(multi_import_pattern, content):
                import_block = match.group(1)
                for line in import_block.split('\n'):
                    line = line.strip()
                    if line and '"' in line:
                        pkg = re.search(r'"([^"]+)"', line)
                        if pkg:
                            imports.append(pkg.group(1))
            if imports:
                metadata["imports"] = imports

        if self.config.extract_functions:
            functions = []
            # Function declarations (including methods)
            func_pattern = r'^func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(([^)]*)\)'
            for match in re.finditer(func_pattern, content, re.MULTILINE):
                func_name = match.group(1)
                params = match.group(2).strip()
                functions.append(f"{func_name}({params})" if params else func_name)
            if functions:
                metadata["functions"] = functions

        if self.config.extract_classes:
            # Go uses structs instead of classes
            structs = []
            struct_pattern = r'^type\s+(\w+)\s+struct'
            for match in re.finditer(struct_pattern, content, re.MULTILINE):
                structs.append(match.group(1))
            if structs:
                metadata["structs"] = structs

        return metadata
