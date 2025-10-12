# TUI Form Designer

**Create beautiful, interactive command-line forms and configuration wizards using YAML flow definitions.**

## 📦 **Dual Package Architecture**

TUI Form Designer is split into two packages for optimal deployment flexibility:

### 🔧 **TUI Form Engine** (Production Runtime)
- **Lightweight runtime** for executing flows in production
- **Minimal dependencies** - only questionary, pyyaml, pydantic
- **Fast startup** and **stable API**
- **Perfect for production environments**

```bash
pip install tui-form-engine
```

### 🎨 **TUI Form Editor** (Development Tools)  
- **Complete development toolkit** for creating and managing flows
- **Interactive designer**, **testing framework**, **validation tools**
- **CLI interface** with comprehensive commands
- **Perfect for development environments**

```bash
pip install tui-form-editor  # Includes tui-form-engine
```

## 🎯 **When to Use Which Package**

| Environment | Package | Use Case |
|-------------|---------|----------|
| **Production** | `tui-form-engine` | Running flows in deployed applications |
| **Development** | `tui-form-editor` | Creating, testing, and managing flows |
| **CI/CD** | `tui-form-editor` | Validation and testing in pipelines |
| **Docker** | `tui-form-engine` | Minimal container size for runtime |

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-tui--form--designer-orange.svg)](https://pypi.org/project/tui-form-designer/)

## ✨ Features

- **📋 YAML-Defined Forms**: Define interactive workflows in human-readable YAML
- **🎨 Interactive Designer**: Visual form creation using Questionary itself  
- **🔍 Comprehensive Validation**: Syntax and logic validation with detailed error reporting
- **🧪 Testing Framework**: Automated testing with mock responses
- **⚡ CLI Tools**: Complete command-line toolkit for form management
- **🎭 Theming Support**: Multiple built-in themes and custom styling
- **🔄 Conditional Logic**: Advanced branching and conditional questions
- **📊 Real-time Validation**: Input validation with immediate feedback
- **🗂️ Output Mapping**: Transform responses to structured data
- **🚀 Easy Integration**: Simple Python API for embedding in applications

## 🚀 Quick Start

### Installation

```bash
pip install tui-form-designer
```

### Basic Usage

```bash
# Interactive mode - explore all tools
tui-designer

# Create a new form interactively
tui-designer design

# Preview existing forms
tui-designer preview --list

# Validate form definitions
tui-designer validate

# Test forms with mock data
tui-designer test --interactive

# Run demo with examples
tui-designer demo
```

### Python API

```python
from tui_form_designer import FlowEngine

# Initialize the engine
engine = FlowEngine(flows_dir="my_flows")

# Execute a form
results = engine.execute_flow("user_registration")
print(f"User: {results['username']}")

# Execute with mock responses for testing
mock_data = {"username": "testuser", "email": "test@example.com"}
results = engine.execute_flow("user_registration", mock_responses=mock_data)
```

## 📖 Example Flow

Create beautiful forms with simple YAML:

```yaml
flow_id: "user_survey"
title: "User Satisfaction Survey"
description: "Quick survey to gather user feedback"
icon: "📋"

steps:
  - id: "user_name"
    type: "text"
    message: "What's your name?"
    validate: "required"
    
  - id: "satisfaction"
    type: "select"
    message: "How satisfied are you with our service?"
    choices:
      - "😍 Very Satisfied"
      - "😊 Satisfied"
      - "😐 Neutral"
      - "😞 Dissatisfied"
      - "😡 Very Dissatisfied"
    
  - id: "feedback"
    type: "text"
    message: "Any additional feedback?"
    instruction: "Your thoughts help us improve"
    
  - id: "recommend"
    type: "confirm"
    message: "Would you recommend us to others?"
    default: true

output_mapping:
  user:
    name: "user_name"
    satisfaction: "satisfaction"
    feedback: "feedback"
    would_recommend: "recommend"
```

This creates an interactive form that looks like:

```
📋 User Satisfaction Survey
   Quick survey to gather user feedback
────────────────────────────────────────

? What's your name? John Doe
? How satisfied are you with our service? 😊 Satisfied
? Any additional feedback? Great service, very helpful!
? Would you recommend us to others? Yes

✅ Flow execution completed!
```

## 🎯 Use Cases

Perfect for:

- **🔧 Application Configuration**: Interactive setup wizards for complex applications
- **🚀 Deployment Workflows**: Guided deployment configuration and environment setup
- **👤 User Onboarding**: Step-by-step user registration and profile creation
- **📋 Surveys & Forms**: Dynamic questionnaires with conditional logic
- **🛠️ Development Tools**: Interactive code generators and project scaffolding
- **⚙️ System Administration**: Server configuration and maintenance workflows
- **📊 Data Collection**: Research surveys and feedback collection

## 🛠️ Available Tools

### 🎨 Design Tool
Create and edit forms interactively:
```bash
tui-designer design
```

### 🔍 Validation Tool
Validate form syntax and logic:
```bash
tui-designer validate                # Validate all flows
tui-designer validate my_form.yml   # Validate specific form
```

### 🧪 Testing Tool
Test forms with mock responses:
```bash
tui-designer test --flow user_survey
tui-designer test --flow user_survey --mock-data test_responses.json
```

### 👁️ Preview Tool
Preview form structure without execution:
```bash
tui-designer preview --list          # List all forms
tui-designer preview --flow my_form  # Preview specific form
```

## 📝 Step Types

### Text Input
```yaml
- id: "username"
  type: "text"
  message: "Enter username:"
  validate: "required"
  default: "user123"
  instruction: "Must be unique"
```

### Single Selection
```yaml
- id: "theme"
  type: "select"
  message: "Choose a theme:"
  choices:
    - "Light"
    - "Dark"
    - "Auto"
  default: "Auto"
```

### Confirmation
```yaml
- id: "agree_terms"
  type: "confirm"
  message: "Agree to terms?"
  default: false
  instruction: "Required to proceed"
```

### Password Input
```yaml
- id: "password"
  type: "password"
  message: "Enter password:"
  validate: "password_length"
  instruction: "At least 8 characters"
```

## 🔧 Advanced Features

### Conditional Logic
Show/hide steps based on previous answers:

```yaml
- id: "enable_email"
  type: "confirm"
  message: "Enable email notifications?"
  
- id: "smtp_host"
  type: "text"
  message: "SMTP host:"
  condition: "enable_email == true"  # Only show if email enabled
```

### Input Validation
Built-in validators for common patterns:

```yaml
- id: "email"
  type: "text"
  message: "Email address:"
  validate: "email"           # Built-in email validation
  
- id: "port"
  type: "text" 
  message: "Port number:"
  validate: "integer"         # Must be a valid integer
```

Available validators: `required`, `email`, `domain`, `integer`, `password_length`

### Output Mapping
Transform flat responses to structured data:

```yaml
steps:
  - id: "db_host"
    type: "text"
    message: "Database host:"
    
  - id: "db_port" 
    type: "text"
    message: "Database port:"

output_mapping:
  database:
    host: "db_host"      # Nested structure
    port: "db_port"
  # Results in: {"database": {"host": "localhost", "port": "5432"}}
```

### Custom Themes
Choose from built-in themes or create custom styling:

```python
from tui_form_designer import FlowEngine
from questionary import Style

# Built-in themes
engine = FlowEngine(theme="dark")     # dark, minimal, default

# Custom styling
custom_style = Style([
    ('question', 'bold cyan'),
    ('answer', 'bold green'),
    ('pointer', 'bold magenta')
])
engine = FlowEngine(style=custom_style)
```

## 📂 Project Structure

```
flows/
├── basic/              # Simple example flows
│   ├── simple_survey.yml
│   └── user_registration.yml
├── advanced/           # Complex multi-step flows  
│   ├── application_setup.yml
│   └── docker_deployment.yml
└── templates/          # Reusable flow templates
    └── openproject_main_config.yml
```

## 🧪 Testing Flows

### Interactive Testing
```bash
tui-designer test --interactive
```

### Mock Response Testing
Create a JSON file with test responses:

```json
{
  "username": "testuser",
  "email": "test@example.com", 
  "account_type": "Premium",
  "agree_terms": true
}
```

Then test with mocked responses:
```bash
tui-designer test --flow registration --mock-data test_responses.json
```

### Generate Mock Templates
Automatically generate mock response templates:
```bash
# This creates registration_mock_template.json
tui-designer test
# Select "Generate mock template" option
```

## 🐍 Python Integration

### Basic Integration
```python
from tui_form_designer import FlowEngine

def setup_application():
    engine = FlowEngine(flows_dir="config_flows")
    config = engine.execute_flow("app_setup")
    
    # Use the configuration
    database_url = config['database']['url']
    debug_mode = config['application']['debug']
    return config
```

### Custom Validation
```python
import questionary
from tui_form_designer import FlowEngine

def custom_validator(value):
    if len(value) < 3:
        raise questionary.ValidationError("Too short!")
    return True

engine = FlowEngine()
engine.validators['custom'] = custom_validator
```

### Error Handling
```python
from tui_form_designer import FlowEngine, FlowValidationError, FlowExecutionError

try:
    engine = FlowEngine()
    results = engine.execute_flow("my_flow")
except FlowValidationError as e:
    print(f"Flow validation failed: {e}")
except FlowExecutionError as e:
    print(f"Flow execution failed: {e}")
```

## 🎨 Styling & Themes

### Built-in Themes

**Default Theme** (Blue/Orange):
```python
engine = FlowEngine(theme="default")
```

**Dark Theme** (Cyan/Green):
```python
engine = FlowEngine(theme="dark")  
```

**Minimal Theme** (No colors):
```python
engine = FlowEngine(theme="minimal")
```

### Custom Styling
```python
from questionary import Style

custom_style = Style([
    ('question', 'bold blue'),
    ('answer', 'fg:#ff9d00 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#cc5454'),
    ('instruction', 'italic'),
])

engine = FlowEngine(style=custom_style)
```

## 🚀 Examples

The package includes several example flows:

- **`simple_survey`**: Basic user satisfaction survey
- **`user_registration`**: Complete user account creation
- **`application_setup`**: Complex app configuration with database, email, etc.
- **`docker_deployment`**: Docker container configuration
- **`openproject_main_config`**: Full OpenProject deployment setup

Try them out:
```bash
tui-designer demo
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup
```bash
git clone https://github.com/JustinCBates/TUI_Form_Designer.git
cd TUI_Form_Designer
pip install -e .[dev]
```

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black src/ tests/
isort src/ tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on the excellent [Questionary](https://github.com/tmbo/questionary) library
- Originally developed as part of the [OpenProject](https://github.com/opf/openproject) configuration management system
- Inspired by the need for better terminal user interfaces in DevOps and system administration tools

## 📊 Project Stats

- **Language**: Python 3.8+
- **Dependencies**: Questionary, PyYAML, Pydantic
- **Size**: Lightweight (~50KB)
- **Type**: CLI Tool + Python Library
- **Status**: Production Ready

---

Made with ❤️ for the terminal UI community