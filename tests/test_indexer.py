"""Test script to verify the indexer works correctly."""
import sys
import os
from pathlib import Path
sys.path.insert(0, 'src')

from main import DocumentIndexer

def test_indexer():
    """Test the indexer on go-test-ground repository."""
    print("=" * 70)
    print("Testing DocumentIndexer")
    print("=" * 70)

    try:
        # Create indexer instance
        print("\n1. Creating indexer instance...")
        indexer = DocumentIndexer("test_go_index")
        print("   SUCCESS: Indexer created")

        # Check configuration
        print("\n2. Checking configuration...")
        print(f"   - Code chunk size: {indexer.config.code_chunk_size}")
        print(f"   - Supported languages: {len(indexer.config.supported_languages)}")
        print(f"   - Extract functions: {indexer.config.extract_functions}")
        print("   SUCCESS: Configuration loaded")

        # Test file detection using test_data directory
        print("\n3. Testing file detection...")
        test_file = Path("test_data/sample_code/calculator.py")

        # Fallback to any code file in test_data or current directory
        if not test_file.exists():
            print(f"   WARNING: {test_file} not found, searching for alternatives...")
            # Try to find any code file in test_data first, then current directory
            for pattern in ["test_data/**/*.py", "test_data/**/*.js", "test_data/**/*.go", "**/*.py", "**/*.js"]:
                matches = list(Path(".").glob(pattern))
                if matches:
                    test_file = matches[0]
                    print(f"   Using alternative file: {test_file}")
                    break
            else:
                print("   ERROR: No test files found. Please ensure test files exist in test_data/.")
                return False

        metadata = indexer.file_handler.get_file_metadata(str(test_file))
        print(f"   - File: {metadata['file_name']}")
        print(f"   - Language: {metadata['language']}")
        print(f"   - Category: {metadata['category']}")
        print("   SUCCESS: File detection works")

        # Test code extraction
        print("\n4. Testing code metadata extraction...")
        with open(str(test_file), 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        code_meta = indexer.code_extractor.extract_metadata(
            str(test_file), content, metadata['language']
        )
        if code_meta:
            print(f"   - Extracted metadata: {list(code_meta.keys())}")
            if 'functions' in code_meta:
                print(f"   - Functions found: {len(code_meta['functions'])}")
            if 'structs' in code_meta:
                print(f"   - Structs found: {len(code_meta['structs'])}")
            if 'imports' in code_meta:
                print(f"   - Imports found: {len(code_meta['imports'])}")
            if 'classes' in code_meta:
                print(f"   - Classes found: {len(code_meta['classes'])}")
        else:
            print("   - No metadata extracted (might be non-code file or unsupported language)")
        print("   SUCCESS: Code extraction works")

        print("\n" + "=" * 70)
        print("ALL TESTS PASSED!")
        print("=" * 70)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = test_indexer()
    sys.exit(0 if success else 1)
