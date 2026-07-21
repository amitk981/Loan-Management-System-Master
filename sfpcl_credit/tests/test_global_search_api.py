import json
from contextlib import nullcontext
from unittest.mock import patch

from django.core.cache import cache
from django.test import Client, TestCase
from django.utils import timezone

from sfpcl_credit.applications.models import ApplicationDocument, LoanApplication
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import BankAccount, Member, MemberScopeAssignment
from sfpcl_credit.members.protected_identity import (
    identity_hash,
    protected_identity_token,
)
from sfpcl_credit.tests.api_contracts import assert_error_envelope
from sfpcl_credit.sap_workflow.models import SapCustomerCode
from sfpcl_credit.processes import global_search


class GlobalSearchApiTests(TestCase):
    URL = "/api/v1/global-search/"
    PASSWORD = "SearchPass123!"
    PERMISSIONS = (
        "members.member.read",
        "applications.loan_application.read",
        "finance.loan_account.read",
        "documents.loan_document.read",
        "audit.audit_log.read",
        "compliance.control.read",
    )

    def setUp(self):
        cache.clear()
        self.client = Client()
        role = Role.objects.create(
            role_code="cfo",
            role_name="CFO",
            is_system_role=True,
            status="active",
        )
        for code in self.PERMISSIONS:
            permission = Permission.objects.create(
                permission_code=code,
                permission_name=code,
                module_name=code.split(".", 1)[0],
                risk_level="high",
            )
            RolePermission.objects.create(role=role, permission=permission)
        self.user = User.objects.create(
            full_name="Authorised Searcher",
            email="searcher@sfpcl.example",
            status="active",
            primary_role=role,
        )
        self.user.set_password(self.PASSWORD)
        self.user.save()
        MemberScopeAssignment.objects.create(
            user=self.user,
            permission_code="members.member.read",
            scope_type="global",
        )
        self.pan = "ABCDE1234F"
        self.aadhaar = "123456789012"
        self.member = Member.objects.create(
            member_number="MEM-SEARCH-001",
            member_type="individual_farmer",
            legal_name="Searchable Farmer",
            display_name="Searchable Farmer",
            folio_number="FOL-SEARCH-001",
            membership_status="active",
            pan_encrypted=protected_identity_token(self.pan, 10),
            pan_hash=identity_hash(self.pan),
            aadhaar_encrypted=protected_identity_token(self.aadhaar, 12),
            aadhaar_hash=identity_hash(self.aadhaar),
            aadhaar_last4="9012",
            mobile_number="9876543210",
            email="farmer.search@example.com",
            kyc_status="verified",
            default_status="no_default",
            number_of_shares=125,
            created_by_user=self.user,
            updated_by_user=self.user,
        )
        self.fpc = Member.objects.create(
            member_number="MEM-SEARCH-FPC",
            member_type="fpc",
            legal_name="Searchable Producer Company",
            display_name="Searchable Producer Company",
            folio_number="FOL-SEARCH-FPC",
            membership_status="active",
            pan_encrypted="synthetic-fpc-pan",
            pan_hash="synthetic-fpc-pan-hash",
            aadhaar_encrypted="",
            aadhaar_hash="",
            mobile_number="",
            email="",
            kyc_status="verified",
            default_status="no_default",
            created_by_user=self.user,
        )
        self.application = LoanApplication.objects.create(
            application_reference_number="APP-SEARCH-001",
            member=self.member,
            borrower_type="individual_farmer",
            received_by_user=self.user,
            created_by_user=self.user,
            updated_by_user=self.user,
        )
        SapCustomerCode.objects.create(
            member=self.member,
            sap_customer_code="SAP-SEARCH-001",
            created_for_loan_application=self.application,
            created_by_user=self.user,
        )
        BankAccount.objects.create(
            owner_party_type="member",
            owner_party_id=self.member.member_id,
            account_holder_name=self.member.display_name,
            account_number_encrypted="synthetic-account-token",
            account_number_hash="synthetic-account-hash",
            account_number_last4="7788",
            ifsc="TEST0000001",
        )
        document_file = DocumentFile.objects.create(
            file_name="searchable-application-form.pdf",
            file_extension="pdf",
            mime_type="application/pdf",
            storage_provider="test",
            storage_key="tests/searchable-application-form.pdf",
            sensitivity_level="confidential",
            uploaded_by_user=self.user,
        )
        self.application_document = ApplicationDocument.objects.create(
            loan_application=self.application,
            document_type="loan_application_form",
            party_type="borrower",
            party_id=self.member.member_id,
            document_file=document_file,
            created_by_user=self.user,
            updated_by_user=self.user,
        )
        self.audit = AuditLog.objects.create(
            actor_user=self.user,
            action="members.member.search_fixture_updated",
            entity_type="member",
            entity_id=self.member.member_id,
            new_value_json={"member_id": str(self.member.member_id)},
        )

    def _headers(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": self.user.email, "password": self.PASSWORD},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}

    def _search(self, search, **payload):
        return self.client.post(
            self.URL,
            data=json.dumps({"search": search, **payload}),
            content_type="application/json",
            headers=self._headers(),
        )

    def test_returns_authorised_group_contract_and_default_empty_compliance_provider(self):
        response = self._search("Searchable Farmer")

        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        self.assertEqual(
            set(payload["data"]["groups"]),
            {
                "members",
                "loan_applications",
                "loan_accounts",
                "documents",
                "repayments",
                "compliance_records",
                "audit_logs",
            },
        )
        result = payload["data"]["groups"]["members"]["items"][0]
        self.assertEqual(result["title"], "Searchable Farmer")
        self.assertEqual(result["identifier"], "FOL-SEARCH-001")
        self.assertEqual(result["status"], "active")
        self.assertEqual(result["risk_status"], "no_default")
        self.assertEqual(result["last_updated_by"], "Authorised Searcher")
        self.assertEqual(result["quick_actions"][0]["label"], "Open")
        self.assertEqual(
            payload["data"]["groups"]["compliance_records"]["pagination"]["total_count"],
            0,
        )
        self.assertEqual(payload["data"]["groups"]["documents"]["pagination"]["total_count"], 1)
        self.assertEqual(payload["data"]["groups"]["audit_logs"]["pagination"]["total_count"], 1)
        application = payload["data"]["groups"]["loan_applications"]["items"][0]
        self.assertEqual(application["identifier"], "APP-SEARCH-001")
        self.assertEqual(application["amount"], None)
        self.assertEqual(
            [action["label"] for action in application["quick_actions"]],
            ["Open", "View documents"],
        )
        for group in payload["data"]["groups"].values():
            self.assertEqual(
                set(group["pagination"]),
                {
                    "page",
                    "page_size",
                    "total_count",
                    "total_pages",
                    "has_next",
                    "has_previous",
                },
            )

    def test_pan_and_aadhaar_lookup_are_exact_or_suffix_only_and_never_echo_raw_input(self):
        for query in (self.pan, self.aadhaar, "9012"):
            with self.subTest(query=query):
                response = self._search(query)
                self.assertEqual(response.status_code, 200, response.content)
                serialized = json.dumps(response.json())
                self.assertNotIn(query, serialized)
                self.assertEqual(
                    response.json()["data"]["groups"]["members"]["items"][0]["title"],
                    "Searchable Farmer",
                )
        for query in ("ABCDE", "89012"):
            with self.subTest(query=query):
                response = self._search(query)
                self.assertEqual(response.status_code, 200, response.content)
                self.assertEqual(
                    response.json()["data"]["groups"]["members"]["pagination"]["total_count"],
                    0,
                )
        self.assertFalse(
            AuditLog.objects.filter(new_value_json__icontains=self.pan).exists()
        )
        self.assertFalse(
            AuditLog.objects.filter(new_value_json__icontains=self.aadhaar).exists()
        )

    def test_all_source_inputs_map_to_the_scoped_member_root(self):
        relation_inputs = {
            "LN-SEARCH-001": "sfpcl_credit.loans.models.LoanAccount.objects.filter",
            "CHEQUE-SEARCH-001": "sfpcl_credit.processes.global_search.BlankDatedCheque.objects.filter",
            "CDSL-SEARCH-001": "sfpcl_credit.processes.global_search.CDSLSharePledge.objects.filter",
            "00000000-0000-4000-8000-000000000404": "sfpcl_credit.processes.global_search.SH4ShareTransferForm.objects.filter",
        }
        inputs = (
            ("Searchable Farmer", "Searchable Farmer"),
            ("Searchable Producer Company", "Searchable Producer Company"),
            ("APP-SEARCH-001", "Searchable Farmer"),
            ("LN-SEARCH-001", "Searchable Farmer"),
            ("FOL-SEARCH-001", "Searchable Farmer"),
            ("125", "Searchable Farmer"),
            (self.pan, "Searchable Farmer"),
            ("9012", "Searchable Farmer"),
            ("9876543210", "Searchable Farmer"),
            ("farmer.search@example.com", "Searchable Farmer"),
            ("SAP-SEARCH-001", "Searchable Farmer"),
            ("CHEQUE-SEARCH-001", "Searchable Farmer"),
            ("CDSL-SEARCH-001", "Searchable Farmer"),
            ("00000000-0000-4000-8000-000000000404", "Searchable Farmer"),
            ("7788", "Searchable Farmer"),
        )
        for query, expected_title in inputs:
            target = relation_inputs.get(query)
            context = patch(target) if target else nullcontext()
            with self.subTest(query=query), context as relation_filter:
                if relation_filter is not None:
                    relation_filter.return_value.values_list.return_value = [
                        self.member.member_id
                    ]
                response = self._search(query)
                self.assertEqual(response.status_code, 200, response.content)
                titles = [
                    row["title"]
                    for row in response.json()["data"]["groups"]["members"]["items"]
                ]
                self.assertIn(expected_title, titles)

    def test_sensitive_and_suffix_queries_use_measured_indexes(self):
        plans = {
            "pan": Member.objects.filter(pan_hash=identity_hash(self.pan)).explain(),
            "aadhaar": Member.objects.filter(aadhaar_hash=identity_hash(self.aadhaar)).explain(),
            "aadhaar_last4": Member.objects.filter(aadhaar_last4="9012").explain(),
            "share_count": Member.objects.filter(number_of_shares=125).explain(),
            "bank_last4": BankAccount.objects.filter(account_number_last4="7788").explain(),
        }
        for field, plan in plans.items():
            with self.subTest(field=field):
                normalized = plan.upper()
                self.assertIn("INDEX", normalized, plan)
                self.assertNotIn("SCAN MEMBERS", normalized, plan)
                self.assertNotIn("SCAN BANK_ACCOUNTS", normalized, plan)
        print("GLOBAL_SEARCH_INDEX_PLANS", plans)

    def test_denied_groups_are_absent_without_counts_or_match_existence(self):
        RolePermission.objects.filter(
            permission__permission_code__in=(
                "documents.loan_document.read",
                "audit.audit_log.read",
                "compliance.control.read",
            )
        ).delete()

        response = self._search("Searchable Farmer")

        self.assertEqual(response.status_code, 200, response.content)
        groups = response.json()["data"]["groups"]
        self.assertNotIn("documents", groups)
        self.assertNotIn("audit_logs", groups)
        self.assertNotIn("compliance_records", groups)

    def test_member_scope_removes_cross_object_name_matches(self):
        Member.objects.filter(pk=self.fpc.pk).update(created_by_user=None)
        MemberScopeAssignment.objects.filter(user=self.user).delete()
        MemberScopeAssignment.objects.create(
            user=self.user,
            permission_code="members.member.read",
            scope_type="assigned",
            member=self.member,
        )
        response = self._search("Searchable Producer Company")
        self.assertEqual(response.status_code, 200, response.content)
        groups = response.json()["data"]["groups"]
        self.assertEqual(groups["members"]["pagination"]["total_count"], 0)
        self.assertEqual(groups["loan_applications"]["pagination"]["total_count"], 0)

    def test_compliance_provider_reuses_the_shared_card_contract(self):
        card = global_search.build_result_card(
            row_id=self.member.member_id,
            result_type="compliance_record",
            title="Section 186 review",
            identifier="CMP-001",
            status="compliant",
            risk_status="low",
            amount=None,
            owner="Compliance Team",
            updated_at=timezone.now(),
            updated_by="Compliance User",
            quick_actions=[],
        )
        global_search.register_compliance_provider(
            lambda **_kwargs: [card]
        )
        try:
            response = self._search("Searchable Farmer")
            self.assertEqual(response.status_code, 200, response.content)
            projected = response.json()["data"]["groups"]["compliance_records"]["items"][0]
            self.assertEqual(set(projected), set(card))
            self.assertEqual(projected["title"], "Section 186 review")
        finally:
            global_search.register_compliance_provider(lambda **_kwargs: [])

    def test_rejects_unauthenticated_unknown_short_wildcard_and_malformed_requests(self):
        unauthenticated = self.client.post(
            self.URL,
            data={"search": "Farmer"},
            content_type="application/json",
        )
        self.assertEqual(unauthenticated.status_code, 401)
        assert_error_envelope(self, unauthenticated.json(), "AUTH_REQUIRED")

        for body in (
            {"search": "x"},
            {"search": "%Farmer"},
            {"search": "Farmer", "unknown": True},
            {"search": ["Farmer"]},
        ):
            with self.subTest(body=body):
                response = self.client.post(
                    self.URL,
                    data=json.dumps(body),
                    content_type="application/json",
                    headers=self._headers(),
                )
                self.assertEqual(response.status_code, 400, response.content)
                assert_error_envelope(self, response.json(), "VALIDATION_ERROR")

    def test_rate_limit_uses_actor_identity_and_returns_safe_error(self):
        for _ in range(30):
            self.assertEqual(self._search("Searchable Farmer").status_code, 200)
        limited = self._search("Searchable Farmer")
        self.assertEqual(limited.status_code, 429, limited.content)
        assert_error_envelope(self, limited.json(), "RATE_LIMITED")
        self.assertNotIn("Searchable Farmer", limited.content.decode())
