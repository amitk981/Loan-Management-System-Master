from uuid import uuid4

from django.test import Client, TestCase

from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import BankAccount, CancelledCheque, Member
from sfpcl_credit.tests.api_contracts import (
    assert_error_envelope,
    assert_pagination_shape,
    assert_success_envelope,
)
from sfpcl_credit.workflows.models import WorkflowEvent


MEMBER_READ_PERMISSION = "members.member.read"
MEMBER_UPDATE_PERMISSION = "members.member.update"


class MemberBankAccountApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.read_permission = Permission.objects.create(
            permission_code=MEMBER_READ_PERMISSION,
            permission_name="View members",
            module_name="members",
            risk_level="medium",
        )
        self.update_permission = Permission.objects.create(
            permission_code=MEMBER_UPDATE_PERMISSION,
            permission_name="Update members",
            module_name="members",
            risk_level="high",
        )
        self.reader = self._user(
            "bank.reader@sfpcl.example",
            "ReaderPass123!",
            self.read_permission,
        )
        self.creator = self._user(
            "bank.creator@sfpcl.example",
            "CreatorPass123!",
            self.update_permission,
        )
        self.reader_creator = self._user(
            "bank.full@sfpcl.example",
            "FullPass123!",
            self.read_permission,
            self.update_permission,
        )
        self.plain = self._user("bank.plain@sfpcl.example", "PlainPass123!")
        self.member = Member.objects.create(
            member_number="MEM-004J",
            member_type="individual_farmer",
            legal_name="Ramesh Patil",
            display_name="Ramesh Patil",
            folio_number="FOL-004J",
            membership_status="active",
            pan_encrypted="member-pan-token",
            pan_hash="member-pan-hash-004j",
            aadhaar_encrypted="member-aadhaar-token",
            aadhaar_hash="member-aadhaar-hash-004j",
            kyc_status="verified",
            default_status="no_default",
        )

    def test_bank_account_can_be_created_and_listed_with_masked_number(self):
        response = self.client.post(
            self._bank_accounts_url(),
            data=self._bank_account_payload(),
            content_type="application/json",
            headers={
                **self._headers("bank.full@sfpcl.example", "FullPass123!"),
                "X-Request-ID": "req-create-bank-account",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        self.assertEqual(body["meta"]["request_id"], "req-create-bank-account")
        bank_account = body["data"]
        self.assertEqual(bank_account["account_holder_name"], "Ramesh Patil")
        self.assertEqual(bank_account["account_number"]["masked"], "********9012")
        self.assertEqual(bank_account["account_number"]["last4"], "9012")
        self.assertFalse(bank_account["account_number"]["can_view_full"])
        self.assertEqual(bank_account["ifsc"], "HDFC0001234")
        self.assertEqual(bank_account["bank_name"], "HDFC Bank")
        self.assertEqual(bank_account["branch_name"], "Nashik Road")
        self.assertEqual(bank_account["verification_status"], "pending")
        self.assertIsNone(bank_account["cancelled_cheque_id"])
        self.assertIsNone(bank_account["signature_verified_flag"])
        self.assertEqual(bank_account["status"], "active")
        self.assertNotIn("account_number_encrypted", bank_account)
        self.assertNotIn("account_number_hash", bank_account)

        persisted = BankAccount.objects.get(
            bank_account_id=bank_account["bank_account_id"]
        )
        self.assertEqual(str(persisted.owner_party_id), str(self.member.member_id))
        self.assertEqual(persisted.owner_party_type, "member")
        self.assertNotEqual(persisted.account_number_encrypted, "123456789012")
        self.assertNotIn("123456789012", persisted.account_number_encrypted)
        self.assertNotEqual(persisted.account_number_hash, "123456789012")
        self.assertEqual(persisted.account_number_last4, "9012")

        list_response = self.client.get(
            self._bank_accounts_url(),
            headers=self._headers("bank.reader@sfpcl.example", "ReaderPass123!"),
        )

        self.assertEqual(list_response.status_code, 200)
        list_body = list_response.json()
        assert_pagination_shape(self, list_body)
        self.assertEqual(list_body["pagination"]["total_count"], 1)
        self.assertEqual(
            list_body["data"][0]["bank_account_id"],
            bank_account["bank_account_id"],
        )
        self.assertEqual(list_body["data"][0]["account_number"]["masked"], "********9012")

    def test_cancelled_cheque_can_be_created_and_listed_with_masked_number(self):
        response = self.client.post(
            self._cancelled_cheques_url(),
            data=self._cancelled_cheque_payload(),
            content_type="application/json",
            headers=self._headers("bank.full@sfpcl.example", "FullPass123!"),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        assert_success_envelope(self, body)
        cheque = body["data"]
        self.assertEqual(cheque["document_id"], self.cheque_document_id)
        self.assertEqual(cheque["account_number"]["masked"], "********4321")
        self.assertEqual(cheque["account_number"]["last4"], "4321")
        self.assertFalse(cheque["account_number"]["can_view_full"])
        self.assertEqual(cheque["ifsc"], "SBIN0000456")
        self.assertEqual(cheque["branch_name"], "Lasalgaon")
        self.assertEqual(cheque["verification_status"], "pending")
        self.assertEqual(cheque["signature_mismatch_flag"], False)
        self.assertNotIn("account_number_encrypted", cheque)
        self.assertNotIn("account_number_hash", cheque)

        persisted = CancelledCheque.objects.get(
            cancelled_cheque_id=cheque["cancelled_cheque_id"]
        )
        self.assertEqual(str(persisted.member_id), str(self.member.member_id))
        self.assertIsNone(persisted.loan_application_id)
        self.assertNotIn("987654324321", persisted.account_number_encrypted)

        list_response = self.client.get(
            self._cancelled_cheques_url(),
            headers=self._headers("bank.reader@sfpcl.example", "ReaderPass123!"),
        )

        self.assertEqual(list_response.status_code, 200)
        list_body = list_response.json()
        assert_pagination_shape(self, list_body)
        self.assertEqual(list_body["pagination"]["total_count"], 1)
        self.assertEqual(
            list_body["data"][0]["cancelled_cheque_id"],
            cheque["cancelled_cheque_id"],
        )

    def test_bank_metadata_endpoints_require_authentication_and_separate_member_permissions(self):
        for url in (self._bank_accounts_url(), self._cancelled_cheques_url()):
            with self.subTest(url=url):
                unauthenticated = self.client.get(url)
                self.assertEqual(unauthenticated.status_code, 401)
                assert_error_envelope(self, unauthenticated.json(), "AUTH_REQUIRED")

                no_read = self.client.get(
                    url,
                    headers=self._headers("bank.creator@sfpcl.example", "CreatorPass123!"),
                )
                self.assertEqual(no_read.status_code, 403)
                assert_error_envelope(self, no_read.json(), "PERMISSION_DENIED")

                no_create = self.client.post(
                    url,
                    data=(
                        self._bank_account_payload()
                        if "bank-accounts" in url
                        else self._cancelled_cheque_payload()
                    ),
                    content_type="application/json",
                    headers=self._headers("bank.reader@sfpcl.example", "ReaderPass123!"),
                )
                self.assertEqual(no_create.status_code, 403)
                assert_error_envelope(self, no_create.json(), "PERMISSION_DENIED")

                plain = self.client.post(
                    url,
                    data=(
                        self._bank_account_payload()
                        if "bank-accounts" in url
                        else self._cancelled_cheque_payload()
                    ),
                    content_type="application/json",
                    headers=self._headers("bank.plain@sfpcl.example", "PlainPass123!"),
                )
                self.assertEqual(plain.status_code, 403)
                assert_error_envelope(self, plain.json(), "PERMISSION_DENIED")

    def test_bank_metadata_endpoints_return_not_found_for_unknown_or_deleted_member(self):
        for url_factory in (self._bank_accounts_url, self._cancelled_cheques_url):
            for member_id in (uuid4(), self._deleted_member().member_id):
                with self.subTest(url=url_factory, member_id=member_id):
                    response = self.client.get(
                        url_factory(member_id),
                        headers=self._headers("bank.reader@sfpcl.example", "ReaderPass123!"),
                    )
                    self.assertEqual(response.status_code, 404)
                    assert_error_envelope(self, response.json(), "NOT_FOUND")

    def test_bank_account_create_rejects_required_and_unsupported_values(self):
        cases = [
            ({"account_holder_name": ""}, "account_holder_name"),
            ({"account_number": ""}, "account_number"),
            ({"account_number": "12"}, "account_number"),
            ({"ifsc": ""}, "ifsc"),
            ({"verification_status": "approved"}, "verification_status"),
            ({"status": "closed"}, "status"),
            ({"cancelled_cheque_id": "not-a-uuid"}, "cancelled_cheque_id"),
            ({"cancelled_cheque_id": str(uuid4())}, "cancelled_cheque_id"),
        ]
        for override, field in cases:
            with self.subTest(override=override):
                response = self.client.post(
                    self._bank_accounts_url(),
                    data=self._bank_account_payload(**override),
                    content_type="application/json",
                    headers=self._headers("bank.creator@sfpcl.example", "CreatorPass123!"),
                )

                self.assertEqual(response.status_code, 400)
                body = response.json()
                assert_error_envelope(self, body, "VALIDATION_ERROR")
                self.assertIn(field, body["error"]["field_errors"])

    def test_cancelled_cheque_create_rejects_required_and_unsupported_values(self):
        cases = [
            ({"document_id": ""}, "document_id"),
            ({"document_id": "not-a-uuid"}, "document_id"),
            ({"account_number": ""}, "account_number"),
            ({"account_number": "abc"}, "account_number"),
            ({"ifsc": ""}, "ifsc"),
            ({"verification_status": "approved"}, "verification_status"),
            ({"loan_application_id": "not-a-uuid"}, "loan_application_id"),
        ]
        for override, field in cases:
            with self.subTest(override=override):
                response = self.client.post(
                    self._cancelled_cheques_url(),
                    data=self._cancelled_cheque_payload(**override),
                    content_type="application/json",
                    headers=self._headers("bank.creator@sfpcl.example", "CreatorPass123!"),
                )

                self.assertEqual(response.status_code, 400)
                body = response.json()
                assert_error_envelope(self, body, "VALIDATION_ERROR")
                self.assertIn(field, body["error"]["field_errors"])

    def test_bank_metadata_creates_audit_metadata_without_workflow_event_or_sensitive_values(self):
        bank_response = self.client.post(
            self._bank_accounts_url(),
            data=self._bank_account_payload(account_number="1111222233334444"),
            content_type="application/json",
            headers=self._headers("bank.creator@sfpcl.example", "CreatorPass123!"),
        )
        cheque_response = self.client.post(
            self._cancelled_cheques_url(),
            data=self._cancelled_cheque_payload(account_number="5555666677778888"),
            content_type="application/json",
            headers=self._headers("bank.creator@sfpcl.example", "CreatorPass123!"),
        )

        self.assertEqual(bank_response.status_code, 200)
        self.assertEqual(cheque_response.status_code, 200)
        bank_id = bank_response.json()["data"]["bank_account_id"]
        cheque_id = cheque_response.json()["data"]["cancelled_cheque_id"]

        bank_audit = AuditLog.objects.filter(action="members.bank_account.created").get()
        self.assertEqual(str(bank_audit.entity_id), bank_id)
        self.assertEqual(bank_audit.entity_type, "bank_account")
        self.assertEqual(bank_audit.new_value_json["member_id"], str(self.member.member_id))
        self.assertEqual(bank_audit.new_value_json["masked_account_number"], "************4444")
        self.assertEqual(bank_audit.new_value_json["account_number_last4"], "4444")

        cheque_audit = AuditLog.objects.filter(
            action="members.cancelled_cheque.created"
        ).get()
        self.assertEqual(str(cheque_audit.entity_id), cheque_id)
        self.assertEqual(cheque_audit.entity_type, "cancelled_cheque")
        self.assertEqual(cheque_audit.new_value_json["member_id"], str(self.member.member_id))
        self.assertEqual(cheque_audit.new_value_json["masked_account_number"], "************8888")
        self.assertEqual(cheque_audit.new_value_json["account_number_last4"], "8888")

        for audit in (bank_audit, cheque_audit):
            flattened = str(audit.new_value_json)
            self.assertNotIn("1111222233334444", flattened)
            self.assertNotIn("5555666677778888", flattened)
            self.assertNotIn("account_number_encrypted", flattened)
            self.assertNotIn("account_number_hash", flattened)
        self.assertEqual(WorkflowEvent.objects.count(), 0)

    def _bank_account_payload(self, **overrides):
        payload = {
            "account_holder_name": "Ramesh Patil",
            "account_number": "123456789012",
            "ifsc": "HDFC0001234",
            "bank_name": "HDFC Bank",
            "branch_name": "Nashik Road",
            "verification_status": "pending",
            "signature_verified_flag": None,
            "status": "active",
        }
        payload.update(overrides)
        return payload

    def _cancelled_cheque_payload(self, **overrides):
        self.cheque_document_id = getattr(self, "cheque_document_id", str(uuid4()))
        payload = {
            "loan_application_id": None,
            "document_id": self.cheque_document_id,
            "account_number": "987654324321",
            "ifsc": "SBIN0000456",
            "branch_name": "Lasalgaon",
            "verification_status": "pending",
            "signature_mismatch_flag": False,
        }
        payload.update(overrides)
        return payload

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

    def _bank_accounts_url(self, member_id=None):
        return f"/api/v1/members/{member_id or self.member.member_id}/bank-accounts/"

    def _cancelled_cheques_url(self, member_id=None):
        return f"/api/v1/members/{member_id or self.member.member_id}/cancelled-cheques/"

    def _deleted_member(self):
        return Member.objects.create(
            member_type="individual_farmer",
            legal_name="Deleted Member",
            display_name="Deleted Member",
            folio_number=f"FOL-{uuid4()}",
            membership_status="inactive",
            pan_encrypted="deleted-pan-token",
            pan_hash=f"deleted-pan-{uuid4()}",
            kyc_status="missing",
            default_status="no_default",
            is_deleted=True,
        )
