from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from django.db import migrations
from django.db.migrations.loader import MigrationLoader
from django.test import TestCase
from django.utils import timezone

from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
)
from sfpcl_credit.identity.models import PortalAccount, Role, User
from sfpcl_credit.legal_documents.migration_state_guard import (
    _CHECKLIST_KEY,
    _HISTORICAL_MODULE,
    _HISTORICAL_PATH,
    _is_retained_transition,
)
from sfpcl_credit.processes.advice_evidence_migration import _template_values


class ArchitectureReviewContractProbes(TestCase):
    def test_source_dispatcher_exposes_idempotent_send(self):
        self.assertTrue(
            hasattr(CommunicationDispatcher, "send"),
            "Source §40.1 requires CommunicationDispatcher.send(..., idempotency_key).",
        )

    def test_async_task_has_a_discoverable_runtime_registration(self):
        project = Path(__file__).resolve().parents[5] / "sfpcl_credit"
        settings = (project / "config" / "settings.py").read_text()
        task_source = (project / "processes" / "tasks.py").read_text()
        self.assertTrue(
            (project / "config" / "celery.py").exists()
            and "CELERY_" in settings
            and (
                ".delay(" in task_source
                or "apply_async(" in task_source
                or "beat_schedule" in settings
            ),
            "Queued rows have no Celery app/configuration, enqueue call, or beat schedule.",
        )

    def test_legacy_template_provenance_is_not_upgraded_from_current_template(self):
        template = SimpleNamespace(
            pk=uuid4(),
            template_code="disbursement_advice_email_v1",
            template_name="Mutable current name",
            template_type="email",
            language_code="en",
            audience="borrower",
            template_version="v1",
            approval_status="approved",
            effective_from=timezone.localdate(),
            effective_to=None,
            variables_json=["borrower_name"],
            subject_template="Advice {{ borrower_name }}",
            body_template="Body {{ borrower_name }}",
        )
        self.assertEqual(
            _template_values(template)["template_provenance_status"],
            "legacy_partial",
            "009H4 forbids reconstructing missing historical provenance from a later template row.",
        )

    def test_historical_guard_rejects_extra_same_model_mutation(self):
        after = MigrationLoader(None).project_state()
        before = after.clone()
        before_model = before.models[_CHECKLIST_KEY]
        before_model.options["constraints"] = [
            item
            for item in before_model.options.get("constraints", ())
            if item.name != "checklist_finance_requires_sanction"
        ]
        before_model.options["review_probe_extra_change"] = "before"
        after.models[_CHECKLIST_KEY].options["review_probe_extra_change"] = "after"
        operation_type = type(
            "AddLegalChecklistConstraint",
            (migrations.operations.base.Operation,),
            {"__module__": _HISTORICAL_MODULE},
        )
        self.assertFalse(
            _is_retained_transition(
                path=_HISTORICAL_PATH,
                operation=operation_type(),
                index=2,
                before=before,
                after=after,
                changed_models={_CHECKLIST_KEY},
            ),
            "The exact historical exception must not bless an extra mutation on DocumentChecklist.",
        )

    def test_pre_initiation_portal_stage_consumes_current_sap_truth(self):
        from sfpcl_credit.tests.test_disbursement_initiation_api import (
            DisbursementInitiationApiTests,
        )

        owner = DisbursementInitiationApiTests(
            "test_current_ready_payment_is_recorded_once_without_transfer_side_effects"
        )
        owner.setUp()
        portal_role, _ = Role.objects.get_or_create(
            role_code="borrower_portal_user",
            defaults={
                "role_name": "Borrower Portal User",
                "is_system_role": True,
                "status": "active",
            },
        )
        portal_user = User.objects.create(
            full_name=owner.application.member.display_name,
            email="architecture.review.portal@example.com",
            status="active",
            primary_role=portal_role,
        )
        portal_user.set_password("ArchitectureReview123!")
        portal_user.save()
        PortalAccount.objects.create(
            member=owner.application.member,
            user=portal_user,
            status=PortalAccount.STATUS_ACTIVE,
            activated_at=timezone.now(),
        )
        login = self.client.post(
            "/api/v1/portal/auth/login/",
            data={
                "identifier": portal_user.email,
                "password": "ArchitectureReview123!",
            },
            content_type="application/json",
        )
        response = self.client.get(
            f"/api/v1/portal/applications/{owner.application.pk}/disbursement-status/",
            HTTP_AUTHORIZATION=f"Bearer {login.json()['data']['access_token']}",
        )
        self.assertEqual(response.status_code, 200, response.content)
        timeline = {item["code"]: item for item in response.json()["data"]["timeline"]}
        self.assertEqual(timeline["sap_setup"]["status"], "complete")
        self.assertEqual(timeline["payment_initiated"]["status"], "pending")

