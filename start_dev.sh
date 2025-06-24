#!/bin/bash
# 🚀 Astro Engine Development Startup Script

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🌟 Starting Astro Engine Development Server${NC}"
echo "============================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Install/upgrade dependencies
echo -e "${GREEN}📥 Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export FLASK_ENV="development"
export FLASK_DEBUG="true"

# Check Redis connection
echo -e "${GREEN}🔍 Checking Redis connection...${NC}"
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Redis is not running. Starting Redis...${NC}"
    if command -v brew &> /dev/null; then
        brew services start redis
    else
        echo -e "${RED}❌ Please start Redis manually${NC}"
        exit 1
    fi
fi

# Start the application
echo -e "${GREEN}🚀 Starting Astro Engine...${NC}"
python -m astro_engine

echo -e "${GREEN}✅ Astro Engine started successfully!${NC}"
