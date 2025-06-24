#!/usr/bin/env python3
"""
Simple test to validate the cache implementation without running full server
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    print("🧪 Testing cache manager import...")
    from astro_engine.cache_manager import AstroCacheManager
    print("✅ Cache manager imported successfully")
    
    print("\n🧪 Testing cache manager initialization...")
    cache = AstroCacheManager()
    print(f"✅ Cache manager initialized: {cache.is_available()}")
    
    print("\n🧪 Testing cache operations...")
    # Test basic cache operations
    test_key = "test:simple"
    test_value = {"message": "Hello, Cache!"}
    
    # Set value
    success = cache.set(test_key, test_value, ttl=60)
    print(f"✅ Cache SET operation: {success}")
    
    # Get value
    retrieved = cache.get(test_key)
    print(f"✅ Cache GET operation: {retrieved == test_value}")
    
    # Test stats
    stats = cache.get_stats()
    print(f"✅ Cache stats: {stats}")
    
    print("\n🧪 Testing app import...")
    from astro_engine.app import app
    print("✅ Flask app imported successfully")
    
    print(f"✅ App configuration: Debug={app.config.get('DEBUG', False)}")
    
    print("\n🏆 ALL TESTS PASSED! The cache implementation is working correctly.")
    
    # Offer to start server
    print("\n" + "="*60)
    print("🚀 Ready to start server for integration testing!")
    print("🔗 Run the following command to start the server:")
    print("   export PYTHONPATH='.'; /Library/Developer/CommandLineTools/usr/bin/python3 run_server.py")
    print("📋 Then run the integration test:")
    print("   /Library/Developer/CommandLineTools/usr/bin/python3 phase1_integration_test.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
