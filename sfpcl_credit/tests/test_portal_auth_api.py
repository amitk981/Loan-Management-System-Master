import json

import jwt
from django.conf import settings
from django.test import Client, override_settings

from sfpcl_credit.identity.models import AuditLog, Role, UserSession
from sfpcl_credit.identity.models import PortalOtpChallenge
from sfpcl_credit.members.models import Member
from sfpcl_credit.tests.base import IdentityTestCase


@override_settings(PORTAL_AUTH_TEST_OTP="246810")
class PortalAuthApiTests(IdentityTestCase):
    def setUp(self):
        super().setUp()
        self.borrower_role = Role.objects.create(
            role_code="borrower_portal_user",
            role_name="Borrower Portal User",
            description="Member portal self-service user",
            is_system_role=True,
            status="active",
        )
        self.member = self._member(
            member_number="M-00042",
            folio_number="FOLIO-42",
            legal_name="Ganesh Thorat",
            email="ganesh.thorat@sfpcl.example",
            mobile_number="+919800000042",
            pan_encrypted="ABCDE1234F",
            aadhaar_encrypted="123456789012",
        )

    def _member(self, **overrides):
        data = {
            "member_number": "M-00001",
            "member_type": "individual_farmer",
            "legal_name": "Member One",
            "display_name": "Member One",
            "folio_number": "FOLIO-1",
            "membership_status": "active",
            "pan_encrypted": "ABCDE9999F",
            "pan_hash": "panhash1",
            "aadhaar_encrypted": "999988887777",
            "aadhaar_hash": "aadhaarhash1",
            "mobile_number": "+919800000001",
            "email": "member.one@sfpcl.example",
            "kyc_status": "verified",
            "default_status": "no_default",
        }
        data.update(overrides)
        return Member.objects.create(**data)

    def _activate_member(self, password="CorrectPortal123!"):
        start_response = Client().post(
            "/api/v1/portal/auth/activation/start/",
            data={
                "folio_or_member_id": self.member.folio_number,
                "contact": self.member.email,
                "pan_last4": "234F",
                "aadhaar_last4": "9012",
            },
            content_type="application/json",
        )
        self.assertEqual(start_response.status_code, 200)
        challenge = PortalOtpChallenge.objects.get(
            challenge_id=start_response.json()["data"]["challenge_id"]
        )
        complete_response = Client().post(
            "/api/v1/portal/auth/activation/complete/",
            data={
                "challenge_id": str(challenge.challenge_id),
                "otp": challenge.test_plain_otp,
                "password": password,
                "confirm_password": password,
            },
            content_type="application/json",
        )
        self.assertEqual(complete_response.status_code, 200)
        return complete_response.json()["data"]

    def test_valid_invited_member_can_activate_and_login_with_member_scoped_tokens(self):
        activation_payload = self._activate_member()

        self.assertEqual(activation_payload["portal_account"]["member_id"], str(self.member.member_id))
        self.assertEqual(activation_payload["portal_account"]["status"], "active")
        self.assertNotIn("pan", json.dumps(activation_payload).lower())
        self.assertTrue(
            AuditLog.objects.filter(
                action="portal.auth.activation.completed",
                entity_id=self.member.member_id,
            ).exists()
        )

        login_response = Client().post(
            "/api/v1/portal/auth/login/",
            data={"identifier": self.member.email, "password": "CorrectPortal123!"},
            content_type="application/json",
        )

        self.assertEqual(login_response.status_code, 200)
        payload = login_response.json()["data"]
        claims = jwt.decode(
            payload["access_token"], settings.SECRET_KEY, algorithms=["HS256"]
        )
        self.assertEqual(claims["member_id"], str(self.member.member_id))
        self.assertEqual(claims["portal_role"], "borrower_member")
        self.assertEqual(claims["role_codes"], ["borrower_portal_user"])
        self.assertNotIn("applications.loan_application.complete_check", payload["user"]["permissions"])
        self.assertEqual(payload["user"]["member_id"], str(self.member.member_id))
        self.assertEqual(payload["user"]["portal_role"], "borrower_member")

        staff_response = Client().post(
            "/api/v1/loan-applications/00000000-0000-0000-0000-000000000000/return-with-deficiencies/",
            data={"items": [], "communication_mode": "portal", "message": "No staff access"},
            content_type="application/json",
            headers={"Authorization": f"Bearer {payload['access_token']}"},
        )
        self.assertEqual(staff_response.status_code, 403)
        self.assertEqual(staff_response.json()["error"]["code"], "PERMISSION_DENIED")

    def test_activation_rejects_unknown_and_already_active_members(self):
        unknown_response = Client().post(
            "/api/v1/portal/auth/activation/start/",
            data={
                "folio_or_member_id": "UNKNOWN",
                "contact": "unknown@sfpcl.example",
                "pan_last4": "0000",
            },
            content_type="application/json",
        )
        self.assertEqual(unknown_response.status_code, 400)
        self.assertEqual(unknown_response.json()["error"]["code"], "ACTIVATION_NOT_ALLOWED")

        self._activate_member()
        repeated_response = Client().post(
            "/api/v1/portal/auth/activation/start/",
            data={
                "folio_or_member_id": self.member.folio_number,
                "contact": self.member.email,
                "pan_last4": "234F",
                "aadhaar_last4": "9012",
            },
            content_type="application/json",
        )
        self.assertEqual(repeated_response.status_code, 409)
        self.assertEqual(repeated_response.json()["error"]["code"], "PORTAL_ACCOUNT_ACTIVE")

    def test_password_reset_is_single_use_and_revokes_existing_sessions(self):
        self._activate_member()
        login_response = Client().post(
            "/api/v1/portal/auth/login/",
            data={"identifier": self.member.mobile_number, "password": "CorrectPortal123!"},
            content_type="application/json",
        )
        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.json()["data"]["access_token"]

        start_response = Client().post(
            "/api/v1/portal/auth/password-reset/start/",
            data={"identifier": self.member.email},
            content_type="application/json",
        )
        self.assertEqual(start_response.status_code, 200)
        challenge = PortalOtpChallenge.objects.get(
            challenge_id=start_response.json()["data"]["challenge_id"]
        )
        complete_payload = {
            "challenge_id": str(challenge.challenge_id),
            "otp": challenge.test_plain_otp,
            "password": "NewPortal123!",
            "confirm_password": "NewPortal123!",
        }

        complete_response = Client().post(
            "/api/v1/portal/auth/password-reset/complete/",
            data=complete_payload,
            content_type="application/json",
        )

        self.assertEqual(complete_response.status_code, 200)
        self.assertEqual(
            UserSession.objects.get(user__email=self.member.email).session_status, "revoked"
        )
        self.assertEqual(
            UserSession.objects.get(user__email=self.member.email).revoked_reason,
            "portal_password_reset",
        )
        self.assertTrue(
            AuditLog.objects.filter(action="portal.auth.password_reset.completed").exists()
        )

        replay_response = Client().post(
            "/api/v1/portal/auth/password-reset/complete/",
            data=complete_payload,
            content_type="application/json",
        )
        self.assertEqual(replay_response.status_code, 400)
        self.assertEqual(replay_response.json()["error"]["code"], "OTP_INVALID")

        me_response = Client().get(
            "/api/v1/auth/me/",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        self.assertEqual(me_response.status_code, 401)

    def test_security_settings_password_change_audits_and_revokes_other_sessions(self):
        self._activate_member()
        first_login = Client().post(
            "/api/v1/portal/auth/login/",
            data={"identifier": self.member.email, "password": "CorrectPortal123!"},
            content_type="application/json",
        )
        second_login = Client().post(
            "/api/v1/portal/auth/login/",
            data={"identifier": self.member.email, "password": "CorrectPortal123!"},
            content_type="application/json",
        )
        self.assertEqual(first_login.status_code, 200)
        self.assertEqual(second_login.status_code, 200)
        first_access = first_login.json()["data"]["access_token"]
        second_access = second_login.json()["data"]["access_token"]

        response = Client().post(
            "/api/v1/portal/auth/password/change/",
            data={
                "current_password": "CorrectPortal123!",
                "new_password": "ChangedPortal123!",
                "confirm_password": "ChangedPortal123!",
            },
            content_type="application/json",
            headers={"Authorization": f"Bearer {second_access}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            AuditLog.objects.filter(action="portal.auth.password_changed").exists()
        )
        revoked = UserSession.objects.filter(revoked_reason="portal_password_change")
        self.assertEqual(revoked.count(), 1)

        first_me_response = Client().get(
            "/api/v1/auth/me/",
            headers={"Authorization": f"Bearer {first_access}"},
        )
        self.assertEqual(first_me_response.status_code, 401)

        second_me_response = Client().get(
            "/api/v1/auth/me/",
            headers={"Authorization": f"Bearer {second_access}"},
        )
        self.assertEqual(second_me_response.status_code, 200)
        self.assertEqual(second_me_response.json()["data"]["member_id"], str(self.member.member_id))
