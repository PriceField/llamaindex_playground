# Code Review Action Plan

**Generated**: 2026-02-08
**Status Legend**: ❌ Not Started | 🔄 In Progress | ✅ Done | ⏭️ Skipped

---

## 🔴 Critical Priority (Do Immediately)

### 3. Add API Key Validation on Startup
**Status**: ✅ Done
**Priority**: P0 (Critical)
**Effort**: 30 mins
**Files**: `src/main.py` (lines 188-202)

**Issue**: Application continues without API_KEY, only failing later during queries

**Tasks**:
- [x] Create `validate_environment()` function in `src/main.py`
- [x] Check required env vars: `API_KEY`, `API_BASE`, `MODEL_NAME`
- [x] Raise clear error if missing: "API_KEY is required in .env file"
- [x] Call validation in `DocumentIndexer.__init__()`
- [x] Add optional flag to skip validation (for indexing-only mode)
- [x] Update README with troubleshooting section

**Implementation**:
```python
def validate_environment(require_llm: bool = True):
    """Validate required environment variables."""
    if require_llm:
        if not os.getenv("API_KEY"):
            raise ValueError(
                "API_KEY is required in .env file\n"
                "Copy .env.example to .env and add your API key"
            )
        if not os.getenv("API_BASE"):
            raise ValueError("API_BASE is required in .env file")
```

---

### 4. Remove Hardcoded Paths from Tests
**Status**: ✅ Done
**Priority**: P0 (Critical)
**Effort**: 15 mins
**Files**: `tests/test_indexer.py` (line 30)

**Issue**: `test_file = r"C:\Git\go-test-ground\main.go"` won't work cross-platform

**Tasks**:
- [x] Replace hardcoded path with relative path or environment variable
- [x] Use `test_data/` directory instead
- [x] Create sample test files if needed
- [x] Update test to work on Linux/Mac/Windows
- [x] Test on Windows to ensure still works

**Implementation**:
```python
# Implemented - line 30 now uses:
test_file = Path("test_data/sample_code/calculator.py")
# With proper fallback to find alternatives in test_data/ directory
# Now fully cross-platform compatible
```


## 🟡 High Priority (This Week)

### 6. Fix Type Annotation Consistency
**Status**: ❌ Not Started
**Priority**: P1 (High)
**Effort**: 30 mins
**Files**: `run_tests.py` (line 51), various files

**Issue**: Mixed use of `dict[str, bool]` (Python 3.10+) vs `Dict[str, bool]` from typing

**Tasks**:
- [ ] Find all uses of lowercase `dict[...]`, `list[...]`, `tuple[...]`
- [ ] Replace with `from typing import Dict, List, Tuple, Optional`
- [ ] Or update `pyproject.toml` to require Python 3.10+
- [ ] Run type checker: `mypy src/` (install mypy first)
- [ ] Fix any type errors found

**Files to check**:
- `run_tests.py:51`: `results: dict[str, bool | None]`

---

### 7. Add Unit Tests for Core Functionality
**Status**: ❌ Not Started
**Priority**: P1 (High)
**Effort**: 4 hours
**Files**: `tests/` (new files)

**Issue**: Current test coverage <20%, only component tests exist

**Tasks**:
- [ ] Create `tests/unit/` directory
- [ ] Add `tests/unit/test_config.py` - test config parsing
- [ ] Add `tests/unit/test_file_handlers.py` - test file detection
- [ ] Add `tests/unit/test_code_extractors.py` - test metadata extraction
- [ ] Add `tests/unit/test_code_chunking.py` - test chunking logic
- [ ] Add `tests/unit/test_code_query_engine.py` - test query engine
- [ ] Aim for >60% code coverage
- [ ] Run: `make test` and verify all pass

**Example test structure**:
```python
# tests/unit/test_file_handlers.py
import pytest
from src.file_handlers import FileHandler
from src.config import IndexerConfig

def test_should_index_python_file():
    config = IndexerConfig()
    handler = FileHandler(config)
    assert handler.should_index_file("test.py", [".py"], None)

def test_should_exclude_pycache():
    config = IndexerConfig()
    handler = FileHandler(config)
    assert not handler.should_index_file("__pycache__/test.py", None, None)
```

---

### 8. Refactor Long Functions
**Status**: ❌ Not Started
**Priority**: P1 (High)
**Effort**: 2 hours
**Files**: `src/main.py` (lines 283-470)

**Issue**: `index_directory()` is 190 lines - too long and hard to test

**Tasks**:
- [ ] Extract `_scan_files()` - file scanning logic
- [ ] Extract `_confirm_indexing()` - user confirmation logic
- [ ] Extract `_setup_signal_handler()` - signal handling setup
- [ ] Extract `_process_file_batch()` - batch processing logic
- [ ] Reduce `index_directory()` to <50 lines
- [ ] Add unit tests for each extracted function
- [ ] Verify integration still works

