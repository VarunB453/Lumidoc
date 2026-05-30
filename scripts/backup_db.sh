#!/bin/bash
# backup_db.sh - Backup the PostgreSQL database
set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups"
BACKUP_FILE="${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql.gz"

# Load environment variables
if [ -f "apps/server/.env" ]; then
    export $(grep -v '^#' apps/server/.env | xargs)
fi

DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-lumidoc_db}
DB_USER=${DB_USER:-lumidoc}

echo "💾 Backing up database: ${DB_NAME}..."

mkdir -p "$BACKUP_DIR"

pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"

echo "✅ Backup saved to: $BACKUP_FILE"
echo "   Size: $(du -h "$BACKUP_FILE" | cut -f1)"
