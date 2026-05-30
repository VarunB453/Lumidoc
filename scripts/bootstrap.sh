#!/bin/bash
# bootstrap.sh - First-time project setup script
set -e

echo "🚀 Bootstrapping Lumidoc..."

# Check prerequisites
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed."; exit 1; }

echo "✅ Prerequisites check passed"

# Setup client
echo "📦 Setting up client..."
cd apps/client
cp .env.example .env.development
npm install
cd ../..

# Setup server
echo "🐍 Setting up server..."
cd apps/server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
cp .env.example .env
cd ../..

# Generate keys
echo "🔑 Generating keys..."
bash scripts/generate_keys.sh

# Setup pre-commit hooks
if command -v pre-commit >/dev/null 2>&1; then
    echo "🪝 Setting up pre-commit hooks..."
    pre-commit install
fi

echo ""
echo "✅ Bootstrap complete!"
echo ""
echo "To start development:"
echo "  Client: cd apps/client && npm run dev"
echo "  Server: cd apps/server && uvicorn app.main:app --reload"
echo "  Docker: docker compose -f infrastructure/docker/compose/docker-compose.dev.yml up"
