import uuid

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [("identity", "0003_portal_member_auth"), ("members", "0008_cancelledcheque_bankaccount_and_more")]
    operations = [
        migrations.AddField(
            model_name="member", name="version", field=models.PositiveIntegerField(db_default=1, default=1)
        ),
        migrations.AddField(model_name="producerinstitutionprofile", name="authorised_signatory_pan_encrypted", field=models.TextField(blank=True)),
        migrations.AddField(model_name="producerinstitutionprofile", name="authorised_signatory_pan_hash", field=models.CharField(blank=True, db_index=True, max_length=128)),
        migrations.AddField(model_name="producerinstitutionprofile", name="authorised_signatory_aadhaar_encrypted", field=models.TextField(blank=True)),
        migrations.AddField(model_name="producerinstitutionprofile", name="authorised_signatory_aadhaar_hash", field=models.CharField(blank=True, db_index=True, max_length=128)),
        migrations.CreateModel(
            name="MemberChangeHistory",
            fields=[
                ("member_change_history_id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("change_type", models.CharField(max_length=40)),
                ("changed_fields", models.JSONField(default=list)),
                ("old_value_json", models.JSONField(default=dict)),
                ("new_value_json", models.JSONField(default=dict)),
                ("reason", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("actor_user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="member_changes", to="identity.user")),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="change_history", to="members.member")),
            ],
            options={"db_table": "member_change_history", "ordering": ["created_at", "member_change_history_id"]},
        ),
    ]
