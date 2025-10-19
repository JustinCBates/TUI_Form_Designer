# TUI Form Designer - Backlog

## Priority 0: CRITICAL SIGNAL HANDLING FIX (PRODUCTION BLOCKER)

### Goal
Fix critical KeyboardInterrupt handling that makes TUI Form Designer unsafe for production use.

### Problem
**CRITICAL SAFETY ISSUE**: TUI engine silently converts Ctrl+C to `None` returns instead of raising exceptions, creating unbreakable application loops where users cannot exit programs.

### Tasks
- [ ] **URGENT**: Fix questionary integration to properly propagate KeyboardInterrupt
- [ ] **CRITICAL**: Ensure consistent behavior - always raise `FlowExecutionError` on Ctrl+C, never return `None`
- [ ] **REQUIRED**: Add comprehensive signal handling tests (single flow, loops, nested scenarios)
- [ ] **SAFETY**: Implement emergency exit mechanisms for unresponsive states
- [ ] **DOCS**: Document signal handling contract for consumer applications

### Evidence
- **Documented**: `CRITICAL-SIGNAL-HANDLING-ISSUE.md`
- **Test Case**: WSL & Docker Manager implementation demonstrates issue
- **Reproduction**: Minimal test case created and validated
- **Impact**: Users become permanently trapped in applications

### Status
**CRITICAL - PRODUCTION BLOCKER** - Must fix before any production use

### AI Developer Alert
🚨 **READ `CRITICAL-SIGNAL-HANDLING-ISSUE.md` IMMEDIATELY** - This issue blocks production use and creates safety hazards for end users.

---

## Priority 1: Architecture Refactoring (Use Control-Flow as Design Tool)

### Goal
Use Control-Flow temporarily to redesign TUI-Form-Designer architecture with clear separation of concerns.

### Tasks
- [ ] Create `design/control_tree.yml` documenting current/desired architecture
- [ ] Rename `FlowEngine` → `FormExecutor` for clarity
- [ ] Extract responsibilities into separate components:
  - [ ] `StepValidator` - Validate step definitions
  - [ ] `StepRenderer` - Render individual steps using questionary
  - [ ] `ResponseCollector` - Collect and format responses
- [ ] Generate architecture documentation from control tree
- [ ] Generate scaffolding for new structure
- [ ] Migrate code to new structure
- [ ] Remove control-flow dependency after refactoring complete

### Benefits
- Clear component responsibilities
- Auto-generated documentation
- Better testability
- Remove naming confusion (FlowEngine vs Control Flow)

### Status
**BACKLOGGED** - Fix critical signal handling first

---

## Future Enhancements

### Features
- [ ] **TUI Persistence System** - Optional response persistence across navigation sessions
- [ ] Support for dynamic step injection
- [ ] Step dependencies and ordering
- [ ] Multi-language support
- [ ] Theme customization UI

### New Features
- [ ] **TUI Workflow Designer** - Interactive YAML workflow creation tool to eliminate hand-coding errors
- [ ] **TUI Persistence System** - Optional response persistence across navigation sessions
- [ ] Support for dynamic step injection
- [ ] Step dependencies and ordering
- [ ] Multi-language support
- [ ] Theme customization UI

### Technical Debt
- [ ] Improve error messages
- [ ] Add more comprehensive tests
- [ ] Performance optimization for large forms
- [ ] Better handling of terminal resize events
- [x] **CRITICAL: Fix Unicode/Encoding Validation** - Validator should detect and report Unicode encoding issues in YAML files (smart quotes, etc.)

---

## Implemented Solutions

### TUI Workflow Designer Tool
**Status:** PROOF-OF-CONCEPT COMPLETE  
**Location:** `workflow_designer.py` and `workflow_designer_demo.py`

**Problem Solved:** Manual YAML creation consistently introduces Unicode encoding errors, syntax mistakes, and structural issues.

**Solution Implemented:**
- Interactive questionary-based workflow designer
- Guided step-by-step YAML creation process
- Built-in validation during creation (field format, step ID validation)
- ASCII-safe YAML output (`allow_unicode=False`)
- Automatic UTF-8 encoding with proper file handling
- Integration with TUI Form Designer validator

**Key Features:**
- Layout metadata creation (ID, title, description, icon)
- Interactive step creation with all field types
- Choice management for select/multiselect steps
- Conditional step display configuration
- Output mapping creation
- Real-time validation feedback

**Benefits:**
- ✅ Eliminates manual YAML coding errors
- ✅ Prevents Unicode encoding issues
- ✅ Ensures proper TUI Form Designer structure
- ✅ Provides immediate validation feedback
- ✅ Generates production-ready workflows

**Future Enhancement Path:**
1. Add to TUI Form Designer core toolkit
2. Create workflow templates for common patterns
3. Add visual workflow preview
4. Enable batch workflow creation

---

### TUI Persistence System
**Status:** PLANNED  
**Priority:** HIGH for WSL & Docker Desktop Manager integration

**Problem Statement:** 
Current TUI system loses user responses when navigating back and forth between selection screens/cards. Users must re-enter information repeatedly, creating poor UX especially in complex multi-step workflows like system configuration wizards.

**Requirements:**

#### Core Persistence Features
- [ ] **Response State Management**
  - Automatically capture and store user responses from all field types
  - Maintain response history across navigation sessions
  - Support partial completion preservation
  - Handle nested/conditional step responses

- [ ] **Navigation Integration**
  - Seamlessly integrate with existing NavigationController
  - Preserve responses when using "← Go back" functionality
  - Re-populate form fields with previously entered values
  - Maintain response consistency across workflow branches

