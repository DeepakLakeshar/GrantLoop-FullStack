#!/bin/bash
# ==============================================================================
# GrantLoop Automated Certificate Renewal Script
# ==============================================================================
# Execution: Recommended to be run daily via cron (e.g., @daily /path/to/certbot-renew.sh)
# Logic: Instructs certbot to renew certificates expiring within 30 days.
# Action: Safely reloads the Nginx container to pick up the new certificate chains.
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status

LOG_FILE="/var/log/certbot-renew.log"

# Log structured output
echo "[$(date -u)] Starting automated Certbot renewal process." >> "$LOG_FILE"

# Execute certbot renewal
if certbot renew --quiet; then
    echo "[$(date -u)] Renewal command executed successfully." >> "$LOG_FILE"
    
    # Reload Nginx configuration cleanly without dropping active connections
    # Assumes Docker Compose is managing the container named 'grantloop_prod_nginx'
    if docker exec grantloop_prod_nginx nginx -s reload; then
        echo "[$(date -u)] Nginx configuration reloaded successfully." >> "$LOG_FILE"
    else
        echo "[$(date -u)] WARNING: Failed to reload Nginx. Manual intervention required." >> "$LOG_FILE"
        exit 1
    fi
else
    echo "[$(date -u)] ERROR: Certbot renewal failed. Check Certbot logs for details." >> "$LOG_FILE"
    exit 1
fi

echo "[$(date -u)] Certificate renewal routine completed." >> "$LOG_FILE"
exit 0
