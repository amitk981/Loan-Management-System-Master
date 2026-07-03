from decimal import Decimal

from django.test import Client

from sfpcl_credit.identity.models import AuditLog, Permission, RolePermission
from sfpcl_credit.tests.base import IdentityTestCase
from sfpcl_credit.tracer.models import (
    LoanAccount,
    LoanApplication,
    Member,
    Repayment,
    WorkflowEvent,
)


TRACER_PERMISSION = "tracer.lifecycle.run"


class TracerApiTests(IdentityTestCase):
    def setUp(self):
        super().setUp()
        permission = Permission.objects.create(
            permission_code=TRACER_PERMISSION,
            permission_name="Run MVP tracer",
            module_name="tracer",
            risk_level="high",
        )
        RolePermission.objects.create(role=self.role, permission=permission)
        self.client = Client()

    def _access_token(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={
                "email": "credit.manager@sfpcl.example",
                "password": "CorrectHorse123!",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["access_token"], response.json()["data"]["refresh_token"]

    def _auth_headers(self):
        access_token, _refresh_token = self._access_token()
        return {"Authorization": f"Bearer {access_token}"}

    def _post(self, path, data=None, headers=None):
        return self.client.post(
            path,
            data=data or {},
            content_type="application/json",
            headers=headers or self._auth_headers(),
        )

    def test_full_tracer_lifecycle_persists_and_audits_every_transition(self):
        headers = self._auth_headers()

        member_response = self._post(
            "/api/v1/tracer/members/",
            {"display_name": "Tracer Member"},
            headers=headers,
        )
        self.assertEqual(member_response.status_code, 200)
        member = member_response.json()["data"]
        self.assertEqual(member["status"], "active")
        self.assertEqual(member["reference"], "MEM-000001")

        application_response = self._post(
            f"/api/v1/tracer/members/{member['member_id']}/loan-applications/",
            {"amount": "400000.00"},
            headers=headers,
        )
        self.assertEqual(application_response.status_code, 200)
        application = application_response.json()["data"]
        self.assertEqual(application["status"], "draft")
        self.assertEqual(application["amount"], "400000.00")

        sanction_response = self._post(
            f"/api/v1/tracer/loan-applications/{application['loan_application_id']}/sanction/",
            headers=headers,
        )
        self.assertEqual(sanction_response.status_code, 200)
        sanction = sanction_response.json()["data"]
        self.assertEqual(sanction["previous_status"], "draft")
        self.assertEqual(sanction["new_status"], "sanctioned")
        self.assertIn("workflow_event_id", sanction)

        account_response = self._post(
            f"/api/v1/tracer/loan-applications/{application['loan_application_id']}/loan-account/",
            headers=headers,
        )
        self.assertEqual(account_response.status_code, 200)
        account = account_response.json()["data"]
        self.assertEqual(account["status"], "pending_disbursement")
        self.assertEqual(account["amount"], "400000.00")

        disbursement_response = self._post(
            f"/api/v1/tracer/loan-accounts/{account['loan_account_id']}/disburse/",
            headers=headers,
        )
        self.assertEqual(disbursement_response.status_code, 200)
        self.assertEqual(disbursement_response.json()["data"]["new_status"], "active")

        repayment_response = self._post(
            f"/api/v1/tracer/loan-accounts/{account['loan_account_id']}/repayments/",
            {"amount": "400000.00"},
            headers=headers,
        )
        self.assertEqual(repayment_response.status_code, 200)
        repayment = repayment_response.json()["data"]
        self.assertEqual(repayment["status"], "posted")
        self.assertEqual(repayment["amount"], "400000.00")

        closure_response = self._post(
            f"/api/v1/tracer/loan-accounts/{account['loan_account_id']}/close/",
            headers=headers,
        )
        self.assertEqual(closure_response.status_code, 200)
        self.assertEqual(closure_response.json()["data"]["new_status"], "closed")

        self.assertEqual(Member.objects.count(), 1)
        self.assertEqual(LoanApplication.objects.get().status, "sanctioned")
        self.assertEqual(LoanAccount.objects.get().status, "closed")
        self.assertEqual(Repayment.objects.get().amount, Decimal("400000.00"))
        self.assertEqual(WorkflowEvent.objects.count(), 7)
        self.assertEqual(
            AuditLog.objects.filter(action__startswith="tracer.").count(),
            7,
        )

    def test_transition_guard_rejects_creating_account_before_sanction(self):
        headers = self._auth_headers()
        member = self._post(
            "/api/v1/tracer/members/",
            {"display_name": "Out Of Order Member"},
            headers=headers,
        ).json()["data"]
        application = self._post(
            f"/api/v1/tracer/members/{member['member_id']}/loan-applications/",
            {"amount": "100000.00"},
            headers=headers,
        ).json()["data"]

        response = self._post(
            f"/api/v1/tracer/loan-applications/{application['loan_application_id']}/loan-account/",
            headers=headers,
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error"]["code"], "INVALID_STATE_TRANSITION")
        self.assertEqual(LoanAccount.objects.count(), 0)

    def test_transition_guards_reject_repeated_sanction_repayment_before_disbursement_and_close_before_repayment(self):
        headers = self._auth_headers()
        member = self._post(
            "/api/v1/tracer/members/",
            {"display_name": "Guard Member"},
            headers=headers,
        ).json()["data"]
        application = self._post(
            f"/api/v1/tracer/members/{member['member_id']}/loan-applications/",
            {"amount": "120000.00"},
            headers=headers,
        ).json()["data"]
        self._post(
            f"/api/v1/tracer/loan-applications/{application['loan_application_id']}/sanction/",
            headers=headers,
        )
        repeated_sanction = self._post(
            f"/api/v1/tracer/loan-applications/{application['loan_application_id']}/sanction/",
            headers=headers,
        )
        account = self._post(
            f"/api/v1/tracer/loan-applications/{application['loan_application_id']}/loan-account/",
            headers=headers,
        ).json()["data"]
        early_repayment = self._post(
            f"/api/v1/tracer/loan-accounts/{account['loan_account_id']}/repayments/",
            {"amount": "120000.00"},
            headers=headers,
        )
        self._post(
            f"/api/v1/tracer/loan-accounts/{account['loan_account_id']}/disburse/",
            headers=headers,
        )
        early_closure = self._post(
            f"/api/v1/tracer/loan-accounts/{account['loan_account_id']}/close/",
            headers=headers,
        )

        self.assertEqual(repeated_sanction.status_code, 409)
        self.assertEqual(early_repayment.status_code, 409)
        self.assertEqual(early_closure.status_code, 409)
        self.assertEqual(Repayment.objects.count(), 0)
        self.assertEqual(LoanAccount.objects.get().status, "active")

    def test_positive_amounts_are_required(self):
        member = self._post(
            "/api/v1/tracer/members/",
            {"display_name": "Amount Member"},
        ).json()["data"]

        response = self._post(
            f"/api/v1/tracer/members/{member['member_id']}/loan-applications/",
            {"amount": "0.00"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "VALIDATION_ERROR")
        self.assertEqual(LoanApplication.objects.count(), 0)

    def test_unauthenticated_tracer_request_returns_standard_401_without_domain_rows(self):
        response = self.client.post(
            "/api/v1/tracer/members/",
            data={"display_name": "Unauthenticated"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        payload = response.json()
        self.assertEqual(payload["success"], False)
        self.assertEqual(payload["error"]["code"], "AUTH_REQUIRED")
        self.assertEqual(payload["meta"]["api_version"], "v1")
        self.assertEqual(Member.objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(action__startswith="tracer.").count(), 0)

    def test_revoked_access_token_is_rejected_before_domain_transition(self):
        access_token, refresh_token = self._access_token()
        logout_response = self.client.post(
            "/api/v1/auth/logout/",
            data={"refresh_token": refresh_token},
            content_type="application/json",
        )
        self.assertEqual(logout_response.status_code, 200)

        response = self.client.post(
            "/api/v1/tracer/members/",
            data={"display_name": "Revoked"},
            content_type="application/json",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "INVALID_TOKEN")
        self.assertEqual(Member.objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(action__startswith="tracer.").count(), 0)

    def test_authenticated_user_without_tracer_permission_cannot_write_domain_rows(self):
        RolePermission.objects.filter(role=self.role).delete()
        access_token, _refresh_token = self._access_token()

        response = self.client.post(
            "/api/v1/tracer/members/",
            data={"display_name": "No Permission"},
            content_type="application/json",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "PERMISSION_DENIED")
        self.assertEqual(Member.objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(action__startswith="tracer.").count(), 0)
