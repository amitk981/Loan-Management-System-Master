from django.db import migrations


def enable_pgcrypto(_apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(
            """
            DO $migration$
            DECLARE
                extension_preexisting boolean;
            BEGIN
                SELECT EXISTS (
                    SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto'
                ) INTO extension_preexisting;
                CREATE EXTENSION IF NOT EXISTS pgcrypto;
                CREATE TABLE IF NOT EXISTS
                    sfpcl_disbursements_pgcrypto_ownership (
                        singleton smallint PRIMARY KEY CHECK (singleton = 1),
                        app_created boolean NOT NULL
                    );
                INSERT INTO sfpcl_disbursements_pgcrypto_ownership
                    (singleton, app_created)
                SELECT 1, NOT extension_preexisting
                ON CONFLICT (singleton) DO NOTHING;
            END
            $migration$;
            """
        )


def disable_pgcrypto(_apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(
            """
            DO $migration$
            DECLARE
                app_created boolean := false;
            BEGIN
                IF TO_REGCLASS(
                    'sfpcl_disbursements_pgcrypto_ownership'
                ) IS NOT NULL THEN
                    SELECT ownership.app_created
                    INTO app_created
                    FROM sfpcl_disbursements_pgcrypto_ownership AS ownership
                    WHERE ownership.singleton = 1;
                    IF app_created THEN
                        DROP EXTENSION IF EXISTS pgcrypto;
                    END IF;
                    DROP TABLE sfpcl_disbursements_pgcrypto_ownership;
                END IF;
            END
            $migration$;
            """
        )


class Migration(migrations.Migration):
    dependencies = [
        ("disbursements", "0009_initial_sap_posting_pending_only"),
    ]

    operations = [
        migrations.RunPython(enable_pgcrypto, disable_pgcrypto),
    ]
