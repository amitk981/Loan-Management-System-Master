"""Public credit action/write parity regression matrix for slice 006X4."""

from django.test import TestCase

from sfpcl_credit.credit.modules.appraisal_workflow import AppraisalWorkflow
from sfpcl_credit.credit.modules.common import CreditModulePermissionDenied
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.tests import test_appraisal_api as appraisal_fixtures
from sfpcl_credit.workflows.models import WorkflowEvent


ACTION_MATRIX = (
    ("credit.appraisal.update", "You do not have permission to update appraisal notes."),
    (
        "revalidate_appraisal_prerequisites",
        "You do not have permission to revalidate appraisal prerequisites.",
    ),
    (
        "credit.appraisal.submit_review",
        "You do not have permission to submit appraisal notes for review.",
    ),
    ("credit.appraisal.review", "You do not have permission to review appraisal notes."),
    (
        "credit.appraisal.submit_sanction",
        "You do not have permission to submit appraisals for sanction.",
    ),
)


class CreditActionParityMatrixTests(TestCase):
    setUp = appraisal_fixtures.AppraisalApiTests.setUp
    _payload = appraisal_fixtures.AppraisalApiTests._payload
    _permission = staticmethod(appraisal_fixtures.AppraisalApiTests._permission)
    _user = staticmethod(appraisal_fixtures.AppraisalApiTests._user)

    def test_permission_denials_project_the_public_write_reason_without_success_evidence(self):
        created = AppraisalWorkflow().create_or_update(
            actor=self.actor,
            application_id=self.application.pk,
            payload=self._payload(),
        ).snapshot
        appraisal_id = created["loan_appraisal_note_id"]
        read_only = {"credit.appraisal.create"}
        projection = AppraisalWorkflow().get(
            actor=self.actor,
            application_id=self.application.pk,
            actor_permissions=read_only,
        ).snapshot
        actions = {item["action_code"]: item for item in projection["available_actions"]}

        for action_code, expected_reason in ACTION_MATRIX:
            with self.subTest(action_code=action_code):
                self.assertEqual(
                    set(actions[action_code]),
                    {
                        "action_code",
                        "label",
                        "enabled",
                        "disabled_reason",
                        "required_permission",
                        "required_role",
                    },
                )
                self.assertFalse(actions[action_code]["enabled"])
                self.assertEqual(actions[action_code]["disabled_reason"], expected_reason)

        audit_count = AuditLog.objects.count()
        event_count = WorkflowEvent.objects.count()
        with self.assertRaisesMessage(CreditModulePermissionDenied, ACTION_MATRIX[0][1]):
            AppraisalWorkflow().create_or_update(
                actor=self.actor,
                application_id=self.application.pk,
                payload={"recommendation": "conditions"},
                partial=True,
                actor_permissions=read_only,
            )

        self.assertEqual(AuditLog.objects.count(), audit_count)
        self.assertEqual(WorkflowEvent.objects.count(), event_count)
        self.assertEqual(
            AppraisalWorkflow().get(
                actor=self.actor,
                application_id=self.application.pk,
                actor_permissions=read_only,
            ).snapshot["recommendation"],
            created["recommendation"],
        )
        self.assertEqual(str(self.application.pk), projection["loan_application_id"])
        self.assertEqual(appraisal_id, projection["loan_appraisal_note_id"])
