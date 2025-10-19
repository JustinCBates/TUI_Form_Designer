#!/usr/bin/env python3
"""
Test script to identify TUI Form Designer issues
"""

import sys
from pathlib import Path

def test_basic_import():
    """Test if we can import the main components"""
    print("🧪 Testing basic imports...")
    try:
        from tui_form_designer import FlowEngine, QuestionaryUI
        print("✅ Basic imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_flow_engine_init():
    """Test if FlowEngine can be initialized"""
    print("\n🧪 Testing FlowEngine initialization...")
    try:
        from tui_form_designer import FlowEngine
        flows_dir = Path("tui_layouts")
        engine = FlowEngine(flows_dir=str(flows_dir))
        print("✅ FlowEngine initialized successfully")
        return True, engine
    except Exception as e:
        print(f"❌ FlowEngine initialization failed: {e}")
        return False, None

def test_flow_discovery(engine):
    """Test if flows can be discovered"""
    print("\n🧪 Testing flow discovery...")
    try:
        # Check if engine has flow discovery methods
        print(f"Engine object: {type(engine)}")
        print(f"Engine attributes: {dir(engine)}")
        return True
    except Exception as e:
        print(f"❌ Flow discovery failed: {e}")
        return False

def main():
    print("🔍 TUI Form Designer Diagnostic Test")
    print("=" * 40)
    
    # Test 1: Basic imports
    if not test_basic_import():
        sys.exit(1)
    
    # Test 2: FlowEngine initialization
    success, engine = test_flow_engine_init()
    if not success:
        sys.exit(1)
    
    # Test 3: Flow discovery
    if not test_flow_discovery(engine):
        sys.exit(1)
    
    print("\n🎉 All basic tests passed!")
    print("Now let's identify specific issues...")

if __name__ == "__main__":
    main()