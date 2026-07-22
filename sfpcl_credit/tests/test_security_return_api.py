import json
import uuid
from datetime import date

from django.test import Client, TestCase
from django.utils import timezone

from sfpcl_credit.closure.models import LoanClosure
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.loans.models import LoanAccount


class SecurityReturnApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_loan_account_reads_api import LoanAccountReadApiTests

        fixture = LoanAccountReadApiTests(
            "test_sanctioned_list_and_detail_are_exact_paginated_zero_write_projections"
        )
        fixture.setUp()
        self.fixture = fixture.fixture
        self.account = fixture.account
        LoanAccount.objects.filter(pk=self.account.pk).update(
            loan_account_status="partially_repaid",
            principal_outstanding="0.00",
            interest_outstanding="0.00",
            charges_outstanding="0.00",
            total_outstanding="0.00",
        )
        closer = self.fixture._user("credit_manager", "Security Return Closer")
        self.closer = closer
        self.fixture._grant(closer, "closure.readiness.read", "closure.loan.close")
        response = Client().post(
            f"/api/v1/loan-accounts/{self.account.pk}/closure/",
            data=json.dumps(
                {
                    "closure_type": "full_repayment",
                    "closure_notes": "Canonical balances verified before security return.",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="security-return-fixture-close",
            **self.fixture._auth(closer),
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.closure = LoanClosure.objects.get(loan_account=self.account)
        self.actor = self.fixture._user(
            "company_secretary", "Security Return Company Secretary"
        )
        self.fixture._grant(self.actor, "closure.security_return.record")
        self.auth = self.fixture._auth(self.actor)
        self.client = Client()

    def test_no_security_closure_derives_not_applicable_items_and_completes(self):
        response = self.client.post(
            f"/api/v1/loan-closures/{self.closure.pk}/security-return/",
            data=json.dumps({}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="security-return-none-001",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["status"], "completed")
        self.assertEqual(data["security_package_id"], None)
        self.assertEqual(
            [(item["item_type"], item["status"]) for item in data["items"]],
            [
                ("sh4", "not_applicable"),
                ("blank_cheque", "not_applicable"),
                ("poa", "not_applicable"),
                ("cdsl", "not_applicable"),
            ],
        )
        self.assertFalse(data["idempotency_replayed"])

        counts = {
            "audits": AuditLog.objects.count(),
            "requests": self.closure.security_return.requests.count(),
        }
        replay = self.client.post(
            f"/api/v1/loan-closures/{self.closure.pk}/security-return/",
            data=json.dumps({}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="security-return-none-001",
            **self.auth,
        )
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertTrue(replay.json()["data"]["idempotency_replayed"])
        self.assertEqual(AuditLog.objects.count(), counts["audits"])
        self.assertEqual(self.closure.security_return.requests.count(), counts["requests"])

        changed = self.client.post(
            f"/api/v1/loan-closures/{self.closure.pk}/security-return/",
            data=json.dumps({"items": []}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="security-return-none-001",
            **self.auth,
        )
        self.assertEqual(changed.status_code, 409, changed.content)

    def test_applicable_package_without_owned_instrument_is_rejected(self):
        from sfpcl_credit.closure.models import SecurityReturn
        from sfpcl_credit.security_instruments.models import SecurityPackage

        SecurityPackage.objects.create(
            loan_application_id=self.account.loan_application_id,
            physical_share_security_required_flag=False,
            demat_pledge_required_flag=False,
            poa_required_flag=True,
            blank_cheque_required_flag=False,
        )

        response = self.client.post(
            f"/api/v1/loan-closures/{self.closure.pk}/security-return/",
            data=json.dumps({}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="security-return-missing-owner-001",
            **self.auth,
        )

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(response.json()["error"]["code"], "SECURITY_RETURN_CONFLICT")
        self.assertFalse(SecurityReturn.objects.exists())

    def test_poa_release_requires_owned_identity_recipient_and_acknowledgement(self):
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.legal_documents.models import LoanDocument
        from sfpcl_credit.security_instruments.models import (
            PowerOfAttorney,
            SecurityPackage,
        )

        package = SecurityPackage.objects.create(
            loan_application_id=self.account.loan_application_id,
            physical_share_security_required_flag=False,
            demat_pledge_required_flag=False,
            poa_required_flag=True,
            blank_cheque_required_flag=False,
        )
        source_document = LoanDocument.objects.filter(
            loan_application_id=self.account.loan_application_id
        ).first()
        poa = PowerOfAttorney.objects.create(
            security_package=package,
            borrower_member_id=self.account.member_id,
            nominee_id=self.account.loan_application.nominee_id,
            attorney_user=self.actor,
            purpose_summary="Governed security power for the loan.",
            loan_document=source_document,
            stamp_duty_record_id=self._stamp(source_document).pk,
            notarisation_record_id=self._notary(source_document).pk,
            execution_status="executed",
            effective_from=date(2026, 7, 1),
            status="active",
            prepared_by_user=self.fixture.actor,
            verified_by_user=self.actor,
            activation_workflow_event_id=uuid.uuid4(),
        )
        acknowledgement = DocumentFile.objects.create(
            file_name="security-return-acknowledgement.pdf",
            file_extension="pdf",
            mime_type="application/pdf",
            storage_provider="local",
            storage_key="tests/security-return-acknowledgement.pdf",
            checksum_sha256="a" * 64,
            uploaded_by_user=self.actor,
            sensitivity_level="restricted",
        )
        LoanDocument.objects.create(
            loan_application_id=self.account.loan_application_id,
            document_type="security_return_acknowledgement",
            document_category="closure",
            document=acknowledgement,
            output_format="pdf",
            generation_status="generated",
            execution_status="executed",
            verification_status="verified",
            verified_by_user=self.actor,
            verified_at=timezone.now(),
        )
        released_at = "2026-07-22T10:30:00Z"

        response = self.client.post(
            f"/api/v1/loan-closures/{self.closure.pk}/security-return/",
            data=json.dumps(
                {
                    "security_package_id": str(package.pk),
                    "expected_version": 0,
                    "acknowledgement_document_id": str(acknowledgement.pk),
                    "items": [
                        {
                            "item_type": "poa",
                            "source_item_id": str(poa.pk),
                            "outcome": "released",
                            "returned_released_to": "Borrower authorised recipient",
                            "returned_released_at": released_at,
                        }
                    ],
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="security-return-poa-001",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["status"], "completed")
        self.assertEqual(data["version"], 1)
        poa_item = next(item for item in data["items"] if item["item_type"] == "poa")
        self.assertEqual(poa_item["status"], "released")
        self.assertEqual(poa_item["source_item_id"], str(poa.pk))
        self.assertEqual(
            poa_item["returned_released_to"], "Borrower authorised recipient"
        )

    def test_cdsl_completion_retains_dp_evidence_and_masks_bo_accounts(self):
        from sfpcl_credit.security_instruments.models import (
            CDSLSharePledge,
            SecurityPackage,
        )

        package = SecurityPackage.objects.create(
            loan_application_id=self.account.loan_application_id,
            physical_share_security_required_flag=False,
            demat_pledge_required_flag=True,
            poa_required_flag=True,
            blank_cheque_required_flag=False,
        )
        poa = self._active_poa(package)
        pledge_evidence = self._verified_document("cdsl_pledge_evidence")
        pledge = CDSLSharePledge.objects.create(
            security_package=package,
            pledgor_member_id=self.account.member_id,
            pledgee_entity_name="SFPCL",
            pledgor_bo_account_encrypted="opaque-pledgor-account",
            pledgor_bo_account_hash="pledgor-hash",
            pledgor_bo_account_last4="3456",
            pledgee_bo_account_encrypted="opaque-pledgee-account",
            pledgee_bo_account_hash="pledgee-hash",
            pledgee_bo_account_last4="7654",
            pledgor_dp_name="Pledgor DP",
            pledgee_dp_name="Pledgee DP",
            prf_status="submitted",
            pledge_sequence_number="PSN-CLOSE-001",
            pledge_acceptance_status="accepted",
            pledged_share_count=100,
            agreement_number="AG-CLOSE-001",
            pledge_status="created",
            evidence_document=pledge_evidence,
            created_at_cdsl=timezone.now(),
            prepared_by_user=self.fixture.actor,
            verified_by_user=self.actor,
            acceptance_workflow_event_id=uuid.uuid4(),
        )
        acknowledgement = self._verified_document("security_return_acknowledgement")
        urf = self._verified_document("cdsl_unpledge_request_form")
        completion = self._verified_document("cdsl_unpledge_completion")

        response = self.client.post(
            f"/api/v1/loan-closures/{self.closure.pk}/security-return/",
            data=json.dumps(
                {
                    "security_package_id": str(package.pk),
                    "expected_version": 0,
                    "acknowledgement_document_id": str(acknowledgement.pk),
                    "items": [
                        {
                            "item_type": "poa",
                            "source_item_id": str(poa.pk),
                            "outcome": "released",
                            "returned_released_to": "Borrower authorised recipient",
                            "returned_released_at": "2026-07-22T10:00:00Z",
                        },
                        {
                            "item_type": "cdsl",
                            "source_item_id": str(pledge.pk),
                            "outcome": "completed",
                            "psn": "PSN-CLOSE-001",
                            "urf_document_id": str(urf.pk),
                            "urf_date": "2026-07-21",
                            "unpledge_type": "full",
                            "pledgor_dp_submitted_at": "2026-07-21T09:00:00Z",
                            "pledgee_dp_acted_at": "2026-07-22T09:30:00Z",
                            "pledgee_dp_outcome": "accepted",
                            "auto_unpledge_flag": False,
                            "completed_at": "2026-07-22T09:30:00Z",
                            "completion_evidence_document_id": str(completion.pk),
                        },
                    ],
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="security-return-cdsl-001",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["status"], "completed")
        cdsl = next(item for item in data["items"] if item["item_type"] == "cdsl")
        self.assertEqual(cdsl["status"], "completed")
        self.assertEqual(cdsl["psn"], "PSN-CLOSE-001")
        self.assertEqual(cdsl["urf_date"], "2026-07-21")
        self.assertEqual(cdsl["unpledge_type"], "full")
        self.assertEqual(cdsl["pledgee_dp_outcome"], "accepted")
        self.assertFalse(cdsl["auto_unpledge_flag"])
        self.assertEqual(cdsl["pledgor_bo_account"], "************3456")
        self.assertEqual(cdsl["pledgee_bo_account"], "************7654")
        self.assertNotIn("opaque-pledgor-account", str(data))

    def test_pending_item_advances_with_fresh_key_and_matching_version(self):
        from sfpcl_credit.security_instruments.models import SecurityPackage

        package = SecurityPackage.objects.create(
            loan_application_id=self.account.loan_application_id,
            physical_share_security_required_flag=False,
            demat_pledge_required_flag=False,
            poa_required_flag=True,
            blank_cheque_required_flag=False,
        )
        poa = self._active_poa(package)
        pending = self._record(
            "security-return-poa-pending",
            {
                "security_package_id": str(package.pk),
                "expected_version": 0,
                "items": [
                    {
                        "item_type": "poa",
                        "source_item_id": str(poa.pk),
                        "outcome": "pending",
                        "pending_reason": "Borrower acknowledgement appointment pending.",
                    }
                ],
            },
        )
        self.assertEqual(pending.status_code, 200, pending.content)
        self.assertEqual(pending.json()["data"]["status"], "pending")
        self.assertEqual(pending.json()["data"]["version"], 1)
        acknowledgement = self._verified_document("security_return_progress_ack")

        completed = self._record(
            "security-return-poa-complete",
            {
                "security_package_id": str(package.pk),
                "expected_version": 1,
                "acknowledgement_document_id": str(acknowledgement.pk),
                "items": [
                    {
                        "item_type": "poa",
                        "source_item_id": str(poa.pk),
                        "outcome": "released",
                        "returned_released_to": "Borrower authorised recipient",
                        "returned_released_at": "2026-07-22T11:00:00Z",
                    }
                ],
            },
        )

        self.assertEqual(completed.status_code, 200, completed.content)
        data = completed.json()["data"]
        self.assertEqual(data["status"], "completed")
        self.assertEqual(data["version"], 2)
        poa_result = next(row for row in data["items"] if row["item_type"] == "poa")
        self.assertEqual(poa_result["status"], "released")

    def test_forged_applicability_and_wrong_role_are_denied_and_audited(self):
        forged = self._record(
            "security-return-forged-applicability",
            {"poa_applicable": False},
        )
        self.assertEqual(forged.status_code, 400, forged.content)

        credit = self.closer
        self.fixture._grant(credit, "closure.security_return.record")
        denied = self.client.post(
            f"/api/v1/loan-closures/{self.closure.pk}/security-return/",
            data=json.dumps({}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="security-return-wrong-role",
            **self.fixture._auth(credit),
        )
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(
            AuditLog.objects.filter(
                action="closure.security_return.denied",
                new_value_json__reason="security_return_authority_denied",
            ).count(),
            1,
        )

    def test_physical_completion_without_recipient_or_acknowledgement_is_rejected(self):
        from sfpcl_credit.security_instruments.models import SecurityPackage

        package = SecurityPackage.objects.create(
            loan_application_id=self.account.loan_application_id,
            physical_share_security_required_flag=False,
            demat_pledge_required_flag=False,
            poa_required_flag=True,
            blank_cheque_required_flag=False,
        )
        poa = self._active_poa(package)
        response = self._record(
            "security-return-missing-ack",
            {
                "security_package_id": str(package.pk),
                "expected_version": 0,
                "items": [
                    {
                        "item_type": "poa",
                        "source_item_id": str(poa.pk),
                        "outcome": "released",
                        "returned_released_at": "2026-07-22T11:00:00Z",
                    }
                ],
            },
        )
        self.assertEqual(response.status_code, 400, response.content)

    def _active_poa(self, package):
        from sfpcl_credit.legal_documents.models import LoanDocument
        from sfpcl_credit.security_instruments.models import PowerOfAttorney

        source_document = LoanDocument.objects.filter(
            loan_application_id=self.account.loan_application_id
        ).first()
        return PowerOfAttorney.objects.create(
            security_package=package,
            borrower_member_id=self.account.member_id,
            nominee_id=self.account.loan_application.nominee_id,
            attorney_user=self.actor,
            purpose_summary="Governed security power for the loan.",
            loan_document=source_document,
            stamp_duty_record_id=self._stamp(source_document).pk,
            notarisation_record_id=self._notary(source_document).pk,
            execution_status="executed",
            effective_from=date(2026, 7, 1),
            status="active",
            prepared_by_user=self.fixture.actor,
            verified_by_user=self.actor,
            activation_workflow_event_id=uuid.uuid4(),
        )

    def _verified_document(self, document_type):
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.legal_documents.models import LoanDocument

        document = DocumentFile.objects.create(
            file_name=f"{document_type}.pdf",
            file_extension="pdf",
            mime_type="application/pdf",
            storage_provider="local",
            storage_key=f"tests/{document_type}-{uuid.uuid4()}.pdf",
            checksum_sha256=uuid.uuid4().hex * 2,
            uploaded_by_user=self.actor,
            sensitivity_level="restricted",
        )
        LoanDocument.objects.create(
            loan_application_id=self.account.loan_application_id,
            document_type=document_type,
            document_category="closure",
            document=document,
            output_format="pdf",
            generation_status="generated",
            execution_status="executed",
            verification_status="verified",
            verified_by_user=self.actor,
            verified_at=timezone.now(),
        )
        return document

    def _record(self, key, payload):
        return self.client.post(
            f"/api/v1/loan-closures/{self.closure.pk}/security-return/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=key,
            **self.auth,
        )

    def _stamp(self, document):
        from sfpcl_credit.legal_documents.models import StampDutyRecord

        return StampDutyRecord.objects.create(
            loan_document=document,
            stamp_paper_amount="0.00",
            stamp_type="physical",
            status="pending",
        )

    def _notary(self, document):
        from sfpcl_credit.legal_documents.models import NotarisationRecord

        return NotarisationRecord.objects.create(
            loan_document=document,
            status="pending",
        )
