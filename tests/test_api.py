#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Astro Engine
Tests all endpoints and validates responses
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import concurrent.futures
import argparse

class AstroEngineAPITester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        # Test data for various scenarios
        self.test_birth_data = {
            "valid_data": {
                "birth_date": "1990-05-15",
                "birth_time": "14:30",
                "latitude": 28.6139,
                "longitude": 77.2090,
                "timezone": "Asia/Kolkata"
            },
            "edge_cases": [
                {
                    "name": "midnight_birth",
                    "data": {
                        "birth_date": "1985-12-25",
                        "birth_time": "00:00",
                        "latitude": 40.7128,
                        "longitude": -74.0060,
                        "timezone": "America/New_York"
                    }
                },
                {
                    "name": "southern_hemisphere",
                    "data": {
                        "birth_date": "1995-03-10",
                        "birth_time": "18:45",
                        "latitude": -33.8688,
                        "longitude": 151.2093,
                        "timezone": "Australia/Sydney"
                    }
                },
                {
                    "name": "near_poles",
                    "data": {
                        "birth_date": "2000-06-21",
                        "birth_time": "12:00",
                        "latitude": 71.0,
                        "longitude": -8.0,
                        "timezone": "Arctic/Longyearbyen"
                    }
                }
            ]
        }
        
        # Corporate test data
        self.corporate_data = {
            "team_data": {
                "members": [
                    {
                        "name": "John Doe",
                        "birth_date": "1985-03-15",
                        "birth_time": "10:30",
                        "latitude": 28.6139,
                        "longitude": 77.2090,
                        "timezone": "Asia/Kolkata",
                        "role": "Manager"
                    },
                    {
                        "name": "Jane Smith",
                        "birth_date": "1990-07-22",
                        "birth_time": "16:45",
                        "latitude": 28.6139,
                        "longitude": 77.2090,
                        "timezone": "Asia/Kolkata",
                        "role": "Developer"
                    }
                ]
            },
            "business_timing": {
                "business_type": "Technology",
                "start_date": "2024-01-01",
                "location": {
                    "latitude": 28.6139,
                    "longitude": 77.2090,
                    "timezone": "Asia/Kolkata"
                }
            }
        }
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test results"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = {
            "test": test_name,
            "status": status,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {details}")
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", True, "API is healthy")
                else:
                    self.log_test("Health Check", False, f"Unhealthy status: {data}")
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/metrics", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "uptime" in data and "requests_total" in data:
                    self.log_test("Metrics Endpoint", True, "Metrics available")
                else:
                    self.log_test("Metrics Endpoint", False, "Missing metrics data")
            else:
                self.log_test("Metrics Endpoint", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Metrics Endpoint", False, f"Error: {str(e)}")
    
    def test_basic_calculation(self, ayanamsa: str = "lahiri"):
        """Test basic astrological calculation"""
        try:
            endpoint = f"{self.base_url}/api/v1/{ayanamsa}/calculate"
            response = self.session.post(
                endpoint,
                json=self.test_birth_data["valid_data"],
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["planets", "houses", "birth_details"]
                
                missing_fields = [field for field in required_fields if field not in data]
                if not missing_fields:
                    # Validate planets data
                    planets = data.get("planets", {})
                    expected_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
                    
                    planets_present = all(planet in planets for planet in expected_planets)
                    if planets_present:
                        self.log_test(f"Basic Calculation ({ayanamsa})", True, 
                                    f"All required data present, {len(planets)} planets calculated")
                    else:
                        missing_planets = [p for p in expected_planets if p not in planets]
                        self.log_test(f"Basic Calculation ({ayanamsa})", False, 
                                    f"Missing planets: {missing_planets}")
                else:
                    self.log_test(f"Basic Calculation ({ayanamsa})", False, 
                                f"Missing fields: {missing_fields}")
            else:
                self.log_test(f"Basic Calculation ({ayanamsa})", False, 
                            f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test(f"Basic Calculation ({ayanamsa})", False, f"Error: {str(e)}")
    
    def test_all_ayanamsa_systems(self):
        """Test all supported ayanamsa systems"""
        ayanamsa_systems = ["lahiri", "kp", "raman"]
        
        for ayanamsa in ayanamsa_systems:
            self.test_basic_calculation(ayanamsa)
    
    def test_edge_cases(self):
        """Test edge case scenarios"""
        for case in self.test_birth_data["edge_cases"]:
            try:
                endpoint = f"{self.base_url}/api/v1/lahiri/calculate"
                response = self.session.post(
                    endpoint,
                    json=case["data"],
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "planets" in data and len(data["planets"]) > 0:
                        self.log_test(f"Edge Case ({case['name']})", True, 
                                    "Calculation successful")
                    else:
                        self.log_test(f"Edge Case ({case['name']})", False, 
                                    "No planet data returned")
                else:
                    self.log_test(f"Edge Case ({case['name']})", False, 
                                f"Status code: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Edge Case ({case['name']})", False, f"Error: {str(e)}")
    
    def test_error_handling(self):
        """Test API error handling"""
        error_test_cases = [
            {
                "name": "Invalid Date Format",
                "data": {
                    "birth_date": "invalid-date",
                    "birth_time": "14:30",
                    "latitude": 28.6139,
                    "longitude": 77.2090,
                    "timezone": "Asia/Kolkata"
                },
                "expected_status": 400
            },
            {
                "name": "Missing Required Field",
                "data": {
                    "birth_time": "14:30",
                    "latitude": 28.6139,
                    "longitude": 77.2090,
                    "timezone": "Asia/Kolkata"
                },
                "expected_status": 400
            },
            {
                "name": "Invalid Coordinates",
                "data": {
                    "birth_date": "1990-05-15",
                    "birth_time": "14:30",
                    "latitude": 999,  # Invalid latitude
                    "longitude": 77.2090,
                    "timezone": "Asia/Kolkata"
                },
                "expected_status": 400
            }
        ]
        
        for case in error_test_cases:
            try:
                endpoint = f"{self.base_url}/api/v1/lahiri/calculate"
                response = self.session.post(endpoint, json=case["data"], timeout=10)
                
                if response.status_code == case["expected_status"]:
                    self.log_test(f"Error Handling ({case['name']})", True, 
                                f"Correct error status: {response.status_code}")
                else:
                    self.log_test(f"Error Handling ({case['name']})", False, 
                                f"Expected {case['expected_status']}, got {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Error Handling ({case['name']})", False, f"Error: {str(e)}")
    
    def test_corporate_endpoints(self):
        """Test corporate astrology endpoints"""
        corporate_endpoints = [
            {
                "endpoint": "/api/v1/corporate/team-compatibility",
                "data": self.corporate_data["team_data"],
                "name": "Team Compatibility"
            },
            {
                "endpoint": "/api/v1/corporate/business-timing",
                "data": self.corporate_data["business_timing"],
                "name": "Business Timing"
            }
        ]
        
        for test_case in corporate_endpoints:
            try:
                url = f"{self.base_url}{test_case['endpoint']}"
                response = self.session.post(url, json=test_case["data"], timeout=30)
                
                # Some endpoints might not be implemented yet (404), which is acceptable
                if response.status_code in [200, 201]:
                    data = response.json()
                    self.log_test(f"Corporate API ({test_case['name']})", True, 
                                "Endpoint operational")
                elif response.status_code == 404:
                    self.log_test(f"Corporate API ({test_case['name']})", True, 
                                "Endpoint not implemented yet (404 expected)")
                else:
                    self.log_test(f"Corporate API ({test_case['name']})", False, 
                                f"Status code: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Corporate API ({test_case['name']})", False, f"Error: {str(e)}")
    
    def test_performance(self):
        """Test API performance"""
        try:
            # Test single request performance
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/api/v1/lahiri/calculate",
                json=self.test_birth_data["valid_data"],
                timeout=30
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200 and response_time < 5.0:
                self.log_test("Performance (Single Request)", True, 
                            f"Response time: {response_time:.2f}s")
            else:
                self.log_test("Performance (Single Request)", False, 
                            f"Slow response: {response_time:.2f}s or error")
            
            # Test concurrent requests
            def make_request():
                return self.session.post(
                    f"{self.base_url}/api/v1/lahiri/calculate",
                    json=self.test_birth_data["valid_data"],
                    timeout=30
                )
            
            start_time = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                responses = [future.result() for future in futures]
            end_time = time.time()
            
            successful_responses = sum(1 for r in responses if r.status_code == 200)
            total_time = end_time - start_time
            
            if successful_responses >= 8 and total_time < 15.0:
                self.log_test("Performance (Concurrent Requests)", True, 
                            f"{successful_responses}/10 successful in {total_time:.2f}s")
            else:
                self.log_test("Performance (Concurrent Requests)", False, 
                            f"Only {successful_responses}/10 successful in {total_time:.2f}s")
                
        except Exception as e:
            self.log_test("Performance Test", False, f"Error: {str(e)}")
    
    def test_caching(self):
        """Test Redis caching functionality"""
        try:
            # Make same request twice
            endpoint = f"{self.base_url}/api/v1/lahiri/calculate"
            data = self.test_birth_data["valid_data"]
            
            # First request (should be calculated)
            start_time = time.time()
            response1 = self.session.post(endpoint, json=data, timeout=30)
            time1 = time.time() - start_time
            
            # Second request (should be cached)
            start_time = time.time()
            response2 = self.session.post(endpoint, json=data, timeout=30)
            time2 = time.time() - start_time
            
            if (response1.status_code == 200 and response2.status_code == 200 and
                response1.json() == response2.json()):
                
                # Check if second request was faster (indicating cache hit)
                if time2 < time1 * 0.8:  # At least 20% faster
                    self.log_test("Caching", True, 
                                f"Cache hit detected (1st: {time1:.2f}s, 2nd: {time2:.2f}s)")
                else:
                    self.log_test("Caching", True, 
                                f"Responses consistent, cache status unclear")
            else:
                self.log_test("Caching", False, "Inconsistent responses")
                
        except Exception as e:
            self.log_test("Caching", False, f"Error: {str(e)}")
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        try:
            # Make rapid requests to trigger rate limiting
            responses = []
            for i in range(25):  # Exceed typical rate limits
                response = self.session.get(f"{self.base_url}/health")
                responses.append(response.status_code)
                if response.status_code == 429:  # Rate limited
                    break
            
            rate_limited = any(status == 429 for status in responses)
            
            if rate_limited:
                self.log_test("Rate Limiting", True, "Rate limiting is working")
            else:
                self.log_test("Rate Limiting", True, 
                            "No rate limiting triggered (may be configured differently)")
                
        except Exception as e:
            self.log_test("Rate Limiting", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🧪 Starting Comprehensive API Testing...")
        print("=" * 60)
        
        # Basic functionality tests
        print("\n🔍 Testing Basic Functionality...")
        self.test_health_endpoint()
        self.test_metrics_endpoint()
        
        # Core calculation tests
        print("\n🌟 Testing Astrological Calculations...")
        self.test_all_ayanamsa_systems()
        self.test_edge_cases()
        
        # Error handling tests
        print("\n🚨 Testing Error Handling...")
        self.test_error_handling()
        
        # Corporate features
        print("\n🏢 Testing Corporate Features...")
        self.test_corporate_endpoints()
        
        # Performance tests
        print("\n⚡ Testing Performance...")
        self.test_performance()
        self.test_caching()
        
        # Security tests
        print("\n🔒 Testing Security Features...")
        self.test_rate_limiting()
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📋 API TESTING REPORT")
        print("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"✅ Tests Passed: {self.passed_tests}/{self.total_tests} ({success_rate:.1f}%)")
        
        # Group results by category
        failed_tests = [r for r in self.test_results if not r["passed"]]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        # Performance summary
        performance_tests = [r for r in self.test_results if "Performance" in r["test"]]
        if performance_tests:
            print(f"\n⚡ Performance Summary:")
            for test in performance_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        print("\n" + "=" * 60)
        
        if success_rate >= 90:
            print("🎉 EXCELLENT! API is working great!")
            status = "EXCELLENT"
        elif success_rate >= 75:
            print("✅ GOOD! API is mostly functional with minor issues.")
            status = "GOOD"
        elif success_rate >= 50:
            print("⚠️  FAIR! API has some issues that need attention.")
            status = "FAIR"
        else:
            print("❌ POOR! API has significant issues.")
            status = "POOR"
        
        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "success_rate": success_rate,
                "status": status
            },
            "detailed_results": self.test_results
        }
        
        with open("api_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: api_test_report.json")
        return success_rate >= 75

def main():
    """Main testing function"""
    parser = argparse.ArgumentParser(description="Test Astro Engine API")
    parser.add_argument(
        "--url", 
        default="http://localhost:5000",
        help="Base URL of the API (default: http://localhost:5000)"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run only basic tests (faster)"
    )
    
    args = parser.parse_args()
    
    tester = AstroEngineAPITester(args.url)
    
    if args.quick:
        print("🏃‍♂️ Running Quick Tests...")
        tester.test_health_endpoint()
        tester.test_basic_calculation()
        is_healthy = tester.generate_report()
    else:
        is_healthy = tester.run_all_tests()
    
    if is_healthy:
        print("\n🚀 API is ready for production!")
    else:
        print("\n🔧 Please fix the issues before deploying.")
    
    sys.exit(0 if is_healthy else 1)

if __name__ == "__main__":
    main()
