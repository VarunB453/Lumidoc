#!/bin/bash
# seed_db.sh - Seed the database with initial/test data
set -e

echo "🌱 Seeding database..."

cd apps/server

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run database migrations
python -m alembic upgrade head

# Run seed script
python -c "
from app.db.seed import seed_database
import asyncio
asyncio.run(seed_database())
print('✅ Database seeded successfully')
"

echo "✅ Database seeding complete"
