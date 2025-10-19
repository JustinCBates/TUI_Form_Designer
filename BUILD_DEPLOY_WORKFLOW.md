# TUI Form Designer - Multi-Repository Build & Deploy Workflow

**Date:** October 16, 2025  
**Purpose:** Establish workflow for distributing TUI packages to consumer projects  
**Version:** 1.0

---

## 🎯 **Workflow Overview**

This document establishes the development and distribution workflow for TUI Form Designer packages across multiple repositories:

- **Source Repository:** `TUI_Form_Designer` (where TUI is developed)
- **Consumer Repositories:** `wsl-and-docker-desktop-manager`, `devcontainer_server_docker`

## 🏗️ **Build System Architecture**

### **TUI Form Designer (Source)**
```
TUI_Form_Designer/
├── src/                    # Source code
├── tui_layouts/           # Demo layouts (fixed)
├── build.sh              # Build script
├── pyproject.toml         # Main package config
├── pyproject-engine.toml  # Production runtime
├── pyproject-editor.toml  # Development tools
├── dist/                  # Built packages
│   ├── engine/           # Production packages
│   └── editor/           # Development packages
└── releases/             # Version releases (NEW)
    └── v1.0.1/
        ├── tui-form-engine-1.0.1.tar.gz
        ├── tui-form-editor-1.0.1.tar.gz
        └── RELEASE_NOTES.md
```

### **Consumer Projects**
```
wsl-and-docker-desktop-manager/
├── tui_integration/       # TUI integration (NEW)
│   ├── requirements.txt   # TUI dependencies
│   ├── layouts/          # Project-specific layouts
│   └── install_tui.ps1   # TUI setup script
└── WSL-TUI-Wizard.ps1    # Main TUI entry point (NEW)

devcontainer_server_docker/
├── tui_integration/       # TUI integration (NEW)
│   ├── requirements.txt   # TUI dependencies
│   ├── layouts/          # Project-specific layouts
│   └── install_tui.py    # TUI setup script
└── project/
    └── vps-tui-launcher.py # TUI entry point (NEW)
```

## 🔄 **Development Workflow**

### **Phase 1: TUI Development & Testing**
1. **Develop in TUI_Form_Designer**
   ```bash
   cd TUI_Form_Designer
   pip install -e .[dev]          # Editable install
   # Make changes to source code
   tui-designer demo              # Test changes
   ```

2. **Fix Issues & Iterate**
   ```bash
   # Run tests
   python test_fixes.py
   
   # Validate all layouts
   tui-designer validate tui_layouts/
   
   # Test CLI functionality
   tui-designer preview --list
   ```

3. **Build Packages**
   ```bash
   # Build both engine and editor packages
   ./build.sh
   
   # Verify packages built successfully
   ls dist/engine/
   ls dist/editor/
   ```

### **Phase 2: Distribution to Consumer Projects**

#### **Option A: Local Development (Editable Install)**
```bash
# In consumer project directory
cd ../wsl-and-docker-desktop-manager
pip install -e ../TUI_Form_Designer[dev]
```

#### **Option B: Package Distribution (Production)**
```bash
# Copy packages to consumer projects
cp TUI_Form_Designer/dist/engine/*.whl wsl-and-docker-desktop-manager/tui_integration/
cp TUI_Form_Designer/dist/engine/*.whl devcontainer_server_docker/tui_integration/

# Install in consumer projects
cd wsl-and-docker-desktop-manager
pip install tui_integration/tui_form_engine-*.whl
```

### **Phase 3: Consumer Project Integration**
1. **Create Project-Specific Layouts**
2. **Implement TUI Entry Points**
3. **Test Integration**
4. **Report Issues Back to TUI Team**

## 📦 **Package Distribution Strategy**

### **For Development (Rapid Iteration)**
- Use **editable installs** (`pip install -e`)
- Changes in TUI source immediately available
- Fast feedback loop for fixing issues

### **For Production (Stable Releases)**
- Use **wheel packages** (`.whl` files)
- Versioned releases with changelog
- Reliable, reproducible deployments

## 🛠️ **Setup Scripts**

### **TUI Integration Setup for WSL Manager**
```powershell
# WSL Manager: install_tui.ps1
param([switch]$Development = $false)

if ($Development) {
    # Development mode: editable install
    Write-Host "Installing TUI Form Designer in development mode..."
    pip install -e "../TUI_Form_Designer[dev]"
} else {
    # Production mode: wheel install
    Write-Host "Installing TUI Form Designer from package..."
    pip install tui_integration/tui_form_engine-*.whl
}

# Verify installation
python -c "from tui_form_designer import FlowEngine; print('TUI installed successfully')"
```

### **TUI Integration Setup for VPS Environment**
```python
# VPS Environment: install_tui.py
import subprocess
import sys
from pathlib import Path

def install_tui(development=False):
    if development:
        # Development mode: editable install
        print("Installing TUI Form Designer in development mode...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-e", 
            "../TUI_Form_Designer[dev]"
        ])
    else:
        # Production mode: wheel install
        print("Installing TUI Form Designer from package...")
        wheel_files = list(Path("tui_integration").glob("tui_form_engine-*.whl"))
        if wheel_files:
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                str(wheel_files[0])
            ])
        else:
            print("No TUI package found. Please run build first.")
            sys.exit(1)
    
    # Verify installation
    try:
        from tui_form_designer import FlowEngine
        print("TUI installed successfully")
    except ImportError as e:
        print(f"TUI installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="Development mode")
    args = parser.parse_args()
    install_tui(development=args.dev)
```

## 🔄 **Issue Reporting & Feedback Loop**

### **When Issues Found in Consumer Projects**
1. **Document the Issue**
   - Error messages
   - Steps to reproduce
   - Expected vs actual behavior

2. **Report to TUI Team**
   - Create issue in TUI_Form_Designer repository
   - Include consumer project context
   - Provide minimal reproduction case

3. **Fix in TUI Source**
   - Make changes in TUI_Form_Designer
   - Test fixes using editable install
   - Build new packages when ready

4. **Distribute Updated Packages**
   - Update version numbers
   - Build new packages
   - Distribute to consumer projects
   - Test integration again

## 🎯 **Immediate Next Steps**

1. **Create Integration Directories**
   ```bash
   mkdir -p wsl-and-docker-desktop-manager/tui_integration/layouts
   mkdir -p devcontainer_server_docker/tui_integration/layouts
   ```

2. **Create Setup Scripts**
   - `install_tui.ps1` for WSL Manager
   - `install_tui.py` for VPS Environment

3. **Test Workflow**
   - Build TUI packages
   - Install in consumer projects
   - Create first TUI layouts
   - Verify integration works

4. **Document Integration**
   - Add TUI setup instructions to README files
   - Create troubleshooting guides
   - Document layout development process

---

**Status:** Ready for implementation  
**Next Action:** Create integration directories and setup scripts
