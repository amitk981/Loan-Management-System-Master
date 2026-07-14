from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless

from django.db import close_old_connections, connection
from django.test import Client, TestCase
from django.test import TransactionTestCase

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.legal_documents.models import ChecklistItem, DocumentChecklist, LoanDocument
from sfpcl_credit.legal_documents.modules import document_checklist
from sfpcl_credit.legal_documents.modules import stamp_notary
from sfpcl_credit.members.models import Member
from sfpcl_credit.tests.api_contracts import assert_success_envelope
from sfpcl_credit.workflows.models import WorkflowEvent


class StampDutyAndNotarisationApiTests(TestCase):
    password = "StampNotaryPass123!"

    def setUp(self):
        self.client = Client()
        self.actor = self._user(
            "compliance_team_member",
            "documents.stamp.record",
            "documents.loan_document.read",
            "documents.checklist.read",
        )
        member = Member.objects.create(
            member_number="MEM-STAMP-001",
            member_type="individual_farmer",
            legal_name="Stamp Test Borrower",
            display_name="Stamp Test Borrower",
            folio_number="FOL-STAMP-001",
            membership_status="active",
            kyc_status="verified",
            default_status="no_default",
        )
        self.application = LoanApplication.objects.create(
            application_reference_number="LO-STAMP-001",
            member=member,
            borrower_type="individual_farmer",
            received_by_user=self.actor,
            created_by_user=self.actor,
            required_loan_amount="400000.00",
            requested_tenure_months=12,
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=LoanApplication.STATUS_APPROVED_BY_SANCTION,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
            terms_acceptance_flag=True,
        )
        generated_file = DocumentFile.objects.create(
            file_name="poa.pdf",
            file_extension=".pdf",
            mime_type="application/pdf",
            file_size_bytes=8,
            storage_provider="local",
            storage_key="tests/poa.pdf",
            checksum_sha256="a" * 64,
            uploaded_by_user=self.actor,
            sensitivity_level="confidential",
        )
        template = DocumentTemplate.objects.create(
            template_code="stamp-poa-v1",
            template_name="Stamp PoA",
            document_type="power_of_attorney",
            borrower_type="individual_farmer",
            template_version="1.0",
            template_file=generated_file,
            approval_status="approved",
            effective_from="2026-01-01",
        )
        self.loan_document = LoanDocument.objects.create(
            loan_application=self.application,
            document_type="power_of_attorney",
            document_category="legal",
            party_required="borrower",
            document_template=template,
            document=generated_file,
            output_format="pdf",
            generation_status=LoanDocument.GENERATION_GENERATED,
            execution_status=LoanDocument.EXECUTION_PENDING,
            verification_status=LoanDocument.VERIFICATION_PENDING,
            renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
            renderer_validated_document_id=generated_file.pk,
            renderer_validated_checksum_sha256=generated_file.checksum_sha256,
        )
        checklist = DocumentChecklist.objects.create(loan_application=self.application)
        self.item = ChecklistItem.objects.create(
            document_checklist=checklist,
            loan_document=self.loan_document,
            item_code="poa",
            item_label="Power of Attorney",
            display_order=4,
            required_flag=True,
            applicable_flag=True,
            completion_status=ChecklistItem.STATUS_PENDING,
            applicability_source="source_always_required",
        )

    def test_compliance_records_pending_stamp_with_atomic_status_and_evidence(self):
        response = self.client.post(
            f"/api/v1/loan-documents/{self.loan_document.pk}/stamp-duty-record/",
            {
                "stamp_paper_amount": "500.00",
                "stamp_type": "physical",
                "stamp_number": "MH-STAMP-123",
                "stamp_purchase_date": "2026-06-22",
                "executed_date": None,
                "status": "pending",
                "remarks": "Prepared for CS verification.",
            },
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-stamp-create",
            HTTP_USER_AGENT="Stamp Test Agent",
            REMOTE_ADDR="203.0.113.20",
            **self._auth(self.actor),
        )

        self.assertEqual(response.status_code, 200, response.content)
        payload = response.json()
        assert_success_envelope(self, payload)
        self.assertEqual(payload["data"]["status"], "pending")
        self.assertEqual(payload["data"]["stamp_paper_amount"], "500.00")
        self.assertNotIn("document_download_url", payload["data"])

        self.loan_document.refresh_from_db()
        self.item.refresh_from_db()
        self.assertEqual(self.loan_document.stamp_status, "pending")
        self.assertEqual(self.item.stamp_status, "pending")
        self.assertEqual(self.item.completion_status, ChecklistItem.STATUS_PENDING)
        audit = AuditLog.objects.get(action="documents.stamp.created")
        self.assertEqual(audit.actor_user, self.actor)
        self.assertEqual(audit.new_value_json["request_id"], "req-stamp-create")
        self.assertEqual(audit.new_value_json["actor_role_codes"], ["compliance_team_member"])
        self.assertEqual(audit.ip_address, "203.0.113.20")
        self.assertEqual(audit.user_agent, "Stamp Test Agent")
        self.assertEqual(
            WorkflowEvent.objects.get(workflow_name="loan_document_stamping").to_state,
            "pending",
        )

    def test_exact_stamp_replay_is_zero_write_and_change_retains_history_in_reads(self):
        payload = {
            "stamp_paper_amount": "1250.00",
            "stamp_type": "electronic",
            "stamp_number": None,
            "stamp_purchase_date": None,
            "executed_date": None,
            "status": "pending",
            "remarks": None,
        }
        url = f"/api/v1/loan-documents/{self.loan_document.pk}/stamp-duty-record/"
        first = self.client.post(url, payload, content_type="application/json", **self._auth(self.actor))
        replay = self.client.post(url, payload, content_type="application/json", **self._auth(self.actor))
        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(first.json()["data"], replay.json()["data"])
        self.assertEqual(AuditLog.objects.filter(action__startswith="documents.stamp.").count(), 1)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="stamp_record").count(), 1)
        self.assertEqual(WorkflowEvent.objects.filter(workflow_name="loan_document_stamping").count(), 1)

        payload["stamp_number"] = "MH-E-456"
        payload["remarks"] = "Number received."
        changed = self.client.post(url, payload, content_type="application/json", **self._auth(self.actor))
        self.assertEqual(changed.status_code, 200, changed.content)
        history = list(VersionHistory.objects.filter(versioned_entity_type="stamp_record").order_by("created_at"))
        self.assertEqual(len(history), 2)
        self.assertIsNone(history[1].old_value_json["stamp_number"])
        self.assertEqual(history[1].new_value_json["stamp_number"], "MH-E-456")

        listed = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/loan-documents/",
            **self._auth(self.actor),
        )
        self.assertEqual(listed.status_code, 200, listed.content)
        self.assertEqual(listed.json()["data"][0]["stamp_status"], "pending")
        checklist_data = document_checklist.serialize(self.item.document_checklist)
        poa = next(item for item in checklist_data["items"] if item["item_code"] == "poa")
        self.assertEqual(poa["stamp_status"], "pending")
        self.assertEqual(poa["completion_status"], "pending")

    def test_only_company_secretary_verifies_and_notary_evidence_is_application_provenanced(self):
        stamp_url = f"/api/v1/loan-documents/{self.loan_document.pk}/stamp-duty-record/"
        adequate = {
            "stamp_paper_amount": "500.00",
            "stamp_type": "physical",
            "stamp_number": "MH-CS-001",
            "stamp_purchase_date": "2026-06-20",
            "executed_date": "2026-06-22",
            "status": "adequate",
            "remarks": "Verified by CS.",
        }
        denied = self.client.post(stamp_url, adequate, content_type="application/json", **self._auth(self.actor))
        self.assertEqual(denied.status_code, 400, denied.content)
        self.assertEqual(AuditLog.objects.filter(action__startswith="documents.stamp.").count(), 0)

        cs = self._user("company_secretary", "documents.stamp.record", "documents.notary.record")
        accepted = self.client.post(stamp_url, adequate, content_type="application/json", **self._auth(cs))
        self.assertEqual(accepted.status_code, 200, accepted.content)
        self.assertEqual(accepted.json()["data"]["status"], "adequate")

        evidence = self._evidence_file(cs, self.application.pk, "notary-proof.pdf")
        notary_url = f"/api/v1/loan-documents/{self.loan_document.pk}/notarisation-record/"
        completed = {
            "notary_name": "Test Notary",
            "notary_registration_number": "NOT-123",
            "notarised_date": "2026-06-22",
            "status": "completed",
            "evidence_document_id": str(evidence.pk),
            "remarks": "Original inspected.",
        }
        response = self.client.post(notary_url, completed, content_type="application/json", **self._auth(cs))
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"]["evidence_document_id"], str(evidence.pk))
        self.assertEqual(response.json()["data"]["evidence_document_name"], "notary-proof.pdf")
        self.loan_document.refresh_from_db()
        self.item.refresh_from_db()
        self.assertEqual(self.loan_document.notarisation_status, "completed")
        self.assertEqual(self.item.notarisation_status, "completed")
        self.assertEqual(self.item.completion_status, "pending")

        unrelated = self._evidence_file(cs, "10000000-0000-0000-0000-000000000099", "wrong-app.pdf")
        completed["evidence_document_id"] = str(unrelated.pk)
        completed["notary_registration_number"] = "NOT-999"
        rejected = self.client.post(notary_url, completed, content_type="application/json", **self._auth(cs))
        self.assertEqual(rejected.status_code, 400, rejected.content)
        self.assertEqual(rejected.json()["error"]["field_errors"], {
            "evidence_document_id": "Document file was not found or is inaccessible."
        })

    def test_invalid_denied_legacy_and_completion_conflicts_are_zero_write(self):
        url = f"/api/v1/loan-documents/{self.loan_document.pk}/stamp-duty-record/"
        base = {
            "stamp_paper_amount": "500.00",
            "stamp_type": "physical",
            "stamp_number": None,
            "stamp_purchase_date": "2026-06-23",
            "executed_date": "2026-06-22",
            "status": "pending",
            "remarks": None,
        }
        invalid = self.client.post(url, {**base, "unexpected": True}, content_type="application/json", **self._auth(self.actor))
        self.assertEqual(invalid.status_code, 400, invalid.content)
        invalid_date = self.client.post(url, base, content_type="application/json", **self._auth(self.actor))
        self.assertEqual(invalid_date.status_code, 400, invalid_date.content)
        invalid_money = self.client.post(url, {**base, "stamp_purchase_date": None, "stamp_paper_amount": "500"}, content_type="application/json", **self._auth(self.actor))
        self.assertEqual(invalid_money.status_code, 400, invalid_money.content)

        reader = self._user("credit_manager", "documents.stamp.record")
        denied = self.client.post(url, {**base, "stamp_purchase_date": None}, content_type="application/json", **self._auth(reader))
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(AuditLog.objects.filter(action__startswith="documents.stamp.").count(), 0)

        LoanDocument.objects.filter(pk=self.loan_document.pk).update(document_id=None)
        legacy = self.client.post(url, {**base, "stamp_purchase_date": None}, content_type="application/json", **self._auth(self.actor))
        self.assertEqual(legacy.status_code, 409, legacy.content)
        LoanDocument.objects.filter(pk=self.loan_document.pk).update(document_id=self.loan_document.document_id)

        created = self.client.post(url, {**base, "stamp_purchase_date": None}, content_type="application/json", **self._auth(self.actor))
        self.assertEqual(created.status_code, 200, created.content)
        self.item.completion_status = ChecklistItem.STATUS_COMPLETE
        self.item.save(update_fields=["completion_status"])
        conflict = self.client.post(
            url,
            {**base, "stamp_purchase_date": None, "stamp_number": "LATE-CHANGE", "status": "insufficient"},
            content_type="application/json",
            **self._auth(self.actor),
        )
        self.assertEqual(conflict.status_code, 409, conflict.content)
        self.assertEqual(AuditLog.objects.filter(action__startswith="documents.stamp.").count(), 1)

    def test_exact_notarisation_replay_is_zero_write(self):
        cs = self._user("company_secretary", "documents.notary.record")
        evidence = self._evidence_file(cs, self.application.pk, "replay-notary.pdf")
        payload = {
            "notary_name": "Replay Notary",
            "notary_registration_number": "NOT-REPLAY",
            "notarised_date": "2026-06-22",
            "status": "completed",
            "evidence_document_id": str(evidence.pk),
            "remarks": None,
        }
        url = f"/api/v1/loan-documents/{self.loan_document.pk}/notarisation-record/"
        first = self.client.post(url, payload, content_type="application/json", **self._auth(cs))
        replay = self.client.post(url, payload, content_type="application/json", **self._auth(cs))
        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(first.json()["data"], replay.json()["data"])
        self.assertEqual(AuditLog.objects.filter(action__startswith="documents.notary.").count(), 1)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="notary_record").count(), 1)

    def test_remaining_contract_denials_are_fielded_and_zero_write(self):
        stamp_url = f"/api/v1/loan-documents/{self.loan_document.pk}/stamp-duty-record/"
        stamp = {
            "stamp_paper_amount": "500.00",
            "stamp_type": "paper",
            "stamp_number": None,
            "stamp_purchase_date": None,
            "executed_date": None,
            "status": "unknown",
            "remarks": None,
        }
        invalid_stamp = self.client.post(stamp_url, stamp, content_type="application/json", **self._auth(self.actor))
        self.assertEqual(invalid_stamp.status_code, 400, invalid_stamp.content)
        self.assertEqual(set(invalid_stamp.json()["error"]["field_errors"]), {"stamp_type", "status"})

        cs = self._user("company_secretary", "documents.notary.record")
        notary_url = f"/api/v1/loan-documents/{self.loan_document.pk}/notarisation-record/"
        incomplete = self.client.post(
            notary_url,
            {
                "notary_name": None,
                "notary_registration_number": None,
                "notarised_date": "not-a-date",
                "status": "completed",
                "evidence_document_id": None,
                "remarks": None,
            },
            content_type="application/json",
            **self._auth(cs),
        )
        self.assertEqual(incomplete.status_code, 400, incomplete.content)
        self.assertIn("notarised_date", incomplete.json()["error"]["field_errors"])
        missing_completed = self.client.post(
            notary_url,
            {
                "notary_name": None,
                "notary_registration_number": None,
                "notarised_date": "2026-06-22",
                "status": "completed",
                "evidence_document_id": None,
                "remarks": None,
            },
            content_type="application/json",
            **self._auth(cs),
        )
        self.assertEqual(missing_completed.status_code, 400, missing_completed.content)
        self.assertEqual(
            set(missing_completed.json()["error"]["field_errors"]),
            {"notary_name", "notary_registration_number", "evidence_document_id"},
        )

        inaccessible = DocumentFile.objects.create(
            file_name="unproven.pdf",
            storage_provider="local",
            storage_key="tests/unproven.pdf",
            checksum_sha256="c" * 64,
            uploaded_by_user=cs,
            sensitivity_level="confidential",
        )
        pending = {
            "notary_name": None,
            "notary_registration_number": None,
            "notarised_date": None,
            "status": "pending",
            "evidence_document_id": str(inaccessible.pk),
            "remarks": None,
        }
        denied_evidence = self.client.post(notary_url, pending, content_type="application/json", **self._auth(cs))
        self.assertEqual(denied_evidence.status_code, 400, denied_evidence.content)
        pending["evidence_document_id"] = "10000000-0000-0000-0000-000000000098"
        nonexistent = self.client.post(notary_url, pending, content_type="application/json", **self._auth(cs))
        self.assertEqual(nonexistent.status_code, 400, nonexistent.content)

        missing = self.client.post(
            "/api/v1/loan-documents/10000000-0000-0000-0000-000000000099/stamp-duty-record/",
            {**stamp, "stamp_type": "physical", "status": "pending"},
            content_type="application/json",
            **self._auth(self.actor),
        )
        self.assertEqual(missing.status_code, 404, missing.content)

        self.application.application_status = LoanApplication.STATUS_SUBMITTED_TO_SANCTION
        self.application.save(update_fields=["application_status"])
        wrong_stage = self.client.post(
            stamp_url,
            {**stamp, "stamp_type": "physical", "status": "pending"},
            content_type="application/json",
            **self._auth(self.actor),
        )
        self.assertEqual(wrong_stage.status_code, 403, wrong_stage.content)
        self.assertEqual(AuditLog.objects.filter(action__startswith="documents.stamp.").count(), 0)
        self.assertEqual(AuditLog.objects.filter(action__startswith="documents.notary.").count(), 0)

    def test_loan_agreement_statuses_do_not_complete_checklist_or_calculate_rate(self):
        agreement_file = DocumentFile.objects.create(
            file_name="agreement.pdf",
            storage_provider="local",
            storage_key="tests/agreement.pdf",
            checksum_sha256="d" * 64,
            uploaded_by_user=self.actor,
            sensitivity_level="confidential",
        )
        template = DocumentTemplate.objects.create(
            template_code="stamp-agreement-v1",
            template_name="Loan Agreement",
            document_type="loan_agreement",
            borrower_type="individual_farmer",
            template_version="1.0",
            template_file=agreement_file,
            approval_status="approved",
            effective_from="2026-01-01",
        )
        agreement = LoanDocument.objects.create(
            loan_application=self.application,
            document_type="loan_agreement",
            document_category="legal",
            document_template=template,
            document=agreement_file,
            output_format="pdf",
            generation_status="generated",
            execution_status="pending",
            verification_status="pending",
            renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
            renderer_validated_document_id=agreement_file.pk,
            renderer_validated_checksum_sha256=agreement_file.checksum_sha256,
        )
        item = ChecklistItem.objects.create(
            document_checklist=self.item.document_checklist,
            loan_document=agreement,
            item_code="loan_agreement",
            item_label="Loan Agreement",
            display_order=9,
            required_flag=True,
            applicable_flag=True,
            completion_status="pending",
            applicability_source="source_always_required",
        )
        response = self.client.post(
            f"/api/v1/loan-documents/{agreement.pk}/stamp-duty-record/",
            {
                "stamp_paper_amount": "731.25",
                "stamp_type": "electronic",
                "stamp_number": "AD-VALOREM-SUPPLIED",
                "stamp_purchase_date": None,
                "executed_date": None,
                "status": "pending",
                "remarks": "No adequacy calculation performed.",
            },
            content_type="application/json",
            **self._auth(self.actor),
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"]["stamp_paper_amount"], "731.25")
        cs = self._user("company_secretary", "documents.notary.record")
        notary = self.client.post(
            f"/api/v1/loan-documents/{agreement.pk}/notarisation-record/",
            {
                "notary_name": None,
                "notary_registration_number": None,
                "notarised_date": None,
                "status": "pending",
                "evidence_document_id": None,
                "remarks": "Prepared separately from stamp facts.",
            },
            content_type="application/json",
            **self._auth(cs),
        )
        self.assertEqual(notary.status_code, 200, notary.content)
        item.refresh_from_db()
        self.assertEqual(item.stamp_status, "pending")
        self.assertEqual(item.notarisation_status, "pending")
        self.assertEqual(item.completion_status, "pending")

        other_file = DocumentFile.objects.create(
            file_name="term-sheet.pdf",
            storage_provider="local",
            storage_key="tests/term-sheet.pdf",
            checksum_sha256="e" * 64,
            uploaded_by_user=self.actor,
            sensitivity_level="confidential",
        )
        other = LoanDocument.objects.create(
            loan_application=self.application,
            document_type="term_sheet",
            document_category="legal",
            document=other_file,
            output_format="docx",
            generation_status="generated",
            execution_status="pending",
            verification_status="pending",
            renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
            renderer_validated_document_id=other_file.pk,
            renderer_validated_checksum_sha256=other_file.checksum_sha256,
        )
        self.assertIsNone(other.stamp_status)
        self.assertIsNone(other.notarisation_status)

    def _user(self, role_code, *permission_codes):
        role = Role.objects.create(
            role_code=role_code,
            role_name=role_code.replace("_", " ").title(),
            status="active",
        )
        for code in permission_codes:
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "documents",
                    "risk_level": "high",
                },
            )
            RolePermission.objects.create(role=role, permission=permission)
        user = User.objects.create(
            full_name=role.role_name,
            email=f"{role_code}@stamp.example",
            status="active",
            primary_role=role,
        )
        user.set_password(self.password)
        user.save(update_fields=["password_hash"])
        return user

    def _auth(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {"HTTP_AUTHORIZATION": f"Bearer {response.json()['data']['access_token']}"}

    @staticmethod
    def _evidence_file(actor, application_id, file_name):
        document = DocumentFile.objects.create(
            file_name=file_name,
            file_extension=".pdf",
            mime_type="application/pdf",
            file_size_bytes=16,
            storage_provider="local",
            storage_key=f"tests/{file_name}",
            checksum_sha256="b" * 64,
            uploaded_by_user=actor,
            sensitivity_level="confidential",
        )
        AuditLog.objects.create(
            actor_user=actor,
            actor_type="user",
            action="documents.file.uploaded",
            entity_type="document_file",
            entity_id=document.pk,
            new_value_json={
                "document_id": str(document.pk),
                "file_name": document.file_name,
                "file_extension": document.file_extension,
                "mime_type": document.mime_type,
                "file_size_bytes": document.file_size_bytes,
                "storage_provider": document.storage_provider,
                "storage_key": document.storage_key,
                "checksum_sha256": document.checksum_sha256,
                "sensitivity_level": document.sensitivity_level,
                "document_category": "legal",
                "related_entity_type": "application",
                "related_entity_id": str(application_id),
            },
        )
        return document


@skipUnless(connection.vendor == "postgresql", "Authoritative stamp five-race requires PostgreSQL.")
class StampDutyConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = StampDutyAndNotarisationApiTests(methodName="test_compliance_records_pending_stamp_with_atomic_status_and_evidence")
        fixture.setUp()
        self.fixture = fixture

    def test_five_changed_submissions_keep_one_current_record_and_complete_ledger(self):
        actor = self.fixture.actor
        loan_document = self.fixture.loan_document
        base = {
            "stamp_paper_amount": "500.00",
            "stamp_type": "electronic",
            "stamp_number": "RACE-SEED",
            "stamp_purchase_date": "2026-06-20",
            "executed_date": None,
            "status": "pending",
            "remarks": "seed",
        }
        stamp_notary.record_stamp(
            actor=actor,
            loan_document_id=loan_document.pk,
            payload=base,
            metadata=stamp_notary.RequestMetadata("race-seed", "203.0.113.1", "race"),
        )
        barrier = Barrier(5)

        def submit(index):
            close_old_connections()
            try:
                thread_actor = User.objects.get(pk=actor.pk)
                barrier.wait()
                return stamp_notary.record_stamp(
                    actor=thread_actor,
                    loan_document_id=loan_document.pk,
                    payload={**base, "stamp_number": f"RACE-{index}", "remarks": f"worker-{index}"},
                    metadata=stamp_notary.RequestMetadata(
                        f"race-{index}", f"203.0.113.{index + 10}", f"race-worker-{index}"
                    ),
                )
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(submit, range(5)))

        self.assertEqual(len({result["stamp_record_id"] for result in results}), 1)
        current = LoanDocument.objects.get(pk=loan_document.pk).stamp_duty_record
        self.assertIn(current.stamp_number, {f"RACE-{index}" for index in range(5)})
        self.assertEqual(AuditLog.objects.filter(action__startswith="documents.stamp.").count(), 6)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="stamp_record").count(), 6)
        self.assertEqual(WorkflowEvent.objects.filter(workflow_name="loan_document_stamping").count(), 6)
