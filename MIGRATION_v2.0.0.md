# Migration Guide: v1.x → v2.0.0

**Date:** October 19, 2025  
**Breaking Changes:** Yes (package consolidation)

## Summary

Version 2.0.0 consolidates all functionality into a single `tui_form_designer` package, removing the outdated `tui_form_engine` and `tui_form_editor` duplicate packages.

## What Changed

### Package Consolidation

**REMOVED packages** (were duplicates/outdated):
- ❌ `tui_form_engine` - DELETED
- ❌ `tui_form_editor` - DELETED

**KEPT package** (the actively maintained one):
- ✅ `tui_form_designer` - MAIN PACKAGE (contains all features)

### Import Changes

#### Before (v1.x):
```python
# These imports NO LONGER WORK in v2.0:
from tui_form_engine import FlowEngine, QuestionaryUI
from tui_form_editor import FlowValidator, InteractiveFlowDesigner
```

#### After (v2.0):
```python
# All imports from single package:
from tui_form_designer import FlowEngine, QuestionaryUI
from tui_form_designer.tools import FlowValidator, InteractiveFlowDesigner
```

### CLI Command Changes

#### Before (v1.x):
```bash
tui-design    # from tui_form_editor
tui-validate  # from tui_form_editor  
tui-test      # from tui_form_editor
tui-preview   # from tui_form_editor
```

#### After (v2.0):
```bash
# All commands still work, now from tui_form_designer:
tui-design    # from tui_form_designer.tools
tui-validate  # from tui_form_designer.tools
tui-test      # from tui_form_designer.tools
tui-preview   # from tui_form_designer.tools
```

## Migration Steps

### Step 1: Update imports
Search and replace in your codebase:
```bash
# Replace tui_form_engine imports:
find . -name "*.py" -exec sed -i 's/from tui_form_engine/from tui_form_designer/g' {} +

# Replace tui_form_editor tool imports:
find . -name "*.py" -exec sed -i 's/from tui_form_editor import/from tui_form_designer.tools import/g' {} +
```

### Step 2: Update requirements
```bash
# Before:
pip install tui-form-designer tui-form-engine tui-form-editor

# After:
pip install tui-form-designer>=2.0.0
```

### Step 3: Test your code
```bash
# Run your tests to ensure everything works:
pytest

# Or test manually:
python -c "from tui_form_designer import FlowEngine; print('✓ Import successful')"
```

## Why This Change?

1. **Eliminated duplication**: Three packages contained overlapping code
2. **Simpler maintenance**: Single source of truth
3. **Better UX**: One package to install, one import path
4. **Clearer API**: No confusion about which package to use

## Compatibility

### What Still Works
- ✅ All CLI commands (`tui-design`, `tui-validate`, etc.)
- ✅ All public APIs (FlowEngine, QuestionaryUI, etc.)
- ✅ All YAML flow definitions
- ✅ All functionality from v1.x

### What Breaks
- ❌ Imports from `tui_form_engine` package
- ❌ Imports from `tui_form_editor` package
- ❌ Installing separate `tui-form-engine` or `tui-form-editor` packages

## Rollback Plan

If you need to stay on v1.x:
```bash
pip install tui-form-designer==1.1.0
```

## Support

- **Issues**: https://github.com/JustinCBates/TUI_Form_Designer/issues
- **Discussions**: https://github.com/JustinCBates/TUI_Form_Designer/discussions

## Timeline

- **v1.1.0**: Last 1.x release (signal handling fix)
- **v2.0.0**: Package consolidation (this release)
- **v2.1.0**: Code quality improvements (planned)
