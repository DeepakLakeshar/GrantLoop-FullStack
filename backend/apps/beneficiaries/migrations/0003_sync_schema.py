"""
0003_sync_schema.py

This migration brings the PHYSICAL database table `campaigns_beneficiary` into
sync with the Django model state.

After 0001_initial (SeparateDatabaseAndState) + 0002_alter…, the Django STATE
already describes the full model.  The DATABASE still has only the original 7
legacy columns:
  id, name, contact_email, contact_phone, verification_status,
  payout_account_reference, campaign_id

Strategy:
  SeparateDatabaseAndState
    state_operations  = []  (state is already correct – nothing to do)
    database_operations = all the ALTERs / ADDs needed to match the model

SQLite compatibility notes:
  - RENAME COLUMN: supported since SQLite 3.25 (2018)
  - DROP COLUMN:   supported since SQLite 3.35 (2021)  – no IF EXISTS clause
  - ADD COLUMN:    always supported
"""
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beneficiaries', '0002_alter_beneficiary_date_of_birth_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # ── State is already correct after 0001 + 0002; nothing to change ──
            state_operations=[],

            # ── Bring the physical table into sync ──────────────────────────
            database_operations=[
                # 1. Rename legacy columns to match current model field names
                migrations.RunSQL(
                    sql="ALTER TABLE campaigns_beneficiary RENAME COLUMN name TO full_name;",
                    reverse_sql="ALTER TABLE campaigns_beneficiary RENAME COLUMN full_name TO name;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE campaigns_beneficiary RENAME COLUMN contact_email TO email;",
                    reverse_sql="ALTER TABLE campaigns_beneficiary RENAME COLUMN email TO contact_email;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE campaigns_beneficiary RENAME COLUMN contact_phone TO phone_number;",
                    reverse_sql="ALTER TABLE campaigns_beneficiary RENAME COLUMN phone_number TO contact_phone;",
                ),

                # 2. Drop the obsolete column (SQLite 3.35+; PostgreSQL always)
                migrations.RunSQL(
                    sql="ALTER TABLE campaigns_beneficiary DROP COLUMN payout_account_reference;",
                    reverse_sql=migrations.RunSQL.noop,
                ),

                # 3. Add address block columns (nullable default so existing rows are safe)
                migrations.RunSQL(
                    sql="ALTER TABLE campaigns_beneficiary ADD COLUMN address TEXT NOT NULL DEFAULT '';",
                    reverse_sql="ALTER TABLE campaigns_beneficiary DROP COLUMN address;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE campaigns_beneficiary ADD COLUMN city VARCHAR(100) NOT NULL DEFAULT '';",
                    reverse_sql="ALTER TABLE campaigns_beneficiary DROP COLUMN city;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE campaigns_beneficiary ADD COLUMN state VARCHAR(100) NOT NULL DEFAULT '';",
                    reverse_sql="ALTER TABLE campaigns_beneficiary DROP COLUMN state;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE campaigns_beneficiary ADD COLUMN country VARCHAR(100) NOT NULL DEFAULT '';",
                    reverse_sql="ALTER TABLE campaigns_beneficiary DROP COLUMN country;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE campaigns_beneficiary ADD COLUMN postal_code VARCHAR(20) NOT NULL DEFAULT '';",
                    reverse_sql="ALTER TABLE campaigns_beneficiary DROP COLUMN postal_code;",
                ),

                # 4. Add identity / biographical columns
                migrations.RunSQL(
                    sql="ALTER TABLE campaigns_beneficiary ADD COLUMN date_of_birth DATE NULL;",
                    reverse_sql="ALTER TABLE campaigns_beneficiary DROP COLUMN date_of_birth;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE campaigns_beneficiary ADD COLUMN government_id VARCHAR(100) NULL;",
                    reverse_sql="ALTER TABLE campaigns_beneficiary DROP COLUMN government_id;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE campaigns_beneficiary ADD COLUMN profile_photo VARCHAR(100) NULL;",
                    reverse_sql="ALTER TABLE campaigns_beneficiary DROP COLUMN profile_photo;",
                ),

                # 5. Verification audit columns
                migrations.RunSQL(
                    sql="ALTER TABLE campaigns_beneficiary ADD COLUMN rejection_reason TEXT NULL;",
                    reverse_sql="ALTER TABLE campaigns_beneficiary DROP COLUMN rejection_reason;",
                ),
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE campaigns_beneficiary "
                        "ADD COLUMN verified_by_id UUID NULL "
                        "REFERENCES accounts_user(id) DEFERRABLE INITIALLY DEFERRED;"
                    ),
                    reverse_sql="ALTER TABLE campaigns_beneficiary DROP COLUMN verified_by_id;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE campaigns_beneficiary ADD COLUMN verified_at TIMESTAMP NULL;",
                    reverse_sql="ALTER TABLE campaigns_beneficiary DROP COLUMN verified_at;",
                ),
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE campaigns_beneficiary "
                        "ADD COLUMN rejected_by_id UUID NULL "
                        "REFERENCES accounts_user(id) DEFERRABLE INITIALLY DEFERRED;"
                    ),
                    reverse_sql="ALTER TABLE campaigns_beneficiary DROP COLUMN rejected_by_id;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE campaigns_beneficiary ADD COLUMN rejected_at TIMESTAMP NULL;",
                    reverse_sql="ALTER TABLE campaigns_beneficiary DROP COLUMN rejected_at;",
                ),

                # 6. Soft-delete flag
                migrations.RunSQL(
                    sql="ALTER TABLE campaigns_beneficiary ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT FALSE;",
                    reverse_sql="ALTER TABLE campaigns_beneficiary DROP COLUMN is_deleted;",
                ),

                # 7. Timestamps  (existing rows receive current timestamp as default)
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE campaigns_beneficiary "
                        "ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;"
                    ),
                    reverse_sql="ALTER TABLE campaigns_beneficiary DROP COLUMN created_at;",
                ),
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE campaigns_beneficiary "
                        "ADD COLUMN updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;"
                    ),
                    reverse_sql="ALTER TABLE campaigns_beneficiary DROP COLUMN updated_at;",
                ),

                # 8. Indexes
                migrations.RunSQL(
                    sql=(
                        "CREATE INDEX IF NOT EXISTS beneficiaries_beneficiary_campaign_idx "
                        "ON campaigns_beneficiary (campaign_id);"
                    ),
                    reverse_sql="DROP INDEX IF EXISTS beneficiaries_beneficiary_campaign_idx;",
                ),
                migrations.RunSQL(
                    sql=(
                        "CREATE INDEX IF NOT EXISTS beneficiaries_beneficiary_verification_status_idx "
                        "ON campaigns_beneficiary (verification_status);"
                    ),
                    reverse_sql="DROP INDEX IF EXISTS beneficiaries_beneficiary_verification_status_idx;",
                ),
                migrations.RunSQL(
                    sql=(
                        "CREATE INDEX IF NOT EXISTS beneficiaries_beneficiary_is_deleted_idx "
                        "ON campaigns_beneficiary (is_deleted);"
                    ),
                    reverse_sql="DROP INDEX IF EXISTS beneficiaries_beneficiary_is_deleted_idx;",
                ),
            ],
        ),
    ]
