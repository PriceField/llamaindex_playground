"""Unit tests for code_chunking module."""
import sys
import pytest
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.insert(0, 'src')

from code_chunking import CodeAwareNodeParser
from llama_index.core import Document
from llama_index.core.schema import TextNode


class TestCodeAwareNodeParser:
    """Test suite for CodeAwareNodeParser."""

    def test_parse_nodes_with_code_document(self, mock_config):
        """Test parsing nodes with code category preserves structure."""
        mock_config.preserve_code_structure = True
        parser = CodeAwareNodeParser(mock_config)

        code_content = """def hello():
    print("Hello, World!")
"""
        doc = Document(
            text=code_content,
            metadata={"language": "python", "category": "code"}
        )

        nodes = parser._parse_nodes([doc])

        assert len(nodes) > 0
        assert all(isinstance(node, TextNode) for node in nodes)
        # Just verify it contains the function name
        assert "hello" in nodes[0].text

    def test_parse_nodes_with_non_code_document(self, mock_config):
        """Test parsing non-code documents uses generic chunking."""
        mock_config.preserve_code_structure = True
        parser = CodeAwareNodeParser(mock_config)

        doc_content = "This is a documentation file with some text content."
        doc = Document(
            text=doc_content,
            metadata={"language": "unknown", "category": "documentation"}
        )

        with patch('code_chunking.SentenceSplitter') as mock_splitter:
            mock_splitter_instance = MagicMock()
            mock_splitter_instance.get_nodes_from_documents.return_value = [
                TextNode(text=doc_content, metadata={})
            ]
            mock_splitter.return_value = mock_splitter_instance

            nodes = parser._parse_nodes([doc])

            mock_splitter.assert_called_once()
            assert len(nodes) > 0

    def test_parse_nodes_preserve_structure_disabled(self, mock_config):
        """Test that disabling preserve_code_structure uses generic chunking."""
        mock_config.preserve_code_structure = False
        parser = CodeAwareNodeParser(mock_config)

        doc = Document(
            text="def test(): pass",
            metadata={"language": "python", "category": "code"}
        )

        with patch('code_chunking.SentenceSplitter') as mock_splitter:
            mock_splitter_instance = MagicMock()
            mock_splitter_instance.get_nodes_from_documents.return_value = [
                TextNode(text="def test(): pass", metadata={})
            ]
            mock_splitter.return_value = mock_splitter_instance

            nodes = parser._parse_nodes([doc])

            mock_splitter.assert_called_once()


class TestPythonChunking:
    """Test suite for Python code chunking."""

    def test_chunk_python_single_function(self, mock_config):
        """Test chunking a single Python function."""
        parser = CodeAwareNodeParser(mock_config)

        code = """def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
"""
        chunks = parser._chunk_python(code)

        assert len(chunks) >= 1
        chunk_text, start_line, end_line = chunks[0]
        assert "calculate_sum" in chunk_text
        assert start_line == 1
        assert end_line >= 1

    def test_chunk_python_multiple_functions(self, mock_config):
        """Test chunking multiple Python functions."""
        parser = CodeAwareNodeParser(mock_config)

        code = """def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b != 0:
        return a / b
    return None
"""
        chunks = parser._chunk_python(code)

        assert len(chunks) >= 3
        chunk_texts = [chunk[0] for chunk in chunks]
        assert any("add" in text for text in chunk_texts)
        assert any("multiply" in text for text in chunk_texts)
        assert any("divide" in text for text in chunk_texts)

    def test_chunk_python_class_with_methods(self, mock_config):
        """Test chunking a Python class with methods."""
        parser = CodeAwareNodeParser(mock_config)

        code = """class Calculator:
    def __init__(self):
        self.result = 0

    def add(self, value):
        self.result += value
        return self.result

    def reset(self):
        self.result = 0
"""
        chunks = parser._chunk_python(code)

        assert len(chunks) >= 1
        # Class and its methods should be in chunks
        chunk_text = chunks[0][0]
        assert "Calculator" in chunk_text

    def test_chunk_python_mixed_code_and_comments(self, mock_config):
        """Test chunking Python code with comments and docstrings."""
        parser = CodeAwareNodeParser(mock_config)

        code = """# This is a module for math operations

def add(a, b):
    '''Add two numbers.'''
    return a + b

# Another comment
def subtract(a, b):
    return a - b
"""
        chunks = parser._chunk_python(code)

        assert len(chunks) >= 2
        # Comments should be preserved with their functions
        chunk_texts = [chunk[0] for chunk in chunks]
        assert any("add" in text for text in chunk_texts)

    def test_chunk_python_large_chunk_splitting(self, mock_config):
        """Test that large chunks are split when exceeding size limits."""
        mock_config.code_chunk_size = 100  # Small chunk size for testing
        parser = CodeAwareNodeParser(mock_config)

        # Create a large code block
        large_code = "\n".join([f"# Comment line {i}" for i in range(50)])
        large_code += "\ndef function():\n    pass\n"

        chunks = parser._chunk_python(large_code)

        # Should be split into multiple chunks
        assert len(chunks) >= 2

    def test_chunk_python_async_functions(self, mock_config):
        """Test chunking async Python functions."""
        parser = CodeAwareNodeParser(mock_config)

        code = """async def fetch_data(url):
    response = await http_get(url)
    return response.json()

async def process_data(data):
    return await transform(data)
"""
        chunks = parser._chunk_python(code)

        assert len(chunks) >= 2
        chunk_texts = [chunk[0] for chunk in chunks]
        assert any("fetch_data" in text for text in chunk_texts)
        assert any("process_data" in text for text in chunk_texts)


