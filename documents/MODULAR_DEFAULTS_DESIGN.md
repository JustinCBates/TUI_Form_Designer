# Virtual Defaults Reconstruction Design

## Core Concept
Virtual reconstruction system that merges modular defaults files into a unified defaults structure at preprocessing time. The TUI Form Engine receives a single, resolved defaults object after hierarchical merging.

## Architecture

### Virtual Defaults Pipeline
```
Main Layout
├── defaults_file: "defaults/config_TUI.defaults.yml"
├── Sublayout: project_basics.layout.yml
│   └── sublayout_defaults: "defaults/project_basics.defaults.yml"
└── Sublayout: database.layout.yml
    └── sublayout_defaults: "defaults/database.defaults.yml"

                    ⬇ PREPROCESSING ENGINE

Virtual Defaults Object
├── Merged global + sublayout defaults
├── Resolution order: sublayout > global
└── Single unified structure for rendering
```

### Preprocessing Steps
1. **Parse main layout** - Extract global defaults_file reference
2. **Load global defaults** - Base defaults structure
3. **Discover sublayouts** - Find all sublayout references with defaults
4. **Load sublayout defaults** - Individual defaults files
5. **Merge hierarchically** - Sublayout overrides global
6. **Create virtual defaults** - Single unified object

## File Structure

### Global Defaults
```yaml
# defaults/config_TUI.defaults.yml
defaults:
  # UI component defaults
  text_input_style: "border"
  select_style: "pointer"
  confirm_style: "classic"
  
  # Common application defaults
  project_name: "openproject"
  environment: "production"
  backup_retention: "7"
```

### Sublayout Defaults
```yaml
# defaults/project_basics.defaults.yml
defaults:
  project_name: "my-project"     # Overrides global
  admin_email: "admin@example.com"
  admin_password_min_length: 12
  
# defaults/database.defaults.yml  
defaults:
  postgres_db: "openproject_production"
  postgres_user: "openproject_admin"
  postgres_port: "5432"
```

### Virtual Merged Result
```yaml
# Generated at preprocessing time
defaults:
  # UI defaults from global
  text_input_style: "border"
  select_style: "pointer" 
  confirm_style: "classic"
  
  # Application defaults (merged)
  project_name: "my-project"        # From project_basics (override)
  environment: "production"         # From global
  backup_retention: "7"             # From global
  admin_email: "admin@example.com"  # From project_basics
  postgres_db: "openproject_production"  # From database
  postgres_user: "openproject_admin"     # From database
```

## Implementation

### Sublayout Defaults Declaration
```yaml
# In sublayout files
title: "Project Basics"
description: "Basic project information"
sublayout_defaults: "defaults/project_basics.defaults.yml"

steps:
  - id: project_name
    type: text
    # No hardcoded default - comes from virtual defaults
```

### Preprocessing Engine
```python
class DefaultsPreprocessor:
    def merge_defaults(self, layout_path):
        # 1. Load main layout and global defaults
        # 2. Discover sublayouts with defaults
        # 3. Load all sublayout defaults files
        # 4. Merge with hierarchy: sublayout > global > hardcoded
        # 5. Return unified virtual defaults object
        pass
        
    def apply_defaults_to_step(self, step, virtual_defaults):
        """
        Apply defaults with three-tier fallback:
        1. Check virtual_defaults for step.id
        2. If not found, use step.default (hardcoded)
        3. If neither exists, no default
        """
        step_id = step.get('id')
        if step_id in virtual_defaults:
            step['default'] = virtual_defaults[step_id]
        # else: keep existing step.default as fallback
        return step
```

## Benefits

### Simplified Rendering
- TUI Form Engine receives single defaults object
- No complex runtime resolution needed
- Clear, predictable default values

### Maintainable Modularity  
- Each sublayout manages its own defaults
- Global defaults provide base layer
- Clean separation of concerns

### Performance
- Preprocessing happens once at layout load
- Runtime execution uses pre-resolved defaults
- No file I/O during form rendering

## Resolution Rules

### Override Priority (Three-Tier Fallback)
1. **Sublayout defaults** (highest) - From sublayout_defaults file
2. **Global defaults** (medium) - From main layout defaults_file
3. **Hardcoded defaults** (lowest) - Fallback safety net in step definition

### Conflict Resolution
- Same key in multiple sublayouts: Last sublayout wins
- Missing sublayout defaults file: Falls back to global defaults
- Missing global defaults: Falls back to hardcoded step defaults
- Missing all defaults: Field has no default (user must provide value)

## Next Steps
1. Implement DefaultsPreprocessor class
2. Update sublayout files with sublayout_defaults declarations
3. Create sublayout-specific defaults files
4. Integrate with virtual layout reconstruction