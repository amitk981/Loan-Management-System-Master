from datetime import date
from decimal import Decimal
import json
from django.test import TestCase
from sfpcl_credit.compliance.models import (
    ComplianceControl,
    ComplianceEvidence,
    ComplianceTask,
    NbfcPrincipalBusinessTest,
)
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import Permission, Role, RolePermission, User
class StatutoryTrackerModuleTests(TestCase):
    def setUp(self):
        self.cfo_role = Role.objects.create(role_code="cfo", role_name="CFO")
        self.reviewer_role = Role.objects.create(
            role_code="compliance_team_member", role_name="Compliance Team Member"
        )
        self.cfo = User.objects.create(
            full_name="CFO Owner", email="statutory-cfo@example.test", primary_role=self.cfo_role,
        )
        self.cfo.set_password("StatutoryPass123!")
        self.cfo.save(update_fields=["password_hash"])
        self.reviewer = User.objects.create(
            full_name="Independent Reviewer", email="statutory-reviewer@example.test",
            primary_role=self.reviewer_role,
        )
        self.reviewer.set_password("StatutoryPass123!")
        self.reviewer.save(update_fields=["password_hash"])
        self._grant(self.cfo_role, "compliance.section186.create")
        self.document = DocumentFile.objects.create(
            file_name="quarterly-financials.pdf", storage_provider="local",
            storage_key="governed/compliance/quarterly-financials.pdf",
            uploaded_by_user=self.cfo, sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
        )

    def test_section_186_calculate_uses_higher_limit_and_flags_excess(self):
        from sfpcl_credit.compliance.modules.section186_tracker import (
            Section186TrackerModule,
        )
        task, evidence = self._accepted_evidence("SECTION_186_LIMIT")
        tracker = Section186TrackerModule.calculate(
            actor=self.cfo,
            period_id=task.pk,
            payload={
                "financial_year": "FY2026-27",
                "quarter": "Q1",
                "paid_up_capital_amount": "10000000.00",
                "free_reserves_amount": "5000000.00",
                "securities_premium_amount": "2000000.00",
                "total_loans_exposure_amount": "11000000.00",
                "compliance_evidence_id": str(evidence.pk),
            },
        )
        self.assertEqual((tracker.limit_60_percent_basis_amount, tracker.limit_100_percent_basis_amount,
                          tracker.applicable_limit_amount, tracker.headroom_amount),
                         (Decimal("10200000.00"), Decimal("7000000.00"), Decimal("10200000.00"), Decimal("-800000.00")))
        self.assertEqual((tracker.within_limit_flag, tracker.special_resolution_required_flag), (False, True))

    def test_nbfc_exact_fifty_and_one_ratio_over_warns_without_trigger(self):
        from sfpcl_credit.compliance.modules.nbfc_principal_business_test import (
            NbfcPrincipalBusinessTestModule,
        )

        self._grant(self.cfo_role, "compliance.nbfc_test.create")
        task, evidence = self._accepted_evidence("NBFC_PRINCIPAL_TEST")

        result = NbfcPrincipalBusinessTestModule.calculate(
            actor=self.cfo,
            period_id=task.pk,
            payload={
                "financial_year": "FY2026-27",
                "quarter": "Q1",
                "financial_assets_amount": "50.00",
                "total_assets_amount": "100.00",
                "financial_income_amount": "60.00",
                "gross_income_amount": "100.00",
                "early_warning_threshold_ratio": "40.0000",
                "compliance_evidence_id": str(evidence.pk),
            },
        )

        self.assertEqual((result.financial_asset_ratio, result.financial_income_ratio),
                         (Decimal("50.0000"), Decimal("60.0000")))
        self.assertEqual((result.registration_triggered_flag, result.one_ratio_above_statutory_flag,
                          result.early_warning_flag), (False, True, True))

    def test_section_186_api_creates_reads_and_reviews_retained_calculation(self):
        self._grant(self.cfo_role, "compliance.section186.read")
        self._grant(self.reviewer_role, "compliance.section186.read")
        self._grant(self.reviewer_role, "compliance.evidence.review")
        task, evidence = self._accepted_evidence("SECTION_186_LIMIT")
        payload = {
            "financial_year": "FY2026-27",
            "quarter": "Q1",
            "paid_up_capital_amount": "100.00",
            "free_reserves_amount": "100.00",
            "securities_premium_amount": "0.00",
            "total_loans_exposure_amount": "100.00",
            "compliance_task_id": str(task.pk),
            "compliance_evidence_id": str(evidence.pk),
        }

        created = self.client.post(
            "/api/v1/compliance/section-186-trackers/",
            data=json.dumps(payload),
            content_type="application/json",
            **self._auth(self.cfo),
        )
        self.assertEqual(created.status_code, 200, created.content)
        tracker_id = created.json()["data"]["section_186_tracker_id"]
        self.assertEqual(created.json()["data"]["applicable_limit_amount"], "120.00")
        retained = self.client.get(
            f"/api/v1/compliance/section-186-trackers/{tracker_id}/",
            **self._auth(self.reviewer),
        )
        self.assertEqual(retained.status_code, 200, retained.content)
        self.assertEqual(retained.json()["data"]["review_status"], "draft")

        reviewed = self.client.post(
            f"/api/v1/compliance/section-186-trackers/{tracker_id}/submit-for-review/",
            data=json.dumps({}),
            content_type="application/json",
            **self._auth(self.cfo),
        )
        self.assertEqual(reviewed.status_code, 200, reviewed.content)
        reviewed = self.client.post(
            f"/api/v1/compliance/section-186-trackers/{tracker_id}/review/",
            data=json.dumps(
                {
                    "decision": "accepted",
                    "comments": "Quarter calculation and evidence agree.",
                    "presented_to_board_flag": False,
                }
            ),
            content_type="application/json",
            **self._auth(self.reviewer),
        )

        self.assertEqual(reviewed.status_code, 200, reviewed.content)
        self.assertEqual(reviewed.json()["data"]["review_status"], "accepted")
        self.assertFalse(reviewed.json()["data"]["presented_to_board_flag"])
        self._grant(self.cfo_role, "compliance.nbfc_test.create")
        self._grant(self.cfo_role, "compliance.nbfc_test.read")
        self._grant(self.reviewer_role, "compliance.nbfc_test.read")
        nbfc_task, nbfc_evidence = self._accepted_evidence("NBFC_PRINCIPAL_TEST")
        nbfc_created = self.client.post(
            "/api/v1/compliance/nbfc-principal-tests/",
            data=json.dumps({
                "financial_year": "FY2026-27", "quarter": "Q1",
                "financial_assets_amount": "51.00", "total_assets_amount": "100.00",
                "financial_income_amount": "51.00", "gross_income_amount": "100.00",
                "early_warning_threshold_ratio": "40.0000",
                "compliance_task_id": str(nbfc_task.pk),
                "compliance_evidence_id": str(nbfc_evidence.pk),
            }),
            content_type="application/json",
            **self._auth(self.cfo),
        )
        self.assertEqual(nbfc_created.status_code, 200, nbfc_created.content)
        nbfc_id = nbfc_created.json()["data"]["nbfc_principal_test_id"]
        nbfc_retained = self.client.get(
            f"/api/v1/compliance/nbfc-principal-tests/{nbfc_id}/",
            **self._auth(self.reviewer),
        )
        self.assertEqual(nbfc_retained.status_code, 200, nbfc_retained.content)
        self.assertTrue(nbfc_retained.json()["data"]["registration_triggered_flag"])

    def test_section_186_table_covers_higher_equal_rounding_and_replay(self):
        from sfpcl_credit.compliance.modules.compliance_control_tracker import (
            ComplianceConflict,
        )
        from sfpcl_credit.compliance.modules.section186_tracker import (
            Section186TrackerModule,
        )

        cases = (
            ("Q1", "0.00", "100.00", "0.00", "100.00", "100.00", True),
            ("Q2", "0.01", "0.00", "0.00", "0.00", "0.01", True),
        )
        for quarter, paid, reserves, premium, exposure, expected_limit, within in cases:
            with self.subTest(quarter=quarter):
                task, evidence = self._accepted_evidence(
                    "SECTION_186_LIMIT", fiscal_quarter=quarter
                )
                payload = {
                    "financial_year": "FY2026-27",
                    "quarter": quarter,
                    "paid_up_capital_amount": paid,
                    "free_reserves_amount": reserves,
                    "securities_premium_amount": premium,
                    "total_loans_exposure_amount": exposure,
                    "compliance_evidence_id": str(evidence.pk),
                }
                first = Section186TrackerModule.calculate(
                    actor=self.cfo, period_id=task.pk, payload=payload
                )
                replay = Section186TrackerModule.calculate(
                    actor=self.cfo, period_id=task.pk, payload=payload
                )
                self.assertEqual(first.pk, replay.pk)
                self.assertEqual(first.applicable_limit_amount, Decimal(expected_limit))
                self.assertEqual(first.within_limit_flag, within)

        changed = dict(payload, total_loans_exposure_amount="1.00")
        with self.assertRaises(ComplianceConflict):
            Section186TrackerModule.calculate(
                actor=self.cfo, period_id=task.pk, payload=changed
            )

    def test_nbfc_table_covers_exact_fifty_one_over_and_both_over(self):
        from sfpcl_credit.compliance.modules.nbfc_principal_business_test import (
            NbfcPrincipalBusinessTestModule,
        )

        self._grant(self.cfo_role, "compliance.nbfc_test.create")
        cases = (
            ("Q1", "50.00", "50.00", False, False),
            ("Q2", "51.00", "50.00", False, True),
            ("Q3", "50.00", "51.00", False, True),
            ("Q4", "51.00", "51.00", True, False),
        )
        for quarter, assets, income, triggered, one_over in cases:
            with self.subTest(quarter=quarter):
                task, evidence = self._accepted_evidence(
                    "NBFC_PRINCIPAL_TEST", fiscal_quarter=quarter
                )
                row = NbfcPrincipalBusinessTestModule.calculate(
                    actor=self.cfo,
                    period_id=task.pk,
                    payload={
                        "financial_year": "FY2026-27",
                        "quarter": quarter,
                        "financial_assets_amount": assets,
                        "total_assets_amount": "100.00",
                        "financial_income_amount": income,
                        "gross_income_amount": "100.00",
                        "early_warning_threshold_ratio": "40.0000",
                        "compliance_evidence_id": str(evidence.pk),
                    },
                )
                self.assertEqual((row.registration_triggered_flag, row.one_ratio_above_statutory_flag),
                                 (triggered, one_over))

    def test_trackers_reject_unsafe_inputs_foreign_evidence_and_self_review(self):
        from sfpcl_credit.compliance.modules.compliance_control_tracker import (
            ComplianceDenied,
            ComplianceInvalid,
        )
        from sfpcl_credit.compliance.modules.nbfc_principal_business_test import (
            NbfcPrincipalBusinessTestModule,
        )
        from sfpcl_credit.compliance.modules.section186_tracker import (
            Section186TrackerModule,
        )

        self._grant(self.cfo_role, "compliance.nbfc_test.create")
        section_task, section_evidence = self._accepted_evidence("SECTION_186_LIMIT")
        nbfc_task, nbfc_evidence = self._accepted_evidence("NBFC_PRINCIPAL_TEST")
        section_payload = {
            "financial_year": "FY2026-27",
            "quarter": "Q1",
            "paid_up_capital_amount": "100.00",
            "free_reserves_amount": "0.00",
            "securities_premium_amount": "0.00",
            "total_loans_exposure_amount": "10.00",
            "compliance_evidence_id": str(section_evidence.pk),
        }
        for changed in (
            dict(section_payload, paid_up_capital_amount="-1.00"),
            dict(section_payload, paid_up_capital_amount="NaN"),
            dict(section_payload, financial_year="2026-27"),
            dict(section_payload, applicable_limit_amount="999.00"),
            dict(section_payload, compliance_evidence_id=str(nbfc_evidence.pk)),
        ):
            with self.subTest(changed=changed):
                with self.assertRaises(ComplianceInvalid):
                    Section186TrackerModule.calculate(
                        actor=self.cfo, period_id=section_task.pk, payload=changed
                    )

        nbfc_payload = {
            "financial_year": "FY2026-27",
            "quarter": "Q1",
            "financial_assets_amount": "1.00",
            "total_assets_amount": "0.00",
            "financial_income_amount": "1.00",
            "gross_income_amount": "10.00",
            "early_warning_threshold_ratio": "40.0000",
            "compliance_evidence_id": str(nbfc_evidence.pk),
        }
        with self.assertRaises(ComplianceInvalid):
            NbfcPrincipalBusinessTestModule.calculate(
                actor=self.cfo, period_id=nbfc_task.pk, payload=nbfc_payload
            )
        with self.assertRaises(ComplianceInvalid):
            NbfcPrincipalBusinessTestModule.calculate(
                actor=self.cfo,
                period_id=nbfc_task.pk,
                payload=dict(nbfc_payload, total_assets_amount="Infinity"),
            )

        row = Section186TrackerModule.calculate(
            actor=self.cfo, period_id=section_task.pk, payload=section_payload
        )
        row.total_loans_exposure_amount = Decimal("999.00")
        with self.assertRaisesMessage(
            ValueError, "Retained statutory calculation facts are immutable."
        ):
            row.save()
        with self.assertRaises(ComplianceDenied):
            Section186TrackerModule.review(
                actor=self.cfo,
                tracker_id=row.pk,
                decision="accepted",
                comments="Self review is forbidden.",
                presented_to_board_flag=False,
            )

    def test_denied_tracker_access_is_audited(self):
        from sfpcl_credit.identity.models import AuditLog

        viewer_role = Role.objects.create(
            role_code="management_viewer", role_name="Management Viewer"
        )
        viewer = User.objects.create(
            full_name="Unauthorised Viewer",
            email="statutory-denied@example.test",
            primary_role=viewer_role,
        )
        viewer.set_password("StatutoryPass123!")
        viewer.save(update_fields=["password_hash"])

        response = self.client.post(
            "/api/v1/compliance/section-186-trackers/",
            data=json.dumps({}),
            content_type="application/json",
            **self._auth(viewer),
        )

        self.assertEqual(response.status_code, 403, response.content)
        denied = AuditLog.objects.get(
            actor_user=viewer, action="compliance.access.denied"
        )
        self.assertEqual(
            denied.new_value_json["path"],
            "/api/v1/compliance/section-186-trackers/",
        )
        AuditLog.objects.all().delete()
        existing_endpoint = self.client.get(
            "/api/v1/compliance-controls/", **self._auth(viewer)
        )
        self.assertEqual(existing_endpoint.status_code, 403)
        denied = AuditLog.objects.get(
            actor_user=viewer, action="compliance.access.denied"
        )
        self.assertEqual(denied.new_value_json["path"], "/api/v1/compliance-controls/")

    def test_nbfc_exact_trigger_and_review_handoff_freeze_board_evidence(self):
        from sfpcl_credit.compliance.modules.compliance_control_tracker import (
            ComplianceInvalid,
        )
        from sfpcl_credit.compliance.modules.nbfc_principal_business_test import (
            NbfcPrincipalBusinessTestModule,
        )
        from sfpcl_credit.identity.models import AuditLog

        self._grant(self.cfo_role, "compliance.nbfc_test.create")
        self._grant(self.reviewer_role, "compliance.evidence.review")
        task, evidence = self._accepted_evidence("NBFC_PRINCIPAL_TEST")
        row = NbfcPrincipalBusinessTestModule.calculate(
            actor=self.cfo,
            period_id=task.pk,
            payload={
                "financial_year": "FY2026-27",
                "quarter": "Q1",
                "financial_assets_amount": "500000.40",
                "total_assets_amount": "1000000.00",
                "financial_income_amount": "500000.40",
                "gross_income_amount": "1000000.00",
                "early_warning_threshold_ratio": "40.0000",
                "compliance_evidence_id": str(evidence.pk),
            },
        )
        self.assertTrue(row.registration_triggered_flag)
        with self.assertRaises(ComplianceInvalid):
            NbfcPrincipalBusinessTestModule.review(
                actor=self.reviewer,
                result_id=row.pk,
                decision="accepted",
                comments="Too early.",
                presented_to_board_flag=True,
                board_document_id=None,
            )
        NbfcPrincipalBusinessTestModule.submit_for_review(
            actor=self.cfo, result_id=row.pk
        )
        board_document = DocumentFile.objects.create(
            file_name="nbfc-board-note.pdf",
            storage_provider="local",
            storage_key="governed/compliance/nbfc-board-note.pdf",
            uploaded_by_user=self.reviewer,
            sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
        )
        reviewed = NbfcPrincipalBusinessTestModule.review(
            actor=self.reviewer,
            result_id=row.pk,
            decision="accepted",
            comments="Presented with the retained Board note.",
            presented_to_board_flag=True,
            board_document_id=board_document.pk,
        )
        audit = AuditLog.objects.get(action="compliance.nbfc_test.reviewed")
        self.assertEqual(audit.new_value_json["decision"], "accepted")
        self.assertEqual(
            audit.new_value_json["board_document_id"], str(board_document.pk)
        )
        reviewed = NbfcPrincipalBusinessTest.objects.get(pk=row.pk)
        reviewed.review_comments = "rewritten"
        with self.assertRaisesMessage(ValueError, "final review is immutable"):
            reviewed.save()

    def _accepted_evidence(self, control_code, fiscal_quarter="Q1"):
        control, _created = ComplianceControl.objects.get_or_create(
            control_code=control_code,
            defaults={
                "control_name": control_code.replace("_", " ").title(),
                "control_area": "statutory",
                "legal_basis": "Approved statutory control.",
                "control_type": ComplianceControl.TYPE_DETECTIVE,
                "frequency": ComplianceControl.FREQUENCY_QUARTERLY,
                "owner_role_code": self.cfo_role.role_code,
                "owner_user": self.cfo,
                "reviewer_user": self.reviewer,
                "first_due_date": date(2026, 6, 30),
                "evidence_required": "Restricted quarterly financial statements.",
                "risk_if_missed": "Statutory assessment overdue.",
            },
        )
        period_map = {
            "Q1": ("2026-Q2", date(2026, 6, 30)),
            "Q2": ("2026-Q3", date(2026, 9, 30)),
            "Q3": ("2026-Q4", date(2026, 12, 31)),
            "Q4": ("2027-Q1", date(2027, 3, 31)),
        }
        task_period, due_date = period_map[fiscal_quarter]
        task = ComplianceTask.objects.create(
            control=control, task_period=task_period, due_date=due_date,
            assigned_to_user=self.cfo, reviewer_user=self.reviewer,
            task_status=ComplianceTask.STATUS_COMPLETED,
        )
        evidence = ComplianceEvidence.objects.create(
            task=task, evidence_type="quarterly_financials", document=self.document,
            summary="Quarterly financial statements.", source_owner="documents",
            source_entity_type="document_file", source_entity_id=self.document.pk,
            source_period=task.task_period, submitted_by_user=self.cfo,
            review_status=ComplianceEvidence.REVIEW_ACCEPTED,
            reviewed_by_user=self.reviewer,
        )
        task.current_evidence = evidence
        task.save(update_fields=["current_evidence"])
        return task, evidence

    @staticmethod
    def _grant(role, code):
        permission, _created = Permission.objects.get_or_create(
            permission_code=code,
            defaults={
                "permission_name": code,
                "module_name": "compliance",
                "risk_level": Permission.RISK_CRITICAL,
            },
        )
        RolePermission.objects.get_or_create(role=role, permission=permission)

    def _auth(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            data=json.dumps({"email": user.email, "password": "StatutoryPass123!"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {"HTTP_AUTHORIZATION": f"Bearer {response.json()['data']['access_token']}"}
