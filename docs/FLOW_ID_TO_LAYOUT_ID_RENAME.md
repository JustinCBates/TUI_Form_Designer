# TUI Form Designer - flow_id → layout_id Rename

**Date:** October 15, 2025  
**Status:** ✅ COMPLETE  
**Breaking Change:** YES  
**Version:** 2.1.0

---

## Summary

Renamed `flow_id` to `layout_id` throughout the TUI Form Designer to avoid confusion with the control-flow system's `flow_id`.

### Rationale

**Problem:** Both systems used `flow_id`:
- **Control-Flow Engine** uses `flow_id` in `control_flows.yml` to identify control flows (phase orchestration)
- **TUI Form Designer** used `flow_id` in `.layout.yml` files to identify forms

**Solution:** Rename TUI's `flow_id` to `layout_id`:
- Matches file naming convention (`.layout.yml` files)
- Avoids namespace collision
- More descriptive of purpose
- Clear separation of concerns

---

## What Changed

### Before (v2.0)
```yaml
flow_id: my_form
title: "My Form"
steps: [...]
```

### After (v2.1)
```yaml
layout_id: my_form  # ← Renamed from flow_id
title: "My Form"
steps: [...]
```

---

## Files Modified

### TUI Form Designer Core (4 files)

1. **`src/tui_form_designer/core/flow_engine.py`**
   - Changed required field from `flow_id` to `layout_id`
   - Line 156: `required_fields = ['layout_id', 'title', 'steps']`

2. **`src/tui_form_designer/tools/validator.py`**
   - Updated sublayout detection logic
   - Updated comments referencing flow_id
   - Line 68: Check for `layout_id` not in sublayouts

3. **`src/tui_form_designer/tools/demo.py`**
   - Updated all sample flows to use `layout_id`
   - Line 136: `'layout_id': 'simple_survey'`
   - Line 184: `'layout_id': 'app_setup'`
   - Line 229: `'layout_id': 'user_registration'`

4. **`src/tui_form_designer/tools/designer.py`**
   - Updated interactive designer to use `layout_id`
   - Line 110: Prompt changed to "Layout ID (filename without .yml)"
   - Line 120: `'layout_id': layout_id`
   - Line 142: Save path uses `layout_id` variable

### Config Manager Layouts (5 files)

1. **`phases/phase_1_discovery/step_0_discovery_prompt/discovery_prompt.layout.yml`**
   - `flow_id: discovery_prompt` → `layout_id: discovery_prompt`

2. **`phases/phase_3_collection/.../layouts/config_tui.layout.yml`**
   - `flow_id: config_tui` → `layout_id: config_tui`

3. **`phases/phase_3_collection/.../layouts/test_layouts/config_tui_minimal.layout.yml`**
   - `flow_id: config_tui_minimal` → `layout_id: config_tui_minimal`

4. **`src/openproject_config_manager/collector/layouts/config_tui.layout.yml`**
   - `flow_id: config_tui` → `layout_id: config_tui`

5. **`src/openproject_config_manager/collector/layouts/test_layouts/config_tui_minimal.layout.yml`**
   - `flow_id: config_tui_minimal` → `layout_id: config_tui_minimal`

### Control-Flow Scaffolder (1 file)

1. **`external/control-flow/src/control_flow_engine/core/scaffolder.py`**
   - Updated TUI layout template to use `layout_id`
   - Line 610: Template changed from `flow_id:` to `layout_id:`

### Documentation (4 files)

1. **`README.md`**
   - Updated main example to use `layout_id`

2. **`README-engine.md`**
   - Updated example to use `layout_id`

3. **`VALIDATOR_NO_BACKWARD_COMPATIBILITY.md`**
   - Updated references from `flow_id` to `layout_id`
   - Updated error messages
   - Updated migration guide

4. **`VALIDATOR_QUICK_REFERENCE.md`**
   - Updated quick reference examples
   - Updated error messages
   - Updated checklists

5. **`FIELD_REFERENCE.md`** (NEW)
   - Comprehensive field documentation
   - Lists all 40 fields used in TUI layouts
   - Highlights the conflict and resolution

---

## Validation Results

### All Forms Pass

```bash
$ find config-manager -name "*.layout.yml" | wc -l
19

$ tui-designer validate [all 19 files]
✅ PASSED: 19/19
❌ FAILED: 0/19
```

**Breakdown:**
- Standalone flows: 5/5 pass
- Sublayouts: 14/14 pass
- All forms production-ready ✅

---

## Breaking Changes

### ⚠️ Required Action

**All existing `.layout.yml` files must be updated:**

```bash
# Find and replace in all layout files
find . -name "*.layout.yml" -exec sed -i 's/^flow_id:/layout_id:/' {} \;
```

**Or manually:**
```yaml
# Change this:
flow_id: my_form

# To this:
layout_id: my_form
```

### Validator Behavior

**Before:** Missing `flow_id` → Error  
**After:** Missing `layout_id` → Error

```
❌ Missing required field: layout_id
```

---

## Compatibility Matrix

| Component | Field Name | Purpose |
|-----------|------------|---------|
| Control-Flow Engine | `flow_id` | Identifies control flows in `control_flows.yml` |
| TUI Form Designer (NEW) | `layout_id` | Identifies TUI layouts in `.layout.yml` |
| ~~TUI Form Designer (OLD)~~ | ~~`flow_id`~~ | ❌ **REMOVED** - caused confusion |

---

## Migration Guide

### For Developers

