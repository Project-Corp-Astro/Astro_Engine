#!/usr/bin/env python3
"""
Phase 2.2: Advanced Prometheus Metrics Validation Test
Tests advanced performance and business metrics implementation

New metrics tested:
- API response time percentiles
- Concurrent user tracking
- Cache performance metrics
- Resource utilization (CPU/Memory)
- Swiss Ephemeris performance
- Business metrics (user interactions, chart requests)
- Error rate calculations
"""

import requests
import time
import json
import threading
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Phase22MetricsValidator:
    """Phase 2.2 Advanced Metrics Validation"""
    
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
            logger.info(f"✅ {test_name}: PASSED {details}")
        else:
            self.test_results['failed_tests'] += 1
            logger.error(f"❌ {test_name}: FAILED {details}")
        
        self.test_results['test_details'].append({
            'test_name': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
    
    def test_performance_summary_endpoint(self):
        """Test new performance summary endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/metrics/performance", timeout=10)
            passed = response.status_code == 200
            
            details = f"Status: {response.status_code}"
            if passed:
                data = response.json()
                performance_metrics = data.get('performance_metrics', {})
                details += f", Keys: {list(performance_metrics.keys())}"
                
            self.log_result("Performance Summary Endpoint", passed, details)
            return response.json() if passed else {}
            
        except Exception as e:
            self.log_result("Performance Summary Endpoint", False, f"Exception: {e}")
            return {}
    
    def test_advanced_prometheus_metrics(self):
        """Test presence of advanced metrics in Prometheus output"""
        try:
            response = self.session.get(f"{self.base_url}/metrics", timeout=10)
            passed = response.status_code == 200
            
            if passed:
                metrics_text = response.text
                
                # Phase 2.2 advanced metrics to check
                advanced_metrics = [
                    'astro_engine_api_response_time_seconds',
                    'astro_engine_concurrent_users_active',
                    'astro_engine_cache_performance_seconds',
                    'astro_engine_ephemeris_calculation_seconds',
                    'astro_engine_calculation_complexity',
                    'astro_engine_user_interactions_total',
                    'astro_engine_error_rate_percentage',
                    'astro_engine_cpu_usage_percentage',
                    'astro_engine_memory_usage_percentage',
                    'astro_engine_redis_memory_bytes'
                ]
                
                found_metrics = []
                missing_metrics = []
                
                for metric in advanced_metrics:
                    if metric in metrics_text:
                        found_metrics.append(metric)
                    else:
                        missing_metrics.append(metric)
                
                passed = len(missing_metrics) == 0
                details = f"Found: {len(found_metrics)}/{len(advanced_metrics)}"
                if missing_metrics:
                    details += f", Missing: {', '.join(missing_metrics[:3])}"
                
            self.log_result("Advanced Prometheus Metrics", passed, details)
            
        except Exception as e:
            self.log_result("Advanced Prometheus Metrics", False, f"Exception: {e}")
    
    def test_chart_calculation_with_advanced_metrics(self):
        """Test chart calculation with enhanced metrics tracking"""
        test_data = {
            "user_name": "Advanced Metrics Test",
            "birth_date": "1995-07-22",
            "birth_time": "18:45:00",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "timezone_offset": 5.5
        }
        
        try:
            # Get initial metrics
            initial_response = self.session.get(f"{self.base_url}/metrics")
            initial_metrics = initial_response.text if initial_response.status_code == 200 else ""
            
            # Make chart calculation request
            start_time = time.time()
            chart_response = self.session.post(
                f"{self.base_url}/lahiri/natal",
                json=test_data,
                timeout=30
            )
            duration = time.time() - start_time
            
            # Get updated metrics
            updated_response = self.session.get(f"{self.base_url}/metrics")
            updated_metrics = updated_response.text if updated_response.status_code == 200 else ""
            
            passed = (chart_response.status_code == 200 and 
                     len(updated_metrics) > len(initial_metrics))
            
            details = f"Chart: {chart_response.status_code}, Duration: {duration:.3f}s, Metrics updated: {len(updated_metrics) > len(initial_metrics)}"
            
            self.log_result("Chart Calculation with Advanced Metrics", passed, details)
            
        except Exception as e:
            self.log_result("Chart Calculation with Advanced Metrics", False, f"Exception: {e}")
    
    def test_concurrent_user_tracking(self):
        """Test concurrent user metrics tracking"""
        def make_concurrent_request(user_id):
            test_data = {
                "user_name": f"Concurrent User {user_id}",
                "birth_date": "1988-11-05",
                "birth_time": "09:30:00",
                "latitude": 22.5726,
                "longitude": 88.3639,
                "timezone_offset": 5.5
            }
            try:
                response = self.session.post(
                    f"{self.base_url}/lahiri/natal",
                    json=test_data,
                    timeout=30
                )
                return response.status_code == 200
            except:
                return False
        
        try:
            # Launch concurrent requests
            threads = []
            for i in range(3):
                thread = threading.Thread(target=make_concurrent_request, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait briefly then check metrics
            time.sleep(0.5)
            
            # Get performance summary
            perf_response = self.session.get(f"{self.base_url}/metrics/performance")
            
            # Wait for threads to complete
            for thread in threads:
                thread.join()
            
            passed = perf_response.status_code == 200
            concurrent_users = 0
            
            if passed:
                data = perf_response.json()
                performance_metrics = data.get('performance_metrics', {})
                concurrent_users = performance_metrics.get('concurrent_users', 0)
            
            details = f"Performance API: {perf_response.status_code}, Concurrent users: {concurrent_users}"
            
            self.log_result("Concurrent User Tracking", passed, details)
            
        except Exception as e:
            self.log_result("Concurrent User Tracking", False, f"Exception: {e}")
    
    def test_cache_performance_metrics(self):
        """Test cache performance tracking"""
        test_data = {
            "user_name": "Cache Performance Test",
            "birth_date": "1993-04-18",
            "birth_time": "14:20:00",
            "latitude": 26.9124,
            "longitude": 75.7873,
            "timezone_offset": 5.5
        }
        
        try:
            # First request (should be cache miss)
            start_time = time.time()
            response1 = self.session.post(f"{self.base_url}/lahiri/natal", json=test_data, timeout=30)
            first_duration = time.time() - start_time
            
            # Second request (should be cache hit)
            start_time = time.time()
            response2 = self.session.post(f"{self.base_url}/lahiri/natal", json=test_data, timeout=30)
            second_duration = time.time() - start_time
            
            # Check cache stats
            cache_response = self.session.get(f"{self.base_url}/cache/stats")
            
            passed = (response1.status_code == 200 and 
                     response2.status_code == 200 and
                     cache_response.status_code == 200 and
                     second_duration < first_duration)
            
            cache_data = cache_response.json() if cache_response.status_code == 200 else {}
            hit_rate = cache_data.get('hit_rate', 0)
            
            details = f"Miss: {first_duration:.3f}s, Hit: {second_duration:.3f}s, Hit rate: {hit_rate:.1f}%"
            
            self.log_result("Cache Performance Metrics", passed, details)
            
        except Exception as e:
            self.log_result("Cache Performance Metrics", False, f"Exception: {e}")
    
    def test_resource_utilization_tracking(self):
        """Test CPU and memory utilization tracking"""
        try:
            # Get performance summary
            response = self.session.get(f"{self.base_url}/metrics/performance", timeout=10)
            passed = response.status_code == 200
            
            cpu_usage = memory_usage = memory_mb = None
            if passed:
                data = response.json()
                performance_metrics = data.get('performance_metrics', {})
                cpu_usage = performance_metrics.get('cpu_usage_percentage')
                memory_usage = performance_metrics.get('memory_usage_percentage')
                memory_mb = performance_metrics.get('memory_usage_mb')
                
                # Check if we have resource metrics
                passed = (cpu_usage is not None and 
                         memory_usage is not None and 
                         memory_mb is not None)
            
            details = f"CPU: {cpu_usage}%, Memory: {memory_usage}%, Memory MB: {memory_mb:.1f}" if passed else "Resource metrics not available"
            
            self.log_result("Resource Utilization Tracking", passed, details)
            
        except Exception as e:
            self.log_result("Resource Utilization Tracking", False, f"Exception: {e}")
    
    def test_error_rate_calculation(self):
        """Test error rate calculation and tracking"""
        try:
            # Make a request that should fail
            invalid_data = {
                "user_name": "Error Test",
                "birth_date": "invalid-date",
                "birth_time": "25:99:99",
                "latitude": 999,
                "longitude": 999,
                "timezone_offset": 99
            }
            
            # Make the invalid request
            error_response = self.session.post(f"{self.base_url}/lahiri/natal", json=invalid_data, timeout=30)
            
            # Make a valid request
            valid_data = {
                "user_name": "Valid Test",
                "birth_date": "1990-05-15",
                "birth_time": "10:30:00",
                "latitude": 28.6139,
                "longitude": 77.2090,
                "timezone_offset": 5.5
            }
            valid_response = self.session.post(f"{self.base_url}/lahiri/natal", json=valid_data, timeout=30)
            
            # Check error rate in performance metrics
            perf_response = self.session.get(f"{self.base_url}/metrics/performance")
            
            passed = (error_response.status_code != 200 and 
                     valid_response.status_code == 200 and
                     perf_response.status_code == 200)
            
            error_rate = None
            if passed:
                data = perf_response.json()
                performance_metrics = data.get('performance_metrics', {})
                error_rate = performance_metrics.get('error_rate_percentage', 0)
            
            details = f"Error status: {error_response.status_code}, Valid status: {valid_response.status_code}, Error rate: {error_rate}%"
            
            self.log_result("Error Rate Calculation", passed, details)
            
        except Exception as e:
            self.log_result("Error Rate Calculation", False, f"Exception: {e}")
    
    def run_phase_2_2_validation(self):
        """Run comprehensive Phase 2.2 metrics validation"""
        logger.info("🔥 PHASE 2.2: ADVANCED PROMETHEUS METRICS VALIDATION")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        # Test new endpoints
        logger.info("📊 Testing new performance endpoints...")
        self.test_performance_summary_endpoint()
        
        # Test advanced metrics
        logger.info("🔍 Testing advanced Prometheus metrics...")
        self.test_advanced_prometheus_metrics()
        
        # Test enhanced functionality
        logger.info("⚡ Testing enhanced metrics tracking...")
        self.test_chart_calculation_with_advanced_metrics()
        self.test_concurrent_user_tracking()
        self.test_cache_performance_metrics()
        self.test_resource_utilization_tracking()
        self.test_error_rate_calculation()
        
        total_duration = time.time() - start_time
        
        # Print summary
        logger.info("=" * 80)
        logger.info("📊 PHASE 2.2 VALIDATION SUMMARY")
        logger.info(f"⏱️  Total test duration: {total_duration:.2f} seconds")
        logger.info(f"✅ Tests passed: {self.test_results['passed_tests']}")
        logger.info(f"❌ Tests failed: {self.test_results['failed_tests']}")
        logger.info(f"📊 Total tests: {self.test_results['total_tests']}")
        
        success_rate = (self.test_results['passed_tests'] / max(self.test_results['total_tests'], 1)) * 100
        logger.info(f"🎯 Success rate: {success_rate:.1f}%")
        
        if self.test_results['failed_tests'] == 0:
            logger.info("🎉 ALL PHASE 2.2 TESTS PASSED!")
            logger.info("✅ Phase 2.2: Advanced Prometheus Metrics - COMPLETE")
        else:
            logger.warning("⚠️  Some Phase 2.2 tests failed. Check logs above for details.")
        
        return self.test_results

if __name__ == "__main__":
    validator = Phase22MetricsValidator()
    results = validator.run_phase_2_2_validation()
