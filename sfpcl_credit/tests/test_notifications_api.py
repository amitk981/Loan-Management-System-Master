import uuid
from unittest import mock

from django.test import Client, TestCase
from django.utils import timezone

from sfpcl_credit.communications import services
from sfpcl_credit.communications.models import ContentTemplate, Notification
from sfpcl_credit.identity.models import (
    AuditLog,
    Permission,
    Role,
    RolePermission,
    Team,
    User,
    UserTeamMembership,
)
from sfpcl_credit.tests.api_contracts import (
    assert_error_envelope,
    assert_pagination_shape,
    assert_success_envelope,
)


NOTIFICATIONS_URL = "/api/v1/notifications/"
NOTIFICATION_READ_PERMISSION = "communications.notification.read"
COMMUNICATION_SEND_PERMISSION = "communications.communication.send"


class NotificationApiTests(TestCase):
    """003IA: current-user notification inbox with persistent read state."""

    def setUp(self):
        self.client = Client()
        self.role = self._role("credit_manager", "Credit Manager")
        self.other_role = self._role("accounts_head", "Accounts Head")
        self.team = self._team("credit_assessment", "Credit Assessment Team")
        self.other_team = self._team("accounts", "Accounts Team")
        notification_permission = Permission.objects.create(
            permission_code=NOTIFICATION_READ_PERMISSION,
            permission_name="Read own notifications",
            module_name="communications",
            risk_level="medium",
        )
        send_permission = Permission.objects.create(
            permission_code=COMMUNICATION_SEND_PERMISSION,
            permission_name="Send communication snapshots",
            module_name="communications",
            risk_level="medium",
        )
        RolePermission.objects.create(role=self.role, permission=notification_permission)
        RolePermission.objects.create(role=self.role, permission=send_permission)
        RolePermission.objects.create(
            role=self.other_role, permission=notification_permission
        )
        self.user = self._user(
            "Credit Manager", "credit.manager@sfpcl.example", self.role, "CreditPass123!"
        )
        UserTeamMembership.objects.create(user=self.user, team=self.team)
        self.other_user = self._user(
            "Accounts Head", "accounts.head@sfpcl.example", self.other_role, "AccountsPass123!"
        )
        UserTeamMembership.objects.create(user=self.other_user, team=self.other_team)
        self.plain_role = self._role("plain_staff", "Plain Staff")
        self.plain_user = self._user(
            "Plain Staff", "plain.staff@sfpcl.example", self.plain_role, "PlainPass123!"
        )
        self.related_entity_id = uuid.uuid4()
        self.template = ContentTemplate.objects.create(
            template_code="internal_review_notice_v1",
            template_name="Internal Review Notice",
            template_type="in_app",
            language_code="en",
            audience="staff",
            subject_template="Review {{application_reference_number}}",
            body_template="{{application_reference_number}} requires credit review.",
            variables_json=["application_reference_number"],
            approval_status=ContentTemplate.STATUS_APPROVED,
            template_version="1.0",
            effective_from="2026-01-01",
            effective_to="2026-12-31",
        )

    def _role(self, code, name):
        return Role.objects.create(
            role_code=code, role_name=name, is_system_role=True, status="active"
        )

    def _team(self, code, name):
        return Team.objects.create(team_code=code, team_name=name, status="active")

    def _user(self, name, email, role, password):
        user = User.objects.create(
            full_name=name, email=email, status="active", primary_role=role
        )
        user.set_password(password)
        user.save()
        return user

    def _access_token(self, email="credit.manager@sfpcl.example", password="CreditPass123!"):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": email, "password": password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["access_token"]

    def _auth_headers(self, **kwargs):
        return {"Authorization": f"Bearer {self._access_token(**kwargs)}"}

    def _plain_headers(self):
        return self._auth_headers(email="plain.staff@sfpcl.example", password="PlainPass123!")

    def _create_notification(self, **overrides):
        communication = overrides.pop("communication", None)
        defaults = {
            "notification_type": "application",
            "category": "Application",
            "severity": Notification.SEVERITY_WARNING,
            "title": "Review LA-2026-0001",
            "message": "LA-2026-0001 requires credit review.",
            "related_entity_type": "loan_application",
            "related_entity_id": self.related_entity_id,
            "action_label": "Open related record",
            "action_url": "/applications/detail",
            "recipient_user": self.user,
            "recipient_role_code": "",
            "recipient_team_code": "",
            "sender_user": self.other_user,
            "communication": communication,
        }
        defaults.update(overrides)
        return Notification.objects.create(**defaults)

    def test_current_user_lists_only_direct_role_and_team_notifications(self):
        direct = self._create_notification(title="Direct notice", recipient_user=self.user)
        role_notice = self._create_notification(
            title="Role notice",
            recipient_user=None,
            recipient_role_code="credit_manager",
        )
        team_notice = self._create_notification(
            title="Team notice",
            recipient_user=None,
            recipient_team_code="credit_assessment",
        )
        self._create_notification(title="Other user", recipient_user=self.other_user)
        self._create_notification(title="Other role", recipient_user=None, recipient_role_code="accounts_head")
        self._create_notification(title="Other team", recipient_user=None, recipient_team_code="accounts")

        response = self.client.get(
            NOTIFICATIONS_URL,
            headers={**self._auth_headers(), "X-Request-ID": "req-notification-list"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_pagination_shape(self, payload)
        self.assertEqual(payload["meta"]["request_id"], "req-notification-list")
        returned_ids = {row["notification_id"] for row in payload["data"]}
        self.assertEqual(returned_ids, {str(direct.notification_id), str(role_notice.notification_id), str(team_notice.notification_id)})
        self.assertEqual(payload["pagination"]["total_count"], 3)
        for row in payload["data"]:
            self.assertIn("read", row)
            self.assertIn("read_state_version", row)
            self.assertIn(row["severity"], ["info", "warning", "urgent"])
            self.assertNotIn("body_snapshot", row)
            self.assertNotIn("recipient_address", row)

    def test_send_communication_creates_staff_notification_for_user_recipient(self):
        response = self.client.post(
            "/api/v1/communications/send/",
            data={
                "related_entity_type": "loan_application",
                "related_entity_id": str(self.related_entity_id),
                "recipient_party_type": "user",
                "recipient_party_id": str(self.user.user_id),
                "recipient_address": "credit.manager@sfpcl.example",
                "channel": "email",
                "content_template_id": str(self.template.content_template_id),
                "merge_data": {"application_reference_number": "LA-2026-0001"},
            },
            content_type="application/json",
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 200)
        communication_id = response.json()["data"]["communication_id"]
        notification = Notification.objects.get(communication_id=communication_id)
        self.assertEqual(notification.recipient_user, self.user)
        self.assertEqual(notification.title, "Review LA-2026-0001")
        self.assertEqual(notification.message, "LA-2026-0001 requires credit review.")
        self.assertEqual(notification.related_entity_id, self.related_entity_id)

        list_response = self.client.get(NOTIFICATIONS_URL, headers=self._auth_headers())
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.json()["data"][0]["communication_id"], communication_id)

    def test_mark_read_persists_and_audits_with_stale_write_protection(self):
        notification = self._create_notification()
        stale = self.client.post(
            f"{NOTIFICATIONS_URL}{notification.notification_id}/mark-read/",
            data={"read_state_version": 99},
            content_type="application/json",
            headers=self._auth_headers(),
        )
        self.assertEqual(stale.status_code, 409)
        assert_error_envelope(self, stale.json(), "STALE_WRITE")

        response = self.client.post(
            f"{NOTIFICATIONS_URL}{notification.notification_id}/mark-read/",
            data={"read_state_version": notification.read_state_version},
            content_type="application/json",
            headers={**self._auth_headers(), "X-Request-ID": "req-mark-read"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_success_envelope(self, payload)
        self.assertTrue(payload["data"]["read"])
        self.assertEqual(payload["data"]["read_state_version"], 2)
        notification.refresh_from_db()
        self.assertEqual(notification.read_by_user, self.user)
        self.assertIsNotNone(notification.read_at)
        audit = AuditLog.objects.get(action="communications.notification.marked_read")
        self.assertEqual(audit.actor_user, self.user)
        self.assertEqual(audit.entity_type, "notification")
        self.assertEqual(audit.entity_id, notification.notification_id)
        self.assertEqual(audit.old_value_json["read"], False)
        self.assertEqual(audit.new_value_json["read"], True)

    def test_mark_read_same_version_retry_after_persisted_success_is_rejected(self):
        notification = self._create_notification()
        attempted_version = notification.read_state_version
        already_read_at = timezone.now()
        Notification.objects.filter(notification_id=notification.notification_id).update(
            read_at=already_read_at,
            read_by_user=self.user,
            read_state_version=attempted_version + 1,
        )
        AuditLog.objects.create(
            actor_user=self.user,
            actor_type="user",
            action="communications.notification.marked_read",
            entity_type="notification",
            entity_id=notification.notification_id,
            old_value_json={
                "read": False,
                "read_at": None,
                "read_by_user_id": None,
                "read_state_version": attempted_version,
            },
            new_value_json={
                "read": True,
                "read_at": already_read_at.isoformat(),
                "read_by_user_id": str(self.user.user_id),
                "read_state_version": attempted_version + 1,
            },
        )

        with mock.patch.object(
            services,
            "_notification_queryset_for_user",
            return_value=_StaleNotificationQuerySet(notification),
        ):
            response = self.client.post(
                f"{NOTIFICATIONS_URL}{notification.notification_id}/mark-read/",
                data={"read_state_version": attempted_version},
                content_type="application/json",
                headers=self._auth_headers(),
            )

        self.assertEqual(response.status_code, 409)
        assert_error_envelope(self, response.json(), "STALE_WRITE")
        notification.refresh_from_db()
        self.assertEqual(notification.read_state_version, attempted_version + 1)
        self.assertEqual(notification.read_at, already_read_at)
        self.assertEqual(notification.read_by_user, self.user)
        marked_read_audits = AuditLog.objects.filter(
            action="communications.notification.marked_read"
        )
        self.assertEqual(marked_read_audits.count(), 1)

    def test_list_rejects_unknown_query_parameters_and_filters_by_read_status(self):
        read = self._create_notification(title="Read notice", read_by_user=self.user)
        read.read_at = "2026-07-06T10:00:00Z"
        read.save(update_fields=["read_at"])
        unread = self._create_notification(title="Unread notice")

        response = self.client.get(
            NOTIFICATIONS_URL,
            data={"read_status": "unread"},
            headers=self._auth_headers(),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["notification_id"] for row in response.json()["data"]], [str(unread.notification_id)])

        invalid = self.client.get(
            NOTIFICATIONS_URL,
            data={"read_status": "maybe", "unknown": "value"},
            headers=self._auth_headers(),
        )
        self.assertEqual(invalid.status_code, 400)
        payload = invalid.json()
        assert_error_envelope(self, payload, "VALIDATION_ERROR")
        self.assertIn("read_status", payload["error"]["field_errors"])
        self.assertIn("unknown", payload["error"]["field_errors"])

    def test_unauthenticated_forbidden_and_wrong_recipient_mark_read_are_blocked(self):
        notification = self._create_notification()
        unauthenticated = self.client.get(NOTIFICATIONS_URL)
        self.assertEqual(unauthenticated.status_code, 401)
        assert_error_envelope(self, unauthenticated.json(), "AUTH_REQUIRED")

        forbidden = self.client.get(NOTIFICATIONS_URL, headers=self._plain_headers())
        self.assertEqual(forbidden.status_code, 403)
        assert_error_envelope(self, forbidden.json(), "PERMISSION_DENIED")

        wrong_recipient = self.client.post(
            f"{NOTIFICATIONS_URL}{notification.notification_id}/mark-read/",
            data={"read_state_version": notification.read_state_version},
            content_type="application/json",
            headers=self._auth_headers(email="accounts.head@sfpcl.example", password="AccountsPass123!"),
        )
        self.assertEqual(wrong_recipient.status_code, 404)
        assert_error_envelope(self, wrong_recipient.json(), "NOT_FOUND")
        notification.refresh_from_db()
        self.assertFalse(notification.read)
        self.assertEqual(
            AuditLog.objects.filter(action="communications.notification.marked_read").count(),
            0,
        )


class _StaleNotificationQuerySet:
    def __init__(self, row):
        self.row = row

    def get(self, **kwargs):
        return self.row
