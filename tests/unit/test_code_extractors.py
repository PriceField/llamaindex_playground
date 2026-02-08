"""Unit tests for code_extractors module."""
import pytest
from unittest.mock import MagicMock

from code_extractors import CodeMetadataExtractor


class TestCodeMetadataExtractor:
    """Test suite for CodeMetadataExtractor."""

    def test_extract_metadata_python(self, mock_config, sample_python_code):
        """Test metadata extraction for Python code."""
        extractor = CodeMetadataExtractor(mock_config)

        metadata = extractor.extract_metadata("test.py", sample_python_code, "python")

        assert "imports" in metadata
        assert "classes" in metadata
        # Note: sample_python_code has class methods, not top-level functions
        # So functions won't be in metadata for this sample
        assert len(metadata["imports"]) >= 1
        # Check that Calculator class is extracted
        assert any("Calculator" in cls for cls in metadata["classes"])

    def test_extract_metadata_unsupported_language(self, mock_config):
        """Test that unsupported languages return empty metadata."""
        extractor = CodeMetadataExtractor(mock_config)

        metadata = extractor.extract_metadata("test.rs", "fn main() {}", "rust")

        assert metadata == {}

    def test_extract_metadata_when_extraction_disabled(self, mock_config):
        """Test that metadata extraction is skipped when all flags are disabled."""
        mock_config.extract_functions = False
        mock_config.extract_classes = False
        mock_config.extract_imports = False

        extractor = CodeMetadataExtractor(mock_config)
        metadata = extractor.extract_metadata("test.py", "import os\nclass Foo: pass", "python")

        assert metadata == {}


class TestPythonExtraction:
    """Test suite for Python metadata extraction."""

    def test_extract_python_imports(self, mock_config):
        """Test extraction of Python import statements."""
        code = """import os
import sys
from pathlib import Path
from typing import List, Dict
"""
        extractor = CodeMetadataExtractor(mock_config)
        metadata = extractor._extract_python_metadata(code)

        assert "imports" in metadata
        imports = metadata["imports"]
        assert any("import os" in imp for imp in imports)
        assert any("import sys" in imp for imp in imports)
        assert any("from pathlib import Path" in imp for imp in imports)

    def test_extract_python_classes(self, mock_config):
        """Test extraction of Python class definitions."""
        code = """class SimpleClass:
    pass

class InheritedClass(BaseClass):
    pass

class MultipleInheritance(Base1, Base2):
    pass
"""
        extractor = CodeMetadataExtractor(mock_config)
        metadata = extractor._extract_python_metadata(code)

        assert "classes" in metadata
        classes = metadata["classes"]
        assert "SimpleClass" in classes
        assert "InheritedClass(BaseClass)" in classes
        assert "MultipleInheritance(Base1, Base2)" in classes

    def test_extract_python_functions(self, mock_config):
        """Test extraction of Python function definitions."""
        code = """def simple_function():
    pass

def function_with_params(a, b, c):
    pass

def function_with_defaults(x=10, y=20):
    pass
"""
        extractor = CodeMetadataExtractor(mock_config)
        metadata = extractor._extract_python_metadata(code)

        assert "functions" in metadata
        functions = metadata["functions"]
        assert "simple_function" in str(functions)
        assert "function_with_params(a, b, c)" in functions

    def test_extract_python_async_functions(self, mock_config):
        """Test extraction of Python async function definitions."""
        code = """async def async_function():
    pass

async def async_with_params(x, y):
    return x + y
"""
        extractor = CodeMetadataExtractor(mock_config)
        metadata = extractor._extract_python_metadata(code)

        assert "functions" in metadata
        functions = metadata["functions"]
        assert "async_function" in str(functions)
        assert "async_with_params(x, y)" in functions


