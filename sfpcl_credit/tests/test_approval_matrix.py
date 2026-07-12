from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal
from unittest import skipUnless

from django.db import close_old_connections, connection
from django.test import Client, RequestFactory, TestCase, TransactionTestCase

from sfpcl_credit.approvals.models import ApprovalMatrixRule, SanctionCommittee
from sfpcl_credit.approvals.modules.approval_matrix import (
    InvalidApprovalFacts,
    NoEffectiveApprovalRule,
    resolve_approval_matrix,
)
from sfpcl_credit.approvals.modules import approval_matrix_configuration
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.tests.api_contracts import assert_error_envelope, assert_success_envelope


class ApprovalMatrixResolverTests(TestCase):
    def setUp(self):
        ApprovalMatrixRule.objects.all().delete()

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

    @staticmethod
    def _user(email, role):
        user = User.objects.create(full_name=email, email=email, status="active", primary_role=role)
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
        self.assertEqual(created.json()["data"]["required_director_count"], 1)
        before = (ApprovalMatrixRule.objects.count(), VersionHistory.objects.count(), AuditLog.objects.count())

        overlap = self.client.post(
            "/api/v1/approval-matrix-rules/",
            data=self._payload(amount_min="500000.00", version_number="2"),
            content_type="application/json", headers=manager_headers,
        )
        self.assertEqual(overlap.status_code, 409, overlap.content)
        assert_error_envelope(self, overlap.json(), "CONFIGURATION_CONFLICT")
        self.assertEqual(
            (ApprovalMatrixRule.objects.count(), VersionHistory.objects.count(), AuditLog.objects.count()),
            before,
        )

    def test_patch_supersedes_instead_of_rewriting_history(self):
        created = self.client.post(
            "/api/v1/approval-matrix-rules/", data=self._payload(),
            content_type="application/json", headers=self._headers(self.manager),
        ).json()["data"]
        response = self.client.patch(
            f"/api/v1/approval-matrix-rules/{created['approval_matrix_rule_id']}/",
            data=self._payload(effective_from="2027-01-01", version_number="2", required_director_count=2),
            content_type="application/json", headers=self._headers(self.manager),
        )
        self.assertEqual(response.status_code, 200, response.content)
        old = ApprovalMatrixRule.objects.get(pk=created["approval_matrix_rule_id"])
        self.assertEqual(old.status, "superseded")
        self.assertEqual(old.effective_to, date(2026, 12, 31))
        self.assertNotEqual(response.json()["data"]["approval_matrix_rule_id"], str(old.pk))

    def test_committee_collection_uses_same_permissions_and_audit_pattern(self):
        cfo_role = Role.objects.create(role_code="cfo_test", role_name="CFO")
        director_role = Role.objects.create(role_code="director_test", role_name="Director")
        cfo = self._user("cfo@example.test", cfo_role)
        d1 = self._user("d1@example.test", director_role)
        d2 = self._user("d2@example.test", director_role)
        response = self.client.post(
            "/api/v1/sanction-committees/",
            data={"committee_name": "FY 2026 Committee", "cfo_user_id": str(cfo.pk),
                  "director_1_user_id": str(d1.pk), "director_2_user_id": str(d2.pk),
                  "board_meeting_reference": "BOARD-2026-01", "effective_from": "2026-04-01",
                  "effective_to": None, "version_number": "1"},
            content_type="application/json", headers=self._headers(self.manager),
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(SanctionCommittee.objects.count(), 1)
        self.assertTrue(AuditLog.objects.filter(action="approvals.sanction_committee.created").exists())

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

    @staticmethod
    def _configuration_snapshot():
        return {
            "rules": list(ApprovalMatrixRule.objects.order_by("pk").values()),
            "committees": list(SanctionCommittee.objects.order_by("pk").values()),
            "versions": list(VersionHistory.objects.order_by("pk").values()),
            "audits": list(AuditLog.objects.exclude(action__startswith="auth.").order_by("pk").values()),
        }


@skipUnless(connection.vendor == "postgresql", "Authoritative approval-matrix race requires PostgreSQL.")
class ApprovalMatrixConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        ApprovalMatrixRule.objects.all().delete()
        role = Role.objects.create(role_code="race_manager", role_name="Race Manager")
        permission = Permission.objects.get(permission_code="approvals.matrix.manage")
        RolePermission.objects.create(role=role, permission=permission)
        self.user = User.objects.create(full_name="Race Manager", email="race@example.test", status="active", primary_role=role)
        self.user.set_password("unused")
        self.user.save()

    @staticmethod
    def _payload(version):
        return ApprovalMatrixApiTests._payload(version_number=version)

    def _create(self, version):
        close_old_connections()
        try:
            user = User.objects.get(pk=self.user.pk)
            request = RequestFactory().post("/api/v1/approval-matrix-rules/")
            return ("won", approval_matrix_configuration.create_rule(user, request, self._payload(version)))
        except approval_matrix_configuration.ConfigurationConflict:
            return ("lost", None)
        finally:
            close_old_connections()

    def test_competing_overlapping_creates_have_one_winner_and_zero_write_loser(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(self._create, ("race-a", "race-b")))

        self.assertEqual(sorted(result[0] for result in results), ["lost", "won"])
        self.assertEqual(ApprovalMatrixRule.objects.count(), 1)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="approval_matrix_rule").count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="approvals.matrix_rule.created").count(), 1)

    def test_competing_supersedes_have_one_winner_and_zero_write_loser(self):
        original = self._create("original")[1]

        def supersede(version):
            close_old_connections()
            try:
                user = User.objects.get(pk=self.user.pk)
                request = RequestFactory().patch("/api/v1/approval-matrix-rules/x/")
                payload = self._payload(version)
                payload["effective_from"] = "2027-01-01"
                approval_matrix_configuration.supersede_rule(
                    user, request, original["approval_matrix_rule_id"], payload
                )
                return "won"
            except approval_matrix_configuration.ConfigurationConflict:
                return "lost"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(supersede, ("replacement-a", "replacement-b")))

        self.assertEqual(sorted(results), ["lost", "won"])
        self.assertEqual(ApprovalMatrixRule.objects.count(), 2)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="approval_matrix_rule").count(), 2)
        self.assertEqual(AuditLog.objects.filter(action__startswith="approvals.matrix_rule.").count(), 2)
