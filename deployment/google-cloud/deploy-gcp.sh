#!/bin/bash
# 🚀 GOOGLE CLOUD DEPLOYMENT SCRIPT FOR ASTRO ENGINE
# Complete deployment to Google Cloud Platform using Cloud Run + Cloud SQL + Memorystore

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Load configuration
source ./gcp-config.env

echo -e "${PURPLE}🚀 ASTRO ENGINE - GOOGLE CLOUD DEPLOYMENT${NC}"
echo -e "${PURPLE}===========================================${NC}"
echo -e "${CYAN}Project: ${GOOGLE_CLOUD_PROJECT}${NC}"
echo -e "${CYAN}Region: ${GOOGLE_CLOUD_REGION}${NC}"
echo -e "${CYAN}Service: ${CLOUD_RUN_SERVICE_NAME}${NC}"
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

# Check if gcloud is installed
check_gcloud() {
    print_info "Checking Google Cloud SDK..."
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud SDK not found. Please install it first:"
        echo "https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    print_status "Google Cloud SDK found"
}

# Set up Google Cloud project
setup_project() {
    print_info "Setting up Google Cloud project..."
    
    # Set project
    gcloud config set project ${GOOGLE_CLOUD_PROJECT}
    
    # Enable required APIs
    print_info "Enabling required APIs..."
    gcloud services enable run.googleapis.com
    gcloud services enable sqladmin.googleapis.com
    gcloud services enable redis.googleapis.com
    gcloud services enable containerregistry.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable monitoring.googleapis.com
    gcloud services enable logging.googleapis.com
    
    print_status "Project setup complete"
}

# Build and push container image
build_and_push() {
    print_info "Building and pushing container image..."
    
    # Build image using Cloud Build
    gcloud builds submit --tag ${CONTAINER_REGISTRY}/${GOOGLE_CLOUD_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG} .
    
    print_status "Container image built and pushed"
}

# Deploy Redis (Cloud Memorystore)
deploy_redis() {
    print_info "Setting up Cloud Memorystore (Redis)..."
    
    # Check if Redis instance exists
    if ! gcloud redis instances describe ${REDIS_INSTANCE_NAME} --region=${GOOGLE_CLOUD_REGION} &> /dev/null; then
        print_info "Creating Redis instance..."
        gcloud redis instances create ${REDIS_INSTANCE_NAME} \
            --size=${REDIS_MEMORY_SIZE_GB} \
            --region=${GOOGLE_CLOUD_REGION} \
            --redis-version=redis_6_x \
            --tier=${REDIS_TIER}
        print_status "Redis instance created"
    else
        print_status "Redis instance already exists"
    fi
}

# Deploy Cloud SQL (Optional - for user management)
deploy_database() {
    print_info "Setting up Cloud SQL (PostgreSQL)..."
    
    # Check if SQL instance exists
    if ! gcloud sql instances describe ${CLOUD_SQL_INSTANCE} &> /dev/null; then
        print_info "Creating Cloud SQL instance..."
        gcloud sql instances create ${CLOUD_SQL_INSTANCE} \
            --database-version=POSTGRES_14 \
            --tier=db-f1-micro \
            --region=${GOOGLE_CLOUD_REGION} \
            --storage-auto-increase \
            --backup-start-time=02:00
        
        # Create database
        gcloud sql databases create ${CLOUD_SQL_DATABASE} --instance=${CLOUD_SQL_INSTANCE}
        
        # Create user
        gcloud sql users create ${CLOUD_SQL_USER} --instance=${CLOUD_SQL_INSTANCE} --password=changeme123!
        
        print_status "Cloud SQL instance created"
    else
        print_status "Cloud SQL instance already exists"
    fi
}

