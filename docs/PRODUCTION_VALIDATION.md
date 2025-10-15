# Production-Ready Validation for TUI Forms

**Date:** October 15, 2025  
**Status:** ✅ Implemented  
**Version:** 1.0

---

## Overview

Enhanced the TUI Form Designer validator with production-readiness validation to catch incomplete development work before deployment.

## What Was Added

### Strict Validation Mode

New `--strict` flag for the validator that enables production-ready checks beyond basic structural validation.

### Detection Capabilities

The strict validator now catches:

1. **TODO Comments** ✅
   - Detects TODO markers in YAML files
   - Indicates incomplete development work

2. **Placeholder IDs** ✅
   - Patterns: `example_*`, `test_*`, `placeholder_*`, `sample_*`, `demo_*`, `temp_*`, `mock_*`, `dummy_*`
   - Indicates scaffolding that hasn't been customized

3. **Generic Messages** ✅
   - "Enter a value:"
   - "Provide configuration input"
   - "Enter text here"
   - Other generic placeholders

4. **Generic Instructions** ✅
   - "Provide configuration input"
   - "Enter your input"
   - Other placeholder text

5. **Exact Scaffolding Template** ✅
   - Detects forms that exactly match the scaffolding template
   - Catches completely uncustomized forms

6. **Incomplete Forms** ✅
   - Single-step forms with placeholder IDs
   - Minimal implementations

---

## Usage

### Command Line

```bash
# Basic validation (structural only)
tui-designer validate my_form.yml

# Production-ready validation (strict mode)
tui-designer validate my_form.yml --strict

# Or use --production alias
tui-designer validate my_form.yml --production

# Validate all forms in directory (strict)
tui-designer validate --strict

# Interactive mode with strict validation
tui-designer validate --interactive --strict
```

### Python API

```python
from tui_form_designer.core.flow_engine import FlowEngine
import yaml

engine = FlowEngine()

# Load flow
with open('my_form.yml') as f:
    flow_def = yaml.safe_load(f)

# Basic validation
errors = engine.validate_flow(flow_def)

# Strict validation (production-ready)
errors = engine.validate_flow(flow_def, strict=True)

if errors:
    print("Validation issues:")
    for error in errors:
        print(f"  - {error}")
```

---

## Example Output

### Scaffolding Template (Caught by Strict Mode)

```yaml
flow_id: test_prompt
title: "Test Configuration Prompt"

steps:
  # TODO: Define form steps
  - id: example_input
    type: text
    message: "Enter a value:"
    instruction: "Provide configuration input"
    default: ""
```

**Validation Result:**
```
🔒 Running in STRICT mode - production-ready validation enabled

🔧 Validating: test_scaffolding_form.yml
⚠️  TODO comments found in YAML - incomplete development
❌ 5 errors/warnings:
  • Step 0 (example_input): Placeholder ID detected
  • Step 0 (example_input): Generic message 'Enter a value:'
  • Step 0 (example_input): Generic instruction 'Provide configuration input'
  • Step 0: Matches exact scaffolding template - not customized!
  • Only 1 step with placeholder ID - form appears incomplete
```

### Properly Customized Form (Passes Strict Mode)

```yaml
flow_id: discovery_prompt
title: "Discovery Configuration Prompt"

steps:
  - id: discovery_mode
    type: select
    message: "Choose discovery mode:"
    instruction: "Select how you want to configure your deployment"
    choices:
      - value: auto
        label: "Automatic - Discover system automatically"
      - value: manual
        label: "Manual - Provide configuration manually"
    default: "auto"
```

**Validation Result:**
```
🔒 Running in STRICT mode - production-ready validation enabled

🔧 Validating: discovery_prompt.layout.yml
✅ Valid and production-ready
```

---

## Integration

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash

echo "Validating TUI forms..."

# Find all .layout.yml files
layouts=$(find . -name "*.layout.yml" -not -path "*/\.*")

# Validate each with strict mode
for layout in $layouts; do
    if ! python3 -m tui_form_designer.tools.validator "$layout" --strict; then
        echo "❌ Production validation failed for: $layout"
        echo "Fix issues or remove --strict for development work"
        exit 1
    fi
