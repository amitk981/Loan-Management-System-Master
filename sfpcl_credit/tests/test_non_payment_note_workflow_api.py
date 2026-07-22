import json
import tempfile
from datetime import date

from django.test import Client, TestCase, override_settings


@override_settings(DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-non-payment-note-"))
class NonPaymentNoteWorkflowApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_extension_note_workflow_api import (
            ExtensionNoteWorkflowApiTests,
        )

        fixture = ExtensionNoteWorkflowApiTests(
            "test_eligible_case_grants_one_audited_extension_with_exact_loan_file_note"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.account
        self.client = Client()

    def _expired_case(self):
        from sfpcl_credit.defaults.modules.default_workflow import DefaultWorkflow

        case_id, _ = self.fixture._grant_extension()
        type(self.account).objects.filter(pk=self.account.pk).update(
            principal_outstanding="300000.00",
            interest_outstanding="45000.00",
            charges_outstanding="0.00",
            total_outstanding="345000.00",
        )
        outcome = DefaultWorkflow.process_extension_expiries(
            as_of_date=date(2027, 7, 1), actor=self.fixture.actor
        )
        self.assertEqual(outcome["expired_count"], 1)
        return case_id

    def _creator(self):
        assessor, auth = self.fixture.fixture._make_assessor()
        user_fixture = self.fixture.fixture.fixture.fixture.fixture.fixture.owner.fixture.fixture
        user_fixture._grant(assessor, "defaults.non_payment_note.create")
        return assessor, auth

    def _create_note(self):
        case_id = self._expired_case()
        creator, auth = self._creator()
        payload = {
            "reason_for_non_payment": "Borrower remains unable to repay after the extension.",
            "intentionality_assessment": "unclear",
            "outstanding_principal_amount": "300000.00",
            "outstanding_interest_amount": "45000.00",
            "recommended_recovery_action": "present_to_sanction_committee",
        }
        response = self.client.post(
            f"/api/v1/default-cases/{case_id}/non-payment-note/",
            data=json.dumps(payload),
            content_type="application/json",
            **auth,
        )
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()["data"], auth

    def _configure_committee(self):
        from sfpcl_credit.approvals.models import SanctionCommittee

        SanctionCommittee.objects.update(status=SanctionCommittee.STATUS_INACTIVE)
        user_fixture = self.fixture.fixture.fixture.fixture.fixture.fixture.owner.fixture.fixture
        cfo = user_fixture._user("cfo", "Recovery CFO")
        director_1 = user_fixture._user("director", "Recovery Director One")
        director_2 = user_fixture._user("director", "Recovery Director Two")
        for user in (cfo, director_1, director_2):
            user_fixture._grant(user, "approvals.case.read", "defaults.case.read")
        user_fixture._grant(cfo, "approvals.case.return")
        committee = SanctionCommittee.objects.create(
            committee_name="Recovery Sanction Committee",
            cfo_user=cfo,
            director_1_user=director_1,
            director_2_user=director_2,
            board_meeting_reference="BOARD-RECOVERY-2027",
            effective_from=date(2026, 1, 1),
            status=SanctionCommittee.STATUS_ACTIVE,
            version_number="recovery-v1",
        )
        return committee, [cfo, director_1, director_2]

    def test_expired_unpaid_extension_creates_one_frozen_source_derived_draft(self):
        from sfpcl_credit.defaults.models import DefaultCase, NonPaymentNote
        from sfpcl_credit.documents.storage import LocalDocumentStorage
        from sfpcl_credit.identity.models import AuditLog

        case_id = self._expired_case()
        creator, auth = self._creator()
        payload = {
            "reason_for_non_payment": "Borrower remains unable to repay after the extension.",
            "intentionality_assessment": "unclear",
            "outstanding_principal_amount": "300000.00",
            "outstanding_interest_amount": "45000.00",
            "recommended_recovery_action": "present_to_sanction_committee",
        }

        response = self.client.post(
            f"/api/v1/default-cases/{case_id}/non-payment-note/",
            data=json.dumps(payload),
            content_type="application/json",
            **auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        note = NonPaymentNote.objects.get()
        data = response.json()["data"]
        self.assertEqual(data["non_payment_note_id"], str(note.pk))
        self.assertEqual(data["default_case_id"], case_id)
        self.assertEqual(data["loan_account_id"], str(self.account.pk))
        self.assertEqual(data["outstanding_principal_amount"], "300000.00")
        self.assertEqual(data["outstanding_interest_amount"], "45000.00")
        self.assertEqual(data["reason_for_non_payment"], payload["reason_for_non_payment"])
        self.assertEqual(data["intentionality_assessment"], "unclear")
        self.assertEqual(
            data["recommended_recovery_action"], "present_to_sanction_committee"
        )
        self.assertEqual(data["prepared_by_user_id"], str(creator.pk))
        self.assertEqual(data["status"], "draft")
        self.assertEqual(data["approval_case_id"], None)
        self.assertEqual(data["submitted_to_sanction_committee_at"], None)
        self.assertEqual(data["frozen_case_facts"]["original_due_date"], "2026-03-31")
        self.assertEqual(data["frozen_case_facts"]["grace_period_end_date"], "2026-06-30")
        self.assertEqual(data["frozen_case_facts"]["extension_end_date"], "2027-06-30")
        self.assertTrue(note.evidence_document_ids_json)
        self.assertEqual(data["evidence_document_ids"], note.evidence_document_ids_json)
        self.assertEqual(data["document_id"], str(note.loan_document_id))
        self.assertEqual(note.loan_document.document_type, "non_payment_note")
        self.assertEqual(note.loan_document.document_category, "recovery")
        self.assertEqual(note.loan_document.generation_status, "generated")
        self.assertTrue(
            LocalDocumentStorage().read_verified(note.loan_document.document).startswith(b"%PDF")
        )
        self.assertEqual(
            DefaultCase.objects.get(pk=case_id).default_case_status,
            "non_payment_under_review",
        )
        self.assertEqual(AuditLog.objects.filter(action="non_payment_note.created").count(), 1)

    def test_credit_manager_submission_freezes_note_and_creates_one_committee_case(self):
        from sfpcl_credit.approvals.models import ApprovalCase
        from sfpcl_credit.defaults.models import NonPaymentNote
        from sfpcl_credit.identity.models import AuditLog

        created, _ = self._create_note()
        committee, approvers = self._configure_committee()
        submitter = self.fixture.actor
        user_fixture = self.fixture.fixture.fixture.fixture.fixture.fixture.owner.fixture.fixture
        user_fixture._grant(submitter, "defaults.non_payment_note.submit")

        response = self.client.post(
            f"/api/v1/non-payment-notes/{created['non_payment_note_id']}/submit-to-sanction-committee/",
            data=json.dumps({}),
            content_type="application/json",
            **self.fixture.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        note = NonPaymentNote.objects.get(pk=created["non_payment_note_id"])
        case = ApprovalCase.objects.get(pk=note.approval_case_id)
        self.assertEqual(note.status, "submitted")
        self.assertIsNotNone(note.submitted_to_sanction_committee_at)
        self.assertEqual(case.approval_type, "recovery")
        self.assertEqual(case.current_status, "pending")
        self.assertEqual(case.related_entity_type, "non_payment_note")
        self.assertEqual(case.related_entity_id, note.pk)
        self.assertEqual(case.sanction_committee, committee)
        self.assertEqual(
            [item["user_id"] for item in case.required_approvers_json],
            [str(user.pk) for user in approvers],
        )
        self.assertEqual(response.json()["data"]["approval_case_id"], str(case.pk))
        self.assertEqual(AuditLog.objects.filter(action="non_payment_note.submitted").count(), 1)
        auth_fixture = self.fixture.fixture.fixture.fixture.fixture.fixture.owner.fixture
        committee_read = self.client.get(
            f"/api/v1/approval-cases/{case.pk}/", **auth_fixture._auth(approvers[0])
        )
        self.assertEqual(committee_read.status_code, 200, committee_read.content)
        self.assertEqual(committee_read.json()["data"]["available_actions"], [])

        from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant

        auditor = user_fixture._user("internal_auditor", "Recovery Auditor")
        user_fixture._grant(auditor, "approvals.case.read")
        ApprovalCaseReadScopeGrant.objects.get_or_create(
            role=auditor.primary_role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
            defaults={"status": ApprovalCaseReadScopeGrant.STATUS_ACTIVE},
        )
        auditor_read = self.client.get(
            f"/api/v1/approval-cases/{case.pk}/", **auth_fixture._auth(auditor)
        )
        self.assertEqual(auditor_read.status_code, 200, auditor_read.content)

    def test_submitted_inputs_change_only_after_explicit_approval_return(self):
        from sfpcl_credit.approvals.models import ApprovalCase
        from sfpcl_credit.defaults.models import NonPaymentNote
        from sfpcl_credit.identity.models import AuditLog

        created, creator_auth = self._create_note()
        self._configure_committee()
        user_fixture = self.fixture.fixture.fixture.fixture.fixture.fixture.owner.fixture.fixture
        user_fixture._grant(self.fixture.actor, "defaults.non_payment_note.submit")
        submit_url = (
            f"/api/v1/non-payment-notes/{created['non_payment_note_id']}"
            "/submit-to-sanction-committee/"
        )
        submitted = self.client.post(
            submit_url,
            data=json.dumps({}),
            content_type="application/json",
            **self.fixture.auth,
        )
        self.assertEqual(submitted.status_code, 200, submitted.content)
        changed_payload = {
            "reason_for_non_payment": "Corrected narrative after committee return.",
            "intentionality_assessment": "unclear",
            "outstanding_principal_amount": "300000.00",
            "outstanding_interest_amount": "45000.00",
            "recommended_recovery_action": "present_to_sanction_committee",
        }
        create_url = f"/api/v1/default-cases/{created['default_case_id']}/non-payment-note/"

        blocked = self.client.post(
            create_url,
            data=json.dumps(changed_payload),
            content_type="application/json",
            **creator_auth,
        )
        self.assertEqual(blocked.status_code, 409, blocked.content)

        case = ApprovalCase.objects.get(pk=submitted.json()["data"]["approval_case_id"])
        cfo = case.sanction_committee.cfo_user
        auth_fixture = self.fixture.fixture.fixture.fixture.fixture.fixture.owner.fixture
        returned = self.client.post(
            f"/api/v1/approval-cases/{case.pk}/return-for-clarification/",
            data=json.dumps(
                {"version": case.version, "comments": "Correct and resubmit the narrative."}
            ),
            content_type="application/json",
            **auth_fixture._auth(cfo),
        )
        self.assertEqual(returned.status_code, 200, returned.content)
        corrected = self.client.post(
            create_url,
            data=json.dumps(changed_payload),
            content_type="application/json",
            **creator_auth,
        )

        self.assertEqual(corrected.status_code, 200, corrected.content)
        note = NonPaymentNote.objects.get(pk=created["non_payment_note_id"])
        self.assertEqual(note.status, "draft")
        self.assertEqual(note.reason_for_non_payment, changed_payload["reason_for_non_payment"])
        self.assertNotEqual(str(note.loan_document_id), created["document_id"])
        self.assertEqual(corrected.json()["data"]["document_id"], str(note.loan_document_id))
        self.assertIsNone(note.approval_case_id)
        self.assertIsNone(note.submitted_to_sanction_committee_at)
        self.assertEqual(AuditLog.objects.filter(action="non_payment_note.returned").count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="non_payment_note.corrected_after_return").count(), 1
        )

    def test_create_replay_converges_and_changed_or_forged_requests_are_zero_write(self):
        from sfpcl_credit.defaults.models import NonPaymentNote
        from sfpcl_credit.identity.models import AuditLog

        created, creator_auth = self._create_note()
        url = f"/api/v1/default-cases/{created['default_case_id']}/non-payment-note/"
        exact = {
            "reason_for_non_payment": created["reason_for_non_payment"],
            "intentionality_assessment": created["intentionality_assessment"],
            "outstanding_principal_amount": created["outstanding_principal_amount"],
            "outstanding_interest_amount": created["outstanding_interest_amount"],
            "recommended_recovery_action": created["recommended_recovery_action"],
        }
        replay = self.client.post(
            url, data=json.dumps(exact), content_type="application/json", **creator_auth
        )
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"]["non_payment_note_id"], created["non_payment_note_id"])

        for payload, expected_status in (
            ({**exact, "reason_for_non_payment": ""}, 400),
            ({**exact, "outstanding_principal_amount": "-1.00"}, 400),
            ({**exact, "outstanding_principal_amount": "NaN"}, 400),
            ({**exact, "outstanding_interest_amount": "44999.00"}, 409),
            ({**exact, "evidence_document_ids": ["00000000-0000-0000-0000-000000000000"]}, 400),
            ({**exact, "reason_for_non_payment": "Changed without return."}, 409),
        ):
            with self.subTest(payload=payload):
                response = self.client.post(
                    url,
                    data=json.dumps(payload),
                    content_type="application/json",
                    **creator_auth,
                )
                self.assertEqual(response.status_code, expected_status, response.content)

        self.assertEqual(NonPaymentNote.objects.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="non_payment_note.created").count(), 1)

    def test_active_extension_and_unauthorised_creator_cannot_create_note(self):
        from sfpcl_credit.defaults.models import NonPaymentNote

        case_id, _ = self.fixture._grant_extension()
        creator, creator_auth = self._creator()
        payload = {
            "reason_for_non_payment": "Premature note.",
            "intentionality_assessment": "unclear",
            "outstanding_principal_amount": f"{self.account.principal_outstanding:.2f}",
            "outstanding_interest_amount": f"{self.account.interest_outstanding:.2f}",
            "recommended_recovery_action": "present_to_sanction_committee",
        }
        url = f"/api/v1/default-cases/{case_id}/non-payment-note/"
        premature = self.client.post(
            url, data=json.dumps(payload), content_type="application/json", **creator_auth
        )
        self.assertEqual(premature.status_code, 409, premature.content)

        auth_fixture = self.fixture.fixture.fixture.fixture.fixture.fixture.owner.fixture
        user_fixture = self.fixture.fixture.fixture.fixture.fixture.fixture.owner.fixture.fixture
        denied = user_fixture._user("field_officer", "Non-Payment Denied")
        user_fixture._grant(denied, "defaults.non_payment_note.create")
        denied_response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            **auth_fixture._auth(denied),
        )
        self.assertEqual(denied_response.status_code, 403, denied_response.content)
        self.assertEqual(NonPaymentNote.objects.count(), 0)
        self.assertNotEqual(creator.pk, denied.pk)

    def test_submit_replay_converges_unauthorised_submit_is_denied_and_inputs_stay_frozen(self):
        from sfpcl_credit.approvals.models import ApprovalCase
        from sfpcl_credit.defaults.models import NonPaymentNote
        from sfpcl_credit.identity.models import AuditLog

        created, _ = self._create_note()
        self._configure_committee()
        submit_url = (
            f"/api/v1/non-payment-notes/{created['non_payment_note_id']}"
            "/submit-to-sanction-committee/"
        )
        denied = self.client.post(
            submit_url,
            data=json.dumps({}),
            content_type="application/json",
            **self.fixture.auth,
        )
        self.assertEqual(denied.status_code, 403, denied.content)
        user_fixture = self.fixture.fixture.fixture.fixture.fixture.fixture.owner.fixture.fixture
        user_fixture._grant(self.fixture.actor, "defaults.non_payment_note.submit")
        first = self.client.post(
            submit_url,
            data=json.dumps({}),
            content_type="application/json",
            **self.fixture.auth,
        )
        replay = self.client.post(
            submit_url,
            data=json.dumps({}),
            content_type="application/json",
            **self.fixture.auth,
        )
        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(first.json()["data"], replay.json()["data"])
        self.assertEqual(
            ApprovalCase.objects.filter(approval_type=ApprovalCase.TYPE_RECOVERY).count(), 1
        )
        self.assertEqual(AuditLog.objects.filter(action="non_payment_note.submitted").count(), 1)
        note = NonPaymentNote.objects.get(pk=created["non_payment_note_id"])
        note.reason_for_non_payment = "Forbidden direct mutation."
        with self.assertRaisesMessage(ValueError, "decision inputs are immutable"):
            note.save()

        detail = self.client.get(
            f"/api/v1/default-cases/{created['default_case_id']}/", **self.fixture.auth
        )
        self.assertEqual(detail.status_code, 200, detail.content)
        self.assertEqual(detail.json()["data"]["available_actions"], [])
        self.assertEqual(
            detail.json()["data"]["non_payment_note"]["non_payment_note_id"],
            created["non_payment_note_id"],
        )
