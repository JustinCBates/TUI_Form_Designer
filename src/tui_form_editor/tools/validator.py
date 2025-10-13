#!/usr/bin/env python3
"""
Flow Validator Tool
Validate YAML flow definitions for syntax and logic errors.
"""

import yaml
from pathlib import Path
import sys
from typing import List, Dict, Any
import argparse

from tui_form_engine.core.flow_engine import FlowEngine
from tui_form_engine.core.exceptions import FlowValidationError
from tui_form_engine.ui.questionary_ui import QuestionaryUI


class FlowValidator:
    """Validate YAML flow definitions."""
    
    def __init__(self, flows_dir: str = "flows"):
        self.flows_dir = Path(flows_dir)
        self.ui = QuestionaryUI()
        self.flow_engine = FlowEngine(flows_dir=flows_dir)
    
    def validate_all_flows(self) -> bool:
        """Validate all flows in the flows directory."""
        if not self.flows_dir.exists():
            self.ui.show_error(f"Flows directory not found: {self.flows_dir}")
            return False
        
        flow_files = list(self.flows_dir.glob("*.yml"))
        if not flow_files:
            self.ui.show_warning("No flow files found")
            return True
        
        self.ui.show_title("Flow Validation", "🔍")
        
        all_valid = True
        for flow_file in flow_files:
            valid = self.validate_flow_file(flow_file)
            if not valid:
                all_valid = False
        
        if all_valid:
            self.ui.show_success(f"All {len(flow_files)} flows are valid! ✨")
        else:
            self.ui.show_error("Some flows have validation errors")
        
        return all_valid
    
    def validate_flow_file(self, flow_path: Path) -> bool:
        """Validate a single flow file."""
        self.ui.show_section_header(f"Validating: {flow_path.name}")
        
        try:
            # Load YAML
            with open(flow_path, 'r') as f:
                flow_def = yaml.safe_load(f)
            
            if not flow_def:
                self.ui.show_error("Empty or invalid YAML file")
                return False
            
            # Validate using FlowEngine
            errors = self.flow_engine.validate_flow(flow_def)
            
            if not errors:
                self.ui.show_success("✅ Valid")
                return True
            else:
                self.ui.show_error(f"❌ {len(errors)} validation errors:")
                for error in errors:
                    self.ui.show_step(f"• {error}")
                return False
                
        except yaml.YAMLError as e:
            self.ui.show_error(f"YAML syntax error: {e}")
            return False
        except Exception as e:
            self.ui.show_error(f"Validation error: {e}")
            return False
    
    def validate_specific_flows(self, flow_files: List[str]) -> bool:
        """Validate specific flow files."""
        self.ui.show_title("Flow Validation", "🔍")
        
        all_valid = True
        for flow_file in flow_files:
            flow_path = Path(flow_file)
            if not flow_path.exists():
                # Try in flows directory
                flow_path = self.flows_dir / flow_file
                if not flow_path.exists():
                    flow_path = self.flows_dir / f"{flow_file}.yml"
            
            if not flow_path.exists():
                self.ui.show_error(f"Flow file not found: {flow_file}")
                all_valid = False
                continue
            
            valid = self.validate_flow_file(flow_path)
            if not valid:
                all_valid = False
        
        return all_valid
    
    def interactive_validate(self):
        """Interactive flow validation."""
        flows = self.flow_engine.get_available_flows()
        if not flows:
            self.ui.show_error("No flows found")
            return
        
        self.ui.show_title("Interactive Flow Validation", "🔍")
        
        while True:
            action = self.ui.select(
                "What would you like to validate?",
                choices=[
                    "All flows",
                    "Specific flow",
                    "Exit"
                ]
            )
            
            if action == "All flows":
                self.validate_all_flows()
            elif action == "Specific flow":
                flow_id = self.ui.select("Select flow to validate:", flows)
                flow_path = self.flows_dir / f"{flow_id}.yml"
                self.validate_flow_file(flow_path)
            elif action == "Exit":
                break


def main():
    """Main entry point for flow validation."""
    parser = argparse.ArgumentParser(description="Validate YAML flow definitions")
    parser.add_argument("flows", nargs="*", help="Specific flow files to validate")
    parser.add_argument("--flows-dir", default="flows", help="Directory containing flow files")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    validator = FlowValidator(flows_dir=args.flows_dir)
    
    if args.interactive:
        validator.interactive_validate()
        return 0
    
    if args.flows:
        success = validator.validate_specific_flows(args.flows)
    else:
        success = validator.validate_all_flows()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())