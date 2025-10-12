#!/usr/bin/env python3
"""
Flow Preview Tool
Preview flow definitions and their structure without execution.
"""

import yaml
from pathlib import Path
import sys
from typing import Dict, Any, Optional
import argparse

from ..core.flow_engine import FlowEngine
from ..core.exceptions import FlowValidationError
from ..ui.questionary_ui import QuestionaryUI


class FlowPreviewer:
    """Preview flow definitions and structure."""
    
    def __init__(self, flows_dir: str = "flows"):
        self.flows_dir = Path(flows_dir)
        self.ui = QuestionaryUI()
        self.flow_engine = FlowEngine(flows_dir=flows_dir)
    
    def preview_flow(self, flow_id: str, step_id: Optional[str] = None):
        """Preview a flow or specific step."""
        try:
            flow_path = self.flows_dir / f"{flow_id}.yml"
            with open(flow_path, 'r') as f:
                flow_def = yaml.safe_load(f)
            
            if step_id:
                self._preview_step(flow_def, step_id)
            else:
                self._preview_full_flow(flow_def)
                
        except FileNotFoundError:
            self.ui.show_error(f"Flow not found: {flow_id}")
        except Exception as e:
            self.ui.show_error(f"Error loading flow: {e}")
    
    def _preview_full_flow(self, flow_def: Dict[str, Any]):
        """Preview the complete flow."""
        # Show header
        title = flow_def.get('title', 'Untitled Flow')
        icon = flow_def.get('icon', '📄')
        self.ui.show_title(f"{icon} {title}", "🔍")
        
        # Show metadata
        if flow_def.get('description'):
            self.ui.show_info(f"Description: {flow_def['description']}")
        
        flow_id = flow_def.get('flow_id', 'unknown')
        self.ui.show_info(f"Flow ID: {flow_id}")
        
        steps = flow_def.get('steps', [])
        self.ui.show_info(f"Steps: {len(steps)}")
        
        # Validate flow
        errors = self.flow_engine.validate_flow(flow_def)
        if errors:
            self.ui.show_warning(f"Validation Issues: {len(errors)}")
            for error in errors[:3]:  # Show first 3 errors
                self.ui.show_step(f"• {error}")
            if len(errors) > 3:
                self.ui.show_step(f"• ... and {len(errors) - 3} more")
        else:
            self.ui.show_success("✅ Flow is valid")
        
        # Show steps overview
        self.ui.show_section_header("Steps Overview", "📋")
        for i, step in enumerate(steps, 1):
            self._preview_step_summary(step, i)
        
        # Show output mapping if present
        if 'output_mapping' in flow_def:
            self.ui.show_section_header("Output Mapping", "🗂️")
            self._preview_output_mapping(flow_def['output_mapping'])
    
    def _preview_step(self, flow_def: Dict[str, Any], step_id: str):
        """Preview a specific step."""
        steps = flow_def.get('steps', [])
        step = None
        
        for s in steps:
            if s.get('id') == step_id:
                step = s
                break
        
        if not step:
            self.ui.show_error(f"Step not found: {step_id}")
            return
        
        self.ui.show_title(f"Step Preview: {step_id}", "🔍")
        self._preview_step_detail(step)
    
    def _preview_step_summary(self, step: Dict[str, Any], index: int):
        """Preview step summary."""
        step_id = step.get('id', f'step_{index}')
        step_type = step.get('type', 'unknown')
        message = step.get('message', 'No message')
        
        # Determine step icon
        icons = {
            'text': '📝',
            'select': '📋',
            'confirm': '❓',
            'password': '🔒',
            'computed': '🧮'
        }
        icon = icons.get(step_type, '❔')
        
        self.ui.show_info(f"{index}. {icon} {step_id} ({step_type})")
        self.ui.show_step(f"'{message[:60]}{'...' if len(message) > 60 else ''}'")
        
        # Show additional info
        extras = []
        if step.get('default'):
            extras.append(f"default: {step['default']}")
        if step.get('condition'):
            extras.append(f"conditional")
        if step.get('validate'):
            extras.append(f"validated")
        if step.get('choices'):
            extras.append(f"{len(step['choices'])} choices")
        
        if extras:
            self.ui.show_step(f"({', '.join(extras)})")
    
    def _preview_step_detail(self, step: Dict[str, Any]):
        """Preview detailed step information."""
        # Basic info
        self.ui.show_info(f"Type: {step.get('type', 'unknown')}")
        self.ui.show_info(f"ID: {step.get('id', 'unknown')}")
        
        if step.get('message'):
            self.ui.show_info(f"Message: {step['message']}")
        
        if step.get('instruction'):
            self.ui.show_info(f"Instruction: {step['instruction']}")
        
        # Type-specific details
        if step.get('type') == 'select' and step.get('choices'):
            self.ui.show_section_header("Choices", "📋")
            for i, choice in enumerate(step['choices'], 1):
                if isinstance(choice, dict):
                    self.ui.show_step(f"{i}. {choice.get('name', choice)}")
                else:
                    self.ui.show_step(f"{i}. {choice}")
        
        # Optional fields
        if step.get('default'):
            self.ui.show_info(f"Default: {step['default']}")
        
        if step.get('validate'):
            self.ui.show_info(f"Validation: {step['validate']}")
        
        if step.get('condition'):
            self.ui.show_info(f"Condition: {step['condition']}")
        
        if step.get('compute'):
            self.ui.show_info(f"Computation: {step['compute']}")
    
    def _preview_output_mapping(self, mapping: Dict[str, Any], indent: int = 0):
        """Preview output mapping structure."""
        prefix = "  " * indent
        
        for key, value in mapping.items():
            if isinstance(value, dict):
                self.ui.show_info(f"{prefix}{key}:")
                self._preview_output_mapping(value, indent + 1)
            else:
                self.ui.show_info(f"{prefix}{key} → {value}")
    
    def list_flows(self):
        """List all available flows with previews."""
        flows = self.flow_engine.get_available_flows()
        if not flows:
            self.ui.show_error("No flows found")
            return
        
        self.ui.show_title("Available Flows", "📁")
        
        for flow_id in flows:
            try:
                flow_path = self.flows_dir / f"{flow_id}.yml"
                with open(flow_path, 'r') as f:
                    flow_def = yaml.safe_load(f)
                
                title = flow_def.get('title', flow_id)
                description = flow_def.get('description', 'No description')
                icon = flow_def.get('icon', '📄')
                steps_count = len(flow_def.get('steps', []))
                
                self.ui.show_section_header(f"{icon} {title}", "")
                self.ui.show_info(f"ID: {flow_id}")
                self.ui.show_info(f"Description: {description}")
                self.ui.show_info(f"Steps: {steps_count}")
                
                # Quick validation
                errors = self.flow_engine.validate_flow(flow_def)
                if errors:
                    self.ui.show_warning(f"⚠️ {len(errors)} validation issues")
                else:
                    self.ui.show_success("✅ Valid")
                
            except Exception as e:
                self.ui.show_error(f"Error reading {flow_id}: {e}")
    
    def interactive_preview(self):
        """Interactive flow preview."""
        flows = self.flow_engine.get_available_flows()
        if not flows:
            self.ui.show_error("No flows found")
            return
        
        self.ui.show_title("Interactive Flow Preview", "🔍")
        
        while True:
            action = self.ui.select(
                "What would you like to preview?",
                choices=[
                    "Preview specific flow",
                    "Preview specific step",
                    "List all flows",
                    "Exit"
                ]
            )
            
            if action == "Preview specific flow":
                flow_id = self.ui.select("Select flow to preview:", flows)
                self.preview_flow(flow_id)
                
            elif action == "Preview specific step":
                flow_id = self.ui.select("Select flow:", flows)
                # Load flow to get steps
                try:
                    flow_path = self.flows_dir / f"{flow_id}.yml"
                    with open(flow_path, 'r') as f:
                        flow_def = yaml.safe_load(f)
                    
                    steps = flow_def.get('steps', [])
                    if not steps:
                        self.ui.show_error("No steps found in flow")
                        continue
                    
                    step_choices = [f"{s.get('id', f'step_{i}')} ({s.get('type', 'unknown')})" 
                                  for i, s in enumerate(steps, 1)]
                    step_choice = self.ui.select("Select step:", step_choices)
                    step_id = step_choice.split(' ')[0]
                    
                    self.preview_flow(flow_id, step_id)
                    
                except Exception as e:
                    self.ui.show_error(f"Error loading flow: {e}")
                
            elif action == "List all flows":
                self.list_flows()
                
            elif action == "Exit":
                break


def main():
    """Main entry point for flow preview."""
    parser = argparse.ArgumentParser(description="Preview YAML flow definitions")
    parser.add_argument("--flow", help="Specific flow to preview")
    parser.add_argument("--step", help="Specific step to preview")
    parser.add_argument("--flows-dir", default="flows", help="Directory containing flow files")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--list", "-l", action="store_true", help="List all flows")
    
    args = parser.parse_args()
    
    previewer = FlowPreviewer(flows_dir=args.flows_dir)
    
    if args.interactive:
        previewer.interactive_preview()
        return 0
    
    if args.list:
        previewer.list_flows()
        return 0
    
    if args.flow:
        previewer.preview_flow(args.flow, args.step)
        return 0
    
    # Default to interactive mode
    previewer.interactive_preview()
    return 0


if __name__ == "__main__":
    sys.exit(main())