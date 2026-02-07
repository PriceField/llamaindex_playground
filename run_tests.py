"""Test runner for LlamaIndex playground tests."""
import sys
import os
import subprocess

def run_test(test_file: str, description: str) -> bool:
    """Run a single test file and report results.

    Args:
        test_file: Path to the test file
        description: Description of the test

    Returns:
        True if test passed, False otherwise
    """
    print("\n" + "=" * 80)
    print(f"Running: {description}")
    print("=" * 80)

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"\n[TIMEOUT] Test timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"\n[ERROR] Failed to run test: {e}")
        return False

def main():
    """Run all tests and report summary."""
    print("=" * 80)
    print("LLAMAINDEX PLAYGROUND TEST SUITE")
    print("=" * 80)

    tests = [
        ("test_indexer.py", "Component Tests - File handling and code extraction"),
    ]

    # Optional tests that require specific setup
    optional_tests = [
        ("test_index_go.py", "Integration Test - Index go-test-ground repository"),
        ("test_query.py", "Integration Test - Query indexed repository"),
    ]

    results: dict[str, bool | None] = {}

    # Run core tests
    print("\n[CORE TESTS]")
    for test_file, description in tests:
        if os.path.exists(test_file):
            results[test_file] = run_test(test_file, description)
        else:
            print(f"\n[SKIP] {test_file} not found")
            results[test_file] = None

    # Ask about optional tests
    print("\n" + "=" * 80)
    print("[OPTIONAL TESTS]")
    print("The following tests require additional setup:")
    print("  - test_index_go.py: Needs test data directory or go-test-ground repo")
    print("  - test_query.py: Needs an existing index (run test_index_go.py first)")
    print("=" * 80)

    run_optional = input("\nRun optional tests? (y/n, default: n): ").strip().lower()

    if run_optional == 'y':
        for test_file, description in optional_tests:
            if os.path.exists(test_file):
                results[test_file] = run_test(test_file, description)
            else:
                print(f"\n[SKIP] {test_file} not found")
                results[test_file] = None

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)

    for test_file, result in results.items():
        if result is True:
            status = "[PASS]"
        elif result is False:
            status = "[FAIL]"
        else:
            status = "[SKIP]"
        print(f"{status} {test_file}")

    print("-" * 80)
    print(f"Total: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print("=" * 80)

    # Exit with appropriate code
    if failed > 0:
        print("\n[RESULT] Some tests failed")
        sys.exit(1)
    elif passed > 0:
        print("\n[RESULT] All tests passed!")
        sys.exit(0)
    else:
        print("\n[RESULT] No tests were run")
        sys.exit(2)

if __name__ == "__main__":
    main()
