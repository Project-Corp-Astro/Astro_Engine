#!/usr/bin/env python3
"""
Production Readiness Assessment for Astro Engine
Comprehensive check of all production components
"""

import os
import sys
import json
import requests
import subprocess
from pathlib import Path
from datetime import datetime

class ProductionReadinessChecker:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.passed = 0
        self.total = 0
        
    def check(self, description, condition, is_critical=True):
        """Run a check and track results"""
        self.total += 1
        status = "✅ PASS" if condition else ("❌ CRITICAL" if is_critical else "⚠️  WARNING")
        print(f"{status} {description}")
        
        if condition:
            self.passed += 1
        else:
            if is_critical:
                self.errors.append(description)
            else:
                self.warnings.append(description)
        
        return condition
    
    def check_files(self):
        """Check all required production files"""
        print("\n📁 CHECKING PRODUCTION FILES...")
        
        files = {
            "astro_engine/app.py": True,
            "Dockerfile": True,
            "docker-compose.yml": True,
            "gunicorn.conf.py": True,
            "nginx.conf": True,
            ".env.production": True,
            ".env.development": True,
            "requirements.txt": True,
            "requirements-prod.txt": True,
            "ultimate_deploy.sh": True,
            "verify_deployment.py": True,
        }
        
        for file_path, is_critical in files.items():
            exists = (self.project_root / file_path).exists()
            self.check(f"File exists: {file_path}", exists, is_critical)
    
    def check_dependencies(self):
        """Check Python dependencies are installed"""
        print("\n📦 CHECKING PYTHON DEPENDENCIES...")
        
        production_deps = [
            "flask", "gunicorn", "gevent", "redis", "prometheus_client",
            "flask_limiter", "flask_cors", "structlog", "celery", "psutil"
        ]
        
        for dep in production_deps:
            try:
                __import__(dep)
                self.check(f"Dependency: {dep}", True, True)
            except ImportError:
                self.check(f"Dependency: {dep}", False, True)
    
    def check_server_running(self):
        """Check if server is running and responsive"""
        print("\n🚀 CHECKING SERVER STATUS...")
        
        try:
            # Health check
            response = requests.get("http://localhost:5001/health", timeout=5)
            self.check("Health endpoint responding", response.status_code == 200)
            
            if response.status_code == 200:
                health_data = response.json()
                self.check("Swiss Ephemeris service", 
                          health_data.get("services", {}).get("swiss_ephemeris") == "ok")
                self.check("API endpoints service", 
                          health_data.get("services", {}).get("api_endpoints") == "ok")
        except Exception as e:
            self.check("Server responding", False, True)
            return False
            
        return True
    
    def check_endpoints(self):
        """Check key endpoints are working"""
        print("\n🔗 CHECKING API ENDPOINTS...")
        
        if not self.check_server_running():
            return
        
        test_data = {
            "user_name": "Production Test",
            "birth_date": "1990-01-01",
            "birth_time": "12:00:00",
            "latitude": 28.7041,
            "longitude": 77.1025,
            "timezone_offset": 5.5
        }
        
        endpoints = [
            ("GET", "/cache/stats", None),
            ("GET", "/metrics", None),
            ("GET", "/metrics/performance", None),
            ("GET", "/logging/status", None),
            ("POST", "/lahiri/natal", test_data),
        ]
        
        for method, endpoint, data in endpoints:
            try:
                if method == "POST":
                    response = requests.post(f"http://localhost:5001{endpoint}", json=data, timeout=10)
                else:
                    response = requests.get(f"http://localhost:5001{endpoint}", timeout=10)
                
                self.check(f"{method} {endpoint}", response.status_code == 200)
            except Exception as e:
                self.check(f"{method} {endpoint}", False, True)
    
    def check_redis(self):
        """Check Redis connection"""
        print("\n🗄️  CHECKING REDIS...")
        
        try:
            response = requests.get("http://localhost:5001/cache/stats", timeout=5)
            if response.status_code == 200:
                cache_data = response.json()
                redis_available = cache_data.get("redis_available", False)
                self.check("Redis connection", redis_available)
                
                if redis_available:
                    redis_info = cache_data.get("redis_info", {})
                    self.check("Redis memory usage reasonable", 
                              float(redis_info.get("used_memory", "0M").replace("M", "")) < 100)
            else:
                self.check("Redis status check", False)
        except Exception:
            self.check("Redis status check", False)
    
    def check_security(self):
        """Check security configurations"""
        print("\n🔒 CHECKING SECURITY...")
        
        # Check .env.production
        env_prod = self.project_root / ".env.production"
        if env_prod.exists():
            content = env_prod.read_text()
            self.check("Production env has secret key", "SECRET_KEY=" in content)
            self.check("Debug disabled in production", "FLASK_DEBUG=false" in content)
            self.check("Production environment set", "FLASK_ENV=production" in content)
            
            # Warning for default secret
            if "your-super-secret-key-change-this-in-production" in content:
                self.check("Secret key changed from default", False, False)
        else:
            self.check("Production environment file", False)
    
    def check_docker(self):
        """Check Docker configuration"""
        print("\n🐳 CHECKING DOCKER CONFIGURATION...")
        
        # Check if Docker is available
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            docker_available = result.returncode == 0
            self.check("Docker installed", docker_available, False)
        except FileNotFoundError:
            self.check("Docker installed", False, False)
        
        # Check Dockerfile
        dockerfile = self.project_root / "Dockerfile"
        if dockerfile.exists():
            content = dockerfile.read_text()
            self.check("Dockerfile uses non-root user", "USER astro" in content)
            self.check("Dockerfile has health check", "HEALTHCHECK" in content)
            self.check("Dockerfile uses production image", "python:3.11-slim" in content)
        
        # Check docker-compose.yml
        compose_file = self.project_root / "docker-compose.yml"
        if compose_file.exists():
            content = compose_file.read_text()
            self.check("Docker Compose has Redis", "redis:" in content)
            self.check("Docker Compose has Nginx", "nginx:" in content)
            self.check("Docker Compose has health checks", "healthcheck:" in content)
    
    def check_monitoring(self):
        """Check monitoring capabilities"""
        print("\n📊 CHECKING MONITORING...")
        
        try:
            # Check metrics endpoint
            response = requests.get("http://localhost:5001/metrics", timeout=5)
            if response.status_code == 200:
                metrics_text = response.text
                self.check("Prometheus metrics exposed", len(metrics_text) > 1000)
                self.check("Cache metrics present", "astro_engine_cache" in metrics_text)
                self.check("API metrics present", "astro_engine_api" in metrics_text)
            else:
                self.check("Metrics endpoint", False)
                
            # Check performance endpoint
            response = requests.get("http://localhost:5001/metrics/performance", timeout=5)
            self.check("Performance metrics endpoint", response.status_code == 200)
            
        except Exception:
            self.check("Monitoring endpoints", False)
    
    def run_assessment(self):
        """Run complete production readiness assessment"""
        print("🌟 ASTRO ENGINE - PRODUCTION READINESS ASSESSMENT")
        print("=" * 60)
        
        self.check_files()
        self.check_dependencies()
        self.check_server_running()
        self.check_endpoints()
        self.check_redis()
        self.check_security()
        self.check_docker()
        self.check_monitoring()
        
        print("\n" + "=" * 60)
        print("📊 PRODUCTION READINESS SUMMARY")
        print("=" * 60)
        
        success_rate = (self.passed / self.total) * 100 if self.total > 0 else 0
        
        print(f"✅ Tests Passed: {self.passed}/{self.total} ({success_rate:.1f}%)")
        
        if self.errors:
            print(f"❌ Critical Issues: {len(self.errors)}")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"⚠️  Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        print("\n🎯 PRODUCTION READINESS STATUS:")
        if success_rate >= 95 and len(self.errors) == 0:
            print("🟢 EXCELLENT - Ready for production deployment!")
            return 0
        elif success_rate >= 80 and len(self.errors) <= 2:
            print("🟡 GOOD - Minor issues to address before production")
            return 1
        else:
            print("🔴 NOT READY - Critical issues must be resolved")
            return 2

if __name__ == "__main__":
    checker = ProductionReadinessChecker()
    exit_code = checker.run_assessment()
    sys.exit(exit_code)
