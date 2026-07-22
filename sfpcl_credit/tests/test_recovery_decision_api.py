import json
import uuid

from django.test import Client, TestCase
from django.utils import timezone


class RecoveryDecisionApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_non_payment_note_workflow_api import (
            NonPaymentNoteWorkflowApiTests,
        )

        fixture = NonPaymentNoteWorkflowApiTests(
            "test_credit_manager_submission_freezes_note_and_creates_one_committee_case"
        )
        fixture.setUp()
        self.fixture = fixture
        self.client = Client()

    def _submitted_case(self, action="invoke_sh4"):
        from sfpcl_credit.approvals.models import ApprovalCase

        created, creator_auth = self.fixture._create_note(action)
        note_id = created["non_payment_note_id"]
        committee, approvers = self.fixture._configure_committee(action)
        user_fixture = (
            self.fixture.fixture.fixture.fixture.fixture.fixture.fixture.owner.fixture.fixture
        )
        user_fixture._grant(
            self.fixture.fixture.actor, "defaults.non_payment_note.submit"
        )
        submitted = self.client.post(
            f"/api/v1/non-payment-notes/{note_id}/submit-to-sanction-committee/",
            data=json.dumps({}),
            content_type="application/json",
            **self.fixture.fixture.auth,
        )
        self.assertEqual(submitted.status_code, 200, submitted.content)
        case = ApprovalCase.objects.get(
            pk=submitted.json()["data"]["approval_case_id"]
        )
        return created, case, approvers, creator_auth

    def _grant_decider(self, actor):
        user_fixture = (
            self.fixture.fixture.fixture.fixture.fixture.fixture.fixture.owner.fixture.fixture
        )
        user_fixture._grant(actor, "recovery.decision.create")
        auth_fixture = (
            self.fixture.fixture.fixture.fixture.fixture.fixture.fixture.owner.fixture
        )
        return auth_fixture._auth(actor)

    def _force_terminal_approval(self, case, approvers):
        from sfpcl_credit.approvals.models import ApprovalAction, ApprovalCase

        for approver, route in zip(approvers, case.required_approvers_json):
            ApprovalAction.objects.create(
                approval_case=case,
                approver_user=approver,
                approver_role_code=route["role_code"],
                approver_display_name=approver.full_name,
                decision="approved",
                comments="Approved the exact configured recovery action.",
            )
        ApprovalCase.objects.filter(pk=case.pk).update(
            current_status=ApprovalCase.STATUS_APPROVED,
            closed_at=timezone.now(),
        )

    def _decision_payload(self, case, decision="invoke_sh4"):
        return {
            "approval_case_id": str(case.pk),
            "decision": decision,
            "decision_reason": "Approved after reviewing the frozen Non-Payment Note.",
        }

    def test_matching_terminal_approval_creates_one_frozen_decision(self):
        from sfpcl_credit.approvals.models import ApprovalAction, ApprovalCase
        from sfpcl_credit.identity.models import AuditLog

        created, case, approvers, _ = self._submitted_case()
        self._force_terminal_approval(case, approvers)
        actor = approvers[0]
        auth = self._grant_decider(actor)

        response = self.client.post(
            f"/api/v1/default-cases/{created['default_case_id']}/recovery-decision/",
            data=json.dumps(self._decision_payload(case)),
            content_type="application/json",
            **auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["default_case_id"], created["default_case_id"])
        self.assertEqual(data["approval_case_id"], str(case.pk))
        self.assertEqual(data["decision"], "invoke_sh4")
        self.assertEqual(data["status"], "approved")
        self.assertEqual(data["available_actions"], [])
        self.assertEqual(
            AuditLog.objects.filter(action="recovery_decision.created").count(), 1
        )

    def test_existing_approval_owner_requires_every_distinct_recovery_authority(self):
        from sfpcl_credit.approvals.models import ApprovalCase

        _, case, approvers, _ = self._submitted_case()
        user_fixture = (
            self.fixture.fixture.fixture.fixture.fixture.fixture.fixture.owner.fixture.fixture
        )
        auth_fixture = (
            self.fixture.fixture.fixture.fixture.fixture.fixture.fixture.owner.fixture
        )
        for approver in approvers:
            user_fixture._grant(approver, "approvals.case.approve")

        statuses = []
        for approver in approvers:
            case.refresh_from_db()
            response = self.client.post(
                f"/api/v1/approval-cases/{case.pk}/approve/",
                data=json.dumps(
                    {
                        "version": case.version,
                        "comments": "Approved the exact configured SH-4 action.",
                    }
                ),
                content_type="application/json",
                **auth_fixture._auth(approver),
            )
            self.assertEqual(response.status_code, 200, response.content)
            statuses.append(response.json()["data"]["approval_case_status"])

        self.assertEqual(statuses, ["pending", "pending", "approved"])
        case.refresh_from_db()
        self.assertEqual(case.current_status, ApprovalCase.STATUS_APPROVED)
        self.assertEqual(case.actions.filter(decision="approved").count(), 3)

    def test_missing_reason_and_client_forged_status_are_zero_write_validation_errors(self):
        from sfpcl_credit.recovery.models import RecoveryDecision

        created, case, approvers, _ = self._submitted_case()
        auth = self._grant_decider(approvers[0])
        url = f"/api/v1/default-cases/{created['default_case_id']}/recovery-decision/"
        for payload in (
            {
                "approval_case_id": str(case.pk),
                "decision": "invoke_sh4",
                "decision_reason": "",
            },
            {
                **self._decision_payload(case),
                "status": "approved",
            },
        ):
            with self.subTest(payload=payload):
                response = self.client.post(
                    url,
                    data=json.dumps(payload),
                    content_type="application/json",
                    **auth,
                )
                self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(RecoveryDecision.objects.count(), 0)

    def test_pending_rejected_incomplete_stale_and_mismatched_approval_are_blocked(self):
        from sfpcl_credit.approvals.models import ApprovalCase
        from sfpcl_credit.recovery.models import RecoveryDecision

        created, case, approvers, _ = self._submitted_case()
        auth = self._grant_decider(approvers[0])
        url = f"/api/v1/default-cases/{created['default_case_id']}/recovery-decision/"

        pending = self.client.post(
            url,
            data=json.dumps(self._decision_payload(case)),
            content_type="application/json",
            **auth,
        )
        self.assertEqual(pending.status_code, 409, pending.content)

        ApprovalCase.objects.filter(pk=case.pk).update(
            current_status=ApprovalCase.STATUS_REJECTED,
            closed_at=timezone.now(),
        )
        rejected = self.client.post(
            url,
            data=json.dumps(self._decision_payload(case)),
            content_type="application/json",
            **auth,
        )
        self.assertEqual(rejected.status_code, 409, rejected.content)

        ApprovalCase.objects.filter(pk=case.pk).update(
            current_status=ApprovalCase.STATUS_APPROVED,
        )
        incomplete = self.client.post(
            url,
            data=json.dumps(self._decision_payload(case)),
            content_type="application/json",
            **auth,
        )
        self.assertEqual(incomplete.status_code, 409, incomplete.content)

        self._force_terminal_approval(case, approvers)
        mismatch = self.client.post(
            url,
            data=json.dumps(self._decision_payload(case, "invoke_cdsl")),
            content_type="application/json",
            **auth,
        )
        self.assertEqual(mismatch.status_code, 409, mismatch.content)

        case.refresh_from_db()
        case.matrix_projection_json = {
            **case.matrix_projection_json,
            "version_number": "forged-stale-version",
        }
        case.save(update_fields=["matrix_projection_json"])
        stale = self.client.post(
            url,
            data=json.dumps(self._decision_payload(case)),
            content_type="application/json",
            **auth,
        )
        self.assertEqual(stale.status_code, 409, stale.content)

        missing = self.client.post(
            url,
            data=json.dumps(
                {
                    **self._decision_payload(case),
                    "approval_case_id": str(uuid.uuid4()),
                }
            ),
            content_type="application/json",
            **auth,
        )
        self.assertEqual(missing.status_code, 404, missing.content)
        self.assertEqual(RecoveryDecision.objects.count(), 0)

    def test_exact_replay_retains_truth_and_changed_or_second_decision_conflicts(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.recovery.models import RecoveryDecision

        created, case, approvers, _ = self._submitted_case()
        self._force_terminal_approval(case, approvers)
        auth = self._grant_decider(approvers[0])
        url = f"/api/v1/default-cases/{created['default_case_id']}/recovery-decision/"
        payload = self._decision_payload(case)
        first = self.client.post(
            url, data=json.dumps(payload), content_type="application/json", **auth
        )
        replay = self.client.post(
            url, data=json.dumps(payload), content_type="application/json", **auth
        )
        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(first.json()["data"], replay.json()["data"])

        for changed in (
            {**payload, "decision_reason": "Changed retained reason."},
            {**payload, "decision": "invoke_cdsl"},
        ):
            response = self.client.post(
                url,
                data=json.dumps(changed),
                content_type="application/json",
                **auth,
            )
            self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(RecoveryDecision.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="recovery_decision.created").count(), 1
        )
        decision = RecoveryDecision.objects.get()
        decision.decision_reason = "Forbidden direct mutation."
        with self.assertRaisesMessage(ValueError, "evidence is immutable"):
            decision.save()

    def test_approved_continue_follow_up_exposes_no_executable_action(self):
        created, case, approvers, _ = self._submitted_case("continue_follow_up")
        self._force_terminal_approval(case, approvers)
        auth = self._grant_decider(approvers[0])
        response = self.client.post(
            f"/api/v1/default-cases/{created['default_case_id']}/recovery-decision/",
            data=json.dumps(self._decision_payload(case, "continue_follow_up")),
            content_type="application/json",
            **auth,
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"]["available_actions"], [])

    def test_note_maker_in_configured_authority_fails_closed_before_submission(self):
        from sfpcl_credit.approvals.models import ApprovalCase, SanctionCommittee
        from sfpcl_credit.defaults.models import NonPaymentNote
        from sfpcl_credit.identity.models import AuditLog, User

        created, _ = self.fixture._create_note("invoke_sh4")
        committee, _ = self.fixture._configure_committee("invoke_sh4")
        maker = User.objects.get(pk=created["prepared_by_user_id"])
        SanctionCommittee.objects.filter(pk=committee.pk).update(cfo_user=maker)
        user_fixture = (
            self.fixture.fixture.fixture.fixture.fixture.fixture.fixture.owner.fixture.fixture
        )
        user_fixture._grant(
            self.fixture.fixture.actor, "defaults.non_payment_note.submit"
        )

        response = self.client.post(
            f"/api/v1/non-payment-notes/{created['non_payment_note_id']}"
            "/submit-to-sanction-committee/",
            data=json.dumps({}),
            content_type="application/json",
            **self.fixture.fixture.auth,
        )

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(
            ApprovalCase.objects.filter(approval_type=ApprovalCase.TYPE_RECOVERY).count(),
            0,
        )
        self.assertEqual(
            NonPaymentNote.objects.get(pk=created["non_payment_note_id"]).status,
            NonPaymentNote.STATUS_DRAFT,
        )
        self.assertEqual(
            AuditLog.objects.filter(action="non_payment_note.submitted").count(), 0
        )

    def test_terminal_rejection_exposes_no_decision_or_execution(self):
        from sfpcl_credit.approvals.models import ApprovalCase
        from sfpcl_credit.recovery.models import RecoveryDecision

        created, case, approvers, _ = self._submitted_case()
        actor = approvers[0]
        user_fixture = (
            self.fixture.fixture.fixture.fixture.fixture.fixture.fixture.owner.fixture.fixture
        )
        user_fixture._grant(actor, "approvals.case.reject")
        auth_fixture = (
            self.fixture.fixture.fixture.fixture.fixture.fixture.fixture.owner.fixture
        )
        rejected = self.client.post(
            f"/api/v1/approval-cases/{case.pk}/reject/",
            data=json.dumps(
                {"version": case.version, "comments": "Recovery action is not approved."}
            ),
            content_type="application/json",
            **auth_fixture._auth(actor),
        )
        self.assertEqual(rejected.status_code, 200, rejected.content)
        self.assertEqual(
            rejected.json()["data"]["approval_case_status"],
            ApprovalCase.STATUS_REJECTED,
        )
        auth = self._grant_decider(actor)
        blocked = self.client.post(
            f"/api/v1/default-cases/{created['default_case_id']}/recovery-decision/",
            data=json.dumps(self._decision_payload(case)),
            content_type="application/json",
            **auth,
        )
        self.assertEqual(blocked.status_code, 409, blocked.content)
        self.assertEqual(RecoveryDecision.objects.count(), 0)
