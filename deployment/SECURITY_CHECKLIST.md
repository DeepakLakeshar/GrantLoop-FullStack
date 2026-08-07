# GrantLoop Production Security Checklist

Ensure every item on this checklist is verified before executing a production deployment.

- [ ] **HTTPS Enabled**: All traffic is encrypted in transit using Let's Encrypt certificates.
- [ ] **HSTS (Strict-Transport-Security)**: Enforced via Nginx headers (`max-age=31536000; includeSubDomains; preload`) to prevent downgrade attacks.
- [ ] **CSP (Content-Security-Policy)**: Validated to ensure safe resource loading without breaking Swagger UI.
- [ ] **X-Frame-Options**: Set to `DENY` to prevent clickjacking.
- [ ] **Referrer-Policy**: Set to `strict-origin-when-cross-origin` to prevent data leakage in URL parameters.
- [ ] **Permissions-Policy**: Camera, microphone, and geolocation strictly disabled.
- [ ] **Secure Cookies**: `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` strictly set to `True` in production Django settings.
- [ ] **CSRF Protection**: Enabled and enforced; `CSRF_TRUSTED_ORIGINS` strictly limited to exact frontend domains.
- [ ] **CORS (Cross-Origin Resource Sharing)**: `CORS_ALLOWED_ORIGINS` contains only authorized domains. Broad wildcards (`*`) are prohibited.
- [ ] **Host Validation**: `ALLOWED_HOSTS` configured strictly to valid production domains (e.g., `grantloop.com`).
- [ ] **Secret Management**: Passwords and API keys injected strictly via `.env` file; no hardcoded credentials inside the codebase.
- [ ] **Database Security**: PostgreSQL exposed exclusively to the internal Docker network; no port forwarding to the host machine.
- [ ] **Redis Security**: Redis broker exposed exclusively to the internal Docker network; persistence enabled safely.
- [ ] **Docker Security**: Containers run as non-root users where possible; volumes isolated from host execution.
- [ ] **Backup Encryption**: Database backup cron jobs pipe outputs through AES-256 or GPG encryption before uploading to cold storage.
- [ ] **Log Retention**: Log files rotate safely, scrubbing PII (Personally Identifiable Information) before indexing.
