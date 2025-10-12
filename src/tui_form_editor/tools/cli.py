#!/usr/bin/env python3
"""
Unified CLI entry point for TUI Form Designer.
Provides access to all tools through a single command interface.
"""

import argparse
import sys
from pathlib import Path

from tui_form_engine.ui.questionary_ui import QuestionaryUI
from tui_form_engine.core.flow_engine import FlowEngine
from tui_form_engine.core.exceptions import FlowValidationError


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="tui-designer",
        description="Interactive form designer for Questionary-based terminal user interfaces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tui-designer design              # Interactive flow designer
  tui-designer validate flows/    # Validate all flows
  tui-designer test --flow survey # Test specific flow
  tui-designer preview --list     # List all flows
        """
    )
    
    parser.add_argument("--flows-dir", default="flows", 
                       help="Directory containing flow files (default: flows)")
    parser.add_argument("--version", action="version", version="TUI Form Designer 1.0.0")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Design command
    design_parser = subparsers.add_parser("design", help="Interactive flow designer")
    design_parser.add_argument("--flow", help="Flow ID to edit")
    
    # Validate command  
    validate_parser = subparsers.add_parser("validate", help="Validate flow definitions")
    validate_parser.add_argument("flows", nargs="*", help="Flow files to validate")
    validate_parser.add_argument("--interactive", "-i", action="store_true", 
                                help="Interactive validation mode")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test flow execution")
    test_parser.add_argument("--flow", help="Flow ID to test")
    test_parser.add_argument("--mock-data", help="JSON file with mock responses")
    test_parser.add_argument("--all", action="store_true", help="Test all flows")
    test_parser.add_argument("--interactive", "-i", action="store_true", 
                            help="Interactive testing mode")
    
    # Preview command
    preview_parser = subparsers.add_parser("preview", help="Preview flow definitions")
    preview_parser.add_argument("--flow", help="Flow ID to preview")
    preview_parser.add_argument("--step", help="Specific step to preview")
    preview_parser.add_argument("--list", "-l", action="store_true", help="List all flows")
    preview_parser.add_argument("--interactive", "-i", action="store_true", 
                               help="Interactive preview mode")
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run demonstration")
    demo_parser.add_argument("--flow", help="Specific flow to demonstrate")
    
    args = parser.parse_args()
    
    # Set flows directory for all tools
    flows_dir = args.flows_dir
    
    # Ensure flows directory exists
    if not Path(flows_dir).exists() and args.command in ['design', 'validate', 'test', 'preview']:
        ui = QuestionaryUI()
        if ui.confirm(f"Flows directory '{flows_dir}' doesn't exist. Create it?"):
            Path(flows_dir).mkdir(parents=True, exist_ok=True)
            ui.show_success(f"Created flows directory: {flows_dir}")
        else:
            ui.show_error("Cannot proceed without flows directory")
            return 1
    
    if args.command == "design":
        from .designer import InteractiveFlowDesigner
        designer = InteractiveFlowDesigner(flows_dir=flows_dir)
        if args.flow:
            # Could implement direct flow editing here
            pass
        designer.run()
        return 0
        
    elif args.command == "validate":
        from .validator import FlowValidator
        validator = FlowValidator(flows_dir=flows_dir)
        
        if args.interactive:
            validator.interactive_validate()
            return 0
        
        if args.flows:
            success = validator.validate_specific_flows(args.flows)
        else:
            success = validator.validate_all_flows()
        return 0 if success else 1
        
    elif args.command == "test":
        from .tester import FlowTester
        tester = FlowTester(flows_dir=flows_dir)
        
        if args.interactive:
            tester.interactive_test()
            return 0
        
        if args.all:
            success = tester.test_all_flows()
            return 0 if success else 1
        
        if args.flow:
            success = tester.test_flow(args.flow, args.mock_data)
            return 0 if success else 1
        
        # Default to interactive
        tester.interactive_test()
        return 0
        
    elif args.command == "preview":
        from .preview import FlowPreviewer
        previewer = FlowPreviewer(flows_dir=flows_dir)
        
        if args.interactive:
            previewer.interactive_preview()
            return 0
        
        if args.list:
            previewer.list_flows()
            return 0
        
        if args.flow:
            previewer.preview_flow(args.flow, args.step)
            return 0
        
        # Default to interactive
        previewer.interactive_preview()
        return 0
        
    elif args.command == "demo":
        from .demo import run_demo
        return run_demo(flows_dir, args.flow)
        
    else:
        # No command specified - show help and interactive menu
        parser.print_help()
        print()
        
        ui = QuestionaryUI()
        ui.show_title("TUI Form Designer", "🎨")
        ui.show_info("Interactive form designer for terminal user interfaces")
        
        action = ui.select(
            "What would you like to do?",
            choices=[
                "🎨 Design flows (Interactive designer)",
                "🔍 Validate flows (Check syntax and logic)",
                "🧪 Test flows (Execute with mock data)",
                "👁️ Preview flows (View structure)",
                "🚀 Run demo (See examples)",
                "❌ Exit"
            ]
        )
        
        if action.startswith("🎨"):
            from .designer import InteractiveFlowDesigner
            designer = InteractiveFlowDesigner(flows_dir=flows_dir)
            designer.run()
        elif action.startswith("🔍"):
            from .validator import FlowValidator
            validator = FlowValidator(flows_dir=flows_dir)
            validator.interactive_validate()
        elif action.startswith("🧪"):
            from .tester import FlowTester
            tester = FlowTester(flows_dir=flows_dir)
            tester.interactive_test()
        elif action.startswith("👁️"):
            from .preview import FlowPreviewer
            previewer = FlowPreviewer(flows_dir=flows_dir)
            previewer.interactive_preview()
        elif action.startswith("🚀"):
            from .demo import run_demo
            return run_demo(flows_dir, None)
        
        return 0


if __name__ == "__main__":
    sys.exit(main())