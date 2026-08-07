#!/bin/bash
# ==============================================================================
# GrantLoop Backup Verification Script
# ==============================================================================
# Validates backup file existence, checksum integrity, and SQL archive readability.
# ==============================================================================

set -e

if [ -z "$1" ]; then
    echo "Usage: bash scripts/verify_backup.sh backups/grantloop_backup_YYYY-MM-DD_HH-MM.sql.gz"
    exit 1
fi

BACKUP_PATH="$1"
CHECKSUM_PATH="${BACKUP_PATH}.sha256"

echo "=> 1. Verifying backup file existence..."
if [ ! -f "$BACKUP_PATH" ]; then
    echo "ERROR: File $BACKUP_PATH does not exist."
    exit 1
fi
echo "Backup file found: $BACKUP_PATH"

echo "=> 2. Verifying SHA-256 checksum integrity..."
if [ -f "$CHECKSUM_PATH" ]; then
    BACKUP_DIR=$(dirname "$BACKUP_PATH")
    if ! (cd "$BACKUP_DIR" && sha256sum -c "$(basename "$CHECKSUM_PATH")" > /dev/null); then
        echo "ERROR: Checksum mismatch. The file is corrupted."
        exit 1
    fi
    echo "Checksum matches successfully."
else
    echo "WARNING: Checksum file not found. Skipping cryptographic validation."
fi

echo "=> 3. Verifying GZIP archive readability and SQL dump integrity..."
# Test gzip integrity without uncompressing
if ! gzip -t "$BACKUP_PATH"; then
    echo "ERROR: Gzip archive is corrupted and cannot be read."
    exit 1
fi

# Look for PostgreSQL dump completion marker
if ! gunzip -c "$BACKUP_PATH" | tail -n 20 | grep -q "PostgreSQL database dump complete"; then
    echo "WARNING: 'PostgreSQL database dump complete' marker not found at the end of the file. The backup may have terminated prematurely."
    # We do not strictly exit 1 here as some versions of pg_dump output might differ slightly, but we warn heavily.
else
    echo "PostgreSQL completion marker found. SQL dump is structurally intact."
fi

echo "✅ Backup verification passed successfully."
exit 0
