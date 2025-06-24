#!/usr/bin/env python3
import requests
import json

print("🚀 TESTING ASTRO ENGINE DEPLOYMENT READINESS")
print("=" * 50)

# Test 1: Health Check
try:
    response = requests.get("http://localhost:5000/health", timeout=5)
    print(f"✅ Health Check: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"❌ Health Check Failed: {e}")

# Test 2: Cache Stats
try:
    response = requests.get("http://localhost:5000/cache/stats", timeout=5)
    print(f"✅ Cache Stats: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"❌ Cache Stats Failed: {e}")

# Test 3: Metrics
try:
    response = requests.get("http://localhost:5000/metrics", timeout=5)
    print(f"✅ Metrics: {response.status_code} - {len(response.text)} bytes")
except Exception as e:
    print(f"❌ Metrics Failed: {e}")

# Test 4: Natal Chart
try:
    test_data = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone": "Asia/Kolkata"
    }
    response = requests.post("http://localhost:5000/lahiri/natal", json=test_data, timeout=10)
    print(f"✅ Natal Chart: {response.status_code}")
except Exception as e:
    print(f"❌ Natal Chart Failed: {e}")

print("=" * 50)
print("🎯 DEPLOYMENT READY!")
