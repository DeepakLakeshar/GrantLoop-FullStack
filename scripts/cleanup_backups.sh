#!/bin/bash
# ==============================================================================
# GrantLoop Backup Retention & Cleanup Script
# ==============================================================================
# Retention Policy:
# - Keeps the last 30 daily backups
# - Keeps the last 12 monthly backups (1st of the month)
# - Safely deletes older backups to conserve disk space.
# ==============================================================================

set -e

BACKUP_DIR="backups"
LOG_FILE="${BACKUP_DIR}/cleanup.log"

echo "[$(date -u)] Initiating backup retention cleanup..." | tee -a "$LOG_FILE"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "ERROR: Backup directory $BACKUP_DIR not found."
    exit 1
fi

# Keep the last 30 daily backups
echo "Enforcing 30-day daily retention policy..." | tee -a "$LOG_FILE"
ls -tp "$BACKUP_DIR"/grantloop_backup_*.sql.gz 2>/dev/null | grep -v '/$' | tail -n +31 | while read -r FILE; do
    # Do not delete if it's the 1st of the month (save for monthly retention)
    if [[ "$FILE" != *"_01_"* ]]; then
        echo "Deleting old daily backup: $FILE" | tee -a "$LOG_FILE"
        rm -f "$FILE"
        rm -f "${FILE}.sha256"
    fi
done

# Keep the last 12 monthly backups (files containing _01_ indicating the 1st of the month)
echo "Enforcing 12-month monthly retention policy..." | tee -a "$LOG_FILE"
ls -tp "$BACKUP_DIR"/grantloop_backup_*_01_*.sql.gz 2>/dev/null | grep -v '/$' | tail -n +13 | while read -r FILE; do
    echo "Deleting old monthly backup: $FILE" | tee -a "$LOG_FILE"
    rm -f "$FILE"
    rm -f "${FILE}.sha256"
done

echo "[$(date -u)] Backup retention cleanup completed successfully." | tee -a "$LOG_FILE"
exit 0
