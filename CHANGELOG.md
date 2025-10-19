# Changelog

## [2.0.0] - 2025-10-19

### Breaking Changes
- **Package Consolidation**: Removed duplicate `tui_form_engine` and `tui_form_editor` packages
- All functionality now in single `tui_form_designer` package
- See `MIGRATION_v2.0.0.md` for migration guide

### Removed
- ❌ `tui_form_engine` package (was outdated duplicate)
- ❌ `tui_form_editor` package (was outdated duplicate)
- ❌ `pyproject-engine.toml` and `pyproject-editor.toml`
- ❌ `README-engine.md` and `README-editor.md`

### Changed
- Single source of truth: `src/tui_form_designer/`
- Simplified import paths: `from tui_form_designer import ...`
- Cleaner project structure

### Notes
- All 93 tests passing
- All CLI tools still work
- All functionality preserved
- **Migration guide**: See `MIGRATION_v2.0.0.md`

## [1.1.0] - 2025-10-19

### Fixed
- **CRITICAL**: Robust signal handling (Ctrl+C) - Phase 1 complete
- None-return detection after question.ask()
- Emergency exit handler (double Ctrl+C)
- Test suite stabilization (UI mocking, validation, preview formatting)

### Changed
- CI workflow updates (modern GitHub Actions v4)
- Updated to pytest-mock for test dependencies

### Added
- Signal handling tests
- Release notes (RELEASE_v1.1.0.md)
- Comprehensive documentation updates

## [1.0.1] - 2025-10-16

### Added
- Automated build and release workflow via GitHub Actions
- Package distribution via GitHub Releases
- Three-tier branching strategy implementation

### Changed
- Switched from dynamic to static versioning for build system compatibility

### Infrastructure
- GitHub Actions CI/CD pipeline
- Automated packaging and release

## [1.0.0] - Initial Release

### Added
- Interactive TUI form designer
- Questionary-based forms
- Form editor and engine components
- Comprehensive form building tools
