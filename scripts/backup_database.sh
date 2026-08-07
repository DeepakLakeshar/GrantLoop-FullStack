#!/bin/bash
# ==============================================================================
# GrantLoop Database Backup Script
# ==============================================================================
# Creates a timestamped, gzipped PostgreSQL dump of the production database.
# Generates a SHA-256 checksum for integrity verification.
# ==============================================================================

set -e

BACKUP_DIR="backups"
LOG_FILE="${BACKUP_DIR}/backup.log"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")
BACKUP_FILE="grantloop_backup_${TIMESTAMP}.sql.gz"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILE}"
CHECKSUM_PATH="${BACKUP_PATH}.sha256"
CONTAINER_NAME="grantloop_prod_postgres"

# Load database credentials if .env exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

DB_USER=${DB_USER:-grantloop}
DB_NAME=${DB_NAME:-grantloop}

mkdir -p "$BACKUP_DIR"

echo "[$(date -u)] Starting database backup to $BACKUP_PATH" | tee -a "$LOG_FILE"

# Execute pg_dump inside the running postgres container and pipe to gzip
if docker exec -t "$CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$DB_NAME" -F p | gzip > "$BACKUP_PATH"; then
    echo "[$(date -u)] Backup compressed successfully." | tee -a "$LOG_FILE"
    
    # Generate SHA-256 Checksum
    cd "$BACKUP_DIR"
    sha256sum "$BACKUP_FILE" > "$(basename "$CHECKSUM_PATH")"
    cd ..
    
    echo "[$(date -u)] SHA-256 checksum generated at $CHECKSUM_PATH" | tee -a "$LOG_FILE"
else
    echo "[$(date -u)] ERROR: Database backup failed!" | tee -a "$LOG_FILE"
    # Cleanup empty or corrupt files on failure
    rm -f "$BACKUP_PATH" "$CHECKSUM_PATH"
    exit 1
fi

echo "[$(date -u)] Backup routine completed successfully." | tee -a "$LOG_FILE"
exit 0
