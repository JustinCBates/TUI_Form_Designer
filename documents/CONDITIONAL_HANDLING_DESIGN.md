# Conditional Handling Design for TUI Layouts

## Implementation Status ⏸️ FUTURE WORK

**Status**: Design document for future feature - NOT YET IMPLEMENTED  
**Priority**: Medium  
**Dependencies**: Virtual Layout System ✅ COMPLETE, Hierarchical Defaults ✅ COMPLETE  
**Target Version**: 3.0.0

This document describes a future enhancement to the TUI Form Engine that will enable conditional step execution based on runtime values, environment variables, and user inputs. The core preprocessing and layout systems are complete; conditional logic will be added as a Phase 2 feature when needed.

**Current Implementation**: Steps execute sequentially without conditional logic  
**Future Enhancement**: Steps can be skipped/shown based on conditions

---

## Overview
Design conditional step execution, branching logic, and dynamic configuration paths for TUI layouts to support environment-specific deployments and user-driven configuration scenarios.

## Use Cases

### 1. Environment-Based Conditionals
```yaml
- id: ssl_setup
  type: confirm
  message: "Enable SSL/HTTPS?"
  condition:
    field: environment
    operator: equals
    value: "production"
```

### 2. Answer-Dependent Steps
```yaml
- id: custom_domain
  type: text
  message: "Enter your domain:"
  condition:
    field: ssl_setup
    operator: equals
    value: true
```

### 3. Feature Toggles
```yaml
- id: backup_config
  type: select
  message: "Backup frequency:"
  choices: ["daily", "weekly", "monthly"]
  condition:
    field: environment
    operator: in
    values: ["staging", "production"]
```

## Conditional Syntax Design

### Basic Conditional Structure
```yaml
steps:
  - id: step_id
    type: text
    message: "Your message"
    condition:
      field: "previous_step_id"
      operator: "equals|not_equals|in|not_in|greater_than|less_than"
      value: "comparison_value"
      values: ["array", "of", "values"]  # for in/not_in operators
```

### Advanced Conditionals
```yaml
steps:
  - id: complex_step
    type: text
    message: "Complex conditional step"
    condition:
      logic: "and|or"
      conditions:
        - field: "environment"
          operator: "equals"
          value: "production"
        - field: "use_ssl"
          operator: "equals"
          value: true
```

### Sublayout Conditionals
```yaml
steps:
  - subid: ssl_sublayout
    sublayout: "./sublayouts/ssl_config.layout.yml"
    condition:
      field: "environment"
      operator: "not_equals"
      value: "development"
```

## Implementation Phases

### Phase 1: Basic Conditionals
- Single condition per step
- Simple operators (equals, not_equals)
- Field-value comparisons

### Phase 2: Advanced Logic
- Multiple conditions with AND/OR logic
- Array operators (in, not_in)
- Numeric comparisons

### Phase 3: Dynamic Sublayouts
- Conditional sublayout inclusion
- Environment-specific configuration paths
- Feature-based layout composition

## Conditional Operators

### Comparison Operators
- `equals`: Exact match
- `not_equals`: Not equal
- `in`: Value in array
- `not_in`: Value not in array
- `greater_than`: Numeric comparison
- `less_than`: Numeric comparison
- `contains`: String contains substring
- `regex`: Regular expression match

### Logic Operators
- `and`: All conditions must be true
- `or`: At least one condition must be true
- `not`: Inverse condition result

## Example: Environment-Specific Layout

```yaml
title: "Conditional OpenProject Setup"
description: "Environment-aware configuration"

steps:
  - id: environment
    type: select
    message: "Select environment:"
    choices: ["development", "staging", "production"]
    
  - id: debug_mode
    type: confirm
    message: "Enable debug mode?"
    condition:
      field: environment
      operator: equals
      value: "development"
      
  - subid: ssl_config
    sublayout: "./sublayouts/ssl_config.layout.yml"
    condition:
      field: environment
      operator: in
      values: ["staging", "production"]
      
  - id: monitoring_setup
    type: confirm
    message: "Enable monitoring?"
    condition:
      logic: or
      conditions:
        - field: environment
          operator: equals
          value: "production"
        - field: debug_mode
          operator: equals
          value: false
```

## TUI Form Designer Changes Required

### 1. Condition Parser
- Parse condition syntax from YAML
- Validate condition structure
- Handle missing fields gracefully

### 2. Condition Evaluator
- Evaluate conditions against current answers
- Support all defined operators
- Handle complex logic (AND/OR)

### 3. Dynamic Step Filtering
- Filter steps based on condition results
- Maintain step order and dependencies
- Handle sublayout conditionals

### 4. Answer State Management
- Track all user answers
- Make previous answers available for conditions
- Handle step skipping and answer cleanup

## Error Handling

### Invalid Conditions
- Reference to non-existent fields
- Invalid operator usage
- Type mismatches

### Circular Dependencies
- Step A depends on Step B which depends on Step A
- Prevention and detection strategies

### Missing Answers
- Condition references step that was skipped
- Default behavior definitions

## Testing Strategy

### Unit Tests
- Individual condition evaluation
- Operator functionality
- Error handling

### Integration Tests
- Full conditional flows
- Complex logic scenarios
- Sublayout conditionals

### User Experience Tests
- Intuitive flow progression
- Clear conditional messaging
- Graceful error handling

## Backward Compatibility
- Non-conditional layouts continue to work
- Gradual adoption of conditional features
- Migration path for existing layouts