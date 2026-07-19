from django.db import migrations


def enable_pgcrypto(_apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")


def disable_pgcrypto(_apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute("DROP EXTENSION IF EXISTS pgcrypto")


class Migration(migrations.Migration):
    dependencies = [
        ("disbursements", "0009_initial_sap_posting_pending_only"),
    ]

    operations = [
        migrations.RunPython(enable_pgcrypto, disable_pgcrypto),
    ]
