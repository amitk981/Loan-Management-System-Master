from django.test import Client
from django.utils import timezone

from sfpcl_credit.identity.models import (
    AuditLog,
    Permission,
    Role,
    RolePermission,
    Team,
    User,
    UserSession,
    UserTeamMembership,
)
from sfpcl_credit.tests.base import IdentityTestCase


class AdminUsersApiTests(IdentityTestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()
        self.system_admin_role = Role.objects.create(
            role_code="system_admin",
            role_name="System Administrator",
            is_system_role=True,
            status="active",
        )
        self.accounts_role = Role.objects.create(
            role_code="accounts_head",
            role_name="Accounts Head",
            is_system_role=True,
            status="active",
        )
        for code in ["users.user.create", "users.user.update", "users.user.disable"]:
            permission = Permission.objects.create(
                permission_code=code,
                permission_name=code,
                module_name="users",
                risk_level="high",
            )
            RolePermission.objects.create(role=self.system_admin_role, permission=permission)
        self.admin = User.objects.create(
            full_name="System Admin",
            email="system.admin@sfpcl.example",
            mobile_number="+919999999999",
            status="active",
            primary_role=self.system_admin_role,
        )
        self.admin.set_password("AdminPass123!")
        self.admin.save()
        self.target = User.objects.create(
            full_name="Target User",
            email="target.user@sfpcl.example",
            mobile_number="+918888888888",
            status="active",
            primary_role=self.role,
        )
        self.target.set_password("TargetPass123!")
        self.target.save()
        self.team = Team.objects.create(
            team_code="credit_assessment",
            team_name="Credit Assessment",
            status="active",
        )

    def _access_token(self, email="system.admin@sfpcl.example", password="AdminPass123!"):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": email, "password": password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["access_token"]

    def _auth_headers(self):
        return {"Authorization": f"Bearer {self._access_token()}"}

    def _partial_admin_headers(self, role_code, permission_codes):
        """Create an active user whose primary role holds exactly permission_codes."""
        role = Role.objects.create(
            role_code=role_code,
            role_name=role_code.replace("_", " ").title(),
            is_system_role=True,
            status="active",
        )
        for code in permission_codes:
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "users",
                    "risk_level": "high",
                },
            )
            RolePermission.objects.create(role=role, permission=permission)
        email = f"{role_code}@sfpcl.example"
        user = User.objects.create(
            full_name=role_code.replace("_", " ").title(),
            email=email,
            mobile_number="+917000000000",
            status="active",
            primary_role=role,
        )
        user.set_password("PartialPass123!")
        user.save()
        token = self._access_token(email, "PartialPass123!")
        return {"Authorization": f"Bearer {token}"}

    def test_admin_user_list_requires_session_and_manage_users_permission(self):
        unauthenticated = self.client.get("/api/v1/admin/users/")
        self.assertEqual(unauthenticated.status_code, 401)
        self.assertEqual(unauthenticated.json()["error"]["code"], "AUTH_REQUIRED")

        no_permission_token = self._access_token(
            "credit.manager@sfpcl.example", "CorrectHorse123!"
        )
        forbidden = self.client.get(
            "/api/v1/admin/users/",
            headers={"Authorization": f"Bearer {no_permission_token}"},
        )

        self.assertEqual(forbidden.status_code, 403)
        self.assertEqual(forbidden.json()["error"]["code"], "PERMISSION_DENIED")

    def test_admin_user_list_and_detail_return_auth_me_role_team_shape_with_pagination(self):
        UserTeamMembership.objects.create(user=self.target, team=self.team, status="active")

        list_response = self.client.get(
            "/api/v1/admin/users/?page=1&page_size=20",
            headers={**self._auth_headers(), "X-Request-ID": "req-admin-users"},
        )

        self.assertEqual(list_response.status_code, 200)
        list_payload = list_response.json()
        self.assertEqual(list_payload["success"], True)
        self.assertEqual(list_payload["meta"]["request_id"], "req-admin-users")
        self.assertEqual(list_payload["pagination"]["page"], 1)
        self.assertEqual(list_payload["pagination"]["page_size"], 20)
        self.assertGreaterEqual(list_payload["pagination"]["total_count"], 2)
        target_item = next(
            item
            for item in list_payload["data"]
            if item["user_id"] == str(self.target.user_id)
        )
        self.assertEqual(target_item["full_name"], "Target User")
        self.assertEqual(target_item["mobile_number"], "+918888888888")
        self.assertEqual(
            target_item["roles"],
            [{"role_code": "credit_manager", "role_name": "Credit Manager"}],
        )
        self.assertEqual(
            target_item["teams"],
            [{"team_code": "credit_assessment", "team_name": "Credit Assessment"}],
        )

        detail_response = self.client.get(
            f"/api/v1/admin/users/{self.target.user_id}/",
            headers=self._auth_headers(),
        )

        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["data"], target_item)

    def test_admin_can_assign_existing_role_add_and_remove_team_and_audit_changes(self):
        role_response = self.client.post(
            f"/api/v1/admin/users/{self.target.user_id}/roles/",
            data={"role_code": "accounts_head"},
            content_type="application/json",
            headers=self._auth_headers(),
        )

        self.assertEqual(role_response.status_code, 200)
        self.target.refresh_from_db()
        self.assertEqual(self.target.primary_role.role_code, "accounts_head")
        self.assertEqual(role_response.json()["data"]["roles"][0]["role_code"], "accounts_head")
        role_audit = AuditLog.objects.get(action="admin.user.role_assigned")
        self.assertEqual(role_audit.actor_user, self.admin)
        self.assertEqual(role_audit.entity_id, self.target.user_id)
        self.assertEqual(role_audit.old_value_json["role_code"], "credit_manager")
        self.assertEqual(role_audit.new_value_json["role_code"], "accounts_head")

        add_team = self.client.post(
            f"/api/v1/admin/users/{self.target.user_id}/teams/",
            data={"team_code": "credit_assessment"},
            content_type="application/json",
            headers=self._auth_headers(),
        )
        self.assertEqual(add_team.status_code, 200)
        self.assertEqual(
            add_team.json()["data"]["teams"],
            [{"team_code": "credit_assessment", "team_name": "Credit Assessment"}],
        )
        self.assertEqual(
            AuditLog.objects.filter(action="admin.user.team_added").count(), 1
        )

        remove_team = self.client.delete(
            f"/api/v1/admin/users/{self.target.user_id}/teams/credit_assessment/",
            headers=self._auth_headers(),
        )
        self.assertEqual(remove_team.status_code, 200)
        self.assertEqual(remove_team.json()["data"]["teams"], [])
        self.assertEqual(
            AuditLog.objects.filter(action="admin.user.team_removed").count(), 1
        )

    def test_status_change_to_suspended_revokes_target_sessions_and_audits(self):
        session = UserSession.objects.create(
            user=self.target,
            refresh_token_hash="unused",
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )

        response = self.client.patch(
            f"/api/v1/admin/users/{self.target.user_id}/status/",
            data={"status": "suspended"},
            content_type="application/json",
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 200)
        self.target.refresh_from_db()
        session.refresh_from_db()
        self.assertEqual(self.target.status, "suspended")
        self.assertEqual(session.session_status, "revoked")
        self.assertEqual(session.revoked_reason, "admin_status_suspended")
        audit = AuditLog.objects.get(action="admin.user.status_changed")
        self.assertEqual(audit.old_value_json["status"], "active")
        self.assertEqual(audit.new_value_json["status"], "suspended")

    def test_unknown_catalogue_values_and_last_system_admin_lockout_return_validation_errors(self):
        unknown_role = self.client.post(
            f"/api/v1/admin/users/{self.target.user_id}/roles/",
            data={"role_code": "missing_role"},
            content_type="application/json",
            headers=self._auth_headers(),
        )
        self.assertEqual(unknown_role.status_code, 400)
        self.assertEqual(unknown_role.json()["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("role_code", unknown_role.json()["error"]["field_errors"])

        lockout = self.client.patch(
            f"/api/v1/admin/users/{self.admin.user_id}/status/",
            data={"status": "suspended"},
            content_type="application/json",
            headers=self._auth_headers(),
        )

        self.assertEqual(lockout.status_code, 400)
        self.assertEqual(lockout.json()["error"]["code"], "VALIDATION_ERROR")
        self.assertIn("status", lockout.json()["error"]["field_errors"])
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.status, "active")

    def _assert_no_write_side_effects(self):
        self.target.refresh_from_db()
        self.assertEqual(self.target.primary_role.role_code, "credit_manager")
        self.assertEqual(self.target.status, "active")
        # No admin user-management mutation was audited (auth login events may exist).
        self.assertEqual(
            AuditLog.objects.filter(action__startswith="admin.user.").count(), 0
        )

    def test_create_only_role_cannot_assign_roles_teams_or_suspend(self):
        headers = self._partial_admin_headers(
            "user_creator", ["users.user.create"]
        )
        session = UserSession.objects.create(
            user=self.target,
            refresh_token_hash="unused",
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )

        assign = self.client.post(
            f"/api/v1/admin/users/{self.target.user_id}/roles/",
            data={"role_code": "accounts_head"},
            content_type="application/json",
            headers=headers,
        )
        self.assertEqual(assign.status_code, 403)
        self.assertEqual(assign.json()["error"]["code"], "PERMISSION_DENIED")

        add_team = self.client.post(
            f"/api/v1/admin/users/{self.target.user_id}/teams/",
            data={"team_code": "credit_assessment"},
            content_type="application/json",
            headers=headers,
        )
        self.assertEqual(add_team.status_code, 403)

        remove_team = self.client.delete(
            f"/api/v1/admin/users/{self.target.user_id}/teams/credit_assessment/",
            headers=headers,
        )
        self.assertEqual(remove_team.status_code, 403)

        suspend = self.client.patch(
            f"/api/v1/admin/users/{self.target.user_id}/status/",
            data={"status": "suspended"},
            content_type="application/json",
            headers=headers,
        )
        self.assertEqual(suspend.status_code, 403)
        self.assertEqual(suspend.json()["error"]["code"], "PERMISSION_DENIED")

        # A create-only user still holds a user-admin permission, so read is allowed.
        listed = self.client.get("/api/v1/admin/users/", headers=headers)
        self.assertEqual(listed.status_code, 200)

        session.refresh_from_db()
        self.assertEqual(session.session_status, UserSession.ACTIVE)
        self._assert_no_write_side_effects()

    def test_update_only_role_can_assign_but_cannot_suspend(self):
        headers = self._partial_admin_headers(
            "user_updater", ["users.user.update"]
        )
        session = UserSession.objects.create(
            user=self.target,
            refresh_token_hash="unused",
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )

        assign = self.client.post(
            f"/api/v1/admin/users/{self.target.user_id}/roles/",
            data={"role_code": "accounts_head"},
            content_type="application/json",
            headers=headers,
        )
        self.assertEqual(assign.status_code, 200)
        self.target.refresh_from_db()
        self.assertEqual(self.target.primary_role.role_code, "accounts_head")

        add_team = self.client.post(
            f"/api/v1/admin/users/{self.target.user_id}/teams/",
            data={"team_code": "credit_assessment"},
            content_type="application/json",
            headers=headers,
        )
        self.assertEqual(add_team.status_code, 200)

        # Restoring status to active is an update, so it is permitted.
        restore = self.client.patch(
            f"/api/v1/admin/users/{self.target.user_id}/status/",
            data={"status": "active"},
            content_type="application/json",
            headers=headers,
        )
        self.assertEqual(restore.status_code, 200)

        # Suspending requires users.user.disable, which this role lacks.
        suspend = self.client.patch(
            f"/api/v1/admin/users/{self.target.user_id}/status/",
            data={"status": "suspended"},
            content_type="application/json",
            headers=headers,
        )
        self.assertEqual(suspend.status_code, 403)
        self.assertEqual(suspend.json()["error"]["code"], "PERMISSION_DENIED")

        # The forbidden suspend left the target active and its session intact; only the
        # earlier legitimate restore-to-active wrote a status_changed audit.
        self.target.refresh_from_db()
        self.assertEqual(self.target.status, "active")
        session.refresh_from_db()
        self.assertEqual(session.session_status, UserSession.ACTIVE)
        status_audits = list(
            AuditLog.objects.filter(action="admin.user.status_changed")
        )
        self.assertTrue(
            all(audit.new_value_json["status"] != "suspended" for audit in status_audits)
        )

    def test_disable_only_role_can_suspend_but_cannot_assign(self):
        headers = self._partial_admin_headers(
            "user_disabler", ["users.user.disable"]
        )

        assign = self.client.post(
            f"/api/v1/admin/users/{self.target.user_id}/roles/",
            data={"role_code": "accounts_head"},
            content_type="application/json",
            headers=headers,
        )
        self.assertEqual(assign.status_code, 403)
        self.assertEqual(assign.json()["error"]["code"], "PERMISSION_DENIED")

        add_team = self.client.post(
            f"/api/v1/admin/users/{self.target.user_id}/teams/",
            data={"team_code": "credit_assessment"},
            content_type="application/json",
            headers=headers,
        )
        self.assertEqual(add_team.status_code, 403)

        self.target.refresh_from_db()
        self.assertEqual(self.target.primary_role.role_code, "credit_manager")
        self.assertFalse(
            AuditLog.objects.filter(action="admin.user.role_assigned").exists()
        )
        self.assertFalse(
            AuditLog.objects.filter(action="admin.user.team_added").exists()
        )

        # Suspending is exactly what users.user.disable authorises.
        session = UserSession.objects.create(
            user=self.target,
            refresh_token_hash="unused",
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )
        suspend = self.client.patch(
            f"/api/v1/admin/users/{self.target.user_id}/status/",
            data={"status": "suspended"},
            content_type="application/json",
            headers=headers,
        )
        self.assertEqual(suspend.status_code, 200)
        self.target.refresh_from_db()
        session.refresh_from_db()
        self.assertEqual(self.target.status, "suspended")
        self.assertEqual(session.session_status, "revoked")

    def test_read_only_user_admin_can_list_but_cannot_write(self):
        headers = self._partial_admin_headers(
            "user_reader", ["users.user.read"]
        )

        listed = self.client.get("/api/v1/admin/users/", headers=headers)
        self.assertEqual(listed.status_code, 200)

        detail = self.client.get(
            f"/api/v1/admin/users/{self.target.user_id}/", headers=headers
        )
        self.assertEqual(detail.status_code, 200)

        assign = self.client.post(
            f"/api/v1/admin/users/{self.target.user_id}/roles/",
            data={"role_code": "accounts_head"},
            content_type="application/json",
            headers=headers,
        )
        self.assertEqual(assign.status_code, 403)
        self.assertEqual(assign.json()["error"]["code"], "PERMISSION_DENIED")
        self._assert_no_write_side_effects()
