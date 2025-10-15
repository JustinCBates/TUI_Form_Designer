# TUI Form Validator v2.2 - Enhanced Validation

**Date:** October 15, 2025  
**Version:** 2.2.0  
**Status:** ✅ Complete  
**Type:** Enhancement (non-breaking)

---

## Overview

Version 2.2 adds comprehensive validation of defaults files and recursive sublayout validation, ensuring complete dependency validation for TUI layouts.

---

## New Features

### 1. Defaults File Validation

**Problem:** Layouts reference `defaults_file` but validator didn't check if files exist or are valid.

**Solution:** Validator now validates:
- ✅ File exists at specified path (relative to layout file)
- ✅ File contains valid YAML syntax
- ✅ File contains a dictionary/mapping (not list or scalar)

**Example:**
```yaml
# Layout file
layout_id: my_form
defaults_file: defaults/my_form.defaults.yml  # This path is now validated!
```

**Error Messages:**
```
❌ Defaults file not found: defaults/my_form.defaults.yml (resolved to: /full/path)
❌ Invalid YAML in defaults file: ...
❌ Defaults file is empty: defaults/my_form.defaults.yml
❌ Defaults file must contain a dictionary/mapping: defaults/my_form.defaults.yml
```

---

### 2. Sublayout Defaults Validation

**Problem:** Sublayouts reference `sublayout_defaults` but these weren't validated.

**Solution:** Same validation as `defaults_file` but for sublayouts.

**Example:**
```yaml
# Sublayout file
title: "Database Configuration"
sublayout_defaults: ../defaults/subdefaults/database.defaults.yml  # Validated!
```

**Fixed Issue:** All sublayout defaults paths were using incorrect relative paths:
- ❌ Before: `defaults/subdefaults/file.yml` (missing `../`)
- ✅ After: `../defaults/subdefaults/file.yml` (correct relative path)

---

### 3. Recursive Sublayout Validation

**Problem:** Layouts reference sublayouts but validator didn't validate the sublayout files themselves.

**Solution:** Validator now:
- ✅ Checks sublayout file exists
- ✅ Validates sublayout YAML syntax
- ✅ Recursively validates sublayout structure
- ✅ Validates sublayout's defaults files
- ✅ Reports errors with sublayout context

**Example:**
```yaml
# Parent layout
steps:
  - subid: db_config
    sublayout: ./sublayouts/database.layout.yml  # This file is validated!
```

**Error Messages:**
```
❌ Step 3: Sublayout file not found: ./sublayouts/database.layout.yml
❌ Step 3: Invalid YAML in sublayout ./sublayouts/database.layout.yml: ...
❌ Step 3 (sublayout ./sublayouts/database.layout.yml): Missing required field: title
❌ Step 3 (sublayout ./sublayouts/database.layout.yml): Defaults file not found: ...
```

---

## Path Resolution

All paths are resolved relative to the layout file location:

```
layouts/
  config_tui.layout.yml
    defaults_file: defaults/config_tui.defaults.yml  # Resolved from layouts/
  sublayouts/
    database.layout.yml
      sublayout_defaults: ../defaults/subdefaults/database.defaults.yml  # Resolved from layouts/sublayouts/
  defaults/
    config_tui.defaults.yml
    subdefaults/
      database.defaults.yml
```

---

## Files Modified

### Validator Code (1 file)
**File:** `src/tui_form_designer/tools/validator.py`

**Changes:**
1. Added `_validate_defaults_file()` method
2. Added `_validate_sublayout_references()` method
3. Updated `validate_flow_file()` to call new validators
4. Updated `_validate_sublayout()` to accept file path parameter
5. Uses `.resolve()` for absolute path resolution

### Layout Files (10 files)
Fixed sublayout defaults paths in:
- `phases/.../sublayouts/*.layout.yml` (5 files)
- `src/.../sublayouts/*.layout.yml` (5 files)

**Change:** `defaults/subdefaults/` → `../defaults/subdefaults/`

### Documentation (3 files)
1. `VALIDATOR_NO_BACKWARD_COMPATIBILITY.md` - Updated with v2.2 changes
2. `VALIDATOR_QUICK_REFERENCE.md` - Added new validation checks
3. `VALIDATOR_V2.2_ENHANCEMENTS.md` - This file

---

## Validation Results

### All Forms Pass
```
✅ 19/19 layout files pass comprehensive validation
- All layout_id fields present
- All defaults_file paths valid
- All sublayout_defaults paths valid  
- All sublayouts recursively validated
- All defaults files contain valid YAML dictionaries
- Production-ready
```

### Example Output
```bash
$ tui-designer validate config_tui.layout.yml

🔍 Flow Validation
🔒 STRICT MODE (default) - Production-ready validation enabled
===================

🔧 Validating: config_tui.layout.yml
✅ Valid flow (production-ready)
```

---

## Benefits

1. **Catch Errors Early**: Missing or invalid defaults files caught during validation
2. **Complete Dependency Validation**: All referenced files validated
3. **Recursive Validation**: Sublayouts validated automatically
4. **Better Error Messages**: Clear indication of which file has issues
5. **Production Confidence**: Know that all dependencies exist before runtime

---

## Breaking Changes

**None** - This is a backward-compatible enhancement. Existing valid forms remain valid.

However, forms with missing or invalid defaults files will now **fail** validation (which is correct behavior).

---

## Migration Guide

### If You Get Defaults File Errors

**Error:**
```
❌ Defaults file not found: defaults/my_form.defaults.yml
```

**Solution:**
1. Check the path is correct relative to the layout file
2. Create the missing defaults file
3. Ensure it contains valid YAML with a dictionary

**Example defaults file:**
```yaml
# defaults/my_form.defaults.yml
project_name: "openproject"
admin_email: "admin@example.com"
enable_ssl: true
```

### If You Get Sublayout Path Errors

**Error:**
```
❌ Step 2 (sublayout ./sublayouts/db.layout.yml): Defaults file not found: defaults/subdefaults/db.defaults.yml
```

**Solution:**
Update sublayout defaults path to use correct relative path:
```yaml
# In sublayout file (layouts/sublayouts/db.layout.yml)
# Wrong:
sublayout_defaults: "defaults/subdefaults/db.defaults.yml"

# Correct:
sublayout_defaults: "../defaults/subdefaults/db.defaults.yml"
```

---

## Testing

Tested with:
- 19 layout files in config-manager
- 5 standalone flows
- 14 sublayouts
- 6 defaults files
- 10 sublayout defaults files

All pass validation ✅

---

## Version History

- **v2.2.0** (Oct 15, 2025) - Added defaults validation and recursive sublayout validation
- **v2.1.0** (Oct 15, 2025) - Renamed flow_id to layout_id, strict by default
- **v2.0.0** (Oct 14, 2025) - Made strict validation default
- **v1.0.0** - Initial validator release
