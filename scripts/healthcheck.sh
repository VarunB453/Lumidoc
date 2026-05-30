#!/bin/bash
# healthcheck.sh - Check health of all services
set -e

echo "🏥 Running health checks..."
echo ""

ERRORS=0

# Check API server
echo -n "  API Server (http://localhost:8000/health): "
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    ERRORS=$((ERRORS + 1))
fi

# Check client
echo -n "  Client (http://localhost:5173): "
if curl -sf http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    ERRORS=$((ERRORS + 1))
fi

# Check PostgreSQL
echo -n "  PostgreSQL (localhost:5432): "
if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    ERRORS=$((ERRORS + 1))
fi

# Check Redis
echo -n "  Redis (localhost:6379): "
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAILED"
    ERRORS=$((ERRORS + 1))
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✅ All services healthy"
else
    echo "❌ $ERRORS service(s) unhealthy"
    exit 1
fi
