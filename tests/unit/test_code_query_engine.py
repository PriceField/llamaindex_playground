"""Unit tests for code_query_engine module."""
import pytest
from unittest.mock import MagicMock, patch

from code_query_engine import CodeQueryEngine


class TestCodeQueryEngine:
    """Test suite for CodeQueryEngine class."""

    @patch('code_query_engine.get_response_synthesizer')
    @patch('code_query_engine.VectorIndexRetriever')
    @patch('code_query_engine.RetrieverQueryEngine')
    def test_create_query_engine_with_defaults(
        self,
        mock_retriever_query_engine,
        mock_retriever_cls,
        mock_synthesizer,
        mock_config
    ):
        """Test creating query engine with default parameters."""
        mock_index = MagicMock()
        mock_config.code_similarity_top_k = 5
        mock_config.include_source_context = True

        engine = CodeQueryEngine(mock_index, mock_config)

        # The method creates a RetrieverQueryEngine internally
        query_engine = engine.create_query_engine()

        # Verify VectorIndexRetriever was called with correct top_k
        mock_retriever_cls.assert_called_once()
        call_kwargs = mock_retriever_cls.call_args[1]
        assert call_kwargs['similarity_top_k'] == 5

    @patch('code_query_engine.get_response_synthesizer')
    @patch('code_query_engine.VectorIndexRetriever')
    @patch('code_query_engine.RetrieverQueryEngine')
    def test_create_query_engine_with_custom_params(
        self,
        mock_retriever_query_engine,
        mock_retriever_cls,
        mock_synthesizer,
        mock_config
    ):
        """Test creating query engine with custom parameters."""
        mock_index = MagicMock()
        mock_config.code_similarity_top_k = 5
        mock_config.include_source_context = True

        engine = CodeQueryEngine(mock_index, mock_config)

        # Create with custom top_k
        query_engine = engine.create_query_engine(similarity_top_k=10)

        # Verify VectorIndexRetriever was called with custom top_k
        mock_retriever_cls.assert_called_once()
        call_kwargs = mock_retriever_cls.call_args[1]
        assert call_kwargs['similarity_top_k'] == 10

    def test_get_code_qa_prompt_with_source_context(self, mock_config):
        """Test QA prompt generation with source context enabled."""
        mock_config.include_source_context = True
        mock_index = MagicMock()

        engine = CodeQueryEngine(mock_index, mock_config)
        prompt_template = engine._get_code_qa_prompt()

        # Verify prompt contains code-specific instructions
        assert prompt_template is not None
        assert "code" in prompt_template.template.lower() or "source" in prompt_template.template.lower()

    def test_get_code_qa_prompt_without_source_context(self, mock_config):
        """Test QA prompt generation with source context disabled."""
        mock_config.include_source_context = False
        mock_index = MagicMock()

        engine = CodeQueryEngine(mock_index, mock_config)
        prompt_template = engine._get_code_qa_prompt()

        # Prompt should still be created
        assert prompt_template is not None

    def test_format_response_with_sources(self, mock_config):
        """Test formatting response with source information."""
        mock_index = MagicMock()
        engine = CodeQueryEngine(mock_index, mock_config)

        # Create mock response with source nodes
        mock_response = MagicMock()
        mock_response.__str__ = MagicMock(return_value="This is the answer to your query.")

        # Create mock source nodes
        mock_node1 = MagicMock()
        mock_node1.metadata = {
            "file_path": "/path/to/file1.py",
            "file_name": "file1.py",
            "language": "python",
            "start_line": 10,
            "end_line": 20
        }
        mock_node1.score = 0.95
        mock_node1.text = "def example():\n    pass"

        mock_node2 = MagicMock()
        mock_node2.metadata = {
            "file_path": "/path/to/file2.py",
            "file_name": "file2.py",
            "language": "python"
        }
        mock_node2.score = 0.85
        mock_node2.text = "import os"

        mock_response.source_nodes = [mock_node1, mock_node2]

        formatted = engine.format_response_with_sources(mock_response)

        # Verify response is formatted
        assert isinstance(formatted, str)
        assert "This is the answer" in formatted
        assert "file1.py" in formatted
        assert "file2.py" in formatted

    def test_format_response_without_sources(self, mock_config):
        """Test formatting response without source nodes."""
        mock_index = MagicMock()
        engine = CodeQueryEngine(mock_index, mock_config)

        mock_response = MagicMock()
        mock_response.__str__ = MagicMock(return_value="Simple response")
        mock_response.source_nodes = []

        formatted = engine.format_response_with_sources(mock_response)

        assert isinstance(formatted, str)
        assert "Simple response" in formatted


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
