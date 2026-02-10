"""Unit tests for metadata extraction strategies."""
import pytest
from pathlib import Path

from strategies.extraction import (
    PythonMetadataExtractor,
    JavaScriptMetadataExtractor,
    JavaMetadataExtractor,
    GoMetadataExtractor,
    MetadataExtractorRegistry,
)
from domain import CodeMetadata


class TestMetadataExtractorRegistry:
    """Test suite for MetadataExtractorRegistry."""

    def test_registry_lookup_python(self):
        """Test registry lookup for Python extractor."""
        registry = MetadataExtractorRegistry()
        extractor = registry.get_by_extension(Path("test.py").suffix)
        assert isinstance(extractor, PythonMetadataExtractor)

    def test_registry_lookup_javascript(self):
        """Test registry lookup for JavaScript extractor."""
        registry = MetadataExtractorRegistry()
        extractor = registry.get_by_extension(Path("app.js").suffix)
        assert isinstance(extractor, JavaScriptMetadataExtractor)

    def test_registry_lookup_typescript(self):
        """Test registry lookup for TypeScript extractor."""
        registry = MetadataExtractorRegistry()
        extractor = registry.get_by_extension(Path("Component.tsx").suffix)
        assert isinstance(extractor, JavaScriptMetadataExtractor)

    def test_registry_lookup_java(self):
        """Test registry lookup for Java extractor."""
        registry = MetadataExtractorRegistry()
        extractor = registry.get_by_extension(Path("Main.java").suffix)
        assert isinstance(extractor, JavaMetadataExtractor)

    def test_registry_lookup_go(self):
        """Test registry lookup for Go extractor."""
        registry = MetadataExtractorRegistry()
        extractor = registry.get_by_extension(Path("main.go").suffix)
        assert isinstance(extractor, GoMetadataExtractor)

    def test_registry_lookup_unsupported_returns_none(self):
        """Test that unsupported file extensions return None."""
        registry = MetadataExtractorRegistry()
        extractor = registry.get_by_extension(Path("file.xyz").suffix)
        assert extractor is None

    def test_registry_all_extractors_registered(self):
        """Test that all expected extractors are registered."""
        registry = MetadataExtractorRegistry()
        # Should have extractors for Python, JavaScript, Java, Go
        assert len(registry._extractors) >= 4


class TestPythonExtraction:
    """Test suite for Python metadata extraction."""

    def test_extract_python_imports(self):
        """Test extraction of Python import statements."""
        code = """import os
import sys
from pathlib import Path
from typing import List, Dict
"""
        extractor = PythonMetadataExtractor()
        metadata = extractor.extract(code, extract_functions=True, extract_classes=True, extract_imports=True)

        assert isinstance(metadata, CodeMetadata)
        assert metadata.language == "python"
        imports = metadata.imports
        assert any("import os" in imp for imp in imports)
        assert any("import sys" in imp for imp in imports)
        assert any("from pathlib import Path" in imp for imp in imports)

    def test_extract_python_classes(self):
        """Test extraction of Python class definitions."""
        code = """class SimpleClass:
    pass

class InheritedClass(BaseClass):
    pass

class MultipleInheritance(Base1, Base2):
    pass
"""
        extractor = PythonMetadataExtractor()
        metadata = extractor.extract(code, extract_functions=True, extract_classes=True, extract_imports=True)

        classes = metadata.classes
        assert "SimpleClass" in classes
        assert "InheritedClass(BaseClass)" in classes
        assert "MultipleInheritance(Base1, Base2)" in classes

    def test_extract_python_functions(self):
        """Test extraction of Python function definitions."""
        code = """def simple_function():
    pass

def function_with_params(a, b, c):
    pass

def function_with_defaults(x=10, y=20):
    pass
"""
        extractor = PythonMetadataExtractor()
        metadata = extractor.extract(code, extract_functions=True, extract_classes=True, extract_imports=True)

        functions = metadata.functions
        assert "simple_function" in str(functions)
        assert "function_with_params(a, b, c)" in functions

    def test_extract_python_async_functions(self):
        """Test extraction of Python async function definitions."""
        code = """async def async_function():
    pass

async def async_with_params(x, y):
    return x + y
"""
        extractor = PythonMetadataExtractor()
        metadata = extractor.extract(code, extract_functions=True, extract_classes=True, extract_imports=True)

        functions = metadata.functions
        assert "async_function" in str(functions)
        assert "async_with_params(x, y)" in functions

    def test_extract_with_functions_disabled(self):
        """Test that function extraction can be disabled."""
        code = """def my_function():
    pass
"""
        extractor = PythonMetadataExtractor()
        metadata = extractor.extract(code, extract_functions=False, extract_classes=True, extract_imports=True)

        assert len(metadata.functions) == 0

    def test_extract_with_classes_disabled(self):
        """Test that class extraction can be disabled."""
        code = """class MyClass:
    pass
"""
        extractor = PythonMetadataExtractor()
        metadata = extractor.extract(code, extract_functions=True, extract_classes=False, extract_imports=True)

        assert len(metadata.classes) == 0

    def test_extract_with_imports_disabled(self):
        """Test that import extraction can be disabled."""
        code = """import os
"""
        extractor = PythonMetadataExtractor()
        metadata = extractor.extract(code, extract_functions=True, extract_classes=True, extract_imports=False)

        assert len(metadata.imports) == 0


