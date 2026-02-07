# Testing Guide for LlamaIndex Playground

This guide explains how to run and use the test files for the LlamaIndex playground project.

## Available Tests

### 1. Component Tests (`test_indexer.py`)

Tests the core components of the indexer:
- IndexerConfig initialization
- File metadata detection
- Code extraction (functions, classes, imports)

**Prerequisites:** None

**Usage:**
```bash
python test_indexer.py
```

This test will automatically find test files in your directory if the default test file doesn't exist.

### 2. Integration Test - Indexing (`test_index_go.py`)

Tests the full indexing workflow by indexing a directory.

**Prerequisites:**
- A directory to index (defaults to `C:\Git\go-test-ground` or `./test_data`)

**Usage:**
```bash
# Auto-confirm mode (for automated testing)
python test_index_go.py

# Manual confirmation mode
python test_index_go.py --no-auto-confirm
```

**Environment Variables:**
- `TEST_DIR`: Override the directory to index

### 3. Integration Test - Querying (`test_query.py`)

Tests the query functionality by querying an existing index.

**Prerequisites:**
- An existing index (created by running `test_index_go.py` first)

**Usage:**
```bash
# Query the default index
python test_query.py

# Query a specific index
python test_query.py my_custom_index

# Query with a custom question
python test_query.py go_test_index "How does the main function work?"
```

**Environment Variables:**
- `INDEX_NAME`: Name of the index to query (default: `go_test_index`)
- `TEST_QUESTION`: Custom question to ask

## Running All Tests

Use the test runner to run all tests with a summary:

```bash
python run_tests.py
```

The test runner will:
1. Run core component tests automatically
2. Ask if you want to run optional integration tests
3. Provide a summary of all test results

## Setting Up Test Data

### Option 1: Use test_data directory

Create a `test_data` directory in the project root and add some code files:

```bash
mkdir test_data
# Add your test files (any code files: .py, .go, .js, etc.)
```

### Option 2: Use go-test-ground repository

If you have the go-test-ground repository:

```bash
# Make sure it's at C:\Git\go-test-ground
# Or set TEST_DIR environment variable:
set TEST_DIR=C:\path\to\your\repo
```

## Expected Output

### Successful Test Run

```
======================================================================
Testing DocumentIndexer
======================================================================

1. Creating indexer instance...
   SUCCESS: Indexer created

2. Checking configuration...
   - Code chunk size: 512
   - Supported languages: 11
   - Extract functions: True
   SUCCESS: Configuration loaded

3. Testing file detection...
   - File: main.go
   - Language: go
   - Category: code
   SUCCESS: File detection works

4. Testing code metadata extraction...
   - Extracted metadata: ['imports', 'functions', 'structs']
   - Functions found: 5
   - Structs found: 2
   - Imports found: 8
   SUCCESS: Code extraction works

======================================================================
ALL TESTS PASSED!
======================================================================
```

## Troubleshooting

### "No test files found"

**Solution:** Create a `test_data` directory with some code files, or ensure the `go-test-ground` repository exists at the expected location.

### "No index found. Run test_index_go.py first"

**Solution:** Run the indexing test before the query test:
```bash
python test_index_go.py
python test_query.py
```

### Tests timeout

**Cause:** The first run downloads the embedding model which can take time.

**Solution:** Wait for the download to complete. Subsequent runs will be faster.

### Import errors

**Solution:** Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Automated Testing / CI Integration

For CI/CD pipelines, use the auto-confirm mode and set up test data:

```bash
# Setup
mkdir test_data
cp -r /path/to/sample/code test_data/

# Run tests
python test_indexer.py
python test_index_go.py  # Auto-confirms by default
python test_query.py

# Or use the test runner
echo "n" | python run_tests.py  # Skip optional tests
```

## Adding New Tests

To add a new test:

1. Create a new test file: `test_yourfeature.py`
2. Follow this structure:

```python
"""Test script for your feature."""
import sys
sys.path.insert(0, 'src')

from main import DocumentIndexer

def test_your_feature():
    """Test description."""
    print("=" * 70)
    print("Testing: Your Feature")
    print("=" * 70)

    try:
        # Your test code here
        print("\n1. Step 1...")
        # ...

        print("\nSUCCESS: Test completed")
        return True

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_your_feature()
    sys.exit(0 if success else 1)
```

3. Add it to `run_tests.py` in the appropriate test list

## Notes

- Tests use the `src/` directory structure, not package imports
- Each test is self-contained and can be run independently
- Test indices are stored in `storage/` directory
- The `DocumentIndexer` class handles all indexing and querying operations
