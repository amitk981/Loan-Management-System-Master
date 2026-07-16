import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
from threading import Barrier
from types import SimpleNamespace
from unittest import skipUnless
from unittest.mock import patch
from uuid import uuid4
from xml.etree import ElementTree

from django.db import close_old_connections, connection
from django.test import (
    Client, RequestFactory, TestCase, TransactionTestCase, override_settings,
)
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import ApprovalCase, SanctionDecision
from sfpcl_credit.credit.models import LoanAppraisalNote, RiskAssessment
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.domain_errors import DomainPermissionDenied
from sfpcl_credit.finance.models import SapCustomerCode, SapCustomerProfileRequest
from sfpcl_credit.finance.modules.annexure_storage import EncryptedAnnexureStorage
from sfpcl_credit.finance.modules.sap_customer_request import create_request
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import Member
from sfpcl_credit.shared.encryption import FieldEncryption
from sfpcl_credit.tests.api_contracts import assert_error_envelope
from sfpcl_credit.tests.api_contracts import assert_success_envelope
from sfpcl_credit.workflows.models import WorkflowEvent


class SapCustomerProfileRequestApiTests(TestCase):
    password = "SapRequestPass123!"

    def setUp(self):
        self.storage = tempfile.TemporaryDirectory()
        self.settings = override_settings(DOCUMENT_STORAGE_ROOT=self.storage.name)
        self.settings.enable()
        self.client = Client()
        self.credit_manager = self._user(
            "credit_manager", "SAP Request Credit Manager", "finance.sap_request.create"
        )
        self.assignee = self._user(
            "senior_manager_finance", "SAP Senior Manager Finance"
        )
        self.application = self._terminal_application()

    def tearDown(self):
        self.settings.disable()
        self.storage.cleanup()

    def test_credit_manager_creates_draft_request_after_terminal_sanction(self):
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/sap-customer-profile-request/",
            {"assigned_to_user_id": str(self.assignee.pk)},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-sap-profile-001",
            HTTP_USER_AGENT="SAP request contract test",
            REMOTE_ADDR="203.0.113.90",
            **self._auth(self.credit_manager),
        )

        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        assert_success_envelope(self, payload)
        data = payload["data"]
        self.assertEqual(data["request_status"], "draft")
        self.assertEqual(
            data["assigned_to_user"],
            {"user_id": str(self.assignee.pk), "full_name": self.assignee.full_name},
        )
        self.assertTrue(data["sap_customer_profile_request_id"])
        self.assertTrue(data["excel_file_id"])
        self.assertEqual(
            AuditLog.objects.filter(action="finance.sap_customer_code.requested").count(),
            1,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="SAPCustomerCodeRequested").count(),
            1,
        )

    def test_service_freezes_canonical_sensitive_facts_in_restricted_annexure(self):
        request = RequestFactory().post(
            "/sap-request/",
            HTTP_X_REQUEST_ID="req-sap-service-001",
            HTTP_USER_AGENT="SAP service contract test",
            REMOTE_ADDR="203.0.113.91",
        )
        response = create_request(
            actor=self.credit_manager,
            application_id=self.application.pk,
            payload={"assigned_to_user_id": str(self.assignee.pk)},
            request=request,
        )

        row = SapCustomerProfileRequest.objects.get(pk=response["sap_customer_profile_request_id"])
        self.assertEqual(row.farmer_full_name, "Ramesh Patil")
        self.assertEqual(row.borrower_type, "individual_farmer")
        self.assertEqual(row.folio_number, "FOL-SAP-001")
        self.assertEqual(row.address_text, "Village Road, Nashik, Nashik, Maharashtra, 422001")
        self.assertEqual(str(row.sanctioned_amount), "400000.00")
        self.assertEqual(
            FieldEncryption.decrypt("finance.sap_request.pan", row.pan_number_encrypted),
            "ABCDE1234F",
        )
        self.assertEqual(
            FieldEncryption.decrypt("finance.sap_request.aadhaar", row.aadhaar_number_encrypted),
            "123412341234",
        )
        self.assertNotIn("ABCDE1234F", row.pan_number_encrypted)
        self.assertNotIn("123412341234", row.aadhaar_number_encrypted)

        document = DocumentFile.objects.get(pk=row.excel_file_id)
        self.assertEqual(document.sensitivity_level, "restricted")
        self.assertEqual(document.file_extension, ".xlsx")
        self.assertEqual(
            document.mime_type,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        physical_bytes = (Path(self.storage.name) / document.storage_key).read_bytes()
        self.assertNotIn(b"ABCDE1234F", physical_bytes)
        self.assertNotIn(b"123412341234", physical_bytes)
        self.assertFalse(zipfile.is_zipfile(BytesIO(physical_bytes)))
        workbook = EncryptedAnnexureStorage().read_verified(document)
        values = self._worksheet_values(workbook)
        self.assertEqual(values[0][:6], [
            "Loan Application Number", "Borrower Full Name", "Borrower Type",
            "Aadhaar Number", "PAN Number", "Registered Address",
        ])
        self.assertEqual(values[1][:6], [
            "LO00000025", "Ramesh Patil", "individual_farmer", "123412341234",
            "ABCDE1234F", "Village Road, Nashik, Nashik, Maharashtra, 422001",
        ])

        self.application.member.legal_name = "Changed after request"
        self.application.member.save(update_fields=["legal_name"])
        row.refresh_from_db()
        self.assertEqual(row.farmer_full_name, "Ramesh Patil")
        evidence = AuditLog.objects.get(action="finance.sap_customer_code.requested")
        serialized_evidence = str(evidence.new_value_json)
        for secret in ("ABCDE1234F", "123412341234", "Village Road"):
            self.assertNotIn(secret, serialized_evidence)
            self.assertNotIn(secret, str(response))

    def test_sequential_retry_returns_same_request_without_duplicate_artifacts(self):
        first = self._post_request("req-sap-replay-1")
        second = self._post_request("req-sap-replay-2")

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(second.status_code, 200, second.content)
        self.assertEqual(first.json()["data"], second.json()["data"])
        self.assertEqual(SapCustomerProfileRequest.objects.count(), 1)
        self.assertEqual(DocumentFile.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="finance.sap_customer_code.requested").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="SAPCustomerCodeRequested").count(), 1
        )

    def test_replay_rejects_a_newly_active_customer_code(self):
        first = self._post_request("req-sap-before-code")
        self.assertEqual(first.status_code, 200, first.content)
        SapCustomerCode.objects.create(
            member=self.application.member,
            sap_customer_code="SAP-CUST-ACTIVATED-AFTER-REQUEST",
            created_for_loan_application=self.application,
            created_by_user=self.assignee,
        )

        replay = self._post_request("req-sap-after-code")

        self.assertEqual(replay.status_code, 409, replay.content)
        assert_error_envelope(self, replay.json(), "SAP_REQUEST_CONFLICT")
        self.assertEqual(SapCustomerProfileRequest.objects.count(), 1)
        self.assertEqual(DocumentFile.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="finance.sap_customer_code.requested").count(), 1
        )

    def test_service_reloads_persisted_actor_before_authorizing(self):
        stale_actor = User.objects.get(pk=self.credit_manager.pk)
        User.objects.filter(pk=stale_actor.pk).update(status="inactive")

        with self.assertRaises(DomainPermissionDenied):
            create_request(
                actor=stale_actor,
                application_id=self.application.pk,
                payload={"assigned_to_user_id": str(self.assignee.pk)},
                request=RequestFactory().post("/sap-request/"),
            )

        self._assert_no_sap_artifacts()

    def test_current_verified_bank_fact_freezes_only_last_four_and_ifsc(self):
        bank_fact = SimpleNamespace(
            valid=True,
            bank_account_masked="********6789",
            ifsc="HDFC0001234",
        )
        with patch(
            "sfpcl_credit.finance.modules.sap_customer_request.resolve_blank_cheque_bank_fact",
            return_value=bank_fact,
        ):
            response = self._post_request("req-sap-verified-bank")

        self.assertEqual(response.status_code, 200, response.content)
        row = SapCustomerProfileRequest.objects.get(loan_application=self.application)
        self.assertEqual(row.bank_account_last4, "6789")
        self.assertEqual(row.ifsc, "HDFC0001234")
        self.assertFalse(hasattr(row, "bank_account_number"))
        values = self._worksheet_values(
            EncryptedAnnexureStorage().read_verified(row.excel_file)
        )
        self.assertEqual(values[1][11:], ["6789", "HDFC0001234"])

    def test_fpc_request_does_not_fabricate_aadhaar(self):
        application = self._terminal_application(
            suffix="FPC", member_type="fpc", pan="FGHIJ5678K", aadhaar=""
        )
        response = self._post_request("req-sap-fpc", application=application)

        self.assertEqual(response.status_code, 200, response.content)
        row = SapCustomerProfileRequest.objects.get(loan_application=application)
        self.assertEqual(row.aadhaar_number_encrypted, "")
        self.assertEqual(self._worksheet_values(
            EncryptedAnnexureStorage().read_verified(row.excel_file)
        )[1][3], "")

    def test_invalid_requests_leave_no_request_file_or_evidence(self):
        invalid_assignee = self._user("field_officer", "Not Finance Assignee")
        response = self._post_request(
            "req-sap-invalid-assignee", assigned_to=invalid_assignee
        )
        self.assertEqual(response.status_code, 400, response.content)
        assert_error_envelope(self, response.json(), "VALIDATION_ERROR")
        self._assert_no_sap_artifacts()

        self.application.application_status = LoanApplication.STATUS_SUBMITTED_TO_SANCTION
        self.application.save(update_fields=["application_status"])
        response = self._post_request("req-sap-non-terminal")
        self.assertEqual(response.status_code, 409, response.content)
        assert_error_envelope(self, response.json(), "INVALID_STATE")
        self._assert_no_sap_artifacts()

    def test_active_customer_code_and_missing_source_fact_roll_back_cleanly(self):
        SapCustomerCode.objects.create(
            member=self.application.member,
            sap_customer_code="SAP-CUST-RETAINED-001",
            created_for_loan_application=self.application,
            created_by_user=self.assignee,
            status="active",
        )
        response = self._post_request("req-sap-existing-code")
        self.assertEqual(response.status_code, 409, response.content)
        assert_error_envelope(self, response.json(), "SAP_REQUEST_CONFLICT")
        self._assert_no_sap_artifacts()

        SapCustomerCode.objects.all().delete()
        self.application.member.registered_pincode = ""
        self.application.member.save(update_fields=["registered_pincode"])
        response = self._post_request("req-sap-missing-fact")
        self.assertEqual(response.status_code, 400, response.content)
        self._assert_no_sap_artifacts()

    def test_wrong_role_and_missing_application_follow_nondisclosure_contract(self):
        outsider = self._user(
            "sap_request_outsider", "SAP Request Outsider", "finance.sap_request.create"
        )
        response = self._post_request("req-sap-wrong-role", actor=outsider)
        self.assertEqual(response.status_code, 403, response.content)
        assert_error_envelope(self, response.json(), "FORBIDDEN")
        self._assert_no_sap_artifacts()

        response = self._post_request(
            "req-sap-missing-parent", application_id=uuid4()
        )
        self.assertEqual(response.status_code, 403, response.content)
        assert_error_envelope(self, response.json(), "OBJECT_ACCESS_DENIED")
        self._assert_no_sap_artifacts()

    def test_cross_object_denial_and_inactive_identities_leave_no_artifacts(self):
        scoped = self._user(
            "sap_scoped_actor", "SAP Scoped Actor", "finance.sap_request.create"
        )
        scoped.approval_authority_type = "credit_manager"
        scoped.save(update_fields=["approval_authority_type"])
        response = self._post_request("req-sap-object-denied", actor=scoped)
        self.assertEqual(response.status_code, 403, response.content)
        assert_error_envelope(self, response.json(), "OBJECT_ACCESS_DENIED")
        self._assert_no_sap_artifacts()

        self.assignee.status = "inactive"
        self.assignee.save(update_fields=["status"])
        response = self._post_request("req-sap-inactive-assignee")
        self.assertEqual(response.status_code, 400, response.content)
        self._assert_no_sap_artifacts()

        self.assignee.status = "active"
        self.assignee.save(update_fields=["status"])
        headers = self._auth(self.credit_manager)
        self.credit_manager.status = "inactive"
        self.credit_manager.save(update_fields=["status"])
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/sap-customer-profile-request/",
            {"assigned_to_user_id": str(self.assignee.pk)},
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 401, response.content)
        self._assert_no_sap_artifacts()

    def test_client_cannot_substitute_canonical_fields(self):
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/sap-customer-profile-request/",
            {
                "assigned_to_user_id": str(self.assignee.pk),
                "farmer_full_name": "Forged Borrower",
                "pan_number": "ZZZZZ9999Z",
            },
            content_type="application/json",
            **self._auth(self.credit_manager),
        )
        self.assertEqual(response.status_code, 400, response.content)
        payload = response.json()
        assert_error_envelope(self, payload, "VALIDATION_ERROR")
        self.assertEqual(payload["error"]["field_errors"], {
            "farmer_full_name": "Unknown field.", "pan_number": "Unknown field."
        })
        self._assert_no_sap_artifacts()

    def _terminal_application(
        self, suffix="001", member_type="individual_farmer",
        pan="ABCDE1234F", aadhaar="123412341234",
    ):
        member = Member.objects.create(
            member_number=f"MEM-SAP-{suffix}",
            member_type=member_type,
            legal_name=f"Ramesh Patil {suffix}" if suffix != "001" else "Ramesh Patil",
            display_name=f"Ramesh Patil {suffix}" if suffix != "001" else "Ramesh Patil",
            folio_number=f"FOL-SAP-{suffix}",
            membership_status="active",
            pan_encrypted=FieldEncryption.encrypt("members.pan", pan),
            pan_hash=f"sap-pan-hash-{suffix}",
            aadhaar_encrypted=(
                FieldEncryption.encrypt("members.aadhaar", aadhaar) if aadhaar else ""
            ),
            aadhaar_hash=f"sap-aadhaar-hash-{suffix}" if aadhaar else "",
            registered_address_line1="Village Road",
            registered_village_city="Nashik",
            registered_district="Nashik",
            registered_state="Maharashtra",
            registered_pincode="422001",
            mobile_number=f"9000000{len(str(suffix)):03d}",
            email=f"ramesh-{suffix}@example.com",
            kyc_status="verified",
            default_status="no_default",
        )
        application = LoanApplication.objects.create(
            application_reference_number=("LO00000025" if suffix == "001" else f"LO-{suffix}"),
            member=member,
            borrower_type=member_type,
            received_by_user=self.credit_manager,
            created_by_user=self.credit_manager,
            required_loan_amount="400000.00",
            requested_tenure_months=12,
            declared_purpose="Seasonal crop finance",
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=LoanApplication.STATUS_APPROVED_BY_SANCTION,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
            terms_acceptance_flag=True,
        )
        risk = RiskAssessment.objects.create(
            loan_application=application,
            market_risk_rating="low",
            operational_risk_rating="low",
            borrower_risk_rating="low",
            overall_risk_rating="low",
            assessed_by_user=self.credit_manager,
        )
        note = LoanAppraisalNote.objects.create(
            loan_application=application,
            prepared_by_user=self.credit_manager,
            reviewed_by_user=self.credit_manager,
            reviewed_at=timezone.now(),
            last_review_decision="reviewed",
            tat_due_at=timezone.now(),
            tat_status=LoanAppraisalNote.TAT_WITHIN,
            eligibility_assessment_id_snapshot="10000000-0000-0000-0000-000000000001",
            loan_limit_assessment_id_snapshot="20000000-0000-0000-0000-000000000002",
            eligibility_snapshot_json={"overall_result": "eligible"},
            loan_limit_snapshot_json={"final_eligible_loan_amount": "400000.00"},
            prerequisite_provenance="verified",
            borrower_summary="No prior borrowing.",
            eligibility_summary="Eligible.",
            loan_limit_summary="Within limit.",
            recommended_amount="400000.00",
            recommended_tenure_months=12,
            recommended_interest_type="floating",
            recommended_security_summary="Standard member security package.",
            repayment_capacity_notes="Adequate.",
            risk_assessment=risk,
            recommendation="approve",
            appraisal_status=LoanAppraisalNote.STATUS_SUBMITTED_TO_SANCTION,
        )
        case = ApprovalCase.objects.create(
            loan_application=application,
            loan_appraisal_note=note,
            submitted_by_user=self.credit_manager,
            submission_remarks="Approved SAP request source facts.",
            current_status=ApprovalCase.STATUS_APPROVED,
            amount="400000.00",
            related_entity_type="loan_application",
            related_entity_id=application.pk,
            reason_for_approval="Approved by sanction committee.",
            closed_at=timezone.now(),
        )
        SanctionDecision.objects.create(
            loan_application=application,
            approval_case=case,
            decision="sanctioned",
            sanctioned_amount="400000.00",
            sanctioned_tenure_months=12,
            interest_rate_type="floating",
            security_required_summary="Standard member security package.",
            decision_reason="Approved.",
        )
        return application

    def _post_request(
        self, request_id, *, application=None, application_id=None,
        assigned_to=None, actor=None,
    ):
        application_id = application_id or (application or self.application).pk
        return self.client.post(
            f"/api/v1/loan-applications/{application_id}/sap-customer-profile-request/",
            {"assigned_to_user_id": str((assigned_to or self.assignee).pk)},
            content_type="application/json",
            HTTP_X_REQUEST_ID=request_id,
            **self._auth(actor or self.credit_manager),
        )

    def _assert_no_sap_artifacts(self):
        self.assertEqual(SapCustomerProfileRequest.objects.count(), 0)
        self.assertEqual(DocumentFile.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="finance.sap_customer_code.requested").count(), 0
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="SAPCustomerCodeRequested").count(), 0
        )

    @staticmethod
    def _worksheet_values(workbook):
        with zipfile.ZipFile(BytesIO(workbook)) as archive:
            root = ElementTree.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        namespace = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        return [
            [cell.findtext("x:is/x:t", default="", namespaces=namespace) for cell in row]
            for row in root.findall("x:sheetData/x:row", namespace)
        ]

    def _user(self, role_code, full_name, *permission_codes):
        role, _ = Role.objects.get_or_create(
            role_code=role_code,
            defaults={"role_name": full_name, "status": "active"},
        )
        for code in permission_codes:
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "finance",
                    "risk_level": "high",
                },
            )
            RolePermission.objects.get_or_create(role=role, permission=permission)
        user = User.objects.create(
            full_name=full_name,
            email=f"{role_code}-{User.objects.count()}@sfpcl.example",
            status="active",
            primary_role=role,
        )
        user.set_password(self.password)
        user.save()
        return user

    def _auth(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.json())
        return {
            "HTTP_AUTHORIZATION": f"Bearer {response.json()['data']['access_token']}"
        }


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class SapCustomerProfileRequestRaceTests(TransactionTestCase):
    reset_sequences = True
    password = SapCustomerProfileRequestApiTests.password

    def setUp(self):
        self.storage = tempfile.TemporaryDirectory()
        self.settings = override_settings(DOCUMENT_STORAGE_ROOT=self.storage.name)
        self.settings.enable()
        self.credit_manager = SapCustomerProfileRequestApiTests._user(
            self, "credit_manager", "SAP Race Credit Manager", "finance.sap_request.create"
        )
        self.assignee = SapCustomerProfileRequestApiTests._user(
            self, "senior_manager_finance", "SAP Race Senior Manager Finance"
        )

    def tearDown(self):
        self.settings.disable()
        self.storage.cleanup()

    def test_five_caller_race_has_one_request_file_and_evidence_winner_twice(self):
        for round_number in range(2):
            application = SapCustomerProfileRequestApiTests._terminal_application(
                self, suffix=f"RACE-{round_number}"
            )
            barrier = Barrier(5)

            def create(index):
                close_old_connections()
                try:
                    actor = User.objects.get(pk=self.credit_manager.pk)
                    request = RequestFactory().post(
                        "/sap-request/", HTTP_X_REQUEST_ID=f"race-{round_number}-{index}"
                    )
                    barrier.wait(timeout=10)
                    return create_request(
                        actor=actor,
                        application_id=application.pk,
                        payload={"assigned_to_user_id": str(self.assignee.pk)},
                        request=request,
                    )
                finally:
                    close_old_connections()

            with ThreadPoolExecutor(max_workers=5) as pool:
                results = list(pool.map(create, range(5)))
            self.assertEqual(
                len({item["sap_customer_profile_request_id"] for item in results}), 1
            )
            self.assertEqual(SapCustomerProfileRequest.objects.count(), round_number + 1)
            self.assertEqual(DocumentFile.objects.count(), round_number + 1)
            self.assertEqual(
                AuditLog.objects.filter(action="finance.sap_customer_code.requested").count(),
                round_number + 1,
            )
            self.assertEqual(
                WorkflowEvent.objects.filter(workflow_name="SAPCustomerCodeRequested").count(),
                round_number + 1,
            )
