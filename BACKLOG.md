# TUI Form Designer - Backlog

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
**BACKLOGGED** - Clean up config-manager first

---

## Future Enhancements

### Features
- [ ] Support for dynamic step injection
- [ ] Step dependencies and ordering
- [ ] Multi-language support
- [ ] Theme customization UI

### Technical Debt
- [ ] Improve error messages
- [ ] Add more comprehensive tests
- [ ] Performance optimization for large forms
- [ ] Better handling of terminal resize events

---

**Created:** 2025-10-14
**Last Updated:** 2025-10-14
