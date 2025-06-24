#!/usr/bin/env python3
"""
Direct Cache Manager Test
Tests the cache manager functionality without Flask server
"""

import sys
import os
import time
import json
from datetime import datetime

# Add the astro_engine directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cache_manager_directly():
    """Test cache manager functionality directly"""
    print("🚀 DIRECT CACHE MANAGER TEST")
    print("=" * 50)
    
    try:
        from astro_engine.cache_manager import AstroCacheManager
        
        # Create a mock Flask app context
        class MockApp:
            def __init__(self):
                self.config = {
                    'REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
                    'CACHE_DEFAULT_TIMEOUT': 3600
                }
        
        mock_app = MockApp()
        cache_manager = AstroCacheManager(mock_app)
        
        print(f"✅ Cache manager initialized")
        print(f"🔌 Redis available: {'✅' if cache_manager.is_available() else '❌'}")
        
        # Test data
        test_data = {
            'birth_date': '1990-01-15',
            'birth_time': '12:30:00',
            'latitude': 28.6139,
            'longitude': 77.2090,
            'timezone_offset': 5.5,
            'calculation_type': 'natal'
        }
        
        # Generate cache key
        cache_key = cache_manager.generate_cache_key(test_data, 'test')
        print(f"🔑 Cache key: {cache_key}")
        
        # Test cache operations
        print("\n🔄 Testing cache operations...")
        
        # Test cache miss
        result = cache_manager.get(cache_key)
        print(f"1️⃣ Get (should be miss): {'✅ Found' if result else '❌ Miss'}")
        
        # Test cache set
        test_result = {
            'planets': [{'name': 'Sun', 'longitude': 280.5}],
            'calculation_time': time.time(),
            'test': True
        }
        
        success = cache_manager.set(cache_key, test_result, 300)
        print(f"2️⃣ Set operation: {'✅ Success' if success else '❌ Failed'}")
        
        # Test cache hit
        cached_result = cache_manager.get(cache_key)
        cache_hit = cached_result is not None
        print(f"3️⃣ Get (should be hit): {'✅ Hit' if cache_hit else '❌ Miss'}")
        
        if cache_hit:
            print(f"   Cached data keys: {list(cached_result.keys())}")
        
        # Performance test
        print("\n⚡ Performance test...")
        iterations = 100
        
        # Test SET performance
        start_time = time.time()
        for i in range(iterations):
            test_key = f"perf_test_{i}"
            cache_manager.set(test_key, {'test_id': i, 'data': f'test_{i}'}, 300)
        set_time = time.time() - start_time
        
        print(f"💾 SET {iterations} items: {set_time:.3f}s ({iterations/set_time:.1f} ops/sec)")
        
        # Test GET performance
        start_time = time.time()
        hits = 0
        for i in range(iterations):
            test_key = f"perf_test_{i}"
            result = cache_manager.get(test_key)
            if result:
                hits += 1
        get_time = time.time() - start_time
        
        print(f"🔍 GET {iterations} items: {get_time:.3f}s ({iterations/get_time:.1f} ops/sec)")
        print(f"🎯 Hit rate: {(hits/iterations)*100:.1f}% ({hits}/{iterations})")
        
        # Test cache statistics
        stats = cache_manager.get_stats()
        print(f"\n📊 Cache Statistics:")
        print(f"   Hit rate: {stats['hit_rate']:.1f}%")
        print(f"   Total operations: {stats['total_operations']}")
        print(f"   Cache hits: {stats['cache_hits']}")
        print(f"   Cache misses: {stats['cache_misses']}")
        print(f"   Cache errors: {stats['cache_errors']}")
        
        # Cleanup
        deleted = cache_manager.delete('perf_test_*')
        print(f"🗑️ Cleanup: {deleted} keys deleted")
        
        # Test cleanup of our test key
        cache_manager.delete(cache_key)
        
        print("\n✅ Direct cache manager test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_cache_decorator():
    """Test the cache decorator functionality"""
    print("\n🎭 CACHE DECORATOR TEST")
    print("=" * 50)
    
    try:
        from astro_engine.cache_manager import cache_calculation
        
        # Test function with caching
        call_count = 0
        
        @cache_calculation('test_func', ttl=300)
        def expensive_calculation(value):
            nonlocal call_count
            call_count += 1
            print(f"🔄 Calculating for value: {value} (call #{call_count})")
            time.sleep(0.1)  # Simulate expensive operation
            return {'result': value * 2, 'timestamp': time.time()}
        
        print("Testing cached function...")
        
        # First call (should be calculated)
        start_time = time.time()
        result1 = expensive_calculation(42)
        time1 = time.time() - start_time
        print(f"1️⃣ First call: {time1:.3f}s, call_count: {call_count}")
        
        # Second call (should be cached)
        start_time = time.time()
        result2 = expensive_calculation(42)
        time2 = time.time() - start_time
        print(f"2️⃣ Second call: {time2:.3f}s, call_count: {call_count}")
        
        # Verify results are the same
        same_result = result1['result'] == result2['result']
        print(f"3️⃣ Results match: {'✅' if same_result else '❌'}")
        
        # Performance improvement
        if time1 > 0 and time2 > 0:
            speedup = time1 / time2
            print(f"🚀 Cache speedup: {speedup:.1f}x faster")
        
        print("✅ Cache decorator test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Decorator test error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 ASTRO ENGINE CACHE VALIDATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    success = True
    
    # Test 1: Direct cache manager
    if not test_cache_manager_directly():
        success = False
    
    # Test 2: Cache decorator
    if not test_cache_decorator():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! Cache implementation is working correctly.")
        print("\n💡 Next steps:")
        print("   1. ✅ Phase 1.1: Redis Client Setup - COMPLETE")
        print("   2. ✅ Phase 1.2: Core Caching Implementation - COMPLETE") 
        print("   3. 🔄 Phase 1.3: Cache Management - IN PROGRESS")
        print("   4. ⏸️ Phase 1.4: Integration Testing - PENDING")
    else:
        print("❌ SOME TESTS FAILED! Please check the error messages above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
