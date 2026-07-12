from django.test import Client, TestCase

from sfpcl_credit.identity.models import Permission, Role, RolePermission, User
from sfpcl_credit.members.models import Member, MemberScopeAssignment
from sfpcl_credit.tests.api_contracts import assert_error_envelope


class MemberScopeAssignmentApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        permission = Permission.objects.create(
            permission_code="members.member.read", permission_name="Read members",
            module_name="members", risk_level="medium",
        )
        role = Role.objects.create(
            role_code="field_officer_scope", role_name="Field Officer", status="active"
        )
        RolePermission.objects.create(role=role, permission=permission)
        self.actor = User.objects.create(
            full_name="Scoped Officer", email="scoped@example.test", status="active",
            primary_role=role,
        )
        self.actor.set_password("ScopedPass123!")
        self.actor.save()
        other_role = Role.objects.create(
            role_code="other_scope", role_name="Other", status="active"
        )
        self.other = User.objects.create(
            full_name="Other", email="other-scope@example.test", status="active",
            primary_role=other_role,
        )
        self.owned = self._member("OWN", self.actor)
        self.assigned = self._member("ASSIGNED", self.other)
        self.hidden = self._member("HIDDEN", self.other)

    @staticmethod
    def _member(name, owner):
        return Member.objects.create(
            member_type="individual_farmer", legal_name=name, display_name=name,
            folio_number=f"F-{name}", membership_status="active", pan_encrypted=f"enc-{name}",
            pan_hash=f"hash-{name}", kyc_status="verified", default_status="no_default",
            created_by_user=owner,
        )

    def _headers(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": self.actor.email, "password": "ScopedPass123!"},
            content_type="application/json",
        )
        return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}

    def test_permission_is_not_global_and_list_count_follows_scope_before_pagination(self):
        MemberScopeAssignment.objects.create(
            user=self.actor, permission_code="members.member.read",
            scope_type="assigned", member=self.assigned,
        )

        response = self.client.get("/api/v1/members/?page_size=1", headers=self._headers())

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["pagination"]["total_count"], 2)
        visible = {self.owned.member_id, self.assigned.member_id}
        detail_codes = {}
        for member in (self.owned, self.assigned, self.hidden):
            detail = self.client.get(f"/api/v1/members/{member.member_id}/", headers=self._headers())
            detail_codes[member.member_id] = detail.status_code
        self.assertEqual({key for key, value in detail_codes.items() if value == 200}, visible)
        self.assertEqual(detail_codes[self.hidden.member_id], 403)
        assert_error_envelope(self, self.client.get(
            f"/api/v1/members/{self.hidden.member_id}/", headers=self._headers()
        ).json(), "OBJECT_ACCESS_DENIED")
