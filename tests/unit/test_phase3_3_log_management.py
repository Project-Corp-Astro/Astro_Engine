#!/usr/bin/env python3
"""
Phase 3.3: Log Management Validation Test
Tests log rotation, levels, aggregation, and documentation features
"""

import os
import sys
import time
import json
import requests
import logging
from datetime import datetime

# Add project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_log_management():
    """Comprehensive test of log management features"""
    
    print("🔥 PHASE 3.3: LOG MANAGEMENT VALIDATION")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    results = {
        'tests_passed': 0,
        'tests_failed': 0,
        'total_tests': 0
    }
    
    def run_test(test_name, test_func):
        """Run a test and track results"""
        results['total_tests'] += 1
        try:
            success = test_func()
            if success:
                print(f"✅ {test_name}: PASSED")
                results['tests_passed'] += 1
            else:
                print(f"❌ {test_name}: FAILED")
                results['tests_failed'] += 1
            return success
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results['tests_failed'] += 1
            return False
    
    # Test 1: Enhanced Logging Status
    def test_enhanced_logging_status():
        print("📊 Testing enhanced logging configuration...")
        response = requests.get(f"{base_url}/logging/status")
        if response.status_code == 200:
            data = response.json()
            config = data.get('configuration', {})
            required_fields = ['structured_logging', 'log_level', 'log_directory', 
                             'rotation_enabled', 'max_log_size_mb', 'backup_count']
            
            for field in required_fields:
                if field not in config:
                    print(f"   Missing field: {field}")
                    return False
            
            print(f"   Log directory: {config.get('log_directory')}")
            print(f"   Rotation enabled: {config.get('rotation_enabled')}")
            print(f"   Max log size: {config.get('max_log_size_mb')}MB")
            print(f"   Backup count: {config.get('backup_count')}")
            return True
        return False
    
    # Test 2: Log Level Management
    def test_log_level_management():
        print("🎚️ Testing log level management...")
        
        # Get current levels
        response = requests.get(f"{base_url}/logging/levels")
        if response.status_code != 200:
            return False
        
        levels_data = response.json()
        original_level = levels_data.get('root')
        print(f"   Original level: {original_level}")
        
        # Test setting different levels
        for level in ['DEBUG', 'WARNING', 'ERROR']:
            response = requests.post(f"{base_url}/logging/levels", 
                                   json={'level': level})
            if response.status_code != 200:
                print(f"   Failed to set level: {level}")
                return False
            
            data = response.json()
            if data.get('new_level') != level:
                print(f"   Level not set correctly: expected {level}, got {data.get('new_level')}")
                return False
            
            print(f"   ✓ Level set to: {level}")
        
        # Restore original level
        requests.post(f"{base_url}/logging/levels", json={'level': original_level})
        return True
    
    # Test 3: Log Testing Functionality
    def test_log_testing():
        print("🧪 Testing log level functionality...")
        response = requests.get(f"{base_url}/logging/test")
        if response.status_code == 200:
            data = response.json()
            tests_run = data.get('tests_run', [])
            expected_tests = ['debug', 'info', 'warning', 'error', 'structured_data']
            
            for test in expected_tests:
                if test not in tests_run:
                    print(f"   Missing test: {test}")
                    return False
            
            print(f"   Tests completed: {len(tests_run)}")
            print(f"   Correlation ID: {data.get('correlation_id', 'N/A')[:8]}...")
            return True
        return False
    
    # Test 4: Log Aggregation
    def test_log_aggregation():
        print("📋 Testing log aggregation...")
        response = requests.get(f"{base_url}/logging/aggregation")
        if response.status_code == 200:
            data = response.json()
            sample_logs = data.get('sample_logs', [])
            
            if len(sample_logs) != 5:
                print(f"   Expected 5 sample logs, got {len(sample_logs)}")
                return False
            
            # Verify log structure
            for i, log in enumerate(sample_logs):
                required_fields = ['timestamp', 'level', 'component', 'message', 'metrics']
                for field in required_fields:
                    if field not in log:
                        print(f"   Missing field in log {i+1}: {field}")
                        return False
            
            print(f"   Generated {len(sample_logs)} structured log entries")
            print(f"   Aggregation ready: {data.get('aggregation_ready')}")
            return True
        return False
    
    # Test 5: Log File Creation
    def test_log_file_creation():
        print("📁 Testing log file creation...")
        
        # Make some requests to generate logs
        for i in range(3):
            requests.get(f"{base_url}/health")
            time.sleep(0.1)
        
        # Check if log directory exists
        log_dir = os.path.join(os.getcwd(), 'logs')
        if not os.path.exists(log_dir):
            print(f"   Log directory not found: {log_dir}")
            return False
        
        # Check for expected log files
        expected_files = ['astro_engine.log']
        found_files = []
        
        for file in os.listdir(log_dir):
            if file.endswith('.log'):
                found_files.append(file)
                file_path = os.path.join(log_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"   Found log file: {file} ({file_size} bytes)")
        
        if not found_files:
            print("   No log files found")
            return False
        
        print(f"   Log files created: {len(found_files)}")
        return True
    
    # Test 6: Performance Metrics Integration
    def test_performance_integration():
        print("⚡ Testing performance logging integration...")
        
        # Generate some performance data
        test_data = {
            "name": "Test User",
            "date": "1990-01-01",
            "time": "12:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone": 5.5
        }
        
        response = requests.post(f"{base_url}/lahiri/natal", json=test_data)
        if response.status_code != 200:
            print(f"   Failed to generate performance data: {response.status_code}")
            return False
        
        # Check performance summary
        response = requests.get(f"{base_url}/metrics/performance")
        if response.status_code == 200:
            data = response.json()
            if 'cache_performance' in data and 'api_performance' in data:
                print("   Performance logging integrated with metrics")
                return True
        
        print("   Performance logging not properly integrated")
        return False
    
    # Run all tests
    print("📊 Testing logging infrastructure...")
    run_test("Enhanced Logging Status", test_enhanced_logging_status)
    
    print("🎚️ Testing log level management...")
    run_test("Log Level Management", test_log_level_management)
    
    print("🧪 Testing log functionality...")
    run_test("Log Testing Functionality", test_log_testing)
    
    print("📋 Testing log aggregation...")
    run_test("Log Aggregation", test_log_aggregation)
    
    print("📁 Testing log file creation...")
    run_test("Log File Creation", test_log_file_creation)
    
    print("⚡ Testing performance integration...")
    run_test("Performance Integration", test_performance_integration)
    
    # Results summary
    print("=" * 60)
    print("📊 PHASE 3.3 VALIDATION SUMMARY")
    print(f"⏱️  Total test duration: {time.time() - start_time:.2f} seconds")
    print(f"✅ Tests passed: {results['tests_passed']}")
    print(f"❌ Tests failed: {results['tests_failed']}")
    print(f"📊 Total tests: {results['total_tests']}")
    print(f"🎯 Success rate: {(results['tests_passed']/results['total_tests']*100):.1f}%")
    
    if results['tests_failed'] == 0:
        print("🎉 ALL PHASE 3.3 TESTS PASSED!")
        print("✅ Phase 3.3: Log Management - COMPLETE")
        return True
    else:
        print("⚠️ Some tests failed. Please check the logs and configuration.")
        return False

if __name__ == "__main__":
    start_time = time.time()
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding properly. Please start the server first.")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Server not running. Please start the server with: python3 run_server.py")
        sys.exit(1)
    
    success = test_log_management()
    sys.exit(0 if success else 1)
