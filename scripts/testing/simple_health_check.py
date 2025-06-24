#!/usr/bin/env python3
"""
Simple Astro Engine Health Check
Tests the actual working endpoints
"""

import requests
import json
import time
from datetime import datetime

def test_endpoint(url, description, method='GET', data=None):
    """Test a single endpoint"""
    try:
        if method == 'POST' and data:
            response = requests.post(url, json=data, timeout=10)
        else:
            response = requests.get(url, timeout=10)
        
        status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
        print(f"{status} {description}: {response.status_code} ({len(response.text)} bytes)")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ FAIL {description}: {str(e)}")
        return False

def main():
    base_url = "http://localhost:5001"
    print("🌟 ASTRO ENGINE HEALTH CHECK")
    print("=" * 50)
    
    # Test data for calculations
    test_data = {
        "user_name": "Test User",
        "birth_date": "1990-01-01", 
        "birth_time": "12:00:00",
        "latitude": 28.7041,
        "longitude": 77.1025,
        "timezone_offset": 5.5
    }
    
    tests = [
        # Core Infrastructure
        (f"{base_url}/health", "Health Check", 'GET', None),
        
        # Calculation Endpoints
        (f"{base_url}/lahiri/natal", "Natal Chart (Lahiri)", 'POST', test_data),
        (f"{base_url}/lahiri/navamsa", "Navamsa Chart (Lahiri)", 'POST', test_data),
        (f"{base_url}/lahiri/calculate_d3", "D3 Chart (Lahiri)", 'POST', test_data),
        (f"{base_url}/lahiri/transit", "Transit Chart (Lahiri)", 'POST', test_data),
        
        # Cache Management
        (f"{base_url}/cache/stats", "Cache Statistics", 'GET', None),
        
        # Metrics & Monitoring
        (f"{base_url}/metrics", "Prometheus Metrics", 'GET', None),
        (f"{base_url}/metrics/json", "Metrics JSON", 'GET', None),
        (f"{base_url}/metrics/performance", "Performance Summary", 'GET', None),
        
        # Logging
        (f"{base_url}/logging/status", "Logging Status", 'GET', None),
        
        # Task Management
        (f"{base_url}/tasks/available", "Available Tasks", 'GET', None),
        (f"{base_url}/tasks/queue/stats", "Queue Stats", 'GET', None),
    ]
    
    passed = 0
    total = len(tests)
    
    for url, description, method, data in tests:
        if test_endpoint(url, description, method, data):
            passed += 1
        time.sleep(0.1)  # Small delay between requests
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        return 0
    elif passed >= total * 0.8:
        print("⚠️  MOSTLY OPERATIONAL (some issues)")
        return 1
    else:
        print("❌ SIGNIFICANT ISSUES DETECTED")
        return 2

if __name__ == "__main__":
    exit(main())
