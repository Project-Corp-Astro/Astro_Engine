#!/bin/bash

# DigitalOcean Deployment Script for Astro Engine
# This script sets up the production environment on a DigitalOcean droplet

set -euo pipefail

# Configuration
DOMAIN="${DOMAIN:-your-domain.com}"
EMAIL="${EMAIL:-admin@your-domain.com}"
APP_DIR="/opt/astro_engine"
USER="astro"

echo "🚀 Starting Astro Engine deployment on DigitalOcean..."

# Update system
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# Install required packages
echo "🔧 Installing system dependencies..."
apt-get install -y \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx \
    ufw \
    fail2ban \
    htop \
    curl \
    git

# Create application user
echo "👤 Creating application user..."
if ! id "$USER" &>/dev/null; then
    useradd -m -s /bin/bash "$USER"
    usermod -aG docker "$USER"
fi

# Create application directory
echo "📁 Setting up application directory..."
mkdir -p "$APP_DIR"
chown "$USER:$USER" "$APP_DIR"

# Clone or copy application files
echo "📥 Setting up application files..."
if [ -d ".git" ]; then
    # If running from git repository
    cp -r . "$APP_DIR/"
else
    echo "Please copy your Astro Engine files to $APP_DIR"
    exit 1
fi

chown -R "$USER:$USER" "$APP_DIR"

# Set up environment file
echo "⚙️ Configuring environment..."
cd "$APP_DIR"
cp .env.production .env

# Generate secret key
SECRET_KEY=$(openssl rand -hex 32)
sed -i "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env

# Update domain in environment
sed -i "s/yourdomain.com/$DOMAIN/g" .env

# Set up firewall
echo "🔒 Configuring firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp

# Configure fail2ban
echo "🛡️ Setting up fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban

# Start Docker services
echo "🐳 Starting Docker services..."
cd "$APP_DIR"
sudo -u "$USER" docker-compose up -d --build

# Set up SSL certificate
echo "🔐 Setting up SSL certificate..."
if [ "$DOMAIN" != "your-domain.com" ]; then
    certbot --nginx -d "$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive
    
    # Update nginx configuration for SSL
    systemctl reload nginx
fi

# Set up log rotation
echo "📝 Setting up log rotation..."
cat > /etc/logrotate.d/astro_engine << EOF
/var/log/astro_engine.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 astro astro
    postrotate
        docker-compose -f $APP_DIR/docker-compose.yml restart astro-engine
    endscript
}
EOF

# Set up monitoring script
echo "📊 Setting up monitoring..."
cat > /usr/local/bin/astro_health_check.sh << 'EOF'
#!/bin/bash
HEALTH_URL="http://localhost:5000/health"
WEBHOOK_URL="${WEBHOOK_URL:-}"

check_health() {
    if curl -sf "$HEALTH_URL" > /dev/null; then
        echo "$(date): Astro Engine is healthy"
        return 0
    else
        echo "$(date): Astro Engine is unhealthy"
        return 1
    fi
}

send_alert() {
    if [ -n "$WEBHOOK_URL" ]; then
        curl -X POST "$WEBHOOK_URL" -H "Content-Type: application/json" \
             -d "{\"text\":\"🚨 Astro Engine health check failed on $(hostname)\"}"
    fi
}

if ! check_health; then
    send_alert
    # Restart the service
    cd /opt/astro_engine
    docker-compose restart astro-engine
fi
EOF

chmod +x /usr/local/bin/astro_health_check.sh

# Set up cron job for health checks
echo "⏰ Setting up health check cron job..."
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/astro_health_check.sh >> /var/log/astro_health.log 2>&1") | crontab -

# Set up auto-updates
echo "🔄 Setting up auto-updates..."
cat > /etc/cron.daily/astro_update << 'EOF'
#!/bin/bash
cd /opt/astro_engine
git pull origin main
docker-compose build --no-cache
docker-compose up -d
EOF

chmod +x /etc/cron.daily/astro_update

# Final security hardening
echo "🔒 Final security hardening..."
# Disable root SSH login
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# Restart SSH
systemctl restart ssh

# Print status
echo "✅ Deployment complete!"
echo ""
echo "📋 Summary:"
echo "- Application URL: https://$DOMAIN"
echo "- Health check: https://$DOMAIN/health"
echo "- Application directory: $APP_DIR"
echo "- User: $USER"
echo ""
echo "🔧 Post-deployment checklist:"
echo "1. Update DNS records to point to this server"
echo "2. Test all API endpoints"
echo "3. Configure monitoring alerts"
echo "4. Set up backup strategy"
echo "5. Update team with new API endpoints"
echo ""
echo "📊 Useful commands:"
echo "- Check status: cd $APP_DIR && docker-compose ps"
echo "- View logs: cd $APP_DIR && docker-compose logs -f"
echo "- Restart: cd $APP_DIR && docker-compose restart"
echo "- Update: cd $APP_DIR && git pull && docker-compose up -d --build"
