"""Unit tests for core functionality."""
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))
