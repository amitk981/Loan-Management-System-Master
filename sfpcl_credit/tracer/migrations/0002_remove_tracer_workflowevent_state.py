from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tracer", "0001_initial"),
        ("workflows", "0001_canonical_workflow_event"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name="WorkflowEvent"),
            ],
        ),
    ]
