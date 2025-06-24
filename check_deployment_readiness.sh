#!/bin/bash
# 🔍 Astro Engine - GCP Deployment Readiness Check
# This script verifies that the project is ready for Google Cloud deployment

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 ASTRO ENGINE - GCP DEPLOYMENT READINESS CHECK${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

passed=0
failed=0

# Function to check if a file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ $1${NC}"
        ((passed++))
    else
        echo -e "${RED}❌ $1 (missing)${NC}"
        ((failed++))
    fi
}

# Function to check if a directory exists
check_directory() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅ $1${NC}"
        ((passed++))
    else
        echo -e "${RED}❌ $1 (missing)${NC}"
        ((failed++))
    fi
}

# Function to check application health
check_app_health() {
    echo -e "${BLUE}📊 Checking Application Health...${NC}"
    
    # Check if app is running
    if curl -s http://127.0.0.1:5000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Application is running and healthy${NC}"
        ((passed++))
        
        # Test API endpoint
        if curl -s -X POST http://127.0.0.1:5000/lahiri/natal \
           -H "Content-Type: application/json" \
           -d '{"user_name":"Test","birth_date":"1990-01-15","birth_time":"10:30:00","latitude":"28.6139","longitude":"77.2090","timezone_offset":5.5}' \
           | grep -q "ascendant"; then
            echo -e "${GREEN}✅ API endpoints working correctly${NC}"
            ((passed++))
        else
            echo -e "${YELLOW}⚠️  API endpoints may have issues${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Application not running (start with: python -m astro_engine)${NC}"
    fi
}

echo -e "${BLUE}📁 Checking Core Files...${NC}"
check_file "astro_engine/__main__.py"
check_file "astro_engine/app.py"
check_file "requirements.txt"
check_file "requirements-prod.txt"
check_file "Dockerfile"
check_file "docker-compose.yml"
check_file ".env.production"

echo ""
echo -e "${BLUE}📁 Checking GCP Deployment Files...${NC}"
check_file "deployment/google-cloud/deploy-gcp.sh"
check_file "deployment/google-cloud/Dockerfile.gcp"
check_file "deployment/google-cloud/cloudbuild.yaml"
check_file "deployment/google-cloud/gcp-config.env"
check_file "deployment/google-cloud/.env.gcp"

echo ""
echo -e "${BLUE}📁 Checking Infrastructure Components...${NC}"
check_directory "astro_engine/ephe"
check_directory "astro_engine/engine"
check_directory "astro_engine/engine/routes"
check_directory "deployment/google-cloud/terraform"

echo ""
echo -e "${BLUE}📁 Checking Documentation...${NC}"
check_file "README.md"
check_file "docs/deployment/DEPLOYMENT_STATUS.md"

echo ""
check_app_health

echo ""
echo -e "${BLUE}📋 DEPLOYMENT READINESS SUMMARY${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}✅ Passed: $passed checks${NC}"
if [ $failed -gt 0 ]; then
    echo -e "${RED}❌ Failed: $failed checks${NC}"
fi

echo ""
if [ $failed -eq 0 ]; then
    echo -e "${GREEN}🎉 READY FOR GCP DEPLOYMENT!${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo -e "${BLUE}1. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install${NC}"
    echo -e "${BLUE}2. Run: gcloud auth login${NC}"
    echo -e "${BLUE}3. Run: gcloud auth configure-docker${NC}"
    echo -e "${BLUE}4. Update deployment/google-cloud/gcp-config.env with your project details${NC}"
    echo -e "${BLUE}5. Run: cd deployment/google-cloud && ./deploy-gcp.sh${NC}"
    exit 0
else
    echo -e "${RED}🚨 NOT READY FOR DEPLOYMENT${NC}"
    echo -e "${YELLOW}Please fix the missing files/issues above before deploying.${NC}"
    exit 1
fi
