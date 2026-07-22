import json
from datetime import date

from django.test import Client, TestCase

from sfpcl_credit.identity.models import Permission, Role, RolePermission, User


class ComplianceApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager_role = Role.objects.create(role_code="company_secretary", role_name="CS")
        self.reviewer_role = Role.objects.create(role_code="cfo", role_name="CFO")
        self.manager = self._user(self.manager_role, "cs@example.test")
        self.reviewer = self._user(self.reviewer_role, "cfo@example.test")
        self._grant(self.manager_role, "compliance.control.read", "compliance.control.manage")
        self.auth = self._auth(self.manager)

    def test_control_create_and_list_use_standard_contract_and_available_actions(self):
        response = self.client.post(
            "/api/v1/compliance-controls/",
            data=json.dumps(
                {
                    "control_code": "MONEY_LENDING_ANNUAL",
                    "control_name": "Annual money-lending law review",
                    "control_area": "money_lending",
                    "legal_basis": "Annual state law applicability review.",
                    "control_type": "detective",
                    "frequency": "annual",
                    "owner_role_code": self.manager_role.role_code,
                    "owner_user_id": str(self.manager.pk),
                    "reviewer_user_id": str(self.reviewer.pk),
                    "first_due_date": date(2027, 3, 31).isoformat(),
                    "evidence_required": "Restricted legal opinion and Board note.",
                    "risk_if_missed": "Annual applicability review overdue.",
                    "status": "active",
                }
            ),
            content_type="application/json",
            **self.auth,
        )
        listed = self.client.get("/api/v1/compliance-controls/", **self.auth)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json()["data"]["control_code"], "MONEY_LENDING_ANNUAL")
        self.assertEqual(response.json()["data"]["available_actions"], ["update"])
        self.assertEqual(listed.status_code, 200, listed.content)
        self.assertEqual(listed.json()["pagination"]["total_count"], 1)

    def test_task_evidence_api_enforces_maker_checker_completion(self):
        from sfpcl_credit.compliance.models import ComplianceControl
        from sfpcl_credit.documents.models import DocumentFile

        self._grant(
            self.manager_role,
            "compliance.task.create",
            "compliance.task.read",
            "compliance.task.update",
            "compliance.evidence.submit",
        )
        self._grant(self.reviewer_role, "compliance.task.read", "compliance.evidence.review")
        control = ComplianceControl.objects.create(
            control_code="ACCESS_REVIEW", control_name="Quarterly access review",
            control_area="data_protection", legal_basis="Approved access control.",
            control_type="detective", frequency="quarterly",
            owner_role_code=self.manager_role.role_code, owner_user=self.manager,
            reviewer_user=self.reviewer, first_due_date=date(2026, 12, 31),
            evidence_required="Restricted access report.", risk_if_missed="Escalate.",
        )
        created = self.client.post(
            "/api/v1/compliance-tasks/",
            data=json.dumps({
                "compliance_control_id": str(control.pk), "task_period": "2026-Q4",
                "due_date": "2026-12-31", "assigned_to_user_id": str(self.manager.pk),
                "reviewer_user_id": str(self.reviewer.pk),
            }), content_type="application/json", **self.auth,
        )
        self.assertEqual(created.status_code, 200, created.content)
        task_id = created.json()["data"]["compliance_task_id"]
        document = DocumentFile.objects.create(
            file_name="access-review.pdf", storage_provider="local",
            storage_key="governed/compliance/access-review.pdf",
            uploaded_by_user=self.manager, sensitivity_level="restricted",
        )
        submitted = self.client.post(
            f"/api/v1/compliance-tasks/{task_id}/evidence/",
            data=json.dumps({"evidence_type": "access_report", "document_id": str(document.pk),
                             "summary": "Quarterly access review completed."}),
            content_type="application/json", **self.auth,
        )
        self.assertEqual(submitted.status_code, 200, submitted.content)
        evidence_id = submitted.json()["data"]["compliance_evidence_id"]
        reviewed = self.client.post(
            f"/api/v1/compliance-evidence/{evidence_id}/review/",
            data=json.dumps({"review_status": "accepted", "review_comments": "Accepted."}),
            content_type="application/json", **self._auth(self.reviewer),
        )
        self.assertEqual(reviewed.status_code, 200, reviewed.content)
        self.assertEqual(reviewed.json()["data"]["task_status"], "completed")

    def _user(self, role, email):
        user = User.objects.create(
            full_name=role.role_name, email=email, primary_role=role, password_hash=""
        )
        user.set_password("CompliancePass123!")
        user.save(update_fields=["password_hash"])
        return user

    def _grant(self, role, *codes):
        for code in codes:
            permission, _created = Permission.objects.get_or_create(
                permission_code=code,
                defaults={"permission_name": code, "module_name": "compliance", "risk_level": "high"},
            )
            RolePermission.objects.get_or_create(role=role, permission=permission)

    def _auth(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "CompliancePass123!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {"HTTP_AUTHORIZATION": f"Bearer {response.json()['data']['access_token']}"}
