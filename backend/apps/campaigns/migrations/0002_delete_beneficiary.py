from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('campaigns', '0001_initial'),
        ('documents', '0003_alter_document_beneficiary'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name='Beneficiary',
                ),
            ],
            database_operations=[],
        )
    ]