class TestJavaScriptExtraction:
    """Test suite for JavaScript metadata extraction."""

    def test_extract_javascript_imports(self, mock_config):
        """Test extraction of JavaScript/TypeScript import statements."""
        code = """import React from 'react';
import { useState, useEffect } from 'react';
import * as utils from './utils';
const fs = require('fs');
const path = require('path');
"""
        extractor = CodeMetadataExtractor(mock_config)
        metadata = extractor._extract_javascript_metadata(code)

        assert "imports" in metadata
        imports = metadata["imports"]
        assert any("React" in imp and "react" in imp for imp in imports)
        assert any("require('fs')" in imp for imp in imports)

    def test_extract_javascript_classes(self, mock_config):
        """Test extraction of JavaScript class definitions."""
        code = """class SimpleClass {
    constructor() {}
}

export class ExportedClass extends BaseClass {
    render() {}
}
"""
        extractor = CodeMetadataExtractor(mock_config)
        metadata = extractor._extract_javascript_metadata(code)

        assert "classes" in metadata
        classes = metadata["classes"]
        assert "SimpleClass" in classes
        assert "ExportedClass extends BaseClass" in classes

    def test_extract_javascript_arrow_functions(self, mock_config):
        """Test extraction of JavaScript arrow functions."""
        code = """const add = (a, b) => a + b;
const multiply = (x, y) => {
    return x * y;
};
export const divide = (a, b) => a / b;
"""
        extractor = CodeMetadataExtractor(mock_config)
        metadata = extractor._extract_javascript_metadata(code)

        assert "functions" in metadata
        functions = metadata["functions"]
        assert "add(a, b)" in functions
        assert "multiply(x, y)" in functions
        assert "divide(a, b)" in functions

    def test_extract_javascript_function_declarations(self, mock_config):
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
        extractor = CodeMetadataExtractor(mock_config)
        metadata = extractor._extract_javascript_metadata(code)

        assert "functions" in metadata
        functions = metadata["functions"]
        assert "regularFunction" in str(functions)
        assert "exportedFunction(param1, param2)" in functions
        assert "asyncFunction(data)" in functions


class TestJavaExtraction:
    """Test suite for Java metadata extraction."""

    def test_extract_java_imports(self, mock_config):
        """Test extraction of Java import statements."""
        code = """import java.util.List;
import java.util.ArrayList;
import static org.junit.Assert.assertEquals;
import com.example.MyClass;
"""
        extractor = CodeMetadataExtractor(mock_config)
        metadata = extractor._extract_java_metadata(code)

        assert "imports" in metadata
        imports = metadata["imports"]
        assert "java.util.List" in imports
        assert "java.util.ArrayList" in imports
        assert "org.junit.Assert.assertEquals" in imports

    def test_extract_java_classes(self, mock_config):
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
        extractor = CodeMetadataExtractor(mock_config)
        metadata = extractor._extract_java_metadata(code)

        assert "classes" in metadata
        classes = metadata["classes"]
        assert "MyClass" in classes
        assert "AbstractClass extends BaseClass" in classes
        assert "MyInterface" in classes

    def test_extract_java_methods(self, mock_config):
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
        extractor = CodeMetadataExtractor(mock_config)
        metadata = extractor._extract_java_metadata(code)

        assert "functions" in metadata
        functions = metadata["functions"]
        # The regex matches method signatures - check that methods are found
        assert len(functions) >= 2
        assert any("add" in func for func in functions)


class TestGoExtraction:
    """Test suite for Go metadata extraction."""

    def test_extract_go_imports(self, mock_config):
        """Test extraction of Go import statements."""
        code = """import "fmt"
import "os"

import (
    "net/http"
    "encoding/json"
    log "github.com/sirupsen/logrus"
)
"""
        extractor = CodeMetadataExtractor(mock_config)
        metadata = extractor._extract_go_metadata(code)

        assert "imports" in metadata
        imports = metadata["imports"]
        assert "fmt" in imports
        assert "os" in imports
        assert "net/http" in imports
        assert "encoding/json" in imports

    def test_extract_go_functions(self, mock_config):
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
        extractor = CodeMetadataExtractor(mock_config)
        metadata = extractor._extract_go_metadata(code)

        assert "functions" in metadata
        functions = metadata["functions"]
        # Check that at least 2 functions are found
        assert len(functions) >= 2
        assert any("main" in func for func in functions)
        assert any("add" in func for func in functions)

    def test_extract_go_structs(self, mock_config):
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
        extractor = CodeMetadataExtractor(mock_config)
        metadata = extractor._extract_go_metadata(code)

        assert "structs" in metadata
        structs = metadata["structs"]
        assert "User" in structs
        assert "Config" in structs


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
