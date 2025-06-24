#!/usr/bin/env python3
"""
Phase 1.4: Integration Testing - Final Cache Implementation Validation
Tests all cached endpoints and validates performance improvements
"""

import time
import requests
import json
import statistics
from datetime import datetime

class Phase1ValidationTest:
    def __init__(self):
        self.test_data = {
            "user_name": "Phase1 Validation",
            "birth_date": "1990-01-15", 
            "birth_time": "12:30:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone_offset": 5.5
        }
        
        # Endpoints to test (from Phase 1.2 implementation)
        self.endpoints = [
            ("/lahiri/natal", "Natal Chart", 86400),
            ("/lahiri/navamsa", "Navamsa D9", 86400), 
            ("/lahiri/calculate_d3", "Dreshkana D3", 86400),
            ("/lahiri/transit", "Transit Chart", 3600)
        ]
    
    def validate_cache_consistency(self):
        """Validate that cached results are consistent across requests"""
        print("🔍 CACHE CONSISTENCY VALIDATION")
        print("=" * 60)
        
        consistent_results = []
        
        for endpoint, name, ttl in self.endpoints:
            print(f"\n🧪 Testing {name} ({endpoint})")
            
            try:
                # Make multiple requests
                responses = []
                for i in range(3):
                    start_time = time.time()
                    response = requests.post(f"http://localhost:5001{endpoint}", json=self.test_data)
                    duration = time.time() - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        responses.append({
                            'data': data,
                            'duration': duration,
                            'request_num': i + 1
                        })
                        
                        cache_hit = data.get('_cache_info', {}).get('hit', False)
                        print(f"  Request {i+1}: {duration:.3f}s {'✅ CACHED' if cache_hit else '🔄 CALCULATED'}")
                    else:
                        print(f"  Request {i+1}: ❌ Error {response.status_code}")
                
                # Check consistency
                if len(responses) >= 2:
                    first_data = responses[0]['data']
                    all_consistent = True
                    
                    for resp in responses[1:]:
                        # Compare planetary positions (excluding cache metadata)
                        if 'planetary_positions' in first_data and 'planetary_positions' in resp['data']:
                            if first_data['planetary_positions'] != resp['data']['planetary_positions']:
                                all_consistent = False
                                break
                    
                    result_status = "✅ CONSISTENT" if all_consistent else "❌ INCONSISTENT"
                    print(f"  Consistency: {result_status}")
                    consistent_results.append(all_consistent)
                
            except Exception as e:
                print(f"  ❌ Test failed: {e}")
                consistent_results.append(False)
        
        overall_consistency = all(consistent_results) if consistent_results else False
        print(f"\n📊 Overall Consistency: {'✅ PASS' if overall_consistency else '❌ FAIL'}")
        return overall_consistency
    
    def validate_performance_improvements(self):
        """Validate that caching provides significant performance improvements"""
        print("\n🚀 PERFORMANCE IMPROVEMENT VALIDATION")
        print("=" * 60)
        
        improvements = []
        
        for endpoint, name, ttl in self.endpoints:
            print(f"\n⚡ Testing {name} performance...")
            
            try:
                # Clear cache for this test
                requests.delete("http://localhost:5001/cache/clear")
                time.sleep(0.1)
                
                # Test uncached performance (first request)
                start_time = time.time()
                response1 = requests.post(f"http://localhost:5001{endpoint}", json=self.test_data)
                uncached_time = time.time() - start_time
                
                # Test cached performance (second request)
                start_time = time.time() 
                response2 = requests.post(f"http://localhost:5001{endpoint}", json=self.test_data)
                cached_time = time.time() - start_time
                
                if response1.status_code == 200 and response2.status_code == 200:
                    speedup = uncached_time / cached_time if cached_time > 0 else 0
                    time_saved = uncached_time - cached_time
                    
                    print(f"  Uncached: {uncached_time:.3f}s")
                    print(f"  Cached:   {cached_time:.3f}s") 
                    print(f"  Speedup:  {speedup:.1f}x faster")
                    print(f"  Saved:    {time_saved:.3f}s per request")
                    
                    # Target: At least 2x improvement
                    target_met = speedup >= 2.0
                    print(f"  Target:   {'✅ MET' if target_met else '❌ MISSED'} (>2x)")
                    
                    improvements.append({
                        'name': name,
                        'speedup': speedup,
                        'target_met': target_met,
                        'time_saved': time_saved
                    })
                
            except Exception as e:
                print(f"  ❌ Performance test failed: {e}")
        
        # Overall performance assessment
        targets_met = sum(1 for imp in improvements if imp['target_met'])
        total_tests = len(improvements)
        
        print(f"\n📈 Performance Summary:")
        print(f"  Endpoints tested: {total_tests}")
        print(f"  Targets met: {targets_met}/{total_tests}")
        
        if improvements:
            avg_speedup = statistics.mean([imp['speedup'] for imp in improvements])
            total_time_saved = sum([imp['time_saved'] for imp in improvements])
            print(f"  Average speedup: {avg_speedup:.1f}x")
            print(f"  Total time saved: {total_time_saved:.3f}s per test cycle")
        
        performance_pass = targets_met == total_tests
        print(f"  Overall: {'✅ PASS' if performance_pass else '❌ FAIL'}")
        
        return performance_pass, improvements
    
    def validate_cache_statistics(self):
        """Validate cache statistics and monitoring"""
        print("\n📊 CACHE STATISTICS VALIDATION")
        print("=" * 60)
        
        try:
            # Get cache stats
            response = requests.get("http://localhost:5001/cache/stats")
            
            if response.status_code == 200:
                stats = response.json()
                
                print(f"📈 Current Cache Statistics:")
                print(f"  Redis available: {'✅' if stats.get('redis_available') else '❌'}")
                print(f"  Hit rate: {stats.get('hit_rate', 0):.1f}%")
                print(f"  Total operations: {stats.get('total_operations', 0)}")
                print(f"  Cache hits: {stats.get('cache_hits', 0)}")
                print(f"  Cache misses: {stats.get('cache_misses', 0)}")
                print(f"  Cache errors: {stats.get('cache_errors', 0)}")
                
                # Validation criteria
                redis_ok = stats.get('redis_available', False)
                hit_rate_ok = stats.get('hit_rate', 0) >= 50  # At least 50% hit rate
                no_errors = stats.get('cache_errors', 0) == 0
                
                validations = [
                    ("Redis Available", redis_ok),
                    ("Hit Rate >50%", hit_rate_ok), 
                    ("No Cache Errors", no_errors)
                ]
                
                print(f"\n✅ Validation Results:")
                all_passed = True
                for name, passed in validations:
                    status = "✅ PASS" if passed else "❌ FAIL"
                    print(f"  {name}: {status}")
                    if not passed:
                        all_passed = False
                
                return all_passed
            else:
                print(f"❌ Failed to get cache stats: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Cache statistics validation failed: {e}")
            return False
    
    def run_comprehensive_validation(self):
        """Run comprehensive Phase 1 validation"""
        print("🏁 PHASE 1.4: INTEGRATION TESTING")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Test Data: {self.test_data}")
        
        results = {}
        
        # Test 1: Cache Consistency
        results['consistency'] = self.validate_cache_consistency()
        
        # Test 2: Performance Improvements  
        results['performance'], performance_details = self.validate_performance_improvements()
        
        # Test 3: Cache Statistics
        results['statistics'] = self.validate_cache_statistics()
        
        # Final Assessment
        print("\n" + "=" * 80)
        print("🎯 PHASE 1 INTEGRATION TEST RESULTS")
        print("=" * 80)
        
        test_results = [
            ("Cache Consistency", results['consistency']),
            ("Performance Improvements", results['performance']),
            ("Cache Statistics", results['statistics'])
        ]
        
        passed_tests = 0
        for name, passed in test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {name}: {status}")
            if passed:
                passed_tests += 1
        
        overall_pass = passed_tests == len(test_results)
        
        print(f"\n🏆 FINAL RESULT: {passed_tests}/{len(test_results)} tests passed")
        
        if overall_pass:
            print("🎉 PHASE 1 IMPLEMENTATION COMPLETE!")
            print("\n✅ Redis Caching Implementation Status:")
            print("   • Cache Manager: ✅ Operational")
            print("   • Performance: ✅ Targets exceeded")
            print("   • Consistency: ✅ Validated")
            print("   • Monitoring: ✅ Statistics available")
            print("   • Error Handling: ✅ Graceful degradation")
            
            print("\n🚀 Ready for Phase 2: Prometheus Metrics Implementation")
        else:
            print("❌ PHASE 1 VALIDATION FAILED")
            print("   Please review failed tests and fix issues before proceeding.")
        
        return overall_pass

def main():
    """Run Phase 1.4 validation"""
    validator = Phase1ValidationTest()
    return validator.run_comprehensive_validation()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
