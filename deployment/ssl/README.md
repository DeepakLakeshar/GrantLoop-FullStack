# GrantLoop SSL & Certificate Management

This directory contains the necessary documentation and automation scripts for managing SSL/TLS certificates and rotating critical secrets across the GrantLoop backend infrastructure.

## 🔒 Certificate Lifecycle (Let's Encrypt & Certbot)

### Overview
We utilize **Let's Encrypt** as our Certificate Authority to provision free, automated, and open SSL/TLS certificates. **Certbot** is the client used to fetch and automatically deploy these certificates.

### DNS Requirements & Domain Validation
Before requesting a certificate, ensure that all domain names (e.g., `grantloop.com`, `api.grantloop.com`) resolve strictly to the IP address of your production server via `A` or `CNAME` records. Certbot utilizes the `HTTP-01` challenge, which requires Nginx to answer a specific HTTP payload at `/.well-known/acme-challenge/` over port 80.

### Obtaining & Replacing Certificates
To obtain a new certificate manually for the first time:
```bash
certbot certonly --webroot -w /var/www/certbot -d grantloop.com -d api.grantloop.com
```
If a certificate expires or needs explicit replacement, use the `--force-renewal` flag:
```bash
certbot renew --force-renewal --cert-name grantloop.com
```

### Automatic Renewal
Certificates expire every 90 days. We employ a cron job that executes `certbot-renew.sh` (provided in this directory) daily. It checks certificate expiration and automatically renews any certificate within 30 days of expiration.

### Renewal Verification & Manual Renewal
Verify the renewal dry-run logic at any time without impacting production limits:
```bash
certbot renew --dry-run
```

### Wildcard Certificates
If deploying multi-tenant subdomains (`*.grantloop.com`), the `HTTP-01` challenge is insufficient. You must use the `DNS-01` challenge via a Certbot DNS plugin (e.g., Cloudflare, Route53) to automatically inject TXT records during validation.

### Troubleshooting
- **Challenge Fails**: Ensure Port 80 is open on your firewall and Nginx is not aggressively redirecting `/.well-known/acme-challenge/` to HTTPS before the challenge is validated.
- **Rate Limits**: Let's Encrypt limits failed validations. Use `--dry-run` to test fixes before requesting actual certificates.

---

## 🛡️ TLS Configuration Guidelines

For maximum security and compliance with modern financial data transit requirements, the Nginx SSL configuration must enforce the following boundaries:

- **Supported Protocols**: `TLSv1.2`, `TLSv1.3`
- **Disabled Protocols**: `SSLv3`, `TLSv1`, `TLSv1.1` (Strictly prohibited).
- **Preferred Cipher Suites**: Use forward-secrecy ciphers (e.g., `ECDHE-ECDSA-AES128-GCM-SHA256`, `ECDHE-RSA-AES128-GCM-SHA256`, `ECDHE-ECDSA-AES256-GCM-SHA384`, `ECDHE-RSA-AES256-GCM-SHA384`, `ECDHE-ECDSA-CHACHA20-POLY1305`, `aRSA+CHACHA20`).

---

## 🔄 Secret Rotation Strategy

Critical credentials must be rotated routinely or immediately upon suspected compromise.

1. **SECRET_KEY Rotation**: 
   - Generate a new 50+ character string. 
   - Update `.env`. 
   - Restart the backend. 
   - *Impact*: Active sessions will be invalidated, forcing all users to re-authenticate. Password reset tokens may expire.
2. **Database Password Rotation**: 
   - Update the password inside the PostgreSQL instance (`ALTER USER grantloop WITH PASSWORD 'new';`). 
   - Update `.env` (`DATABASE_URL`). 
   - Restart `backend`, `celery_worker`, and `celery_beat`.
3. **Redis Password Rotation**: 
   - Update `redis.conf` with the new `requirepass`. 
   - Update `.env` (`REDIS_URL` and `CELERY_BROKER_URL`). 
   - Restart all containers.
4. **Stripe & Razorpay Key Rotation**: 
   - Generate a new Secret Key from the provider's dashboard. 
   - Update `.env` (`STRIPE_SECRET_KEY`, `RAZORPAY_KEY_SECRET`). 
   - Gracefully restart the backend workers. Old keys can be rolled back in the dashboard if necessary.
5. **Sentry DSN Rotation**: 
   - Cycle the client key in the Sentry Project Settings. Update `.env`. Restart the backend.

---

## 🆘 Disaster Recovery (SSL & Secrets)

- **Lost Certificate / Compromised Key Recovery**: Immediately revoke the compromised certificate via Certbot (`certbot revoke --cert-path /etc/letsencrypt/live/grantloop.com/cert.pem`). Delete the compromised keys from the server and request a fresh certificate via the standard `HTTP-01` challenge.
- **Revoked Certificates**: If Let's Encrypt revokes your certificate (due to a CA bug or key leak), Nginx will fail to serve trusted HTTPS. Run `certbot renew --force-renewal` immediately.
- **Server Migration**: When migrating to a new physical server, **do not** copy the `/etc/letsencrypt/` directory. Instead, update DNS to point to the new server and run a fresh `certbot certonly` command to generate new cryptographic keys bound to the new host.
- **DNS Migration**: If switching DNS providers, ensure TTLs are lowered to 300s 48 hours prior to migration. Certbot `HTTP-01` validations will fail if DNS propagation has not completed globally.
