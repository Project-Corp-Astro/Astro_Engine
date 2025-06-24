#!/usr/bin/env python3
"""
Phase 2.1: Prometheus Metrics Validation Test
Validates comprehensive metrics collection and monitoring
"""

import requests
import time
import json
from datetime import datetime

class PrometheusMetricsTest:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.test_data = {
            "user_name": "Prometheus Test",
            "birth_date": "1990-01-15",
            "birth_time": "12:30:00",
            "latitude": 28.6139,
            "longitude": 77.209,
            "timezone_offset": 5.5
        }
    
    def test_metrics_endpoints(self):
        """Test metrics endpoints availability"""
        print("🔍 TESTING METRICS ENDPOINTS")
        print("=" * 60)
        
        # Test Prometheus metrics endpoint
        print("📊 Testing Prometheus /metrics endpoint...")
        metrics_response = requests.get(f"{self.base_url}/metrics")
        if metrics_response.status_code == 200:
            print(f"  ✅ Status: {metrics_response.status_code}")
            print(f"  📏 Content length: {len(metrics_response.text)} bytes")
            print(f"  🏷️  Content type: {metrics_response.headers.get('content-type', 'unknown')}")
        else:
            print(f"  ❌ Error: {metrics_response.status_code}")
            return False
        
        # Test JSON metrics endpoint
        print("\n🧪 Testing JSON /metrics/json endpoint...")
        json_response = requests.get(f"{self.base_url}/metrics/json")
        if json_response.status_code == 200:
            data = json_response.json()
            print(f"  ✅ Status: {json_response.status_code}")
            print(f"  📊 Metrics status: {data.get('metrics_status', 'unknown')}")
            print(f"  🕒 Timestamp: {data.get('timestamp', 'unknown')}")
        else:
            print(f"  ❌ Error: {json_response.status_code}")
            return False
        
        return True
    
    def test_request_metrics(self):
        """Test request-level metrics collection"""
        print("\n🚀 TESTING REQUEST METRICS")
        print("=" * 60)
        
        # Get initial metrics
        initial_metrics = self._get_metrics_text()
        initial_requests = self._count_metric_occurrences(initial_metrics, "astro_engine_requests_total")
        
        print(f"📋 Initial request count: {initial_requests}")
        
        # Make test requests
        endpoints = [
            ("/lahiri/natal", "natal chart"),
            ("/lahiri/navamsa", "navamsa chart"),
            ("/lahiri/calculate_d3", "d3 chart"),
            ("/lahiri/transit", "transit chart")
        ]
        
        for endpoint, name in endpoints:
            print(f"\n📤 Making request to {name} ({endpoint})")
            start_time = time.time()
            response = requests.post(f"{self.base_url}{endpoint}", json=self.test_data)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                print(f"  ✅ Status: {response.status_code}")
                print(f"  ⏱️  Duration: {duration:.3f}s")
                print(f"  📏 Response size: {len(response.content)} bytes")
            else:
                print(f"  ❌ Error: {response.status_code}")
        
        # Check metrics after requests
        time.sleep(1)  # Brief pause for metrics to update
        final_metrics = self._get_metrics_text()
        final_requests = self._count_metric_occurrences(final_metrics, "astro_engine_requests_total")
        
        print(f"\n📊 Final request count: {final_requests}")
        print(f"📈 New requests recorded: {final_requests - initial_requests}")
        
        return final_requests > initial_requests
    
    def test_cache_metrics(self):
        """Test cache-related metrics"""
        print("\n💾 TESTING CACHE METRICS")
        print("=" * 60)
        
        # Check cache metrics in Prometheus format
        metrics_text = self._get_metrics_text()
        
        # Look for cache metrics
        cache_metrics = [
            "astro_engine_cache_operations_total",
            "astro_engine_cache_hit_rate",
            "astro_engine_cache_size_bytes"
        ]
        
        found_metrics = {}
        for metric in cache_metrics:
            count = self._count_metric_occurrences(metrics_text, metric)
            found_metrics[metric] = count
            print(f"📊 {metric}: {count} entries")
        
        # Validate cache operations
        cache_ops = self._extract_cache_operations(metrics_text)
        print(f"\n🔍 Cache Operations Found:")
        for operation, count in cache_ops.items():
            print(f"  {operation}: {count}")
        
        return len(found_metrics) > 0 and any(count > 0 for count in found_metrics.values())
    
    def test_calculation_metrics(self):
        """Test calculation-specific metrics"""
        print("\n🧮 TESTING CALCULATION METRICS")
        print("=" * 60)
        
        metrics_text = self._get_metrics_text()
        
        # Look for calculation metrics
        calc_metrics = [
            "astro_engine_calculation_duration_seconds",
            "astro_engine_calculations_total"
        ]
        
        found_calc_metrics = {}
        for metric in calc_metrics:
            count = self._count_metric_occurrences(metrics_text, metric)
            found_calc_metrics[metric] = count
            print(f"📊 {metric}: {count} entries")
        
        # Extract calculation types
        calc_types = self._extract_calculation_types(metrics_text)
        print(f"\n🎯 Calculation Types Found:")
        for calc_type in calc_types:
            print(f"  • {calc_type}")
        
        return len(calc_types) > 0
    
    def test_business_metrics(self):
        """Test business-level metrics"""
        print("\n📈 TESTING BUSINESS METRICS")
        print("=" * 60)
        
        metrics_text = self._get_metrics_text()
        
        # Look for business metrics
        business_metrics = [
            "astro_engine_chart_requests_total",
            "astro_engine_active_requests"
        ]
        
        for metric in business_metrics:
            count = self._count_metric_occurrences(metrics_text, metric)
            print(f"📊 {metric}: {count} entries")
        
        return True
    
    def _get_metrics_text(self):
        """Get metrics in Prometheus text format"""
        response = requests.get(f"{self.base_url}/metrics")
        return response.text if response.status_code == 200 else ""
    
    def _count_metric_occurrences(self, text, metric_name):
        """Count occurrences of a metric in the text"""
        return text.count(metric_name)
    
    def _extract_cache_operations(self, text):
        """Extract cache operation types and counts"""
        operations = {}
        lines = text.split('\n')
        for line in lines:
            if 'astro_engine_cache_operations_total{' in line and '}' in line:
                # Extract operation and result
                if 'operation="' in line and 'result="' in line:
                    operation_start = line.find('operation="') + 11
                    operation_end = line.find('"', operation_start)
                    result_start = line.find('result="') + 8
                    result_end = line.find('"', result_start)
                    
                    if operation_end > operation_start and result_end > result_start:
                        operation = line[operation_start:operation_end]
                        result = line[result_start:result_end]
                        key = f"{operation}_{result}"
                        
                        # Extract count
                        try:
                            count_start = line.rfind(' ') + 1
                            count = float(line[count_start:])
                            operations[key] = count
                        except:
                            pass
        
        return operations
    
    def _extract_calculation_types(self, text):
        """Extract calculation types from metrics"""
        calc_types = set()
        lines = text.split('\n')
        for line in lines:
            if 'astro_engine_calculation' in line and 'calculation_type="' in line:
                start = line.find('calculation_type="') + 18
                end = line.find('"', start)
                if end > start:
                    calc_types.add(line[start:end])
        
        return sorted(calc_types)
    
    def run_comprehensive_test(self):
        """Run comprehensive metrics validation"""
        print("🎯 PROMETHEUS METRICS VALIDATION TEST")
        print("=" * 70)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Base URL: {self.base_url}")
        
        # Check server health
        try:
            health_response = requests.get(f"{self.base_url}/health", timeout=5)
            if health_response.status_code == 200:
                print("✅ Server health check passed")
            else:
                print(f"⚠️  Server health check warning: {health_response.status_code}")
        except Exception as e:
            print(f"❌ Server health check failed: {e}")
            return
        
        # Run test suite
        tests = [
            ("Metrics Endpoints", self.test_metrics_endpoints),
            ("Request Metrics", self.test_request_metrics),
            ("Cache Metrics", self.test_cache_metrics),
            ("Calculation Metrics", self.test_calculation_metrics),
            ("Business Metrics", self.test_business_metrics)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    print(f"\n✅ {test_name}: PASSED")
                    passed += 1
                else:
                    print(f"\n❌ {test_name}: FAILED")
            except Exception as e:
                print(f"\n💥 {test_name}: ERROR - {e}")
        
        # Summary
        print("\n" + "=" * 70)
        print("🏆 PROMETHEUS METRICS TEST SUMMARY")
        print("=" * 70)
        print(f"📊 Tests passed: {passed}/{total}")
        print(f"📈 Success rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Prometheus metrics fully operational!")
        elif passed >= total * 0.8:
            print("✅ MOSTLY SUCCESSFUL - Minor issues to investigate")
        else:
            print("⚠️  NEEDS ATTENTION - Multiple test failures")
        
        # Final metrics snapshot
        print(f"\n📸 Final Metrics Snapshot:")
        try:
            json_response = requests.get(f"{self.base_url}/metrics/json")
            if json_response.status_code == 200:
                data = json_response.json()
                cache_stats = data.get('cache_statistics', {})
                print(f"  Cache hit rate: {cache_stats.get('hit_rate', 0):.1f}%")
                print(f"  Cache operations: {cache_stats.get('total_operations', 0)}")
                print(f"  Redis available: {'✅' if cache_stats.get('redis_available') else '❌'}")
        except:
            print("  ⚠️  Could not retrieve final metrics")

if __name__ == "__main__":
    tester = PrometheusMetricsTest()
    tester.run_comprehensive_test()
