"""Anchor legal checklist constraint state in its owning migration graph.

Disbursements 0005 replaced two Epic-009 placeholder constraints with their
live names. This legal-owned descendant makes that reviewed historical state a
prerequisite for every future legal migration without replaying schema or data
operations.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("communications", "0004_advice_outbox_and_receipt_owner"),
        (
            "disbursements",
            "0005_disbursementadviceintent_loanregisterupdate_and_more",
        ),
        (
            "disbursements",
            "0007_remove_disbursement_disb_success_evidence_complete_and_more",
        ),
        ("legal_documents", "0014_staff_documentation_durable_actions"),
    ]

    operations = []
