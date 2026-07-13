import uuid
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):
    dependencies = [("identity", "0003_portal_member_auth"), ("members", "0009_member_identity_governance")]
    operations = [migrations.AddConstraint(model_name="member", constraint=models.UniqueConstraint(condition=~models.Q(("pan_hash", "")), fields=("pan_hash",), name="uniq_member_pan_hash")),
    migrations.AddConstraint(model_name="member", constraint=models.UniqueConstraint(condition=~models.Q(("aadhaar_hash", "")), fields=("aadhaar_hash",), name="uniq_member_aadhaar_hash")),
    migrations.CreateModel(name="MemberIdentityChangeRequest", fields=[
        ("identity_change_request_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
        ("proposed_pan_encrypted", models.TextField(blank=True)), ("proposed_pan_hash", models.CharField(blank=True, max_length=128)),
        ("proposed_aadhaar_encrypted", models.TextField(blank=True)), ("proposed_aadhaar_hash", models.CharField(blank=True, max_length=128)),
        ("reason", models.TextField()), ("member_version", models.PositiveIntegerField()), ("status", models.CharField(db_index=True, default="pending", max_length=20)),
        ("created_at", models.DateTimeField(default=django.utils.timezone.now)), ("approved_at", models.DateTimeField(blank=True, null=True)),
        ("approver_user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="approved_member_identity_changes", to="identity.user")),
        ("member", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="identity_change_requests", to="members.member")),
        ("requester_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="requested_member_identity_changes", to="identity.user")),
    ], options={"db_table": "member_identity_change_requests"})]
