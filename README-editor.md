# TUI Form Editor

**Development tools for creating and managing YAML flow definitions.**

This package provides interactive tools for designing, testing, and validating flows. It builds on top of **tui-form-engine** to provide a complete development experience.

## 🎯 Perfect For Development

- ✅ **Interactive Flow Designer** - Visual flow creation
- ✅ **Comprehensive Validation** - Flow definition validation
- ✅ **Mock Testing Framework** - Test flows with simulated inputs
- ✅ **Flow Preview** - Preview flows before deployment
- ✅ **Command-Line Interface** - Complete CLI toolkit

## 📦 Installation

```bash
pip install tui-form-editor
```

This automatically installs `tui-form-engine` as a dependency.

## 🚀 Quick Start

### Command Line Interface

```bash
# Create new flows interactively
tui-designer

# Validate existing flows
tui-validate flows/

# Test flows with mock data
tui-test flows/user_registration.yml

# Preview flow structure
tui-preview flows/user_registration.yml

# Run demonstration
tui-demo
```

### Python API

```python
from tui_form_editor import InteractiveFlowDesigner, FlowValidator

# Create flows programmatically
designer = InteractiveFlowDesigner(flows_dir="flows")
flow = designer.create_new_flow()

# Validate flows
validator = FlowValidator(flows_dir="flows")
validation_result = validator.validate_all_flows()
```

## 🛠️ Development Tools

### Interactive Flow Designer
Create flows using an intuitive interface:

```python
from tui_form_editor import InteractiveFlowDesigner

designer = InteractiveFlowDesigner(flows_dir="flows")

# Interactive flow creation
flow = designer.create_new_flow()

# Add steps interactively  
step = designer.create_step()

# Create output mapping
mapping = designer.create_output_mapping(flow['steps'])
```

### Flow Validator
Comprehensive validation of flow definitions:

```python
from tui_form_editor import FlowValidator

validator = FlowValidator(flows_dir="flows")

# Validate single flow
errors = validator.validate_flow_file("user_registration.yml")

# Validate all flows
results = validator.validate_all_flows()

# Validate specific flows
results = validator.validate_specific_flows(["flow1.yml", "flow2.yml"])
```

### Flow Tester
Test flows with mock responses:

```python
from tui_form_editor import FlowTester

tester = FlowTester(flows_dir="flows")

# Test with mock file
result = tester.test_flow("user_registration", "mocks/user_registration.json")

# Test all flows
results = tester.test_all_flows("mocks/")

# Generate mock template
template = tester.generate_mock_template("user_registration")
```

### Flow Previewer
Preview and explore flow structures:

```python
from tui_form_editor import FlowPreviewer

previewer = FlowPreviewer(flows_dir="flows")

# Preview flow structure
previewer.preview_flow("user_registration")

# Preview specific step
previewer.preview_step("user_registration", "email_step")

# List all available flows
previewer.list_flows()
```

## 📋 CLI Commands

### `tui-designer`
Interactive flow designer interface:
- Create new flows step-by-step
- Edit existing flows
- Preview flows as you build them
- Save and validate automatically

### `tui-validate`
Validate flow definitions:
```bash
tui-validate flows/                    # Validate all flows
tui-validate flows/user_reg.yml        # Validate specific flow
tui-validate flows/ --strict           # Strict validation mode
```

### `tui-test`
Test flows with mock data:
```bash
tui-test flows/user_reg.yml                     # Test with auto-generated mocks
tui-test flows/user_reg.yml --mock mocks.json   # Test with specific mock file
tui-test flows/ --mock-dir mocks/               # Test all flows with mock directory
```

### `tui-preview`
Preview flow structures:
```bash
tui-preview flows/user_reg.yml           # Preview entire flow
tui-preview flows/user_reg.yml --step 2  # Preview specific step
tui-preview flows/ --list                # List all flows
```

### `tui-demo`
Run interactive demonstrations:
```bash
tui-demo                    # Run default demo
tui-demo --flow survey      # Run specific demo flow
tui-demo --create-examples  # Create example flows
```

## 🎨 Features

### Interactive Flow Creation
- Step-by-step flow building
- Real-time validation
- Preview as you build
- Template generation

### Comprehensive Testing
- Mock response generation
- Automated flow testing
- Validation testing
- Performance testing

### Advanced Validation
- Schema validation
- Logical consistency checks
- Reference validation
- Performance analysis

### Development Workflow
- Flow scaffolding
- Template management
- Batch operations
- Integration testing

## 📚 Related Packages

- **[tui-form-engine](https://github.com/JustinCBates/TUI_Form_Designer)** - Runtime engine for production

## 📄 License

MIT License - see LICENSE file for details.