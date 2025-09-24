#!/usr/bin/env python3
"""
Test script for FloatChat system
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.append(str(backend_path))

def test_database():
    """Test database functionality"""
    print("Testing database...")
    
    from database_manager import DatabaseManager
    
    db = DatabaseManager()
    db.create_sample_data()
    
    # Test basic query
    result = db.execute_query("SELECT COUNT(*) as count FROM profiles")
    print(f"✅ Database test passed: {result['data'][0]['count']} profiles found")
    
    return True

def test_chatbot():
    """Test chatbot functionality"""
    print("Testing AI chatbot...")
    
    from ai_chatbot import AIChatbot
    
    chatbot = AIChatbot()
    
    # Test queries
    test_queries = [
        "Show me a summary of the data",
        "Find profiles with temperature above 15 degrees",
        "How many profiles are there?"
    ]
    
    for query in test_queries:
        result = chatbot.process_user_input(query)
        if result['success']:
            print(f"✅ Query '{query}' processed successfully")
        else:
            print(f"❌ Query '{query}' failed: {result['error']}")
            return False
    
    return True

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import plotly
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    try:
        import folium
        print("✅ Folium imported successfully")
    except ImportError as e:
        print(f"❌ Folium import failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 FloatChat System Test")
    print("=" * 30)
    
    tests = [
        ("Import Test", test_imports),
        ("Database Test", test_database),
        ("Chatbot Test", test_chatbot)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with error: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to run.")
        print("Run 'python simple_launcher.py' to start the application.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
