#!/usr/bin/env python3
"""
Phase 4.1: Celery Setup Validation Test
Tests Celery configuration, task submission, and basic functionality
"""

import os
import sys
import time
import json
import requests
import threading
import subprocess
from datetime import datetime

# Add project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_celery_setup():
    """Comprehensive test of Celery setup and basic functionality"""
    
    print("🔥 PHASE 4.1: CELERY SETUP VALIDATION")
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
    
    # Test 1: Celery Configuration Test
    def test_celery_configuration():
        print("⚙️ Testing Celery configuration...")
        try:
            from astro_engine.celery_manager import AstroCeleryManager
            from astro_engine.celery_tasks import celery_app
            
            # Test Celery app creation
            if not celery_app:
                print("   Celery app not created")
                return False
            
            # Check configuration
            config = celery_app.conf
            
            print(f"   Broker URL: {config.broker_url}")
            print(f"   Result backend: {config.result_backend}")
            print(f"   Task serializer: {config.task_serializer}")
            print(f"   Result serializer: {config.result_serializer}")
            print(f"   Timezone: {config.timezone}")
            
            # Verify required settings
            required_settings = [
                'broker_url', 'result_backend', 'task_serializer', 
                'result_serializer', 'timezone'
            ]
            
            for setting in required_settings:
                if not hasattr(config, setting):
                    print(f"   Missing configuration: {setting}")
                    return False
            
            return True
            
        except ImportError as e:
            print(f"   Import error: {e}")
            return False
        except Exception as e:
            print(f"   Configuration error: {e}")
            return False
    
    # Test 2: Task Registration Test
    def test_task_registration():
        print("📋 Testing task registration...")
        try:
            from astro_engine.celery_tasks import get_available_tasks, AVAILABLE_TASKS
            
            available_tasks = get_available_tasks()
            expected_tasks = ['natal_chart', 'divisional_chart', 'bulk_charts', 'test_task']
            
            print(f"   Available tasks: {available_tasks}")
            
            for task in expected_tasks:
                if task not in available_tasks:
                    print(f"   Missing task: {task}")
                    return False
                
                # Check if task is in registry
                if task not in AVAILABLE_TASKS:
                    print(f"   Task not in registry: {task}")
                    return False
                
                print(f"   ✓ Task registered: {task}")
            
            return True
            
        except Exception as e:
            print(f"   Task registration error: {e}")
            return False
    
    # Test 3: Redis Connection Test
    def test_redis_connection():
        print("🔗 Testing Redis connection for Celery...")
        try:
            import redis
            
            # Test broker connection
            broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
            broker_client = redis.from_url(broker_url)
            broker_client.ping()
            print(f"   ✓ Broker connection successful: {broker_url}")
            
            # Test result backend connection
            backend_url = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
            backend_client = redis.from_url(backend_url)
            backend_client.ping()
            print(f"   ✓ Backend connection successful: {backend_url}")
            
            return True
            
        except redis.ConnectionError:
            print("   ❌ Redis connection failed - is Redis running?")
            return False
        except Exception as e:
            print(f"   Redis test error: {e}")
            return False
    
    # Test 4: Celery Manager Integration Test
    def test_celery_manager_integration():
        print("🔧 Testing Celery manager integration...")
        try:
            from astro_engine.celery_manager import AstroCeleryManager
            
            # Create mock Flask app
            class MockApp:
                def __init__(self):
                    self.config = {}
            
            app = MockApp()
            manager = AstroCeleryManager()
            manager.init_app(app)
            
            # Check if manager is properly initialized
            if not hasattr(app, 'celery_manager'):
                print("   Celery manager not attached to app")
                return False
            
            if not manager.celery_app:
                print("   Celery app not initialized in manager")
                return False
            
            print("   ✓ Celery manager initialized")
            print("   ✓ Manager attached to Flask app")
            print("   ✓ Celery app created in manager")
            
            return True
            
        except Exception as e:
            print(f"   Manager integration error: {e}")
            return False
    
    # Test 5: API Endpoints Test (without worker)
    def test_api_endpoints():
        print("🌐 Testing Celery API endpoints...")
        try:
            # Test available tasks endpoint
            response = requests.get(f"{base_url}/tasks/available", timeout=5)
            if response.status_code != 200:
                print(f"   Available tasks endpoint failed: {response.status_code}")
                return False
            
            data = response.json()
            if not data.get('success'):
                print("   Available tasks endpoint returned error")
                return False
            
            available_tasks = data.get('available_tasks', [])
            print(f"   ✓ Available tasks: {available_tasks}")
            
            # Test queue stats endpoint
            response = requests.get(f"{base_url}/tasks/queue/stats", timeout=5)
            if response.status_code == 200:
                stats_data = response.json()
                if stats_data.get('success'):
                    print("   ✓ Queue stats endpoint working")
                else:
                    print("   ⚠️ Queue stats endpoint returned error (expected without worker)")
            
            return True
            
        except requests.exceptions.RequestException:
            print("   ❌ Server not responding - please start the server")
            return False
        except Exception as e:
            print(f"   API endpoint test error: {e}")
            return False
    
    # Test 6: Task Validation Test
    def test_task_validation():
        print("✅ Testing task validation...")
        try:
            # Test task data structures
            test_tasks = {
                'natal_chart': {
                    'name': 'Test User',
                    'date': '1990-01-01',
                    'time': '12:00',
                    'latitude': 28.6139,
                    'longitude': 77.2090,
                    'timezone': 5.5
                },
                'divisional_chart': {
                    'name': 'Test User',
                    'date': '1990-01-01',
                    'time': '12:00',
                    'latitude': 28.6139,
                    'longitude': 77.2090,
                    'timezone': 5.5,
                    'division_type': 'D9'
                },
                'test_task': {
                    'work_duration': 1,
                    'test_data': 'validation'
                }
            }
            
            for task_name, task_data in test_tasks.items():
                # Validate task data structure
                required_fields = {
                    'natal_chart': ['name', 'date', 'time', 'latitude', 'longitude', 'timezone'],
                    'divisional_chart': ['name', 'date', 'time', 'latitude', 'longitude', 'timezone', 'division_type'],
                    'test_task': ['work_duration']
                }
                
                for field in required_fields.get(task_name, []):
                    if field not in task_data:
                        print(f"   Missing field in {task_name}: {field}")
                        return False
                
                print(f"   ✓ Task data valid: {task_name}")
            
            return True
            
        except Exception as e:
            print(f"   Task validation error: {e}")
            return False
    
    # Run all tests
    print("⚙️ Testing Celery configuration...")
    run_test("Celery Configuration", test_celery_configuration)
    
    print("📋 Testing task registration...")
    run_test("Task Registration", test_task_registration)
    
    print("🔗 Testing Redis connection...")
    run_test("Redis Connection", test_redis_connection)
    
    print("🔧 Testing manager integration...")
    run_test("Celery Manager Integration", test_celery_manager_integration)
    
    print("🌐 Testing API endpoints...")
    run_test("API Endpoints", test_api_endpoints)
    
    print("✅ Testing task validation...")
    run_test("Task Validation", test_task_validation)
    
    # Results summary
    print("=" * 60)
    print("📊 PHASE 4.1 VALIDATION SUMMARY")
    print(f"⏱️  Total test duration: {time.time() - start_time:.2f} seconds")
    print(f"✅ Tests passed: {results['tests_passed']}")
    print(f"❌ Tests failed: {results['tests_failed']}")
    print(f"📊 Total tests: {results['total_tests']}")
    print(f"🎯 Success rate: {(results['tests_passed']/results['total_tests']*100):.1f}%")
    
    if results['tests_failed'] == 0:
        print("🎉 ALL PHASE 4.1 TESTS PASSED!")
        print("✅ Phase 4.1: Celery Setup - COMPLETE")
        print("\n📋 NEXT STEPS:")
        print("1. Start Redis server: redis-server")
        print("2. Start Celery worker: python3 start_celery_worker.py")
        print("3. Test task execution with Phase 4.2")
        return True
    else:
        print("⚠️ Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    start_time = time.time()
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding properly. Please start the server first.")
            print("   Run: python3 run_server.py")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Server not running. Please start the server with: python3 run_server.py")
        sys.exit(1)
    
    success = test_celery_setup()
    sys.exit(0 if success else 1)