# Create Cloud Storage bucket for ephemeris data
create_storage() {
    print_info "Setting up Cloud Storage..."
    
    # Check if bucket exists
    if ! gsutil ls gs://${STORAGE_BUCKET} &> /dev/null; then
        print_info "Creating storage bucket..."
        gsutil mb -c ${STORAGE_CLASS} -l ${GOOGLE_CLOUD_REGION} gs://${STORAGE_BUCKET}
        
        # Upload ephemeris data
        gsutil -m cp -r astro_engine/ephe/* gs://${STORAGE_BUCKET}/ephe/
        
        print_status "Storage bucket created and ephemeris data uploaded"
    else
        print_status "Storage bucket already exists"
    fi
}

# Deploy to Cloud Run
deploy_cloud_run() {
    print_info "Deploying to Cloud Run..."
    
    # Get Redis IP
    REDIS_IP=$(gcloud redis instances describe ${REDIS_INSTANCE_NAME} --region=${GOOGLE_CLOUD_REGION} --format="value(host)")
    
    # Deploy service
    gcloud run deploy ${CLOUD_RUN_SERVICE_NAME} \
        --image ${CONTAINER_REGISTRY}/${GOOGLE_CLOUD_PROJECT}/${IMAGE_NAME}:${IMAGE_TAG} \
        --region ${CLOUD_RUN_REGION} \
        --platform ${CLOUD_RUN_PLATFORM} \
        --memory ${CLOUD_RUN_MEMORY} \
        --cpu ${CLOUD_RUN_CPU} \
        --concurrency ${CLOUD_RUN_CONCURRENCY} \
        --max-instances ${CLOUD_RUN_MAX_INSTANCES} \
        --min-instances ${CLOUD_RUN_MIN_INSTANCES} \
        --set-env-vars "REDIS_URL=redis://${REDIS_IP}:6379/0" \
        --set-env-vars "FLASK_ENV=production" \
        --set-env-vars "GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}" \
        --allow-unauthenticated \
        --port 5000
    
    print_status "Cloud Run deployment complete"
}

# Set up monitoring and logging
setup_monitoring() {
    print_info "Setting up monitoring and logging..."
    
    if [[ "$ENABLE_CLOUD_MONITORING" == "true" ]]; then
        print_info "Cloud Monitoring will be automatically enabled"
    fi
    
    if [[ "$ENABLE_CLOUD_LOGGING" == "true" ]]; then
        print_info "Cloud Logging will be automatically enabled"
    fi
    
    print_status "Monitoring and logging configured"
}

# Display deployment information
show_deployment_info() {
    echo ""
    echo -e "${PURPLE}🎉 DEPLOYMENT COMPLETE!${NC}"
    echo -e "${PURPLE}======================${NC}"
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe ${CLOUD_RUN_SERVICE_NAME} --region=${CLOUD_RUN_REGION} --format="value(status.url)")
    
    echo -e "${GREEN}✅ Service URL: ${SERVICE_URL}${NC}"
    echo -e "${GREEN}✅ Health Check: ${SERVICE_URL}/health${NC}"
    echo -e "${GREEN}✅ Metrics: ${SERVICE_URL}/metrics${NC}"
    echo -e "${GREEN}✅ Cache Stats: ${SERVICE_URL}/cache/stats${NC}"
    
    echo ""
    echo -e "${CYAN}📊 Resource Information:${NC}"
    echo -e "${CYAN}• Cloud Run Service: ${CLOUD_RUN_SERVICE_NAME}${NC}"
    echo -e "${CYAN}• Redis Instance: ${REDIS_INSTANCE_NAME}${NC}"
    echo -e "${CYAN}• SQL Instance: ${CLOUD_SQL_INSTANCE}${NC}"
    echo -e "${CYAN}• Storage Bucket: gs://${STORAGE_BUCKET}${NC}"
    
    echo ""
    echo -e "${YELLOW}🔧 Next Steps:${NC}"
    echo -e "${YELLOW}• Update DNS to point to: ${SERVICE_URL}${NC}"
    echo -e "${YELLOW}• Configure custom domain if needed${NC}"
    echo -e "${YELLOW}• Set up SSL certificate${NC}"
    echo -e "${YELLOW}• Configure monitoring alerts${NC}"
}

# Main deployment function
main() {
    print_info "Starting Google Cloud deployment..."
    
    check_gcloud
    setup_project
    
    # Create infrastructure
    deploy_redis
    deploy_database
    create_storage
    
    # Build and deploy application
    build_and_push
    deploy_cloud_run
    
    # Setup monitoring
    setup_monitoring
    
    # Show results
    show_deployment_info
    
    print_status "Google Cloud deployment completed successfully!"
}

# Check for help flag
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Deploy Astro Engine to Google Cloud Platform"
    echo ""
    echo "Before running this script:"
    echo "1. Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    echo "2. Run: gcloud auth login"
    echo "3. Run: gcloud auth configure-docker"
    echo "4. Update gcp-config.env with your project settings"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    exit 0
fi

# Run main deployment
main "$@"
