#!/usr/bin/env python3
"""
Deployment Verification Script for Astro Engine
Validates all production configurations and dependencies
"""

import os
import sys
import json
import subprocess
import importlib.util
from pathlib import Path

class DeploymentVerifier:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.checks_passed = 0
        self.total_checks = 0
        
    def check(self, description, condition, error_msg=None, warning_msg=None):
        """Run a verification check"""
        self.total_checks += 1
        if condition:
            print(f"✅ {description}")
            self.checks_passed += 1
            return True
        else:
            if error_msg:
                print(f"❌ {description}: {error_msg}")
                self.errors.append(f"{description}: {error_msg}")
            elif warning_msg:
                print(f"⚠️  {description}: {warning_msg}")
                self.warnings.append(f"{description}: {warning_msg}")
            else:
                print(f"❌ {description}")
                self.errors.append(description)
            return False
    
    def verify_files_exist(self):
        """Verify all required files exist"""
        print("\n🔍 Checking Required Files...")
        
        required_files = [
            "astro_engine/app.py",
            "requirements.txt",
            "requirements-prod.txt",
            "Dockerfile",
            "docker-compose.yml",
            "gunicorn.conf.py",
            "nginx.conf",
            "deploy.sh",
            ".env.production",
            ".env.development",
            "README.md",
            "DIGITALOCEAN_DEPLOYMENT.md"
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            self.check(
                f"File exists: {file_path}",
                full_path.exists(),
                f"Missing required file: {file_path}"
            )
    
    def verify_python_dependencies(self):
        """Verify Python dependencies are installable"""
        print("\n📦 Checking Python Dependencies...")
        
        requirements_files = ["requirements.txt", "requirements-prod.txt"]
        
        for req_file in requirements_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                try:
                    with open(req_path, 'r') as f:
                        deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    
                    self.check(
                        f"Dependencies parseable: {req_file}",
                        len(deps) > 0,
                        f"No dependencies found in {req_file}"
                    )
                    
                    # Check for critical dependencies
                    critical_deps = ['Flask', 'redis', 'gunicorn']
                    for dep in critical_deps:
                        has_dep = any(dep.lower() in line.lower() for line in deps)
                        self.check(
                            f"Critical dependency {dep} in {req_file}",
                            has_dep,
                            f"Missing critical dependency: {dep}"
                        )
                        
                except Exception as e:
                    self.check(
                        f"Requirements file readable: {req_file}",
                        False,
                        f"Error reading {req_file}: {e}"
                    )
    
    def verify_environment_files(self):
        """Verify environment configuration files"""
        print("\n🌍 Checking Environment Configuration...")
        
        env_files = [".env.development", ".env.production"]
        required_vars = [
            "FLASK_ENV",
            "SECRET_KEY",
            "REDIS_URL"
        ]
        
        for env_file in env_files:
            env_path = self.project_root / env_file
            if env_path.exists():
                try:
                    with open(env_path, 'r') as f:
                        content = f.read()
                    
                    for var in required_vars:
                        has_var = var in content
                        self.check(
                            f"Environment variable {var} in {env_file}",
                            has_var,
                            f"Missing environment variable: {var}"
                        )
                        
                except Exception as e:
                    self.check(
                        f"Environment file readable: {env_file}",
                        False,
                        f"Error reading {env_file}: {e}"
                    )
    
    def verify_docker_configuration(self):
        """Verify Docker configuration"""
        print("\n🐳 Checking Docker Configuration...")
        
        # Check Dockerfile
        dockerfile_path = self.project_root / "Dockerfile"
        if dockerfile_path.exists():
            try:
                with open(dockerfile_path, 'r') as f:
                    dockerfile_content = f.read()
                
                required_instructions = [
                    "FROM python:",
                    "WORKDIR",
                    "COPY requirements",
                    "RUN pip install",
                    "EXPOSE"
                ]
                
                for instruction in required_instructions:
                    has_instruction = instruction in dockerfile_content
                    self.check(
                        f"Dockerfile has {instruction}",
                        has_instruction,
                        f"Missing Dockerfile instruction: {instruction}"
                    )
                    
            except Exception as e:
                self.check(
                    "Dockerfile readable",
                    False,
                    f"Error reading Dockerfile: {e}"
                )
        
        # Check docker-compose.yml
        compose_path = self.project_root / "docker-compose.yml"
        if compose_path.exists():
            try:
                with open(compose_path, 'r') as f:
                    compose_content = f.read()
                
                required_services = ["astro-engine", "redis", "nginx"]
                for service in required_services:
                    has_service = service in compose_content
                    self.check(
                        f"Docker Compose has {service} service",
                        has_service,
                        f"Missing Docker Compose service: {service}"
                    )
                    
            except Exception as e:
                self.check(
                    "docker-compose.yml readable",
                    False,
                    f"Error reading docker-compose.yml: {e}"
                )
    
    def verify_application_structure(self):
        """Verify application structure"""
        print("\n🏗️ Checking Application Structure...")
        
        app_path = self.project_root / "astro_engine" / "app.py"
        if app_path.exists():
            try:
                with open(app_path, 'r') as f:
                    app_content = f.read()
                
                required_imports = [
                    "from flask import",
                    "from flask_limiter"
                ]
                
                for import_stmt in required_imports:
                    has_import = import_stmt in app_content
                    self.check(
                        f"Application has import: {import_stmt}",
                        has_import,
                        f"Missing import in app.py: {import_stmt}"
                    )
                
                # Check for essential routes
                essential_routes = ["/health", "/metrics"]
                for route in essential_routes:
                    has_route = route in app_content
                    self.check(
                        f"Application has route: {route}",
                        has_route,
                        f"Missing route in app.py: {route}"
                    )
                    
            except Exception as e:
                self.check(
                    "app.py readable",
                    False,
                    f"Error reading app.py: {e}"
                )
    
    def verify_documentation(self):
        """Verify documentation completeness"""
        print("\n📚 Checking Documentation...")
        
        readme_path = self.project_root / "README.md"
        if readme_path.exists():
            try:
                with open(readme_path, 'r') as f:
                    readme_content = f.read()
                
                required_sections = [
                    "# 🌟 Astro Engine",
                    "## 🚀 Quick Start Guide",
                    "## 📡 API Documentation",
                    "## 🐳 Docker Deployment",
                    "## 🏗️ Architecture"
                ]
                
                for section in required_sections:
                    has_section = section in readme_content
                    self.check(
                        f"README has section: {section}",
                        has_section,
                        f"Missing README section: {section}"
                    )
                    
                # Check README length (should be comprehensive)
                lines = readme_content.split('\n')
                self.check(
                    "README is comprehensive (>1000 lines)",
                    len(lines) > 1000,
                    f"README is only {len(lines)} lines, might need more detail"
                )
                
            except Exception as e:
                self.check(
                    "README.md readable",
                    False,
                    f"Error reading README.md: {e}"
                )
    
    def verify_deployment_script(self):
        """Verify deployment script"""
        print("\n🚀 Checking Deployment Script...")
        
        deploy_path = self.project_root / "deploy.sh"
        if deploy_path.exists():
            try:
                with open(deploy_path, 'r') as f:
                    deploy_content = f.read()
                
                required_commands = [
                    "docker-compose",
                    "systemctl",
                    "ufw",
                    "certbot"
                ]
                
                for command in required_commands:
                    has_command = command in deploy_content
                    self.check(
                        f"Deploy script uses: {command}",
                        has_command,
                        warning_msg=f"Deploy script might be missing: {command}"
                    )
                
                # Check if script is executable
                is_executable = os.access(deploy_path, os.X_OK)
                self.check(
                    "Deploy script is executable",
                    is_executable,
                    "Deploy script should be executable (chmod +x deploy.sh)"
                )
                
            except Exception as e:
                self.check(
                    "deploy.sh readable",
                    False,
                    f"Error reading deploy.sh: {e}"
                )
    
    def check_system_requirements(self):
        """Check system requirements"""
        print("\n🖥️ Checking System Requirements...")
        
        # Check Python version
        python_version = sys.version_info
        self.check(
            "Python 3.8+",
            python_version >= (3, 8),
            f"Python {python_version.major}.{python_version.minor} < 3.8"
        )
        
        # Check for Docker (if available)
        try:
            result = subprocess.run(
                ["docker", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            self.check(
                "Docker available",
                result.returncode == 0,
                "Docker not installed or not in PATH"
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.check(
                "Docker available",
                False,
                "Docker not installed or not accessible"
            )
        
        # Check for docker-compose
        try:
            result = subprocess.run(
                ["docker-compose", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            self.check(
                "Docker Compose available",
                result.returncode == 0,
                "Docker Compose not installed or not in PATH"
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.check(
                "Docker Compose available",
                False,
                "Docker Compose not installed or not accessible"
            )
    
    def generate_report(self):
        """Generate final verification report"""
        print("\n" + "="*60)
        print("📋 DEPLOYMENT VERIFICATION REPORT")
        print("="*60)
        
        success_rate = (self.checks_passed / self.total_checks) * 100 if self.total_checks > 0 else 0
        
        print(f"✅ Checks Passed: {self.checks_passed}/{self.total_checks} ({success_rate:.1f}%)")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        print("\n" + "="*60)
        
        if success_rate >= 90 and len(self.errors) == 0:
            print("🎉 DEPLOYMENT READY! Your Astro Engine is production-ready!")
            print("👉 Next step: Run './deploy.sh' on your DigitalOcean droplet")
            return True
        elif success_rate >= 80:
            print("⚠️  MOSTLY READY - Please fix the errors above before deploying")
            return False
        else:
            print("❌ NOT READY - Multiple issues need to be resolved")
            return False
    
    def run_all_checks(self):
        """Run all verification checks"""
        print("🔍 Starting Astro Engine Deployment Verification...")
        print("="*60)
        
        self.verify_files_exist()
        self.verify_python_dependencies()
        self.verify_environment_files()
        self.verify_docker_configuration()
        self.verify_application_structure()
        self.verify_documentation()
        self.verify_deployment_script()
        self.check_system_requirements()
        
        return self.generate_report()

def main():
    """Main verification function"""
    verifier = DeploymentVerifier()
    is_ready = verifier.run_all_checks()
    
    if is_ready:
        print("\n🚀 Ready for deployment!")
        print("Run this command on your DigitalOcean droplet:")
        print("./deploy.sh")
    else:
        print("\n🔧 Please fix the issues above before deploying.")
    
    sys.exit(0 if is_ready else 1)

if __name__ == "__main__":
    main()
