"""Progress tracking for document indexing operations."""

import json
import os
from datetime import datetime
from pathlib import Path


def debug_log(message: str) -> None:
    """Print debug message if debug mode is enabled."""
    debug = os.getenv("APP_DEBUG", "False").lower() == "true"
    if debug:
        print(f"[DEBUG] {message}")


class ProgressTracker:
    """Track indexing progress with resume capability."""

    def __init__(self, storage_dir: Path):
        """Initialize progress tracker.

        Args:
            storage_dir: Directory where progress.json will be saved
        """
        self.storage_dir = storage_dir
        self.progress_file = storage_dir / "progress.json"
        self.data: dict = self._create_empty_data()

    def _create_empty_data(self) -> dict[str, object]:
        """Create empty progress data structure.

        Returns:
            Empty progress data dictionary
        """
        return {
            "version": "1.0",
            "status": "in_progress",
            "started_at": datetime.now().isoformat(),
            "last_updated": None,
            "config": {},
            "progress": {
                "total_files": 0,
                "processed_files": 0,
                "processed_file_paths": [],
                "last_batch_at": None,
                "error_files": []
            }
        }

    def load(self) -> dict[str, object]:
        """Load existing progress or create new.

        Returns:
            Progress data dictionary
        """
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            debug_log(f"Loaded progress: {self.data['progress']['processed_files']} files processed")
        else:
            self.data = self._create_empty_data()
            debug_log("Created new progress tracker")
        return self.data

    def save(self) -> None:
        """Save current progress to disk."""
        self.data["last_updated"] = datetime.now().isoformat()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)
        debug_log(f"Progress saved: {self.data['progress']['processed_files']} files")

    def mark_processed(self, file_path: str) -> None:
        """Mark a file as processed.

        Args:
            file_path: Path of the processed file
        """
        if file_path not in self.data["progress"]["processed_file_paths"]:
            self.data["progress"]["processed_file_paths"].append(file_path)
            self.data["progress"]["processed_files"] += 1

    def is_processed(self, file_path: str) -> bool:
        """Check if file was already processed.

        Args:
            file_path: Path to check

        Returns:
            True if file was processed, False otherwise
        """
        return file_path in self.data["progress"]["processed_file_paths"]

    def mark_error(self, file_path: str, error: str) -> None:
        """Mark a file as having an error.

        Args:
            file_path: Path of the file with error
            error: Error message
        """
        self.data["progress"]["error_files"].append({
            "path": file_path,
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        })

    def mark_complete(self) -> None:
        """Mark indexing as complete."""
        self.data["status"] = "completed"
        self.data["progress"]["last_batch_at"] = datetime.now().isoformat()
        self.save()
