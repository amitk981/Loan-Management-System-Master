from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from decimal import Decimal
import json
from unittest import skipUnless

from django.db import close_old_connections, connection
from django.test import Client, RequestFactory, TestCase, TransactionTestCase
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import (
    ApprovalCase,
    ApprovalConfigurationLock,
    ApprovalConfigurationProposal,
    ApprovalMatrixRule,
    SanctionCommittee,
)
from sfpcl_credit.approvals.modules.approval_matrix import (
    InvalidApprovalFacts,
    NoEffectiveApprovalRule,
    resolve_approval_matrix,
)
from sfpcl_credit.approvals.modules import approval_matrix_configuration
from sfpcl_credit.approvals.modules.sanction_committee import (
    NoEffectiveSanctionCommittee,
    resolve_sanction_committee,
)
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.credit.models import LoanAppraisalNote, RiskAssessment
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import Member
from sfpcl_credit.tests.api_contracts import assert_error_envelope, assert_success_envelope
from sfpcl_credit.workflows.models import WorkflowEvent


class ApprovalMatrixResolverTests(TestCase):
    def setUp(self):
        ApprovalMatrixRule.objects.all().delete()
        ApprovalConfigurationLock.objects.get_or_create(lock_name="approval_matrix")

    def test_exact_five_lakh_resolves_stored_inclusive_rule_projection(self):
        rule = ApprovalMatrixRule.objects.create(
            decision_type="loan_sanction",
            amount_min=Decimal("0.00"),
            amount_max=Decimal("500000.00"),
            required_approver_roles_json=["cfo", "director"],
            required_director_count=1,
            joint_approval_required_flag=True,
            register_required="credit_sanction_register",
            effective_from=date(2026, 4, 1),
            status="active",
            version_number="1",
        )

        projection = resolve_approval_matrix(
            decision_type="loan_sanction",
            amount=Decimal("500000.00"),
            condition_code=None,
            decision_date=date(2026, 7, 13),
        )

        self.assertEqual(projection.approval_matrix_rule_id, rule.pk)
        self.assertEqual(projection.decision_date, date(2026, 7, 13))
        self.assertEqual(projection.version_number, "1")
        self.assertEqual(projection.required_director_count, 1)
        self.assertEqual(projection.required_approver_roles, ("cfo", "director"))
        self.assertTrue(projection.joint_approval_required)
        self.assertEqual(projection.register_required, "credit_sanction_register")

    def test_condition_and_decision_date_are_authoritative_stored_facts(self):
        current = ApprovalMatrixRule.objects.create(
            decision_type="loan_sanction", amount_min="0", amount_max=None,
            condition_code="exceeds_permissible_limit",
            required_approver_roles_json=["cfo", "director"], required_director_count=2,
            register_required="exception_register", effective_from=date(2026, 4, 1),
            effective_to=date(2026, 12, 31), status="active", version_number="exception-v1",
        )
        ApprovalMatrixRule.objects.create(
            decision_type="loan_sanction", amount_min="0", amount_max=None,
            condition_code="exceeds_permissible_limit",
            required_approver_roles_json=["board"], required_director_count=0,
            register_required="exception_register", effective_from=date(2027, 1, 1),
            status="active", version_number="exception-v2",
        )

        resolved = resolve_approval_matrix(
            decision_type="loan_sanction", amount="1.00",
            condition_code="exceeds_permissible_limit", decision_date=date(2026, 7, 13),
        )

        self.assertEqual(resolved.approval_matrix_rule_id, current.pk)
        self.assertEqual(resolved.register_required, "exception_register")
        with self.assertRaises(NoEffectiveApprovalRule):
            resolve_approval_matrix(
                decision_type="loan_sanction", amount="1.00", condition_code=None,
                decision_date=date(2026, 7, 13),
            )

    def test_non_finite_amount_is_rejected_without_query_authority(self):
        with self.assertRaises(InvalidApprovalFacts):
            resolve_approval_matrix(
                decision_type="loan_sanction", amount="NaN", condition_code=None,
                decision_date=date(2026, 7, 13),
            )

    def test_historical_date_still_resolves_superseded_rule(self):
        historical = ApprovalMatrixRule.objects.create(
            decision_type="loan_sanction", amount_min="0", amount_max="500000",
            required_approver_roles_json=["cfo", "director"], required_director_count=1,
            effective_from=date(2026, 4, 1), effective_to=date(2026, 12, 31),
            status="superseded", version_number="historical-v1",
        )
        ApprovalMatrixRule.objects.create(
            decision_type="loan_sanction", amount_min="0", amount_max="500000",
            required_approver_roles_json=["cfo", "director"], required_director_count=2,
            effective_from=date(2027, 1, 1), status="active", version_number="current-v2",
        )

        projection = resolve_approval_matrix(
            decision_type="loan_sanction", amount="100.00", condition_code=None,
            decision_date=date(2026, 7, 13),
        )

        self.assertEqual(projection.approval_matrix_rule_id, historical.pk)
        self.assertEqual(projection.version_number, "historical-v1")


class SeededApprovalMatrixTests(TestCase):
    def test_source_rules_resolve_below_exact_above_and_exception_routes(self):
        exact = resolve_approval_matrix(
            decision_type="loan_sanction", amount="500000.00", condition_code=None,
            decision_date=date(2026, 4, 1),
        )
        above = resolve_approval_matrix(
            decision_type="loan_sanction", amount="500000.01", condition_code=None,
            decision_date=date(2026, 4, 1),
        )
        exception = resolve_approval_matrix(
            decision_type="loan_sanction", amount="1.00",
            condition_code="exceeds_permissible_limit", decision_date=date(2026, 4, 1),
        )

        self.assertEqual(exact.required_director_count, 1)
        self.assertEqual(above.required_director_count, 2)
        self.assertEqual(exception.required_director_count, 2)
        self.assertEqual(exception.register_required, "exception_register")


class ApprovalMatrixApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        ApprovalMatrixRule.objects.all().delete()
        read = Permission.objects.create(
            permission_code="approvals.matrix.read", permission_name="Read matrix",
            module_name="approvals", risk_level="medium",
        )
        manage = Permission.objects.create(
            permission_code="approvals.matrix.manage", permission_name="Manage matrix",
            module_name="approvals", risk_level="critical",
        )
        manager_role = Role.objects.create(role_code="matrix_manager", role_name="Matrix Manager")
        RolePermission.objects.create(role=manager_role, permission=read)
        RolePermission.objects.create(role=manager_role, permission=manage)
        self.manager = self._user("manager@example.test", manager_role)
        reader_role = Role.objects.create(role_code="matrix_reader", role_name="Matrix Reader")
        RolePermission.objects.create(role=reader_role, permission=read)
        self.reader = self._user("reader@example.test", reader_role)
        plain_role = Role.objects.create(role_code="plain", role_name="Plain")
        self.plain = self._user("plain@example.test", plain_role)
        authority_role = Role.objects.create(role_code="business_checker", role_name="Business Checker")
        self.checker = self._user("checker@example.test", authority_role, "cfo")
        self.inactive_checker = self._user("inactive-checker@example.test", authority_role, "cfo")
        self.inactive_checker.status = "inactive"; self.inactive_checker.save(update_fields=["status"])
        self.director_checker = self._user("director-checker@example.test", authority_role, "director")

    @staticmethod
    def _user(email, role, approval_authority_type=""):
        user = User.objects.create(full_name=email, email=email, status="active", primary_role=role,
                                   approval_authority_type=approval_authority_type)
        user.set_password("Pass123!pass")
        user.save()
        return user

    def _headers(self, user):
        response = self.client.post(
            "/api/v1/auth/login/", data={"email": user.email, "password": "Pass123!pass"},
            content_type="application/json",
        )
        return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}

    @staticmethod
    def _payload(**overrides):
        payload = {
            "decision_type": "loan_sanction", "amount_min": "0.00",
            "amount_max": "500000.00", "condition_code": None,
            "required_approver_roles": ["cfo", "director"], "required_director_count": 1,
            "joint_approval_required_flag": True,
            "register_required": "credit_sanction_register",
            "effective_from": "2026-04-01", "effective_to": None,
            "version_number": "1",
            "reason": "Annual governed configuration update",
        }
        payload.update(overrides)
        return payload

    @staticmethod
    def _committee_payload(cfo, d1, d2, **overrides):
        payload = {
            "committee_name": "FY 2026 Committee", "cfo_user_id": str(cfo.pk),
            "director_1_user_id": str(d1.pk), "director_2_user_id": str(d2.pk),
            "board_meeting_reference": "BOARD-2026-01", "effective_from": "2026-04-01",
            "effective_to": None, "version_number": "1",
            "reason": "Annual governed committee update",
        }
        payload.update(overrides)
        return payload

    def test_auth_and_atomic_create_overlap_contract(self):
        unauthenticated = self.client.get("/api/v1/approval-matrix-rules/")
        self.assertEqual(unauthenticated.status_code, 401)
        forbidden = self.client.post(
            "/api/v1/approval-matrix-rules/", data=self._payload(),
            content_type="application/json", headers=self._headers(self.reader),
        )
        self.assertEqual(forbidden.status_code, 403)

        manager_headers = self._headers(self.manager)
        created = self.client.post(
            "/api/v1/approval-matrix-rules/", data=self._payload(),
            content_type="application/json", headers=manager_headers,
        )
        self.assertEqual(created.status_code, 200, created.content)
        assert_success_envelope(self, created.json())
        self._approve(created.json()["data"])
        before = (ApprovalMatrixRule.objects.count(), VersionHistory.objects.count(), AuditLog.objects.exclude(action__startswith="auth.").count())

        overlap = self.client.post(
            "/api/v1/approval-matrix-rules/",
            data=self._payload(amount_min="500000.00", version_number="2"),
            content_type="application/json", headers=manager_headers,
        )
        self.assertEqual(overlap.status_code, 200, overlap.content)
        denied = self._approve(overlap.json()["data"], expected_status=409)
        assert_error_envelope(self, denied.json(), "CONFIGURATION_CONFLICT")
        self.assertEqual(
            (ApprovalMatrixRule.objects.count(), VersionHistory.objects.count(), AuditLog.objects.exclude(action__startswith="auth.").count()),
            before,
        )

    def test_create_rule_requires_reason_and_stays_pending_until_distinct_business_approval(self):
        headers = self._headers(self.manager)
        payload_without_reason = self._payload(); payload_without_reason.pop("reason")
        missing_reason = self.client.post(
            "/api/v1/approval-matrix-rules/", data=payload_without_reason,
            content_type="application/json", headers=headers,
        )
        self.assertEqual(missing_reason.status_code, 400, missing_reason.content)
        self.assertEqual(ApprovalConfigurationProposal.objects.count(), 0)

        proposed = self.client.post(
            "/api/v1/approval-matrix-rules/",
            data=self._payload(reason="Annual matrix governance update"),
            content_type="application/json", headers=headers,
        )
        self.assertEqual(proposed.status_code, 200, proposed.content)
        self.assertEqual(proposed.json()["data"]["status"], "pending")
        self.assertEqual(ApprovalMatrixRule.objects.count(), 0)
        self.assertEqual(VersionHistory.objects.count(), 0)
        self.assertEqual(AuditLog.objects.exclude(action__startswith="auth.").count(), 0)

    def test_proposal_detail_is_limited_to_participants_eligible_checkers_and_matrix_readers(self):
        proposal = self.client.post(
            "/api/v1/approval-matrix-rules/", data=self._payload(),
            content_type="application/json", headers=self._headers(self.manager),
        ).json()["data"]
        path = (
            "/api/v1/approval-configuration-proposals/"
            f"{proposal['approval_configuration_proposal_id']}/"
        )

        self.assertEqual(self.client.get(path).status_code, 401)
        denied = self.client.get(path, headers=self._headers(self.plain))
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(denied.json()["error"]["code"], "FORBIDDEN")
        for actor in (self.manager, self.checker, self.reader):
            allowed = self.client.get(path, headers=self._headers(actor))
            self.assertEqual(allowed.status_code, 200, allowed.content)
            self.assertEqual(
                allowed.json()["data"]["approval_configuration_proposal_id"],
                proposal["approval_configuration_proposal_id"],
            )

    def test_proposal_decision_enforces_authority_version_rejection_and_immutable_evidence(self):
        proposed = self.client.post(
            "/api/v1/approval-matrix-rules/", data=self._payload(reason="Traceable change reason"),
            content_type="application/json", headers=self._headers(self.manager),
        ).json()["data"]
        path = f"/api/v1/approval-configuration-proposals/{proposed['approval_configuration_proposal_id']}"
        before = self._configuration_snapshot()
        for actor, code in (
            (self.manager, "MAKER_CHECKER_VIOLATION"),
            (self.plain, "APPROVAL_AUTHORITY_REQUIRED"),
            (self.director_checker, "APPROVAL_AUTHORITY_REQUIRED"),
        ):
            denied = self.client.post(f"{path}/approve/", data={"version": 1},
                                      content_type="application/json", headers=self._headers(actor))
            self.assertEqual(denied.status_code, 403)
            self.assertEqual(denied.json()["error"]["code"], code)
        inactive_login = self.client.post(
            "/api/v1/auth/login/", data={"email": self.inactive_checker.email, "password": "Pass123!pass"},
            content_type="application/json",
        )
        self.assertEqual(inactive_login.status_code, 401)
        self.assertEqual(self._configuration_snapshot(), before)

        stale = self.client.post(f"{path}/approve/", data={"version": 2},
                                 content_type="application/json", headers=self._headers(self.checker))
        self.assertEqual(stale.status_code, 409)
        self.assertEqual(stale.json()["error"]["code"], "STALE_VERSION")
        approved = self.client.post(f"{path}/approve/", data={"version": 1},
                                    content_type="application/json", headers=self._headers(self.checker))
        self.assertEqual(approved.status_code, 200, approved.content)
        history = VersionHistory.objects.get()
        self.assertEqual(history.author_user, self.manager)
        self.assertEqual(history.approver_user, self.checker)
        self.assertEqual(history.change_summary, "Traceable change reason")
        audit = AuditLog.objects.get(action="config.changed")
        self.assertEqual(audit.new_value_json["reason"], "Traceable change reason")
        duplicate = self.client.post(f"{path}/approve/", data={"version": 2},
                                     content_type="application/json", headers=self._headers(self.checker))
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(duplicate.json()["error"]["code"], "TRANSITION_CONFLICT")

        rejected_proposal = self.client.post(
            "/api/v1/approval-matrix-rules/",
            data=self._payload(amount_min="600000.00", amount_max="700000.00", version_number="reject-me"),
            content_type="application/json", headers=self._headers(self.manager),
        ).json()["data"]
        reject_path = f"/api/v1/approval-configuration-proposals/{rejected_proposal['approval_configuration_proposal_id']}/reject/"
        missing = self.client.post(reject_path, data={"version": 1}, content_type="application/json",
                                   headers=self._headers(self.checker))
        self.assertEqual(missing.status_code, 400)
        rejected = self.client.post(reject_path, data={"version": 1, "reason": "Policy evidence incomplete"},
                                    content_type="application/json", headers=self._headers(self.checker))
        self.assertEqual(rejected.status_code, 200)
        self.assertEqual(ApprovalMatrixRule.objects.count(), 1)

    def test_patch_supersedes_instead_of_rewriting_history(self):
        proposal = self.client.post(
            "/api/v1/approval-matrix-rules/", data=self._payload(),
            content_type="application/json", headers=self._headers(self.manager),
        ).json()["data"]
        self._approve(proposal)
        created = approval_matrix_configuration.serialize_rule(ApprovalMatrixRule.objects.get())
        response = self.client.patch(
            f"/api/v1/approval-matrix-rules/{created['approval_matrix_rule_id']}/",
            data=self._payload(effective_from="2027-01-01", version_number="2", required_director_count=2),
            content_type="application/json", headers=self._headers(self.manager),
        )
        self.assertEqual(response.status_code, 200, response.content)
        self._approve(response.json()["data"])
        old = ApprovalMatrixRule.objects.get(pk=created["approval_matrix_rule_id"])
        self.assertEqual(old.status, "superseded")
        self.assertEqual(old.effective_to, date(2026, 12, 31))
        self.assertTrue(ApprovalMatrixRule.objects.exclude(pk=old.pk).filter(status="active").exists())

    def test_historical_backfill_cannot_ambiguate_a_superseded_rule(self):
        headers = self._headers(self.manager)
        original_proposal = self.client.post(
            "/api/v1/approval-matrix-rules/",
            data=self._payload(),
            content_type="application/json",
            headers=headers,
        ).json()["data"]
        self._approve(original_proposal)
        original = approval_matrix_configuration.serialize_rule(ApprovalMatrixRule.objects.get())
        supersede = self.client.patch(
            f"/api/v1/approval-matrix-rules/{original['approval_matrix_rule_id']}/",
            data=self._payload(effective_from="2027-01-01", version_number="2"),
            content_type="application/json",
            headers=headers,
        )
        self._approve(supersede.json()["data"])
        response = self.client.post(
            "/api/v1/approval-matrix-rules/",
            data=self._payload(
                effective_from="2026-06-01",
                effective_to="2026-06-30",
                version_number="historical-backfill",
            ),
            content_type="application/json",
            headers=headers,
        )

        self.assertEqual(response.status_code, 200, response.content)
        before = self._configuration_snapshot()
        self._approve(response.json()["data"], expected_status=409)
        self.assertEqual(self._configuration_snapshot(), before)
        resolved = resolve_approval_matrix(
            decision_type="loan_sanction",
            amount="100.00",
            condition_code=None,
            decision_date=date(2026, 6, 15),
        )
        self.assertEqual(str(resolved.approval_matrix_rule_id), original["approval_matrix_rule_id"])

    def test_committee_collection_uses_same_permissions_and_audit_pattern(self):
        cfo_role = Role.objects.create(role_code="cfo_test", role_name="CFO")
        director_role = Role.objects.create(role_code="director_test", role_name="Director")
        cfo = self._user("cfo@example.test", cfo_role, "cfo")
        d1 = self._user("d1@example.test", director_role, "director")
        d2 = self._user("d2@example.test", director_role, "director")
        response = self.client.post(
            "/api/v1/sanction-committees/",
            data={"committee_name": "FY 2026 Committee", "cfo_user_id": str(cfo.pk),
                  "director_1_user_id": str(d1.pk), "director_2_user_id": str(d2.pk),
                  "board_meeting_reference": "BOARD-2026-01", "effective_from": "2026-04-01",
                  "effective_to": None, "version_number": "1", "reason": "Committee update"},
            content_type="application/json", headers=self._headers(self.manager),
        )
        self.assertEqual(response.status_code, 200, response.content)
        self._approve(response.json()["data"])
        self.assertEqual(SanctionCommittee.objects.count(), 1)
        self.assertTrue(AuditLog.objects.filter(action="config.changed").exists())

    def test_committee_requires_persisted_authority_and_resolves_by_decision_date(self):
        role = Role.objects.create(role_code="committee_shape", role_name="CFO / Director")
        ordinary = self._user("ordinary@example.test", role)
        d1 = self._user("authority-d1@example.test", role, "director")
        d2 = self._user("authority-d2@example.test", role, "director")
        before = self._configuration_snapshot()
        denied = self.client.post(
            "/api/v1/sanction-committees/", data=self._committee_payload(ordinary, d1, d2),
            content_type="application/json", headers=self._headers(self.manager),
        )
        self.assertEqual(denied.status_code, 400, denied.content)
        self.assertEqual(self._configuration_snapshot(), before)

        cfo = self._user("authority-cfo@example.test", role, "cfo")
        proposed = self.client.post(
            "/api/v1/sanction-committees/", data=self._committee_payload(cfo, d1, d2),
            content_type="application/json", headers=self._headers(self.manager),
        ).json()["data"]
        self._approve(proposed)
        created = approval_matrix_configuration.serialize_committee(SanctionCommittee.objects.get())
        projection = resolve_sanction_committee(date(2026, 6, 1))
        self.assertEqual(str(projection.sanction_committee_id), created["sanction_committee_id"])
        self.assertEqual(projection.version_number, "1")
        with self.assertRaises(NoEffectiveSanctionCommittee):
            resolve_sanction_committee(date(2025, 1, 1))

    def test_historical_and_current_committees_resolve_independently_by_decision_date(self):
        role = Role.objects.create(role_code="committee_history", role_name="Committee History")
        cfo = self._user("history-cfo@example.test", role, "cfo")
        d1 = self._user("history-d1@example.test", role, "director")
        d2 = self._user("history-d2@example.test", role, "director")
        historical = SanctionCommittee.objects.create(
            committee_name="Historical Committee", cfo_user=cfo, director_1_user=d1,
            director_2_user=d2, board_meeting_reference="BOARD-HISTORY-1",
            effective_from=date(2025, 4, 1), effective_to=date(2026, 3, 31),
            status=SanctionCommittee.STATUS_SUPERSEDED, version_number="history-v1",
        )
        current = SanctionCommittee.objects.create(
            committee_name="Current Committee", cfo_user=cfo, director_1_user=d1,
            director_2_user=d2, board_meeting_reference="BOARD-CURRENT-2",
            effective_from=date(2026, 4, 1), status=SanctionCommittee.STATUS_ACTIVE,
            version_number="current-v2",
        )

        historical_projection = resolve_sanction_committee(date(2026, 3, 31))
        current_projection = resolve_sanction_committee(date(2026, 4, 1))

        self.assertEqual(historical_projection.sanction_committee_id, historical.pk)
        self.assertEqual(historical_projection.version_number, "history-v1")
        self.assertEqual(current_projection.sanction_committee_id, current.pk)
        self.assertEqual(current_projection.version_number, "current-v2")

    def test_conflicting_committee_backfill_keeps_complete_ledger_and_resolver_unchanged(self):
        role = Role.objects.create(role_code="committee_backfill", role_name="Committee Backfill")
        cfo = self._user("backfill-cfo@example.test", role, "cfo")
        d1 = self._user("backfill-d1@example.test", role, "director")
        d2 = self._user("backfill-d2@example.test", role, "director")
        historical = SanctionCommittee.objects.create(
            committee_name="Retained Historical Committee", cfo_user=cfo,
            director_1_user=d1, director_2_user=d2,
            board_meeting_reference="BOARD-RETAINED-1", effective_from=date(2025, 4, 1),
            effective_to=date(2026, 3, 31), status=SanctionCommittee.STATUS_SUPERSEDED,
            version_number="retained-v1",
        )
        proposal = self.client.post(
            "/api/v1/sanction-committees/",
            data=self._committee_payload(
                cfo, d1, d2, committee_name="Conflicting Backfill",
                effective_from="2025-08-01", effective_to="2025-08-31",
                version_number="conflicting-backfill",
            ),
            content_type="application/json", headers=self._headers(self.manager),
        ).json()["data"]
        before = self._configuration_snapshot()

        denied = self._approve(proposal, expected_status=409)

        self.assertEqual(denied.json()["error"]["code"], "CONFIGURATION_CONFLICT")
        self.assertEqual(self._configuration_snapshot(), before)
        projection = resolve_sanction_committee(date(2025, 8, 15))
        self.assertEqual(projection.sanction_committee_id, historical.pk)
        detail = self.client.get(
            f"/api/v1/approval-configuration-proposals/{proposal['approval_configuration_proposal_id']}/",
            headers=self._headers(self.checker),
        )
        self.assertEqual(detail.status_code, 200, detail.content)
        self.assertEqual(detail.json()["data"]["status"], "pending")
        self.assertEqual(detail.json()["data"]["payload"]["version_number"], "conflicting-backfill")

    def test_duplicate_committee_member_is_an_independent_zero_write_public_row(self):
        role = Role.objects.create(role_code="duplicate_committee", role_name="Duplicate Committee")
        cfo = self._user("duplicate-cfo@example.test", role, "cfo")
        director = self._user("duplicate-director@example.test", role, "director")
        before = self._configuration_snapshot()
        denied = self.client.post(
            "/api/v1/sanction-committees/", data=self._committee_payload(cfo, director, director),
            content_type="application/json", headers=self._headers(self.manager),
        )
        self.assertEqual(denied.status_code, 400, denied.content)
        self.assertEqual(self._configuration_snapshot(), before)

    def test_swapped_committee_authority_is_an_independent_zero_write_public_row(self):
        role = Role.objects.create(role_code="swapped_committee", role_name="Swapped Committee")
        cfo = self._user("swapped-cfo@example.test", role, "cfo")
        d1 = self._user("swapped-d1@example.test", role, "director")
        d2 = self._user("swapped-d2@example.test", role, "director")
        before = self._configuration_snapshot()
        denied = self.client.post(
            "/api/v1/sanction-committees/", data=self._committee_payload(d1, cfo, d2),
            content_type="application/json", headers=self._headers(self.manager),
        )
        self.assertEqual(denied.status_code, 400, denied.content)
        self.assertEqual(self._configuration_snapshot(), before)

    def test_configuration_collections_are_bounded_paginated_and_reject_unknown_params(self):
        ApprovalMatrixRule.objects.create(
            decision_type="loan_sanction", amount_min="0.00", amount_max="500000.00",
            required_approver_roles_json=["cfo", "director"], required_director_count=1,
            register_required="credit_sanction_register", effective_from="2026-04-01",
            status=ApprovalMatrixRule.STATUS_ACTIVE, version_number="reader-v1",
        )
        headers = self._headers(self.reader)
        response = self.client.get("/api/v1/approval-matrix-rules/?page=1&page_size=1", headers=headers)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["page_size"], 1)
        self.assertLessEqual(len(response.json()["data"]), 1)
        rule = response.json()["data"][0]
        self.assertEqual(rule["authority_summary"], "CFO + one Director")
        self.assertEqual(rule["minimum_approver_count"], 2)
        unknown = self.client.get("/api/v1/sanction-committees/?all=true", headers=headers)
        self.assertEqual(unknown.status_code, 400, unknown.content)

    def test_read_and_mutation_permission_negatives_cover_both_resources(self):
        for path in ("/api/v1/approval-matrix-rules/", "/api/v1/sanction-committees/"):
            self.assertEqual(self.client.get(path).status_code, 401)
            self.assertEqual(self.client.get(path, headers=self._headers(self.plain)).status_code, 403)
            self.assertEqual(
                self.client.post(path, data={}, content_type="application/json").status_code,
                401,
            )

    def test_invalid_non_finite_create_leaves_complete_configuration_evidence_unchanged(self):
        before = self._configuration_snapshot()
        response = self.client.post(
            "/api/v1/approval-matrix-rules/", data=self._payload(amount_min="NaN"),
            content_type="application/json", headers=self._headers(self.manager),
        )
        after_login = self._configuration_snapshot()
        after_login["audits"] = before["audits"]

        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(after_login, before)

    def test_rule_and_committee_malformed_inputs_are_independent_zero_write_rows(self):
        role = Role.objects.create(role_code="malformed_committee", role_name="Malformed Committee")
        cfo = self._user("malformed-cfo@example.test", role, "cfo")
        d1 = self._user("malformed-d1@example.test", role, "director")
        d2 = self._user("malformed-d2@example.test", role, "director")
        rows = (
            ("/api/v1/approval-matrix-rules/", self._payload(amount_min="Infinity")),
            ("/api/v1/approval-matrix-rules/", self._payload(unknown_rule_fact=True)),
            ("/api/v1/sanction-committees/", self._committee_payload(cfo, d1, d2, cfo_user_id="not-a-uuid")),
            ("/api/v1/sanction-committees/", self._committee_payload(cfo, d1, d2, unknown_committee_fact=True)),
            ("/api/v1/sanction-committees/", self._committee_payload(cfo, d1, d1)),
            ("/api/v1/sanction-committees/", self._committee_payload(d1, cfo, d2)),
        )
        headers = self._headers(self.manager)
        for path, payload in rows:
            with self.subTest(path=path, payload=payload):
                before = self._configuration_snapshot()
                response = self.client.post(
                    path, data=payload, content_type="application/json", headers=headers,
                )
                self.assertEqual(response.status_code, 400, response.content)
                self.assertEqual(self._configuration_snapshot(), before)

    def test_inactive_configuration_never_resolves_and_checker_is_revalidated_at_decision_time(self):
        inactive_rule = ApprovalMatrixRule.objects.create(
            decision_type="inactive_route", amount_min="0", amount_max="10",
            required_approver_roles_json=["cfo"], required_director_count=0,
            effective_from=date(2026, 4, 1), status="inactive", version_number="inactive-rule",
        )
        role = Role.objects.create(role_code="inactive_resolution", role_name="Inactive Resolution")
        cfo = self._user("inactive-resolution-cfo@example.test", role, "cfo")
        d1 = self._user("inactive-resolution-d1@example.test", role, "director")
        d2 = self._user("inactive-resolution-d2@example.test", role, "director")
        SanctionCommittee.objects.create(
            committee_name="Inactive Committee", cfo_user=cfo, director_1_user=d1,
            director_2_user=d2, board_meeting_reference="INACTIVE-BOARD",
            effective_from=date(2026, 4, 1), status="inactive", version_number="inactive-committee",
        )
        with self.assertRaises(NoEffectiveApprovalRule):
            resolve_approval_matrix(
                decision_type=inactive_rule.decision_type, amount="1", condition_code=None,
                decision_date=date(2026, 7, 13),
            )
        with self.assertRaises(NoEffectiveSanctionCommittee):
            resolve_sanction_committee(date(2026, 7, 13))

        proposal = self.client.post(
            "/api/v1/approval-matrix-rules/", data=self._payload(decision_type="fresh_route"),
            content_type="application/json", headers=self._headers(self.manager),
        ).json()["data"]
        self.checker.status = "inactive"
        self.checker.save(update_fields=["status"])
        before = self._configuration_snapshot()
        with self.assertRaises(approval_matrix_configuration.ConfigurationConflict) as denied:
            approval_matrix_configuration.decide_proposal(
                proposal["approval_configuration_proposal_id"], self.checker,
                RequestFactory().post("/proposal/approve/"), {"version": 1}, "approve",
            )
        self.assertEqual(denied.exception.code, "APPROVAL_AUTHORITY_REQUIRED")
        self.assertEqual(self._configuration_snapshot(), before)

    @staticmethod
    def _configuration_snapshot():
        return {
            "proposals": list(ApprovalConfigurationProposal.objects.order_by("pk").values()),
            "rules": list(ApprovalMatrixRule.objects.order_by("pk").values()),
            "committees": list(SanctionCommittee.objects.order_by("pk").values()),
            "cases": list(ApprovalCase.objects.order_by("pk").values()),
            "versions": list(VersionHistory.objects.order_by("pk").values()),
            "audits": list(AuditLog.objects.exclude(action__startswith="auth.").order_by("pk").values()),
        }

    def _approve(self, proposal, expected_status=200):
        response = self.client.post(
            f"/api/v1/approval-configuration-proposals/{proposal['approval_configuration_proposal_id']}/approve/",
            data={"version": proposal["version"]}, content_type="application/json",
            headers=self._headers(self.checker),
        )
        self.assertEqual(response.status_code, expected_status, response.content)
        return response


