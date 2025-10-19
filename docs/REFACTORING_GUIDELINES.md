# TUI Form Designer - Refactoring Guidelines

**Version:** 1.0  
**Date:** October 16, 2025  
**Purpose:** Ensure comprehensive updates during major refactors

---

## 🎯 **Overview**

This document establishes guidelines for conducting thorough refactors in TUI Form Designer, ensuring no components are overlooked during structural changes.

## 📋 **Universal Refactor Checklist**

Use this checklist for ANY refactor that changes:
- Field names or structure
- API interfaces  
- File formats
- Validation rules
- CLI commands

### **Core System Components**

- [ ] **Source Code Files**
  - Update all references in `src/tui_form_designer/`
  - Update validation logic
  - Update error messages and exceptions
  - Update type hints and docstrings

- [ ] **Configuration & Build**
  - Update `pyproject.toml` if needed
  - Update build scripts (`build.sh`)
  - Update version numbers appropriately

### **Examples & Demonstrations**

⚠️ **CRITICAL:** Demo files are often overlooked but essential for user experience

- [ ] **Demo YAML Files**
  - `tui_layouts/basic/*.yml`
  - `tui_layouts/advanced/*.yml` 
  - `tui_layouts/templates/*.yml`

- [ ] **Inline Examples**
  - Code examples in `tools/demo.py`
  - Hardcoded samples in CLI tools
  - Test data and mock responses

- [ ] **Documentation Examples**
  - `README.md` YAML examples
  - `README-engine.md` examples
  - `README-editor.md` examples
  - All docs in `docs/` directory

### **External Dependencies**

- [ ] **Related Projects**
  - OpenProject Config Manager layouts
  - Control-Flow scaffolder templates
  - Any projects that import TUI Form Designer

- [ ] **Generated Content**
  - Template files created by scaffolders
  - Auto-generated documentation
  - Example projects or tutorials

### **Testing & Validation**

- [ ] **Automated Tests**
  - Unit tests in `tests/`
  - Integration tests
  - Validation test cases
  - Mock data and fixtures

- [ ] **Manual Verification**
  - Run demo commands successfully
  - Test CLI tool functionality
  - Verify validation works correctly
  - Check error handling

### **Documentation & Communication**

- [ ] **User-Facing Documentation**
  - Main README.md
  - Package-specific READMEs
  - API documentation
  - Quick reference guides

- [ ] **Developer Documentation**
  - Architecture documents
  - Design specifications
  - Migration guides
  - Breaking change notifications

- [ ] **Version Management**
  - Update version numbers
  - Create changelog entries
  - Tag releases appropriately
  - Update compatibility matrices

## 🚨 **High-Risk Areas**

These areas are commonly missed during refactors:

### **Demo Files**
- **Risk:** Break first-time user experience
- **Location:** `tui_layouts/` directory
- **Verification:** Run `tui-designer demo` successfully

### **Hardcoded Examples**
- **Risk:** Inconsistent documentation
- **Location:** Tool files, README examples
- **Verification:** All examples use current syntax

### **Validation Logic**
- **Risk:** Silent failures or incorrect errors
- **Location:** `flow_engine.py`, validator tools
- **Verification:** Old and new formats handled correctly

### **External Templates**
- **Risk:** Generated content uses old formats
- **Location:** Scaffolders, template engines
- **Verification:** Generated files validate correctly

## 🔧 **Refactor Process**

### **Phase 1: Planning**
1. Identify all affected components using this checklist
2. Create migration plan with rollback strategy
3. Communicate breaking changes to stakeholders
4. Plan version number increment

### **Phase 2: Implementation**
1. Update core system components first
2. Update examples and demos second
3. Update documentation third
4. Update external dependencies last

### **Phase 3: Verification**
1. Run all automated tests
2. Manual verification of demo functionality
3. Test CLI commands end-to-end
4. Verify external project compatibility

### **Phase 4: Documentation**
1. Update all documentation
2. Create migration guides if needed
3. Update this refactor checklist if lessons learned
4. Communicate changes to users

## 📚 **Historical Examples**

### **flow_id → layout_id Rename (v2.1.0)**
- **Lesson:** Demo files were initially missed
- **Impact:** CLI demo commands failed
- **Resolution:** Added demo files to standard checklist
- **Documentation:** See `FLOW_ID_TO_LAYOUT_ID_RENAME.md`

## 🎯 **Success Criteria**

A refactor is complete when:
- [ ] All checklist items verified
- [ ] All automated tests pass
- [ ] Demo commands work end-to-end  
- [ ] Documentation reflects changes
- [ ] External projects still function
- [ ] Migration guide provided (if breaking)

## 🔄 **Continuous Improvement**

After each major refactor:
1. Review what was missed
2. Update this checklist
3. Add lessons learned section
4. Improve automation where possible

---

**Remember:** It's better to over-communicate and over-check than to break user workflows with incomplete refactors.

**Last Updated:** October 16, 2025