# Release Summary

**Version**: `vX.Y.Z`
**Release Date**: `YYYY-MM-DD`

*Brief summary of the primary goals and achievements of this release.*

## 🚀 Major Features & Enhancements
- [Feature 1 description]
- [Feature 2 description]

## 🛠️ Bug Fixes
- [Bug fix 1 description]
- [Bug fix 2 description]

## ⚠️ Breaking Changes
- [Breaking change 1 description and migration path]
- [Breaking change 2 description and migration path]

## 🚢 Deployment Notes
- Any required environment variables added or removed?
- Does this release require heavy database migrations? (Expected downtime: X minutes)
- Any manual script executions required post-deployment?

## ✅ Verification Checklist
Before approving this release for production cutover, confirm the following:
- [ ] All automated tests pass in CI/CD pipeline.
- [ ] Staging deployment completed without errors.
- [ ] No performance regression detected on staging load tests.
- [ ] Security scans (Snyk/Bandit) report 0 critical vulnerabilities.
- [ ] Backward compatibility with current frontend is verified.

## ⏪ Rollback Instructions
If a catastrophic failure occurs post-deployment:
1. Revert the repository to the previous stable tag (`vX.Y.Z-1`).
2. Run `docker compose -f docker-compose.prod.yml up -d --build`.
3. Monitor logs for recovery via `docker compose logs -f backend`.
4. If schema was broken, execute `bash scripts/restore_database.sh` using the latest verified snapshot prior to this release.
