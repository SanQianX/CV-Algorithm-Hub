#!/bin/bash
# ============================================
# CV Algorithm Hub - Blue-Green Status Script
# Shows current deployment status
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

source .env 2>/dev/null || true

CURRENT_COLOR=${CVHUB_DEPLOYMENT_COLOR:-blue}

echo "================================"
echo "  Blue-Green Deployment Status"
echo "================================"
echo ""
echo "Current Color: $CURRENT_COLOR"
echo "Inactive Color: $([ "$CURRENT_COLOR" = "blue" ] && echo "green" || echo "blue")"
echo ""

echo "Service Status:"
docker-compose --profile ps --services --filter "status=running" 2>/dev/null || echo "No services running"
echo ""

echo "Recent Health Checks:"
curl -s http://localhost:8080/health 2>/dev/null | head -c 200 || echo "No health data"
echo ""
