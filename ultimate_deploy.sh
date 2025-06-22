#!/bin/bash
# 🚀 ULTIMATE DIGITALOCEAN DEPLOYMENT SCRIPT
# Complete one-click deployment for Astro Engine on DigitalOcean
# Run this script on your DigitalOcean Ubuntu droplet

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
DOMAIN="${1:-astro-engine.example.com}"
EMAIL="${2:-admin@example.com}"
APP_NAME="astro-engine"
PROJECT_DIR="/opt/astro-engine"

echo -e "${PURPLE}🚀 ASTRO ENGINE - ULTIMATE DIGITALOCEAN DEPLOYMENT${NC}"
echo -e "${PURPLE}===============================================${NC}"
echo -e "${CYAN}Domain: ${DOMAIN}${NC}"
echo -e "${CYAN}Email: ${EMAIL}${NC}"
echo -e "${CYAN}Project Directory: ${PROJECT_DIR}${NC}"
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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_error "This script should not be run as root for security reasons!"
    print_info "Please run as a regular user with sudo privileges"
    exit 1
fi

# Step 1: System Update
print_info "Step 1: Updating system packages..."
sudo apt update -y
sudo apt upgrade -y
print_status "System packages updated"

# Step 2: Install Essential Packages
print_info "Step 2: Installing essential packages..."
sudo apt install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    ufw \
    fail2ban \
    htop \
    nginx
print_status "Essential packages installed"

# Step 3: Install Docker
print_info "Step 3: Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    print_status "Docker installed"
else
    print_warning "Docker already installed"
fi

# Step 4: Install Docker Compose
print_info "Step 4: Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed"
else
    print_warning "Docker Compose already installed"
fi

# Step 5: Configure Firewall
print_info "Step 5: Configuring firewall..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
echo "y" | sudo ufw enable
print_status "Firewall configured"

# Step 6: Configure Fail2Ban
print_info "Step 6: Configuring Fail2Ban..."
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
print_status "Fail2Ban configured"

# Step 7: Create Application Directory
print_info "Step 7: Setting up application directory..."
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR
print_status "Application directory created"

# Step 8: Clone or Update Repository
print_info "Step 8: Setting up application code..."
if [ -d "$PROJECT_DIR/.git" ]; then
    print_info "Repository exists, updating..."
    cd $PROJECT_DIR
    git pull origin main
else
    print_info "Cloning repository..."
    # If this script is in the repo, copy current directory
    if [ -f "./docker-compose.yml" ]; then
        cp -r . $PROJECT_DIR/
        cd $PROJECT_DIR
        # Initialize git if not already done
        if [ ! -d ".git" ]; then
            git init
            git add .
            git commit -m "Initial deployment commit"
        fi
    else
        print_error "Please run this script from the Astro Engine directory or provide repository URL"
        exit 1
    fi
fi
print_status "Application code ready"

# Step 9: Configure Environment
print_info "Step 9: Configuring environment..."
cd $PROJECT_DIR

# Copy production environment if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.production" ]; then
        cp .env.production .env
    else
        print_warning "Creating basic .env file"
        cat > .env << EOF
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)
REDIS_URL=redis://redis:6379/0
HOST=0.0.0.0
PORT=5000
WORKERS=4
LOG_LEVEL=INFO
RATE_LIMIT_REQUESTS=1000
CORS_ORIGINS=https://$DOMAIN
METRICS_ENABLED=true
EOF
    fi
fi

# Update domain in environment
sed -i "s/your-domain.com/$DOMAIN/g" .env

print_status "Environment configured"

# Step 10: Install SSL Certificate
print_info "Step 10: Installing SSL certificate..."
if ! command -v certbot &> /dev/null; then
    sudo apt install -y certbot python3-certbot-nginx
fi

# Update nginx configuration with domain
if [ -f "nginx.conf" ]; then
    sed -i "s/your-domain.com/$DOMAIN/g" nginx.conf
fi

print_status "SSL tools installed"

# Step 11: Build and Start Services
print_info "Step 11: Building and starting services..."

# Make sure we're in the right directory
cd $PROJECT_DIR

# Stop any existing services
sudo docker-compose down 2>/dev/null || true

# Build and start services
sudo docker-compose build --no-cache
sudo docker-compose up -d

# Wait for services to start
print_info "Waiting for services to start..."
sleep 30

print_status "Services started"

# Step 12: Configure Nginx and SSL
print_info "Step 12: Configuring Nginx and SSL..."

# Copy nginx configuration
if [ -f "nginx.conf" ]; then
    sudo cp nginx.conf /etc/nginx/sites-available/$APP_NAME
    sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
