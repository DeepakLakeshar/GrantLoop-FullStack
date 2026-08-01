from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('campaigns', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Beneficiary',
                    fields=[
                        ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                        ('full_name', models.CharField(max_length=255)),
                        ('email', models.EmailField(db_index=True, max_length=254)),
                        ('phone_number', models.CharField(max_length=30)),
                        ('address', models.TextField()),
                        ('city', models.CharField(max_length=100)),
                        ('state', models.CharField(max_length=100)),
                        ('country', models.CharField(max_length=100)),
                        ('postal_code', models.CharField(max_length=20)),
                        ('date_of_birth', models.DateField(blank=True, null=True)),
                        ('government_id', models.CharField(max_length=100, unique=True)),
                        ('profile_photo', models.FileField(blank=True, null=True, upload_to='beneficiaries/')),
                        ('verification_status', models.CharField(choices=[('pending', 'Pending'), ('verified', 'Verified'), ('rejected', 'Rejected')], default='pending', db_index=True, max_length=20)),
                        ('rejection_reason', models.TextField(blank=True, null=True)),
                        ('verified_at', models.DateTimeField(blank=True, null=True)),
                        ('rejected_at', models.DateTimeField(blank=True, null=True)),
                        ('is_deleted', models.BooleanField(default=False, db_index=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='beneficiary_records', to='campaigns.campaign')),
                        ('rejected_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rejected_beneficiaries', to='accounts.user')),
                        ('verified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='verified_beneficiaries', to='accounts.user')),
                    ],
                    options={
                        'ordering': ['-created_at'],
                        'db_table': 'campaigns_beneficiary',
                        'verbose_name_plural': 'beneficiaries',
                    },
                ),
                migrations.AddIndex(
                    model_name='beneficiary',
                    index=models.Index(fields=['campaign'], name='campaigns_b_campaig_a908c7_idx'),
                ),
            ],
            database_operations=[],
        )
    ]
