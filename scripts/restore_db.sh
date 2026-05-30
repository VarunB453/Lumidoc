#!/bin/bash
# restore_db.sh - Restore the PostgreSQL database from a backup
set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    echo ""
    echo "Available backups:"
    ls -la backups/*.sql.gz 2>/dev/null || echo "  No backups found"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Load environment variables
if [ -f "apps/server/.env" ]; then
    export $(grep -v '^#' apps/server/.env | xargs)
fi

DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-lumidoc_db}
DB_USER=${DB_USER:-lumidoc}

echo "⚠️  WARNING: This will overwrite the current database: ${DB_NAME}"
read -p "Are you sure? (y/N): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Cancelled."
    exit 0
fi

echo "🔄 Restoring database from: $BACKUP_FILE..."

gunzip -c "$BACKUP_FILE" | psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME"

echo "✅ Database restored successfully"
