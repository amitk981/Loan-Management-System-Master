import json
from uuid import uuid4

from django.test import Client, TestCase

from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import BankAccount, CancelledCheque, CropPlan, LandHolding, Member
from sfpcl_credit.tests.api_contracts import assert_error_envelope, assert_success_envelope
from sfpcl_credit.workflows.models import WorkflowEvent


APPLICATION_READ_PERMISSION = "applications.loan_application.read"
APPLICATION_CREATE_PERMISSION = "applications.loan_application.create"
APPLICATION_UPDATE_PERMISSION = "applications.loan_application.update"
APPLICATION_SUBMIT_PERMISSION = "applications.loan_application.submit"


class LoanApplicationDraftApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.read_permission = self._permission(APPLICATION_READ_PERMISSION, "View applications")
        self.create_permission = self._permission(
            APPLICATION_CREATE_PERMISSION,
            "Create loan application",
        )
        self.update_permission = self._permission(
            APPLICATION_UPDATE_PERMISSION,
            "Update draft application",
        )
        self.submit_permission = self._permission(
            APPLICATION_SUBMIT_PERMISSION,
            "Submit loan application",
        )
        self.creator = self._user(
            "applications.creator@sfpcl.example",
            "CreatorPass123!",
            self.read_permission,
            self.create_permission,
            self.update_permission,
            self.submit_permission,
        )
        self.reader = self._user(
            "applications.reader@sfpcl.example",
            "ReaderPass123!",
            self.read_permission,
        )
        self.plain = self._user("applications.plain@sfpcl.example", "PlainPass123!")
        self.member = self._member("005A", "Ramesh Patil")
        self.other_member = self._member("005A-OTHER", "Sita Farms")
        self.land = LandHolding.objects.create(
            member=self.member,
            document_type="7_12_extract",
            survey_number="123/4",
            village="Niphad",
            area_acres="5.00",
            document_id=uuid4(),
        )
        self.crop = CropPlan.objects.create(
            member=self.member,
            crop_type="grapes",
            season="FY2026 Kharif",
            planned_area_acres="5.00",
            estimated_cost_amount="100000.00",
            loan_purpose_alignment="agriculture_aligned",
            document_id=uuid4(),
        )
        self.cheque = CancelledCheque.objects.create(
            member=self.member,
            document_id=uuid4(),
            account_number_encrypted="cheque-token-123456789012",
            account_number_hash="cheque-hash-123456789012",
            account_number_last4="9012",
            ifsc="HDFC0001234",
            branch_name="Nashik Road",
        )
        self.bank = BankAccount.objects.create(
            owner_party_type="member",
            owner_party_id=self.member.member_id,
            account_holder_name="Ramesh Patil",
            account_number_encrypted="bank-token-123456789012",
            account_number_hash="bank-hash-123456789012",
            account_number_last4="9012",
            ifsc="HDFC0001234",
            bank_name="HDFC Bank",
            branch_name="Nashik Road",
            cancelled_cheque=self.cheque,
        )

    def test_create_and_read_draft_returns_metadata_only_response_and_audit(self):
        response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(),
            content_type="application/json",
            headers={
                **self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
                "X-Request-ID": "req-create-loan-draft",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        self.assertEqual(body["meta"]["request_id"], "req-create-loan-draft")
        draft = body["data"]
        self.assertEqual(draft["application_status"], "draft")
        self.assertEqual(draft["current_stage"], "initial_loan_request")
        self.assertIsNone(draft["application_reference_number"])
        self.assertEqual(draft["member"]["member_id"], str(self.member.member_id))
        self.assertEqual(draft["member"]["display_name"], "Ramesh Patil")
        self.assertEqual(draft["required_loan_amount"], "400000.00")
        self.assertEqual(draft["requested_tenure_months"], 12)
        self.assertEqual(draft["declared_purpose"], "Crop production loan for grape cultivation")
        self.assertEqual(draft["purpose_category"], "crop_production")
        self.assertEqual(draft["land_holding"]["land_holding_id"], str(self.land.land_holding_id))
        self.assertEqual(draft["crop_plan"]["crop_plan_id"], str(self.crop.crop_plan_id))
        self.assertEqual(draft["bank_account"]["bank_account_id"], str(self.bank.bank_account_id))
        self.assertEqual(draft["bank_account"]["account_holder_name"], "Ramesh Patil")
        self.assertEqual(draft["bank_account"]["account_number"]["masked"], "********9012")
        self.assertFalse(draft["bank_account"]["account_number"]["can_view_full"])
        self.assertEqual(
            draft["cancelled_cheque"]["cancelled_cheque_id"],
            str(self.cheque.cancelled_cheque_id),
        )

        read_response = self.client.get(
            f"/api/v1/loan-applications/{draft['loan_application_id']}/",
            headers=self._headers("applications.reader@sfpcl.example", "ReaderPass123!"),
        )

        self.assertEqual(read_response.status_code, 200)
        read_body = read_response.json()
        assert_success_envelope(self, read_body)
        self.assertEqual(read_body["data"], draft)

        audit = AuditLog.objects.filter(action="applications.loan_application.created").get()
        self.assertEqual(audit.entity_type, "loan_application")
        self.assertEqual(str(audit.entity_id), draft["loan_application_id"])
        self.assertEqual(audit.new_value_json["member_id"], str(self.member.member_id))
        self.assertEqual(audit.new_value_json["bank_account_id"], str(self.bank.bank_account_id))
        self.assertEqual(audit.new_value_json["masked_bank_account_number"], "********9012")

        workflow_event = WorkflowEvent.objects.filter(entity_type="loan_application").get()
        self.assertEqual(str(workflow_event.entity_id), draft["loan_application_id"])
        self.assertEqual(workflow_event.workflow_name, "loan_application")
        self.assertIsNone(workflow_event.from_state)
        self.assertEqual(workflow_event.to_state, "draft")

        flattened = f"{body} {audit.new_value_json}"
        self.assertNotIn("member-pan-token", flattened)
        self.assertNotIn("member-aadhaar-token", flattened)
        self.assertNotIn("bank-token-123456789012", flattened)
        self.assertNotIn("bank-hash-123456789012", flattened)
        self.assertNotIn("cheque-token-123456789012", flattened)
        self.assertNotIn("cheque-hash-123456789012", flattened)
        self.assertNotIn("123456789012", flattened)
        self.assertNotIn('"holder_name"', json.dumps(body))

    def test_submit_draft_transitions_to_submitted_and_records_metadata_only_evidence(self):
        create_response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(create_response.status_code, 200)
        draft = create_response.json()["data"]

        response = self.client.post(
            f"/api/v1/loan-applications/{draft['loan_application_id']}/submit/",
            data={"submission_notes": "Application form signed by applicant."},
            content_type="application/json",
            headers={
                **self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
                "X-Request-ID": "req-submit-loan-application",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        submitted = body["data"]
        self.assertEqual(submitted["loan_application_id"], draft["loan_application_id"])
        self.assertEqual(submitted["application_status"], "submitted")
        self.assertEqual(submitted["current_stage"], "initial_loan_request")
        self.assertEqual(submitted["completeness_status"], "not_started")
        self.assertIsNone(submitted["application_reference_number"])
        self.assertIsNotNone(submitted["submitted_at"])
        self.assertEqual(submitted["submitted_by_user_id"], str(self.creator.user_id))
        self.assertEqual(submitted["bank_account"]["account_holder_name"], "Ramesh Patil")
        self.assertEqual(submitted["bank_account"]["account_number"]["masked"], "********9012")
        self.assertFalse(submitted["bank_account"]["account_number"]["can_view_full"])

        read_response = self.client.get(
            f"/api/v1/loan-applications/{draft['loan_application_id']}/",
            headers=self._headers("applications.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(read_response.json()["data"], submitted)

        audit = AuditLog.objects.filter(action="applications.loan_application.submitted").get()
        self.assertEqual(str(audit.entity_id), draft["loan_application_id"])
        self.assertEqual(audit.old_value_json["application_status"], "draft")
        self.assertEqual(audit.new_value_json["application_status"], "submitted")
        self.assertEqual(audit.new_value_json["request_id"], "req-submit-loan-application")
        self.assertEqual(audit.new_value_json["masked_bank_account_number"], "********9012")

        workflow_event = WorkflowEvent.objects.filter(
            entity_type="loan_application",
            from_state="draft",
            to_state="submitted",
        ).get()
        self.assertEqual(str(workflow_event.entity_id), draft["loan_application_id"])
        self.assertEqual(workflow_event.workflow_name, "loan_application")

        flattened = f"{body} {audit.old_value_json} {audit.new_value_json}"
        self.assertNotIn("member-pan-token", flattened)
        self.assertNotIn("member-aadhaar-token", flattened)
        self.assertNotIn("bank-token-123456789012", flattened)
        self.assertNotIn("bank-hash-123456789012", flattened)
        self.assertNotIn("cheque-token-123456789012", flattened)
        self.assertNotIn("cheque-hash-123456789012", flattened)
        self.assertNotIn("123456789012", flattened)

    def test_patch_updates_allowed_draft_fields_and_rejects_cross_member_references(self):
        create_response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(create_response.status_code, 200)
        application_id = create_response.json()["data"]["loan_application_id"]
        other_bank = BankAccount.objects.create(
            owner_party_type="member",
            owner_party_id=self.other_member.member_id,
            account_holder_name="Sita Farms",
            account_number_encrypted="other-bank-token-999900001111",
            account_number_hash="other-bank-hash-999900001111",
            account_number_last4="1111",
            ifsc="SBIN0000456",
        )

        bad_response = self.client.patch(
            f"/api/v1/loan-applications/{application_id}/",
            data={"bank_account_id": str(other_bank.bank_account_id)},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(bad_response.status_code, 400)
        bad_body = bad_response.json()
        assert_error_envelope(self, bad_body, "VALIDATION_ERROR")
        self.assertIn("bank_account_id", bad_body["error"]["field_errors"])

        good_response = self.client.patch(
            f"/api/v1/loan-applications/{application_id}/",
            data={
                "required_loan_amount": "450000.00",
                "requested_tenure_months": 18,
                "declared_purpose": "Updated crop production loan purpose",
                "borrower_request_notes": "Updated notes",
            },
            content_type="application/json",
            headers={
                **self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
                "X-Request-ID": "req-update-loan-draft",
            },
        )

        self.assertEqual(good_response.status_code, 200)
        body = good_response.json()
        assert_success_envelope(self, body)
        draft = body["data"]
        self.assertEqual(draft["loan_application_id"], application_id)
        self.assertEqual(draft["member"]["member_id"], str(self.member.member_id))
        self.assertEqual(draft["required_loan_amount"], "450000.00")
        self.assertEqual(draft["requested_tenure_months"], 18)
        self.assertEqual(draft["declared_purpose"], "Updated crop production loan purpose")
        self.assertEqual(draft["borrower_request_notes"], "Updated notes")
        self.assertEqual(draft["bank_account"]["bank_account_id"], str(self.bank.bank_account_id))

        update_audit = AuditLog.objects.filter(
            action="applications.loan_application.updated"
        ).get()
        self.assertEqual(str(update_audit.entity_id), application_id)
        self.assertEqual(update_audit.new_value_json["required_loan_amount"], "450000.00")
        self.assertEqual(update_audit.new_value_json["request_id"], "req-update-loan-draft")
        self.assertEqual(WorkflowEvent.objects.filter(entity_type="loan_application").count(), 1)

    def test_submit_enforces_permissions_required_facts_and_draft_only_transition(self):
        draft_response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(draft_response.status_code, 200)
        application_id = draft_response.json()["data"]["loan_application_id"]

        no_submit_permission = self.client.post(
            f"/api/v1/loan-applications/{application_id}/submit/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertEqual(no_submit_permission.status_code, 403)
        assert_error_envelope(self, no_submit_permission.json(), "PERMISSION_DENIED")

        missing_application = self.client.post(
            f"/api/v1/loan-applications/{uuid4()}/submit/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(missing_application.status_code, 404)
        assert_error_envelope(self, missing_application.json(), "NOT_FOUND")

        incomplete_response = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(
                required_loan_amount="",
                declared_purpose="",
                purpose_category="",
            ),
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(incomplete_response.status_code, 200)
        incomplete_id = incomplete_response.json()["data"]["loan_application_id"]
        incomplete_submit = self.client.post(
            f"/api/v1/loan-applications/{incomplete_id}/submit/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(incomplete_submit.status_code, 400)
        incomplete_body = incomplete_submit.json()
        assert_error_envelope(self, incomplete_body, "VALIDATION_ERROR")
        self.assertIn("required_loan_amount", incomplete_body["error"]["field_errors"])
        self.assertIn("declared_purpose", incomplete_body["error"]["field_errors"])
        self.assertIn("purpose_category", incomplete_body["error"]["field_errors"])

        first_submit = self.client.post(
            f"/api/v1/loan-applications/{application_id}/submit/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(first_submit.status_code, 200)

        second_submit = self.client.post(
            f"/api/v1/loan-applications/{application_id}/submit/",
            data={},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(second_submit.status_code, 409)
        assert_error_envelope(self, second_submit.json(), "INVALID_STATE_TRANSITION")

        patch_submitted = self.client.patch(
            f"/api/v1/loan-applications/{application_id}/",
            data={"borrower_request_notes": "Attempt edit after submit"},
            content_type="application/json",
            headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(patch_submitted.status_code, 400)
        patch_body = patch_submitted.json()
        assert_error_envelope(self, patch_body, "VALIDATION_ERROR")
        self.assertIn("application_status", patch_body["error"]["field_errors"])

    def test_draft_endpoints_enforce_permissions_and_validation(self):
        unauthenticated = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(),
            content_type="application/json",
        )
        self.assertEqual(unauthenticated.status_code, 401)
        assert_error_envelope(self, unauthenticated.json(), "AUTH_REQUIRED")

        no_create = self.client.post(
            "/api/v1/loan-applications/",
            data=self._draft_payload(),
            content_type="application/json",
            headers=self._headers("applications.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertEqual(no_create.status_code, 403)
        assert_error_envelope(self, no_create.json(), "PERMISSION_DENIED")

        plain = self.client.get(
            f"/api/v1/loan-applications/{uuid4()}/",
            headers=self._headers("applications.plain@sfpcl.example", "PlainPass123!"),
        )
        self.assertEqual(plain.status_code, 403)
        assert_error_envelope(self, plain.json(), "PERMISSION_DENIED")

        cases = [
            ({"member_id": str(uuid4())}, "member_id"),
            ({"member_id": "not-a-uuid"}, "member_id"),
            ({"required_loan_amount": "0"}, "required_loan_amount"),
            ({"required_loan_amount": "-1.00"}, "required_loan_amount"),
            ({"land_holding_id": "not-a-uuid"}, "land_holding_id"),
            ({"crop_plan_id": "not-a-uuid"}, "crop_plan_id"),
            ({"bank_account_id": "not-a-uuid"}, "bank_account_id"),
            ({"cancelled_cheque_id": "not-a-uuid"}, "cancelled_cheque_id"),
        ]
        for override, field in cases:
            with self.subTest(override=override):
                response = self.client.post(
                    "/api/v1/loan-applications/",
                    data=self._draft_payload(**override),
                    content_type="application/json",
                    headers=self._headers("applications.creator@sfpcl.example", "CreatorPass123!"),
                )
                self.assertEqual(response.status_code, 400)
                body = response.json()
                assert_error_envelope(self, body, "VALIDATION_ERROR")
                self.assertIn(field, body["error"]["field_errors"])

    def _draft_payload(self, **overrides):
        payload = {
            "member_id": str(self.member.member_id),
            "required_loan_amount": "400000.00",
            "requested_tenure_months": 12,
            "declared_purpose": "Crop production loan for grape cultivation",
            "purpose_category": "crop_production",
            "loan_type_requested": "short_term",
            "land_holding_id": str(self.land.land_holding_id),
            "crop_plan_id": str(self.crop.crop_plan_id),
            "bank_account_id": str(self.bank.bank_account_id),
            "cancelled_cheque_id": str(self.cheque.cancelled_cheque_id),
            "borrower_request_notes": "Borrower prefers assisted digital intake.",
            "terms_acceptance_flag": False,
        }
        payload.update(overrides)
        return payload

    def _permission(self, code, name):
        return Permission.objects.create(
            permission_code=code,
            permission_name=name,
            module_name=code.split(".")[0],
            risk_level="high",
        )

    def _user(self, email, password, *permissions):
        role = Role.objects.create(
            role_code=email.split("@")[0].replace(".", "_"),
            role_name=email,
            is_system_role=True,
            status="active",
        )
        for permission in permissions:
            RolePermission.objects.create(role=role, permission=permission)
        user = User.objects.create(full_name=email, email=email, status="active", primary_role=role)
        user.set_password(password)
        user.save()
        return user

    def _token(self, email, password):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": email, "password": password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["access_token"]

    def _headers(self, email, password):
        return {"Authorization": f"Bearer {self._token(email, password)}"}

    def _member(self, suffix, display_name):
        return Member.objects.create(
            member_number=f"MEM-{suffix}",
            member_type="individual_farmer",
            legal_name=display_name,
            display_name=display_name,
            folio_number=f"FOL-{suffix}",
            membership_status="active",
            pan_encrypted=f"{suffix}-member-pan-token",
            pan_hash=f"{suffix}-member-pan-hash",
            aadhaar_encrypted=f"{suffix}-member-aadhaar-token",
            aadhaar_hash=f"{suffix}-member-aadhaar-hash",
            kyc_status="verified",
            default_status="no_default",
        )
