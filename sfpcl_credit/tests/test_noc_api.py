import json
import hashlib
from datetime import date
from tempfile import TemporaryDirectory
from uuid import uuid4

from django.core.files.base import ContentFile
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from sfpcl_credit.closure.models import LoanClosure
from sfpcl_credit.communications.models import (
    Communication,
    CommunicationDeliveryJob,
    ContentTemplate,
)
from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.legal_documents.models import LoanDocument
from sfpcl_credit.loans.models import LoanAccount


class NocIssuanceApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_loan_account_reads_api import LoanAccountReadApiTests

        self.document_storage = TemporaryDirectory()
        self.storage_override = override_settings(
            DOCUMENT_STORAGE_ROOT=self.document_storage.name
        )
        self.storage_override.enable()
        self.addCleanup(self.storage_override.disable)
        self.addCleanup(self.document_storage.cleanup)
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
        self.account.member.email = "noc.borrower@example.test"
        self.account.member.save(update_fields=["email"])
        self.closer = self.fixture._user("credit_manager", "NOC Closing Credit Manager")
        self.fixture._grant(
            self.closer,
            "closure.readiness.read",
            "closure.loan.close",
        )
        close = Client().post(
            f"/api/v1/loan-accounts/{self.account.pk}/closure/",
            data=json.dumps(
                {
                    "closure_type": "full_repayment",
                    "closure_notes": "Canonical balances verified for NOC issuance.",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="noc-fixture-close",
            **self.fixture._auth(self.closer),
        )
        self.assertEqual(close.status_code, 200, close.content)
        self.closure = LoanClosure.objects.get(loan_account=self.account)

        self.issuer = self.fixture._user("company_secretary", "NOC Company Secretary")
        self.fixture._grant(
            self.issuer,
            "closure.noc.issue",
            "communications.communication.send",
        )
        from sfpcl_credit.identity.models import Team, UserTeamMembership

        compliance_team, _ = Team.objects.get_or_create(
            team_code="compliance",
            defaults={"team_name": "Compliance Team", "status": "active"},
        )
        UserTeamMembership.objects.create(
            user=self.issuer, team=compliance_team, status="active"
        )
        self.auth = self.fixture._auth(self.issuer)
        self.document = self._generated_noc_document()
        ContentTemplate.objects.create(
            template_code="noc_issued_email",
            template_name="NOC Issued Email",
            template_type="email",
            language_code="en",
            audience="borrower",
            subject_template="NOC issued for {{loan_account_number}}",
            body_template=(
                "Dear {{borrower_name}}, your No Objection Certificate for "
                "{{loan_account_number}} is ready."
            ),
            variables_json=["borrower_name", "loan_account_number"],
            approval_status=ContentTemplate.STATUS_APPROVED,
            template_version="1.0",
            effective_from=date(2026, 1, 1),
        )
        self.client = Client()

    def test_eligible_full_repayment_closure_issues_one_noc_and_queues_delivery(self):
        response = self._issue("issue-noc-001")

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        from sfpcl_credit.closure.models import NocRecord

        noc = NocRecord.objects.get(loan_closure=self.closure)
        self.assertEqual(data["noc_id"], str(noc.pk))
        self.assertEqual(data["loan_closure_id"], str(self.closure.pk))
        self.assertEqual(data["document_id"], str(self.document.document_id))
        self.assertEqual(data["delivery_mode"], "email")
        self.assertEqual(data["delivery_status"], "queued")
        self.assertFalse(data["idempotency_replayed"])
        self.assertEqual(noc.loan_account_id, self.account.pk)
        self.assertEqual(noc.member_id, self.account.member_id)
        self.assertEqual(noc.issued_by_user_id, self.issuer.pk)
        self.assertEqual(noc.signatory_user_id, self.issuer.pk)
        self.assertEqual(noc.signatory_name_snapshot, self.issuer.full_name)
        self.assertEqual(noc.generation_audit.action, "documents.loan_document.generated")
        self.assertEqual(noc.document_template_id_snapshot, self.document.generated_loan_documents.get().document_template_id)
        self.assertEqual(noc.document_template_version_snapshot, "1.0")
        self.assertEqual(noc.renderer_contract_version_snapshot, LoanDocument.RENDERER_CONTRACT_V1)
        self.assertEqual(noc.document_checksum_sha256_snapshot, self.document.checksum_sha256)
        self.assertEqual(len(noc.merge_values_sha256_snapshot), 64)
        self.assertEqual(noc.borrower_name_snapshot, self.account.member.legal_name)
        self.assertEqual(
            noc.application_reference_snapshot,
            self.account.loan_application.application_reference_number,
        )
        self.assertEqual(noc.disbursed_amount_snapshot, self.account.disbursed_amount)
        self.assertEqual(noc.full_repayment_at_snapshot, self.closure.closed_at)
        communication = Communication.objects.get(pk=noc.communication_id)
        job = CommunicationDeliveryJob.objects.get(communication_id=communication.pk)
        self.assertEqual(job.status, CommunicationDeliveryJob.STATUS_QUEUED)
        self.assertEqual(communication.related_entity_id, noc.pk)
        self.assertEqual(communication.recipient_party_id, self.account.member_id)
        self.assertEqual(
            AuditLog.objects.filter(action="closure.noc.issued", entity_id=noc.pk).count(),
            1,
        )

    def test_borrower_can_read_only_own_issued_noc(self):
        from sfpcl_credit.identity.models import PortalAccount, User
        from sfpcl_credit.members.models import Member

        issued = self._issue("issue-noc-borrower-read")
        self.assertEqual(issued.status_code, 200, issued.content)
        owner = self.fixture._user("borrower_portal_user", "NOC Borrower Owner")
        PortalAccount.objects.create(
            member=self.account.member,
            user=owner,
            status=PortalAccount.STATUS_ACTIVE,
            activated_at=timezone.now(),
        )
        owner_response = self.client.get(
            f"/api/v1/loan-closures/{self.closure.pk}/noc/",
            **self.fixture._auth(owner),
        )
        self.assertEqual(owner_response.status_code, 200, owner_response.content)
        self.assertEqual(
            owner_response.json()["data"]["noc_id"], issued.json()["data"]["noc_id"]
        )

        foreign_member = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Foreign NOC Member",
            display_name="Foreign NOC Member",
            folio_number="NOC-FOREIGN-FOLIO",
            membership_status="active",
            pan_encrypted="foreign-noc-encrypted-pan",
            pan_hash="foreign-noc-pan-hash",
            kyc_status="verified",
            default_status="no_default",
        )
        foreign = User.objects.create(
            full_name="Foreign NOC Borrower",
            email="foreign.noc.borrower@example.test",
            status="active",
            primary_role=owner.primary_role,
        )
        foreign.set_password(self.fixture.password)
        foreign.save()
        PortalAccount.objects.create(
            member=foreign_member,
            user=foreign,
            status=PortalAccount.STATUS_ACTIVE,
            activated_at=timezone.now(),
        )
        denied = self.client.get(
            f"/api/v1/loan-closures/{self.closure.pk}/noc/",
            **self.fixture._auth(foreign),
        )
        self.assertEqual(denied.status_code, 404, denied.content)
        self.assertEqual(denied.json()["error"]["code"], "NOT_FOUND")
        self.assertEqual(
            AuditLog.objects.filter(action="closure.noc.read_denied").count(), 1
        )

    def test_authorised_noc_download_uses_document_owner_and_is_audited(self):
        issued = self._issue("issue-noc-download")
        self.assertEqual(issued.status_code, 200, issued.content)

        response = self.client.get(
            f"/api/v1/loan-closures/{self.closure.pk}/noc/download/",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertIn(str(self.document.pk), data["download_url"])
        self.assertEqual(
            AuditLog.objects.filter(
                action="documents.file.downloaded",
                entity_id=self.document.pk,
                actor_user=self.issuer,
            ).count(),
            1,
        )

    def test_credit_manager_read_is_scoped_to_the_manager_who_closed_the_loan(self):
        from sfpcl_credit.identity.models import User

        issued = self._issue("issue-noc-credit-read-scope")
        self.assertEqual(issued.status_code, 200, issued.content)

        owner_read = self.client.get(
            f"/api/v1/loan-closures/{self.closure.pk}/noc/",
            **self.fixture._auth(self.closer),
        )
        self.assertEqual(owner_read.status_code, 200, owner_read.content)

        other_credit_manager = User.objects.create(
            full_name="Other NOC Credit Manager",
            email="other.noc.credit.manager@example.test",
            primary_role=self.closer.primary_role,
            status=User.ACTIVE_STATUS,
        )
        other_credit_manager.set_password(self.fixture.password)
        other_credit_manager.save(update_fields=["password_hash"])
        self.fixture._grant(other_credit_manager, "closure.readiness.read")

        foreign_read = self.client.get(
            f"/api/v1/loan-closures/{self.closure.pk}/noc/",
            **self.fixture._auth(other_credit_manager),
        )
        self.assertEqual(foreign_read.status_code, 404, foreign_read.content)
        self.assertEqual(foreign_read.json()["error"]["code"], "NOT_FOUND")

    def test_exact_replay_returns_same_certificate_and_changed_replay_is_rejected(self):
        from sfpcl_credit.closure.models import ClosureRequirement, NocRecord

        first = self._issue("issue-noc-replay")
        replay = self._issue("issue-noc-replay")
        changed = self._issue(
            "issue-noc-replay", recipient_email="changed-recipient@example.test"
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(changed.status_code, 409, changed.content)
        self.assertEqual(first.json()["data"]["noc_id"], replay.json()["data"]["noc_id"])
        self.assertTrue(replay.json()["data"]["idempotency_replayed"])
        self.assertEqual(NocRecord.objects.count(), 1)
        self.assertEqual(LoanDocument.objects.filter(document_type="noc").count(), 1)
        self.assertEqual(Communication.objects.filter(related_entity_type="noc").count(), 1)
        self.assertEqual(CommunicationDeliveryJob.objects.count(), 1)
        self.assertEqual(
            ClosureRequirement.objects.get(
                loan_closure=self.closure,
                requirement_type=ClosureRequirement.TYPE_NOC,
            ).requirement_status,
            ClosureRequirement.STATUS_COMPLETED,
        )
        retained = LoanClosure.objects.get(pk=self.closure.pk)
        self.assertEqual(retained.readiness_snapshot_json, self.closure.readiness_snapshot_json)

    def test_certificate_facts_foreign_document_signatory_and_wrong_role_are_rejected(self):
        from sfpcl_credit.closure.models import NocRecord

        forged = self._issue("issue-noc-forged-facts", borrower_name="Forged Borrower")
        missing_document = self._issue(
            "issue-noc-missing-document", document_id=str(uuid4())
        )
        wrong_signatory = self._issue(
            "issue-noc-wrong-signatory", signatory_user_id=str(self.closer.pk)
        )
        wrong_role = self.fixture._user("field_officer", "NOC Permission Without Role")
        self.fixture._grant(wrong_role, "closure.noc.issue")
        denied_role = self.client.post(
            f"/api/v1/loan-closures/{self.closure.pk}/noc/",
            data=json.dumps(
                {
                    "document_id": str(self.document.pk),
                    "delivery_mode": "email",
                    "recipient_email": self.account.member.email,
                    "signatory_user_id": str(self.issuer.pk),
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="issue-noc-wrong-role",
            **self.fixture._auth(wrong_role),
        )

        self.assertEqual(forged.status_code, 400, forged.content)
        self.assertIn("borrower_name", forged.json()["error"]["field_errors"])
        self.assertEqual(missing_document.status_code, 409, missing_document.content)
        self.assertEqual(wrong_signatory.status_code, 409, wrong_signatory.content)
        self.assertEqual(denied_role.status_code, 403, denied_role.content)
        self.assertFalse(NocRecord.objects.exists())
        self.assertEqual(
            AuditLog.objects.filter(action="closure.noc.issue_denied").count(), 4
        )

    def test_failed_delivery_handoff_retains_no_false_issue_and_can_retry(self):
        from sfpcl_credit.closure.models import NocRecord

        template = ContentTemplate.objects.get(template_code="noc_issued_email")
        template_values = {
            field.name: getattr(template, field.name)
            for field in ContentTemplate._meta.fields
            if not field.primary_key
        }
        template.delete()

        failed = self._issue("issue-noc-retryable-handoff")
        self.assertEqual(failed.status_code, 409, failed.content)
        self.assertFalse(NocRecord.objects.exists())
        self.assertFalse(Communication.objects.filter(related_entity_type="noc").exists())
        self.assertFalse(CommunicationDeliveryJob.objects.exists())
        self.assertEqual(AuditLog.objects.filter(action="closure.noc.issued").count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(
                action="closure.noc.issue_denied",
                new_value_json__reason="delivery_handoff_failed",
            ).count(),
            1,
        )

        ContentTemplate.objects.create(**template_values)
        retried = self._issue("issue-noc-retryable-handoff")
        self.assertEqual(retried.status_code, 200, retried.content)
        self.assertEqual(NocRecord.objects.count(), 1)
        self.assertEqual(LoanDocument.objects.filter(document_type="noc").count(), 1)
        self.assertEqual(Communication.objects.filter(related_entity_type="noc").count(), 1)
        self.assertEqual(CommunicationDeliveryJob.objects.count(), 1)

    def test_compliance_issuer_uses_governed_company_secretary_signatory(self):
        from sfpcl_credit.closure.models import NocRecord

        compliance = self.fixture._user("compliance_team_member", "NOC Compliance Issuer")
        self.fixture._grant(compliance, "closure.noc.issue")
        from sfpcl_credit.identity.models import UserTeamMembership

        UserTeamMembership.objects.create(
            user=compliance,
            team=self.issuer.team_memberships.get().team,
            status="active",
        )
        self.auth = self.fixture._auth(compliance)

        response = self._issue("issue-noc-compliance")

        self.assertEqual(response.status_code, 200, response.content)
        noc = NocRecord.objects.get()
        self.assertEqual(noc.issued_by_user_id, compliance.pk)
        self.assertEqual(noc.issued_by_role_code, "compliance_team_member")
        self.assertEqual(noc.signatory_user_id, self.issuer.pk)
        self.assertEqual(noc.signatory_role_code, "company_secretary")

    def test_provider_result_is_retained_without_generating_another_certificate(self):
        from sfpcl_credit.closure.models import NocRecord

        issued = self._issue("issue-noc-provider-result")
        self.assertEqual(issued.status_code, 200, issued.content)
        noc = NocRecord.objects.get()
        CommunicationDeliveryJob.objects.filter(pk=noc.communication_job_id).update(
            status=CommunicationDeliveryJob.STATUS_FAILED,
            last_failure_code="provider_rejected",
        )

        read = self.client.get(
            f"/api/v1/loan-closures/{self.closure.pk}/noc/", **self.auth
        )

        self.assertEqual(read.status_code, 200, read.content)
        self.assertEqual(read.json()["data"]["delivery_status"], "failed")
        self.assertEqual(NocRecord.objects.get().delivery_status, "failed")
        self.assertEqual(LoanDocument.objects.filter(document_type="noc").count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(
                action="closure.noc.delivery_status_observed", entity_id=noc.pk
            ).count(),
            1,
        )

    def test_issue_rejects_same_role_and_permission_without_compliance_object_scope(self):
        from sfpcl_credit.identity.models import User

        foreign_cs = User.objects.create(
            full_name="Foreign NOC Secretary",
            email="foreign.noc.secretary@example.test",
            primary_role=self.issuer.primary_role,
            status=User.ACTIVE_STATUS,
        )
        foreign_cs.set_password(self.fixture.password)
        foreign_cs.save(update_fields=["password_hash"])
        self.fixture._grant(foreign_cs, "closure.noc.issue")
        self.auth = self.fixture._auth(foreign_cs)

        response = self._issue("issue-noc-out-of-scope")

        self.assertEqual(response.status_code, 404, response.content)
        self.assertEqual(response.json()["error"]["code"], "NOT_FOUND")
        self.assertEqual(
            AuditLog.objects.filter(
                action="closure.noc.issue_denied",
                new_value_json__reason="loan_closure_scope_denied",
            ).count(),
            1,
        )

    def _issue(self, idempotency_key, **overrides):
        payload = {
            "document_id": str(self.document.document_id),
            "delivery_mode": "email",
            "recipient_email": self.account.member.email,
            "signatory_user_id": str(self.issuer.pk),
            **overrides,
        }
        return self.client.post(
            f"/api/v1/loan-closures/{self.closure.pk}/noc/",
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=idempotency_key,
            HTTP_X_REQUEST_ID="req-issue-noc-001",
            **self.auth,
        )

    def _generated_noc_document(self):
        from sfpcl_credit.legal_documents.modules import document_renderer
        from sfpcl_credit.tests.test_loan_document_generation_api import (
            LoanDocumentGenerationApiTests,
        )

        merge_values = {
            "borrower_name": self.account.member.legal_name,
            "loan_account_number": self.account.loan_account_number,
            "application_reference": (
                self.account.loan_application.application_reference_number
            ),
            "disbursed_amount": f"{self.account.disbursed_amount:.2f}",
            "full_repayment_date": self.closure.closed_at.date().isoformat(),
            "issued_by": self.issuer.full_name,
            "issue_date": timezone.localdate().isoformat(),
        }
        template_bytes = LoanDocumentGenerationApiTests._genuine_docx_fixture(
            sorted(merge_values),
            title="No Objection Certificate — No dues remain",
            footer="Governed NOC template",
        )
        source_stored = LocalDocumentStorage().store(
            ContentFile(template_bytes, name="noc-template.docx")
        )
        source = DocumentFile.objects.create(
            file_name="noc-template.docx",
            file_extension=".docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size_bytes=source_stored.file_size_bytes,
            storage_provider=source_stored.storage_provider,
            storage_key=source_stored.storage_key,
            checksum_sha256=source_stored.checksum_sha256,
            uploaded_by_user=self.issuer,
            sensitivity_level=DocumentFile.SENSITIVITY_CONFIDENTIAL,
        )
        template = DocumentTemplate.objects.create(
            template_code="noc-v1",
            template_name="No Objection Certificate",
            document_type="noc",
            template_version="1.0",
            template_file=source,
            merge_fields_json=sorted(merge_values),
            approval_status=DocumentTemplate.STATUS_APPROVED,
            effective_from=date(2026, 1, 1),
        )
        rendered = document_renderer.render(
            template_bytes=template_bytes,
            merge_values=merge_values,
            output_format="pdf",
        )
        output_stored = LocalDocumentStorage().store(
            ContentFile(rendered.content, name="noc-output.pdf")
        )
        output = DocumentFile.objects.create(
            file_name="noc-output.pdf",
            file_extension=".pdf",
            mime_type="application/pdf",
            file_size_bytes=output_stored.file_size_bytes,
            storage_provider=output_stored.storage_provider,
            storage_key=output_stored.storage_key,
            checksum_sha256=output_stored.checksum_sha256,
            uploaded_by_user=self.issuer,
            sensitivity_level=DocumentFile.SENSITIVITY_CONFIDENTIAL,
        )
        loan_document = LoanDocument.objects.create(
            loan_application=self.account.loan_application,
            document_type="noc",
            document_category="closure",
            party_required="borrower",
            document_template=template,
            document=output,
            output_format="pdf",
            generation_status=LoanDocument.GENERATION_GENERATED,
            execution_status=LoanDocument.EXECUTION_PENDING,
            verification_status=LoanDocument.VERIFICATION_PENDING,
            renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
            renderer_validated_document_id=output.pk,
            renderer_validated_checksum_sha256=output.checksum_sha256,
        )
        merge_digest = hashlib.sha256(
            json.dumps(
                merge_values, sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest()
        AuditLog.objects.create(
            actor_user=self.issuer,
            action="documents.loan_document.generated",
            entity_type="loan_document",
            entity_id=loan_document.pk,
            new_value_json={
                "document_type": "noc",
                "document_id": str(output.pk),
                "document_template_id": str(template.pk),
                "template_version": template.template_version,
                "output_format": "pdf",
                "renderer_contract_version": LoanDocument.RENDERER_CONTRACT_V1,
                "renderer_validated_checksum_sha256": output.checksum_sha256,
                "merge_field_names": sorted(merge_values),
                "merge_values_sha256": merge_digest,
            },
        )
        return output
