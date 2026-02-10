"""Unit tests for code chunking strategies."""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from strategies.chunking import (
    PythonChunker,
    JavaScriptChunker,
    JavaChunker,
    GoChunker,
    ChunkerRegistry,
)
from domain import CodeChunk
from config import ChunkingConfig
from code_chunking import CodeAwareNodeParser
from llama_index.core import Document
from llama_index.core.schema import TextNode


class TestChunkerRegistry:
    """Test suite for ChunkerRegistry."""

    def test_registry_initializes_with_default_chunkers(self):
        """Test registry auto-registers default chunkers."""
        registry = ChunkerRegistry()

        supported_languages = registry.get_supported_languages()
        assert "python" in supported_languages
        assert "javascript" in supported_languages
        assert "java" in supported_languages
        assert "go" in supported_languages

    def test_get_by_language(self):
        """Test retrieving chunker by language name."""
        registry = ChunkerRegistry()

        python_chunker = registry.get_by_language("python")
        assert python_chunker is not None
        assert isinstance(python_chunker, PythonChunker)

        js_chunker = registry.get_by_language("javascript")
        assert js_chunker is not None
        assert isinstance(js_chunker, JavaScriptChunker)

    def test_get_by_extension(self):
        """Test retrieving chunker by file extension."""
        registry = ChunkerRegistry()

        # Test with various Python extensions
        python_chunker = registry.get_by_extension(".py")
        assert python_chunker is not None
        assert isinstance(python_chunker, PythonChunker)

        # Test JavaScript extensions
        js_chunker = registry.get_by_extension(".js")
        assert js_chunker is not None
        assert isinstance(js_chunker, JavaScriptChunker)

        # Test extension without leading dot
        chunker = registry.get_by_extension("py")
        assert chunker is not None
        assert isinstance(chunker, PythonChunker)

    def test_get_by_extension_case_insensitive(self):
        """Test extension lookup is case-insensitive."""
        registry = ChunkerRegistry()

        chunker1 = registry.get_by_extension(".PY")
        chunker2 = registry.get_by_extension(".py")
        assert chunker1 is not None
        assert chunker2 is not None
        assert type(chunker1) == type(chunker2)

    def test_get_supported_extensions(self):
        """Test getting all supported file extensions."""
        registry = ChunkerRegistry()

        extensions = registry.get_supported_extensions()
        assert ".py" in extensions
        assert ".js" in extensions
        assert ".java" in extensions
        assert ".go" in extensions

    def test_register_duplicate_raises_error(self):
        """Test that registering duplicate language raises ValueError."""
        registry = ChunkerRegistry()

        with pytest.raises(ValueError, match="already registered"):
            registry.register(PythonChunker())

    def test_unknown_language_returns_none(self):
        """Test that unknown language/extension returns None."""
        registry = ChunkerRegistry()

        assert registry.get_by_language("rust") is None
        assert registry.get_by_extension(".rs") is None


class TestCodeAwareNodeParser:
    """Test suite for CodeAwareNodeParser (integration with strategies)."""

    def test_parse_nodes_with_code_document(self, chunking_config):
        """Test parsing nodes with code category preserves structure."""
        parser = CodeAwareNodeParser.from_config(chunking_config)

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

    def test_parse_nodes_with_non_code_document(self, chunking_config):
        """Test parsing non-code documents uses generic chunking."""
        parser = CodeAwareNodeParser.from_config(chunking_config)

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

    def test_parse_nodes_preserve_structure_disabled(self, chunking_config):
        """Test that disabling preserve_code_structure uses generic chunking."""
        # Create config with preserve_code_structure disabled
        config = ChunkingConfig(
            code_chunk_size=chunking_config.code_chunk_size,
            code_chunk_overlap=chunking_config.code_chunk_overlap,
            doc_chunk_size=chunking_config.doc_chunk_size,
            doc_chunk_overlap=chunking_config.doc_chunk_overlap,
            preserve_code_structure=False,
            include_line_numbers=chunking_config.include_line_numbers,
        )
        parser = CodeAwareNodeParser.from_config(config)

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

    def test_chunk_python_single_function(self, chunking_config):
        """Test chunking a single Python function."""
        chunker = PythonChunker()

        code = """def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
"""
        chunks = chunker.chunk(
            code,
            "test.py",
            chunking_config.code_chunk_size,
            chunking_config.code_chunk_overlap,
        )

        assert len(chunks) >= 1
        chunk = chunks[0]
        assert isinstance(chunk, CodeChunk)
        assert "calculate_sum" in chunk.text
        assert chunk.start_line == 1
        assert chunk.end_line >= 1
        assert chunk.language == "python"

    def test_chunk_python_multiple_functions(self, chunking_config):
        """Test chunking multiple Python functions."""
        chunker = PythonChunker()

        code = """def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b != 0:
        return a / b
    return None
"""
        chunks = chunker.chunk(
            code,
            "test.py",
            chunking_config.code_chunk_size,
            chunking_config.code_chunk_overlap,
        )

        assert len(chunks) >= 3
        chunk_texts = [chunk.text for chunk in chunks]
        assert any("add" in text for text in chunk_texts)
        assert any("multiply" in text for text in chunk_texts)
        assert any("divide" in text for text in chunk_texts)

    def test_chunk_python_class_with_methods(self, chunking_config):
        """Test chunking a Python class with methods."""
        chunker = PythonChunker()

        code = """class Calculator:
    def __init__(self):
        self.result = 0

    def add(self, value):
        self.result += value
        return self.result

    def reset(self):
        self.result = 0
"""
        chunks = chunker.chunk(
            code,
            "test.py",
            chunking_config.code_chunk_size,
            chunking_config.code_chunk_overlap,
        )

        assert len(chunks) >= 1
        # Class and its methods should be in chunks
        assert "Calculator" in chunks[0].text

    def test_chunk_python_mixed_code_and_comments(self, chunking_config):
        """Test chunking Python code with comments and docstrings."""
        chunker = PythonChunker()

        code = """# This is a module for math operations

def add(a, b):
    '''Add two numbers.'''
    return a + b

# Another comment
def subtract(a, b):
    return a - b
"""
        chunks = chunker.chunk(
            code,
            "test.py",
            chunking_config.code_chunk_size,
            chunking_config.code_chunk_overlap,
        )

        assert len(chunks) >= 2
        # Comments should be preserved with their functions
        chunk_texts = [chunk.text for chunk in chunks]
        assert any("add" in text for text in chunk_texts)

    def test_chunk_python_large_chunk_splitting(self, chunking_config):
        """Test that large chunks are split when exceeding size limits."""
        chunker = PythonChunker()

        # Create a large code block
        large_code = "\n".join([f"# Comment line {i}" for i in range(50)])
        large_code += "\ndef function():\n    pass\n"

        chunks = chunker.chunk(
            large_code,
            "test.py",
            chunk_size=100,  # Small chunk size for testing
            chunk_overlap=chunking_config.code_chunk_overlap,
        )

        # Should be split into multiple chunks
        assert len(chunks) >= 2

    def test_chunk_python_async_functions(self, chunking_config):
        """Test chunking async Python functions."""
        chunker = PythonChunker()

        code = """async def fetch_data(url):
    response = await http_get(url)
    return response.json()

async def process_data(data):
    return await transform(data)
"""
        chunks = chunker.chunk(
            code,
            "test.py",
            chunking_config.code_chunk_size,
            chunking_config.code_chunk_overlap,
        )

        assert len(chunks) >= 2
        chunk_texts = [chunk.text for chunk in chunks]
        assert any("fetch_data" in text for text in chunk_texts)
        assert any("process_data" in text for text in chunk_texts)


