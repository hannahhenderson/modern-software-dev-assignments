#!/usr/bin/env python3
"""
Test script for Petting Zootopia MCP Server
Run this to verify all tools are working correctly.
"""

import asyncio
import sys
import os

# Add the server directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from petting_zootopia import greet, duck, dog, cat

async def test_greet():
    """Test the greet function"""
    print("🧪 Testing greet function...")
    try:
        result = greet("Alice")
        print(f"✅ Greet result: {result}")
        return result == "Hello, Alice!"
    except Exception as e:
        print(f"❌ Greet failed: {e}")
        return False

async def test_duck():
    """Test the duck function"""
    print("\n🦆 Testing duck function...")
    try:
        result = await duck()
        print(f"✅ Duck result: {result}")
        return result.startswith("http") and "duck" in result.lower()
    except Exception as e:
        print(f"❌ Duck failed: {e}")
        return False

async def test_dog():
    """Test the dog function"""
    print("\n🐶 Testing dog function...")
    try:
        result = await dog()
        print(f"✅ Dog result: {result}")
        return result.startswith("http") and "dog" in result.lower()
    except Exception as e:
        print(f"❌ Dog failed: {e}")
        return False

async def test_cat():
    """Test the cat function"""
    print("\n🐱 Testing cat function...")
    try:
        result = await cat()
        print(f"✅ Cat result: {result}")
        return result.startswith("http") and "cat" in result.lower()
    except Exception as e:
        print(f"❌ Cat failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Petting Zootopia MCP Server Tests")
    print("=" * 50)
    
    tests = [
        ("Greet Function", test_greet()),
        ("Duck Function", test_duck()),
        ("Dog Function", test_dog()),
        ("Cat Function", test_cat())
    ]
    
    results = []
    for test_name, test_coro in tests:
        result = await test_coro
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your MCP server is working correctly.")
        print("\n💡 Next steps:")
        print("  1. Configure Claude Desktop with your server")
        print("  2. Or use the MCP Inspector tool")
        print("  3. Or try the web interface")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
