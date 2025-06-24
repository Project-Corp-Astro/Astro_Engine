#!/usr/bin/env python3
"""
Debug script to test cache decorator functionality
"""
import requests
import time
import json

def test_cache_decorator():
    """Test the cache decorator is working"""
    
    test_data = {
        "user_name": "Debug Test",
        "birth_date": "1990-01-15",
        "birth_time": "12:30:00",
        "latitude": 28.6139,
        "longitude": 77.209,
        "timezone_offset": 5.5
    }
    
    print("🧪 Testing Cache Decorator Functionality")
    print("=" * 50)
    
    # First request - should be calculated
    print("📤 First request (should be calculated)...")
    start_time = time.time()
    response1 = requests.post("http://localhost:5001/lahiri/natal", json=test_data)
    time1 = time.time() - start_time
    
    if response1.status_code == 200:
        data1 = response1.json()
        perf1 = data1.get('_performance', {})
        print(f"  Status: {response1.status_code}")
        print(f"  Response time: {time1:.3f}s")
        print(f"  Performance metadata: {perf1}")
        print(f"  Cached: {perf1.get('cached', 'Unknown')}")
    else:
        print(f"  ❌ Error: {response1.status_code} - {response1.text}")
        return False
    
    # Second request - should be cached
    print("\n📤 Second request (should be cached)...")
    start_time = time.time()
    response2 = requests.post("http://localhost:5001/lahiri/natal", json=test_data)
    time2 = time.time() - start_time
    
    if response2.status_code == 200:
        data2 = response2.json()
        perf2 = data2.get('_performance', {})
        print(f"  Status: {response2.status_code}")
        print(f"  Response time: {time2:.3f}s")
        print(f"  Performance metadata: {perf2}")
        print(f"  Cached: {perf2.get('cached', 'Unknown')}")
    else:
        print(f"  ❌ Error: {response2.status_code} - {response2.text}")
        return False
    
    # Check cache stats
    print("\n📊 Cache Statistics...")
    stats_response = requests.get("http://localhost:5001/cache/stats")
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"  Cache hits: {stats.get('cache_hits', 0)}")
        print(f"  Cache misses: {stats.get('cache_misses', 0)}")
        print(f"  Cache errors: {stats.get('cache_errors', 0)}")
        print(f"  Hit rate: {stats.get('hit_rate', 0):.1%}")
        print(f"  Redis info: {stats.get('redis_info', {})}")
    else:
        print(f"  ❌ Cache stats error: {stats_response.status_code}")
    
    # Analysis
    print("\n🔍 Analysis:")
    if perf1.get('cached') == False and perf2.get('cached') == True:
        print("  ✅ Cache decorator is working correctly!")
        print(f"  ⚡ Performance improvement: {(time1/time2):.1f}x faster")
        return True
    elif perf1.get('cached') is None and perf2.get('cached') is None:
        print("  ❌ No performance metadata found - cache decorator not working")
        return False
    else:
        print("  ⚠️  Unexpected caching behavior")
        print(f"     First request cached: {perf1.get('cached')}")
        print(f"     Second request cached: {perf2.get('cached')}")
        return False

if __name__ == "__main__":
    try:
        # Test if server is running
        response = requests.get("http://localhost:5001/health", timeout=2)
        if response.status_code != 200:
            print("❌ Server not responding on port 5001")
            exit(1)
        
        print("🚀 Server is running, starting cache test...")
        success = test_cache_decorator()
        
        if success:
            print("\n🏆 Cache implementation is working correctly!")
        else:
            print("\n❌ Cache implementation needs debugging")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server on port 5001")
        print("💡 Make sure the server is running: /Library/Developer/CommandLineTools/usr/bin/python3 run_server.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
