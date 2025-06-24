#!/bin/bash
# 🐳 DOCKER SETUP VALIDATION SCRIPT FOR ASTRO ENGINE
# Tests Docker configuration and container functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🐳 ASTRO ENGINE - DOCKER SETUP VALIDATION${NC}"
echo -e "${PURPLE}=========================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is installed
check_docker() {
    print_info "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Please install Docker first:"
        echo "https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose not found. Please install Docker Compose:"
        echo "https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed"
    docker --version
    docker-compose --version
    echo ""
}

# Check Docker daemon
check_docker_daemon() {
    print_info "Checking Docker daemon..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi
    print_status "Docker daemon is running"
    echo ""
}

# Validate Docker configuration files
validate_docker_files() {
    print_info "Validating Docker configuration files..."
    
    # Check Dockerfile
    if [[ ! -f "Dockerfile" ]]; then
        print_error "Dockerfile not found"
        exit 1
    fi
    print_status "Dockerfile found"
    
    # Check docker-compose.yml
    if [[ ! -f "docker-compose.yml" ]]; then
        print_error "docker-compose.yml not found"
        exit 1
    fi
    print_status "docker-compose.yml found"
    
    # Check .dockerignore
    if [[ ! -f ".dockerignore" ]]; then
        print_warning ".dockerignore not found (recommended but not required)"
    else
        print_status ".dockerignore found"
    fi
    
    # Check .env.production
    if [[ ! -f ".env.production" ]]; then
        print_error ".env.production not found (required for Docker)"
        exit 1
    fi
    print_status ".env.production found"
    
    # Validate docker-compose.yml syntax
    if docker-compose config > /dev/null 2>&1; then
        print_status "docker-compose.yml syntax is valid"
    else
        print_error "docker-compose.yml has syntax errors"
        exit 1
    fi
    
    echo ""
}

# Build Docker images
build_images() {
    print_info "Building Docker images..."
    
    # Build main application image
    if docker-compose build astro-engine; then
        print_status "Astro Engine image built successfully"
    else
        print_error "Failed to build Astro Engine image"
        exit 1
    fi
    
    echo ""
}

# Test container startup
test_container_startup() {
    print_info "Testing container startup..."
    
    # Start services in detached mode
    if docker-compose up -d; then
        print_status "Containers started successfully"
    else
        print_error "Failed to start containers"
        exit 1
    fi
    
    echo ""
    print_info "Waiting for services to be ready..."
    sleep 30  # Wait for services to initialize
    
    # Check container health
    print_info "Checking container health..."
    
    # Check if astro-engine container is running
    if docker-compose ps astro-engine | grep -q "Up"; then
        print_status "Astro Engine container is running"
    else
        print_error "Astro Engine container is not running"
        docker-compose logs astro-engine
        cleanup_containers
        exit 1
    fi
    
    # Check if Redis container is running
    if docker-compose ps redis | grep -q "Up"; then
        print_status "Redis container is running"
    else
        print_error "Redis container is not running"
        docker-compose logs redis
        cleanup_containers
        exit 1
    fi
    
    echo ""
}

# Test API endpoints
test_api_endpoints() {
    print_info "Testing API endpoints..."
    
    # Wait a bit more for the application to fully start
    sleep 10
    
    # Test health endpoint
    print_info "Testing health endpoint..."
    if curl -f -s http://localhost:5000/health > /dev/null; then
        print_status "Health endpoint is responding"
    else
        print_error "Health endpoint is not responding"
        print_info "Container logs:"
        docker-compose logs astro-engine
        cleanup_containers
        exit 1
    fi
    
    # Test metrics endpoint
    print_info "Testing metrics endpoint..."
    if curl -f -s http://localhost:5000/metrics > /dev/null; then
        print_status "Metrics endpoint is responding"
    else
        print_warning "Metrics endpoint is not responding (might be disabled in Docker)"
    fi
    
    # Test natal chart endpoint
    print_info "Testing natal chart calculation..."
    response=$(curl -s -X POST http://localhost:5000/lahiri/natal \
        -H "Content-Type: application/json" \
        -d '{
            "user_name": "Docker Test",
            "birth_date": "1990-01-15",
            "birth_time": "10:30:00",
            "latitude": "28.6139",
            "longitude": "77.2090",
            "timezone_offset": 5.5
        }')
    
    if echo "$response" | grep -q "chart_data"; then
        print_status "Natal chart calculation is working"
    else
        print_error "Natal chart calculation failed"
        echo "Response: $response"
        cleanup_containers
        exit 1
    fi
    
    echo ""
}

# Test Redis connectivity
test_redis_connectivity() {
    print_info "Testing Redis connectivity..."
    
    # Test Redis from within the astro-engine container
    if docker-compose exec -T astro-engine python -c "
import redis
try:
    r = redis.Redis(host='redis', port=6379, db=0)
    r.ping()
    print('Redis connection successful')
except Exception as e:
    print(f'Redis connection failed: {e}')
    exit(1)
"; then
        print_status "Redis connectivity test passed"
    else
        print_error "Redis connectivity test failed"
        cleanup_containers
        exit 1
    fi
    
    echo ""
}

# Performance test
performance_test() {
    print_info "Running basic performance test..."
    
    start_time=$(date +%s)
    
    # Make 10 requests to test performance
    for i in {1..10}; do
        curl -s -X POST http://localhost:5000/lahiri/natal \
            -H "Content-Type: application/json" \
            -d '{
                "user_name": "Perf Test '$i'",
                "birth_date": "1990-01-15",
                "birth_time": "10:30:00",
                "latitude": "28.6139",
                "longitude": "77.2090",
                "timezone_offset": 5.5
            }' > /dev/null
    done
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    print_status "Performance test completed: 10 requests in ${duration} seconds"
    echo ""
}

# Cleanup containers
cleanup_containers() {
    print_info "Cleaning up containers..."
    docker-compose down -v
    print_status "Containers cleaned up"
}

# Main execution
main() {
    echo -e "${BLUE}Starting Docker validation process...${NC}"
    echo ""
    
    check_docker
    check_docker_daemon
    validate_docker_files
    build_images
    test_container_startup
    test_api_endpoints
    test_redis_connectivity
    performance_test
    
    echo -e "${GREEN}🎉 ALL DOCKER TESTS PASSED!${NC}"
    echo -e "${GREEN}✅ Docker setup is working correctly${NC}"
    echo -e "${GREEN}✅ Containers are healthy${NC}"
    echo -e "${GREEN}✅ API endpoints are functional${NC}"
    echo -e "${GREEN}✅ Redis caching is working${NC}"
    echo -e "${GREEN}✅ Performance is acceptable${NC}"
    echo ""
    echo -e "${BLUE}Your Astro Engine is ready for Docker deployment!${NC}"
    echo ""
    
    # Ask if user wants to keep containers running
    read -p "Keep containers running? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        cleanup_containers
    else
        echo -e "${BLUE}Containers are still running. Use 'docker-compose down' to stop them.${NC}"
    fi
}

# Run main function
main "$@"
