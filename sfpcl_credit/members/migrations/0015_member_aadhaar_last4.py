from django.db import migrations, models


def backfill_aadhaar_last4(apps, schema_editor):
    Member = apps.get_model("members", "Member")
    for member in Member.objects.exclude(aadhaar_encrypted="").iterator(chunk_size=500):
        suffix = str(member.aadhaar_encrypted).rsplit(":", 1)[-1]
        if len(suffix) == 4 and suffix.isdigit():
            Member.objects.filter(pk=member.pk).update(aadhaar_last4=suffix)


class Migration(migrations.Migration):
    dependencies = [("members", "0014_remove_memberscopeassignment_uniq_member_scope_assignment_and_more")]

    operations = [
        migrations.AddField(
            model_name="member",
            name="aadhaar_last4",
            field=models.CharField(
                blank=True, db_default="", default="", db_index=True, max_length=4
            ),
        ),
        migrations.AlterField(
            model_name="member",
            name="number_of_shares",
            field=models.PositiveIntegerField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name="bankaccount",
            name="account_number_last4",
            field=models.CharField(blank=True, db_index=True, max_length=4),
        ),
        migrations.AlterField(
            model_name="cancelledcheque",
            name="account_number_last4",
            field=models.CharField(blank=True, db_index=True, max_length=4),
        ),
        migrations.RunPython(backfill_aadhaar_last4, migrations.RunPython.noop),
    ]
