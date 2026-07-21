import json
import uuid
from contextlib import nullcontext
from unittest.mock import patch

from django.core.cache import cache
from django.test import Client, TestCase
from django.utils import timezone

from sfpcl_credit.applications.models import ApplicationDocument, LoanApplication, Witness
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import BankAccount, Member, MemberScopeAssignment, Shareholding
from sfpcl_credit.members.models import CancelledCheque
from sfpcl_credit.members.protected_identity import (
    identity_hash,
    protected_identity_token,
)
from sfpcl_credit.tests.api_contracts import assert_error_envelope
from sfpcl_credit.sap_workflow.models import SapCustomerCode
from sfpcl_credit.processes import global_search
from sfpcl_credit.legal_documents.models import LoanDocument
from sfpcl_credit.security_instruments.models import (
    BlankDatedCheque,
    CDSLSharePledge,
    SH4ShareTransferForm,
    SecurityPackage,
)
from sfpcl_credit.shared.encryption import FieldEncryption


class GlobalSearchApiTests(TestCase):
    URL = "/api/v1/global-search/"
    PASSWORD = "SearchPass123!"
    PERMISSIONS = (
        "members.member.read",
        "members.sensitive.reveal_pan",
        "members.sensitive.reveal_aadhaar",
        "applications.loan_application.read",
        "finance.loan_account.read",
        "finance.sap_code.read",
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

    def test_pan_and_aadhaar_inputs_require_their_canonical_sensitive_authority(self):
        RolePermission.objects.filter(
            permission__permission_code__in=(
                "members.sensitive.reveal_pan",
                "members.sensitive.reveal_aadhaar",
            )
        ).delete()

        for query in (self.pan, self.aadhaar, "9012"):
            with self.subTest(query=query):
                response = self._search(query)
                self.assertEqual(response.status_code, 200, response.content)
                self.assertEqual(
                    response.json()["data"]["groups"]["members"]["pagination"][
                        "total_count"
                    ],
                    0,
                )
                self.assertEqual(
                    response.json()["data"]["groups"]["loan_applications"][
                        "pagination"
                    ]["total_count"],
                    0,
                )
                self.assertEqual(
                    response.json()["data"]["groups"]["loan_accounts"][
                        "pagination"
                    ]["total_count"],
                    0,
                )

    def test_all_source_inputs_map_to_the_scoped_member_root(self):
        relation_inputs = {
            "LN-SEARCH-001": "sfpcl_credit.loans.modules.search_facade.matching_member_ids",
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
            ("7788", "Searchable Farmer"),
        )
        for query, expected_title in inputs:
            target = relation_inputs.get(query)
            context = patch(target) if target else nullcontext()
            with self.subTest(query=query), context as relation_filter:
                if relation_filter is not None:
                    relation_filter.return_value = frozenset({self.member.member_id})
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
        self.assertEqual(
            [
                action["label"]
                for action in groups["loan_applications"]["items"][0][
                    "quick_actions"
                ]
            ],
            ["Open"],
        )

    def test_sap_and_bank_suffix_cannot_feed_independent_groups_without_input_authority(self):
        RolePermission.objects.filter(
            permission__permission_code="finance.sap_code.read"
        ).delete()
        sap_denied = self._search("SAP-SEARCH-001")
        self.assertEqual(sap_denied.status_code, 200, sap_denied.content)
        for group in ("members", "loan_applications", "loan_accounts"):
            self.assertEqual(
                sap_denied.json()["data"]["groups"][group]["pagination"][
                    "total_count"
                ],
                0,
            )

        RolePermission.objects.filter(
            permission__permission_code="members.member.read"
        ).delete()
        MemberScopeAssignment.objects.filter(user=self.user).delete()
        bank_denied = self._search("7788")
        self.assertEqual(bank_denied.status_code, 200, bank_denied.content)
        self.assertNotIn("members", bank_denied.json()["data"]["groups"])
        for group in ("loan_applications", "loan_accounts"):
            self.assertEqual(
                bank_denied.json()["data"]["groups"][group]["pagination"][
                    "total_count"
                ],
                0,
            )

    def test_cfo_without_blank_cheque_authority_cannot_resolve_owner_by_cheque(self):
        self.assertNotIn("security.package.read", self.PERMISSIONS)
        self.assertNotIn("security.blank_cheque.manage", self.PERMISSIONS)
        with patch(
            "sfpcl_credit.security_instruments.search_facade.BlankDatedCheque.objects.filter"
        ) as restricted_owner:
            restricted_owner.return_value.values_list.return_value = [
                self.member.member_id
            ]

            response = self._search("CHEQUE-SEARCH-001")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.json()["data"]["groups"]["members"]["pagination"][
                "total_count"
            ],
            0,
        )
        restricted_owner.assert_not_called()

    def test_sensitive_input_cannot_fall_through_to_a_non_owner_reference(self):
        LoanApplication.objects.create(
            application_reference_number="CHEQUE-COLLISION-001",
            member=self.member,
            borrower_type="individual_farmer",
            received_by_user=self.user,
            created_by_user=self.user,
            updated_by_user=self.user,
        )
        LoanApplication.objects.create(
            application_reference_number="SAP-COLLISION-001",
            member=self.member,
            borrower_type="individual_farmer",
            received_by_user=self.user,
            created_by_user=self.user,
            updated_by_user=self.user,
        )

        for query in ("CHEQUE-COLLISION-001", "SAP-COLLISION-001"):
            with self.subTest(query=query):
                response = self._search(query)
                self.assertEqual(response.status_code, 200, response.content)
                groups = response.json()["data"]["groups"]
                self.assertEqual(groups["members"]["pagination"]["total_count"], 0)
                self.assertEqual(
                    groups["loan_applications"]["pagination"]["total_count"], 0
                )

    def test_security_authorised_actor_resolves_real_blank_cheque_without_raw_disclosure(self):
        for code in (
            "security.package.read",
            "security.blank_cheque.manage",
            "security.sh4.manage",
            "security.cdsl_pledge.manage",
        ):
            permission = Permission.objects.create(
                permission_code=code,
                permission_name=code,
                module_name="security",
                risk_level="critical",
            )
            RolePermission.objects.create(role=self.user.primary_role, permission=permission)
        package = SecurityPackage.objects.create(
            loan_application=self.application,
            blank_cheque_required_flag=True,
            cancelled_cheque_required_flag=True,
        )
        cancelled = CancelledCheque.objects.create(
            loan_application_id=self.application.pk,
            member=self.member,
            document_id=self.application_document.document_file_id,
            account_number_encrypted="protected-cancelled-account",
            account_number_hash="security-search-cancelled-hash",
            account_number_last4="7788",
            ifsc="TEST0000001",
            verification_status="verified",
        )
        raw_cheque = "CHEQUE-REAL-001"
        BlankDatedCheque.objects.create(
            security_package=package,
            member=self.member,
            bank_account=BankAccount.objects.get(owner_party_id=self.member.pk),
            cancelled_cheque=cancelled,
            cheque_number_encrypted=FieldEncryption.encrypt(
                "blank_cheque.cheque_number", raw_cheque
            ),
            cheque_number_hash=FieldEncryption.hash_for_lookup(
                "blank_cheque.cheque_number", raw_cheque
            ),
            cheque_status="collected",
            collected_at=timezone.localdate(),
            prepared_by_user=self.user,
        )
        verifier = User.objects.create(
            full_name="Security Search Verifier",
            email="security-search-verifier@sfpcl.example",
            status="active",
            primary_role=self.user.primary_role,
        )
        cdsl_reference = "CDSL-REAL-001"
        CDSLSharePledge.objects.create(
            security_package=package,
            pledgor_member=self.member,
            pledgee_entity_name="SFPCL",
            pledgor_bo_account_encrypted="protected-pledgor-bo",
            pledgor_bo_account_hash="security-search-pledgor-hash",
            pledgor_bo_account_last4="1234",
            pledgee_bo_account_encrypted="protected-pledgee-bo",
            pledgee_bo_account_hash="security-search-pledgee-hash",
            pledgee_bo_account_last4="5678",
            pledgor_dp_name="Pledgor DP",
            pledgee_dp_name="Pledgee DP",
            prf_status="submitted",
            pledge_sequence_number=cdsl_reference,
            pledge_acceptance_status="rejected",
            pledge_status="pending",
            evidence_document_id=self.application_document.document_file_id,
            prepared_by_user=self.user,
            verified_by_user=verifier,
            acceptance_workflow_event_id=uuid.uuid4(),
        )
        shareholding = Shareholding.objects.create(
            member=self.member,
            folio_number=self.member.folio_number,
            number_of_shares=10,
            holding_mode="physical",
            pledged_share_count=0,
            available_share_count=10,
        )
        witness = Witness.objects.create(
            loan_application=self.application,
            member=self.member,
            witness_name="Security Search Witness",
            pan_encrypted="protected-witness-pan",
            pan_hash="security-search-witness-pan-hash",
            aadhaar_encrypted="protected-witness-aadhaar",
            aadhaar_hash="security-search-witness-aadhaar-hash",
        )
        loan_document = LoanDocument.objects.create(
            loan_application=self.application,
            document_type="sh4",
            document_category="security",
            output_format="pdf",
            generation_status="generated",
            execution_status="pending",
            verification_status="pending",
        )
        sh4 = SH4ShareTransferForm.objects.create(
            security_package=package,
            member=self.member,
            witness=witness,
            shareholding=shareholding,
            share_count=10,
            loan_document=loan_document,
            form_status="pending",
            prepared_by_user=self.user,
        )

        for query in (raw_cheque, cdsl_reference, str(sh4.pk)):
            with self.subTest(query=query):
                response = self._search(query)
                self.assertEqual(response.status_code, 200, response.content)
                serialized = json.dumps(response.json())
                self.assertNotIn(query, serialized)
                self.assertEqual(
                    response.json()["data"]["groups"]["members"]["pagination"][
                        "total_count"
                    ],
                    1,
                )

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

    def test_application_authority_is_independent_and_scope_precedes_result_cap(self):
        RolePermission.objects.filter(
            permission__permission_code="members.member.read"
        ).delete()
        MemberScopeAssignment.objects.filter(user=self.user).delete()
        other = User.objects.create(
            full_name="Denied Application Owner",
            email="denied-app-owner@sfpcl.example",
            status="active",
            primary_role=self.user.primary_role,
        )
        LoanApplication.objects.bulk_create(
            [
                LoanApplication(
                    application_reference_number=f"APP-DENIED-{index:03d}",
                    member=self.member,
                    borrower_type="individual_farmer",
                    received_by_user=other,
                    created_by_user=other,
                    updated_by_user=other,
                )
                for index in range(100)
            ]
        )

        response = self._search("Searchable Farmer")

        self.assertEqual(response.status_code, 200, response.content)
        groups = response.json()["data"]["groups"]
        self.assertNotIn("members", groups)
        self.assertEqual(groups["loan_applications"]["pagination"]["total_count"], 1)
        self.assertEqual(
            groups["loan_applications"]["items"][0]["identifier"],
            "APP-SEARCH-001",
        )

    def test_opaque_continuation_replays_pages_without_resubmitting_sensitive_input(self):
        initial = self._search(self.pan, page_size=20, pages={"members": 1})
        self.assertEqual(initial.status_code, 200, initial.content)
        continuation = initial.json()["data"]["continuation"]
        self.assertEqual(len(continuation), 32)
        self.assertNotIn(self.pan, json.dumps(initial.json()))

        replay = self.client.post(
            self.URL,
            data=json.dumps(
                {"continuation": continuation, "pages": {"members": 2}}
            ),
            content_type="application/json",
            headers=self._headers(),
        )

        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"]["continuation"], continuation)
        self.assertEqual(
            replay.json()["data"]["groups"]["members"]["pagination"]["page_size"],
            20,
        )
        self.assertNotIn(self.pan, json.dumps(replay.json()))

    def test_invalid_or_ambiguous_continuations_fail_without_match_disclosure(self):
        for body in (
            {"continuation": "not-a-token"},
            {"continuation": "0" * 32},
            {"search": "Searchable Farmer", "continuation": "0" * 32},
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

    def test_member_pages_enforce_1_20_21_100_101_boundaries(self):
        Member.objects.bulk_create(
            [
                Member(
                    member_number=f"MEM-BOUNDARY-{index:03d}",
                    member_type="fpc",
                    legal_name=f"Boundary Member {index:03d}",
                    display_name=f"Boundary Member {index:03d}",
                    folio_number=f"FOL-BOUNDARY-{index:03d}",
                    membership_status="active",
                    pan_encrypted=f"boundary-pan-{index:03d}",
                    pan_hash=f"boundary-pan-hash-{index:03d}",
                    aadhaar_encrypted="",
                    aadhaar_hash="",
                    mobile_number="",
                    email="",
                    kyc_status="verified",
                    default_status="no_default",
                    created_by_user=self.user,
                )
                for index in range(101)
            ]
        )

        first = self._search("Boundary", page_size=20, pages={"members": 1})
        second = self._search("Boundary", page_size=20, pages={"members": 2})
        last = self._search("Boundary", page_size=20, pages={"members": 5})
        clamped = self._search("Boundary", page_size=20, pages={"members": 6})
        single = self._search("Boundary", page_size=1, pages={"members": 1})

        for response in (first, second, last, clamped, single):
            self.assertEqual(response.status_code, 200, response.content)
            self.assertEqual(
                response.json()["data"]["groups"]["members"]["pagination"][
                    "total_count"
                ],
                100,
            )
        self.assertEqual(len(first.json()["data"]["groups"]["members"]["items"]), 20)
        self.assertEqual(len(second.json()["data"]["groups"]["members"]["items"]), 20)
        self.assertEqual(len(last.json()["data"]["groups"]["members"]["items"]), 20)
        self.assertEqual(
            clamped.json()["data"]["groups"]["members"]["pagination"]["page"], 5
        )
        self.assertEqual(len(single.json()["data"]["groups"]["members"]["items"]), 1)

    def test_each_delivered_group_uses_1_20_21_100_101_pagination_contract(self):
        delivered_groups = (
            "members",
            "loan_applications",
            "loan_accounts",
            "documents",
            "repayments",
            "audit_logs",
        )
        for group in delivered_groups:
            for count in (1, 20, 21, 100, 101):
                with self.subTest(group=group, count=count):
                    page = global_search.paginate_group(
                        range(count), page=1, page_size=20
                    )
                    self.assertEqual(page["pagination"]["total_count"], min(count, 100))
                    self.assertEqual(
                        page["pagination"]["total_pages"],
                        1 if count == 1 else min(5, (count + 19) // 20),
                    )
                    self.assertEqual(len(page["items"]), min(count, 20))

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
