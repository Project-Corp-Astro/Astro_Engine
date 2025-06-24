#!/usr/bin/env python3
"""
COMPREHENSIVE DEPLOYMENT VALIDATION SCRIPT
Tests all departments and features for 100% deployment readiness
"""

import requests
import json
import time
import sys
import subprocess
from datetime import datetime

def run_test(test_name, test_func):
    """Run a test and record results"""
    print(f"🧪 Testing: {test_name}")
    try:
        start_time = time.time()
        result = test_func()
        duration = time.time() - start_time
        if result:
            print(f"   ✅ PASS ({duration:.3f}s)")
            return True, duration
        else:
            print(f"   ❌ FAIL ({duration:.3f}s)")
            return False, duration
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False, 0

def test_server_health():
    """Test server health endpoint"""
    try:
        response = requests.get("http://localhost:5000/health", timeout=10)
        return response.status_code == 200
    except:
        return False

def test_cache_system():
    """Test Redis caching system"""
    try:
        response = requests.get("http://localhost:5000/cache/stats", timeout=10)
        return response.status_code == 200 and "redis_available" in response.text
    except:
        return False

def test_metrics_system():
    """Test Prometheus metrics"""
    try:
        response = requests.get("http://localhost:5000/metrics", timeout=10)
        return response.status_code == 200 and "astro_engine" in response.text
    except:
        return False

def test_logging_system():
    """Test structured logging"""
    try:
        response = requests.get("http://localhost:5000/logging/status", timeout=10)
        return response.status_code == 200
    except:
        return False

def test_natal_calculation():
    """Test natal chart calculation"""
    try:
        test_data = {
            "birth_date": "1990-05-15",
            "birth_time": "14:30",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone": "Asia/Kolkata"
        }
        response = requests.post("http://localhost:5000/lahiri/natal", 
                               json=test_data, timeout=15)
        return response.status_code == 200
    except:
        return False

def test_navamsa_calculation():
    """Test navamsa chart calculation"""
    try:
        test_data = {
            "birth_date": "1990-05-15",
            "birth_time": "14:30",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone": "Asia/Kolkata"
        }
        response = requests.post("http://localhost:5000/lahiri/navamsa", 
                               json=test_data, timeout=15)
        return response.status_code == 200
    except:
        return False

def test_cache_performance():
    """Test cache hit/miss performance"""
    try:
        test_data = {
            "birth_date": "1990-05-15",
            "birth_time": "14:30",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone": "Asia/Kolkata"
        }
        
        # First call (cache miss)
        start = time.time()
        response1 = requests.post("http://localhost:5000/lahiri/natal", 
                                json=test_data, timeout=15)
        first_call_time = time.time() - start
        
        # Second call (cache hit)
        start = time.time()
        response2 = requests.post("http://localhost:5000/lahiri/natal", 
                                json=test_data, timeout=15)
        second_call_time = time.time() - start
        
        # Cache should make second call faster
        return (response1.status_code == 200 and 
                response2.status_code == 200 and 
                second_call_time < first_call_time)
    except:
        return False

def test_error_handling():
    """Test error handling with invalid data"""
    try:
        # Test with invalid data
        invalid_data = {"invalid": "data"}
        response = requests.post("http://localhost:5000/lahiri/natal", 
                               json=invalid_data, timeout=10)
        # Should return error but not crash
        return response.status_code in [400, 422, 500]
    except:
        return False

def test_concurrent_requests():
    """Test handling multiple concurrent requests"""
    try:
        test_data = {
            "birth_date": "1990-05-15",
            "birth_time": "14:30",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone": "Asia/Kolkata"
        }
        
        # Make 5 concurrent requests
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for i in range(5):
                future = executor.submit(
                    requests.post, 
                    "http://localhost:5000/lahiri/natal",
                    json=test_data,
                    timeout=20
                )
                futures.append(future)
            
            # Check all requests succeeded
            results = [future.result().status_code == 200 for future in futures]
            return all(results)
    except:
        return False

def test_file_structure():
    """Test deployment file structure"""
    try:
        required_files = [
            "astro_engine/app.py",
            "Dockerfile",
            "docker-compose.yml",
            "requirements.txt",
            "requirements-prod.txt",
            ".env.production"
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                return False
        return True
    except:
        return False

def test_google_cloud_deployment_files():
    """Test Google Cloud deployment configuration"""
    try:
        gcp_files = [
            "deployment/google-cloud/deploy-gcp.sh",
            "deployment/google-cloud/Dockerfile.gcp",
            "deployment/google-cloud/cloudbuild.yaml",
            "deployment/google-cloud/gcp-config.env"
        ]
        
        for file_path in gcp_files:
            if not os.path.exists(file_path):
                return False
        return True
    except:
        return False

def main():
    print("🚀 COMPREHENSIVE ASTRO ENGINE DEPLOYMENT VALIDATION")
    print("=" * 60)
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Target URL: http://localhost:5000")
    print()
    
    # Test suite
    tests = [
        ("Server Health Check", test_server_health),
        ("File Structure Validation", test_file_structure),
        ("Google Cloud Deployment Files", test_google_cloud_deployment_files),
        ("Cache System (Redis)", test_cache_system),
        ("Metrics System (Prometheus)", test_metrics_system),
        ("Logging System (Structured)", test_logging_system),
        ("Natal Chart Calculation", test_natal_calculation),
        ("Navamsa Chart Calculation", test_navamsa_calculation),
        ("Cache Performance", test_cache_performance),
        ("Error Handling", test_error_handling),
        ("Concurrent Request Handling", test_concurrent_requests),
    ]
    
    # Run all tests
    passed = 0
    total = len(tests)
    total_duration = 0
    
    for test_name, test_func in tests:
        success, duration = run_test(test_name, test_func)
        total_duration += duration
        if success:
            passed += 1
    
    print()
    print("=" * 60)
    print("📊 FINAL DEPLOYMENT VALIDATION RESULTS")
    print("=" * 60)
    print(f"✅ Tests Passed: {passed}/{total} ({(passed/total)*100:.1f}%)")
    print(f"⏱️  Total Duration: {total_duration:.2f} seconds")
    
    if passed == total:
        print("🎉 RESULT: 100% DEPLOYMENT READY! 🚀")
        print("✅ All systems operational and ready for production deployment")
        print("✅ Google Cloud deployment files verified")
        print("✅ Performance optimization features working")
        print("✅ Error handling and concurrency tested")
    else:
        print(f"⚠️  RESULT: {(passed/total)*100:.1f}% Ready")
        print(f"❌ {total-passed} tests failed - review issues before deployment")
    
    print()
    print("🌟 Next Steps:")
    print("   1. Review any failed tests above")
    print("   2. Deploy to Google Cloud using: deployment/google-cloud/deploy-gcp.sh")
    print("   3. Monitor performance with Prometheus metrics")
    print("   4. Check structured logs for any issues")
    
    return passed == total

if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    success = main()
    sys.exit(0 if success else 1)
