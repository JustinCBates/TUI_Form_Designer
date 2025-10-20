#!/usr/bin/env python3
"""
Demo Tool
Demonstrate TUI Form Designer capabilities with example flows.
"""

from pathlib import Path
import sys
from typing import Optional

from ..core.flow_engine import FlowEngine
from ..ui.questionary_ui import QuestionaryUI


def run_demo(flows_dir: str = "flows", flow_id: Optional[str] = None) -> int:
    """Run demonstration of TUI Form Designer."""
    ui = QuestionaryUI()
    flow_engine = FlowEngine(flows_dir=flows_dir)

    ui.show_title("TUI Form Designer Demo", "🚀")
    ui.show_info("Demonstrating interactive form capabilities")

    # Check if we have flows to demo
    flows = flow_engine.get_available_flows()

    if not flows:
        ui.show_warning("No flows found - creating sample flows for demo")
        create_sample_flows(flows_dir)
        flows = flow_engine.get_available_flows()

    if flow_id:
        if flow_id in flows:
            demo_specific_flow(flow_engine, flow_id, ui)
        else:
            ui.show_error(f"Flow not found: {flow_id}")
            return 1
    else:
        demo_interactive_selection(flow_engine, flows, ui)

    return 0


def demo_interactive_selection(flow_engine: FlowEngine, flows: list, ui: QuestionaryUI):
    """Interactive demo flow selection."""
    while True:
        ui.show_section_header("Available Demo Flows", "📋")

        # Show flows with descriptions
        flow_descriptions = []
        for flow_id in flows:
            try:
                flow_path = flow_engine.flows_dir / f"{flow_id}.yml"
                import yaml

                with open(flow_path) as f:
                    flow_def = yaml.safe_load(f)

                title = flow_def.get("title", flow_id)
                description = flow_def.get("description", "No description")
                icon = flow_def.get("icon", "📄")

                flow_descriptions.append(f"{icon} {title} - {description}")
            except Exception:
                flow_descriptions.append(f"📄 {flow_id}")

        flow_descriptions.append("❌ Exit Demo")

        choice = ui.select("Select a flow to demonstrate:", flow_descriptions)

        if choice.startswith("❌"):
            ui.show_info("Demo completed! 👋")
            break

        # Extract flow_id from choice
        selected_flow = None
        for i, flow_id in enumerate(flows):
            if choice == flow_descriptions[i]:
                selected_flow = flow_id
                break

        if selected_flow:
            demo_specific_flow(flow_engine, selected_flow, ui)


def demo_specific_flow(flow_engine: FlowEngine, flow_id: str, ui: QuestionaryUI):
    """Demonstrate a specific flow."""
    try:
        ui.show_phase_header(f"Demonstrating: {flow_id}", "🎬")

        # Show flow information
        flow_path = flow_engine.flows_dir / f"{flow_id}.yml"
        import yaml

        with open(flow_path) as f:
            flow_def = yaml.safe_load(f)

        title = flow_def.get("title", flow_id)
        description = flow_def.get("description", "No description")
        steps_count = len(flow_def.get("steps", []))

        ui.show_info(f"Title: {title}")
        ui.show_info(f"Description: {description}")
        ui.show_info(f"Steps: {steps_count}")

        if not ui.confirm("Execute this flow?", default=True):
            return

        # Execute the flow
        ui.show_section_header("Flow Execution", "▶️")
        results = flow_engine.execute_flow(flow_id)

        # Show results
        ui.show_success("Flow completed successfully! ✨")
        ui.show_section_header("Results", "📊")

        def display_results(data, indent=0):
            prefix = "  " * indent
            for key, value in data.items():
                if isinstance(value, dict):
                    ui.show_info(f"{prefix}{key}:")
                    display_results(value, indent + 1)
                else:
                    ui.show_info(f"{prefix}{key}: {value}")

        display_results(results)

    except Exception as e:
        ui.show_error(f"Demo failed: {e}")


