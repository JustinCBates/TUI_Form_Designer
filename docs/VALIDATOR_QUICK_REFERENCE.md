# TUI Form Validator - Quick Reference

**Version:** 2.2.0  
**Status:** ✅ Production-Ready (Strict Mode by Default)

---

## Quick Commands

```bash
# Validate single form (strict by default)
tui-designer validate my_form.yml

# Validate all forms in directory
tui-designer validate

# Development mode (not recommended)
tui-designer validate my_form.yml --no-strict

# Interactive mode
tui-designer validate --interactive
```

---

## What the Validator Checks (v2.2)

### Layout Files
- ✅ Required fields: `layout_id`, `title`, `steps`
- ✅ Valid step types and structure
- ✅ **NEW**: `defaults_file` existence and YAML validity
- ✅ **NEW**: Referenced sublayout files existence
- ✅ **NEW**: Recursive sublayout validation

### Sublayout Files
- ✅ Required fields: `title`, `steps`
- ✅ Same step validation as layouts
- ✅ **NEW**: `sublayout_defaults` existence and YAML validity

### Defaults Files (NEW in v2.2)
- ✅ File existence at specified path
- ✅ Valid YAML syntax
- ✅ Contains dictionary/mapping (not list or scalar)

### Production-Ready Checks (Strict Mode)
- ✅ TODO comments in YAML
- ✅ Placeholder IDs: `example_*`, `test_*`, etc.
- ✅ Generic messages and instructions
- ✅ Scaffolding template patterns

---

## Required Fields

### Standalone Flow
```yaml
layout_id: my_form        # REQUIRED (renamed from flow_id in v2.1)
title: "My Form"        # REQUIRED
steps: [...]           # REQUIRED
defaults_file: "path"   # OPTIONAL (validated if present)
```

### Sublayout (Fragment)
```yaml
# layout_id NOT required (it's a fragment)
title: "Database Config"       # REQUIRED
steps: [...]                  # REQUIRED
sublayout_defaults: "path"     # OPTIONAL (validated if present)
```

### Sublayout Reference
```yaml
steps:
  - subid: db_config      # REQUIRED for sublayout refs
    sublayout: "./path"   # REQUIRED (file validated automatically)
```

---

## Valid Step Types

- ✅ `text` - Text input
- ✅ `select` - Single selection
- ✅ `multiselect` - Multiple selection
- ✅ `confirm` - Yes/No
- ✅ `password` - Password input
- ✅ `computed` - Computed values
- ✅ `info` - Information display

---

## Production-Ready Checks (Strict Mode - Default)

### ❌ Will Fail/Warn

**TODO Comments:**
```yaml
# TODO: Add defaults  # <- ❌ WARNING
flow_id: my_form
```

**Placeholder IDs:**
```yaml
- id: example_input    # <- ❌ WARNING (example_*)
- id: test_field       # <- ❌ WARNING (test_*)
- id: placeholder_x    # <- ❌ WARNING (placeholder_*)
```

**Generic Messages:**
```yaml
message: "Enter a value:"  # <- ❌ WARNING
message: "Provide configuration input"  # <- ❌ WARNING
```

### ✅ Will Pass

**Proper Form:**
```yaml
flow_id: discovery_prompt
title: "Discovery Configuration"
steps:
  - id: discovery_mode
    type: select
    message: "Choose discovery mode:"
    choices:
      - value: auto
        label: "Automatic Discovery"
```

---

## Common Errors & Fixes

### Error: Missing required field: layout_id
```yaml
# ❌ Bad
title: "My Form"
steps: [...]

# ✅ Good
layout_id: my_form
title: "My Form"
steps: [...]
```

### Error: Invalid step type 'info'
**FIXED!** `info` is now valid (was missing from validator)

### Error: Invalid step type 'multiselect'
**FIXED!** `multiselect` is now valid (was missing from validator)

### Warning: TODO comments found
```yaml
# ❌ Bad
# TODO: Add this later
flow_id: my_form

# ✅ Good
flow_id: my_form
# (no TODO comments)
```

### Warning: Placeholder ID detected
```yaml
# ❌ Bad
- id: example_input

# ✅ Good
- id: discovery_mode
```

---

## Validation Status

**Config Manager Forms:** 19/19 ✅ PASS

- ✅ discovery_prompt.layout.yml
- ✅ config_tui.layout.yml (x2)
- ✅ config_tui_minimal.layout.yml (x2)
- ✅ database.layout.yml (x2 sublayouts)
- ✅ environment.layout.yml (x2 sublayouts)
- ✅ network.layout.yml (x2 sublayouts)
- ✅ project_basics.layout.yml (x2 sublayouts)
- ✅ resources.layout.yml (x2 sublayouts)
- ✅ summary.layout.yml (x2 sublayouts)
- ✅ welcome.layout.yml (x2 sublayouts)

---

## Exit Codes

- `0` - All forms valid
- `1` - Validation errors found

---

## Integration

### Pre-commit Hook
```bash
#!/bin/bash
find . -name "*.layout.yml" -exec tui-designer validate {} \;
```

### CI/CD
```yaml
- name: Validate Forms
  run: tui-designer validate
```

---

## Migration Checklist

When creating or updating forms:

- [ ] Add `layout_id` to standalone flows
- [ ] Remove all TODO comments
- [ ] Replace placeholder IDs (example_*, test_*, etc.)
- [ ] Customize all messages (no generic text)
- [ ] Run `tui-designer validate` (strict by default)
- [ ] Fix any warnings before committing

---

**Version:** 2.0.0 (Breaking Changes)  
**Date:** October 15, 2025  
**No Backward Compatibility**
