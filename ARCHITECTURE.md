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

## ⚠️ Architectural Limitations & Workflow Concerns

### 🎯 Form-Centric vs Workflow-Centric Design

**Current Design Philosophy**: 
- TUI Form Designer follows a **"collect-and-output"** model
- Single form → User input collection → Configuration file output → Handoff to next system
- Works excellently for **linear data collection** workflows

**Identified Limitations**:
- **Limited Branching Logic**: Conditionals only skip fields, don't support complex workflow routing
- **No Early Exit Patterns**: Forms expect to run to completion, making "status check" or "info display" flows cumbersome  
- **Single Output Assumption**: Assumes all interactions result in configuration file generation
- **No Loopback Support**: No native support for returning to previous steps or main menus

### 🔍 Real-World Use Case Analysis

**Example: WSL & Docker Manager Status Check Flow**
```
Expected: Menu → "Check Status" → Display Info → Return to Menu
Current:  Menu → "Check Status" → Full Configuration Questions → Save Config
```

**Workaround Required**:
- Split into multiple separate forms (`main_menu.yml`, `status_check.yml`, `full_config.yml`)
- Manual routing logic in Python application layer
- Custom handling for different workflow paths

### 🏗️ Recommended Separation of Concerns

#### **Current Architecture**:
```
TUI Form Designer: UI Definition + Data Collection + Basic Flow Control
Application Layer: Business Logic + File Operations
```

#### **Recommended Architecture**:
```
TUI Form Designer: Pure UI Definition + Field Rendering + Validation
Workflow Engine:   Flow Control + Routing + State Management + Branching Logic  
Application Layer: Business Logic + Data Processing + System Integration
```

### 🎯 Design Recommendations

#### **For TUI Form Designer Evolution**:
1. **Focus on UI Excellence**: Keep forms as pure UI definition tools
2. **Enhanced Conditional Logic**: Support for complex field conditionals within forms
3. **Workflow Integration Points**: Standard hooks for external workflow engines
4. **Multiple Output Modes**: Support info-only, partial completion, and full configuration modes

#### **For Applications Using TUI Forms**:
1. **Workflow-First Design**: Design workflow logic separately from UI forms
2. **Form Composition**: Use multiple simple forms rather than complex conditional forms
3. **External Routing**: Handle branching logic in application layer, not form layer
4. **Clear Separation**: Keep UI concerns separate from business logic concerns

### 📚 Implementation Patterns

#### **Pattern 1: Multi-Form Composition** (Current WSL Manager Approach)
```python
# Good for: Simple branching, different output types
menu_result = engine.execute_flow("main_menu")
if menu_result.choice == "status_check":
    status_result = engine.execute_flow("status_check") 
    # Handle status display
else:
    config_result = engine.execute_flow("full_configuration")
    # Handle configuration saving
```

#### **Pattern 2: Workflow Engine Integration** (Recommended for Complex Flows)
```python
# Good for: Complex workflows, multiple decision points, state management
workflow = WorkflowEngine(forms={"menu": "main_menu.yml", "config": "full_config.yml"})
workflow.define_flow({
    "start": "menu",
    "menu": {"status": "display_status", "configure": "config"},
    "config": {"success": "save_and_exit", "cancel": "menu"}
})
result = workflow.execute()
```

### 🎖️ Lessons Learned

- **TUI Form Designer excels** at consistent UI and data collection
- **Complex workflow logic should live outside** the form system  
- **Separation of concerns** improves maintainability and reusability
- **Form composition** is preferable to complex conditional forms
- **Application-layer routing** provides more flexibility than form-layer conditionals

*Documented based on real-world implementation experience with WSL & Docker Desktop Manager project (October 2025)*

## 🌊 Workflow Architecture Analysis & Future Direction

### 📋 Current Workflow Limitations Discovered

During implementation of complex user workflows, several critical limitations emerged that point toward the need for a **dedicated workflow layer**:

#### **1. Navigation & State Management**
```yaml
# Current Challenge: No native back navigation
Current TUI Form: Linear progression only, restart required for corrections
Implemented Workaround: Application-layer navigation stack with "← Go back" menu choices
Ideal Solution: Native workflow state management with bidirectional navigation
```

