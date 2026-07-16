from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from django.db import close_old_connections, connection, connections
from django.test import Client, TestCase, TransactionTestCase
from unittest import skipUnless
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import ApprovalCase, SanctionDecision
from sfpcl_credit.credit.models import LoanAppraisalNote, RiskAssessment
from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
from sfpcl_credit.identity.models import (
    AuditLog,
    Permission,
    Role,
    RolePermission,
    User,
)
from sfpcl_credit.legal_documents.models import LoanDocument
from sfpcl_credit.loans.models import LoanAccount, LoanStatusHistory, LoanTerms
from sfpcl_credit.loans.modules.loan_account_lifecycle import (
    RequestMetadata,
    create_loan_account,
)
from sfpcl_credit.members.models import Member, Nominee, Shareholding
from sfpcl_credit.sap_workflow.models import SapCustomerCode
from sfpcl_credit.tests.api_contracts import assert_success_envelope
from sfpcl_credit.workflows.models import WorkflowEvent


class LoanAccountCreationApiTests(TestCase):
    password = "LoanAccountPass123!"

    def setUp(self):
        self.client = Client()
        self.actor = self._user("loan_account_creator", "Loan Account Creator")
        self._grant(self.actor, "finance.loan_account.create")
        (
            self.application,
            self.case,
            self.sanction,
            self.shareholding,
        ) = self._terminal_application()
        self._legal_document("term_sheet")
        self._legal_document("loan_agreement")

    def test_terminal_sanction_creates_unfunded_account_terms_and_evidence(self):
        response = self._post(
            {
                "sanction_decision_id": str(self.sanction.pk),
                "loan_account_number": "  LN-2026-00025  ",
            }
        )

        self.assertEqual(response.status_code, 200, response.content)
        assert_success_envelope(self, response.json())
        data = response.json()["data"]
        account = LoanAccount.objects.get(pk=data["loan_account_id"])
        terms = LoanTerms.objects.get(pk=data["loan_terms_id"])
        self.assertEqual(data["loan_account_number"], "LN-2026-00025")
        self.assertEqual(data["loan_account_status"], "sanctioned")
        self.assertEqual(data["sanctioned_amount"], "400000.00")
        self.assertEqual(data["loan_type"], "short_term")
        self.assertEqual(data["interest_rate_type"], "floating")
        self.assertEqual(data["current_interest_rate"], "9.2500")
        self.assertEqual(data["repayment_date"], "2027-06-22")
        self.assertIsNone(data["sap_customer_code_id"])
        self.assertEqual(
            (
                account.disbursed_amount,
                account.principal_outstanding,
                account.interest_outstanding,
                account.charges_outstanding,
                account.total_outstanding,
            ),
            (0, 0, 0, 0, 0),
        )
        self.assertEqual(terms.loan_account_id, account.pk)
        self.assertEqual(terms.borrower_details_snapshot_json, {
            "member_id": str(self.application.member_id),
            "legal_name": "Ramesh Patil",
            "member_type": "individual_farmer",
            "folio_number": "FOL-LOAN-001",
        })
        self.assertEqual(terms.nominee_details_snapshot_json, {
            "nominee_id": str(self.application.nominee_id),
            "name": "Anita Patil",
            "relationship": "spouse",
        })
        self.assertEqual(terms.shareholding_snapshot_json, {
            "shareholding_id": str(self.shareholding.pk),
            "folio_number": "FOL-LOAN-001",
            "number_of_shares": 100,
            "holding_mode": "physical",
        })
        self.assertEqual(terms.purpose, "Seasonal crop finance")
        self.assertEqual(terms.security_details_json, {
            "summary": "Standard member security package."
        })
        self.assertEqual(terms.dispute_resolution_text, "SFPCL dispute policy applies.")
        self.assertEqual(terms.term_sheet_document_id, self.term_sheet.document_id)
        self.assertEqual(
            terms.loan_agreement_document_id, self.loan_agreement.document_id
        )
        history = LoanStatusHistory.objects.get(loan_account=account)
        self.assertIsNone(history.from_status)
        self.assertEqual(history.to_status, "sanctioned")
        self.assertEqual(history.changed_by_user_id, self.actor.pk)
        self.assertEqual(history.loan_application_id_snapshot, self.application.pk)
        self.assertEqual(history.member_id_snapshot, self.application.member_id)
        self.assertEqual(history.sanction_decision_id_snapshot, self.sanction.pk)
        self.assertIsNone(history.sap_customer_code_id_snapshot)
        self.assertEqual(history.loan_terms_id_snapshot, terms.pk)
        self.assertFalse(history.replay_flag)
        self.assertEqual(history.outcome, "created")
        self.assertEqual(
            AuditLog.objects.filter(
                action="finance.loan_account.created", entity_id=account.pk
            ).count(),
            1,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="LoanAccountCreated", entity_id=account.pk
            ).count(),
            1,
        )
        secret_surface = str(response.json()) + str(
            list(
                AuditLog.objects.filter(
                    action="finance.loan_account.created"
                ).values_list("new_value_json", flat=True)
            )
        ) + str(list(LoanStatusHistory.objects.values())) + str(
            list(WorkflowEvent.objects.filter(workflow_name="LoanAccountCreated").values())
        )
        for secret in (
            "protected-pan",
            "protected-aadhaar",
            "protected-nominee-pan",
            "protected-nominee-aadhaar",
            "output-term_sheet",
            "output-loan_agreement",
        ):
            self.assertNotIn(secret, secret_surface)

    def test_exact_retry_replays_without_writes_and_changed_retry_conflicts(self):
        payload = {
            "sanction_decision_id": str(self.sanction.pk),
            "loan_account_number": "LN-2026-00025",
        }
        first = self._post(payload)
        replay = self._post(payload)

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(first.json()["data"], replay.json()["data"])
        self.assertEqual(LoanAccount.objects.count(), 1)
        self.assertEqual(LoanTerms.objects.count(), 1)
        self.assertEqual(LoanStatusHistory.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="finance.loan_account.created").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="LoanAccountCreated").count(), 1
        )

        changed = self._post({**payload, "loan_account_number": "LN-2026-99999"})
        self.assertEqual(changed.status_code, 409, changed.content)
        self.assertEqual(changed.json()["error"]["code"], "LOAN_ACCOUNT_CONFLICT")
        self.assertEqual(LoanAccount.objects.count(), 1)
        self.assertEqual(LoanTerms.objects.count(), 1)
        self.assertEqual(LoanStatusHistory.objects.count(), 1)

    def test_non_object_json_is_a_stable_zero_write_validation_error(self):
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/create-loan-account/",
            data="[]",
            content_type="application/json",
            **self._auth(self.actor),
        )

        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(response.json()["error"]["code"], "VALIDATION_ERROR")
        self.assertEqual(LoanAccount.objects.count(), 0)
        self.assertEqual(LoanTerms.objects.count(), 0)
        self.assertEqual(LoanStatusHistory.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="finance.loan_account.created").count(), 0
        )

    def test_missing_malformed_and_overlength_payloads_are_zero_write(self):
        payloads = (
            ({}, {"sanction_decision_id", "loan_account_number"}),
            (
                {
                    "sanction_decision_id": "not-a-uuid",
                    "loan_account_number": "LN-BAD-UUID",
                },
                {"sanction_decision_id"},
            ),
            (
                {
                    "sanction_decision_id": str(self.sanction.pk),
                    "loan_account_number": "X" * 81,
                },
                {"loan_account_number"},
            ),
        )
        for payload, expected_fields in payloads:
            with self.subTest(payload=payload):
                response = self._post(payload)
                self.assertEqual(response.status_code, 400, response.content)
                self.assertEqual(
                    set(response.json()["error"]["field_errors"]), expected_fields
                )
        self.assertEqual(LoanAccount.objects.count(), 0)
        self.assertEqual(LoanTerms.objects.count(), 0)

    def test_permission_scope_stale_source_and_missing_evidence_are_zero_write(self):
        ungranted = self._user("ungranted_account_actor", "Ungranted Actor")
        denied = self._post(
            {
                "sanction_decision_id": str(self.sanction.pk),
                "loan_account_number": "LN-DENIED-001",
            },
            actor=ungranted,
        )
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(denied.json()["error"]["code"], "FORBIDDEN")

        scoped = self._user("scoped_account_actor", "Scoped Actor")
        self._grant(scoped, "finance.loan_account.create")
        outside_scope = self._post(
            {
                "sanction_decision_id": str(self.sanction.pk),
                "loan_account_number": "LN-DENIED-002",
            },
            actor=scoped,
        )
        self.assertEqual(outside_scope.status_code, 403, outside_scope.content)
        self.assertEqual(
            outside_scope.json()["error"]["code"], "OBJECT_ACCESS_DENIED"
        )

        unknown = self._post(
            {
                "sanction_decision_id": str(self.sanction.pk),
                "loan_account_number": "LN-UNKNOWN-001",
                "sanctioned_amount": "1.00",
            }
        )
        self.assertEqual(unknown.status_code, 400, unknown.content)
        self.assertEqual(
            unknown.json()["error"]["field_errors"],
            {"sanctioned_amount": "Unknown field."},
        )

        stale = self._post(
            {
                "sanction_decision_id": str(uuid4()),
                "loan_account_number": "LN-STALE-001",
            }
        )
        self.assertEqual(stale.status_code, 409, stale.content)
        self.assertEqual(stale.json()["error"]["code"], "STALE_STATE")

        ApprovalCase.objects.filter(pk=self.case.pk).update(
            current_status=ApprovalCase.STATUS_REJECTED
        )
        non_terminal = self._post(
            {
                "sanction_decision_id": str(self.sanction.pk),
                "loan_account_number": "LN-NON-TERMINAL-001",
            }
        )
        self.assertEqual(non_terminal.status_code, 409, non_terminal.content)
        ApprovalCase.objects.filter(pk=self.case.pk).update(
            current_status=ApprovalCase.STATUS_APPROVED
        )

        self.term_sheet.delete()
        missing_evidence = self._post(
            {
                "sanction_decision_id": str(self.sanction.pk),
                "loan_account_number": "LN-MISSING-DOC-001",
            }
        )
        self.assertEqual(missing_evidence.status_code, 400, missing_evidence.content)
        self.assertEqual(
            missing_evidence.json()["error"]["field_errors"],
            {"term_sheet": "Current executed and verified legal evidence is required."},
        )
        self.assertEqual(LoanAccount.objects.count(), 0)
        self.assertEqual(LoanTerms.objects.count(), 0)
        self.assertEqual(LoanStatusHistory.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="finance.loan_account.created").count(), 0
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="LoanAccountCreated").count(), 0
        )

    def test_inactive_actor_token_is_rejected_before_any_write(self):
        headers = self._auth(self.actor)
        self.actor.status = "inactive"
        self.actor.save(update_fields=["status"])
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/create-loan-account/",
            {
                "sanction_decision_id": str(self.sanction.pk),
                "loan_account_number": "LN-INACTIVE-001",
            },
            content_type="application/json",
            **headers,
        )
        self.assertEqual(response.status_code, 401, response.content)
        self.assertEqual(LoanAccount.objects.count(), 0)
        self.assertEqual(LoanTerms.objects.count(), 0)
        self.assertEqual(LoanStatusHistory.objects.count(), 0)

    def test_public_sap_decision_links_only_exact_active_member_application(self):
        code = SapCustomerCode.objects.create(
            member=self.application.member,
            sap_customer_code="CUST-LOAN-001",
            created_for_loan_application=self.application,
            created_by_user=self.actor,
            status="active",
        )
        decision = SimpleNamespace(
            customer_code_id=code.pk,
            member_id=self.application.member_id,
            profile_request_id=uuid4(),
            loan_application_id=self.application.pk,
            status="active",
        )
        with patch(
            "sfpcl_credit.loans.modules.loan_account_lifecycle."
            "SapCustomerProfileModule.get_customer_code_for_member",
            return_value=decision,
        ) as selector:
            response = self._post(
                {
                    "sanction_decision_id": str(self.sanction.pk),
                    "loan_account_number": "LN-SAP-001",
                }
            )
        selector.assert_called_once_with(
            self.application.member_id, for_update=True
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"]["sap_customer_code_id"], str(code.pk))
        self.assertEqual(LoanAccount.objects.get().sap_customer_code_id, code.pk)

    def test_inactive_or_cross_application_sap_decision_is_not_linked(self):
        decision = SimpleNamespace(
            customer_code_id=uuid4(),
            member_id=self.application.member_id,
            profile_request_id=uuid4(),
            loan_application_id=uuid4(),
            status="inactive",
        )
        with patch(
            "sfpcl_credit.loans.modules.loan_account_lifecycle."
            "SapCustomerProfileModule.get_customer_code_for_member",
            return_value=decision,
        ):
            response = self._post(
                {
                    "sanction_decision_id": str(self.sanction.pk),
                    "loan_account_number": "LN-SAP-INCOHERENT-001",
                }
            )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIsNone(response.json()["data"]["sap_customer_code_id"])
        self.assertIsNone(LoanAccount.objects.get().sap_customer_code_id)

    def test_case_and_whitespace_equivalent_number_is_globally_rejected(self):
        first = self._post(
            {
                "sanction_decision_id": str(self.sanction.pk),
                "loan_account_number": "LN Shared 001",
            }
        )
        self.assertEqual(first.status_code, 200, first.content)
        application, _case, sanction, _holding = self._terminal_application("002")
        self._legal_document("term_sheet", application=application)
        self._legal_document("loan_agreement", application=application)

        duplicate = self._post(
            {
                "sanction_decision_id": str(sanction.pk),
                "loan_account_number": "  ln   shared 001  ",
            },
            application=application,
        )
        self.assertEqual(duplicate.status_code, 409, duplicate.content)
        self.assertEqual(
            duplicate.json()["error"]["code"], "LOAN_ACCOUNT_CONFLICT"
        )
        self.assertEqual(LoanAccount.objects.count(), 1)
        self.assertEqual(LoanTerms.objects.count(), 1)
        self.assertEqual(LoanStatusHistory.objects.count(), 1)

    def test_loan_owner_imports_only_the_public_sap_module(self):
        source = Path(__file__).parents[1] / "loans/modules/loan_account_lifecycle.py"
        text = source.read_text(encoding="utf-8")
        self.assertIn(
            "sfpcl_credit.sap_workflow.modules.sap_customer_profile import", text
        )
        for forbidden in (
            "sfpcl_credit.finance",
            "sfpcl_credit.legal_documents.models",
            "annexure_storage",
            "ManualSapAdapter",
            "SapRequestConflict",
        ):
            self.assertNotIn(forbidden, text)

    def test_missing_governed_dispute_term_fails_closed(self):
        facts = dict(self.case.appraisal_facts_json)
        facts.pop("dispute_resolution", None)
        ApprovalCase.objects.filter(pk=self.case.pk).update(appraisal_facts_json=facts)

        response = self._post(
            {
                "sanction_decision_id": str(self.sanction.pk),
                "loan_account_number": "LN-MISSING-DISPUTE-001",
            }
        )
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(
            response.json()["error"]["field_errors"],
            {"dispute_resolution": "Current governed dispute term is required."},
        )
        self.assertEqual(LoanAccount.objects.count(), 0)

    def test_newer_nonterminal_legal_document_blocks_stale_eligible_fallback(self):
        self._legal_document(
            "term_sheet", variant="replacement", execution_status="pending"
        )
        response = self._post(
            {
                "sanction_decision_id": str(self.sanction.pk),
                "loan_account_number": "LN-STALE-TERM-SHEET-001",
            }
        )
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(
            response.json()["error"]["field_errors"],
            {"term_sheet": "Current executed and verified legal evidence is required."},
        )
        self.assertEqual(LoanAccount.objects.count(), 0)

    def test_terms_and_status_history_are_immutable_and_links_are_nullable(self):
        response = self._post(
            {
                "sanction_decision_id": str(self.sanction.pk),
                "loan_account_number": "LN-IMMUTABLE-001",
            }
        )
        self.assertEqual(response.status_code, 200, response.content)
        terms = LoanTerms.objects.get()
        with self.assertRaisesMessage(Exception, "Loan terms are immutable"):
            LoanTerms.objects.filter(pk=terms.pk).update(purpose="changed")
        with self.assertRaisesMessage(Exception, "Loan terms are immutable"):
            terms.save()
        history = LoanStatusHistory.objects.get()
        with self.assertRaisesMessage(Exception, "append-only"):
            LoanStatusHistory.objects.filter(pk=history.pk).update(reason="changed")
        with self.assertRaisesMessage(Exception, "append-only"):
            history.delete()
        self.assertTrue(LoanTerms._meta.get_field("term_sheet_document").null)
        self.assertTrue(LoanTerms._meta.get_field("loan_agreement_document").null)

    def _terminal_application(self, suffix="001"):
        member = Member.objects.create(
            member_number=f"MEM-LOAN-{suffix}",
            member_type="individual_farmer",
            legal_name="Ramesh Patil",
            display_name="Ramesh Patil",
            folio_number=f"FOL-LOAN-{suffix}",
            membership_status="active",
            pan_encrypted="protected-pan",
            pan_hash=f"loan-account-pan-hash-{suffix}",
            aadhaar_encrypted="protected-aadhaar",
            aadhaar_hash=f"loan-account-aadhaar-hash-{suffix}",
            kyc_status="verified",
            default_status="no_default",
        )
        nominee = Nominee.objects.create(
            member=member,
            nominee_name="Anita Patil",
            gender="female",
            relationship_to_borrower="spouse",
            pan_encrypted="protected-nominee-pan",
            pan_hash=f"loan-account-nominee-pan-{suffix}",
            aadhaar_encrypted="protected-nominee-aadhaar",
            aadhaar_hash=f"loan-account-nominee-aadhaar-{suffix}",
            kyc_status="verified",
        )
        shareholding = Shareholding.objects.create(
            member=member,
            folio_number=member.folio_number,
            number_of_shares=100,
            holding_mode="physical",
            pledged_share_count=0,
            available_share_count=100,
            status="active",
        )
        application = LoanApplication.objects.create(
            application_reference_number=f"LO-ACCOUNT-{suffix}",
            member=member,
            nominee=nominee,
            borrower_type=member.member_type,
            received_by_user=self.actor,
            created_by_user=self.actor,
            required_loan_amount="400000.00",
            requested_tenure_months=12,
            declared_purpose="Seasonal crop finance",
            purpose_category="crop_finance",
            loan_type_requested="short_term",
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
            assessed_by_user=self.actor,
        )
        note = LoanAppraisalNote.objects.create(
            loan_application=application,
            prepared_by_user=self.actor,
            reviewed_by_user=self.actor,
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
            submitted_by_user=self.actor,
            submission_remarks="Approved loan account source facts.",
            current_status=ApprovalCase.STATUS_APPROVED,
            amount="400000.00",
            related_entity_type="loan_application",
            related_entity_id=application.pk,
            reason_for_approval="Approved by sanction committee.",
            closed_at=timezone.now(),
            appraisal_facts_json={
                "borrower": {
                    "member_id": str(member.pk),
                    "name": member.legal_name,
                    "member_type": member.member_type,
                    "folio_number": member.folio_number,
                },
                "nominee": {
                    "nominee_id": str(nominee.pk),
                    "name": nominee.nominee_name,
                    "relationship": nominee.relationship_to_borrower,
                },
                "shareholding": {
                    "shareholding_id": str(shareholding.pk),
                    "folio_number": shareholding.folio_number,
                    "number_of_shares": shareholding.number_of_shares,
                    "holding_mode": shareholding.holding_mode,
                },
                "purpose": {
                    "category": application.purpose_category,
                    "description": application.declared_purpose,
                },
                "dispute_resolution": "SFPCL dispute policy applies.",
            },
        )
        sanction = SanctionDecision.objects.create(
            loan_application=application,
            approval_case=case,
            decision="sanctioned",
            sanctioned_amount="400000.00",
            sanctioned_tenure_months=12,
            interest_rate_type="floating",
            interest_rate_value="9.2500",
            repayment_date="2027-06-22",
            penal_interest_rate="2.0000",
            charges_json={"processing_fee": "1000.00"},
            security_required_summary="Standard member security package.",
            conditions_precedent="Documentation conditions satisfied.",
            decision_reason="Approved.",
        )
        return application, case, sanction, shareholding

    def _legal_document(
        self,
        document_type,
        application=None,
        *,
        variant="current",
        execution_status="executed",
    ):
        application = application or self.application
        reference = application.application_reference_number.lower()
        template_file = DocumentFile.objects.create(
            file_name=f"{document_type}.docx",
            storage_provider="local",
            storage_key=f"templates/{document_type}.docx",
            checksum_sha256=f"template-{document_type}",
            sensitivity_level="internal",
        )
        output = DocumentFile.objects.create(
            file_name=f"{document_type}.pdf",
            storage_provider="local",
            storage_key=f"generated/{document_type}.pdf",
            checksum_sha256=f"output-{document_type}",
            sensitivity_level="confidential",
        )
        template = DocumentTemplate.objects.create(
            template_code=f"009c-{reference}-{document_type}-{variant}",
            template_name=f"009C {document_type}",
            document_type=document_type,
            borrower_type="individual_farmer",
            template_version=f"{reference}-{variant}",
            template_file=template_file,
            merge_fields_json=[],
            approval_status="approved",
            effective_from=timezone.localdate(),
        )
        document = LoanDocument.objects.create(
            loan_application=application,
            document_type=document_type,
            document_category="legal",
            party_required="borrower",
            document_template=template,
            document=output,
            output_format="pdf",
            generation_status="generated",
            execution_status=execution_status,
            verification_status="verified",
            renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
            renderer_validated_document_id=output.pk,
            renderer_validated_checksum_sha256=output.checksum_sha256,
            verified_by_user=self.actor,
            verified_at=timezone.now(),
        )
        if application == self.application:
            setattr(self, document_type, document)
        return document

    def _post(self, payload, actor=None, application=None):
        application = application or self.application
        return self.client.post(
            f"/api/v1/loan-applications/{application.pk}/create-loan-account/",
            payload,
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-loan-account-001",
            HTTP_USER_AGENT="loan account contract test",
            REMOTE_ADDR="203.0.113.40",
            **self._auth(actor or self.actor),
        )

    def _user(self, role_code, full_name):
        role = Role.objects.create(
            role_code=role_code,
            role_name=full_name,
            status="active",
        )
        user = User.objects.create(
            full_name=full_name,
            email=f"{role_code}@sfpcl.example",
            status="active",
            primary_role=role,
        )
        user.set_password(self.password)
        user.save()
        return user

    @staticmethod
    def _grant(user, *permission_codes):
        for code in permission_codes:
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "finance",
                    "risk_level": "critical",
                },
            )
            RolePermission.objects.get_or_create(
                role=user.primary_role, permission=permission
            )

    def _auth(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {
            "HTTP_AUTHORIZATION": f"Bearer {response.json()['data']['access_token']}"
        }


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class LoanAccountCreationRaceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.fixture = LoanAccountCreationApiTests(
            methodName=(
                "test_terminal_sanction_creates_unfunded_account_terms_and_evidence"
            )
        )
        self.fixture.setUp()

    def test_five_concurrent_exact_creates_retain_one_complete_winner_tuple(self):
        gate = Barrier(5)

        def contender(index):
            close_old_connections()
            try:
                actor = User.objects.get(pk=self.fixture.actor.pk)
                gate.wait(timeout=15)
                result = create_loan_account(
                    actor=actor,
                    application_id=self.fixture.application.pk,
                    payload={
                        "sanction_decision_id": str(self.fixture.sanction.pk),
                        "loan_account_number": "LN-RACE-009C",
                    },
                    metadata=RequestMetadata(
                        request_id=f"009c-race-{index}",
                        ip_address="203.0.113.40",
                        user_agent="009C PostgreSQL race",
                    ),
                )
                return result["loan_account_id"]
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(contender, range(5)))

        self.assertEqual(len(set(results)), 1)
        account = LoanAccount.objects.get()
        self.assertEqual(str(account.pk), results[0])
        self.assertEqual(LoanTerms.objects.filter(loan_account=account).count(), 1)
        self.assertEqual(
            LoanStatusHistory.objects.filter(loan_account=account).count(), 1
        )
        self.assertEqual(
            AuditLog.objects.filter(
                action="finance.loan_account.created", entity_id=account.pk
            ).count(),
            1,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="LoanAccountCreated", entity_id=account.pk
            ).count(),
            1,
        )
