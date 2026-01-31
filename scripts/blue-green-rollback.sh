#!/bin/bash
# ============================================
# CV Algorithm Hub - Blue-Green Rollback Script
# Rolls back to the previous color
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

# Load configuration
source .env 2>/dev/null || true

CURRENT_COLOR=${CVHUB_DEPLOYMENT_COLOR:-blue}
PREV_COLOR=$([ "$CURRENT_COLOR" = "blue" ] && echo "green" || echo "blue")

log_warn "Rolling back from $CURRENT_COLOR to $PREV_COLOR..."

# Reload nginx to switch back
docker exec cvhub-nginx nginx -s reload

# Update configuration
sed -i "s/CVHUB_DEPLOYMENT_COLOR=$CURRENT_COLOR/CVHUB_DEPLOYMENT_COLOR=$PREV_COLOR/" .env

log_info "Rollback to $PREV_COLOR completed!"
