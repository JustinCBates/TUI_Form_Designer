#!/usr/bin/env python3
"""
Test the fixed TUI Form Designer functionality
"""

import sys
from pathlib import Path

def test_updated_yaml_files():
    """Test that YAML files now use layout_id"""
    print("🧪 Testing updated YAML files...")
    
    simple_survey_path = Path("tui_layouts/basic/simple_survey.yml")
    user_reg_path = Path("tui_layouts/basic/user_registration.yml")
    
    if not simple_survey_path.exists():
        print(f"❌ File not found: {simple_survey_path}")
        return False
    
    if not user_reg_path.exists():
        print(f"❌ File not found: {user_reg_path}")
        return False
    
    # Check simple_survey.yml
    with open(simple_survey_path, 'r') as f:
        content = f.read()
        if 'layout_id:' in content and 'flow_id:' not in content:
            print(f"✅ {simple_survey_path} updated to use layout_id")
        else:
            print(f"❌ {simple_survey_path} still has issues")
            return False
    
    # Check user_registration.yml  
    with open(user_reg_path, 'r') as f:
        content = f.read()
        if 'layout_id:' in content and 'flow_id:' not in content:
            print(f"✅ {user_reg_path} updated to use layout_id")
        else:
            print(f"❌ {user_reg_path} still has issues")
            return False
    
    return True

def test_flow_engine_methods():
    """Test that FlowEngine has required methods"""
    print("\n🧪 Testing FlowEngine methods...")
    
    try:
        from tui_form_designer import FlowEngine
        
        # Test initialization
        engine = FlowEngine(flows_dir="tui_layouts/basic")
        print("✅ FlowEngine initialized successfully")
        
        # Test get_available_flows method exists
        if hasattr(engine, 'get_available_flows'):
            print("✅ get_available_flows method exists")
            
            # Test it works
            flows = engine.get_available_flows()
            print(f"✅ Found flows: {flows}")
            
            if 'simple_survey' in flows and 'user_registration' in flows:
                print("✅ Demo flows discovered correctly")
                return True
            else:
                print(f"❌ Expected flows not found: {flows}")
                return False
        else:
            print("❌ get_available_flows method missing")
            return False
            
    except Exception as e:
        print(f"❌ FlowEngine test failed: {e}")
        return False

def test_flow_validation():
    """Test that flows validate correctly"""
    print("\n🧪 Testing flow validation...")
    
    try:
        from tui_form_designer import FlowEngine
        import yaml
        
        engine = FlowEngine(flows_dir="tui_layouts/basic")
        
        # Test simple_survey validation
        with open("tui_layouts/basic/simple_survey.yml", 'r') as f:
            flow_def = yaml.safe_load(f)
        
        errors = engine.validate_flow(flow_def)
        if not errors:
            print("✅ simple_survey.yml validates successfully")
        else:
            print(f"❌ simple_survey.yml validation errors: {errors}")
            return False
        
        # Test user_registration validation
        with open("tui_layouts/basic/user_registration.yml", 'r') as f:
            flow_def = yaml.safe_load(f)
            
        errors = engine.validate_flow(flow_def)
        if not errors:
            print("✅ user_registration.yml validates successfully")
        else:
            print(f"❌ user_registration.yml validation errors: {errors}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

def main():
    print("🔍 TUI Form Designer Fix Verification")
    print("=" * 40)
    
    # Test 1: YAML files updated
    if not test_updated_yaml_files():
        sys.exit(1)
    
    # Test 2: FlowEngine methods
    if not test_flow_engine_methods():
        sys.exit(1)
    
    # Test 3: Flow validation
    if not test_flow_validation():
        sys.exit(1)
    
    print("\n🎉 All fixes verified successfully!")
    print("✅ Demo YAML files updated to use layout_id")
    print("✅ FlowEngine.get_available_flows() method working")
    print("✅ Flow validation passes")

if __name__ == "__main__":
    main()