done

echo "✅ All TUI forms are production-ready"
```

### CI/CD Pipeline

```yaml
# .github/workflows/validate-forms.yml
name: Validate TUI Forms

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install tui-form-designer
      
      - name: Validate forms (strict mode)
        run: |
          find . -name "*.layout.yml" -exec \
            python -m tui_form_designer.tools.validator {} --strict \;
```

---

## Implementation Details

### Files Modified

1. **`src/tui_form_designer/core/flow_engine.py`**
   - Added `strict` parameter to `validate_flow()` method
   - Added `_validate_production_ready()` method
   - Implements all detection patterns

2. **`src/tui_form_designer/tools/validator.py`**
   - Added `strict` parameter to `FlowValidator` class
   - Added `--strict` and `--production` CLI flags
   - Added TODO comment detection in raw YAML
   - Enhanced error messages for strict mode

### Code Structure

```python
class FlowEngine:
    def validate_flow(self, flow_definition, strict=False):
        errors = []
        
        # Structural validation (always)
        errors.extend(self._validate_structure(flow_definition))
        
        # Production-ready validation (strict mode only)
        if strict:
            errors.extend(self._validate_production_ready(flow_definition))
        
        return errors
    
    def _validate_production_ready(self, flow_definition):
        """Check for scaffolding patterns and incomplete work."""
        warnings = []
        
        # Check placeholder IDs, generic messages, etc.
        # Returns list of production-readiness warnings
        
        return warnings
```

---

## Design Rationale

### Why Separate Strict Mode?

1. **Development Flexibility**
   - Developers can work with scaffolding during development
   - Basic validation still catches structural errors

2. **Clear Intent**
   - `--strict` flag signals "ready for production"
   - Makes it explicit when production-ready checks are needed

3. **Backward Compatibility**
   - Existing workflows continue to work
   - No breaking changes to validator behavior

### Why These Patterns?

The detection patterns were chosen based on:
- Common scaffolding generators (including control-flow)
- Generic placeholder text that appears in templates
- Patterns that indicate incomplete customization
- Real-world issue: discovery_prompt.layout.yml was overwritten with scaffolding

---

## Best Practices

### During Development

```bash
# Use basic validation while developing
tui-designer validate my_form.yml

# Iterate on form design without strict checks
```

### Before Committing

```bash
# Run strict validation
tui-designer validate my_form.yml --strict

# Fix any warnings before committing
```

### In CI/CD

```bash
# Always use strict mode in pipelines
tui-designer validate --strict --flows-dir layouts/

# Fail builds if validation fails
```

### Code Reviews

- Include form validation in review checklist
- Require strict validation to pass
- Flag any forms with TODO comments

---

## Future Enhancements

Potential improvements:

- [ ] Configurable warning levels (error vs warning)
- [ ] Custom placeholder patterns via config file
- [ ] Auto-fix suggestions for common issues
- [ ] Integration with form designer tool
- [ ] Severity levels for different checks
- [ ] Skip patterns for intentional placeholders

---

## Related Issues

**Original Problem:**
- `discovery_prompt.layout.yml` was overwritten by scaffolder
- Contained exact scaffolding template (`example_input`)
- No validation caught this before runtime

**Solution:**
- Strict validator catches scaffolding patterns
- Prevents deployment of incomplete forms
- Developer-friendly development workflow

---

## Testing

### Test Cases

1. ✅ Scaffolding template → Caught (5 warnings)
2. ✅ TODO comments → Caught
3. ✅ Placeholder IDs → Caught
4. ✅ Generic messages → Caught
5. ✅ Customized form → Passes
6. ✅ Backward compatibility → Basic validation still works

### Test Files

- `/tmp/test_scaffolding_form.yml` - Exact scaffolding template
- `discovery_prompt.layout.yml` - Properly customized form

---

**Status:** ✅ Complete and Ready for Use  
**Version:** 1.0  
**Last Updated:** October 15, 2025
