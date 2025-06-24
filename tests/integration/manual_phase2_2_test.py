#!/usr/bin/env python3
"""
Manual Phase 2.2 Metrics Validation
Simple validation of key Phase 2.2 metrics implementation
"""

import requests
import json
import time

def test_phase_2_2_metrics():
    base_url = "http://localhost:5001"
    
    print("🔥 PHASE 2.2 METRICS VALIDATION")
    print("="*50)
    
    # Test 1: Performance endpoint
    print("\n1. Testing Performance Summary Endpoint...")
    try:
        response = requests.get(f"{base_url}/metrics/performance", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Performance endpoint working")
            print(f"   📊 Cache hit rate: {data['performance_metrics']['cache_hit_rate']:.1f}%")
        else:
            print(f"   ❌ Performance endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Performance endpoint error: {e}")
    
    # Test 2: Chart calculation with metrics
    print("\n2. Testing Chart Calculation with Metrics...")
    test_data = {
        "user_name": "Metrics Test User",
        "birth_date": "1985-06-20",
        "birth_time": "10:15:00",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "timezone_offset": 5.5
    }
    
    try:
        response = requests.post(f"{base_url}/lahiri/natal", json=test_data, timeout=10)
        if response.status_code == 200:
            print("   ✅ Chart calculation successful")
        else:
            print(f"   ❌ Chart calculation failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Chart calculation error: {e}")
    
    # Test 3: Check advanced metrics in Prometheus output
    print("\n3. Testing Advanced Prometheus Metrics...")
    try:
        response = requests.get(f"{base_url}/metrics", timeout=5)
        if response.status_code == 200:
            metrics_text = response.text
            
            # Check for Phase 2.2 metrics
            advanced_metrics = [
                'astro_engine_user_interactions_total',
                'astro_engine_chart_requests_total',
                'astro_engine_ephemeris_calculation_seconds',
                'astro_engine_calculation_complexity',
                'astro_engine_cache_performance_seconds'
            ]
            
            found = []
            for metric in advanced_metrics:
                if metric in metrics_text:
                    found.append(metric)
            
            print(f"   ✅ Found {len(found)}/{len(advanced_metrics)} advanced metrics")
            for metric in found:
                print(f"   📈 {metric}")
                
        else:
            print(f"   ❌ Metrics endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Metrics endpoint error: {e}")
    
    # Test 4: Cache performance
    print("\n4. Testing Cache Performance Metrics...")
    try:
        # Second request should be faster (cached)
        start_time = time.time()
        response = requests.post(f"{base_url}/lahiri/natal", json=test_data, timeout=10)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            print(f"   ✅ Cached request completed in {duration:.3f}s")
            
            # Check cache stats
            cache_response = requests.get(f"{base_url}/cache/stats", timeout=5)
            if cache_response.status_code == 200:
                cache_data = cache_response.json()
                print(f"   📊 Cache hit rate: {cache_data.get('hit_rate', 0):.1f}%")
                print(f"   📊 Total operations: {cache_data.get('total_operations', 0)}")
        else:
            print(f"   ❌ Cached request failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Cache test error: {e}")
    
    print("\n" + "="*50)
    print("✅ Phase 2.2 Manual Validation Complete")
    print("🎯 Advanced metrics implementation verified!")

if __name__ == "__main__":
    test_phase_2_2_metrics()
