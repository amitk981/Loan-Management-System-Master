import json
from decimal import Decimal

from django.core.cache import cache
from django.test import Client, TestCase
from django.utils import timezone

from sfpcl_credit.compliance.models import (
    ComplianceControl,
    ComplianceEvidence,
    ComplianceTask,
    KYCReview,
    MoneyLendingLawReview,
    NbfcPrincipalBusinessTest,
    Section186Tracker,
)
from sfpcl_credit.compliance.search_facade import search_compliance_records
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import (
    AuditLog,
    Permission,
    Role,
    RolePermission,
    User,
)
from sfpcl_credit.members.models import (
    KycProfile,
    Member,
    MemberScopeAssignment,
)
from sfpcl_credit.processes import global_search


class GlobalSearchComplianceTests(TestCase):
    URL = "/api/v1/global-search/"
    PASSWORD = "SyntheticSearch123!"

    def setUp(self):
        cache.clear()
        self.client = Client()
        self.owner_role = Role.objects.create(
            role_code="compliance_team_member",
            role_name="Compliance Team Member",
            is_system_role=True,
            status="active",
        )
        reviewer_role = Role.objects.create(
            role_code="cfo",
            role_name="CFO",
            is_system_role=True,
            status="active",
        )
        for code in ("compliance.control.read", "compliance.task.read"):
            permission = Permission.objects.create(
                permission_code=code,
                permission_name=code,
                module_name="compliance",
                risk_level=Permission.RISK_HIGH,
            )
            RolePermission.objects.create(role=self.owner_role, permission=permission)
        self.owner = User.objects.create(
            full_name="Synthetic Compliance Owner",
            email="compliance-search-owner@sfpcl.example",
            status="active",
            primary_role=self.owner_role,
        )
        self.owner.set_password(self.PASSWORD)
        self.owner.save()
        self.reviewer = User.objects.create(
            full_name="Synthetic Compliance Reviewer",
            email="compliance-search-reviewer@sfpcl.example",
            status="active",
            primary_role=reviewer_role,
        )
        self.control = ComplianceControl.objects.create(
            control_code="SYNTHETIC_SEARCH_CONTROL",
            control_name="Synthetic browser compliance review",
            control_area="governance",
            legal_basis="Restricted legal basis must not enter search.",
            control_type=ComplianceControl.TYPE_DETECTIVE,
            frequency=ComplianceControl.FREQUENCY_QUARTERLY,
            owner_role_code=self.owner_role.role_code,
            owner_user=self.owner,
            reviewer_user=self.reviewer,
            first_due_date=timezone.localdate(),
            evidence_required="Restricted evidence requirement must not enter search.",
            risk_if_missed="Restricted internal risk must not enter search.",
            status=ComplianceControl.STATUS_ACTIVE,
        )
        self.task = ComplianceTask.objects.create(
            control=self.control,
            task_period="2026-Q3",
            due_date=timezone.localdate(),
            assigned_to_user=self.owner,
            reviewer_user=self.reviewer,
            task_status=ComplianceTask.STATUS_DUE,
            remarks="Restricted task note must not enter search.",
        )
        global_search.register_compliance_provider(search_compliance_records)

    def _grant(self, *codes):
        for code in codes:
            permission = Permission.objects.create(
                permission_code=code,
                permission_name=code,
                module_name="compliance",
                risk_level=Permission.RISK_HIGH,
            )
            RolePermission.objects.create(role=self.owner_role, permission=permission)

    def _user_with_permissions(self, role_code, *codes):
        role = Role.objects.create(
            role_code=role_code,
            role_name=role_code.replace("_", " ").title(),
            status="active",
        )
        for code in codes:
            permission, _created = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "compliance",
                    "risk_level": Permission.RISK_HIGH,
                },
            )
            RolePermission.objects.create(role=role, permission=permission)
        return User.objects.create(
            full_name=f"Synthetic {role.role_name}",
            email=f"{role_code}@search.sfpcl.example",
            status="active",
            primary_role=role,
        )

    def _accepted_evidence(self, code, name, period="2026-Q3"):
        control = ComplianceControl.objects.create(
            control_code=code,
            control_name=name,
            control_area="statutory",
            legal_basis="Restricted statutory analysis.",
            control_type=ComplianceControl.TYPE_DETECTIVE,
            frequency=ComplianceControl.FREQUENCY_QUARTERLY,
            owner_role_code=self.owner_role.role_code,
            owner_user=self.owner,
            reviewer_user=self.reviewer,
            first_due_date=timezone.localdate(),
            evidence_required="Restricted evidence.",
            risk_if_missed="Restricted risk.",
            status=ComplianceControl.STATUS_ACTIVE,
        )
        task = ComplianceTask.objects.create(
            control=control,
            task_period=period,
            due_date=timezone.localdate(),
            assigned_to_user=self.owner,
            reviewer_user=self.reviewer,
            task_status=ComplianceTask.STATUS_COMPLETED,
        )
        document = DocumentFile.objects.create(
            file_name=f"{code.lower()}.pdf",
            file_extension="pdf",
            mime_type="application/pdf",
            storage_provider="test",
            storage_key=f"tests/{code.lower()}.pdf",
            sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
            uploaded_by_user=self.owner,
        )
        evidence = ComplianceEvidence.objects.create(
            task=task,
            evidence_type="statutory_calculation",
            document=document,
            summary="Restricted evidence summary.",
            source_owner="compliance",
            source_entity_type="compliance_task",
            source_entity_id=task.pk,
            source_period=task.task_period,
            submitted_by_user=self.owner,
            review_status=ComplianceEvidence.REVIEW_ACCEPTED,
            reviewed_by_user=self.reviewer,
            reviewed_at=timezone.now(),
            review_comments="Restricted review comments.",
        )
        task.current_evidence = evidence
        task.save(update_fields=["current_evidence"])
        return task, evidence

    def _search(self, query):
        return self._search_as(self.owner, self.PASSWORD, query)

    def _search_as(self, user, password, query):
        login = self.client.post(
            "/api/v1/auth/login/",
            data=json.dumps({"email": user.email, "password": password}),
            content_type="application/json",
        )
        token = login.json()["data"]["access_token"]
        return self.client.post(
            self.URL,
            data=json.dumps({"search": query}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {token}"},
        )

    def test_owner_finds_safe_control_and_task_cards(self):
        AuditLog.objects.create(
            actor_user=self.reviewer,
            actor_type="user",
            action="compliance.control.updated",
            entity_type="compliance_control",
            entity_id=self.control.pk,
            new_value_json={"safe": "projection"},
        )
        response = self._search("Synthetic browser compliance")

        self.assertEqual(response.status_code, 200, response.content)
        group = response.json()["data"]["groups"]["compliance_records"]
        self.assertEqual(group["pagination"]["total_count"], 2)
        self.assertEqual(
            [row["identifier"] for row in group["items"]],
            ["SYNTHETIC_SEARCH_CONTROL", "SYNTHETIC_SEARCH_CONTROL · 2026-Q3"],
        )
        self.assertEqual(
            [row["quick_actions"] for row in group["items"]],
            [
                [{"label": "Open", "page": "compliance", "entity_id": str(self.control.pk)}],
                [{"label": "Open", "page": "compliance", "entity_id": str(self.task.pk)}],
            ],
        )
        self.assertEqual(
            group["items"][0]["last_updated_by"], self.reviewer.full_name
        )
        serialized = json.dumps(group)
        for restricted in (
            "Restricted legal basis",
            "Restricted evidence requirement",
            "Restricted internal risk",
            "Restricted task note",
        ):
            self.assertNotIn(restricted, serialized)

    def test_cross_scope_guesses_and_provider_failures_leak_no_match_existence(self):
        outsider_role = Role.objects.create(
            role_code="compliance_outsider",
            role_name="Compliance Outsider",
            status="active",
        )
        read_permission = Permission.objects.get(
            permission_code="compliance.control.read"
        )
        RolePermission.objects.create(
            role=outsider_role, permission=read_permission
        )
        outsider = User.objects.create(
            full_name="Synthetic Scoped Outsider",
            email="compliance-search-outsider@sfpcl.example",
            status="active",
            primary_role=outsider_role,
        )
        outsider.set_password(self.PASSWORD)
        outsider.save()

        for guess in (self.control.control_name, str(self.control.pk)):
            with self.subTest(guess=guess):
                response = self._search_as(outsider, self.PASSWORD, guess)
                self.assertEqual(response.status_code, 200, response.content)
                group = response.json()["data"]["groups"]["compliance_records"]
                self.assertEqual(group["items"], [])
                self.assertEqual(group["pagination"]["total_count"], 0)
                self.assertNotIn(self.control.control_name, response.content.decode())

        global_search.register_compliance_provider(
            lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("owner unavailable"))
        )
        unavailable = self._search("Synthetic browser compliance")
        self.assertEqual(unavailable.status_code, 200, unavailable.content)
        self.assertNotIn(
            "compliance_records", unavailable.json()["data"]["groups"]
        )
        self.assertNotIn("owner unavailable", unavailable.content.decode())

        global_search.register_compliance_provider(
            lambda **_kwargs: [
                {
                    "id": str(self.control.pk),
                    "result_type": "compliance_record",
                    "title": self.control.control_name,
                    "identifier": self.control.control_code,
                    "status": self.control.status,
                    "risk_status": None,
                    "amount": None,
                    "owner": self.owner.full_name,
                    "last_updated_at": timezone.now().isoformat(),
                    "last_updated_by": self.owner.full_name,
                    "quick_actions": [
                        {
                            "label": "Open",
                            "page": "audit",
                            "entity_id": str(self.control.pk),
                        }
                    ],
                }
            ]
        )
        invalid_mapping = self._search("Synthetic browser compliance")
        self.assertEqual(invalid_mapping.status_code, 200, invalid_mapping.content)
        self.assertNotIn(
            "compliance_records", invalid_mapping.json()["data"]["groups"]
        )
        global_search.register_compliance_provider(search_compliance_records)

    def test_compliance_cfo_cs_and_auditor_permission_matrix(self):
        evidence = ComplianceEvidence.objects.create(
            task=self.task,
            evidence_type="safe_matrix_type",
            document=DocumentFile.objects.create(
                file_name="restricted-matrix.pdf",
                file_extension="pdf",
                mime_type="application/pdf",
                storage_provider="test",
                storage_key="tests/restricted-matrix.pdf",
                sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
                uploaded_by_user=self.owner,
            ),
            summary="Restricted matrix summary",
            source_owner="compliance",
            source_entity_type="compliance_task",
            source_entity_id=self.task.pk,
            source_period=self.task.task_period,
            submitted_by_user=self.owner,
            review_status=ComplianceEvidence.REVIEW_PENDING,
        )
        cfo_permission_codes = (
            "compliance.control.read",
            "compliance.task.read",
            "compliance.evidence.review",
        )
        for code in cfo_permission_codes:
            permission, _created = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "compliance",
                    "risk_level": Permission.RISK_HIGH,
                },
            )
            RolePermission.objects.create(
                role=self.reviewer.primary_role, permission=permission
            )
        company_secretary = self._user_with_permissions(
            "company_secretary",
            "compliance.control.read",
            "compliance.control.manage",
            "compliance.task.read",
        )
        auditor = self._user_with_permissions(
            "internal_auditor",
            "compliance.control.read",
            "compliance.task.read",
            "compliance.evidence.review",
        )

        expected = {
            self.owner.pk: {str(self.control.pk), str(self.task.pk)},
            self.reviewer.pk: {
                str(self.control.pk),
                str(self.task.pk),
                str(evidence.pk),
            },
            company_secretary.pk: {str(self.control.pk)},
            auditor.pk: {
                str(self.control.pk),
                str(self.task.pk),
                str(evidence.pk),
            },
        }
        for actor in (self.owner, self.reviewer, company_secretary, auditor):
            with self.subTest(role=actor.primary_role.role_code):
                cards = search_compliance_records(
                    actor=actor,
                    search="Synthetic browser compliance",
                    member_ids=frozenset(),
                )
                self.assertEqual({row["id"] for row in cards}, expected[actor.pk])
                for card in cards:
                    if card["id"] == str(evidence.pk):
                        self.assertEqual(card["quick_actions"], [])
                    else:
                        self.assertEqual(
                            card["quick_actions"][0]["page"], "compliance"
                        )
                self.assertNotIn("Restricted matrix", json.dumps(cards))

    def test_compliance_group_uses_shared_cap_and_independent_pagination(self):
        for index in range(21):
            ComplianceControl.objects.create(
                control_code=f"PAGE_MATRIX_{index:02d}",
                control_name=f"Pagination matrix control {index:02d}",
                control_area="governance",
                legal_basis="Restricted",
                control_type=ComplianceControl.TYPE_DETECTIVE,
                frequency=ComplianceControl.FREQUENCY_QUARTERLY,
                owner_role_code=self.owner_role.role_code,
                owner_user=self.owner,
                reviewer_user=self.reviewer,
                first_due_date=timezone.localdate(),
                evidence_required="Restricted",
                risk_if_missed="Restricted",
                status=ComplianceControl.STATUS_ACTIVE,
            )
        login = self.client.post(
            "/api/v1/auth/login/",
            data=json.dumps({"email": self.owner.email, "password": self.PASSWORD}),
            content_type="application/json",
        )
        token = login.json()["data"]["access_token"]
        first = self.client.post(
            self.URL,
            data=json.dumps(
                {"search": "Pagination matrix", "page_size": 20}
            ),
            content_type="application/json",
            headers={"Authorization": f"Bearer {token}"},
        )
        group = first.json()["data"]["groups"]["compliance_records"]
        self.assertEqual(group["pagination"]["total_count"], 21)
        self.assertEqual(len(group["items"]), 20)
        self.assertTrue(group["pagination"]["has_next"])
        second = self.client.post(
            self.URL,
            data=json.dumps(
                {
                    "continuation": first.json()["data"]["continuation"],
                    "pages": {"compliance_records": 2},
                }
            ),
            content_type="application/json",
            headers={"Authorization": f"Bearer {token}"},
        )
        second_group = second.json()["data"]["groups"]["compliance_records"]
        self.assertEqual(len(second_group["items"]), 1)
        self.assertTrue(second_group["pagination"]["has_previous"])

    def test_governed_evidence_and_money_lending_review_are_minimised(self):
        self._grant(
            "compliance.evidence.submit",
            "compliance.money_lending_review.manage",
        )
        task, evidence = self._accepted_evidence(
            "MONEY_LENDING_ANNUAL",
            "Annual money-lending compliance",
            period="FY2026-27",
        )
        board_note = DocumentFile.objects.create(
            file_name="restricted-board-note.pdf",
            file_extension="pdf",
            mime_type="application/pdf",
            storage_provider="test",
            storage_key="tests/restricted-board-note.pdf",
            sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
            uploaded_by_user=self.owner,
        )
        review = MoneyLendingLawReview.objects.create(
            financial_year="FY2026-27",
            state="Maharashtra",
            applicability="exempt",
            exemption_applicable_flag=True,
            legal_opinion_document=evidence.document,
            board_note_document=board_note,
            task=task,
            evidence=evidence,
            reviewed_by_user=self.owner,
            remarks="Restricted legal opinion narrative must not leak.",
        )

        response = self._search("FY2026-27")

        self.assertEqual(response.status_code, 200, response.content)
        rows = response.json()["data"]["groups"]["compliance_records"]["items"]
        by_id = {row["id"]: row for row in rows}
        evidence_card = by_id[str(evidence.pk)]
        self.assertEqual(
            evidence_card["identifier"],
            "MONEY_LENDING_ANNUAL · FY2026-27",
        )
        self.assertEqual(evidence_card["status"], "accepted")
        self.assertEqual(evidence_card["quick_actions"], [])
        money_card = by_id[str(review.pk)]
        self.assertEqual(
            money_card["identifier"],
            "Money lending · FY2026-27 · Maharashtra",
        )
        self.assertEqual(money_card["status"], "exempt")
        self.assertEqual(
            money_card["quick_actions"],
            [{"label": "Open", "page": "compliance", "entity_id": str(review.pk)}],
        )
        serialized = json.dumps(rows).lower()
        for restricted in (
            "restricted-board-note",
            "restricted legal opinion",
            str(evidence.document_id).lower(),
            str(board_note.pk).lower(),
        ):
            self.assertNotIn(restricted, serialized)

    def test_statutory_trackers_project_source_amount_and_risk(self):
        self._grant("compliance.section186.read", "compliance.nbfc_test.read")
        section_task, section_evidence = self._accepted_evidence(
            "SECTION_186_LIMIT", "Section 186 quarterly limit"
        )
        nbfc_task, nbfc_evidence = self._accepted_evidence(
            "NBFC_PRINCIPAL_TEST", "NBFC principal-business test"
        )
        section = Section186Tracker.objects.create(
            financial_year="FY2026-27",
            quarter="Q2",
            paid_up_capital_amount=Decimal("100000.00"),
            free_reserves_amount=Decimal("50000.00"),
            securities_premium_amount=Decimal("25000.00"),
            limit_60_percent_basis_amount=Decimal("105000.00"),
            limit_100_percent_basis_amount=Decimal("75000.00"),
            applicable_limit_amount=Decimal("105000.00"),
            total_loans_exposure_amount=Decimal("90000.00"),
            headroom_amount=Decimal("15000.00"),
            within_limit_flag=True,
            special_resolution_required_flag=False,
            task=section_task,
            evidence=section_evidence,
            prepared_by_user=self.owner,
            reviewer_user=self.reviewer,
            reviewed_at=timezone.now(),
            review_decision="accepted",
            input_snapshot_json={"restricted_input": "must not leak"},
            result_snapshot_json={"restricted_result": "must not leak"},
            reviewer_snapshot_json={"restricted_reviewer": "must not leak"},
            evidence_snapshot_json={"restricted_evidence": "must not leak"},
        )
        nbfc = NbfcPrincipalBusinessTest.objects.create(
            financial_year="FY2026-27",
            quarter="Q2",
            financial_assets_amount=Decimal("60000.00"),
            total_assets_amount=Decimal("100000.00"),
            financial_asset_ratio=Decimal("60.0000"),
            financial_income_amount=Decimal("55000.00"),
            gross_income_amount=Decimal("100000.00"),
            financial_income_ratio=Decimal("55.0000"),
            early_warning_threshold_ratio=Decimal("45.0000"),
            registration_triggered_flag=True,
            one_ratio_above_statutory_flag=False,
            early_warning_flag=True,
            task=nbfc_task,
            evidence=nbfc_evidence,
            prepared_by_user=self.owner,
            reviewer_user=self.reviewer,
            input_snapshot_json={"restricted_input": "must not leak"},
            result_snapshot_json={"restricted_result": "must not leak"},
            reviewer_snapshot_json={"restricted_reviewer": "must not leak"},
            evidence_snapshot_json={"restricted_evidence": "must not leak"},
        )

        response = self._search("FY2026-27")

        self.assertEqual(response.status_code, 200, response.content)
        rows = response.json()["data"]["groups"]["compliance_records"]["items"]
        by_id = {row["id"]: row for row in rows}
        self.assertEqual(by_id[str(section.pk)]["amount"], "105000.00")
        self.assertEqual(by_id[str(section.pk)]["risk_status"], "within_limit")
        self.assertEqual(
            by_id[str(section.pk)]["identifier"], "Section 186 · FY2026-27 Q2"
        )
        self.assertIsNone(by_id[str(nbfc.pk)]["amount"])
        self.assertEqual(by_id[str(nbfc.pk)]["risk_status"], "registration_triggered")
        self.assertEqual(
            by_id[str(nbfc.pk)]["identifier"], "NBFC test · FY2026-27 Q2"
        )
        serialized = json.dumps(rows)
        self.assertNotIn("restricted_", serialized.lower())

    def test_rekyc_review_uses_member_scope_without_exposing_kyc_values(self):
        self._grant("compliance.kyc_review.manage")
        member = Member.objects.create(
            member_number="MEM-SAFE-KYC-001",
            member_type="individual_farmer",
            legal_name="Synthetic ReKYC Farmer",
            display_name="Synthetic ReKYC Farmer",
            folio_number="FOL-SAFE-KYC-001",
            membership_status="active",
            pan_encrypted="restricted-pan-token",
            pan_hash="restricted-pan-hash",
            aadhaar_encrypted="restricted-aadhaar-token",
            aadhaar_hash="restricted-aadhaar-hash",
            aadhaar_last4="9876",
            kyc_status="rekyc_due",
            default_status="no_default",
            created_by_user=self.owner,
        )
        profile = KycProfile.objects.create(
            party_type="member",
            party_id=member.pk,
            kyc_status="rekyc_due",
            ckyc_identifier_encrypted="restricted-ckyc-token",
            ckyc_consent_flag=True,
            beneficial_ownership_verified_flag=True,
            risk_rating="high",
            last_verified_at=timezone.now(),
        )
        task, _evidence = self._accepted_evidence(
            "KYC_AML", "KYC and AML review"
        )
        task.task_status = ComplianceTask.STATUS_OVERDUE
        task.save(update_fields=["task_status"])
        review = KYCReview.objects.create(
            member=member,
            kyc_profile=profile,
            review_type=KYCReview.TYPE_REKYC,
            cycle_key="restricted-cycle-key",
            source_verified_at=timezone.now(),
            due_date=timezone.localdate(),
            kyc_status_before="verified",
            status=KYCReview.STATUS_OVERDUE,
            completeness_snapshot_json={
                "risk_rating": "high",
                "pan": "restricted-pan-value",
                "ckyc": "restricted-ckyc-value",
            },
            completion_evidence_json=["restricted-evidence-id"],
            task=task,
        )
        MemberScopeAssignment.objects.create(
            user=self.owner,
            permission_code="compliance.kyc_review.manage",
            scope_type="global",
        )
        RolePermission.objects.filter(
            role=self.owner_role,
            permission__permission_code="compliance.task.read",
        ).delete()
        kyc_update = AuditLog.objects.create(
            actor_user=self.reviewer,
            actor_type="user",
            action="compliance.kyc_review.assigned",
            entity_type="kyc_review",
            entity_id=review.pk,
            new_value_json={"assigned_to_user_id": str(self.owner.pk)},
        )

        response = self._search("Synthetic ReKYC Farmer")

        self.assertEqual(response.status_code, 200, response.content)
        rows = response.json()["data"]["groups"]["compliance_records"]["items"]
        card = next(row for row in rows if row["id"] == str(review.pk))
        self.assertEqual(card["identifier"], "Re-KYC · MEM-SAFE-KYC-001")
        self.assertEqual(card["status"], "overdue")
        self.assertEqual(card["risk_status"], "high")
        self.assertEqual(card["owner"], self.owner.full_name)
        self.assertEqual(card["quick_actions"], [])
        self.assertEqual(card["last_updated_by"], self.reviewer.full_name)
        self.assertEqual(
            card["last_updated_at"],
            kyc_update.created_at.isoformat().replace("+00:00", "Z"),
        )
        serialized = json.dumps(card).lower()
        for restricted in (
            "restricted-pan",
            "restricted-aadhaar",
            "restricted-ckyc",
            "restricted-cycle",
            "restricted-evidence",
            "9876",
        ):
            self.assertNotIn(restricted, serialized)
