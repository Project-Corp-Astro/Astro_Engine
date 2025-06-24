#!/usr/bin/env python3
"""
Redis Connection Test for Astro Engine
Tests Redis connectivity and cache manager functionality
"""

import os
import sys
import time
from datetime import datetime

# Add the astro_engine directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from astro_engine.cache_manager import AstroCacheManager
    import redis
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


def test_redis_connection():
    """Test basic Redis connectivity"""
    print("🔄 Testing Redis connection...")
    
    try:
        # Test direct Redis connection
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        client = redis.Redis.from_url(redis_url, decode_responses=True)
        
        # Test ping
        response = client.ping()
        if response:
            print(f"✅ Redis ping successful: {redis_url}")
        else:
            print(f"❌ Redis ping failed: {redis_url}")
            return False
            
        # Test basic operations
        test_key = "astro_engine:test"
        test_value = {"test": True, "timestamp": str(datetime.utcnow())}
        
        # Set test value
        client.setex(test_key, 60, str(test_value))
        print(f"✅ Redis SET successful: {test_key}")
        
        # Get test value
        retrieved = client.get(test_key)
        if retrieved:
            print(f"✅ Redis GET successful: {retrieved}")
        else:
            print("❌ Redis GET failed")
            return False
        
        # Delete test key
        client.delete(test_key)
        print(f"✅ Redis DELETE successful: {test_key}")
        
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Redis connection error: {e}")
        print("💡 Make sure Redis is running on localhost:6379")
        print("   - Install Redis: brew install redis (macOS) or apt install redis (Ubuntu)")
        print("   - Start Redis: redis-server")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_cache_manager():
    """Test AstroCacheManager functionality"""
    print("\n🔄 Testing AstroCacheManager...")
    
    try:
        # Create a mock Flask app context
        class MockApp:
            def __init__(self):
                self.config = {
                    'REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
                    'CACHE_DEFAULT_TIMEOUT': 3600
                }
        
        mock_app = MockApp()
        cache_manager = AstroCacheManager(mock_app)
        
        if not cache_manager.is_available():
            print("❌ Cache manager reports Redis as unavailable")
            return False
        
        print("✅ Cache manager initialized successfully")
        
        # Test cache key generation
        test_data = {
            'birth_date': '1990-01-01',
            'birth_time': '12:00:00',
            'latitude': 28.6139,
            'longitude': 77.2090,
            'timezone_offset': 5.5,
            'ayanamsa': 'lahiri'
        }
        
        cache_key = cache_manager.generate_cache_key(test_data, 'test')
        print(f"✅ Cache key generated: {cache_key}")
        
        # Test cache operations
        test_result = {
            'planets': [{'name': 'Sun', 'longitude': 280.5}],
            'houses': [{'number': 1, 'longitude': 45.0}],
            'calculation_time': 0.125
        }
        
        # Set cache
        success = cache_manager.set(cache_key, test_result, 300)  # 5 minutes TTL
        if success:
            print("✅ Cache SET operation successful")
        else:
            print("❌ Cache SET operation failed")
            return False
        
        # Get from cache
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            print("✅ Cache GET operation successful")
            print(f"   Cached data: {list(cached_result.keys())}")
        else:
            print("❌ Cache GET operation failed")
            return False
        
        # Test cache stats
        stats = cache_manager.get_stats()
        print("✅ Cache statistics:")
        print(f"   Hit rate: {stats['hit_rate']:.1f}%")
        print(f"   Total operations: {stats['total_operations']}")
        print(f"   Cache hits: {stats['cache_hits']}")
        print(f"   Cache misses: {stats['cache_misses']}")
        
        # Clean up test data
        deleted = cache_manager.delete(cache_key)
        print(f"✅ Cleanup completed: {deleted} keys deleted")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache manager test error: {e}")
        return False


def test_performance():
    """Test cache performance with multiple operations"""
    print("\n🔄 Testing cache performance...")
    
    try:
        class MockApp:
            def __init__(self):
                self.config = {
                    'REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
                    'CACHE_DEFAULT_TIMEOUT': 3600
                }
        
        mock_app = MockApp()
        cache_manager = AstroCacheManager(mock_app)
        
        if not cache_manager.is_available():
            print("❌ Cache not available for performance test")
            return False
        
        # Performance test parameters
        num_operations = 100
        test_data_base = {
            'birth_date': '1990-01-01',
            'birth_time': '12:00:00',
            'latitude': 28.6139,
            'longitude': 77.2090,
            'timezone_offset': 5.5,
            'ayanamsa': 'lahiri'
        }
        
        # Test SET performance
        print(f"Testing {num_operations} SET operations...")
        start_time = time.time()
        
        for i in range(num_operations):
            test_data = test_data_base.copy()
            test_data['test_id'] = i
            cache_key = cache_manager.generate_cache_key(test_data, 'perf_test')
            
            test_result = {
                'test_id': i,
                'data': f'test_data_{i}',
                'timestamp': time.time()
            }
            
            cache_manager.set(cache_key, test_result, 300)
        
        set_time = time.time() - start_time
        print(f"✅ SET performance: {num_operations} ops in {set_time:.3f}s ({num_operations/set_time:.1f} ops/sec)")
        
        # Test GET performance
        print(f"Testing {num_operations} GET operations...")
        start_time = time.time()
        cache_hits = 0
        
        for i in range(num_operations):
            test_data = test_data_base.copy()
            test_data['test_id'] = i
            cache_key = cache_manager.generate_cache_key(test_data, 'perf_test')
            
            result = cache_manager.get(cache_key)
            if result:
                cache_hits += 1
        
        get_time = time.time() - start_time
        hit_rate = (cache_hits / num_operations) * 100
        
        print(f"✅ GET performance: {num_operations} ops in {get_time:.3f}s ({num_operations/get_time:.1f} ops/sec)")
        print(f"✅ Cache hit rate: {hit_rate:.1f}% ({cache_hits}/{num_operations})")
        
        # Cleanup
        deleted = cache_manager.delete('perf_test:*')
        print(f"✅ Cleanup: {deleted} test keys deleted")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Astro Engine Redis Connection Test")
    print("=" * 50)
    
    success = True
    
    # Test 1: Basic Redis connection
    if not test_redis_connection():
        success = False
    
    # Test 2: Cache manager functionality
    if not test_cache_manager():
        success = False
    
    # Test 3: Performance testing
    if not test_performance():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Redis caching is ready for Astro Engine.")
        print("\n💡 Next steps:")
        print("   1. Apply caching decorators to calculation functions")
        print("   2. Monitor cache hit rates in production")
        print("   3. Tune TTL values based on usage patterns")
    else:
        print("❌ Some tests failed. Please check Redis installation and configuration.")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure Redis is installed and running")
        print("   2. Check Redis connection parameters")
        print("   3. Verify network connectivity")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
