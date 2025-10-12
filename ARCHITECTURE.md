# TUI Form Designer - Architecture Separation

## 📋 Overview

The TUI Form Designer has been restructured into a **dual package architecture** to support both production and development use cases efficiently.

## 🏗️ New Structure

```
tui-form-designer/
├── src/
│   ├── tui_form_engine/      # 🔧 Production Runtime
│   │   ├── core/             # Core engine components
│   │   ├── ui/               # UI components
│   │   └── __init__.py       # Engine API
│   └── tui_form_editor/      # 🎨 Development Tools
│       ├── tools/            # Designer, validator, tester, etc.
│       └── __init__.py       # Editor API
├── pyproject-engine.toml     # Engine package config
├── pyproject-editor.toml     # Editor package config
├── README-engine.md          # Engine documentation
├── README-editor.md          # Editor documentation
└── build.sh                  # Dual build script
```

## 📦 Package Separation

### 🔧 TUI Form Engine (Production)
**Purpose**: Lightweight runtime for executing flows in production environments

**Components**:
- `FlowEngine` - Core YAML flow execution
- `QuestionaryUI` - Basic UI components  
- `Exceptions` - Error handling
- **Dependencies**: questionary, pyyaml, pydantic (minimal)

**Use Cases**:
- Production applications
- Docker containers
- CI/CD environments
- Embedded systems

### 🎨 TUI Form Editor (Development)
**Purpose**: Complete development toolkit for creating and managing flows

**Components**:
- `InteractiveFlowDesigner` - Visual flow creation
- `FlowValidator` - Flow definition validation
- `FlowTester` - Testing with mock responses
- `FlowPreviewer` - Flow structure preview
- CLI tools (tui-designer, tui-validate, etc.)
- **Dependencies**: tui-form-engine + development tools

**Use Cases**:
- Flow development
- Testing and validation
- CI/CD pipeline validation
- Development environments

## 🔄 Import Changes

### Before (Monolithic)
```python
from tui_form_designer import FlowEngine, QuestionaryUI
from tui_form_designer.tools import FlowValidator
```

### After (Separated)

**Production Code**:
```python
# Lightweight engine only
from tui_form_engine import FlowEngine, QuestionaryUI
```

**Development Code**:
```python
# Full development toolkit (includes engine)
from tui_form_editor import (
    FlowEngine, QuestionaryUI,           # Engine components
    InteractiveFlowDesigner, FlowValidator # Editor tools
)
```

## 🚀 Installation Options

### Production Deployment
```bash
pip install tui-form-engine
```
- **Size**: ~50KB (minimal)
- **Dependencies**: 3 packages
- **Use**: Runtime execution only

### Development Environment  
```bash
pip install tui-form-editor
```
- **Size**: ~200KB (complete)
- **Dependencies**: 10+ packages
- **Use**: Full development toolkit

## 📋 Benefits

### For Production
- ✅ **Minimal footprint** - smaller containers
- ✅ **Fewer dependencies** - reduced security surface
- ✅ **Faster startup** - quicker initialization
- ✅ **Stable API** - production-focused interface

### For Development
- ✅ **Complete toolset** - all development features
- ✅ **Backward compatibility** - includes engine
- ✅ **Rich CLI** - comprehensive command interface
- ✅ **Testing framework** - mock testing capabilities

## 🔧 Build Process

Use the provided build script to create both packages:

```bash
./build.sh
```

Outputs:
- `dist/engine/` - Production engine package
- `dist/editor/` - Development editor package

## 📚 Migration Guide

### Existing Code (Engine Only)
No changes needed - engine code remains the same:
```python
from tui_form_designer import FlowEngine  # Still works
```
↓ Becomes:
```python
from tui_form_engine import FlowEngine   # New import
```

### Development Tools
```python
from tui_form_designer.tools import FlowValidator  # Old
```
↓ Becomes:
```python
from tui_form_editor import FlowValidator           # New
```

## 🎯 Deployment Strategy

1. **Development Phase**: Use `tui-form-editor` for creating flows
2. **Production Phase**: Switch to `tui-form-engine` for deployment
3. **CI/CD**: Use `tui-form-editor` for testing and validation

This architecture provides optimal flexibility for both development workflows and production deployments.