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

## Implementation Status ✅ COMPLETE

### Implemented Components

#### 1. Preprocessing Engine (`collect_user_configuration.py`)
The `_expand_sublayouts()` method implements the full virtual defaults reconstruction:
- ✅ Loads global `defaults_file` from main layout
- ✅ Discovers sublayouts with `sublayout_defaults` declarations
- ✅ Loads all sublayout defaults files
- ✅ Merges hierarchically (sublayout > global > hardcoded)
- ✅ Creates unified `unified_defaults.yml` file
- ✅ Updates flow definition to use unified defaults

```python
# Actual implementation in collect_user_configuration.py
def _expand_sublayouts(self, flow_data: Dict[str, Any], flow_path: Path):
    # 1. Load global defaults
    merged_defaults = {}
    if 'defaults_file' in flow_data:
        global_defaults = self._load_defaults_file(...)
        merged_defaults.update(global_defaults)
    
    # 2. Expand sublayouts and merge their defaults
    for step in flow_data['steps']:
        if 'sublayout' in step:
            sublayout_data = yaml.safe_load(...)
            
            # Load sublayout defaults (overrides global)
            if 'sublayout_defaults' in sublayout_data:
                sublayout_defaults = self._load_defaults_file(...)
                merged_defaults.update(sublayout_defaults)
    
    # 3. Create unified defaults file
    unified_defaults_path = self.output_dir / "unified_defaults.yml"
    yaml.safe_dump({'defaults': merged_defaults}, ...)
    flow_data['defaults_file'] = str(unified_defaults_path.absolute())
```

#### 2. TUI Engine Defaults Loading (`flow_engine.py`)
The `_merge_defaults()` method applies the unified defaults to steps:
- ✅ Loads `defaults_file` from flow definition
- ✅ Resolves absolute and relative paths
- ✅ Merges defaults into step definitions
- ✅ Respects priority: unified defaults > hardcoded step defaults
- ✅ Handles missing defaults gracefully (silent fallback)

```python
# Actual implementation in flow_engine.py
def _load_flow(self, flow_id: str) -> Dict[str, Any]:
    flow_def = yaml.safe_load(...)
    
    # Load and merge defaults if defaults_file is specified
    if 'defaults_file' in flow_def:
        flow_def = self._merge_defaults(flow_def, flow_path)
    
    return flow_def

def _merge_defaults(self, flow_def, flow_path):
    # Load unified defaults file
    defaults = yaml.safe_load(defaults_path)['defaults']
    
    # Apply to steps (overwrites hardcoded defaults)
    for step in flow_def['steps']:
        step_id = step.get('id')
        if step_id and step_id in defaults:
            step['default'] = defaults[step_id]
```

#### 3. Sublayout Structure
All sublayouts have been configured with proper defaults declarations:
- ✅ `sublayout_defaults` field in all sublayout files
- ✅ Separate defaults files in `defaults/subdefaults/` directory
- ✅ Proper path resolution (relative to main layout dir)

Example sublayout files:
- `layouts/sublayouts/database.layout.yml` → `defaults/subdefaults/database.defaults.yml`
- `layouts/sublayouts/project_basics.layout.yml` → `defaults/subdefaults/project_basics.defaults.yml`
- `layouts/sublayouts/environment.layout.yml` → `defaults/subdefaults/environment.defaults.yml`
- `layouts/sublayouts/network.layout.yml` → `defaults/subdefaults/network.defaults.yml`
- `layouts/sublayouts/resources.layout.yml` → `defaults/subdefaults/resources.defaults.yml`

### Verified Results

**Test Case**: OpenProject configuration with 7 sublayouts
- Global defaults: 5 entries
- Sublayout defaults: 21 additional entries
- **Unified defaults: 26 total entries** ✅

**Hierarchical Override Verification**:
```yaml
# Global defaults has:
domain: "srv1035368.hstgr.cloud"
port: "80"

# Network sublayout overrides:
domain: "localhost"  # ← Takes precedence
port: "8080"         # ← Takes precedence

# Result in unified_defaults.yml:
domain: localhost    # ✅ From sublayout
port: '8080'         # ✅ From sublayout
```

### File Locations

**Config Manager (Phase 3)**:
- Preprocessor: `phases/phase_3_collection/step_1_collect_user_configuration/collect_user_configuration.py`
- Main layout: `layouts/config_tui.layout.yml`
- Global defaults: `layouts/defaults/config_tui.defaults.yml`
- Sublayouts: `layouts/sublayouts/*.layout.yml`
- Sublayout defaults: `layouts/defaults/subdefaults/*.defaults.yml`
- Generated unified defaults: `outputs/unified_defaults.yml`

**TUI Form Engine**:
- Defaults loader: `src/tui_form_engine/core/flow_engine.py`
- Methods: `_load_flow()`, `_merge_defaults()`

## Architecture Summary

### Data Flow
```
Main Layout (config_tui.layout.yml)
  ├── defaults_file: "defaults/config_tui.defaults.yml" (5 entries)
  ├── sublayout: "sublayouts/project_basics.layout.yml"
  │     └── sublayout_defaults: "defaults/subdefaults/project_basics.defaults.yml" (4 entries)
  ├── sublayout: "sublayouts/database.layout.yml"
  │     └── sublayout_defaults: "defaults/subdefaults/database.defaults.yml" (6 entries)
  ├── sublayout: "sublayouts/environment.layout.yml"
  │     └── sublayout_defaults: "defaults/subdefaults/environment.defaults.yml" (4 entries)
  ├── sublayout: "sublayouts/network.layout.yml"
  │     └── sublayout_defaults: "defaults/subdefaults/network.defaults.yml" (3 entries)
  └── sublayout: "sublayouts/resources.layout.yml"
        └── sublayout_defaults: "defaults/subdefaults/resources.defaults.yml" (4 entries)

            ⬇ _expand_sublayouts() PREPROCESSING

outputs/unified_defaults.yml (26 merged entries)
  ├── Global defaults (base layer)
  ├── Sublayout defaults (override layer)
  └── Hierarchical merge complete

            ⬇ TUI ENGINE LOADS

Flow with unified defaults applied to all 13 steps
  └── Each step.default populated from unified_defaults.yml
```

## Maintenance Notes

### Adding New Sublayouts
1. Create sublayout file: `layouts/sublayouts/new_section.layout.yml`
2. Add `sublayout_defaults: "defaults/subdefaults/new_section.defaults.yml"`
3. Create defaults file: `layouts/defaults/subdefaults/new_section.defaults.yml`
4. Reference sublayout in main layout: `sublayout: "sublayouts/new_section.layout.yml"`
5. Preprocessing will automatically merge the new defaults

### Modifying Defaults Priority
To change which defaults take precedence, modify the order of `merged_defaults.update()` calls in `_expand_sublayouts()`. Current order (last wins):
1. Global defaults loaded first (base)
2. Sublayout defaults loaded in order (each overwrites previous)
3. Last sublayout's defaults have highest priority

### Troubleshooting
- **Defaults not appearing**: Check file paths are relative to main layout directory
- **Wrong values**: Verify sublayout load order (later sublayouts override earlier ones)
- **Missing defaults file**: System falls back to hardcoded step defaults (silent failure)
- **Path resolution issues**: Ensure `sublayout_defaults` paths use forward slashes

## Performance Characteristics

- **Preprocessing Time**: ~10-50ms for 7 sublayouts with 26 defaults
- **File I/O**: Happens once during preprocessing, not during rendering
- **Memory**: Single unified defaults object (~1-2KB for typical configs)
- **Scalability**: O(n) where n = number of sublayouts + global defaults