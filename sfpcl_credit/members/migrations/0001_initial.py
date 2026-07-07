# Generated for Ralph slice 004A.

import uuid

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("identity", "0002_permission_rolepermission_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Member",
            fields=[
                ("member_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("member_number", models.CharField(blank=True, max_length=80, null=True, unique=True)),
                ("member_type", models.CharField(db_index=True, max_length=60)),
                ("legal_name", models.CharField(db_index=True, max_length=255)),
                ("display_name", models.CharField(max_length=255)),
                ("folio_number", models.CharField(db_index=True, max_length=100)),
                ("membership_start_date", models.DateField(blank=True, null=True)),
                ("membership_status", models.CharField(db_index=True, max_length=60)),
                ("pan_encrypted", models.TextField()),
                ("pan_hash", models.CharField(db_index=True, max_length=128)),
                ("aadhaar_encrypted", models.TextField(blank=True)),
                ("aadhaar_hash", models.CharField(blank=True, db_index=True, max_length=128)),
                ("registered_address_line1", models.CharField(blank=True, max_length=255)),
                ("registered_address_line2", models.CharField(blank=True, max_length=255)),
                ("registered_village_city", models.CharField(blank=True, max_length=150)),
                ("registered_district", models.CharField(blank=True, max_length=150)),
                ("registered_state", models.CharField(blank=True, max_length=150)),
                ("registered_pincode", models.CharField(blank=True, max_length=20)),
                ("mobile_number", models.CharField(blank=True, db_index=True, max_length=20)),
                ("email", models.EmailField(blank=True, db_index=True, max_length=255)),
                ("kyc_status", models.CharField(db_index=True, max_length=60)),
                ("rekyc_due_date", models.DateField(blank=True, db_index=True, null=True)),
                ("default_status", models.CharField(db_index=True, max_length=60)),
                ("active_member_status_id", models.UUIDField(blank=True, null=True)),
                ("primary_bank_account_id", models.UUIDField(blank=True, null=True)),
                ("number_of_shares", models.PositiveIntegerField(blank=True, null=True)),
                ("holding_mode", models.CharField(blank=True, max_length=60)),
                ("available_share_count", models.PositiveIntegerField(blank=True, null=True)),
                ("active_member_status", models.CharField(blank=True, max_length=60)),
                ("active_member_verified_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(blank=True, null=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("created_by_user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="created_members", to="identity.user")),
                ("updated_by_user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="updated_members", to="identity.user")),
            ],
            options={
                "db_table": "members",
            },
        ),
        migrations.AddIndex(
            model_name="member",
            index=models.Index(fields=["member_type", "membership_status"], name="idx_members_type_status"),
        ),
        migrations.AddIndex(
            model_name="member",
            index=models.Index(fields=["folio_number"], name="idx_members_folio_number"),
        ),
        migrations.AddIndex(
            model_name="member",
            index=models.Index(fields=["pan_hash"], name="idx_members_pan_hash"),
        ),
        migrations.AddIndex(
            model_name="member",
            index=models.Index(fields=["aadhaar_hash"], name="idx_members_aadhaar_hash"),
        ),
        migrations.AddIndex(
            model_name="member",
            index=models.Index(fields=["mobile_number"], name="idx_members_mobile"),
        ),
        migrations.AddIndex(
            model_name="member",
            index=models.Index(fields=["kyc_status"], name="idx_members_kyc_status"),
        ),
        migrations.AddIndex(
            model_name="member",
            index=models.Index(fields=["default_status"], name="idx_members_default_status"),
        ),
    ]
