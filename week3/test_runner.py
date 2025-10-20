#!/usr/bin/env python3
"""
Simple test runner to check for issues in the test suite.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def check_imports():
    """Check if all required modules can be imported."""
    print("🔍 Checking imports...")
    
    try:
        # Check web client
        sys.path.append(str(Path(__file__).parent / "web_client"))
        from app import app
        print("✅ Web client app imported successfully")
    except Exception as e:
        print(f"❌ Web client app import failed: {e}")
        return False
    
    try:
        # Check MCP client
        sys.path.append(str(Path(__file__).parent / "mcp_client"))
        from ai_mcp_client import create_mcp_client
        print("✅ MCP client imported successfully")
    except Exception as e:
        print(f"❌ MCP client import failed: {e}")
        return False
    
    try:
        # Check server functions
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "petting_zootopia", 
            str(Path(__file__).parent / "server" / "petting_zootopia.py")
        )
        petting_zootopia = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(petting_zootopia)
        print("✅ Server functions imported successfully")
    except Exception as e:
        print(f"❌ Server functions import failed: {e}")
        return False
    
    return True

def check_dependencies():
    """Check if all required dependencies are available."""
    print("\n🔍 Checking dependencies...")
    
    required_modules = [
        'pytest',
        'httpx', 
        'requests',
        'asyncio',
        'unittest.mock'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - MISSING")
            missing.append(module)
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install pytest httpx requests")
        return False
    
    return True

def check_test_files():
    """Check if test files exist and are readable."""
    print("\n🔍 Checking test files...")
    
    test_files = [
        "tests/test_web_app.py",
        "tests/test_ai_backends.py", 
        "tests/test_mcp_tools.py",
        "tests/test_e2e.py",
        "tests/test_mcp_client_llm.py"
    ]
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"✅ {test_file}")
        else:
            print(f"❌ {test_file} - NOT FOUND")
            return False
    
    return True

def main():
    """Run all checks."""
    print("🧪 Petting Zootopia Test Suite Checker")
    print("=" * 50)
    
    all_good = True
    
    # Check dependencies
    if not check_dependencies():
        all_good = False
    
    # Check test files
    if not check_test_files():
        all_good = False
    
    # Check imports
    if not check_imports():
        all_good = False
    
    print("\n" + "=" * 50)
    if all_good:
        print("✅ All checks passed! Tests should run successfully.")
        print("\nTo run tests:")
        print("  python -m pytest tests/ -v")
        print("  or")
        print("  ./run_tests.sh")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
