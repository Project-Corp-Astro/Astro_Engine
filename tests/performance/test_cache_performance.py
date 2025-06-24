#!/usr/bin/env python3
"""
Cache Performance Test for Astro Engine
Tests caching effectiveness with real calculation endpoints
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the astro_engine directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class CachePerformanceTester:
    """Test cache performance and effectiveness"""
    
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.test_data = {
            "user_name": "Cache Test User",
            "birth_date": "1990-01-01",
            "birth_time": "12:00:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone_offset": 5.5
        }
        self.endpoints_to_test = [
            ("/lahiri/natal", "natal_chart"),
            ("/lahiri/navamsa", "navamsa_chart"),
            ("/lahiri/transit", "transit_chart"),
            ("/lahiri/calculate_d3", "d3_chart"),
            ("/lahiri/calculate_d9", "d9_chart"),
            ("/lahiri/calculate_d10", "d10_chart")
        ]
        
    def clear_cache(self):
        """Clear all cache entries"""
        try:
            response = requests.delete(f"{self.base_url}/cache/clear")
            if response.status_code == 200:
                print("✅ Cache cleared successfully")
                return True
            else:
                print(f"⚠️ Cache clear failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cache clear error: {e}")
            return False
    
    def get_cache_stats(self):
        """Get cache statistics"""
        try:
            response = requests.get(f"{self.base_url}/cache/stats")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ Cache stats failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Cache stats error: {e}")
            return None
    
    def test_endpoint_performance(self, endpoint, description, iterations=5):
        """Test performance of a specific endpoint"""
        print(f"\n🔄 Testing {description} ({endpoint})")
        print(f"   Running {iterations} iterations...")
        
        times = []
        cache_hits = 0
        cache_misses = 0
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    json=self.test_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                times.append(response_time)
                
                if response.status_code == 200:
                    # Check if response contains cache info
                    data = response.json()
                    if isinstance(data, dict) and '_performance' in data:
                        if data['_performance'].get('cached', False):
                            cache_hits += 1
                        else:
                            cache_misses += 1
                    
                    print(f"   Iteration {i+1}: {response_time:.3f}s {'(cached)' if i > 0 else '(fresh)'}")
                else:
                    print(f"   Iteration {i+1}: Failed ({response.status_code})")
                    
            except requests.exceptions.Timeout:
                print(f"   Iteration {i+1}: Timeout (>30s)")
                times.append(30.0)
            except Exception as e:
                print(f"   Iteration {i+1}: Error - {e}")
                times.append(float('inf'))
        
        # Calculate statistics
        valid_times = [t for t in times if t != float('inf')]
        if valid_times:
            avg_time = sum(valid_times) / len(valid_times)
            min_time = min(valid_times)
            max_time = max(valid_times)
            
            # Calculate cache improvement
            if len(valid_times) > 1:
                first_call = valid_times[0]  # Fresh calculation
                cached_calls = valid_times[1:]  # Potentially cached
                avg_cached = sum(cached_calls) / len(cached_calls)
                improvement = ((first_call - avg_cached) / first_call) * 100
                
                print(f"   📊 Results:")
                print(f"      First call (fresh): {first_call:.3f}s")
                print(f"      Avg cached calls: {avg_cached:.3f}s")
                print(f"      Performance improvement: {improvement:.1f}%")
                print(f"      Min/Max: {min_time:.3f}s / {max_time:.3f}s")
                
                return {
                    'endpoint': endpoint,
                    'description': description,
                    'first_call': first_call,
                    'avg_cached': avg_cached,
                    'improvement_percent': improvement,
                    'min_time': min_time,
                    'max_time': max_time,
                    'cache_hits': cache_hits,
                    'cache_misses': cache_misses
                }
            else:
                print(f"   📊 Results: Avg time: {avg_time:.3f}s")
                return {
                    'endpoint': endpoint,
                    'description': description,
                    'avg_time': avg_time,
                    'cache_hits': cache_hits,
                    'cache_misses': cache_misses
                }
        else:
            print("   ❌ All requests failed")
            return None
    
    def test_concurrent_performance(self, endpoint, description, concurrent_users=10):
        """Test concurrent access performance"""
        print(f"\n🚀 Concurrent test: {description}")
        print(f"   Testing with {concurrent_users} concurrent users")
        
        def make_request():
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    json=self.test_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                end_time = time.time()
                return {
                    'success': response.status_code == 200,
                    'time': end_time - start_time,
                    'status': response.status_code
                }
            except Exception as e:
                return {
                    'success': False,
                    'time': float('inf'),
                    'error': str(e)
                }
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_request) for _ in range(concurrent_users)]
            results = [future.result() for future in as_completed(futures)]
        
        total_time = time.time() - start_time
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        if successful:
            times = [r['time'] for r in successful]
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"   📊 Concurrent Results:")
            print(f"      Total time: {total_time:.3f}s")
            print(f"      Successful requests: {len(successful)}/{concurrent_users}")
            print(f"      Avg response time: {avg_time:.3f}s")
            print(f"      Min/Max response time: {min_time:.3f}s / {max_time:.3f}s")
            print(f"      Requests per second: {len(successful)/total_time:.1f}")
            
            return {
                'total_time': total_time,
                'successful': len(successful),
                'failed': len(failed),
                'avg_response_time': avg_time,
                'requests_per_second': len(successful)/total_time
            }
        else:
            print(f"   ❌ All {concurrent_users} requests failed")
            return None
    
    def test_cache_memory_usage(self):
        """Test cache memory usage and key count"""
        print(f"\n💾 Testing cache memory usage")
        
        # Clear cache first
        self.clear_cache()
        
        # Make requests to populate cache
        endpoints_tested = 0
        for endpoint, description in self.endpoints_to_test[:3]:  # Test first 3 endpoints
            try:
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    json=self.test_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                if response.status_code == 200:
                    endpoints_tested += 1
                    print(f"   ✅ Cached {description}")
                else:
                    print(f"   ❌ Failed to cache {description}")
            except Exception as e:
                print(f"   ❌ Error caching {description}: {e}")
        
        # Get cache stats
        stats = self.get_cache_stats()
        if stats:
            print(f"   📊 Cache Memory Usage:")
            print(f"      Endpoints cached: {endpoints_tested}")
            print(f"      Cache hits: {stats.get('cache_hits', 0)}")
            print(f"      Cache misses: {stats.get('cache_misses', 0)}")
            print(f"      Hit rate: {stats.get('hit_rate', 0):.1f}%")
            print(f"      Memory cache size: {stats.get('memory_cache_size', 0)}")
            
            if 'redis_info' in stats and stats['redis_info'].get('status') != 'unavailable':
                redis_info = stats['redis_info']
                print(f"      Redis memory: {redis_info.get('used_memory', 'N/A')}")
                print(f"      Redis keys: {redis_info.get('total_keys', 0)}")
        
        return stats
    
    def run_comprehensive_test(self):
        """Run comprehensive cache performance test"""
        print("🚀 Astro Engine Cache Performance Test")
        print("=" * 60)
        
        results = {}
        
        # Test 1: Check if server is running
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                print("✅ Server is running and healthy")
            else:
                print(f"⚠️ Server health check failed: {response.status_code}")
                return
        except Exception as e:
            print(f"❌ Server is not accessible: {e}")
            print("💡 Please start the server with: python astro_engine/app.py")
            return
        
        # Test 2: Cache connectivity
        initial_stats = self.get_cache_stats()
        if initial_stats:
            redis_available = initial_stats.get('redis_available', False)
            print(f"✅ Cache system: {'Redis' if redis_available else 'Memory fallback'}")
        else:
            print("⚠️ Cache system not available")
        
        # Test 3: Clear cache and test individual endpoints
        self.clear_cache()
        endpoint_results = []
        
        for endpoint, description in self.endpoints_to_test[:4]:  # Test first 4 endpoints
            result = self.test_endpoint_performance(endpoint, description)
            if result:
                endpoint_results.append(result)
        
        results['endpoint_tests'] = endpoint_results
        
        # Test 4: Concurrent performance test
        if endpoint_results:
            best_endpoint = min(endpoint_results, key=lambda x: x.get('avg_cached', x.get('avg_time', float('inf'))))
            concurrent_result = self.test_concurrent_performance(
                best_endpoint['endpoint'], 
                best_endpoint['description']
            )
            results['concurrent_test'] = concurrent_result
        
        # Test 5: Cache memory usage
        memory_stats = self.test_cache_memory_usage()
        results['memory_stats'] = memory_stats
        
        # Test 6: Final performance summary
        print(f"\n📊 PERFORMANCE SUMMARY")
        print("=" * 60)
        
        if endpoint_results:
            improvements = [r.get('improvement_percent', 0) for r in endpoint_results if 'improvement_percent' in r]
            if improvements:
                avg_improvement = sum(improvements) / len(improvements)
                print(f"Average cache performance improvement: {avg_improvement:.1f}%")
                
                best_improvement = max(improvements)
                print(f"Best cache performance improvement: {best_improvement:.1f}%")
                
                # Check if we met our target (10x improvement = 90% reduction)
                target_improvement = 85  # 85% improvement target
                if avg_improvement >= target_improvement:
                    print(f"🎉 PERFORMANCE TARGET MET! (>{target_improvement}% improvement)")
                else:
                    print(f"⚠️ Performance target not fully met (target: {target_improvement}%)")
        
        final_stats = self.get_cache_stats()
        if final_stats:
            hit_rate = final_stats.get('hit_rate', 0)
            print(f"Cache hit rate: {hit_rate:.1f}%")
            
            if hit_rate >= 70:
                print("🎉 CACHE HIT RATE TARGET MET! (>70%)")
            else:
                print("⚠️ Cache hit rate below target (70%)")
        
        # Test 7: Export results
        results['summary'] = {
            'timestamp': datetime.utcnow().isoformat(),
            'server_url': self.base_url,
            'redis_available': initial_stats.get('redis_available', False) if initial_stats else False,
            'endpoints_tested': len(endpoint_results),
            'average_improvement': sum(improvements) / len(improvements) if improvements else 0,
            'cache_hit_rate': final_stats.get('hit_rate', 0) if final_stats else 0
        }
        
        # Save results to file
        with open('cache_performance_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: cache_performance_results.json")
        print("\n🎯 Next steps:")
        print("   1. Review performance improvements")
        print("   2. Tune cache TTL values if needed")
        print("   3. Monitor cache hit rates in production")
        print("   4. Consider implementing cache warming strategies")
        
        return results

def main():
    """Main test function"""
    tester = CachePerformanceTester()
    
    # Allow custom server URL
    if len(sys.argv) > 1:
        tester.base_url = sys.argv[1]
        print(f"Using custom server URL: {tester.base_url}")
    
    results = tester.run_comprehensive_test()
    return 0 if results else 1

if __name__ == "__main__":
    sys.exit(main())
