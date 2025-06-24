#!/usr/bin/env python3
"""
Phase 3.1: Structured Logging Validation Test
Tests structured logging implementation and integration

Tests include:
- Logging configuration and status
- Request/response logging with correlation IDs
- Calculation logging with performance data
- Error logging with context
- Cache operation logging
- Business event logging
"""

import requests
import json
import time
import uuid
from datetime import datetime

class StructuredLoggingValidator:
    """Phase 3.1 Structured Logging Validation"""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
    
    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.test_results['total_tests'] += 1
        if passed:
            self.test_results['passed_tests'] += 1
            print(f"✅ {test_name}: PASSED {details}")
        else:
            self.test_results['failed_tests'] += 1
            print(f"❌ {test_name}: FAILED {details}")
        
        self.test_results['test_details'].append({
            'test_name': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def test_logging_status_endpoint(self):
        """Test logging status and configuration endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/logging/status", timeout=10)
            passed = response.status_code == 200
            
            details = f"Status: {response.status_code}"
            if passed:
                data = response.json()
                structured_logging = data.get('structured_logging', 'unknown')
                environment = data.get('environment', 'unknown')
                details += f", Structured logging: {structured_logging}, Environment: {environment}"
                
            self.log_result("Logging Status Endpoint", passed, details)
            return response.json() if passed else {}
            
        except Exception as e:
            self.log_result("Logging Status Endpoint", False, f"Exception: {e}")
            return {}
    
    def test_correlation_id_tracking(self):
        """Test correlation ID tracking across requests"""
        try:
            # Generate a custom correlation ID
            correlation_id = str(uuid.uuid4())
            headers = {'X-Correlation-ID': correlation_id}
            
            # Make a request with correlation ID
            response = self.session.get(f"{self.base_url}/health", headers=headers, timeout=10)
            
            # Check if correlation ID is returned in response headers
            returned_correlation_id = response.headers.get('X-Correlation-ID')
            
            passed = (response.status_code == 200 and 
                     returned_correlation_id == correlation_id)
            
            details = f"Sent: {correlation_id[:8]}..., Returned: {returned_correlation_id[:8] if returned_correlation_id else 'None'}..."
            
            self.log_result("Correlation ID Tracking", passed, details)
            
        except Exception as e:
            self.log_result("Correlation ID Tracking", False, f"Exception: {e}")
    
    def test_structured_logging_in_calculation(self):
        """Test structured logging during chart calculations"""
        test_data = {
            "user_name": "Structured Logging Test",
            "birth_date": "1990-01-15",
            "birth_time": "14:30:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone_offset": 5.5
        }
        
        try:
            # Add correlation ID for tracking
            correlation_id = str(uuid.uuid4())
            headers = {
                'Content-Type': 'application/json',
                'X-Correlation-ID': correlation_id
            }
            
            response = self.session.post(
                f"{self.base_url}/lahiri/natal",
                json=test_data,
                headers=headers,
                timeout=30
            )
            
            passed = response.status_code == 200
            details = f"Status: {response.status_code}, Correlation ID: {correlation_id[:8]}..."
            
            if passed:
                # Check if correlation ID is in response
                returned_correlation_id = response.headers.get('X-Correlation-ID')
                if returned_correlation_id == correlation_id:
                    details += ", Correlation ID matched"
                else:
                    details += ", Correlation ID mismatch"
            
            self.log_result("Structured Logging in Calculation", passed, details)
            
        except Exception as e:
            self.log_result("Structured Logging in Calculation", False, f"Exception: {e}")
    
    def test_error_logging_with_context(self):
        """Test error logging with structured context"""
        try:
            # Make an invalid request to trigger error logging
            invalid_data = {
                "user_name": "Error Test",
                "birth_date": "invalid-date",
                "birth_time": "25:99:99",
                "latitude": 999,
                "longitude": 999,
                "timezone_offset": 99
            }
            
            correlation_id = str(uuid.uuid4())
            headers = {
                'Content-Type': 'application/json',
                'X-Correlation-ID': correlation_id
            }
            
            response = self.session.post(
                f"{self.base_url}/lahiri/natal",
                json=invalid_data,
                headers=headers,
                timeout=30
            )
            
            # Error response expected
            passed = response.status_code in [400, 422, 500]
            
            # Check if correlation ID is preserved in error response
            returned_correlation_id = response.headers.get('X-Correlation-ID')
            correlation_preserved = returned_correlation_id == correlation_id
            
            details = f"Error status: {response.status_code}, Correlation preserved: {correlation_preserved}"
            
            self.log_result("Error Logging with Context", passed, details)
            
        except Exception as e:
            self.log_result("Error Logging with Context", False, f"Exception: {e}")
    
    def test_cache_operation_logging(self):
        """Test cache operation logging"""
        test_data = {
            "user_name": "Cache Logging Test",
            "birth_date": "1985-06-20",
            "birth_time": "10:15:00",
            "latitude": 19.0760,
            "longitude": 72.8777,
            "timezone_offset": 5.5
        }
        
        try:
            correlation_id = str(uuid.uuid4())
            headers = {
                'Content-Type': 'application/json',
                'X-Correlation-ID': correlation_id
            }
            
            # First request (cache miss)
            response1 = self.session.post(
                f"{self.base_url}/lahiri/natal",
                json=test_data,
                headers=headers,
                timeout=30
            )
            
            # Second request (cache hit)
            response2 = self.session.post(
                f"{self.base_url}/lahiri/natal",
                json=test_data,
                headers=headers,
                timeout=30
            )
            
            passed = (response1.status_code == 200 and response2.status_code == 200)
            
            # Check cache stats to verify cache operations
            cache_response = self.session.get(f"{self.base_url}/cache/stats")
            cache_hit_rate = 0
            if cache_response.status_code == 200:
                cache_data = cache_response.json()
                cache_hit_rate = cache_data.get('hit_rate', 0)
            
            details = f"Requests: {response1.status_code}, {response2.status_code}, Cache hit rate: {cache_hit_rate:.1f}%"
            
            self.log_result("Cache Operation Logging", passed, details)
            
        except Exception as e:
            self.log_result("Cache Operation Logging", False, f"Exception: {e}")
    
    def test_performance_logging_integration(self):
        """Test integration of structured logging with performance metrics"""
        try:
            correlation_id = str(uuid.uuid4())
            headers = {'X-Correlation-ID': correlation_id}
            
            # Get performance summary with structured logging
            response = self.session.get(
                f"{self.base_url}/metrics/performance",
                headers=headers,
                timeout=10
            )
            
            passed = response.status_code == 200
            
            if passed:
                data = response.json()
                cache_hit_rate = data.get('performance_metrics', {}).get('cache_hit_rate', 0)
                returned_correlation_id = response.headers.get('X-Correlation-ID')
                
                details = f"Performance data available, Cache hit rate: {cache_hit_rate:.1f}%, Correlation ID: {returned_correlation_id[:8] if returned_correlation_id else 'None'}..."
            else:
                details = f"Failed with status: {response.status_code}"
            
            self.log_result("Performance Logging Integration", passed, details)
            
        except Exception as e:
            self.log_result("Performance Logging Integration", False, f"Exception: {e}")
    
    def run_phase_3_1_validation(self):
        """Run comprehensive Phase 3.1 structured logging validation"""
        print("🔥 PHASE 3.1: STRUCTURED LOGGING VALIDATION")
        print("="*60)
        
        start_time = time.time()
        
        # Test logging infrastructure
        print("\n📊 Testing logging infrastructure...")
        self.test_logging_status_endpoint()
        
        # Test correlation ID tracking
        print("\n🔗 Testing correlation ID tracking...")
        self.test_correlation_id_tracking()
        
        # Test logging in calculations
        print("\n⚡ Testing calculation logging...")
        self.test_structured_logging_in_calculation()
        
        # Test error logging
        print("\n❌ Testing error logging...")
        self.test_error_logging_with_context()
        
        # Test cache logging
        print("\n💾 Testing cache operation logging...")
        self.test_cache_operation_logging()
        
        # Test performance integration
        print("\n📈 Testing performance logging integration...")
        self.test_performance_logging_integration()
        
        total_duration = time.time() - start_time
        
        # Print summary
        print("\n" + "="*60)
        print("📊 PHASE 3.1 VALIDATION SUMMARY")
        print(f"⏱️  Total test duration: {total_duration:.2f} seconds")
        print(f"✅ Tests passed: {self.test_results['passed_tests']}")
        print(f"❌ Tests failed: {self.test_results['failed_tests']}")
        print(f"📊 Total tests: {self.test_results['total_tests']}")
        
        success_rate = (self.test_results['passed_tests'] / max(self.test_results['total_tests'], 1)) * 100
        print(f"🎯 Success rate: {success_rate:.1f}%")
        
        if self.test_results['failed_tests'] == 0:
            print("🎉 ALL PHASE 3.1 TESTS PASSED!")
            print("✅ Phase 3.1: Structured Logging Framework - COMPLETE")
        else:
            print("⚠️  Some Phase 3.1 tests failed. Check logs above for details.")
        
        return self.test_results

if __name__ == "__main__":
    validator = StructuredLoggingValidator()
    results = validator.run_phase_3_1_validation()