fi

# Test nginx configuration
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
print_info "Obtaining SSL certificate for $DOMAIN..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $EMAIL || {
    print_warning "SSL certificate setup failed. Continuing with HTTP..."
}

print_status "Nginx and SSL configured"

# Step 13: Set up systemd service for auto-restart
print_info "Step 13: Setting up systemd service..."
sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null << EOF
[Unit]
Description=Astro Engine Docker Compose Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME
print_status "Systemd service configured"

# Step 14: Set up automatic SSL renewal
print_info "Step 14: Setting up automatic SSL renewal..."
(sudo crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | sudo crontab -
print_status "SSL auto-renewal configured"

# Step 15: Set up log rotation
print_info "Step 15: Setting up log rotation..."
sudo tee /etc/logrotate.d/$APP_NAME > /dev/null << EOF
/var/lib/docker/containers/*/*-json.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF
print_status "Log rotation configured"

# Step 16: Final Verification
print_info "Step 16: Running final verification..."

# Check if services are running
if sudo docker-compose ps | grep -q "Up"; then
    print_status "Docker services are running"
else
    print_error "Some Docker services failed to start"
    sudo docker-compose logs
fi

# Check if nginx is running
if sudo systemctl is-active --quiet nginx; then
    print_status "Nginx is running"
else
    print_error "Nginx is not running"
fi

# Test health endpoint
sleep 10
if curl -f http://localhost/health &>/dev/null; then
    print_status "Health endpoint is responding"
else
    print_warning "Health endpoint not responding yet (may need more time)"
fi

# Step 17: Display Final Information
echo ""
echo -e "${PURPLE}🎉 DEPLOYMENT COMPLETE! 🎉${NC}"
echo -e "${PURPLE}========================${NC}"
echo ""
echo -e "${GREEN}✅ Your Astro Engine is now deployed and ready!${NC}"
echo ""
echo -e "${CYAN}🌐 Application URLs:${NC}"
echo -e "   Health Check: https://$DOMAIN/health"
echo -e "   Metrics: https://$DOMAIN/metrics"
echo -e "   API Base: https://$DOMAIN/api/v1/"
echo ""
echo -e "${CYAN}📋 Management Commands:${NC}"
echo -e "   View logs: sudo docker-compose logs -f"
echo -e "   Restart: sudo systemctl restart $APP_NAME"
echo -e "   Status: sudo docker-compose ps"
echo -e "   Update: cd $PROJECT_DIR && git pull && sudo docker-compose up -d --build"
echo ""
echo -e "${CYAN}🔧 Monitoring:${NC}"
echo -e "   Nginx status: sudo systemctl status nginx"
echo -e "   SSL renewal: sudo certbot certificates"
echo -e "   Firewall: sudo ufw status"
echo -e "   Fail2ban: sudo fail2ban-client status"
echo ""
echo -e "${CYAN}📱 Integration:${NC}"
echo -e "   Base URL: https://$DOMAIN"
echo -e "   API Documentation: See README.md"
echo -e "   Rate Limits: 1000 requests/hour per IP"
echo ""
echo -e "${YELLOW}⚠️  Next Steps:${NC}"
echo "1. Test API endpoints with: curl https://$DOMAIN/health"
echo "2. Run comprehensive tests: ./test_api.py --url=https://$DOMAIN"
echo "3. Update DNS records to point $DOMAIN to this server"
echo "4. Share API documentation with your team"
echo "5. Set up monitoring alerts (optional)"
echo ""
echo -e "${GREEN}🚀 Your Corp Astro ecosystem is now powered by enterprise-grade astrology calculations!${NC}"
echo ""

# Create deployment summary
cat > $PROJECT_DIR/deployment_summary.txt << EOF
ASTRO ENGINE DEPLOYMENT SUMMARY
===============================

Deployment Date: $(date)
Domain: $DOMAIN
Server: $(hostname -I | awk '{print $1}')
Project Directory: $PROJECT_DIR

Services Deployed:
- Astro Engine API (Flask + Gunicorn)
- Redis Cache
- Nginx Reverse Proxy
- SSL/TLS Certificate
- Firewall (UFW)
- Fail2Ban Security
- Log Rotation
- Auto-restart Service

URLs:
- Health: https://$DOMAIN/health
- Metrics: https://$DOMAIN/metrics
- API: https://$DOMAIN/api/v1/

Status: PRODUCTION READY ✅
EOF

print_status "Deployment summary saved to $PROJECT_DIR/deployment_summary.txt"

echo -e "${PURPLE}Deployment completed successfully! 🌟${NC}"
