import json
from datetime import date

from django.test import Client, TestCase


class ExtensionNoteWorkflowApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_default_grace_assessment_api import (
            DefaultGraceAssessmentApiTests,
        )

        fixture = DefaultGraceAssessmentApiTests(
            "test_credit_assessment_team_stores_expired_case_assessment_and_projects_it"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.account
        self.actor = fixture.actor
        self.auth = fixture.auth
        self.client = Client()
        user_fixture = fixture.fixture.fixture.fixture.fixture.owner.fixture.fixture
        user_fixture._grant(self.actor, "defaults.extension.grant")

    def _eligible_case(self):
        from sfpcl_credit.defaults.modules.default_workflow import DefaultWorkflow

        case_id = self.fixture._open_case(date(2026, 3, 31))
        DefaultWorkflow.process_grace_expiries(
            as_of_date=date(2026, 7, 1), actor=self.actor
        )
        assessor, assessor_auth = self.fixture._make_assessor()
        evidence = self.fixture._evidence_document(suffix="extension-assessment")
        response = self.client.post(
            f"/api/v1/default-cases/{case_id}/assess/",
            data=json.dumps(self.fixture._assessment_payload(evidence.pk)),
            content_type="application/json",
            **assessor_auth,
        )
        self.assertEqual(response.status_code, 200, response.content)
        return case_id, assessor

    def _extension_document(self):
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.legal_documents.models import LoanDocument

        file = DocumentFile.objects.create(
            file_name="extension-note.pdf",
            storage_provider="local",
            storage_key="defaults/extension-note.pdf",
            sensitivity_level="confidential",
        )
        loan_document = LoanDocument.objects.create(
            loan_application=self.account.loan_application,
            document_type="extension_note",
            document_category="recovery",
            document=file,
            output_format="pdf",
            generation_status="generated",
            execution_status="pending",
            verification_status="pending",
        )
        return loan_document

    def _grant_extension(self):
        case_id, _ = self._eligible_case()
        document = self._extension_document()
        payload = {
            "extension_reason": "Non-intentional crop loss delayed repayment.",
            "extension_start_date": "2026-07-01",
            "extension_end_date": "2027-06-30",
            "document_id": str(document.pk),
        }
        response = self.client.post(
            f"/api/v1/default-cases/{case_id}/grant-extension/",
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(response.status_code, 200, response.content)
        return case_id, response.json()["data"]

    def test_eligible_case_grants_one_audited_extension_with_exact_loan_file_note(self):
        from sfpcl_credit.defaults.models import DefaultCase, ExtensionNote
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.workflows.models import WorkflowEvent

        case_id, _ = self._eligible_case()
        document = self._extension_document()
        payload = {
            "extension_reason": "Non-intentional crop loss delayed repayment.",
            "extension_start_date": "2026-07-01",
            "extension_end_date": "2027-06-30",
            "document_id": str(document.pk),
        }

        response = self.client.post(
            f"/api/v1/default-cases/{case_id}/grant-extension/",
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        note = ExtensionNote.objects.get()
        self.assertEqual(
            response.json()["data"],
            {
                "extension_note_id": str(note.pk),
                "default_case_id": case_id,
                "loan_account_id": str(self.account.pk),
                **payload,
                "prepared_by_user_id": str(self.actor.pk),
                "approved_by_user_id": None,
                "status": "active",
            },
        )
        case = DefaultCase.objects.get(pk=case_id)
        self.assertEqual(case.default_case_status, "extension_granted")
        self.assertEqual(case.extension_note, note)
        self.assertEqual(note.loan_document, document)
        self.assertEqual(
            AuditLog.objects.filter(action="extension.granted").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="default_case", to_state="extension_granted"
            ).count(),
            1,
        )

    def test_case_detail_projects_grant_action_then_retained_extension_note(self):
        case_id, _ = self._eligible_case()
        document = self._extension_document()
        payload = {
            "extension_reason": "Non-intentional crop loss delayed repayment.",
            "extension_start_date": "2026-07-01",
            "extension_end_date": "2027-06-30",
            "document_id": str(document.pk),
        }

        before = self.client.get(f"/api/v1/default-cases/{case_id}/", **self.auth)
        self.assertEqual(before.status_code, 200, before.content)
        self.assertEqual(before.json()["data"]["available_actions"], ["grant_extension"])

        granted = self.client.post(
            f"/api/v1/default-cases/{case_id}/grant-extension/",
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(granted.status_code, 200, granted.content)
        detail = self.client.get(f"/api/v1/default-cases/{case_id}/", **self.auth)

        self.assertEqual(detail.status_code, 200, detail.content)
        self.assertEqual(detail.json()["data"]["extension_note"], granted.json()["data"])
        self.assertEqual(detail.json()["data"]["available_actions"], [])

    def test_unpaid_extension_expiry_marks_one_review_required_under_replay(self):
        from sfpcl_credit.defaults.models import DefaultCase, ExtensionNote
        from sfpcl_credit.defaults.modules.default_workflow import DefaultWorkflow
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.scheduler.models import ScheduledJob

        case_id, _ = self._grant_extension()

        first = DefaultWorkflow.process_extension_expiries(
            as_of_date=date(2027, 7, 1), actor=self.actor
        )
        replay = DefaultWorkflow.process_extension_expiries(
            as_of_date=date(2027, 7, 1), actor=self.actor
        )

        self.assertEqual(
            first,
            {
                "processed_count": 1,
                "cured_count": 0,
                "expired_count": 1,
                "review_tasks_created_count": 1,
                "failure_count": 0,
            },
        )
        self.assertEqual(replay["processed_count"], 0)
        self.assertEqual(
            DefaultCase.objects.get(pk=case_id).default_case_status,
            "extension_expired",
        )
        self.assertEqual(ExtensionNote.objects.get().status, "expired")
        task = ScheduledJob.objects.get(idempotency_key=f"extension-review:{case_id}")
        self.assertEqual(task.job_type, "default_assessment")
        self.assertEqual(task.related_entity_type, "default_case")
        self.assertEqual(AuditLog.objects.filter(action="extension.expired").count(), 1)
        self.assertFalse(hasattr(DefaultCase.objects.get(pk=case_id), "non_payment_note"))

    def test_payment_during_extension_cures_case_without_deleting_or_rewriting_note(self):
        from sfpcl_credit.defaults.models import DefaultCase, ExtensionNote
        from sfpcl_credit.defaults.modules.default_workflow import DefaultWorkflow
        from sfpcl_credit.identity.models import AuditLog

        case_id, granted = self._grant_extension()
        type(self.account).objects.filter(pk=self.account.pk).update(
            principal_outstanding="0.00", total_outstanding="0.00"
        )

        outcome = DefaultWorkflow.process_extension_expiries(
            as_of_date=date(2026, 8, 1), actor=self.actor
        )

        self.assertEqual(outcome["cured_count"], 1)
        case = DefaultCase.objects.get(pk=case_id)
        self.assertEqual(case.default_case_status, "resolved_by_repayment")
        self.assertIsNotNone(case.closed_at)
        note = ExtensionNote.objects.get(pk=granted["extension_note_id"])
        self.assertEqual(note.status, "active")
        self.assertEqual(note.extension_start_date.isoformat(), granted["extension_start_date"])
        self.assertEqual(note.extension_end_date.isoformat(), granted["extension_end_date"])
        self.assertEqual(AuditLog.objects.filter(action="extension.cured").count(), 1)

    def test_exact_replay_converges_and_changed_replay_conflicts(self):
        from sfpcl_credit.defaults.models import ExtensionNote
        from sfpcl_credit.identity.models import AuditLog

        case_id, granted = self._grant_extension()
        payload = {
            "extension_reason": granted["extension_reason"],
            "extension_start_date": granted["extension_start_date"],
            "extension_end_date": granted["extension_end_date"],
            "document_id": granted["document_id"],
        }
        replay = self.client.post(
            f"/api/v1/default-cases/{case_id}/grant-extension/",
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth,
        )
        changed = self.client.post(
            f"/api/v1/default-cases/{case_id}/grant-extension/",
            data=json.dumps({**payload, "extension_reason": "Changed hardship reason."}),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], granted)
        self.assertEqual(changed.status_code, 409, changed.content)
        self.assertEqual(ExtensionNote.objects.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="extension.granted").count(), 1)

    def test_ineligible_classification_dates_payment_closure_and_authority_are_rejected(self):
        from django.utils import timezone

        from sfpcl_credit.defaults.models import DefaultAssessment, ExtensionNote

        case_id, _ = self._eligible_case()
        document = self._extension_document()
        valid = {
            "extension_reason": "Documented non-intentional hardship.",
            "extension_start_date": "2026-07-01",
            "extension_end_date": "2027-06-30",
            "document_id": str(document.pk),
        }
        url = f"/api/v1/default-cases/{case_id}/grant-extension/"

        for payload in (
            {**valid, "extension_start_date": "2026-06-30"},
            {**valid, "extension_end_date": "2027-07-01"},
            {**valid, "extension_reason": ""},
            {**valid, "caller_says_eligible": True},
        ):
            with self.subTest(payload=payload):
                response = self.client.post(
                    url, data=json.dumps(payload), content_type="application/json", **self.auth
                )
                self.assertEqual(response.status_code, 400, response.content)
                self.assertEqual(ExtensionNote.objects.count(), 0)

        DefaultAssessment.objects.update(payment_failure_classification="intentional")
        intentional = self.client.post(
            url, data=json.dumps(valid), content_type="application/json", **self.auth
        )
        self.assertEqual(intentional.status_code, 409, intentional.content)
        DefaultAssessment.objects.update(payment_failure_classification="unclear")
        unclear = self.client.post(
            url, data=json.dumps(valid), content_type="application/json", **self.auth
        )
        self.assertEqual(unclear.status_code, 409, unclear.content)
        DefaultAssessment.objects.update(payment_failure_classification="non_intentional")

        type(self.account).objects.filter(pk=self.account.pk).update(
            principal_outstanding="0.00", total_outstanding="0.00"
        )
        paid = self.client.post(
            url, data=json.dumps(valid), content_type="application/json", **self.auth
        )
        self.assertEqual(paid.status_code, 409, paid.content)
        type(self.account).objects.filter(pk=self.account.pk).update(
            principal_outstanding="1000.00",
            total_outstanding="1000.00",
            closed_at=timezone.now(),
        )
        closed = self.client.post(
            url, data=json.dumps(valid), content_type="application/json", **self.auth
        )
        self.assertEqual(closed.status_code, 409, closed.content)

        user_fixture = self.fixture.fixture.fixture.fixture.fixture.owner.fixture.fixture
        denied = user_fixture._user("field_officer", "Extension Denied")
        auth_fixture = self.fixture.fixture.fixture.fixture.fixture.owner.fixture
        denied_response = self.client.post(
            url,
            data=json.dumps(valid),
            content_type="application/json",
            **auth_fixture._auth(denied),
        )
        self.assertEqual(denied_response.status_code, 403, denied_response.content)
        self.assertEqual(ExtensionNote.objects.count(), 0)

    def test_missing_wrong_type_and_foreign_extension_documents_are_rejected(self):
        from uuid import uuid4

        from sfpcl_credit.applications.models import LoanApplication
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.legal_documents.models import LoanDocument

        case_id, _ = self._eligible_case()
        wrong_type = self.fixture._evidence_document(suffix="wrong-extension-type")
        foreign_application = LoanApplication.objects.create(
            member=self.account.member,
            borrower_type=self.account.loan_application.borrower_type,
            received_by_user=self.actor,
        )
        foreign_file = DocumentFile.objects.create(
            file_name="foreign-extension-note.pdf",
            storage_provider="local",
            storage_key="defaults/foreign-extension-note.pdf",
            sensitivity_level="confidential",
        )
        foreign = LoanDocument.objects.create(
            loan_application=foreign_application,
            document_type="extension_note",
            document_category="recovery",
            document=foreign_file,
            output_format="pdf",
            generation_status="generated",
            execution_status="pending",
            verification_status="pending",
        )
        base = {
            "extension_reason": "Documented non-intentional hardship.",
            "extension_start_date": "2026-07-01",
            "extension_end_date": "2027-06-30",
        }

        wrong_type_loan_document = LoanDocument.objects.get(document=wrong_type)
        for document_id in (uuid4(), wrong_type_loan_document.pk, foreign.pk):
            with self.subTest(document_id=document_id):
                response = self.client.post(
                    f"/api/v1/default-cases/{case_id}/grant-extension/",
                    data=json.dumps({**base, "document_id": str(document_id)}),
                    content_type="application/json",
                    **self.auth,
                )
                self.assertEqual(response.status_code, 400, response.content)

    def test_active_extension_dates_are_immutable(self):
        from sfpcl_credit.defaults.models import ExtensionNote

        _, granted = self._grant_extension()
        note = ExtensionNote.objects.get(pk=granted["extension_note_id"])
        note.extension_end_date = date(2027, 7, 1)
        with self.assertRaisesMessage(ValueError, "effective dates are immutable"):
            note.save()
        with self.assertRaisesMessage(ValueError, "effective dates are immutable"):
            ExtensionNote.objects.filter(pk=note.pk).update(
                extension_start_date=date(2026, 7, 2)
            )
