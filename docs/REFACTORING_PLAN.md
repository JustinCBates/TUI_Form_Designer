# TUI Form Designer - Refactoring Plan

Branch: `refactor`
Date: 2025-10-19
Owner: Core maintainers

This plan guides the refactor work based on `ANTI_PATTERN_ANALYSIS.md`.

## Goals
- Eliminate production blocker (signal handling)
- Consolidate packages into a single maintainable structure
- Clarify naming (Flow → Form) and public API
- Improve reliability with tests and consistent error handling

## Phases

### Phase 1: Critical Safety Fix (v1.1.0) ✅ COMPLETE
**Status:** ✅ **COMPLETE** - Commit: `3a82ce3` (January 19, 2025)  
**Duration:** ~2 hours  

- [x] Implement robust Ctrl+C propagation (no silent None returns)
- [x] Add emergency exit (double Ctrl+C → force exit)
- [x] Add signal handling tests (single, loop, nested)
- [x] Update CRITICAL-SIGNAL-HANDLING-ISSUE.md to resolved

**Implementation:**
- Added None-return detection after question.ask()
- Emergency exit handler (double Ctrl+C within 2 seconds → sys.exit(130))
- Signal handler install/restore in execute_flow()
- 2/2 tests passing in tests/test_signal_handling.py

**Files Changed:**
- src/tui_form_designer/core/flow_engine.py (+signal handling)
- tests/test_signal_handling.py (NEW)
- CRITICAL-SIGNAL-HANDLING-ISSUE.md (marked RESOLVED)

### Phase 2: Architecture Cleanup (v2.0.0) ✅ COMPLETE
**Status:** ✅ **COMPLETE** - Commit: TBD (October 19, 2025)

- [x] Consolidate to single package `tui_form_designer`
- [x] Remove `tui_form_engine` and `tui_form_editor` duplicate packages
- [x] All tests still passing (93/93)
- [x] Create MIGRATION_v2.0.0.md guide
- [x] Version bumped to 2.0.0

**Implementation:**
- Deleted src/tui_form_engine/ (outdated duplicate)
- Deleted src/tui_form_editor/ (outdated duplicate)
- Removed pyproject-engine.toml, pyproject-editor.toml
- Removed README-engine.md, README-editor.md
- Single source of truth: src/tui_form_designer/

**Files Changed:**
- Removed: src/tui_form_engine/ (entire directory)
- Removed: src/tui_form_editor/ (entire directory)
- Removed: pyproject-{engine,editor}.toml, README-{engine,editor}.md
- Added: MIGRATION_v2.0.0.md
- Updated: pyproject.toml (version 2.0.0)
- Updated: src/tui_form_designer/__init__.py (version 2.0.0)

### Phase 3: Code Quality (v2.1.0)
- [ ] Standardize error handling (no silent excepts, no None returns)
- [ ] Single source of truth for version (metadata)
- [ ] Type hints for public API
- [ ] Expand tests and coverage thresholds

## Deliverables
- Updated source tree under `src/tui_form_designer/`
- Passing CI with new tests
- Migration notes and deprecation paths
- Versioned releases for each phase

## References
- `ANTI_PATTERN_ANALYSIS.md`
- `CRITICAL-SIGNAL-HANDLING-ISSUE.md`