def create_sample_flows(flows_dir: str):
    """Create sample flows for demonstration."""
    flows_path = Path(flows_dir)
    flows_path.mkdir(parents=True, exist_ok=True)

    # Sample 1: Simple Survey
    survey_flow = {
        "layout_id": "simple_survey",
        "title": "Simple Survey",
        "description": "A basic user satisfaction survey",
        "icon": "📋",
        "steps": [
            {
                "id": "user_name",
                "type": "text",
                "message": "What's your name?",
                "validate": "required",
            },
            {
                "id": "satisfaction",
                "type": "select",
                "message": "How satisfied are you with our service?",
                "choices": [
                    "😍 Very Satisfied",
                    "😊 Satisfied",
                    "😐 Neutral",
                    "😞 Dissatisfied",
                    "😡 Very Dissatisfied",
                ],
            },
            {
                "id": "recommend",
                "type": "confirm",
                "message": "Would you recommend us to others?",
                "default": True,
            },
            {
                "id": "feedback",
                "type": "text",
                "message": "Any additional feedback? (optional)",
                "instruction": "Your feedback helps us improve",
            },
        ],
        "output_mapping": {
            "user": {
                "name": "user_name",
                "satisfaction": "satisfaction",
                "would_recommend": "recommend",
                "feedback": "feedback",
            }
        },
    }

    # Sample 2: Application Setup
    setup_flow = {
        "layout_id": "app_setup",
        "title": "Application Setup Wizard",
        "description": "Configure your application settings",
        "icon": "⚙️",
        "steps": [
            {
                "id": "app_name",
                "type": "text",
                "message": "Application name:",
                "default": "MyApp",
                "validate": "required",
            },
            {
                "id": "environment",
                "type": "select",
                "message": "Deployment environment:",
                "choices": ["development", "staging", "production"],
                "default": "development",
            },
            {
                "id": "database_url",
                "type": "text",
                "message": "Database URL:",
                "default": "postgresql://localhost:5432/myapp",
                "instruction": "Full connection string for your database",
            },
            {
                "id": "enable_debug",
                "type": "confirm",
                "message": "Enable debug mode?",
                "default": True,
                "condition": "environment == development",
            },
            {
                "id": "admin_email",
                "type": "text",
                "message": "Administrator email:",
                "validate": "email",
                "instruction": "Email for system notifications",
            },
        ],
        "output_mapping": {
            "application": {
                "name": "app_name",
                "environment": "environment",
                "debug_enabled": "enable_debug",
            },
            "database": {"url": "database_url"},
            "admin": {"email": "admin_email"},
        },
    }

    # Sample 3: User Registration
    registration_flow = {
        "layout_id": "user_registration",
        "title": "User Registration",
        "description": "Register a new user account",
        "icon": "👤",
        "steps": [
            {
                "id": "username",
                "type": "text",
                "message": "Choose a username:",
                "validate": "required",
                "instruction": "Must be unique and at least 3 characters",
            },
            {
                "id": "email",
                "type": "text",
                "message": "Email address:",
                "validate": "email",
            },
            {
                "id": "password",
                "type": "password",
                "message": "Password:",
                "validate": "password_length",
                "instruction": "At least 8 characters",
            },
            {
                "id": "account_type",
                "type": "select",
                "message": "Account type:",
                "choices": ["Basic", "Premium", "Enterprise"],
                "default": "Basic",
            },
            {
                "id": "newsletter",
                "type": "confirm",
                "message": "Subscribe to newsletter?",
                "default": False,
                "instruction": "Get updates about new features",
            },
            {
                "id": "terms_accepted",
                "type": "confirm",
                "message": "Accept terms and conditions?",
                "default": False,
                "instruction": "Required to create account",
            },
        ],
        "output_mapping": {
            "user": {
                "username": "username",
                "email": "email",
                "password": "password",
                "account_type": "account_type",
            },
            "preferences": {"newsletter": "newsletter"},
            "legal": {"terms_accepted": "terms_accepted"},
        },
    }

    # Write sample flows
    samples = [
        ("simple_survey.yml", survey_flow),
        ("app_setup.yml", setup_flow),
        ("user_registration.yml", registration_flow),
    ]

    import yaml

    for filename, flow_data in samples:
        flow_path = flows_path / filename
        with open(flow_path, "w") as f:
            yaml.dump(flow_data, f, default_flow_style=False, sort_keys=False)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TUI Form Designer Demo")
    parser.add_argument(
        "--flows-dir", default="flows", help="Directory containing flow files"
    )
    parser.add_argument("--flow", help="Specific flow to demonstrate")

    args = parser.parse_args()
    sys.exit(run_demo(args.flows_dir, args.flow))
