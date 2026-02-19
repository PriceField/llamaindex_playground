"""Shared fixtures for unit tests."""
import pytest

from config import (
    ChunkingConfig,
    ExtractionConfig,
    EmbeddingConfig,
    QueryConfig,
    FileFilterConfig,
    LanguageDetector,
    FileCategorizer,
)


@pytest.fixture
def chunking_config():
    """Create a real ChunkingConfig for testing."""
    return ChunkingConfig(
        code_chunk_size=512,
        code_chunk_overlap=50,
        doc_chunk_size=1024,
        doc_chunk_overlap=20,
        include_line_numbers=True,
        preserve_code_structure=True,
    )


@pytest.fixture
def extraction_config():
    """Create a real ExtractionConfig for testing."""
    return ExtractionConfig(
        extract_functions=True,
        extract_classes=True,
        extract_imports=True,
    )


@pytest.fixture
def embedding_config():
    """Create a real EmbeddingConfig for testing."""
    return EmbeddingConfig(
        embed_model_type="local",  # Use local for testing (no API calls)
        embed_model_name="BAAI/bge-small-en-v1.5",
        embed_api_key="",
        embed_api_base="",
        embed_openai_model="text-embedding-ada-002",
    )


@pytest.fixture
def file_filter_config():
    """Create a real FileFilterConfig for testing."""
    return FileFilterConfig(
        supported_languages=["python", "javascript", "java", "go"],
        default_exclude_patterns=[
            # Version control
            ".git",
            # Build artifacts & dependencies
            "node_modules", "dist", "build", "target",
            # Python environments & caches
            "__pycache__", ".venv", "venv", "ENV", "env",
            ".pytest_cache", ".mypy_cache", "*.pyc", "*.pyo", "*.egg-info",
            # IDE & Editor files
            ".vscode", ".idea", "*.swp", "*.swo",
            # AI/LLM tools
            ".claude",
            # OS files
            ".DS_Store", "Thumbs.db",
            # General caches & storage
            ".cache", "storage",
            # Binary files
            "*.so", "*.dll", "*.exe",
            # Sensitive files
            ".env",
        ],
    )


@pytest.fixture
def query_config():
    """Create a real QueryConfig for testing."""
    return QueryConfig(
        code_similarity_top_k=5,
        use_metadata_filters=True,
        include_source_context=True,
    )


@pytest.fixture
def language_detector():
    """Create a real LanguageDetector for testing."""
    return LanguageDetector()


@pytest.fixture
def file_categorizer():
    """Create a real FileCategorizer for testing."""
    return FileCategorizer()


@pytest.fixture
def sample_python_code():
    """Sample Python code for testing."""
    return """import os
from pathlib import Path

class Calculator:
    def add(self, a, b):
        return a + b

    async def async_add(self, a, b):
        return a + b
"""


@pytest.fixture
def sample_javascript_code():
    """Sample JavaScript code for testing."""
    return """import React from 'react';

class Component extends React.Component {
    render() { return null; }
}

const helper = (x) => x * 2;
"""


@pytest.fixture
def sample_java_code():
    """Sample Java code for testing."""
    return """import java.util.List;

public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
}
"""


@pytest.fixture
def sample_go_code():
    """Sample Go code for testing."""
    return """package main

import "fmt"

type User struct {
    ID int
    Name string
}

func main() {
    fmt.Println("Hello")
}
"""