class TestJavaScriptExtraction:
    """Test suite for JavaScript metadata extraction."""

    def test_extract_javascript_imports(self):
        """Test extraction of JavaScript/TypeScript import statements."""
        code = """import React from 'react';
import { useState, useEffect } from 'react';
import * as utils from './utils';
const fs = require('fs');
const path = require('path');
"""
        extractor = JavaScriptMetadataExtractor()
        metadata = extractor.extract(code, extract_functions=True, extract_classes=True, extract_imports=True)

        assert metadata.language == "javascript"
        imports = metadata.imports
        assert any("React" in imp and "react" in imp for imp in imports)
        assert any("require('fs')" in imp for imp in imports)

    def test_extract_javascript_classes(self):
        """Test extraction of JavaScript class definitions."""
        code = """class SimpleClass {
    constructor() {}
}

export class ExportedClass extends BaseClass {
    render() {}
}
"""
        extractor = JavaScriptMetadataExtractor()
        metadata = extractor.extract(code, extract_functions=True, extract_classes=True, extract_imports=True)

        classes = metadata.classes
        assert "SimpleClass" in classes
        assert "ExportedClass extends BaseClass" in classes

    def test_extract_javascript_arrow_functions(self):
        """Test extraction of JavaScript arrow functions."""
        code = """const add = (a, b) => a + b;
const multiply = (x, y) => {
    return x * y;
};
export const divide = (a, b) => a / b;
"""
        extractor = JavaScriptMetadataExtractor()
        metadata = extractor.extract(code, extract_functions=True, extract_classes=True, extract_imports=True)

        functions = metadata.functions
        assert "add(a, b)" in functions
        assert "multiply(x, y)" in functions
        assert "divide(a, b)" in functions

    def test_extract_javascript_function_declarations(self):
        """Test extraction of JavaScript function declarations."""
        code = """function regularFunction() {
    return true;
}

export function exportedFunction(param1, param2) {
    console.log(param1, param2);
}

async function asyncFunction(data) {
    return await process(data);
}
"""
        extractor = JavaScriptMetadataExtractor()
        metadata = extractor.extract(code, extract_functions=True, extract_classes=True, extract_imports=True)

        functions = metadata.functions
        assert "regularFunction" in str(functions)
        assert "exportedFunction(param1, param2)" in functions
        assert "asyncFunction(data)" in functions


class TestJavaExtraction:
    """Test suite for Java metadata extraction."""

    def test_extract_java_imports(self):
        """Test extraction of Java import statements."""
        code = """import java.util.List;
import java.util.ArrayList;
import static org.junit.Assert.assertEquals;
import com.example.MyClass;
"""
        extractor = JavaMetadataExtractor()
        metadata = extractor.extract(code, extract_functions=True, extract_classes=True, extract_imports=True)

        assert metadata.language == "java"
        imports = metadata.imports
        assert "java.util.List" in imports
        assert "java.util.ArrayList" in imports
        assert "org.junit.Assert.assertEquals" in imports

    def test_extract_java_classes(self):
        """Test extraction of Java class and interface definitions."""
        code = """public class MyClass {
    public void method() {}
}

public abstract class AbstractClass extends BaseClass {
    abstract void abstractMethod();
}

public interface MyInterface {
    void interfaceMethod();
}
"""
        extractor = JavaMetadataExtractor()
        metadata = extractor.extract(code, extract_functions=True, extract_classes=True, extract_imports=True)

        classes = metadata.classes
        assert "MyClass" in classes
        assert "AbstractClass extends BaseClass" in classes
        # Interfaces should be in interfaces field, not classes
        assert "MyInterface" in metadata.interfaces

    def test_extract_java_methods(self):
        """Test extraction of Java method definitions."""
        code = """public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }

    private static String formatResult(int result) {
        return String.valueOf(result);
    }

    protected List<Integer> getNumbers() {
        return new ArrayList<>();
    }
}
"""
        extractor = JavaMetadataExtractor()
        metadata = extractor.extract(code, extract_functions=True, extract_classes=True, extract_imports=True)

        functions = metadata.functions
        # The regex matches method signatures - check that methods are found
        assert len(functions) >= 2
        assert any("add" in func for func in functions)


class TestGoExtraction:
    """Test suite for Go metadata extraction."""

    def test_extract_go_imports(self):
        """Test extraction of Go import statements."""
        code = """import "fmt"
import "os"

import (
    "net/http"
    "encoding/json"
    log "github.com/sirupsen/logrus"
)
"""
        extractor = GoMetadataExtractor()
        metadata = extractor.extract(code, extract_functions=True, extract_classes=True, extract_imports=True)

        assert metadata.language == "go"
        imports = metadata.imports
        assert "fmt" in imports
        assert "os" in imports
        assert "net/http" in imports
        assert "encoding/json" in imports

    def test_extract_go_functions(self):
        """Test extraction of Go function definitions."""
        code = """func main() {
    fmt.Println("Hello")
}

func add(a int, b int) int {
    return a + b
}

func (s *Server) HandleRequest(w http.ResponseWriter, r *http.Request) {
    // method with receiver
}
"""
        extractor = GoMetadataExtractor()
        metadata = extractor.extract(code, extract_functions=True, extract_classes=True, extract_imports=True)

        functions = metadata.functions
        # Check that at least 2 functions are found
        assert len(functions) >= 2
        assert any("main" in func for func in functions)
        assert any("add" in func for func in functions)

    def test_extract_go_structs(self):
        """Test extraction of Go struct definitions."""
        code = """type User struct {
    ID   int
    Name string
}

type Config struct {
    Host string
    Port int
}
"""
        extractor = GoMetadataExtractor()
        metadata = extractor.extract(code, extract_functions=True, extract_classes=True, extract_imports=True)

        # Go structs are stored in the structs field
        # But they may also appear in classes for compatibility
        # Check the actual returned metadata structure
        if metadata.structs:
            structs = metadata.structs
            assert "User" in structs
            assert "Config" in structs
        else:
            # If using classes field for backward compatibility
            classes = metadata.classes
            assert "User" in classes
            assert "Config" in classes


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
