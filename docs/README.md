# TUI Form Designer - Documentation

This directory contains all design documents, implementation summaries, and reference guides for the TUI Form Designer system.

## 📁 Document Categories

### 🎨 **Design Specifications**

Core design documents describing major features and architectural decisions:

- **CONDITIONAL_HANDLING_DESIGN.md** - Conditional field display and logic handling
- **MODULAR_DEFAULTS_DESIGN.md** - Modular defaults system architecture
- **VIRTUAL_LAYOUT_DESIGN.md** - Virtual layout merging and inheritance system

### 📊 **Implementation Summaries**

Completion reports and status updates for major features:

- **TUI_RENAME_SUMMARY.md** - flow_id → layout_id rename completion summary
- **TUI_VALIDATOR_COMPLETE_STATUS.md** - Complete validator implementation status
- **TUI_VALIDATOR_V2.2_SUMMARY.md** - Validator v2.2 enhancements summary
- **VALIDATOR_OVERHAUL_SUMMARY.md** - Complete validator overhaul summary
- **FLOW_ID_TO_LAYOUT_ID_RENAME.md** - Detailed rename migration documentation
- **PRODUCTION_VALIDATION.md** - Production-ready validation implementation

### 📚 **Reference Guides**

Quick references and field documentation:

- **FIELD_REFERENCE.md** - Complete field type reference
- **VALIDATOR_QUICK_REFERENCE.md** - Quick reference for validator usage
- **VALIDATOR_NO_BACKWARD_COMPATIBILITY.md** - Breaking changes documentation
- **VALIDATOR_V2.2_ENHANCEMENTS.md** - Version 2.2 enhancement details

## 🎯 **Quick Start**

### For New Developers
1. Start with **FIELD_REFERENCE.md** to understand available field types
2. Review **VALIDATOR_QUICK_REFERENCE.md** for validation rules
3. Read design specs to understand core features:
   - **VIRTUAL_LAYOUT_DESIGN.md** for layout inheritance
   - **MODULAR_DEFAULTS_DESIGN.md** for defaults system
   - **CONDITIONAL_HANDLING_DESIGN.md** for conditional logic

### For Form Designers
1. Check **FIELD_REFERENCE.md** for available field types
2. Use **VALIDATOR_QUICK_REFERENCE.md** to ensure forms are valid
3. Review **PRODUCTION_VALIDATION.md** for production requirements

### For Project Maintainers
1. Review implementation summaries for recent changes
2. Check **VALIDATOR_OVERHAUL_SUMMARY.md** for current validation status
3. Reference **TUI_VALIDATOR_COMPLETE_STATUS.md** for version history

## 📋 **Version Information**

### Current Versions
- **TUI Form Designer**: 2.1.0
- **Validator**: 2.2.0 (strict by default, no backward compatibility)
- **Field ID**: `layout_id` (renamed from `flow_id` in v2.1.0)

### Major Milestones
- **v2.2.0** - Dependency validation (defaults files, sublayouts)
- **v2.1.0** - flow_id → layout_id rename (breaking change)
- **v2.0.0** - Strict validation by default (no backward compatibility)
- **v1.0.0** - Initial release with basic validation

## 🔗 **Related Documentation**

- **Main Project Docs**: `/opt/openproject/docs/`
- **Control Flow Docs**: `/opt/openproject/external/control-flow/docs/`
- **Config Manager Docs**: `/opt/openproject/external/config-manager/docs/`

## 📝 **Maintenance**

This documentation is actively maintained. When adding new features:

1. Create or update design spec in design specifications section
2. Add implementation summary when feature is complete
3. Update quick reference guides as needed
4. Keep version information current
5. Update this README when adding new document categories

---

**Last Updated**: October 15, 2025  
**Maintainer**: OpenProject Team
