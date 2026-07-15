"""Anchor application-owned evidence fields in the legal migration graph.

Applications 0016 physically and statefully added the two retained ChecklistAction
relations. This no-op legal-owned descendant makes that state an explicit prerequisite
for every future legal_documents migration without replaying either column.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("applications", "0016_bankverificationdecision_and_more"),
        ("legal_documents", "0012_portal_documentation_submission"),
    ]

    operations = []
