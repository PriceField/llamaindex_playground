"""Test script to verify the indexer works correctly."""
import sys
import os
sys.path.insert(0, 'src')

from main import DocumentIndexer

def test_indexer():
    """Test the indexer on go-test-ground repository."""
    print("=" * 70)
    print("Testing DocumentIndexer on go-test-ground repository")
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

        # Test file detection
        print("\n3. Testing file detection...")
        test_file = r"C:\Git\go-test-ground\main.go"
        metadata = indexer.file_handler.get_file_metadata(test_file)
        print(f"   - File: {metadata['file_name']}")
        print(f"   - Language: {metadata['language']}")
        print(f"   - Category: {metadata['category']}")
        print("   SUCCESS: File detection works")

        # Test code extraction
        print("\n4. Testing code metadata extraction...")
        with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        code_meta = indexer.code_extractor.extract_metadata(
            test_file, content, metadata['language']
        )
        if code_meta:
            print(f"   - Extracted metadata: {list(code_meta.keys())}")
            if 'functions' in code_meta:
                print(f"   - Functions found: {len(code_meta['functions'])}")
            if 'imports' in code_meta:
                print(f"   - Imports found: {len(code_meta['imports'])}")
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
