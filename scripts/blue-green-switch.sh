#!/bin/bash
# ============================================
# CV Algorithm Hub - Blue-Green Switch Script
# Switches traffic to the newly deployed version
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Load configuration
source .env 2>/dev/null || true

CURRENT_COLOR=${CVHUB_DEPLOYMENT_COLOR:-blue}
log_info "Current color: $CURRENT_COLOR"

# Reload nginx to switch traffic
log_info "Reloading nginx to switch traffic to $CURRENT_COLOR..."
docker exec cvhub-nginx nginx -s reload

# Wait for nginx to reload
sleep 5

# Verify traffic switch
HEALTH_CHECK_URL=${HEALTH_CHECK_URL:-http://localhost/health}
log_info "Verifying traffic switch..."
if curl -f "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
    log_info "Traffic switch successful!"
    log_info "Blue-green deployment completed!"
else
    log_warn "Health check failed after switch, rolling back..."
    ./blue-green-rollback.sh
fi
