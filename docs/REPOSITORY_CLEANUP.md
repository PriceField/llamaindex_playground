# Repository Cleanup Plan

**Date**: February 11, 2026
**Status**: Ready for Implementation
**Priority**: CRITICAL (Blocking Phase 4 Progress)

---

## Context

The repository is in Phase 4 of a major SOLID refactoring project. While most of the work has been done well (52% test coverage, 184/184 tests passing, clean architecture with Strategy Pattern), there are critical issues blocking progress and several cleanup opportunities identified.

**Critical Discovery**: The old `src/config.py` module was deleted in Phase 3, but the `IndexerConfig` class it contained is still imported by 7 files. This is a **blocking issue** - the code cannot run without this class.

**Why This Cleanup Matters**:
- Unblock Phase 4 progress (coverage boost + main.py migration)
- Remove technical debt from the refactoring
- Ensure clean git history
- Improve repository organization

---

## Critical Files Affected

### Files Importing Missing IndexerConfig:
1. [src/app_factory.py](../src/app_factory.py#L26) - Creates IndexerConfig() as "temporary bridge"
2. [src/code_chunking.py](../src/code_chunking.py#L21) - Integration layer
3. [src/code_extractors.py](../src/code_extractors.py#L17) - Integration layer
4. [src/code_query_engine.py](../src/code_query_engine.py#L9) - Query engine
5. [src/file_handlers.py](../src/file_handlers.py#L5) - File handling
6. [src/free_query_mode.py](../src/free_query_mode.py#L7) - Free query mode
7. [src/main.py](../src/main.py#L29) - Main application (1,293 lines)

### Cleanup Targets:
- Empty ghost directories: `srcstrategieschunking/`, `srcstrategiesextraction/`
- 10 staged git files (documentation reorganization)
- 4 old test files in `tests/old/`
- Root-level test files needing reorganization
- `demo_free_vs_paid.py` (uses old architecture)

---

## Implementation Plan

### Phase 1: Fix Critical Blocker (IndexerConfig)

**Approach**: Create a legacy compatibility bridge class that aggregates the new focused configs.

**Files to Create/Modify**:
1. **Create** `src/config/indexer_config.py`:
   - Legacy `IndexerConfig` class that wraps the 5 new configs
   - Constructor accepts all old parameters for backward compatibility
   - Provides properties to access new config objects
   - Add deprecation warning in docstring
   - Include migration examples

2. **Update** `src/config/__init__.py`:
   - Export `IndexerConfig` for backward compatibility
   - Add comment marking it as "legacy bridge - Phase 4 migration target"

**Design Pattern**: Adapter Pattern (wraps new configs to provide old interface)

**Rationale**:
- Minimal disruption - existing code continues to work
- Clear migration path - each file can migrate incrementally
- Testable - can verify old interface still works
- Reversible - can be removed cleanly after Phase 4

### Phase 2: Clean Empty Ghost Directories

**Action**: Delete both empty directories created by path handling bug
- `srcstrategieschunking/`
- `srcstrategiesextraction/`

**Method**: Use bash `rmdir` command (safe - only removes empty directories)

**Investigation**: Search codebase for incorrect path concatenation patterns

### Phase 3: Commit Documentation Reorganization

**Action**: Review and commit the 10 staged files

**Files Staged**:
- Modified: `README.md`
- Renamed to `docs/`: 7 documentation files
- Added: `docs/README.md`

**Commit Message**:
```
Reorganize documentation into docs/ folder

- Move all documentation files to docs/ for better organization
- Add docs/README.md as documentation index
- Update main README.md with Phase 3 completion status

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

### Phase 4: Reorganize Test Structure

**Current Issues**:
- `test_indexing_orchestrator.py` at root (29 tests) → should be in `unit/`
- `test_api.py` at root → determine if unit or integration test, move accordingly

**Actions**:
1. Move `tests/test_indexing_orchestrator.py` → `tests/unit/test_indexing_orchestrator.py`
2. Review `tests/test_api.py` and move to appropriate directory
3. Update any import paths if needed

**Result**: Clear structure with `unit/`, `integration/`, `old/` subdirectories

### Phase 5: Archive Old Tests (Post-Migration)

**Action**: Keep for now, mark for deletion after Phase 4 main.py migration

**Files in `tests/old/`**:
- `test_env_validation.py` - Tests old validate_environment()
- `test_indexer.py` - Tests DocumentIndexer
- `test_index_go.py` - Integration test
- `test_query.py` - Query tests

**Rationale**:
- These reference `DocumentIndexer` from `main.py`
- May serve as migration reference
- Already ignored by pytest config
- Safe to keep until Phase 4 complete

### Phase 6: Remove Demo Script

**File**: `demo_free_vs_paid.py`

**Purpose**: Interactive demo comparing FREE (retrieval-only) vs PAID (LLM) query modes

**User Decision**: Delete - not needed

**Rationale**:
- Not a test file (interactive demo script)
- Uses old `DocumentIndexer` architecture (would need migration)
- Functionality already documented in [FREE_QUERY_MODE.md](FREE_QUERY_MODE.md)
- The actual codebase demonstrates this functionality
- Would require ongoing maintenance after migration

**Action**: Delete file

---

## Verification Strategy

### 1. IndexerConfig Fix Verification
```bash
# Run existing tests to ensure backward compatibility
pytest tests/ -v

# Check imports work
python -c "from src.config import IndexerConfig; print('Import successful')"

# Verify all 7 files can import
python -c "from src import app_factory, code_chunking, code_extractors, code_query_engine, file_handlers, free_query_mode, main; print('All imports successful')"
```

### 2. Directory Cleanup Verification
```bash
# Verify directories are empty before deletion
ls -la srcstrategieschunking/ srcstrategiesextraction/

# After deletion, verify they're gone
test ! -d srcstrategieschunking && test ! -d srcstrategiesextraction && echo "Cleanup successful"
```

### 3. Git Status Verification
```bash
# Check staged files
git status

# Review diff before commit
git diff --cached

# After commit, verify clean working tree
git status
```

### 4. Test Reorganization Verification
```bash
# Run all tests after moving files
pytest tests/ -v

# Verify coverage still works
pytest --cov=src tests/

# Check test count matches (184 tests)
pytest --collect-only | grep "test session starts"
```

---

## Risk Assessment

### High Risk (Requires Careful Review)
1. **IndexerConfig creation**: Must maintain exact backward compatibility
   - Mitigation: Comprehensive unit tests for legacy interface
   - Fallback: Revert commit if tests fail

### Medium Risk
1. **Test file moves**: May break imports or paths
   - Mitigation: Run full test suite after each move
   - Fallback: Git revert individual file moves

### Low Risk (Safe Operations)
1. **Delete empty directories**: Only removes empty dirs
2. **Commit staged files**: Already reviewed, just documentation
3. **Archive old tests**: Already ignored by pytest

---

## Success Criteria

- ✅ All 7 files can import `IndexerConfig` without errors
- ✅ All 184 tests pass after IndexerConfig fix
- ✅ Empty ghost directories removed
- ✅ Documentation changes committed with clean message
- ✅ Test files organized in proper directories
- ✅ Coverage remains at 52%+ (no regression)
- ✅ Git status clean (no unexpected changes)
- ✅ No import errors when running `python -m pytest`

---

## Post-Cleanup Next Steps (Phase 4 Continuation)

After cleanup is complete:

1. **Boost Coverage to 80%+** (Resume Phase 4 Priority 1):
   - `app_factory.py`: 0% → 90%+ (~4% boost)
   - LLM modules: 0% → 90%+ (~3% boost)
   - `document_loader.py`: 28% → 90%+ (~1% boost)
   - Domain objects: 48-70% → 90%+ (~3% boost)
   - `free_query_mode.py`: 0% → 90%+ (~2% boost)

2. **Migrate main.py** (Phase 4 Priority 2):
   - Replace `DocumentIndexer` with `IndexingOrchestrator`
   - Extract `ProgressTracker` to separate module
   - Remove duplicate `CustomOpenAI` class
   - Move `validate_environment()` to utilities
   - Update CLI interface

3. **Final Cleanup** (Post-Phase 4):
   - Delete `tests/old/` directory (archive to backup branch)
   - Remove `IndexerConfig` legacy bridge
   - Evaluate integration layers for removal
   - Update all imports to new focused configs

---

## Files to Create/Modify Summary

### Create:
- `src/config/indexer_config.py` - Legacy compatibility bridge

### Modify:
- `src/config/__init__.py` - Export IndexerConfig

### Move:
- `tests/test_indexing_orchestrator.py` → `tests/unit/`
- `tests/test_api.py` → `tests/unit/` or `tests/integration/`

### Delete:
- `srcstrategieschunking/` (empty directory)
- `srcstrategiesextraction/` (empty directory)
- `demo_free_vs_paid.py` (interactive demo, not needed)

### Commit:
- 10 staged documentation files (already ready)

### Archive (Later):
- `tests/old/` entire directory (after Phase 4)

---

## Notes

- **Strangler Fig Pattern**: Continue building new alongside old, no breaking changes
- **Backward Compatibility**: IndexerConfig bridge maintains old interface
- **Test-Driven**: Run tests after each change to catch regressions
- **Incremental**: Each phase can be committed independently
- **Reversible**: All changes can be rolled back via git if needed

---

## Related Documentation

- [Refactoring Plan](REFACTOR_PLAN.md) - Overall refactoring strategy
- [Phase 4 Progress](PHASE4_PROGRESS.md) - Current phase status
- [Testing Guide](TESTING.md) - Test conventions and coverage goals