#### **2. Decision Trees & Branching Logic**  
```yaml
# Current Challenge: Limited conditional logic
Current TUI Form: Basic field conditionals only (show/hide fields)
Real-World Need: Complex branching workflows based on system state
Implemented Workaround: Multiple separate forms + Python routing logic
Ideal Solution: Workflow definition language with decision nodes
```

#### **3. Context-Aware Flows**
```yaml
# Current Challenge: Static form definitions
Current TUI Form: Fixed choices and flow paths
Real-World Need: Dynamic options based on runtime detection
Implemented Workaround: Python-generated temporary YAML files
Ideal Solution: Dynamic workflow adaptation based on context
```

### 🎯 Proposed Workflow Definition Language

#### **Enhanced Workflow Schema Concept**
```yaml
workflow_id: "smart_installer_workflow"
version: "2.0"
entry_point: "detect_system_state"

# Workflow-level configuration
workflow_config:
  navigation:
    back_enabled: true
    breadcrumbs: true
    cancel_points: ["main_menu", "confirmation"]
  
  context_providers:
    - name: "system_detection"
      module: "system_detection.py"
      function: "detect_system_state"

# Decision nodes for complex branching
decision_nodes:
  system_state_branch:
    condition: "context.system_state.overall_state"
    branches:
      "clean_system": "fresh_install_flow"
      "both_installed": "reinstall_or_exit_flow"
      "partial_install": "partial_repair_flow"
    default: "fallback_flow"

# Reusable flow definitions
flows:
  detect_system_state:
    type: "context_provider"
    provider: "system_detection"
    next: "system_state_branch"
    
  main_menu:
    type: "form"
    layout: "main_menu.yml"
    navigation:
      back: false  # Entry point, no back
      cancel: "exit_workflow"
    routes:
      "Configure": "detect_system_state"
      "Status Check": "status_check_flow"
      "Exit": "exit_workflow"
      
  fresh_install_flow:
    type: "form" 
    layout: "fresh_install_config.yml"
    navigation:
      back: "main_menu"
      cancel: "main_menu"
    context_injection:
      - field: "recommended_memory"
        value: "context.system_info.recommended_memory"
    
  status_check_flow:
    type: "sequence"
    steps:
      - type: "info_display"
        provider: "system_detection" 
        template: "status_report.txt"
      - type: "confirmation"
        message: "Return to main menu?"
        default: true
    navigation:
      back: "main_menu"
    routes:
      "Yes": "main_menu"
      "No": "exit_workflow"

# State persistence and recovery
state_management:
  persistence: true
  recovery_points: ["main_menu", "configuration_complete"]
  session_timeout: "30m"
```

### 🏗️ Proposed Architecture Evolution

#### **Phase 1: Enhanced Form Engine** (Backward Compatible)
```python
# Enhanced TUI Form Engine with workflow hooks
class EnhancedFlowEngine:
    def __init__(self, workflow_definition: str):
        self.workflow = WorkflowDefinition.load(workflow_definition)
        self.navigation_stack = NavigationStack()
        self.context_providers = ContextProviderRegistry()
        
    def execute_workflow(self) -> WorkflowResult:
        current_node = self.workflow.entry_point
        
        while current_node:
            node = self.workflow.get_node(current_node)
            
            if node.type == "form":
                result = self._execute_form_with_navigation(node)
            elif node.type == "decision":
                result = self._execute_decision_node(node)
            elif node.type == "context_provider":
                result = self._execute_context_provider(node)
                
            current_node = self._determine_next_node(node, result)
            
        return self.generate_result()
```

#### **Phase 2: Native Workflow Features**
- **Built-in Navigation**: Native back/forward buttons and breadcrumbs
- **Decision Trees**: Visual workflow designer with branching logic
- **Context Injection**: Runtime data injection into forms
- **State Management**: Automatic session persistence and recovery
- **Flow Validation**: Pre-execution workflow validation and testing

#### **Phase 3: Advanced Workflow Capabilities**  
- **Parallel Flows**: Multi-threaded workflow execution
- **Conditional Resumption**: Smart restart from interruption points
- **Workflow Templates**: Reusable workflow patterns and libraries
- **Integration Hooks**: Native API integrations and external system calls

