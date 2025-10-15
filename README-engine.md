# TUI Form Engine

**Lightweight runtime engine for executing YAML-defined interactive flows.**

This is the production runtime component of TUI Form Designer. It provides the core engine for executing flows without the development/editing tools.

## 🎯 Perfect For Production

- ✅ **Minimal Dependencies** - Only questionary, pyyaml, and pydantic
- ✅ **Lightweight** - No development tools or editors included
- ✅ **Fast Startup** - Quick initialization for production environments
- ✅ **Stable API** - Production-ready interface

## 📦 Installation

```bash
pip install tui-form-engine
```

## 🚀 Quick Start

```python
from tui_form_engine import FlowEngine

# Initialize engine
engine = FlowEngine(flows_dir="flows")

# Execute a flow
result = engine.execute_flow("user_registration")
print(f"User: {result['name']}, Email: {result['email']}")
```

## 🔧 Core Components

### FlowEngine
The main engine for loading and executing YAML flow definitions.

```python
from tui_form_engine import FlowEngine

engine = FlowEngine(
    flows_dir="flows",        # Directory containing YAML flows
    theme="default"           # UI theme: default, dark, minimal
)

# Execute with user interaction
result = engine.execute_flow("my_flow")

# Execute with mock responses (testing)
mock_responses = {"name": "John", "email": "john@example.com"}
result = engine.execute_flow("my_flow", mock_responses=mock_responses)
```

### QuestionaryUI
Enhanced UI components with themes and styling.

```python
from tui_form_engine import QuestionaryUI

ui = QuestionaryUI(theme="dark")
name = ui.prompt("Enter your name:")
confirmed = ui.confirm("Continue?")
choice = ui.select("Choose option:", ["A", "B", "C"])
```

## 📋 Flow Definition Format

Create YAML files defining your interactive flows:

```yaml
layout_id: user_registration
title: User Registration
description: Collect user information
steps:
  - id: name
    type: text
    message: "Enter your name:"
    validate: required
    
  - id: email
    type: text
    message: "Enter your email:"
    validate: email
    
  - id: subscribe
    type: confirm
    message: "Subscribe to newsletter?"
    default: true

output_mapping:
  user:
    name: name
    email: email
    newsletter: subscribe
```

## 🎨 Themes

Choose from built-in themes:
- **default** - Clean, professional look
- **dark** - Dark mode with bright accents  
- **minimal** - Simplified, minimalist style

## 🔒 Production Ready

- ✅ **Exception Handling** - Comprehensive error management
- ✅ **Validation** - Built-in input validation
- ✅ **Conditional Logic** - Dynamic flow control
- ✅ **Output Mapping** - Structured result formatting
- ✅ **Mock Testing** - Support for automated testing

## 📚 Related Packages

- **[tui-form-editor](https://github.com/JustinCBates/TUI_Form_Designer)** - Development tools for creating flows

## 📄 License

MIT License - see LICENSE file for details.