**Target structure**:
```python
def index_directory(self, directory: str, ...):
    """Main entry point - orchestrates indexing."""
    all_files, pending_files = self._scan_files(directory, ...)
    if not self._confirm_indexing(all_files, pending_files):
        return
    self._setup_signal_handler()
    self._process_batches(pending_files, ...)
```

---

### 9. Improve Error Handling Consistency
**Status**: ❌ Not Started
**Priority**: P1 (High)
**Effort**: 2 hours
**Files**: Multiple files across `src/`

**Issue**: Inconsistent error handling - sometimes returns None, sometimes prints, sometimes raises

**Tasks**:
- [ ] Define error handling strategy in `ARCHITECTURE.md`
- [ ] Add custom exceptions: `IndexerError`, `ConfigurationError`, `ValidationError`
- [ ] Use exceptions for unexpected errors (file not found, API errors)
- [ ] Use return values for expected failures (file filtered, already processed)
- [ ] Add logging framework: `import logging`
- [ ] Replace all `print()` with `logger.info()`, `logger.error()`, etc.
- [ ] Add `--verbose` flag to control log level

**Example**:
```python
# src/exceptions.py (new file)
class IndexerError(Exception):
    """Base exception for indexer errors."""
    pass

class ConfigurationError(IndexerError):
    """Raised when configuration is invalid."""
    pass
```

---

### 10. Cross-Platform Makefile
**Status**: ❌ Not Started
**Priority**: P1 (High)
**Effort**: 1 hour
**Files**: `Makefile`, `scripts/` (new)

**Issue**: Makefile uses Unix commands (`rm`, `find`) that don't work on Windows

**Tasks**:
- [ ] Option A: Create `tasks.py` with Python-based task runner
- [ ] Option B: Add Windows-compatible commands to Makefile
- [ ] Option C: Use `invoke` or `nox` for cross-platform tasks
- [ ] Move complex logic to Python scripts in `scripts/` directory
- [ ] Test on both Windows and Linux
- [ ] Update README with platform-specific notes if needed

**Recommended approach** (tasks.py):
```python
# tasks.py
import shutil
from pathlib import Path

def clean():
    """Clean cache and coverage files."""
    patterns = ["__pycache__", ".pytest_cache", "htmlcov", "*.pyc"]
    for pattern in patterns:
        for path in Path(".").rglob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
```

---

## 🟢 Medium Priority (Next 2 Weeks)

### 11. Add Environment Variable Validation
**Status**: ❌ Not Started
**Priority**: P2 (Medium)
**Effort**: 1 hour
**Files**: `src/config.py`

**Tasks**:
- [ ] Add validation for numeric values (BATCH_SIZE > 0)
- [ ] Add validation for file paths (if provided, must exist)
- [ ] Add validation for mutually exclusive options
- [ ] Raise `ConfigurationError` on invalid config
- [ ] Add unit tests for validation logic

---

### 12. Replace Regex with AST Parsing
**Status**: ❌ Not Started
**Priority**: P2 (Medium)
**Effort**: 6 hours
**Files**: `src/code_extractors.py`, `src/code_chunking.py`

**Issue**: Regex-based parsing is fragile and misses edge cases

**Tasks**:
- [ ] For Python: Use `ast` module instead of regex
- [ ] For JS/TS: Evaluate tree-sitter or esprima
- [ ] For Java/Go: Evaluate tree-sitter
- [ ] Create `src/parsers/` module for language-specific parsers
- [ ] Add fallback to regex if AST parsing fails
- [ ] Add tests with complex code (nested functions, decorators, etc.)

---

### 13. Add Logging Framework
**Status**: ❌ Not Started
**Priority**: P2 (Medium)
**Effort**: 2 hours
**Files**: All files in `src/`

**Tasks**:
- [ ] Add `src/logger.py` with configured logging
- [ ] Replace all `print()` with `logger.info()`, `logger.debug()`, etc.
- [ ] Replace `debug_log()` with `logger.debug()`
- [ ] Add file logging to `logs/` directory
- [ ] Add rotation: keep last 7 days of logs
- [ ] Add `--log-level` CLI argument

---

### 14. Add CI/CD Pipeline
**Status**: ❌ Not Started
**Priority**: P2 (Medium)
**Effort**: 2 hours
**Files**: `.github/workflows/` (new)

**Tasks**:
- [ ] Create `.github/workflows/test.yml`
- [ ] Run tests on push and PR
- [ ] Run linting (black, pylint)
- [ ] Check test coverage (fail if <60%)
- [ ] Test on multiple Python versions (3.11, 3.12)
- [ ] Test on multiple OS (Ubuntu, Windows, macOS)

---