### 🎨 Design Principles for Workflow Layer

#### **1. Separation of Concerns**
```
Workflow Definition (YAML) ← Pure workflow logic, no UI details
Form Definition (YAML)     ← Pure UI definition, no workflow logic  
Application Logic (Python) ← Business logic, system integration
```

#### **2. Progressive Enhancement**
- **Level 1**: Basic forms work as before (backward compatibility)
- **Level 2**: Enhanced forms with workflow features (opt-in)
- **Level 3**: Full workflow orchestration (advanced use cases)

#### **3. Context-Aware Design**
- **Dynamic Choices**: Form choices populated from context providers
- **Conditional Flows**: Workflow paths determined by runtime conditions
- **State Preservation**: User progress maintained across sessions

### 🚀 Implementation Roadmap

#### **Immediate (Next Release)**
1. **NavigationController Integration**: Make navigation controller a first-class feature
2. **Enhanced Conditional Logic**: Improve field-level conditionals
3. **Context Provider API**: Standard interface for runtime data injection

#### **Short Term (6 months)**
1. **Workflow Definition Schema**: Formal YAML schema for workflows
2. **Decision Node Support**: Native branching logic in workflow engine
3. **State Management API**: Session persistence and recovery

#### **Long Term (12+ months)**  
1. **Visual Workflow Designer**: GUI tool for creating complex workflows
2. **Workflow Testing Framework**: Automated testing for workflow logic
3. **Enterprise Integration**: API connectors and advanced orchestration

### 💡 Migration Strategy

#### **For Existing Applications**
```python
# Current approach (still supported)
results = engine.execute_flow("simple_form")

# Enhanced approach (new capability)
workflow_engine = WorkflowEngine("complex_workflow.yml")
results = workflow_engine.execute()

# Migration path: Gradual adoption
simple_forms = engine  # Keep simple forms as-is
complex_flows = WorkflowEngine(...)  # Use workflow engine for complex cases
```

#### **For TUI Form Designer Core**
1. **Maintain API Compatibility**: Existing `FlowEngine` continues to work
2. **Add Workflow Layer**: New `WorkflowEngine` for advanced use cases  
3. **Gradual Feature Integration**: Merge workflow features into core over time

### 🎖️ Key Insights from Real-World Implementation

#### **What We Learned**:
- **Form-first design breaks down** with complex user journeys
- **Navigation is essential** for user confidence and error correction
- **Context-awareness is critical** for intelligent user experiences  
- **Workflow logic complexity grows exponentially** without proper architecture
- **Separation of concerns is vital** for maintainability and testing

#### **What We Recommend**:
- **Invest in workflow architecture** as a first-class concern
- **Design for navigation and state management** from the beginning
- **Create clear boundaries** between UI, workflow, and business logic
- **Plan for context injection and dynamic adaptation**
- **Build testing and validation tools** alongside the workflow engine

*Enhanced workflow analysis based on WSL & Docker Desktop Manager and VPS Environment implementation experience (October 2025)*

---

## 📖 Related Documentation

- **[Workflow Architecture Design](docs/WORKFLOW_ARCHITECTURE_DESIGN.md)** - Comprehensive design document for workflow engine evolution
- **[Implementation Examples](examples/workflow_patterns/)** - Real-world workflow implementation patterns  
- **[Migration Guide](docs/WORKFLOW_MIGRATION.md)** - Step-by-step guide for adopting workflow features

## 🤝 Contributing to Workflow Development

The workflow architecture represents a significant evolution of TUI Form Designer. We welcome contributions in the following areas:

### **🔬 Research & Design**
- Workflow pattern analysis and documentation
- User experience research for complex flows
- Performance benchmarking and optimization strategies

### **⚙️ Implementation** 
- Core workflow engine development
- Navigation controller enhancement
- Context provider framework

### **📚 Documentation & Examples**
- Workflow design patterns and templates
- Migration guides and tutorials 
- Testing framework development

### **🧪 Testing & Validation**
- Real-world workflow testing
- Backward compatibility validation
- Performance and scalability testing

**Get Involved**: Join the [Workflow Architecture Working Group](https://github.com/TUI_Form_Designer/discussions/workflow-architecture) to contribute to the future of TUI workflows.