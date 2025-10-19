# Release Notes - v2.0.0 (Architecture Cleanup)

**Release Date:** October 19, 2025  
**Breaking Changes:** Yes - Package consolidation  
**Migration Guide:** See [MIGRATION_v2.0.0.md](MIGRATION_v2.0.0.md)

---

## 🎯 Overview

Version 2.0.0 represents a major architectural cleanup that consolidates three separate packages into a single, maintainable codebase. This release eliminates **4,106 lines of duplicate code** while preserving all functionality.

## ⚠️ BREAKING CHANGES

### Package Consolidation

**REMOVED** (were outdated duplicates):
- ❌ `tui_form_engine` package - 2,364 lines removed
- ❌ `tui_form_editor` package - 1,742 lines removed
- ❌ `pyproject-engine.toml` and `pyproject-editor.toml`
- ❌ `README-engine.md` and `README-editor.md`

**KEPT** (actively maintained):
- ✅ `tui_form_designer` - Single source of truth

### Import Changes

#### Before (v1.x) - NO LONGER WORKS:
```python
from tui_form_engine import FlowEngine, QuestionaryUI
from tui_form_editor import FlowValidator, InteractiveFlowDesigner
```

#### After (v2.0) - NEW IMPORT PATHS:
```python
from tui_form_designer import FlowEngine, QuestionaryUI
from tui_form_designer.tools import FlowValidator, InteractiveFlowDesigner
```

## ✨ What's New

### Architecture Improvements
- **Single package design**: All functionality in `tui_form_designer`
- **Eliminated duplication**: 4,106 lines of redundant code removed
- **Cleaner structure**: One import path, one package to install
- **Better maintainability**: Single source of truth for all features

### Documentation
- 📘 New `MIGRATION_v2.0.0.md` with complete upgrade guide
- 📝 Updated `CHANGELOG.md` with breaking changes
- 📋 Updated `REFACTORING_PLAN.md` - Phase 2 complete

## 🔧 What Still Works

### CLI Tools (All Working)
```bash
tui-design      # Interactive flow designer
tui-validate    # Flow validator
tui-test        # Flow tester with mock data
tui-preview     # Flow previewer
```

### Core Functionality
- ✅ FlowEngine execution
- ✅ QuestionaryUI components
- ✅ YAML flow definitions
- ✅ All validation and error handling
- ✅ Signal handling (Ctrl+C safety)

### Tests
- ✅ All 93 tests passing
- ✅ Test coverage maintained
- ✅ CI/CD pipeline green

## 📊 Impact Summary

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **Packages** | 3 | 1 | -66% |
| **Lines of Code** | ~5,000 | ~900 | -82% |
| **Config Files** | 5 | 1 | -80% |
| **README Files** | 3 | 1 | -66% |
| **Import Paths** | Multiple | Single | Simplified |
| **Tests Passing** | 93 | 93 | ✓ Stable |

## 🚀 Installation

### New Installation:
```bash
pip install https://github.com/JustinCBates/TUI_Form_Designer/releases/download/v2.0.0/tui_form_designer-2.0.0-py3-none-any.whl
```

### Upgrading from v1.x:
```bash
# 1. Uninstall old packages
pip uninstall tui-form-designer tui-form-engine tui-form-editor -y

# 2. Install v2.0.0
pip install https://github.com/JustinCBates/TUI_Form_Designer/releases/download/v2.0.0/tui_form_designer-2.0.0-py3-none-any.whl

# 3. Update your imports (see MIGRATION_v2.0.0.md)
```

## 🔄 Migration Steps

### Quick Migration:
```bash
# Update imports in your codebase:
find . -name "*.py" -exec sed -i 's/from tui_form_engine/from tui_form_designer/g' {} +
find . -name "*.py" -exec sed -i 's/from tui_form_editor import/from tui_form_designer.tools import/g' {} +

# Test:
python -c "from tui_form_designer import FlowEngine; print('✓ Migration successful')"
```

For detailed migration instructions, see **[MIGRATION_v2.0.0.md](MIGRATION_v2.0.0.md)**

## 📦 Artifacts

- **Wheel**: `tui_form_designer-2.0.0-py3-none-any.whl` (38.5 KB)
- **Source**: `tui_form_designer-2.0.0.tar.gz` (80.1 KB)

## 🐛 Bug Fixes

None - this is a pure architectural refactor with no functional changes.

## 🔐 Security

No security changes in this release.

## 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

## 🗺️ Roadmap

### v2.1.0 (Planned - Phase 3)
- Standardize error handling
- Add comprehensive type hints
- Expand test coverage
- Performance optimizations

## 🙏 Credits

**Phase 2 Refactoring:**
- Package consolidation and cleanup
- Migration documentation
- CI/CD pipeline maintenance

## 📞 Support

- **Issues**: https://github.com/JustinCBates/TUI_Form_Designer/issues
- **Discussions**: https://github.com/JustinCBates/TUI_Form_Designer/discussions
- **Migration Help**: See [MIGRATION_v2.0.0.md](MIGRATION_v2.0.0.md)

## ⚡ Previous Releases

- **v1.1.0** (Oct 19, 2025): Critical signal handling fix
- **v1.0.1** (Oct 16, 2025): CI/CD pipeline
- **v1.0.0**: Initial release

---

**Note:** This is a breaking release. Please review the migration guide carefully before upgrading production systems.