### 15. Improve Documentation
**Status**: ❌ Not Started
**Priority**: P2 (Medium)
**Effort**: 3 hours
**Files**: Various `.md` files

**Tasks**:
- [ ] Create `ARCHITECTURE.md` - system design overview
- [ ] Create `CONTRIBUTING.md` - how to contribute
- [ ] Add inline comments to complex algorithms (chunking logic)
- [ ] Add architecture diagram (mermaid or ASCII)
- [ ] Document query filter examples in README
- [ ] Add FAQ section to README

---

## 🔵 Low Priority (Backlog)

### 16. Add Type Hints Throughout
**Status**: ❌ Not Started
**Priority**: P3 (Low)
**Effort**: 3 hours

**Tasks**:
- [ ] Add type hints to all function signatures
- [ ] Add return type annotations
- [ ] Run `mypy --strict src/`
- [ ] Fix all type errors
- [ ] Add to CI pipeline

---

### 17. Dependency Injection for Settings
**Status**: ❌ Not Started
**Priority**: P3 (Low)
**Effort**: 4 hours

**Tasks**:
- [ ] Remove global `Settings` mutations
- [ ] Pass configuration explicitly to classes
- [ ] Use context managers for scoped settings
- [ ] Enable parallel indexing with different configs

---

### 18. Performance Optimization
**Status**: ❌ Not Started
**Priority**: P3 (Low)
**Effort**: 8 hours

**Tasks**:
- [ ] Profile code with `cProfile`
- [ ] Identify bottlenecks
- [ ] Add parallel file processing
- [ ] Optimize chunking algorithms
- [ ] Add benchmark suite

---

### 19. Add Telemetry/Metrics
**Status**: ❌ Not Started
**Priority**: P3 (Low)
**Effort**: 4 hours

**Tasks**:
- [ ] Track indexing metrics (files/sec, errors, etc.)
- [ ] Track query metrics (latency, tokens, etc.)
- [ ] Add prometheus exporter (optional)
- [ ] Create dashboard template

---

### 20. Enhanced Query Features
**Status**: ❌ Not Started
**Priority**: P3 (Low)
**Effort**: 6 hours

**Tasks**:
- [ ] Add semantic code search
- [ ] Add symbol search (find all usages)
- [ ] Add cross-reference tracking
- [ ] Add call graph generation

---

## 📊 Progress Summary

**Last Updated**: 2026-02-08 (Night)

| Priority | Total | Done | In Progress | Not Started |
|----------|-------|------|-------------|-------------|
| P0 (Critical) | 5 | 3 | 0 | 2 |
| P1 (High) | 5 | 0 | 0 | 5 |
| P2 (Medium) | 5 | 0 | 0 | 5 |
| P3 (Low) | 5 | 0 | 0 | 5 |
| **TOTAL** | **20** | **3** | **0** | **17** |

---

## 🎯 Suggested Work Sessions

### Session 1 (2 hours): Critical Fixes
1. Fix dependency mismatch (#1)
2. Remove hardcoded paths (#4)
3. Git status cleanup (#5)
4. Add API key validation (#3)

### Session 2 (3 hours): Replace CustomOpenAI
1. Research endpoint type
2. Implement proper LLM integration (#2)
3. Test thoroughly
4. Update documentation

### Session 3 (4 hours): Testing Foundation
1. Add unit tests (#7)
2. Set up test infrastructure
3. Aim for 60% coverage

### Session 4 (3 hours): Code Quality
1. Refactor long functions (#8)
2. Fix type annotations (#6)
3. Run linters

### Session 5 (2 hours): Developer Experience
1. Cross-platform Makefile (#10)
2. Improve error handling (#9)

---

## 📝 Notes & Decisions

### Decision Log
- **2026-02-08**: Plan created from comprehensive code review
- **2026-02-08**: ✅ Decided to use OpenAI-compatible endpoint (existing setup)
- [ ] **TBD**: Decision on task runner (Makefile vs tasks.py)
- [ ] **TBD**: Decision on AST parser library for non-Python languages

### Blocked Items
- None currently

### Questions for Product Owner
1. Are we using OpenAI API or Anthropic Claude API?
2. What's the minimum Python version we need to support?
3. What's the priority: more features or better testing?
4. Do we need Windows support or Linux-only?

---

## 🔄 How to Use This Plan

1. **Pick a task**: Choose from Critical (P0) or High (P1) priority
2. **Update status**: Change ❌ to 🔄 when starting
3. **Check boxes**: Mark subtasks as you complete them
4. **Update status**: Change 🔄 to ✅ when done
5. **Update summary**: Increment the progress table
6. **Commit changes**: `git add CODE_REVIEW_PLAN.md && git commit -m "Update plan progress"`
7. **Tell Claude**: "Continue with task #X" or "I finished task #Y, what's next?"

---

**End of Plan** | [Jump to Top](#code-review-action-plan)
