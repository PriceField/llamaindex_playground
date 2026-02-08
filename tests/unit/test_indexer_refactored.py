"""Unit tests for refactored DocumentIndexer methods.

Tests for the extracted methods from index_directory() refactoring.
"""

import signal
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
import pytest
from src.main import DocumentIndexer, ProgressTracker


class TestPrintIndexingConfig:
    """Tests for _print_indexing_config() method."""

    def test_print_indexing_config_basic(self, tmp_path, capsys):
        """Test printing basic indexing configuration."""
        with patch('src.main.validate_environment'):
            indexer = DocumentIndexer("test_index", require_llm=False)
            indexer.storage_dir = tmp_path

        directory_path = Path("/test/directory")
        indexer._print_indexing_config(
            directory_path=directory_path,
            recursive=True,
            batch_size=10,
            autosave_interval=60,
            file_extensions=None,
            exclude_patterns=None
        )

        captured = capsys.readouterr()
        assert "[DIR] Indexing directory:" in captured.out
        assert str(directory_path) in captured.out
        assert "Recursive: True" in captured.out
        assert "Batch size: 10 files" in captured.out
        assert "Auto-save: every 60 seconds" in captured.out

    def test_print_indexing_config_with_extensions(self, tmp_path, capsys):
        """Test printing config with file extensions."""
        with patch('src.main.validate_environment'):
            indexer = DocumentIndexer("test_index", require_llm=False)
            indexer.storage_dir = tmp_path

        directory_path = Path("/test/directory")
        indexer._print_indexing_config(
            directory_path=directory_path,
            recursive=True,
            batch_size=10,
            autosave_interval=60,
            file_extensions=['.py', '.md'],
            exclude_patterns=['*test*']
        )

        captured = capsys.readouterr()
        assert "File types: .py, .md" in captured.out
        assert "Excluding: *test*" in captured.out


class TestSaveConfigToTracker:
    """Tests for _save_config_to_tracker() method."""

    def test_save_config_to_tracker(self, tmp_path):
        """Test saving configuration to progress tracker."""
        with patch('src.main.validate_environment'):
            indexer = DocumentIndexer("test_index", require_llm=False)
            indexer.storage_dir = tmp_path

        tracker = ProgressTracker(tmp_path)
        tracker.load()

        directory_path = Path("/test/directory")
        indexer._save_config_to_tracker(
            tracker=tracker,
            directory_path=directory_path,
            file_extensions=['.py'],
            exclude_patterns=['*test*'],
            recursive=True,
            batch_size=20,
            autosave_interval=120
        )

        assert tracker.data["config"]["directory"] == str(directory_path)
        assert tracker.data["config"]["file_extensions"] == ['.py']
        assert tracker.data["config"]["exclude_patterns"] == ['*test*']
        assert tracker.data["config"]["recursive"] is True
        assert tracker.data["config"]["batch_size"] == 20
        assert tracker.data["config"]["autosave_interval"] == 120


class TestPrintCompletionSummary:
    """Tests for _print_completion_summary() method."""

    def test_print_completion_summary_no_errors(self, tmp_path, capsys):
        """Test printing completion summary without errors."""
        with patch('src.main.validate_environment'):
            indexer = DocumentIndexer("test_index", require_llm=False)
            indexer.storage_dir = tmp_path

        tracker = ProgressTracker(tmp_path)
        tracker.load()
        tracker.data["progress"]["processed_files"] = 10

        indexer._print_completion_summary(tracker, total_files=10)

        captured = capsys.readouterr()
        assert "[OK] Indexing complete!" in captured.out
        assert "Total files: 10" in captured.out
        assert "Processed: 10" in captured.out
        assert str(tmp_path) in captured.out

    def test_print_completion_summary_with_errors(self, tmp_path, capsys):
        """Test printing completion summary with errors."""
        with patch('src.main.validate_environment'):
            indexer = DocumentIndexer("test_index", require_llm=False)
            indexer.storage_dir = tmp_path

        tracker = ProgressTracker(tmp_path)
        tracker.load()
        tracker.data["progress"]["processed_files"] = 8
        tracker.data["progress"]["error_files"] = {"file1.py": "error1", "file2.py": "error2"}

        indexer._print_completion_summary(tracker, total_files=10)

        captured = capsys.readouterr()
        assert "[OK] Indexing complete!" in captured.out
        assert "Total files: 10" in captured.out
        assert "Processed: 8" in captured.out
        assert "Errors: 2" in captured.out


