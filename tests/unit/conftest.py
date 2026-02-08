"""Shared fixtures for unit tests."""
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_config():
    """Create a mock IndexerConfig for testing."""
    config = MagicMock()
    # Chunking settings
    config.code_chunk_size = 512
    config.code_chunk_overlap = 50
    config.doc_chunk_size = 1024
    config.doc_chunk_overlap = 20

    # Extraction settings
    config.extract_functions = True
    config.extract_classes = True
    config.extract_imports = True
    config.include_line_numbers = True
    config.preserve_code_structure = True

    # Default patterns
    config.default_exclude_patterns = ["node_modules", "__pycache__", ".git"]

    # Methods
    config.detect_language = MagicMock(return_value="python")
    config.detect_category = MagicMock(return_value="code")

    return config


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
