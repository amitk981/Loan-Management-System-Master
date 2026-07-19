import tempfile
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import Client, TestCase, override_settings

from sfpcl_credit.applications.models import ApplicationDeficiency, LoanApplication
from sfpcl_credit.documents.models import DocumentTemplate
from sfpcl_credit.identity.models import PortalAccount
from sfpcl_credit.legal_documents.models import LoanDocument


PORTAL_EMAIL = "e2e.portal@sfpcl.example"
PORTAL_PASSWORD = "E2eTracer123!"
COMPLIANCE_EMAIL = "e2e.portal.compliance@sfpcl.example"


@override_settings(
    DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-portal-e2e-seed-")
)
class SeedPortalE2eFixtureTests(TestCase):
    def test_epic009_then_portal_seed_order_reuses_governed_template_identities(self):
        with patch.dict(
            "os.environ",
            {"SFPCL_DEBUG": "true", "SFPCL_ALLOW_E2E_SEED": "true"},
        ):
            call_command("seed_epic_009_e2e_fixture")
            call_command("seed_portal_e2e_fixture")
            call_command("seed_portal_e2e_fixture")

        for document_type in ("term_sheet", "power_of_attorney"):
            self.assertEqual(
                DocumentTemplate.objects.filter(
                    document_type=document_type,
                    borrower_type="individual_farmer",
                    template_version="1.0",
                ).count(),
                1,
            )

    def test_seed_refuses_without_both_isolated_e2e_guards(self):
        with self.assertRaisesMessage(CommandError, "isolated E2E seed guards"):
            call_command("seed_portal_e2e_fixture")

        self.assertFalse(PortalAccount.objects.filter(user__email=PORTAL_EMAIL).exists())

    def test_seed_is_idempotent_and_exposes_real_portal_contracts(self):
        call_command("seed_role_catalogue")
        with patch.dict(
            "os.environ",
            {"SFPCL_DEBUG": "true", "SFPCL_ALLOW_E2E_SEED": "true"},
        ):
            call_command("seed_portal_e2e_fixture")
            call_command("seed_portal_e2e_fixture")

        self.assertEqual(
            PortalAccount.objects.filter(user__email=PORTAL_EMAIL).count(), 1
        )
        self.assertEqual(
            LoanApplication.objects.filter(
                application_reference_number__in=["LO000008L4", "LO000008L4-R"]
            ).count(),
            2,
        )
        approved = LoanApplication.objects.get(
            application_reference_number="LO000008L4"
        )
        current_term_sheet = LoanDocument.objects.get(
            loan_application=approved, document_type="term_sheet"
        )
        self.assertEqual(current_term_sheet.generation_status, "generated")
        self.assertEqual(
            current_term_sheet.renderer_contract_version,
            LoanDocument.RENDERER_CONTRACT_V1,
        )
        self.assertTrue(current_term_sheet.renderer_validated_document_id)
        self.assertEqual(
            ApplicationDeficiency.objects.filter(
                loan_application__application_reference_number="LO000008L4-R",
                resolution_status="open",
            ).count(),
            1,
        )

        client = Client()
        login = client.post(
            "/api/v1/portal/auth/login/",
            data={"identifier": PORTAL_EMAIL, "password": PORTAL_PASSWORD},
            content_type="application/json",
        )
        self.assertEqual(login.status_code, 200, login.content)
        headers = {
            "Authorization": f"Bearer {login.json()['data']['access_token']}"
        }
        current_user = client.get("/api/v1/auth/me/", headers=headers)
        self.assertEqual(current_user.status_code, 200, current_user.content)
        self.assertEqual(
            current_user.json()["data"]["roles"],
            [
                {
                    "role_code": "borrower_portal_user",
                    "role_name": "Borrower / Member",
                }
            ],
        )
        applications = client.get("/api/v1/portal/applications/", headers=headers)
        self.assertEqual(applications.status_code, 200, applications.content)
        references = {
            item["application_reference_number"]
            for item in applications.json()["data"]["items"]
        }
        self.assertEqual(references, {"LO000008L4", "LO000008L4-R"})

        documentation = client.get(
            f"/api/v1/portal/applications/{approved.pk}/documentation-actions/",
            headers=headers,
        )
        self.assertEqual(documentation.status_code, 200, documentation.content)
        term_sheet = next(
            item
            for item in documentation.json()["data"]["actions"]
            if item["action_code"] == "term_sheet"
        )
        self.assertEqual(term_sheet["status"], "complete")
        self.assertIsNotNone(term_sheet["download"])
        self.assertFalse(term_sheet["upload_allowed"])
        self.assertFalse(term_sheet["reupload_allowed"])

        staff_login = client.post(
            "/api/v1/auth/login/",
            data={"email": COMPLIANCE_EMAIL, "password": PORTAL_PASSWORD},
            content_type="application/json",
        )
        self.assertEqual(staff_login.status_code, 200, staff_login.content)
        staff_headers = {
            "Authorization": f"Bearer {staff_login.json()['data']['access_token']}"
        }
        workspace = client.get(
            f"/api/v1/loan-applications/{approved.pk}/documentation-workspace/",
            headers=staff_headers,
        )
        self.assertEqual(workspace.status_code, 200, workspace.content)
        power_of_attorney = next(
            item
            for item in workspace.json()["data"]["items"]
            if item["item_code"] == "poa"
        )
        self.assertEqual(
            {action["label"] for action in power_of_attorney["available_actions"]},
            {
                "Record borrower signature",
                "Record nominee signature",
                "Record stamp",
                "Record notarisation",
                "Upload / re-upload signed copy",
                "Request correction",
            },
        )
