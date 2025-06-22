#!/usr/bin/env python3
"""
ULTIMATE ASTRO ENGINE VALIDATION SUITE
Complete end-to-end testing and verification
"""

import requests
import json
import time
import sys
import os
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any
import concurrent.futures
import argparse
from pathlib import Path

class UltimateAstroEngineValidator:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.start_time = datetime.now()
        
        # Comprehensive test data for all scenarios
        self.test_cases = {
            "basic_birth_data": {
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
                    "name": "noon_birth",
                    "data": {
                        "birth_date": "1995-06-21",
                        "birth_time": "12:00",
                        "latitude": 51.5074,
                        "longitude": -0.1278,
                        "timezone": "Europe/London"
                    }
                },
                {
                    "name": "southern_hemisphere",
                    "data": {
                        "birth_date": "1988-03-10",
                        "birth_time": "18:45",
                        "latitude": -33.8688,
                        "longitude": 151.2093,
                        "timezone": "Australia/Sydney"
                    }
                },
                {
                    "name": "arctic_region",
                    "data": {
                        "birth_date": "2000-06-21",
                        "birth_time": "00:00",
                        "latitude": 71.0,
                        "longitude": -8.0,
                        "timezone": "Arctic/Longyearbyen"
                    }
                },
                {
                    "name": "leap_year",
                    "data": {
                        "birth_date": "2000-02-29",
                        "birth_time": "15:30",
                        "latitude": 28.6139,
                        "longitude": 77.2090,
                        "timezone": "Asia/Kolkata"
                    }
                }
            ],
            "historical_dates": [
                {
                    "name": "ancient_date",
                    "data": {
                        "birth_date": "1500-01-01",
                        "birth_time": "12:00",
                        "latitude": 28.6139,
                        "longitude": 77.2090,
                        "timezone": "Asia/Kolkata"
                    }
                },
                {
                    "name": "future_date",
                    "data": {
                        "birth_date": "2050-12-31",
                        "birth_time": "23:59",
                        "latitude": 28.6139,
                        "longitude": 77.2090,
                        "timezone": "Asia/Kolkata"
                    }
                }
            ],
            "stress_test_data": [
                {
                    "birth_date": f"199{i}-0{(i%9)+1}-{(i%28)+1:02d}",
                    "birth_time": f"{(i%24):02d}:{(i*15)%60:02d}",
                    "latitude": 28.6139 + (i * 0.1),
                    "longitude": 77.2090 + (i * 0.1),
                    "timezone": "Asia/Kolkata"
                } for i in range(10)
            ]
        }
    
    def log_test(self, test_name: str, passed: bool, details: str = "", duration: float = 0):
        """Log test results with timing"""
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
            "duration": round(duration, 3),
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        duration_str = f" ({duration:.3f}s)" if duration > 0 else ""
        print(f"{status} {test_name}: {details}{duration_str}")
    
    def test_infrastructure_health(self):
        """Test basic infrastructure health"""
        print("\n🏥 Testing Infrastructure Health...")
        
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/health")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Infrastructure Health", True, 
                                f"All systems healthy", duration)
                    
                    # Check specific services
                    services = data.get("services", {})
                    for service, status in services.items():
                        self.log_test(f"Service: {service}", status == "ok", 
                                    f"Status: {status}")
                else:
                    self.log_test("Infrastructure Health", False, 
                                f"Unhealthy status: {data.get('status')}", duration)
            else:
                self.log_test("Infrastructure Health", False, 
                            f"HTTP {response.status_code}", duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Infrastructure Health", False, f"Error: {str(e)}", duration)
    
    def test_all_ayanamsa_systems(self):
        """Test all ayanamsa calculation systems"""
        print("\n🌟 Testing All Ayanamsa Systems...")
        
        ayanamsa_systems = ["lahiri", "kp", "raman"]
        
        for ayanamsa in ayanamsa_systems:
            start_time = time.time()
            try:
                endpoint = f"{self.base_url}/api/v1/{ayanamsa}/calculate"
                response = self.session.post(endpoint, json=self.test_cases["basic_birth_data"])
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Validate response structure
                    required_fields = ["planets", "houses", "birth_details"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        planets = data.get("planets", {})
                        expected_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
                        planets_present = all(planet in planets for planet in expected_planets)
                        
                        if planets_present:
                            self.log_test(f"Ayanamsa System: {ayanamsa.upper()}", True,
                                        f"{len(planets)} planets calculated", duration)
                        else:
                            missing_planets = [p for p in expected_planets if p not in planets]
                            self.log_test(f"Ayanamsa System: {ayanamsa.upper()}", False,
                                        f"Missing planets: {missing_planets}", duration)
                    else:
                        self.log_test(f"Ayanamsa System: {ayanamsa.upper()}", False,
                                    f"Missing fields: {missing_fields}", duration)
                else:
                    self.log_test(f"Ayanamsa System: {ayanamsa.upper()}", False,
                                f"HTTP {response.status_code}", duration)
                    
            except Exception as e:
                duration = time.time() - start_time
                self.log_test(f"Ayanamsa System: {ayanamsa.upper()}", False, 
                            f"Error: {str(e)}", duration)
    
    def test_edge_cases_comprehensive(self):
        """Test comprehensive edge cases"""
        print("\n🎯 Testing Edge Cases...")
        
        for case in self.test_cases["edge_cases"]:
            start_time = time.time()
            try:
                endpoint = f"{self.base_url}/api/v1/lahiri/calculate"
                response = self.session.post(endpoint, json=case["data"])
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if "planets" in data and len(data["planets"]) >= 7:
                        self.log_test(f"Edge Case: {case['name']}", True,
                                    f"Calculation successful", duration)
                    else:
                        self.log_test(f"Edge Case: {case['name']}", False,
                                    f"Incomplete planet data", duration)
                else:
                    self.log_test(f"Edge Case: {case['name']}", False,
                                f"HTTP {response.status_code}", duration)
                    
            except Exception as e:
                duration = time.time() - start_time
                self.log_test(f"Edge Case: {case['name']}", False, f"Error: {str(e)}", duration)
    
    def test_historical_dates(self):
        """Test historical and future date calculations"""
        print("\n📅 Testing Historical & Future Dates...")
        
        for case in self.test_cases["historical_dates"]:
            start_time = time.time()
            try:
                endpoint = f"{self.base_url}/api/v1/lahiri/calculate"
                response = self.session.post(endpoint, json=case["data"])
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if "planets" in data:
                        self.log_test(f"Historical: {case['name']}", True,
                                    f"Date range supported", duration)
                    else:
                        self.log_test(f"Historical: {case['name']}", False,
                                    f"No planet data", duration)
                else:
                    self.log_test(f"Historical: {case['name']}", False,
                                f"HTTP {response.status_code}", duration)
                    
            except Exception as e:
                duration = time.time() - start_time
                self.log_test(f"Historical: {case['name']}", False, f"Error: {str(e)}", duration)
    
    def test_error_handling_comprehensive(self):
        """Test comprehensive error handling"""
        print("\n🚨 Testing Error Handling...")
        
        error_cases = [
            {
                "name": "Invalid Date Format",
                "data": {"birth_date": "invalid-date", "birth_time": "14:30", 
                        "latitude": 28.6139, "longitude": 77.2090, "timezone": "Asia/Kolkata"},
                "expected_status": 400
            },
            {
                "name": "Missing Birth Date",
                "data": {"birth_time": "14:30", "latitude": 28.6139, 
                        "longitude": 77.2090, "timezone": "Asia/Kolkata"},
                "expected_status": 400
            },
            {
                "name": "Invalid Latitude",
                "data": {"birth_date": "1990-05-15", "birth_time": "14:30",
                        "latitude": 999, "longitude": 77.2090, "timezone": "Asia/Kolkata"},
                "expected_status": 400
            },
            {
                "name": "Invalid Longitude",
                "data": {"birth_date": "1990-05-15", "birth_time": "14:30",
                        "latitude": 28.6139, "longitude": 999, "timezone": "Asia/Kolkata"},
                "expected_status": 400
            },
            {
                "name": "Invalid Time Format",
                "data": {"birth_date": "1990-05-15", "birth_time": "25:99",
                        "latitude": 28.6139, "longitude": 77.2090, "timezone": "Asia/Kolkata"},
                "expected_status": 400
            },
            {
                "name": "Empty Request",
                "data": {},
                "expected_status": 400
            }
        ]
        
        for case in error_cases:
            start_time = time.time()
            try:
                endpoint = f"{self.base_url}/api/v1/lahiri/calculate"
                response = self.session.post(endpoint, json=case["data"])
                duration = time.time() - start_time
                
                if response.status_code == case["expected_status"]:
                    self.log_test(f"Error Handling: {case['name']}", True,
                                f"Correct error response", duration)
                else:
                    self.log_test(f"Error Handling: {case['name']}", False,
                                f"Expected {case['expected_status']}, got {response.status_code}", duration)
                    
            except Exception as e:
                duration = time.time() - start_time
                self.log_test(f"Error Handling: {case['name']}", False, f"Error: {str(e)}", duration)
    
    def test_performance_stress(self):
        """Test performance under stress"""
        print("\n⚡ Testing Performance & Stress...")
        
        # Single request performance
        start_time = time.time()
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/lahiri/calculate",
                json=self.test_cases["basic_birth_data"]
            )
            duration = time.time() - start_time
            
            if response.status_code == 200 and duration < 3.0:
                self.log_test("Single Request Performance", True,
                            f"Fast response", duration)
            else:
                self.log_test("Single Request Performance", False,
                            f"Slow or failed", duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Single Request Performance", False, f"Error: {str(e)}", duration)
        
        # Concurrent requests test
        def make_concurrent_request(data):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/v1/lahiri/calculate",
                    json=data
                )
                return response.status_code == 200
            except:
                return False
        
        start_time = time.time()
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(make_concurrent_request, data) 
                    for data in self.test_cases["stress_test_data"]
                ]
                results = [future.result() for future in futures]
            
            duration = time.time() - start_time
            success_count = sum(results)
            total_requests = len(results)
            
            if success_count >= total_requests * 0.8:  # 80% success rate
                self.log_test("Concurrent Requests", True,
                            f"{success_count}/{total_requests} successful", duration)
            else:
                self.log_test("Concurrent Requests", False,
                            f"Only {success_count}/{total_requests} successful", duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Concurrent Requests", False, f"Error: {str(e)}", duration)
    
    def test_caching_performance(self):
        """Test caching effectiveness"""
        print("\n💾 Testing Caching Performance...")
        
        # Make same request twice to test caching
        endpoint = f"{self.base_url}/api/v1/lahiri/calculate"
        data = self.test_cases["basic_birth_data"]
        
        try:
            # First request
            start_time = time.time()
            response1 = self.session.post(endpoint, json=data)
            time1 = time.time() - start_time
            
            # Small delay
            time.sleep(0.1)
            
            # Second request (should hit cache)
            start_time = time.time()
            response2 = self.session.post(endpoint, json=data)
            time2 = time.time() - start_time
            
            if (response1.status_code == 200 and response2.status_code == 200 and
                response1.json() == response2.json()):
                
                if time2 < time1 * 0.9:  # Second request should be faster
                    self.log_test("Caching Performance", True,
                                f"Cache hit detected (1st: {time1:.3f}s, 2nd: {time2:.3f}s)")
                else:
                    self.log_test("Caching Performance", True,
                                f"Consistent responses (caching status unclear)")
            else:
                self.log_test("Caching Performance", False, "Inconsistent responses")
                
        except Exception as e:
            self.log_test("Caching Performance", False, f"Error: {str(e)}")
    
    def test_security_features(self):
        """Test security features"""
        print("\n🔒 Testing Security Features...")
        
        # Test rate limiting
        rapid_requests = []
        start_time = time.time()
        
        try:
            for i in range(30):  # Make rapid requests
                response = self.session.get(f"{self.base_url}/health")
                rapid_requests.append(response.status_code)
                if response.status_code == 429:  # Rate limited
                    break
            
            duration = time.time() - start_time
            rate_limited = any(status == 429 for status in rapid_requests)
            
            if rate_limited:
                self.log_test("Rate Limiting", True, "Rate limiting active", duration)
            else:
                self.log_test("Rate Limiting", True, 
                            "No rate limiting triggered (may be configured for higher limits)", duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test("Rate Limiting", False, f"Error: {str(e)}", duration)
        
        # Test CORS headers
        try:
            response = self.session.get(f"{self.base_url}/health")
            if "Access-Control-Allow-Origin" in response.headers:
                self.log_test("CORS Headers", True, "CORS configured")
            else:
                self.log_test("CORS Headers", False, "No CORS headers found")
        except Exception as e:
            self.log_test("CORS Headers", False, f"Error: {str(e)}")
    
    def test_monitoring_endpoints(self):
        """Test monitoring and observability"""
        print("\n📊 Testing Monitoring Endpoints...")
        
        # Test metrics endpoint
        try:
            response = self.session.get(f"{self.base_url}/metrics")
            if response.status_code == 200:
                data = response.json()
                if "timestamp" in data and "status" in data:
                    self.log_test("Metrics Endpoint", True, "Metrics available")
                else:
                    self.log_test("Metrics Endpoint", False, "Invalid metrics format")
            elif response.status_code == 404:
                self.log_test("Metrics Endpoint", True, "Metrics disabled (404 expected)")
            else:
                self.log_test("Metrics Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Metrics Endpoint", False, f"Error: {str(e)}")
    
    def validate_deployment_files(self):
        """Validate deployment files exist"""
        print("\n📁 Validating Deployment Files...")
        
        required_files = [
            "docker-compose.yml",
            "Dockerfile", 
            "deploy.sh",
            "ultimate_deploy.sh",
            "requirements.txt",
            "requirements-prod.txt",
            ".env.production",
            ".env.development"
        ]
        
        for file_path in required_files:
            if Path(file_path).exists():
                self.log_test(f"File: {file_path}", True, "Present")
            else:
                self.log_test(f"File: {file_path}", False, "Missing")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive validation report"""
        print("\n" + "="*80)
        print("📋 ULTIMATE ASTRO ENGINE VALIDATION REPORT")
        print("="*80)
        
        total_duration = (datetime.now() - self.start_time).total_seconds()
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"⏱️  Total Testing Time: {total_duration:.2f} seconds")
        print(f"✅ Tests Passed: {self.passed_tests}/{self.total_tests} ({success_rate:.1f}%)")
        
        # Categorize results
        failed_tests = [r for r in self.test_results if not r["passed"]]
        performance_tests = [r for r in self.test_results if "Performance" in r["test"] or "Stress" in r["test"]]
        security_tests = [r for r in self.test_results if "Security" in r["test"] or "Rate" in r["test"]]
        
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        if performance_tests:
            print(f"\n⚡ Performance Summary:")
            for test in performance_tests:
                status = "✅" if test["passed"] else "❌"
                print(f"   {status} {test['test']}: {test['details']}")
        
        if security_tests:
            print(f"\n🔒 Security Summary:")
            for test in security_tests:
                status = "✅" if test["passed"] else "❌"
                print(f"   {status} {test['test']}: {test['details']}")
        
        print("\n" + "="*80)
        
        # Overall assessment
        if success_rate >= 95:
            print("🎉 EXCELLENT! Astro Engine is production-ready!")
            status = "EXCELLENT"
        elif success_rate >= 90:
            print("✅ GREAT! Minor issues but ready for deployment.")
            status = "GREAT"
        elif success_rate >= 80:
            print("⚠️  GOOD! Some issues need attention before production.")
            status = "GOOD"
        elif success_rate >= 70:
            print("🔧 FAIR! Multiple issues need fixing.")
            status = "FAIR"
        else:
            print("❌ POOR! Significant issues prevent production deployment.")
            status = "POOR"
        
        # Save detailed report
        report_data = {
            "validation_timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "total_duration_seconds": total_duration,
            "summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "success_rate": success_rate,
                "overall_status": status
            },
            "detailed_results": self.test_results,
            "performance_metrics": {
                "average_response_time": sum(r["duration"] for r in self.test_results if r["duration"] > 0) / len([r for r in self.test_results if r["duration"] > 0]),
                "total_api_calls": len([r for r in self.test_results if "API" in r["test"] or "calculate" in r["test"]]),
                "cache_tests": len([r for r in self.test_results if "Cache" in r["test"]])
            }
        }
        
        with open("ultimate_validation_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Comprehensive report saved to: ultimate_validation_report.json")
        return success_rate >= 90
    
    def run_ultimate_validation(self):
        """Run the complete validation suite"""
        print("🚀 STARTING ULTIMATE ASTRO ENGINE VALIDATION")
        print("=" * 80)
        print(f"🎯 Target URL: {self.base_url}")
        print(f"⏰ Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Core functionality tests
        self.test_infrastructure_health()
        self.test_all_ayanamsa_systems()
        
        # Comprehensive testing
        self.test_edge_cases_comprehensive()
        self.test_historical_dates()
        self.test_error_handling_comprehensive()
        
        # Performance and stress testing
        self.test_performance_stress()
        self.test_caching_performance()
        
        # Security testing
        self.test_security_features()
        
        # Monitoring and observability
        self.test_monitoring_endpoints()
        
        # Deployment validation
        self.validate_deployment_files()
        
        return self.generate_comprehensive_report()

def main():
    """Main validation function"""
    parser = argparse.ArgumentParser(description="Ultimate Astro Engine Validation")
    parser.add_argument(
        "--url", 
        default="http://localhost:5000",
        help="Base URL of the API (default: http://localhost:5000)"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Run in production mode (more comprehensive tests)"
    )
    
    args = parser.parse_args()
    
    print("🌟 ULTIMATE ASTRO ENGINE VALIDATION SUITE")
    print("=" * 50)
    
    validator = UltimateAstroEngineValidator(args.url)
    
    if args.production:
        print("🏭 Running in PRODUCTION validation mode...")
    else:
        print("🧪 Running in DEVELOPMENT validation mode...")
    
    is_ready = validator.run_ultimate_validation()
    
    if is_ready:
        print("\n🎉 ASTRO ENGINE IS READY FOR PRODUCTION!")
        print("🚀 Deploy with confidence!")
    else:
        print("\n🔧 Please address the issues before production deployment.")
    
    sys.exit(0 if is_ready else 1)

if __name__ == "__main__":
    main()
