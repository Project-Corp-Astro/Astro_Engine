#!/bin/bash
# 🚀 Production Validation Test for Astro Engine

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m' 
NC='\033[0m'

echo -e "${BLUE}🚀 Testing Production Configuration...${NC}"

# Set production environment
export FLASK_ENV=production
export PYTHONPATH="$(pwd)"

# Test with gunicorn (production server)
echo -e "${BLUE}Starting with Gunicorn (Production Mode)...${NC}"

# Start gunicorn in background
gunicorn -w 2 -b 0.0.0.0:5001 astro_engine.app:create_app\(\) &
GUNICORN_PID=$!

sleep 5

# Test endpoints
echo -e "${BLUE}Testing health endpoint...${NC}"
if curl -s http://localhost:5001/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ Health endpoint working${NC}"
else
    echo "❌ Health endpoint failed"
    kill $GUNICORN_PID
    exit 1
fi

echo -e "${BLUE}Testing natal chart API...${NC}"
if curl -s -X POST http://localhost:5001/lahiri/natal \
   -H "Content-Type: application/json" \
   -d '{"user_name":"Test","birth_date":"1990-01-15","birth_time":"10:30:00","latitude":"28.6139","longitude":"77.2090","timezone_offset":5.5}' \
   | grep -q "ascendant"; then
    echo -e "${GREEN}✅ Natal chart API working${NC}"
else
    echo "❌ Natal chart API failed"
    kill $GUNICORN_PID
    exit 1
fi

# Cleanup
kill $GUNICORN_PID

echo -e "${GREEN}🎉 Production validation successful!${NC}"
echo -e "${GREEN}✅ Ready for GCP deployment${NC}"
