from django.db import migrations


def create_owner_guards(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor == "postgresql":
        schema_editor.execute(
            """
            CREATE FUNCTION enforce_current_dpd_snapshot_owner()
            RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'DPD snapshots cannot be reparented'
                    USING ERRCODE = '23503';
            END;
            $$ LANGUAGE plpgsql;
            """
        )
        schema_editor.execute(
            """
            CREATE TRIGGER current_dpd_snapshot_owner_guard
            BEFORE UPDATE OF loan_account_id OR DELETE ON dpd_statuses
            FOR EACH ROW EXECUTE FUNCTION enforce_current_dpd_snapshot_owner();
            """
        )
        schema_editor.execute(
            """
            CREATE FUNCTION retain_approved_dpd_policy_version()
            RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'approved DPD policy versions are immutable'
                    USING ERRCODE = '23514';
            END;
            $$ LANGUAGE plpgsql;
            """
        )
        schema_editor.execute(
            """
            CREATE TRIGGER approved_dpd_policy_version_guard
            BEFORE UPDATE OR DELETE ON dpd_operational_bucket_schemes
            FOR EACH ROW EXECUTE FUNCTION retain_approved_dpd_policy_version();
            """
        )
    elif vendor == "sqlite":
        schema_editor.execute(
            """
            CREATE TRIGGER current_dpd_snapshot_owner_guard
            BEFORE UPDATE OF loan_account_id ON dpd_statuses
            FOR EACH ROW
            BEGIN
                SELECT RAISE(ABORT, 'DPD snapshots cannot be reparented');
            END;
            """
        )
        # SQLite's Django test flush is implemented as DELETE statements, so the
        # database-only delete guard is exercised by the authoritative PostgreSQL
        # contract. Runtime SQLite callers remain protected by the model/queryset.
        schema_editor.execute(
            """
            CREATE TRIGGER approved_dpd_policy_version_guard_update
            BEFORE UPDATE ON dpd_operational_bucket_schemes
            FOR EACH ROW
            BEGIN
                SELECT RAISE(ABORT, 'approved DPD policy versions are immutable');
            END;
            """
        )


def drop_owner_guards(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor == "postgresql":
        schema_editor.execute(
            "DROP TRIGGER IF EXISTS current_dpd_snapshot_owner_guard ON dpd_statuses;"
        )
        schema_editor.execute("DROP FUNCTION IF EXISTS enforce_current_dpd_snapshot_owner();")
        schema_editor.execute(
            "DROP TRIGGER IF EXISTS approved_dpd_policy_version_guard "
            "ON dpd_operational_bucket_schemes;"
        )
        schema_editor.execute("DROP FUNCTION IF EXISTS retain_approved_dpd_policy_version();")
    elif vendor == "sqlite":
        schema_editor.execute("DROP TRIGGER IF EXISTS current_dpd_snapshot_owner_guard;")
        schema_editor.execute("DROP TRIGGER IF EXISTS approved_dpd_policy_version_guard_update;")


class Migration(migrations.Migration):
    dependencies = [
        ("loans", "0009_dpd_pointer_integrity"),
        ("monitoring", "0004_quarterly_mis"),
    ]

    operations = [migrations.RunPython(create_owner_guards, drop_owner_guards)]