class TestJavaScriptChunking:
    """Test suite for JavaScript chunking."""

    def test_chunk_javascript_functions(self, mock_config):
        """Test chunking JavaScript function declarations."""
        parser = CodeAwareNodeParser(mock_config)

        code = """function add(a, b) {
    return a + b;
}

function multiply(x, y) {
    return x * y;
}
"""
        chunks = parser._chunk_javascript(code)

        assert len(chunks) >= 2
        chunk_texts = [chunk[0] for chunk in chunks]
        assert any("add" in text for text in chunk_texts)
        assert any("multiply" in text for text in chunk_texts)

    def test_chunk_javascript_classes(self, mock_config):
        """Test chunking JavaScript classes."""
        parser = CodeAwareNodeParser(mock_config)

        code = """class Calculator {
    constructor() {
        this.result = 0;
    }

    add(value) {
        this.result += value;
        return this.result;
    }

    reset() {
        this.result = 0;
    }
}
"""
        chunks = parser._chunk_javascript(code)

        assert len(chunks) >= 1
        assert "Calculator" in chunks[0][0]
        assert "constructor" in chunks[0][0]

    def test_chunk_javascript_arrow_functions(self, mock_config):
        """Test chunking JavaScript arrow functions."""
        parser = CodeAwareNodeParser(mock_config)

        code = """const add = (a, b) => {
    return a + b;
}

const multiply = (x, y) => {
    return x * y;
}
"""
        chunks = parser._chunk_javascript(code)

        assert len(chunks) >= 2
        chunk_texts = [chunk[0] for chunk in chunks]
        assert any("add" in text for text in chunk_texts)
        assert any("multiply" in text for text in chunk_texts)

    def test_chunk_javascript_nested_braces(self, mock_config):
        """Test chunking JavaScript code with nested braces."""
        parser = CodeAwareNodeParser(mock_config)

        code = """function processData(data) {
    if (data) {
        for (let item of data) {
            if (item.valid) {
                console.log(item);
            }
        }
    }
    return data;
}
"""
        chunks = parser._chunk_javascript(code)

        assert len(chunks) >= 1
        # Should keep function together despite nested braces
        assert "processData" in chunks[0][0]
        assert chunks[0][0].count("{") == chunks[0][0].count("}")


class TestGenericChunking:
    """Test suite for generic chunking."""

    def test_chunk_generic_documentation(self, mock_config):
        """Test generic chunking for documentation files."""
        mock_config.doc_chunk_size = 1024
        mock_config.doc_chunk_overlap = 20
        parser = CodeAwareNodeParser(mock_config)

        doc_content = "This is a documentation file. " * 50
        doc = Document(
            text=doc_content,
            metadata={"category": "documentation"}
        )

        with patch('code_chunking.SentenceSplitter') as mock_splitter:
            mock_splitter_instance = MagicMock()
            mock_splitter_instance.get_nodes_from_documents.return_value = [
                TextNode(text=doc_content, metadata={})
            ]
            mock_splitter.return_value = mock_splitter_instance

            nodes = parser._chunk_generic(doc)

            # Verify SentenceSplitter was called with doc chunk size
            mock_splitter.assert_called_once_with(
                chunk_size=1024,
                chunk_overlap=20
            )
            assert len(nodes) > 0

    def test_chunk_generic_other_files(self, mock_config):
        """Test generic chunking for other file types."""
        mock_config.code_chunk_size = 512
        mock_config.code_chunk_overlap = 50
        parser = CodeAwareNodeParser(mock_config)

        content = "Some configuration content. " * 30
        doc = Document(
            text=content,
            metadata={"category": "configuration"}
        )

        with patch('code_chunking.SentenceSplitter') as mock_splitter:
            mock_splitter_instance = MagicMock()
            mock_splitter_instance.get_nodes_from_documents.return_value = [
                TextNode(text=content, metadata={})
            ]
            mock_splitter.return_value = mock_splitter_instance

            nodes = parser._chunk_generic(doc)

            # Should use code chunk size for non-documentation
            mock_splitter.assert_called_once_with(
                chunk_size=512,
                chunk_overlap=50
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