**Step 1:** Update existing layout files
```bash
cd your-project
find . -name "*.layout.yml" -exec sed -i 's/^flow_id:/layout_id:/' {} \;
```

**Step 2:** Validate all forms
```bash
tui-designer validate
```

**Step 3:** Update any code that references `flow_id`
- Search for `flow_def['flow_id']` → change to `flow_def['layout_id']`
- Update any YAML parsing code

**Step 4:** Update documentation
- README files
- Developer guides
- API documentation

### For Projects Using TUI Form Designer

**If you have custom code:**
1. Search for `flow_id` references in your codebase
2. Replace with `layout_id` where it refers to TUI layouts
3. Keep `flow_id` for control-flow references

**Example:**
```python
# Before
layout = yaml.safe_load(file)
form_id = layout['flow_id']  # ❌ Old

# After
layout = yaml.safe_load(file)
form_id = layout['layout_id']  # ✅ New
```

---

## Why layout_id?

### Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| `form_id` | Clear purpose | Less specific | ❌ Not chosen |
| `tui_id` | TUI-specific | Too generic | ❌ Not chosen |
| **`layout_id`** | **Matches `.layout.yml`** | **None** | ✅ **CHOSEN** |

### Benefits

1. **Consistency** - Files are `.layout.yml`, identifier is `layout_id`
2. **Clarity** - Immediately clear what it identifies
3. **Separation** - No confusion with control-flow's `flow_id`
4. **Descriptive** - Describes structure (layout) not just function (form)

---

## Testing

### Test 1: Validator Accepts layout_id
```bash
$ tui-designer validate discovery_prompt.layout.yml
✅ Valid flow (production-ready)
```

### Test 2: All Forms Pass
```bash
$ find config-manager -name "*.layout.yml" -exec tui-designer validate {} \;
✅ 19/19 PASSED
```

### Test 3: Sample Flows Valid
```bash
$ tui-designer demo
✅ Sample flows created with layout_id
```

---

## Rollback Procedure

**If needed**, rollback is straightforward:

```bash
# Revert all layout files
find . -name "*.layout.yml" -exec sed -i 's/^layout_id:/flow_id:/' {} \;

# Checkout previous validator version
git checkout v2.0 -- src/tui_form_designer/
```

**Note:** Not recommended - layout_id is the correct naming.

---

## Future Considerations

### Potential Enhancements

1. **Automatic Migration Tool**
   ```bash
   tui-designer migrate --from flow_id --to layout_id
   ```

2. **Backward Compatibility Warning**
   - Detect old `flow_id` in layouts
   - Show deprecation warning
   - Auto-suggest migration

3. **IDE Support**
   - Update VSCode snippets
   - Update schema files
   - Update autocomplete

---

## Documentation Updates

All documentation now uses `layout_id`:

- ✅ README.md
- ✅ README-engine.md
- ✅ VALIDATOR_NO_BACKWARD_COMPATIBILITY.md
- ✅ VALIDATOR_QUICK_REFERENCE.md
- ✅ FIELD_REFERENCE.md (NEW)
- ✅ Inline code comments
- ✅ Docstrings
- ✅ Examples

---

## Impact Assessment

### Low Impact

**Why?**
- Early in development
- Only 19 layout files to update
- No external users yet
- Clear migration path
- Immediate benefits

### Benefits Outweigh Costs

**Benefits:**
- ✅ No namespace conflicts
- ✅ Clear separation of concerns
- ✅ Better naming convention
- ✅ Matches file extension
- ✅ Future-proof

**Costs:**
- ⚠️ One-time migration of 19 files
- ⚠️ Update documentation

**Verdict:** ✅ Rename is justified and beneficial

---

## Status

✅ **COMPLETE**

- Core validator updated
- All layout files migrated
- All documentation updated
- All tests passing (19/19)
- Control-flow scaffolder updated
- No breaking issues found

## 📝 **Lessons Learned**

### ⚠️ **Demo Files Oversight**

**Issue Discovered:** Demo files in `tui_layouts/` directory were initially missed during the refactor and still contained `flow_id` instead of `layout_id`.

**Impact:** 
- Demo commands failed to execute
- New users couldn't test basic functionality
- CLI tools couldn't discover available flows

**Resolution:** 
- Updated `tui_layouts/basic/simple_survey.yml`
- Updated `tui_layouts/basic/user_registration.yml`
- Added this documentation note for future refactors

### 🔄 **Refactor Checklist for Future Changes**

When performing field renames or structural changes, ensure ALL of the following are updated:

**Core Components:**
- [ ] Source code files
- [ ] Validation logic
- [ ] Error messages

**Examples & Demos:**
- [ ] Demo YAML files in `tui_layouts/`
- [ ] Inline code examples in tools/demo.py
- [ ] README.md examples
- [ ] Documentation examples

**External Projects:**
- [ ] Config Manager layouts
- [ ] Control-Flow scaffolder templates
- [ ] Any dependent repositories

**Testing & Validation:**
- [ ] Unit tests
- [ ] Integration tests
- [ ] Demo functionality verification
- [ ] CLI command verification

**Documentation:**
- [ ] README files
- [ ] API documentation
- [ ] Migration guides
- [ ] Breaking change notifications

**CRITICAL:** Demo files are often overlooked but are essential for:
- First-time user experience
- CLI tool functionality
- Automated testing
- Documentation examples

---

**Version:** 2.1.0  
**Breaking Change:** YES (field renamed)  
**Migration Required:** YES (simple find/replace)  
**Rollback Available:** YES (not recommended)  

**Last Updated:** October 16, 2025
