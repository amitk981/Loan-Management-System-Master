from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal
from unittest import skipUnless

from django.db import close_old_connections, connection
from django.test import Client, RequestFactory, TestCase, TransactionTestCase

from sfpcl_credit.approvals.models import (
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
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.tests.api_contracts import assert_error_envelope, assert_success_envelope


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

    def test_proposal_decision_enforces_authority_version_rejection_and_immutable_evidence(self):
        proposed = self.client.post(
            "/api/v1/approval-matrix-rules/", data=self._payload(reason="Traceable change reason"),
            content_type="application/json", headers=self._headers(self.manager),
        ).json()["data"]
        path = f"/api/v1/approval-configuration-proposals/{proposed['approval_configuration_proposal_id']}"
        before = self._configuration_snapshot()
        for actor, code in (
            (self.manager, "MAKER_CHECKER_VIOLATION"),
            (self.plain, "APPROVER_AUTHORITY_REQUIRED"),
            (self.director_checker, "APPROVER_AUTHORITY_REQUIRED"),
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
        before = self._configuration_snapshot()

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

    def test_configuration_collections_are_bounded_paginated_and_reject_unknown_params(self):
        headers = self._headers(self.reader)
        response = self.client.get("/api/v1/approval-matrix-rules/?page=1&page_size=1", headers=headers)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["page_size"], 1)
        self.assertLessEqual(len(response.json()["data"]), 1)
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

    @staticmethod
    def _configuration_snapshot():
        return {
            "rules": list(ApprovalMatrixRule.objects.order_by("pk").values()),
            "committees": list(SanctionCommittee.objects.order_by("pk").values()),
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
        self.d1 = User.objects.create(full_name="Race Director 1", email="race-d1@example.test", status="active", primary_role=authority_role, approval_authority_type="director")
        self.d2 = User.objects.create(full_name="Race Director 2", email="race-d2@example.test", status="active", primary_role=authority_role, approval_authority_type="director")

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

    def _committee_payload(self, version, effective_from="2026-04-01"):
        return ApprovalMatrixApiTests._committee_payload(
            self.cfo, self.d1, self.d2, version_number=version, effective_from=effective_from
        )

    def _create_committee(self, version):
        close_old_connections()
        try:
            user = User.objects.get(pk=self.user.pk)
            request = RequestFactory().post("/api/v1/sanction-committees/")
            return ("won", approval_matrix_configuration.create_committee(user, request, self._committee_payload(version)))
        except approval_matrix_configuration.ConfigurationConflict:
            return ("lost", None)
        finally:
            close_old_connections()

    def test_competing_committee_creates_have_one_winner_and_zero_write_loser(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(self._create_committee, ("committee-a", "committee-b")))
        self.assertEqual(sorted(result[0] for result in results), ["lost", "won"])
        self.assertEqual(SanctionCommittee.objects.count(), 1)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="sanction_committee").count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="approvals.sanction_committee.created").count(), 1)

    def test_competing_committee_supersedes_have_one_winner_and_zero_write_loser(self):
        original = self._create_committee("original-committee")[1]

        def supersede(version):
            close_old_connections()
            try:
                user = User.objects.get(pk=self.user.pk)
                request = RequestFactory().patch("/api/v1/sanction-committees/x/")
                approval_matrix_configuration.supersede_committee(
                    user, request, original["sanction_committee_id"],
                    self._committee_payload(version, effective_from="2027-01-01"),
                )
                return "won"
            except approval_matrix_configuration.ConfigurationConflict:
                return "lost"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(supersede, ("committee-next-a", "committee-next-b")))
        self.assertEqual(sorted(results), ["lost", "won"])
        self.assertEqual(SanctionCommittee.objects.count(), 2)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="sanction_committee").count(), 2)
        self.assertEqual(AuditLog.objects.filter(action__startswith="approvals.sanction_committee.").count(), 2)
