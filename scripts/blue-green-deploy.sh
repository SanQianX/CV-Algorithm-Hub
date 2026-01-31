#!/bin/bash
# ============================================
# CV Algorithm Hub - Blue-Green Deployment Script
# Deploys to the inactive color (blue or green)
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Load configuration
source .env 2>/dev/null || true

CURRENT_COLOR=${CVHUB_DEPLOYMENT_COLOR:-blue}
NEW_COLOR=$([ "$CURRENT_COLOR" = "blue" ] && echo "green" || echo "blue")

log_info "Current deployment color: $CURRENT_COLOR"
log_info "Deploying to: $NEW_COLOR"

# Create deployment directory for new color
DEPLOY_DIR="./deployments/$NEW_COLOR"
mkdir -p "$DEPLOY_DIR"

# Pull latest images
log_info "Pulling latest images..."
docker-compose --profile prod pull

# Build new images with new color tag
log_info "Building images for $NEW_COLOR..."
docker-compose --profile prod build --build-arg DEPLOYMENT_COLOR=$NEW_COLOR

# Start services with new color (without nginx)
log_info "Starting $NEW_COLOR services..."
docker-compose --profile prod up -d --no-color

# Wait for services to be healthy
log_info "Waiting for services to be healthy..."
sleep 30

# Health check
log_info "Performing health check..."
HEALTH_CHECK_URL=${HEALTH_CHECK_URL:-http://localhost:8080/health}
if curl -f "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
    log_info "Health check passed!"
else
    log_warn "Health check failed, checking logs..."
    docker-compose --profile prod logs --tail=50
    log_error "Health check failed! Rolling back..."
    docker-compose --profile prod down
    exit 1
fi

# Update deployment color
log_info "Updating deployment color to $NEW_COLOR..."
sed -i "s/CVHUB_DEPLOYMENT_COLOR=$CURRENT_COLOR/CVHUB_DEPLOYMENT_COLOR=$NEW_COLOR/" .env

log_info "Blue-green deployment to $NEW_COLOR completed!"
log_info "Run 'make bg-switch' to switch traffic to the new version"