class TestJavaScriptChunking:
    """Test suite for JavaScript chunking."""

    def test_chunk_javascript_functions(self, chunking_config):
        """Test chunking JavaScript function declarations."""
        chunker = JavaScriptChunker()

        code = """function add(a, b) {
    return a + b;
}

function multiply(x, y) {
    return x * y;
}
"""
        chunks = chunker.chunk(
            code,
            "test.js",
            chunking_config.code_chunk_size,
            chunking_config.code_chunk_overlap,
        )

        assert len(chunks) >= 2
        chunk_texts = [chunk.text for chunk in chunks]
        assert any("add" in text for text in chunk_texts)
        assert any("multiply" in text for text in chunk_texts)

    def test_chunk_javascript_classes(self, chunking_config):
        """Test chunking JavaScript classes."""
        chunker = JavaScriptChunker()

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
        chunks = chunker.chunk(
            code,
            "test.js",
            chunking_config.code_chunk_size,
            chunking_config.code_chunk_overlap,
        )

        assert len(chunks) >= 1
        assert "Calculator" in chunks[0].text
        assert "constructor" in chunks[0].text

    def test_chunk_javascript_arrow_functions(self, chunking_config):
        """Test chunking JavaScript arrow functions."""
        chunker = JavaScriptChunker()

        code = """const add = (a, b) => {
    return a + b;
}

const multiply = (x, y) => {
    return x * y;
}
"""
        chunks = chunker.chunk(
            code,
            "test.js",
            chunking_config.code_chunk_size,
            chunking_config.code_chunk_overlap,
        )

        assert len(chunks) >= 2
        chunk_texts = [chunk.text for chunk in chunks]
        assert any("add" in text for text in chunk_texts)
        assert any("multiply" in text for text in chunk_texts)

    def test_chunk_javascript_nested_braces(self, chunking_config):
        """Test chunking JavaScript code with nested braces."""
        chunker = JavaScriptChunker()

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
        chunks = chunker.chunk(
            code,
            "test.js",
            chunking_config.code_chunk_size,
            chunking_config.code_chunk_overlap,
        )

        assert len(chunks) >= 1
        # Should keep function together despite nested braces
        assert "processData" in chunks[0].text
        assert chunks[0].text.count("{") == chunks[0].text.count("}")


class TestGenericChunking:
    """Test suite for generic chunking."""

    def test_chunk_generic_documentation(self, chunking_config):
        """Test generic chunking for documentation files."""
        parser = CodeAwareNodeParser.from_config(chunking_config)

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
                chunk_size=chunking_config.doc_chunk_size,
                chunk_overlap=chunking_config.doc_chunk_overlap,
            )
            assert len(nodes) > 0

    def test_chunk_generic_other_files(self, chunking_config):
        """Test generic chunking for other file types."""
        parser = CodeAwareNodeParser.from_config(chunking_config)

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
                chunk_size=chunking_config.code_chunk_size,
                chunk_overlap=chunking_config.code_chunk_overlap,
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
