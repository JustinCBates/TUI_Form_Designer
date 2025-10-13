# Virtual Layout Reconstruction Design

## Core Concept
Preprocessing engine that merges main layout + sublayouts into a single virtual layout structure. The TUI Form Engine receives a unified layout after sublayout resolution and step merging.

## Architecture

### Virtual Layout Pipeline
```
Main Layout (config_tui_modular.layout.yml)
├── inline steps (welcome, confirm_config)
├── subid: project_basics → sublayouts/project_basics.layout.yml
├── subid: database_config → sublayouts/database.layout.yml
└── subid: network_setup → sublayouts/network.layout.yml

                    ⬇ PREPROCESSING ENGINE

Virtual Layout Object
├── Merged steps from main + all sublayouts
├── Resolved subid references
├── Maintained step ordering
└── Single unified layout for execution
```

### Preprocessing Steps
1. **Parse main layout** - Load title, description, metadata
2. **Discover sublayout references** - Find all subid/sublayout pairs
3. **Load sublayout files** - Parse individual sublayout YAML files
4. **Merge step arrays** - Combine inline steps + sublayout steps
5. **Resolve ordering** - Maintain proper step sequence
6. **Create virtual layout** - Single unified layout object

## Virtual Layout Structure

### Input: Modular Layout
```yaml
# config_tui_modular.layout.yml
title: "OpenProject Configuration"
steps:
  - id: welcome
    type: info
    message: "Welcome..."
    
  - subid: project_basics
    sublayout: "./sublayouts/project_basics.layout.yml"
    
  - subid: database_config
    sublayout: "./sublayouts/database.layout.yml"
    
  - id: confirm_config
    type: confirm
    message: "Proceed?"
```

### Output: Virtual Layout
```yaml
# Generated virtual layout
title: "OpenProject Configuration"
version: "1.0.0"
steps:
  # Inline step from main layout
  - id: welcome
    type: info
    message: "Welcome..."
    
  # Steps from project_basics sublayout
  - id: project_name
    type: text
    message: "Project name:"
    default: "openproject"
    
  - id: admin_email
    type: text
    message: "Administrator email:"
    
  - id: admin_password
    type: password
    message: "Administrator password:"
    
  # Steps from database sublayout  
  - id: postgres_db
    type: text
    message: "PostgreSQL database name:"
    default: "openproject_db"
    
  - id: postgres_user
    type: text
    message: "PostgreSQL username:"
    
  # Inline step from main layout
  - id: confirm_config
    type: confirm
    message: "Proceed?"
```

## Implementation

### LayoutPreprocessor Class
```python
class LayoutPreprocessor:
    def reconstruct_virtual_layout(self, main_layout_path):
        """
        Merge main layout + sublayouts into virtual layout
        """
        # 1. Load main layout YAML
        main_layout = self.load_yaml(main_layout_path)
        
        # 2. Initialize virtual layout with main metadata
        virtual_layout = {
            'title': main_layout.get('title'),
            'description': main_layout.get('description'),
            'version': main_layout.get('version'),
            'steps': []
        }
        
        # 3. Process each step/subid in order
        for step in main_layout['steps']:
            if 'subid' in step:
                # Load and merge sublayout
                sublayout_steps = self.load_sublayout(step['sublayout'])
                virtual_layout['steps'].extend(sublayout_steps)
            else:
                # Add inline step
                virtual_layout['steps'].append(step)
                
        return virtual_layout
        
    def load_sublayout(self, sublayout_path):
        """Load sublayout and return its steps array"""
        sublayout = self.load_yaml(sublayout_path)
        return sublayout.get('steps', [])
```

### Sublayout Resolution Rules
1. **Step ID Uniqueness** - Each step must have unique ID across all sublayouts
2. **Order Preservation** - Steps appear in order: main step, sublayout steps, next main step
3. **Metadata Inheritance** - Main layout metadata (title, description) preserved
4. **Error Handling** - Missing sublayout files cause preprocessing failure

## Benefits

### Simplified Execution
- TUI Form Engine receives familiar single-layout structure
- No runtime sublayout resolution needed
- Standard step processing logic

### Development Efficiency
- Modular sublayout development and testing
- Clean separation of configuration sections
- Reusable sublayout components

### Debugging
- Virtual layout can be inspected/saved for debugging
- Clear visibility into final merged structure
- Step ordering validation

## Integration Points

### With Defaults System
```python
def process_layout_with_defaults(main_layout_path):
    # 1. Virtual layout reconstruction
    virtual_layout = LayoutPreprocessor().reconstruct_virtual_layout(main_layout_path)
    
    # 2. Virtual defaults reconstruction  
    virtual_defaults = DefaultsPreprocessor().merge_defaults(main_layout_path)
    
    # 3. Apply defaults to virtual layout
    final_layout = apply_defaults(virtual_layout, virtual_defaults)
    
    return final_layout
```

### With TUI Form Engine
```python
# Current usage (unchanged)
flow_engine = FlowEngine(flows_dir=layouts_dir)
result = flow_engine.run_flow(flow_name)

# Internal change: FlowEngine uses virtual layout
class FlowEngine:
    def load_flow(self, flow_name):
        layout_path = f"{self.flows_dir}/{flow_name}.layout.yml"
        
        # NEW: Preprocessing step
        virtual_layout = LayoutPreprocessor().reconstruct_virtual_layout(layout_path)
        
        return virtual_layout
```

## Error Handling

### Missing Sublayouts
- File not found errors with clear sublayout path
- Validation of sublayout file structure
- Graceful fallback or hard failure options

### Circular References
- Detection of sublayout → sublayout references
- Prevention of infinite recursion
- Clear error messages

### Step ID Conflicts
- Validation of unique step IDs across all sublayouts
- Conflict resolution strategies
- Development-time warnings

## Next Steps
1. Implement LayoutPreprocessor class
2. Update FlowEngine to use virtual layout reconstruction
3. Test with existing config_tui_modular.layout.yml
4. Integrate with virtual defaults system