#!/bin/bash
# ==============================================================================
# GrantLoop Database Restore Script
# ==============================================================================
# Restores a specified gzipped PostgreSQL dump to the production database.
# Verifies the SHA-256 checksum before attempting restoration.
# ==============================================================================

set -e

if [ -z "$1" ]; then
    echo "Usage: bash scripts/restore_database.sh backups/grantloop_backup_YYYY-MM-DD_HH-MM.sql.gz"
    exit 1
fi

BACKUP_PATH="$1"
CHECKSUM_PATH="${BACKUP_PATH}.sha256"
LOG_FILE="backups/restore.log"
CONTAINER_NAME="grantloop_prod_postgres"

if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

DB_USER=${DB_USER:-grantloop}
DB_NAME=${DB_NAME:-grantloop}

echo "[$(date -u)] Initiating restore procedure for $BACKUP_PATH" | tee -a "$LOG_FILE"

# Validate Backup Exists
if [ ! -f "$BACKUP_PATH" ]; then
    echo "ERROR: Backup file $BACKUP_PATH not found." | tee -a "$LOG_FILE"
    exit 1
fi

# Verify Checksum
if [ ! -f "$CHECKSUM_PATH" ]; then
    echo "WARNING: Checksum file $CHECKSUM_PATH not found. Bypassing checksum validation." | tee -a "$LOG_FILE"
else
    echo "Verifying checksum..."
    BACKUP_DIR=$(dirname "$BACKUP_PATH")
    BACKUP_FILE=$(basename "$BACKUP_PATH")
    if ! (cd "$BACKUP_DIR" && sha256sum -c "$(basename "$CHECKSUM_PATH")"); then
        echo "ERROR: Checksum validation failed! The backup file is corrupt or tampered with." | tee -a "$LOG_FILE"
        exit 1
    fi
    echo "Checksum verified successfully."
fi

# Request confirmation before overwriting production data
read -p "⚠️  WARNING: This will overwrite the current production database '$DB_NAME'. Are you sure? (y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Restore aborted by user." | tee -a "$LOG_FILE"
    exit 0
fi

echo "[$(date -u)] Dropping and recreating database schema..." | tee -a "$LOG_FILE"

# Disconnect active connections, drop and recreate database
docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME';"
docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME;"

echo "[$(date -u)] Restoring data from $BACKUP_PATH..." | tee -a "$LOG_FILE"

# Restore using psql
if gunzip -c "$BACKUP_PATH" | docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME"; then
    echo "[$(date -u)] Database restore completed successfully." | tee -a "$LOG_FILE"
else
    echo "[$(date -u)] ERROR: Database restore failed!" | tee -a "$LOG_FILE"
    exit 1
fi

exit 0