class TestConfirmIndexing:
    """Tests for _confirm_indexing() method."""

    def test_confirm_indexing_resume_accepted(self, tmp_path, monkeypatch):
        """Test user confirms resume."""
        with patch('src.main.validate_environment'):
            indexer = DocumentIndexer("test_index", require_llm=False)
            indexer.storage_dir = tmp_path

        monkeypatch.setattr('builtins.input', lambda _: 'y')
        result = indexer._confirm_indexing(
            all_file_count=10,
            pending_file_count=5,
            processed_count=5
        )
        assert result is True

    def test_confirm_indexing_resume_rejected(self, tmp_path, monkeypatch):
        """Test user rejects resume."""
        with patch('src.main.validate_environment'):
            indexer = DocumentIndexer("test_index", require_llm=False)
            indexer.storage_dir = tmp_path

        monkeypatch.setattr('builtins.input', lambda _: 'n')
        result = indexer._confirm_indexing(
            all_file_count=10,
            pending_file_count=5,
            processed_count=5
        )
        assert result is False

    def test_confirm_indexing_no_pending_files(self, tmp_path):
        """Test early return when no pending files."""
        with patch('src.main.validate_environment'):
            indexer = DocumentIndexer("test_index", require_llm=False)
            indexer.storage_dir = tmp_path

        result = indexer._confirm_indexing(
            all_file_count=10,
            pending_file_count=0,
            processed_count=10
        )
        assert result is False

    def test_confirm_indexing_fresh_start(self, tmp_path, monkeypatch):
        """Test fresh start confirmation."""
        with patch('src.main.validate_environment'):
            indexer = DocumentIndexer("test_index", require_llm=False)
            indexer.storage_dir = tmp_path

        monkeypatch.setattr('builtins.input', lambda _: 'y')
        result = indexer._confirm_indexing(
            all_file_count=10,
            pending_file_count=10,
            processed_count=0
        )
        assert result is True

    def test_confirm_indexing_fresh_start_no_files(self, tmp_path):
        """Test fresh start with no files to index."""
        with patch('src.main.validate_environment'):
            indexer = DocumentIndexer("test_index", require_llm=False)
            indexer.storage_dir = tmp_path

        result = indexer._confirm_indexing(
            all_file_count=0,
            pending_file_count=0,
            processed_count=0
        )
        assert result is False


class TestSetupSignalHandler:
    """Tests for _setup_signal_handler() method."""

    def test_setup_signal_handler_registered(self, tmp_path):
        """Test that signal handler is registered."""
        with patch('src.main.validate_environment'):
            indexer = DocumentIndexer("test_index", require_llm=False)
            indexer.storage_dir = tmp_path

        tracker = ProgressTracker(tmp_path)
        tracker.load()

        # Store original handler
        original_handler = signal.getsignal(signal.SIGINT)

        try:
            indexer._setup_signal_handler(tracker)
            new_handler = signal.getsignal(signal.SIGINT)

            # Verify handler was changed
            assert new_handler != original_handler
            assert callable(new_handler)
        finally:
            # Restore original handler
            signal.signal(signal.SIGINT, original_handler)


class TestScanFiles:
    """Tests for _scan_files() method."""

    def test_scan_files_updates_tracker(self, tmp_path):
        """Test that tracker is updated with total files."""
        with patch('src.main.validate_environment'):
            indexer = DocumentIndexer("test_index", require_llm=False)
            indexer.storage_dir = tmp_path

        # Create test files
        test_dir = tmp_path / "test_files"
        test_dir.mkdir()
        (test_dir / "file1.py").write_text("# test")
        (test_dir / "file2.py").write_text("# test")

        tracker = ProgressTracker(tmp_path)
        tracker.load()

        all_files, pending_files = indexer._scan_files(
            directory_path=test_dir,
            recursive=True,
            file_extensions=['.py'],
            exclude_patterns=None,
            tracker=tracker
        )

        assert len(all_files) == 2
        assert len(pending_files) == 2
        assert tracker.data["progress"]["total_files"] == 2

    def test_scan_files_excludes_processed(self, tmp_path):
        """Test that already processed files are filtered."""
        with patch('src.main.validate_environment'):
            indexer = DocumentIndexer("test_index", require_llm=False)
            indexer.storage_dir = tmp_path

        # Create test files
        test_dir = tmp_path / "test_files"
        test_dir.mkdir()
        file1 = test_dir / "file1.py"
        file2 = test_dir / "file2.py"
        file1.write_text("# test")
        file2.write_text("# test")

        tracker = ProgressTracker(tmp_path)
        tracker.load()
        # Mark file1 as processed
        tracker.mark_processed(str(file1.resolve()))

        all_files, pending_files = indexer._scan_files(
            directory_path=test_dir,
            recursive=True,
            file_extensions=['.py'],
            exclude_patterns=None,
            tracker=tracker
        )

        assert len(all_files) == 2
        assert len(pending_files) == 1
        assert str(file2.resolve()) in pending_files
        assert str(file1.resolve()) not in pending_files
