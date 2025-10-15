# TUI Form Designer - Complete Field Reference

## Top-Level Fields (Layout File Root)

### Currently Used:
```yaml
flow_id: "my_form"              # ⚠️ CONFLICTS with control-flow system
title: "My Form Title"
description: "Form description"
icon: "🔧"
version: "1.0.0"
metadata: {...}                 # Optional metadata object
defaults_file: "path/to/defaults.yml"
steps: [...]                    # Array of step definitions
output_mapping: {...}           # Optional output transformation
validation: {...}               # Optional validation rules
```

### Sublayout-Specific:
```yaml
sublayout_defaults: "path/to/defaults.yml"  # For sublayout fragments
```

---

## Metadata Object Fields

```yaml
metadata:
  id: "form_identifier"
  version: "1.0.0"
  type: "modular"
  components: 7
  maintainer: "Team Name"
  created: "2024"
  description: "Detailed description"
  author: "Author Name"
  category: "deployment"
  tags: ["tag1", "tag2"]
  estimated_time: "5 minutes"
```

---

## Step Fields (Common)

### Required for Most Types:
```yaml
id: "step_identifier"         # Unique step ID
type: "text"                  # Step type: text, select, multiselect, confirm, password, info, computed
message: "Question text"      # The question/prompt (not required for info, computed)
```

### Optional (All Types):
```yaml
condition: "previous_step == 'value'"  # Conditional display
instruction: "Help text"               # Additional guidance
default: "default value"               # Default value
```

---

## Step Type-Specific Fields

### Text Input (`text`):
```yaml
validate: "required"           # Validation rule
pattern: "regex"              # Regex pattern
error_message: "Custom error" # Custom validation message  
min_length: 3
max_length: 50
```

### Single Selection (`select`):
```yaml
choices: ["A", "B", "C"]      # Simple list
# OR
choices:                      # Advanced format
  - name: "Display name"
    value: "actual_value"
default: "A"
```

### Multiple Selection (`multiselect`):
```yaml
choices: ["A", "B", "C"]
defaults: ["A"]               # Pre-selected (note: plural!)
min_selections: 1
max_selections: 3
```

### Confirmation (`confirm`):
```yaml
default: true                 # Boolean default
```

### Password (`password`):
```yaml
validate: "password_length"
min_length: 8
confirm: true                 # Ask for confirmation
```

### Information Display (`info`):
```yaml
title: "Section Header"       # Header (message is the body)
message: |                    # Multi-line content
  Line 1
  Line 2
```

### Computed Values (`computed`):
```yaml
compute: "expression"         # Python expression
when: "condition"             # When to compute
description: "What it does"
fallback: "default"           # If computation fails
```

---

## Sublayout Reference Fields

```yaml
subid: "unique_sublayout_id"     # Unique ID for this sublayout ref
sublayout: "./path/to/file.yml"  # Path to sublayout file
```

---

## Output Mapping Fields

```yaml
output_mapping:
  section_name:
    output_key: "step_id"      # Map step to output structure
```

---

## Validation Fields

```yaml
validation:
  rules: [...]
  # (Structure varies - check examples)
```

---

## Summary: Field Name Conflicts

### ⚠️ CONFLICT DETECTED:
**`flow_id`** is used in:
1. **TUI Form Designer** (`.layout.yml` files) - identifies a form/layout
2. **Control-Flow Engine** (`control_flows.yml`) - identifies a control flow

### Recommended Rename:
**`flow_id` → `layout_id`**

**Rationale:**
- Files are named `*.layout.yml`
- Avoids confusion with control-flow system
- More descriptive of actual purpose
- Consistent with naming convention

### Alternative Options:
- `form_id` - emphasizes it's a form
- `tui_id` - emphasizes TUI-specific
- `layout_id` - ✅ **RECOMMENDED** - matches file naming

---

## Complete Field List (Alphabetical)

```
author          # metadata field
category        # metadata field
choices         # select/multiselect field
components      # metadata field  
compute         # computed field
condition       # step field
confirm         # password field
created         # metadata field
default         # step field
defaults        # multiselect field (note: plural)
defaults_file   # top-level field
description     # top-level or metadata field
error_message   # text field
estimated_time  # metadata field
fallback        # computed field
flow_id         # ⚠️ top-level field (RENAME TO layout_id)
icon            # top-level field
id              # step field or metadata field
instruction     # step field
max_length      # text field
max_selections  # multiselect field
message         # step field
metadata        # top-level object
min_length      # text/password field
min_selections  # multiselect field
name            # choice field (in advanced format)
output_mapping  # top-level object
pattern         # text field
steps           # top-level array
subid           # sublayout reference field
sublayout       # sublayout reference field  
sublayout_defaults  # sublayout-specific field
tags            # metadata field
title           # top-level or info step field
type            # step field or metadata field
validate        # step field
validation      # top-level object
value           # choice field (in advanced format)
version         # top-level or metadata field
when            # computed field
```

---

**Total Unique Fields: ~40**
**Conflict: 1 (`flow_id`)**
**Recommended Change: `flow_id` → `layout_id`**
