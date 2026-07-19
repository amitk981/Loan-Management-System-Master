import json
from uuid import uuid4

from django.test import Client, TestCase
from django.utils import timezone


class SubsidiaryDeductionReconciliationApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_bank_statement_matching_api import (
            BankStatementMatchingApiTests,
        )

        fixture = BankStatementMatchingApiTests(
            "test_exact_statement_evidence_matches_one_receipt_without_financial_mutation"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.account
        self.actor = fixture.actor
        fixture.fixture.fixture.fixture.owner.fixture.fixture._grant(
            self.actor, "finance.repayment.allocate"
        )
        self.client = Client()
        self.auth = fixture.auth
        self.subsidiary_company_id = uuid4()

    def test_verified_agreement_allows_subsidiary_deduction_capture(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import (
            LoanAccount,
            Repayment,
            SubsidiaryDeductionEvidence,
        )

        agreement = self._verified_tri_party_agreement()
        account_before = LoanAccount.objects.values().get(pk=self.account.pk)

        payload = self._payload()
        response = self._capture(payload, "subsidiary-capture-001")

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        repayment = Repayment.objects.get(pk=data["repayment_id"])
        evidence = SubsidiaryDeductionEvidence.objects.get(repayment=repayment)
        self.assertEqual(repayment.repayment_source, "subsidiary_deduction")
        self.assertEqual(repayment.payment_method, "subsidiary_transfer")
        self.assertEqual(repayment.allocation_status, "pending")
        self.assertEqual(repayment.sap_posting_status, "pending")
        self.assertEqual(evidence.tri_party_agreement_id, agreement.pk)
        self.assertEqual(
            str(evidence.subsidiary_company_id), payload["subsidiary_company_id"]
        )
        self.assertEqual(evidence.produce_payment_reference, "PRODUCE-PAY-001")
        self.assertEqual(evidence.transfer_reference, "SUB-TRANSFER-001")
        self.assertEqual(evidence.reconciliation_status, "pending_statement")
        self.assertEqual(evidence.treasury_verification_status, "pending")
        audit = AuditLog.objects.get(action="repayment.receipt_created")
        self.assertNotIn("PRODUCE-PAY-001", str(audit.new_value_json))
        self.assertNotIn("SUB-TRANSFER-001", str(audit.new_value_json))
        self.assertNotIn("Deducted under", str(audit.new_value_json))
        self.assertEqual(LoanAccount.objects.values().get(pk=self.account.pk), account_before)
        self.assertEqual(data["tri_party_agreement_id"], str(agreement.pk))
        self.assertEqual(data["reconciliation_status"], "pending_statement")

    def test_exact_statement_treasury_sap_and_canonical_allocation_complete_in_order(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import (
            LoanAccount,
            RepaymentAllocation,
            RepaymentLedgerEntry,
            RepaymentSchedule,
            SubsidiaryDeductionEvidence,
        )

        self._verified_tri_party_agreement()
        captured = self._capture(self._payload(), "subsidiary-e2e-capture")
        self.assertEqual(captured.status_code, 200, captured.content)
        repayment_id = captured.json()["data"]["repayment_id"]
        before = LoanAccount.objects.get(pk=self.account.pk)
        principal_before = before.principal_outstanding
        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=self.account.repayment_date,
            principal_due=before.principal_outstanding,
            interest_due=before.interest_outstanding,
            charges_due=before.charges_outstanding,
            total_due=before.total_outstanding,
            schedule_status="pending",
        )

        premature_sap = self._mark_sap(repayment_id)
        self.assertEqual(premature_sap.status_code, 409, premature_sap.content)

        imported = self.fixture._upload(
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-15,2026-12-15,75000.00,Payment for "
            f"{self.account.member.legal_name} application "
            f"{self.account.loan_application.application_reference_number},"
            f"SUB-TRANSFER-001,{self.account.loan_account_number}\n",
            key="subsidiary-e2e-statement",
        )
        self.assertEqual(imported.status_code, 200, imported.content)
        self.assertEqual(imported.json()["data"]["matched_count"], 1)

        verified = self.client.post(
            f"/api/v1/repayments/{repayment_id}/verify-subsidiary-deduction/",
            data=json.dumps({"remarks": "Treasury verified the exact statement line."}),
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-subsidiary-treasury-001",
            **self.auth,
        )
        self.assertEqual(verified.status_code, 200, verified.content)
        self.assertEqual(verified.json()["data"]["reconciliation_status"], "reconciled")
        self.assertEqual(
            verified.json()["data"]["treasury_verification_status"], "verified"
        )
        verified_replay = self.client.post(
            f"/api/v1/repayments/{repayment_id}/verify-subsidiary-deduction/",
            data=json.dumps({"remarks": "Treasury verified the exact statement line."}),
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-subsidiary-treasury-001",
            **self.auth,
        )
        changed_verification = self.client.post(
            f"/api/v1/repayments/{repayment_id}/verify-subsidiary-deduction/",
            data=json.dumps({"remarks": "Changed terminal verification."}),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(verified_replay.status_code, 200, verified_replay.content)
        self.assertEqual(changed_verification.status_code, 409, changed_verification.content)

        posted = self._mark_sap(repayment_id)
        replay = self._mark_sap(repayment_id)
        changed_posting = self._mark_sap(
            repayment_id, sap_entry_reference="SAP-SUBSIDIARY-CHANGED"
        )
        self.assertEqual(posted.status_code, 200, posted.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(changed_posting.status_code, 409, changed_posting.content)
        self.assertEqual(replay.json()["data"], posted.json()["data"])

        allocated = self.client.post(
            f"/api/v1/repayments/{repayment_id}/allocate/",
            data=json.dumps(
                {
                    "allocation_rule": "principal_first",
                    "remarks": "Subsidiary receipt allocated through canonical 010C.",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="subsidiary-e2e-allocation",
            **self.auth,
        )
        self.assertEqual(allocated.status_code, 200, allocated.content)
        self.account.refresh_from_db()
        evidence = SubsidiaryDeductionEvidence.objects.get(repayment_id=repayment_id)
        self.assertEqual(evidence.reconciliation_status, "reconciled")
        self.assertEqual(evidence.treasury_verification_status, "verified")
        self.assertEqual(
            self.account.principal_outstanding, principal_before - evidence.repayment.amount_received
        )
        self.assertEqual(RepaymentAllocation.objects.filter(repayment_id=repayment_id).count(), 1)
        self.assertEqual(RepaymentLedgerEntry.objects.filter(allocation__repayment_id=repayment_id).count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="repayment.subsidiary_treasury_verified").count(), 1
        )
        self.assertEqual(AuditLog.objects.filter(action="repayment.sap_posted").count(), 1)

    def test_capture_validation_agreement_duplicates_and_replay_are_zero_balance_write(self):
        from sfpcl_credit.loans.models import LoanAccount, Repayment

        account_before = LoanAccount.objects.values().get(pk=self.account.pk)
        missing_agreement = self._capture(self._payload(), "missing-agreement")
        self.assertEqual(missing_agreement.status_code, 409, missing_agreement.content)
        self.assertEqual(Repayment.objects.count(), 0)

        self._verified_tri_party_agreement()
        invalid_cases = (
            ({**self._payload(), "amount_received": "-1.00"}, "negative"),
            ({**self._payload(), "subsidiary_company_id": "not-a-uuid"}, "company"),
            ({**self._payload(), "produce_payment_reference": " "}, "produce"),
            ({**self._payload(), "transfer_reference": " "}, "transfer"),
            (
                {**self._payload(), "bank_reference_number": "DIFFERENT-TRANSFER"},
                "conflicting-transfer",
            ),
        )
        for payload, key in invalid_cases:
            with self.subTest(key=key):
                response = self._capture(payload, key)
                self.assertEqual(response.status_code, 400, response.content)
                self.assertEqual(Repayment.objects.count(), 0)

        payload = self._payload()
        created = self._capture(payload, "stable-subsidiary-key")
        replay = self._capture(payload, "stable-subsidiary-key")
        duplicate_transfer = self._capture(payload, "different-subsidiary-key")
        duplicate_produce = self._capture(
            {
                **payload,
                "bank_reference_number": "SUB-TRANSFER-002",
                "transfer_reference": "SUB-TRANSFER-002",
            },
            "different-produce-key",
        )
        self.assertEqual(created.status_code, 200, created.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(duplicate_transfer.status_code, 409, duplicate_transfer.content)
        self.assertEqual(duplicate_produce.status_code, 409, duplicate_produce.content)
        self.assertEqual(Repayment.objects.count(), 1)
        self.assertEqual(
            replay.json()["data"]["original_response"], created.json()["data"]
        )
        self.assertEqual(LoanAccount.objects.values().get(pk=self.account.pk), account_before)

    def test_capture_can_claim_one_preexisting_exact_statement_through_010d_owner(self):
        from sfpcl_credit.loans.models import BankStatementLine, LoanAccount

        self._verified_tri_party_agreement()
        account_before = LoanAccount.objects.values().get(pk=self.account.pk)
        imported = self.fixture._upload(
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-15,2026-12-15,75000.00,Payment for "
            f"{self.account.member.legal_name} application "
            f"{self.account.loan_application.application_reference_number},"
            f"SUB-TRANSFER-001,{self.account.loan_account_number}\n",
            key="subsidiary-preexisting-statement",
        )
        self.assertEqual(imported.status_code, 200, imported.content)
        self.assertEqual(imported.json()["data"]["unmatched_count"], 1)
        line_id = imported.json()["data"]["lines"][0]["bank_statement_line_id"]

        captured = self._capture(
            {**self._payload(), "bank_statement_line_id": line_id},
            "subsidiary-preexisting-capture",
        )

        self.assertEqual(captured.status_code, 200, captured.content)
        self.assertEqual(captured.json()["data"]["bank_statement_line_id"], line_id)
        line = BankStatementLine.objects.get(pk=line_id)
        self.assertEqual(line.match_status, "matched")
        self.assertEqual(
            str(line.matched_repayment_id), captured.json()["data"]["repayment_id"]
        )
        self.assertEqual(LoanAccount.objects.values().get(pk=self.account.pk), account_before)

    def test_unclear_statement_and_excess_amount_remain_nonallocating_exceptions(self):
        from sfpcl_credit.loans.models import (
            LoanAccount,
            RepaymentAllocation,
            RepaymentLedgerEntry,
            SubsidiaryDeductionEvidence,
        )

        self._verified_tri_party_agreement()
        captured = self._capture(self._payload(), "unclear-subsidiary-capture")
        repayment_id = captured.json()["data"]["repayment_id"]
        account_before = LoanAccount.objects.values().get(pk=self.account.pk)
        unclear = self.fixture._upload(
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-15,2026-12-15,75000.00,Unclear produce transfer,"
            f"SUB-TRANSFER-001,{self.account.loan_account_number}\n",
            key="unclear-subsidiary-statement",
        )
        self.assertEqual(unclear.status_code, 200, unclear.content)
        self.assertEqual(unclear.json()["data"]["matched_count"], 0)
        self.assertEqual(unclear.json()["data"]["unmatched_count"], 1)
        self.assertEqual(
            unclear.json()["data"]["lines"][0]["match_reason_code"],
            "missing_borrower_and_application_narration",
        )
        blocked = self.client.post(
            f"/api/v1/repayments/{repayment_id}/verify-subsidiary-deduction/",
            data=json.dumps({"remarks": "Cannot verify unclear narration."}),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(blocked.status_code, 409, blocked.content)
        self.assertEqual(LoanAccount.objects.values().get(pk=self.account.pk), account_before)
        self.assertEqual(RepaymentAllocation.objects.count(), 0)
        self.assertEqual(RepaymentLedgerEntry.objects.count(), 0)

        # Authorised manual reconciliation retains the unclear line but excess stays exceptional.
        line_id = unclear.json()["data"]["lines"][0]["bank_statement_line_id"]
        matched = self.client.post(
            f"/api/v1/bank-statement-lines/{line_id}/match/",
            data=json.dumps(
                {
                    "repayment_id": repayment_id,
                    "reason": "Authorised evidence review identified the borrower.",
                }
            ),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(matched.status_code, 200, matched.content)
        LoanAccount.objects.filter(pk=self.account.pk).update(
            principal_outstanding="50000.00", total_outstanding="50000.00"
        )
        exception = self.client.post(
            f"/api/v1/repayments/{repayment_id}/verify-subsidiary-deduction/",
            data=json.dumps({"remarks": "Transfer exceeds known outstanding."}),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(exception.status_code, 200, exception.content)
        evidence = SubsidiaryDeductionEvidence.objects.get(repayment_id=repayment_id)
        self.assertEqual(evidence.reconciliation_status, "exception")
        self.assertEqual(evidence.treasury_verification_status, "pending")
        self.assertEqual(RepaymentAllocation.objects.count(), 0)
        self.assertEqual(RepaymentLedgerEntry.objects.count(), 0)

    def test_effective_role_permission_and_nondisclosing_scope_guard_every_mutation(self):
        helper = self.fixture.fixture.fixture.fixture.owner.fixture.fixture
        wrong_role = helper._user(
            "subsidiary_test_auditor", "Subsidiary Permission-Only Auditor"
        )
        helper._grant(
            wrong_role,
            "finance.repayment.create",
            "finance.repayment.allocate",
            "finance.repayment.mark_sap_posted",
        )
        auth_helper = self.fixture.fixture.fixture.fixture.owner.fixture
        wrong_auth = auth_helper._auth(wrong_role)

        for auth, expected in (({}, 401), (wrong_auth, 403)):
            with self.subTest(expected=expected):
                denied = self.client.post(
                    f"/api/v1/loan-accounts/{self.account.pk}/repayments/",
                    data=json.dumps(self._payload()),
                    content_type="application/json",
                    HTTP_IDEMPOTENCY_KEY=f"authority-{expected}",
                    **auth,
                )
                self.assertEqual(denied.status_code, expected, denied.content)

        self._verified_tri_party_agreement()
        inaccessible = self.client.post(
            f"/api/v1/loan-accounts/{uuid4()}/repayments/",
            data=json.dumps(self._payload()),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="inaccessible-subsidiary-account",
            **self.auth,
        )
        self.assertEqual(inaccessible.status_code, 404, inaccessible.content)

    def _verified_tri_party_agreement(self):
        from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
        from sfpcl_credit.legal_documents.models import LoanDocument

        template_file = DocumentFile.objects.create(
            file_name="subsidiary-agreement.docx",
            storage_provider="local",
            storage_key="templates/subsidiary-agreement.docx",
            checksum_sha256="subsidiary-agreement-template",
            sensitivity_level="internal",
        )
        output = DocumentFile.objects.create(
            file_name="subsidiary-agreement.pdf",
            storage_provider="local",
            storage_key="generated/subsidiary-agreement.pdf",
            checksum_sha256="subsidiary-agreement-output",
            sensitivity_level="confidential",
        )
        template = DocumentTemplate.objects.create(
            template_code=f"subsidiary-{self.account.pk}",
            template_name="Subsidiary tri-party agreement",
            document_type="tri_party_agreement",
            borrower_type="individual_farmer",
            template_version=f"1.0-{self.account.pk}",
            template_file=template_file,
            merge_fields_json=[],
            approval_status="approved",
            effective_from=timezone.localdate(),
        )
        return LoanDocument.objects.create(
            loan_application=self.account.loan_application,
            document_type="tri_party_agreement",
            document_category="legal",
            party_required="borrower",
            document_template=template,
            document=output,
            output_format="pdf",
            generation_status="generated",
            execution_status="executed",
            verification_status="verified",
            renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
            renderer_validated_document_id=output.pk,
            renderer_validated_checksum_sha256=output.checksum_sha256,
            verified_by_user=self.actor,
            verified_at=timezone.now(),
        )

    def _payload(self):
        return {
            "repayment_source": "subsidiary_deduction",
            "amount_received": "75000.00",
            "received_date": "2026-12-15",
            "payment_method": "subsidiary_transfer",
            "bank_reference_number": "SUB-TRANSFER-001",
            "subsidiary_company_id": str(self.subsidiary_company_id),
            "produce_payment_reference": "PRODUCE-PAY-001",
            "transfer_reference": "SUB-TRANSFER-001",
            "remarks": "Deducted under the verified tri-party agreement.",
        }

    def _capture(self, payload, key):
        return self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/repayments/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=key,
            HTTP_X_REQUEST_ID="req-subsidiary-capture-001",
            **self.auth,
        )

    def _mark_sap(self, repayment_id, *, sap_entry_reference="SAP-SUBSIDIARY-001"):
        return self.client.post(
            f"/api/v1/repayments/{repayment_id}/mark-sap-posted/",
            data=json.dumps(
                {
                    "sap_entry_reference": sap_entry_reference,
                    "sap_posted_at": "2026-12-16T10:00:00Z",
                    "remarks": "Treasury receipt posted in SAP.",
                }
            ),
            content_type="application/json",
            **self.auth,
        )
