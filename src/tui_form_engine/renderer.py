#!/usr/bin/env python3
"""
TUI Form Engine - Production Renderer
====================================

A lightweight, production-ready renderer for executing TUI forms without
design/editing capabilities. This is what end users interact with.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core.flow_engine import FlowEngine
from .core.exceptions import FlowValidationError, FlowExecutionError


class FormRenderer:
    """Production renderer for TUI forms - end-user facing interface."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize the renderer."""
        self.console = console or Console()
        self.engine = FlowEngine()
    
    def render_flow(
        self, 
        flow_path: str, 
        mock_responses: Optional[Dict[str, Any]] = None,
        output_file: Optional[str] = None,
        quiet: bool = False
    ) -> Dict[str, Any]:
        """
        Render and execute a flow for end-user interaction.
        
        Args:
            flow_path: Path to the YAML flow definition
            mock_responses: Optional mock responses for testing
            output_file: Optional file to save responses to
            quiet: Suppress non-essential output
            
        Returns:
            Dict containing user inputs and metadata
        """
        if not quiet:
            self._show_welcome()
        
        try:
            # Load and validate flow definition
            flow_def = self._load_flow_yaml(flow_path)
            flow_id = flow_def.get('metadata', {}).get('id', 'unnamed_flow')
            
            if not quiet:
                self._show_flow_info(flow_def)
            
            # Execute the flow using the engine
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True
            ) as progress:
                if not quiet:
                    task = progress.add_task("Preparing form...", total=None)
                
                # Execute the flow - use the flow definition directly
                # Create a temporary flow ID from the metadata or filename
                flow_id = flow_def.get('metadata', {}).get('id') or Path(flow_path).stem
                
                # Set the flows directory to the directory containing the flow file
                flow_dir = Path(flow_path).parent
                self.engine.flows_dir = flow_dir
                
                # Execute using the flow ID
                responses = self.engine.execute_flow(
                    flow_id, 
                    mock_responses=mock_responses
                )
                
                if not quiet:
                    progress.update(task, description="Complete!")
            
            # Create response object
            response_data = {
                "flow_id": flow_id,
                "completed_at": datetime.now().isoformat(),
                "responses": responses,
                "metadata": {
                    "total_steps": len(responses),
                    "execution_time": datetime.now().isoformat()
                }
            }
            
            # Save output if requested
            if output_file:
                self._save_output(response_data, output_file)
            
            if not quiet:
                self._show_completion(response_data, output_file)
            
            return response_data
            
        except Exception as e:
            self.console.print(f"[red]❌ Error: {str(e)}[/red]")
            raise
    
    def _load_flow_yaml(self, flow_path: str) -> Dict[str, Any]:
        """Load flow definition from YAML file."""
        path = Path(flow_path)
        if not path.exists():
            raise FileNotFoundError(f"Flow definition not found: {flow_path}")
        
        with open(path, 'r') as f:
            flow_data = yaml.safe_load(f)
        
        return flow_data
    
    def _show_welcome(self):
        """Show welcome message."""
        welcome_text = Text("🎯 Interactive Configuration", style="bold blue")
        self.console.print(Panel(
            welcome_text,
            title="Welcome",
            border_style="blue",
            padding=(1, 2)
        ))
    
    def _show_flow_info(self, flow_def: Dict[str, Any]):
        """Show flow information."""
        metadata = flow_def.get('metadata', {})
        steps = flow_def.get('steps', [])
        
        info_text = Text()
        info_text.append(f"📋 Flow: ", style="bold")
        info_text.append(f"{metadata.get('title', 'Unnamed Flow')}\n", style="cyan")
        
        if metadata.get('description'):
            info_text.append(f"📝 Description: ", style="bold")
            info_text.append(f"{metadata['description']}\n", style="dim")
        
        info_text.append(f"📊 Steps: ", style="bold")
        info_text.append(f"{len(steps)} configuration steps", style="green")
        
        self.console.print(Panel(
            info_text,
            title="Configuration Overview",
            border_style="green",
            padding=(1, 2)
        ))
        self.console.print()  # Add spacing
    
    def _save_output(self, response_data: Dict[str, Any], output_file: str):
        """Save response to file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(response_data, f, indent=2)
    
    def _show_completion(self, response_data: Dict[str, Any], output_file: Optional[str]):
        """Show completion message."""
        completion_text = Text()
        completion_text.append("🎉 Configuration completed successfully!\n\n", style="bold green")
        
        completion_text.append(f"📊 Collected ", style="bold")
        completion_text.append(f"{len(response_data['responses'])} responses\n", style="cyan")
        
        completion_text.append(f"⏱️  Completed at ", style="bold")
        completion_text.append(f"{response_data['completed_at']}\n", style="dim")
        
        if output_file:
            completion_text.append(f"💾 Saved to ", style="bold")
            completion_text.append(f"{output_file}", style="yellow")
        
        self.console.print(Panel(
            completion_text,
            title="Success",
            border_style="green",
            padding=(1, 2)
        ))


def main():
    """CLI entry point for the form renderer."""
    parser = argparse.ArgumentParser(
        description="TUI Form Engine - Production Renderer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a configuration flow
  python -m tui_form_engine.renderer config.yml
  
  # Run with mock responses (for testing)
  python -m tui_form_engine.renderer config.yml --mock responses.json
  
  # Save output to file
  python -m tui_form_engine.renderer config.yml --output results.json
  
  # Quiet mode (minimal output)
  python -m tui_form_engine.renderer config.yml --quiet
        """
    )
    
    parser.add_argument(
        "flow_file",
        help="Path to the YAML flow definition file"
    )
    
    parser.add_argument(
        "--mock",
        help="Path to JSON file with mock responses (for testing)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Path to save the response JSON file"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress non-essential output"
    )
    
    args = parser.parse_args()
    
    # Load mock responses if provided
    mock_responses = None
    if args.mock:
        mock_path = Path(args.mock)
        if not mock_path.exists():
            print(f"Error: Mock file not found: {args.mock}", file=sys.stderr)
            sys.exit(1)
        
        with open(mock_path, 'r') as f:
            mock_responses = json.load(f)
    
    # Create renderer and execute flow
    renderer = FormRenderer()
    
    try:
        response = renderer.render_flow(
            flow_path=args.flow_file,
            mock_responses=mock_responses,
            output_file=args.output,
            quiet=args.quiet
        )
        
        if args.quiet:
            # In quiet mode, just output the response data
            print(json.dumps(response.responses, indent=2))
        
    except KeyboardInterrupt:
        print("\n👋 Configuration cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()