- [ ] **Storage Backend Options**
  - [ ] **Memory-based**: In-memory storage for single session persistence
  - [ ] **File-based**: JSON/YAML file storage for cross-session persistence
  - [ ] **Temporary**: OS temp directory for automatic cleanup
  - [ ] **Project-based**: Save to project directory for workflow resumption

#### Export & Integration Features
- [ ] **Export Mechanisms**
  - Export complete response set at successful workflow completion
  - Support multiple output formats (JSON, YAML, PowerShell variables)
  - Custom export templates for different target systems
  - Selective export (exclude sensitive/temporary responses)

- [ ] **WSL & Docker Manager Integration**
  - Export configuration for PowerShell script consumption
  - Map TUI responses to PowerShell script parameters
  - Generate execution-ready configuration files
  - Support phased configuration export (backup, install, configure, restore)

#### Advanced Persistence Features
- [ ] **Response Validation Persistence**
  - Store validation results to avoid re-validation
  - Cache expensive validation operations (network checks, file system scans)
  - Preserve validation state across navigation

- [ ] **Workflow Resumption**
  - Auto-save progress at configurable intervals
  - Resume interrupted workflows from last completed step
  - Handle workflow version compatibility (schema changes)
  - Provide "Continue where you left off" functionality

- [ ] **Response Templating**
  - Save common response patterns as reusable templates
  - User-defined template creation and management
  - Template sharing and import/export
  - Pre-populate workflows from templates

#### Configuration & Control
- [ ] **Persistence Policies**
  - Configurable persistence levels (none, session, permanent)
  - Per-field persistence control (exclude sensitive fields)
  - Automatic cleanup policies (age-based, size-based)
  - Privacy controls for sensitive information

- [ ] **Response Transformation**
  - Transform responses for different target systems
  - Custom mapping functions (TUI field → PowerShell parameter)
  - Response validation and sanitization before export
  - Support for complex data structure transformation

#### Technical Architecture
- [ ] **PersistenceManager Class**
  - Singleton pattern for global response state management
  - Pluggable storage backends (memory, file, database)
  - Thread-safe response operations
  - Event-driven response capture and restoration

- [ ] **ResponseStore Interface**
  - Standardized interface for different storage backends
  - Key-value storage with hierarchical support (workflow.step.field)
  - Metadata storage (timestamps, validation results, user notes)
  - Atomic operations for concurrent access safety

- [ ] **Integration Points**
  - Hook into existing FlowEngine/FormExecutor
  - Extend NavigationController for response restoration
  - Modify StepRenderer to populate from persistence store
  - Add export triggers to successful workflow completion

#### Use Cases for WSL & Docker Manager
1. **System Configuration Wizard**
   - User starts complex WSL installation configuration
   - Navigates through multiple screens (WSL distro, Docker settings, networking)
   - Goes back to change distro selection
   - Previous Docker and networking choices are preserved
   - Exports final configuration for PowerShell execution

2. **Workflow Resumption**
   - User begins backup and reinstall process
   - Interrupts during Docker configuration
   - Returns later and resumes from Docker configuration step
   - All previous backup and WSL choices are restored

3. **Template-based Configuration**
   - User creates "Development Environment" template
   - Template includes common distro, Docker, and networking choices
   - Future configurations auto-populate from template
   - Reduces repeated data entry for similar setups

#### Implementation Priority
1. **Phase 1**: Memory-based persistence with NavigationController integration
2. **Phase 2**: File-based persistence and export functionality
3. **Phase 3**: Template system and advanced resumption features
4. **Phase 4**: WSL & Docker Manager integration and PowerShell export

#### Benefits
- ✅ Eliminates repeated data entry during navigation
- ✅ Enables complex workflow resumption
- ✅ Provides seamless integration with external systems
- ✅ Improves user experience in multi-step processes
- ✅ Enables workflow templating and reuse
- ✅ Supports enterprise configuration management patterns

---

## Critical Bug Fixes

### Unicode/Encoding Validation in YAML Files
**Priority:** ✅ COMPLETED  
**Issue:** TUI Form Designer's validator didn't detect Unicode encoding issues in YAML files, leading to runtime `UnicodeDecodeError: 'charmap' codec can't decode byte 0x90` errors.

**Root Cause:**
- Validator opens files without specifying encoding (`open(file, 'r')` vs `open(file, 'r', encoding='utf-8')`)
- Smart quotes (`'` `'`) and other Unicode characters cause Windows cp1252 codec failures
- No pre-validation of file encoding or character compatibility

**Solution Implemented:**
1. ✅ **Encoding Detection**: Added `_validate_file_encoding()` method to validator
2. ✅ **Smart Quote Detection**: Scans for problematic Unicode characters (U+2018, U+2019, etc.)
3. ✅ **Detailed Error Messages**: Reports specific Unicode issues with character positions and fix suggestions
4. ✅ **File Encoding Validation**: All YAML file operations now use explicit UTF-8 encoding
5. ✅ **Graceful Error Handling**: Validator catches encoding issues before runtime errors

**Files Affected:**
- `src/tui_form_designer/tools/validator.py` - Main validator
- `src/tui_form_designer/core/flow_engine.py` - YAML loading
- All YAML file readers throughout codebase

**Test Case:**
- YAML file with smart quotes should be detected and reported before runtime
- Validation should provide clear guidance on fixing Unicode issues

---

**Created:** 2025-10-14  
**Last Updated:** 2025-10-16