@skipUnless(connection.vendor == "postgresql", "Authoritative approval-matrix race requires PostgreSQL.")
class ApprovalMatrixConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        ApprovalMatrixRule.objects.all().delete()
        ApprovalConfigurationLock.objects.get_or_create(lock_name="approval_matrix")
        role = Role.objects.create(role_code="race_manager", role_name="Race Manager")
        permission, _ = Permission.objects.get_or_create(
            permission_code="approvals.matrix.manage",
            defaults={"permission_name": "Manage matrix", "module_name": "approvals", "risk_level": "critical"},
        )
        RolePermission.objects.create(role=role, permission=permission)
        self.user = User.objects.create(full_name="Race Manager", email="race@example.test", status="active", primary_role=role)
        self.user.set_password("unused")
        self.user.save()
        authority_role = Role.objects.create(role_code="race_authority", role_name="Race Authority")
        self.cfo = User.objects.create(full_name="Race CFO", email="race-cfo@example.test", status="active", primary_role=authority_role, approval_authority_type="cfo")
        self.company_secretary = User.objects.create(full_name="Race CS", email="race-cs@example.test", status="active", primary_role=authority_role, approval_authority_type="company_secretary")
        self.d1 = User.objects.create(full_name="Race Director 1", email="race-d1@example.test", status="active", primary_role=authority_role, approval_authority_type="director")
        self.d2 = User.objects.create(full_name="Race Director 2", email="race-d2@example.test", status="active", primary_role=authority_role, approval_authority_type="director")
        self.client = Client()
        self.company_secretary.set_password("Pass123!pass")
        self.company_secretary.save()
        login = self.client.post(
            "/api/v1/auth/login/",
            data={"email": self.company_secretary.email, "password": "Pass123!pass"},
            content_type="application/json",
        )
        self.proposal_headers = {
            "Authorization": f"Bearer {login.json()['data']['access_token']}"
        }
        self.open_case = self._create_open_case()
        self._reject_proposal_without_mutating_open_case()

    def _reject_proposal_without_mutating_open_case(self):
        proposal = approval_matrix_configuration.create_rule(
            self.user,
            RequestFactory().post("/api/v1/approval-matrix-rules/"),
            self._payload("rejection-probe") | {
                "decision_type": "rejection_probe",
                "reason": "Reject without touching the open case",
            },
        )
        case_before = ApprovalCase.objects.filter(pk=self.open_case.pk).values().get()
        approval_matrix_configuration.decide_proposal(
            proposal["approval_configuration_proposal_id"], self.company_secretary,
            RequestFactory().post("/proposal/reject/"),
            {"version": 1, "reason": "Governance evidence is incomplete"}, "reject",
        )
        self.assertEqual(
            ApprovalCase.objects.filter(pk=self.open_case.pk).values().get(), case_before
        )

    def _create_open_case(self):
        case_rule = ApprovalMatrixRule.objects.create(
            decision_type="case_snapshot_route", amount_min="123.45", amount_max="678.90",
            required_approver_roles_json=["cfo", "director"], required_director_count=2,
            joint_approval_required_flag=True, register_required="case_snapshot_register",
            effective_from=date(2025, 1, 1), effective_to=date(2025, 12, 31),
            status=ApprovalMatrixRule.STATUS_INACTIVE, version_number="case-rule-v17",
        )
        case_committee = SanctionCommittee.objects.create(
            committee_name="Immutable Case Committee", cfo_user=self.cfo,
            director_1_user=self.d1, director_2_user=self.d2,
            board_meeting_reference="CASE-BOARD-23", effective_from=date(2025, 1, 1),
            effective_to=date(2025, 12, 31), status=SanctionCommittee.STATUS_INACTIVE,
            version_number="case-committee-v23",
        )
        member = Member.objects.create(
            member_number="MEM-APPROVAL-RACE-001", member_type="individual_farmer",
            legal_name="Approval Race Member", display_name="Approval Race Member",
            membership_status="active", folio_number="FOL-APPROVAL-RACE-001",
            kyc_status="verified", default_status="no_default",
        )
        application = LoanApplication.objects.create(
            application_reference_number="LO-APPROVAL-RACE-001", member=member,
            borrower_type=member.member_type, received_by_user=self.user,
            required_loan_amount="400000.00", current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=LoanApplication.STATUS_SUBMITTED_TO_SANCTION,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
        )
        risk = RiskAssessment.objects.create(
            loan_application=application, market_risk_rating="medium",
            operational_risk_rating="low", borrower_risk_rating="low",
            overall_risk_rating="low", assessed_by_user=self.user,
        )
        note = LoanAppraisalNote.objects.create(
            loan_application=application, prepared_by_user=self.user,
            tat_due_at=timezone.now() + timedelta(days=1), tat_status=LoanAppraisalNote.TAT_WITHIN,
            eligibility_assessment_id_snapshot="10000000-0000-0000-0000-000000000001",
            loan_limit_assessment_id_snapshot="20000000-0000-0000-0000-000000000002",
            eligibility_snapshot_json={"overall_result": "eligible", "marker": "case-race"},
            loan_limit_snapshot_json={"final_eligible_loan_amount": "400000.00", "marker": "case-race"},
            borrower_summary="Race borrower", eligibility_summary="Eligible",
            loan_limit_summary="Within limit", recommended_amount="400000.00",
            recommended_security_summary="Stored security", repayment_capacity_notes="Adequate",
            risk_assessment=risk, recommendation="approve",
            appraisal_status=LoanAppraisalNote.STATUS_SUBMITTED_TO_SANCTION,
        )
        workflow = WorkflowEvent.objects.create(
            workflow_name="loan_application", entity_type="loan_application",
            entity_id=application.pk, from_state="credit_reviewed",
            to_state="submitted_to_sanction_committee", triggered_by_user=self.user,
            trigger_reason="Discriminating immutable race fixture",
        )
        return ApprovalCase.objects.create(
            loan_application=application, loan_appraisal_note=note,
            current_status="pending_approval", exception_required_flag=True,
            submission_remarks="Immutable case race marker", submitted_by_user=self.user,
            workflow_event=workflow,
            approval_matrix_rule=case_rule, approval_matrix_rule_version="case-rule-v17",
            sanction_committee=case_committee,
            sanction_committee_version="case-committee-v23",
            required_approvers_json={
                "roles": ["cfo", "director"], "director_count": 2,
                "marker": "complete-case-ledger",
            },
            decision_date=date(2026, 7, 13), version=7,
        )

    @staticmethod
    def _payload(version):
        return ApprovalMatrixApiTests._payload(
            version_number=version,
            reason=f"Governed rule activation {version}",
        )

    def _propose_rule(self, version, *, target_id=None):
        request = RequestFactory().post(
            "/api/v1/approval-matrix-rules/",
            HTTP_X_REQUEST_ID=f"rule-proposal-{version}",
        )
        if target_id is None:
            return approval_matrix_configuration.create_rule(self.user, request, self._payload(version))
        payload = self._payload(version)
        payload["effective_from"] = "2027-01-01"
        return approval_matrix_configuration.supersede_rule(self.user, request, target_id, payload)

    def _decide(self, proposal_id, checker_id):
        close_old_connections()
        try:
            checker = User.objects.get(pk=checker_id)
            request = RequestFactory().post(f"/api/v1/approval-configuration-proposals/{proposal_id}/approve/")
            approval_matrix_configuration.decide_proposal(
                proposal_id, checker, request, {"version": 1}, "approve"
            )
            return "won"
        except approval_matrix_configuration.ConfigurationConflict as exc:
            return exc.code
        finally:
            close_old_connections()

    def _race(self, proposals, *, loser_code="CONFIGURATION_CONFLICT"):
        ledger_before = ApprovalMatrixApiTests._configuration_snapshot()
        target_serialized_before = None
        if proposals[0]["target_entity_id"]:
            target_model = (
                ApprovalMatrixRule
                if proposals[0]["proposal_type"].startswith("rule_")
                else SanctionCommittee
            )
            target = target_model.objects.get(pk=proposals[0]["target_entity_id"])
            target_serialized_before = (
                approval_matrix_configuration.serialize_rule(target)
                if target_model is ApprovalMatrixRule
                else approval_matrix_configuration.serialize_committee(target)
            )
        original = {
            row["approval_configuration_proposal_id"]: ApprovalConfigurationProposal.objects.filter(
                pk=row["approval_configuration_proposal_id"]
            ).values().get()
            for row in proposals
        }
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(
                lambda args: self._decide(*args),
                ((proposals[0]["approval_configuration_proposal_id"], self.cfo.pk),
                 (proposals[1]["approval_configuration_proposal_id"], self.company_secretary.pk)),
            ))
        self.assertEqual(sorted(results), sorted([loser_code, "won"]))
        proposal_ids = [row["approval_configuration_proposal_id"] for row in proposals]
        approved = ApprovalConfigurationProposal.objects.get(
            pk__in=proposal_ids, status="approved"
        )
        loser = ApprovalConfigurationProposal.objects.get(pk__in=proposal_ids, status="pending")
        self.assertEqual(
            ApprovalConfigurationProposal.objects.filter(pk=loser.pk).values().get(),
            original[str(loser.pk)],
        )
        self.assertEqual(approved.version, 2)
        self.assertEqual(
            ApprovalMatrixApiTests._configuration_snapshot()["cases"], ledger_before["cases"]
        )
        ledger_after = ApprovalMatrixApiTests._configuration_snapshot()
        before_proposals = {
            str(row["approval_configuration_proposal_id"]): row
            for row in ledger_before["proposals"]
        }
        after_proposals = {
            str(row["approval_configuration_proposal_id"]): row
            for row in ledger_after["proposals"]
        }
        self.assertEqual(set(after_proposals), set(before_proposals))
        self.assertEqual(after_proposals[str(loser.pk)], before_proposals[str(loser.pk)])
        unchanged_proposal_ids = set(before_proposals) - {str(approved.pk), str(loser.pk)}
        self.assertEqual(
            {key: after_proposals[key] for key in unchanged_proposal_ids},
            {key: before_proposals[key] for key in unchanged_proposal_ids},
        )
        approved_before = before_proposals[str(approved.pk)]
        approved_after = after_proposals[str(approved.pk)]
        for field in set(approved_before) - {
            "status", "version", "decided_by_user_id", "decided_at"
        }:
            self.assertEqual(approved_after[field], approved_before[field], field)
        self.assertEqual(approved_after["status"], "approved")
        self.assertEqual(approved_after["version"], 2)
        self.assertIsNotNone(approved_after["decided_by_user_id"])
        self.assertIsNotNone(approved_after["decided_at"])
        added_evidence = {}
        for key, primary_key in (
            ("versions", "version_history_id"), ("audits", "audit_log_id")
        ):
            before_rows = {str(row[primary_key]): row for row in ledger_before[key]}
            after_rows = {str(row[primary_key]): row for row in ledger_after[key]}
            self.assertEqual(set(before_rows), set(after_rows) & set(before_rows))
            self.assertEqual(
                {row_id: after_rows[row_id] for row_id in before_rows}, before_rows
            )
            new_evidence_ids = set(after_rows) - set(before_rows)
            self.assertEqual(len(new_evidence_ids), 1)
            added_evidence[key] = after_rows[new_evidence_ids.pop()]
        resource_key = "rules" if approved.proposal_type.startswith("rule_") else "committees"
        other_resource_key = "committees" if resource_key == "rules" else "rules"
        self.assertEqual(ledger_after[other_resource_key], ledger_before[other_resource_key])
        expected_resource_growth = 1
        self.assertEqual(
            len(ledger_after[resource_key]),
            len(ledger_before[resource_key]) + expected_resource_growth,
        )
        resource_primary_key = (
            "approval_matrix_rule_id" if resource_key == "rules" else "sanction_committee_id"
        )
        before_resources = {
            str(row[resource_primary_key]): row for row in ledger_before[resource_key]
        }
        after_resources = {
            str(row[resource_primary_key]): row for row in ledger_after[resource_key]
        }
        new_resource_ids = set(after_resources) - set(before_resources)
        self.assertEqual(len(new_resource_ids), 1)
        new_resource_id = new_resource_ids.pop()
        target_before = None
        target_after = None
        if approved.target_entity_id:
            target_id = str(approved.target_entity_id)
            target_before = before_resources[target_id]
            target_after = after_resources[target_id]
            for field in set(target_before) - {"status", "effective_to"}:
                self.assertEqual(target_after[field], target_before[field], field)
            self.assertEqual(target_after["status"], "superseded")
            self.assertEqual(
                target_after["effective_to"],
                date.fromisoformat(approved.payload_json["effective_from"]) - timedelta(days=1),
            )
            unchanged_resource_ids = set(before_resources) - {target_id}
        else:
            unchanged_resource_ids = set(before_resources)
        self.assertEqual(
            {key: after_resources[key] for key in unchanged_resource_ids},
            {key: before_resources[key] for key in unchanged_resource_ids},
        )
        new_resource = (
            ApprovalMatrixRule.objects.get(pk=new_resource_id)
            if resource_key == "rules"
            else SanctionCommittee.objects.get(pk=new_resource_id)
        )
        serialized_resource = (
            approval_matrix_configuration.serialize_rule(new_resource)
            if resource_key == "rules"
            else approval_matrix_configuration.serialize_committee(new_resource)
        )
        self.assertEqual(
            {key: value for key, value in serialized_resource.items() if key not in {
                resource_primary_key, "status"
            }},
            approved.payload_json,
        )
        self.assertEqual(serialized_resource["status"], "active")
        expected_entity_type = (
            "approval_matrix_rule" if resource_key == "rules" else "sanction_committee"
        )
        history = added_evidence["versions"]
        self.assertEqual(history["versioned_entity_type"], expected_entity_type)
        self.assertEqual(str(history["versioned_entity_id"]), new_resource_id)
        self.assertEqual(history["version_number"], approved.payload_json["version_number"])
        self.assertEqual(history["change_summary"], approved.reason)
        self.assertEqual(history["author_user_id"], approved.made_by_user_id)
        self.assertEqual(history["approver_user_id"], approved.decided_by_user_id)
        self.assertNotEqual(history["author_user_id"], history["approver_user_id"])
        self.assertIsNone(history["reviewer_user_id"])
        self.assertIsNone(history["board_approval_reference"])
        self.assertEqual(history["approval_reference"], approved.request_id)
        self.assertEqual(history["approved_at"], approved.decided_at)
        self.assertEqual(history["effective_from"], new_resource.effective_from)
        self.assertEqual(history["effective_to"], new_resource.effective_to)
        self.assertEqual(history["created_at"], history["approved_at"])

        audit = added_evidence["audits"]
        expected_new_value = {
            "configuration": serialized_resource,
            "reason": approved.reason,
            "proposal_id": str(approved.pk),
            "author_user_id": str(approved.made_by_user_id),
            "approver_user_id": str(approved.decided_by_user_id),
            "request_id": approved.request_id,
        }
        if target_after is not None:
            expected_new_value["superseded_configuration"] = (
                approval_matrix_configuration.serialize_rule(new_resource.__class__.objects.get(
                    pk=target_after[resource_primary_key]
                ))
                if resource_key == "rules"
                else approval_matrix_configuration.serialize_committee(new_resource.__class__.objects.get(
                    pk=target_after[resource_primary_key]
                ))
            )
        expected_history_old_value = None
        if target_serialized_before is not None:
            expected_history_old_value = {
                "configuration": target_serialized_before,
                "target_entity_id": str(approved.target_entity_id),
            }
        expected_history_new_value = {
            "proposal_id": str(approved.pk),
            "proposal_type": approved.proposal_type,
            "proposal_payload": approved.payload_json,
            "target_entity_id": (
                str(approved.target_entity_id) if approved.target_entity_id else None
            ),
            "activated_configuration": serialized_resource,
        }
        if target_after is not None:
            expected_history_new_value["superseded_configuration"] = expected_new_value[
                "superseded_configuration"
            ]
        self.assertEqual(history["old_value_json"], expected_history_old_value)
        self.assertEqual(history["new_value_json"], expected_history_new_value)
        self.assertEqual(audit["actor_user_id"], approved.decided_by_user_id)
        self.assertEqual(audit["actor_type"], "user")
        self.assertEqual(audit["action"], "config.changed")
        self.assertEqual(audit["entity_type"], expected_entity_type)
        self.assertEqual(str(audit["entity_id"]), new_resource_id)
        self.assertEqual(audit["old_value_json"], target_serialized_before)
        self.assertEqual(audit["new_value_json"], expected_new_value)
        winner_evidence = json.dumps(
            {"history": history, "audit": audit}, default=str, sort_keys=True
        )
        self.assertNotIn(loser.reason, winner_evidence)
        self.assertNotIn(loser.request_id, winner_evidence)
        self.assertNotIn(loser.payload_json["version_number"], winner_evidence)
        detail = self.client.get(
            f"/api/v1/approval-configuration-proposals/{loser.pk}/",
            headers=self.proposal_headers,
        )
        self.assertEqual(detail.status_code, 200, detail.content)
        public_loser = detail.json()["data"]
        self.assertEqual(public_loser["reason"], loser.reason)
        self.assertEqual(public_loser["made_by_user_id"], str(loser.made_by_user_id))
        self.assertEqual(public_loser["payload"], loser.payload_json)
        self.assertEqual(
            public_loser["target_entity_id"],
            str(loser.target_entity_id) if loser.target_entity_id else None,
        )
        self.assertEqual(public_loser["status"], "pending")
        self.assertEqual(public_loser["version"], 1)
        self.assertIsNone(public_loser["decided_by_user_id"])
        self.assertIsNone(public_loser["decided_at"])
        self.assertIsNone(public_loser["rejection_reason"])
        self.assertEqual(
            [action["enabled"] for action in public_loser["available_actions"]], [True, True]
        )
        if approved.proposal_type.startswith("rule_"):
            resolve_approval_matrix(
                decision_type=approved.payload_json["decision_type"],
                amount=approved.payload_json["amount_min"] or "0.00",
                condition_code=approved.payload_json["condition_code"],
                decision_date=date.fromisoformat(approved.payload_json["effective_from"]),
            )
        else:
            resolve_sanction_committee(
                date.fromisoformat(approved.payload_json["effective_from"])
            )
        self.assertEqual(
            ApprovalCase.objects.filter(pk=self.open_case.pk).values().get(),
            ledger_before["cases"][0],
        )
        return approved, loser

    def test_competing_overlapping_creates_have_one_winner_and_zero_write_loser(self):
        proposals = [self._propose_rule(version) for version in ("race-a", "race-b")]
        self._race(proposals)
        self.assertEqual(ApprovalMatrixRule.objects.exclude(pk=self.open_case.approval_matrix_rule_id).count(), 1)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="approval_matrix_rule").count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="config.changed").count(), 1)

    def test_competing_supersedes_have_one_winner_and_zero_write_loser(self):
        original_proposal = self._propose_rule("original")
        self._decide(original_proposal["approval_configuration_proposal_id"], self.cfo.pk)
        original = ApprovalMatrixRule.objects.exclude(pk=self.open_case.approval_matrix_rule_id).get()
        proposals = [
            self._propose_rule(version, target_id=original.pk)
            for version in ("replacement-a", "replacement-b")
        ]
        self._race(proposals, loser_code="PROPOSAL_STALE")
        self.assertEqual(ApprovalMatrixRule.objects.exclude(pk=self.open_case.approval_matrix_rule_id).count(), 2)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="approval_matrix_rule").count(), 2)
        self.assertEqual(AuditLog.objects.filter(action="config.changed").count(), 2)

    def _committee_payload(self, version, effective_from="2026-04-01"):
        return ApprovalMatrixApiTests._committee_payload(
            self.cfo, self.d1, self.d2, version_number=version,
            effective_from=effective_from,
            reason=f"Governed committee activation {version}",
        )

    def _propose_committee(self, version, *, target_id=None):
        request = RequestFactory().post(
            "/api/v1/sanction-committees/",
            HTTP_X_REQUEST_ID=f"committee-proposal-{version}",
        )
        payload = self._committee_payload(
            version, effective_from="2027-01-01" if target_id else "2026-04-01"
        )
        if target_id is None:
            return approval_matrix_configuration.create_committee(self.user, request, payload)
        return approval_matrix_configuration.supersede_committee(
            self.user, request, target_id, payload
        )

    def test_competing_committee_creates_have_one_winner_and_zero_write_loser(self):
        proposals = [self._propose_committee(version) for version in ("committee-a", "committee-b")]
        self._race(proposals)
        self.assertEqual(SanctionCommittee.objects.exclude(pk=self.open_case.sanction_committee_id).count(), 1)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="sanction_committee").count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="config.changed").count(), 1)

    def test_competing_committee_supersedes_have_one_winner_and_zero_write_loser(self):
        original_proposal = self._propose_committee("original-committee")
        self._decide(original_proposal["approval_configuration_proposal_id"], self.cfo.pk)
        original = SanctionCommittee.objects.exclude(pk=self.open_case.sanction_committee_id).get()
        proposals = [
            self._propose_committee(version, target_id=original.pk)
            for version in ("committee-next-a", "committee-next-b")
        ]
        self._race(proposals, loser_code="PROPOSAL_STALE")
        self.assertEqual(SanctionCommittee.objects.exclude(pk=self.open_case.sanction_committee_id).count(), 2)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="sanction_committee").count(), 2)
        self.assertEqual(AuditLog.objects.filter(action="config.changed").count(), 2)
