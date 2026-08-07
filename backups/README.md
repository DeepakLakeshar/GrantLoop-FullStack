# GrantLoop Database Backups

This directory acts as the local staging area for automated PostgreSQL database dumps and their associated cryptographic checksums.

## 🗄️ Storage Structure
- **Archives**: Backups are generated as compressed SQL plain-text dumps (`grantloop_backup_YYYY-MM-DD_HH-MM.sql.gz`).
- **Checksums**: Each archive is paired with a SHA-256 hash file (`.sha256`) to ensure file integrity and prevent silently restoring a corrupted archive.
- **Logs**: Backup and cleanup execution logs are stored locally (`backup.log`, `cleanup.log`, `restore.log`).

## ⏳ Retention Policy
The automated `scripts/cleanup_backups.sh` script enforces the following retention lifecycle to balance recoverability with disk space:
- **Daily Retention**: Retains the last 30 daily snapshots.
- **Monthly Retention**: Retains the last 12 snapshots taken on the 1st day of the month.
- Older backups are automatically purged.

## 🔐 Encryption Recommendations
By default, these backups are compressed but **not encrypted** at rest. Before transmitting these files off-site, it is highly recommended to pipe the `pg_dump` output through GPG or OpenSSL AES-256 encryption.

## 🌍 Off-Site Backup Strategy
Local backups are insufficient for Disaster Recovery if the host server is destroyed. Ensure a cron job automatically syncs this `backups/` directory to an immutable, off-site S3 bucket (e.g., AWS S3 with Object Lock, DigitalOcean Spaces) immediately after `backup_database.sh` completes.
