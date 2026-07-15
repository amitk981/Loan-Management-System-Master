from concurrent.futures import ThreadPoolExecutor
from importlib import import_module
from threading import Barrier
from tempfile import TemporaryDirectory
from unittest import skipUnless
from django.db import close_old_connections, connection
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, TransactionTestCase
from django.test import override_settings
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.legal_documents.models import (
    ChecklistItem,
    DocumentChecklist,
    LoanDocument,
    NotarisationRecord,
    SignatureRecord,
    StampDutyRecord,
)
from sfpcl_credit.members.models import Member, Nominee
from sfpcl_credit.tests.api_contracts import assert_success_envelope
from sfpcl_credit.workflows.models import WorkflowEvent
from sfpcl_credit.legal_documents.modules import document_checklist, signatures, stamp_notary
from sfpcl_credit.security_instruments.models import PowerOfAttorney, SecurityPackage
from sfpcl_credit.security_instruments.modules import power_of_attorney
from sfpcl_credit.processes import security_instrument_evidence
from sfpcl_credit.tests import test_document_checklist_api


class PowerOfAttorneyApiTests(TestCase):
    password = "PowerOfAttorneyPass123!"

    def setUp(self):
        self.document_storage = TemporaryDirectory()
        self.addCleanup(self.document_storage.cleanup)
        storage_override = override_settings(DOCUMENT_STORAGE_ROOT=self.document_storage.name)
        storage_override.enable()
        self.addCleanup(storage_override.disable)
        fixture = test_document_checklist_api.DocumentChecklistApiTests(
            methodName="test_approved_sanction_creates_ordered_applicability_once_with_evidence"
        )
        fixture.setUp()
        self.fixture = fixture
        self.client = fixture.client
        self.password = fixture.password
        self.application = fixture.application
        self.member = self.application.member
        self.compliance = fixture._user(
            "compliance_team_member",
            "Power of Attorney Compliance",
            "security.package.read",
            "security.package.create",
            "security.poa.manage",
            "documents.signature.record",
            "documents.stamp.record",
            "documents.notary.record",
            "documents.loan_document.generate",
            "documents.loan_document.read",
            "documents.template.file_reference",
        )
        self.nominee = Nominee.objects.create(
            member=self.member,
            nominee_name="Power Nominee",
            gender="female",
            pan_encrypted="encrypted-pan",
            pan_hash="poa-pan-hash",
            aadhaar_encrypted="encrypted-aadhaar",
            aadhaar_hash="poa-aadhaar-hash",
        )
        self.application.nominee = self.nominee
        self.application.received_by_user = self.compliance
        self.application.created_by_user = self.compliance
        self.application.save(update_fields=["nominee", "received_by_user", "created_by_user"])
        checklist = document_checklist.refresh_for_approved_sanction(
            actor=fixture.actor,
            application_id=self.application.pk,
            source_reason="poa_test_setup",
        )
        self.poa_item = checklist.items.get(item_code="poa")
        self.poa_item.remarks = "Preserve checklist ownership."
        self.poa_item.save(update_fields=["remarks"])

    def test_package_refresh_is_replay_safe_and_preserves_checklist_truth(self):
        url = f"/api/v1/loan-applications/{self.application.pk}/security-package/refresh/"
        first = self.client.post(
            url,
            {},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-package-create",
            HTTP_USER_AGENT="PoA Test Agent",
            REMOTE_ADDR="203.0.113.40",
            **self._auth(self.compliance),
        )
        self.assertEqual(first.status_code, 200, first.content)
        assert_success_envelope(self, first.json())
        data = first.json()["data"]
        self.assertEqual(data["loan_application_id"], str(self.application.pk))
        self.assertEqual(data["security_status"], "pending")
        self.assertTrue(data["poa_required_flag"])
        self.assertFalse(data["security_ready_flag"])
        self.assertIsNone(data["power_of_attorney"])

        replay = self.client.post(url, {}, content_type="application/json", **self._auth(self.compliance))
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], data)
        self.assertEqual(AuditLog.objects.filter(action="security.package.created").count(), 1)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="security_package").count(), 1)
        self.assertEqual(WorkflowEvent.objects.filter(workflow_name="security_package").count(), 1)
        audit = AuditLog.objects.get(action="security.package.created")
        self.assertEqual(audit.new_value_json["request_id"], "req-package-create")
        self.assertEqual(audit.ip_address, "203.0.113.40")

        self.poa_item.refresh_from_db()
        self.assertEqual(self.poa_item.completion_status, ChecklistItem.STATUS_PENDING)
        self.assertIsNone(self.poa_item.verified_by_user_id)
        self.assertEqual(self.poa_item.remarks, "Preserve checklist ownership.")

        read = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/security-package/",
            **self._auth(self.compliance),
        )
        self.assertEqual(read.status_code, 200, read.content)
        self.assertEqual(read.json()["data"], data)

    def test_package_read_role_and_object_scope_never_grants_mutation_or_reveal(self):
        package = self._refresh_package()
        read_permission = Permission.objects.get(
            permission_code="security.package.read"
        )
        assigned_cfo = self.fixture.cfo
        assigned_director = self.fixture.director
        unrelated_director = self.fixture.second_director
        for role in {
            assigned_cfo.primary_role,
            assigned_director.primary_role,
        }:
            RolePermission.objects.get_or_create(
                role=role, permission=read_permission
            )
        credit_manager = self._user("credit_manager", "security.package.read")
        senior_finance = self._user(
            "senior_manager_finance", "security.package.read", "documents.checklist.read"
        )
        cfc = self._user(
            "chief_financial_controller", "security.package.read", "documents.checklist.read"
        )
        auditor = self._user("internal_auditor", "security.package.read")
        ApprovalCaseReadScopeGrant.objects.create(
            role=auditor.primary_role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
        )
        company_secretary = self._user(
            "company_secretary", "security.package.read"
        )
        url = f"/api/v1/loan-applications/{self.application.pk}/security-package/"
        nested_urls = (
            f"/api/v1/security-packages/{package['security_package_id']}/power-of-attorney/",
            f"/api/v1/security-packages/{package['security_package_id']}/sh4-share-transfer-form/",
            f"/api/v1/security-packages/{package['security_package_id']}/cdsl-share-pledge/",
            f"/api/v1/security-packages/{package['security_package_id']}/blank-dated-cheque/",
        )

        allowed = (
            self.compliance,
            company_secretary,
            credit_manager,
            assigned_cfo,
            assigned_director,
            auditor,
        )
        for reader in allowed:
            with self.subTest(reader=reader.email):
                response = self.client.get(url, **self._auth(reader))
                self.assertEqual(response.status_code, 200, response.content)
                serialized = str(response.json()["data"])
                self.assertNotIn("storage_key", serialized)
                self.assertNotIn("download", serialized)
                self.assertNotIn("reveal", serialized)

        for reader in (senior_finance, cfc):
            with self.subTest(finance_reader_before_readiness=reader.email):
                self.assertEqual(
                    self.client.get(url, **self._auth(reader)).status_code, 403
                )
                self.assertEqual(
                    self.client.get(
                        f"/api/v1/loan-applications/{self.application.pk}/document-checklist/",
                        **self._auth(reader),
                    ).status_code,
                    403,
                )
                for nested_url in nested_urls:
                    self.assertEqual(
                        self.client.get(
                            nested_url, **self._auth(reader)
                        ).status_code,
                        403,
                    )

        self.application.legal_document_checklist.checklist_status = "sanction_approved"
        self.application.legal_document_checklist.save(update_fields=["checklist_status"])
        self.assertEqual(self.client.get(url, **self._auth(senior_finance)).status_code, 200)
        self.assertEqual(
            self.client.get(
                f"/api/v1/loan-applications/{self.application.pk}/document-checklist/",
                **self._auth(senior_finance),
            ).status_code,
            200,
        )
        for nested_url in nested_urls:
            self.assertEqual(
                self.client.get(
                    nested_url, **self._auth(senior_finance)
                ).status_code,
                404,
            )
        self.assertEqual(self.client.get(url, **self._auth(cfc)).status_code, 403)
        for nested_url in nested_urls:
            self.assertEqual(
                self.client.get(nested_url, **self._auth(cfc)).status_code,
                403,
            )

        unrelated = self.client.get(url, **self._auth(unrelated_director))
        self.assertEqual(unrelated.status_code, 403, unrelated.content)
        self.assertEqual(
            unrelated.json()["error"]["code"], "OBJECT_ACCESS_DENIED"
        )
        missing_permission = self._user("security_read_missing_permission")
        missing = self.client.get(
            "/api/v1/loan-applications/ffffffff-ffff-ffff-ffff-ffffffffffff/security-package/",
            **self._auth(missing_permission),
        )
        self.assertEqual(missing.status_code, 403, missing.content)
        self.assertEqual(missing.json()["error"]["code"], "FORBIDDEN")

        inactive = self._user("inactive_security_reader", "security.package.read")
        inactive.status = "inactive"
        inactive.save(update_fields=["status"])
        inactive_response = self.client.get(url, **self._auth_header(inactive))
        self.assertEqual(inactive_response.status_code, 401, inactive_response.content)

        refresh_url = (
            f"/api/v1/loan-applications/{self.application.pk}/security-package/refresh/"
        )
        mutation = self.client.post(
            refresh_url,
            {"unexpected": "must not parse"},
            content_type="application/json",
            **self._auth(credit_manager),
        )
        self.assertEqual(mutation.status_code, 403, mutation.content)
        self.assertEqual(mutation.json()["error"]["code"], "FORBIDDEN")
        poa_mutation = self.client.post(
            (
                f"/api/v1/security-packages/{package['security_package_id']}"
                "/power-of-attorney/"
            ),
            {"status": "active", "unexpected": "must not parse"},
            content_type="application/json",
            **self._auth(credit_manager),
        )
        self.assertEqual(poa_mutation.status_code, 403, poa_mutation.content)
        self.assertEqual(poa_mutation.json()["error"]["code"], "FORBIDDEN")
        self.assertEqual(PowerOfAttorney.objects.count(), 0)
        self.assertEqual(SecurityPackage.objects.count(), 1)
        self.assertEqual(
            str(SecurityPackage.objects.get().pk), package["security_package_id"]
        )

    def test_mutable_status_without_frozen_sanction_cannot_create_package(self):
        fake = LoanApplication.objects.create(
            application_reference_number="LO-FAKE-POA",
            member=self.member,
            nominee=self.nominee,
            borrower_type="individual_farmer",
            received_by_user=self.compliance,
            created_by_user=self.compliance,
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=LoanApplication.STATUS_APPROVED_BY_SANCTION,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
        )
        response = self.client.post(
            f"/api/v1/loan-applications/{fake.pk}/security-package/refresh/",
            {}, content_type="application/json", **self._auth(self.compliance),
        )
        self.assertEqual(response.status_code, 403, response.content)
        self.assertEqual(SecurityPackage.objects.count(), 0)

    def test_missing_manage_permission_denies_before_payload_and_writes_nothing(self):
        package = self._refresh_package()
        RolePermission.objects.filter(
            role=self.compliance.primary_role,
            permission__permission_code="security.poa.manage",
        ).delete()
        response = self.client.post(
            f"/api/v1/security-packages/{package['security_package_id']}/power-of-attorney/",
            {"status": "active"},
            content_type="application/json",
            **self._auth(self.compliance),
        )
        self.assertEqual(response.status_code, 403, response.content)
        self.assertEqual(PowerOfAttorney.objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(action__startswith="security.poa.").count(), 0)

    def test_missing_or_null_stamp_reference_cannot_create_poa(self):
        package = self._refresh_package()
        attorney = self._user("company_secretary", "security.poa.manage")
        document, _stamp, notary = self._poa_evidence()
        payload = {
            "borrower_member_id": str(self.member.pk),
            "nominee_id": str(self.nominee.pk),
            "attorney_user_id": str(attorney.pk),
            "purpose_summary": (
                "Authorise Company Secretary to initiate sale of shares on default."
            ),
            "loan_document_id": str(document.pk),
            "notarisation_record_id": str(notary.pk),
            "execution_status": "pending",
            "effective_from": None,
            "status": "draft",
        }
        url = (
            f"/api/v1/security-packages/{package['security_package_id']}"
            "/power-of-attorney/"
        )
        for supplied_value in ("omitted", None):
            with self.subTest(stamp_reference=supplied_value):
                candidate = dict(payload)
                if supplied_value is None:
                    candidate["stamp_duty_record_id"] = None
                response = self.client.post(
                    url,
                    candidate,
                    content_type="application/json",
                    **self._auth(self.compliance),
                )
                self.assertEqual(response.status_code, 400, response.content)
                self.assertIn(
                    "stamp_duty_record_id",
                    response.json()["error"]["field_errors"],
                )
                self.assertEqual(PowerOfAttorney.objects.count(), 0)
                self.assertEqual(
                    AuditLog.objects.filter(
                        action__startswith="security.poa."
                    ).count(),
                    0,
                )

    def test_missing_projection_target_rolls_back_poa_and_success_evidence(self):
        package = self._refresh_package()
        attorney = self._user("company_secretary", "security.poa.manage")
        document, stamp, notary = self._poa_evidence()
        self.poa_item.delete()
        response = self.client.post(
            f"/api/v1/security-packages/{package['security_package_id']}/power-of-attorney/",
            {
                "borrower_member_id": str(self.member.pk),
                "nominee_id": str(self.nominee.pk),
                "attorney_user_id": str(attorney.pk),
                "purpose_summary": "Authorise Company Secretary to initiate sale of shares on default.",
                "loan_document_id": str(document.pk),
                "stamp_duty_record_id": str(stamp.pk),
                "notarisation_record_id": str(notary.pk),
                "execution_status": "pending",
                "effective_from": None,
                "status": "draft",
            },
            content_type="application/json",
            **self._auth(self.compliance),
        )
        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(PowerOfAttorney.objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(action__startswith="security.poa.").count(), 0)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="power_of_attorney").count(), 0)

    def test_compliance_prepares_one_replay_safe_draft_from_canonical_facts(self):
        package = self._refresh_package()
        Role.objects.get_or_create(
            role_code="company_secretary",
            defaults={"role_name": "Company Secretary", "status": "active"},
        )
        attorney = self._user("legal_operations", "security.poa.manage")
        attorney.approval_authority_type = "company_secretary"
        attorney.save(update_fields=["approval_authority_type"])
        loan_document, stamp, notary = self._poa_evidence()
        payload = {
            "borrower_member_id": str(self.member.pk),
            "nominee_id": str(self.nominee.pk),
            "attorney_user_id": str(attorney.pk),
            "purpose_summary": "Authorise Company Secretary to initiate sale of shares on default.",
            "loan_document_id": str(loan_document.pk),
            "stamp_duty_record_id": str(stamp.pk),
            "notarisation_record_id": str(notary.pk),
            "execution_status": "pending",
            "effective_from": None,
            "status": "draft",
        }
        url = f"/api/v1/security-packages/{package['security_package_id']}/power-of-attorney/"
        negated = self.client.post(
            url,
            {
                **payload,
                "purpose_summary": (
                    "Company Secretary must not initiate sale of shares on default."
                ),
            },
            content_type="application/json",
            **self._auth(self.compliance),
        )
        self.assertEqual(negated.status_code, 400, negated.content)
        self.assertEqual(PowerOfAttorney.objects.count(), 0)
        first = self.client.post(
            url,
            payload,
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-poa-draft",
            **self._auth(self.compliance),
        )
        self.assertEqual(first.status_code, 200, first.content)
        assert_success_envelope(self, first.json())
        data = first.json()["data"]
        self.assertEqual(data["status"], "draft")
        self.assertEqual(data["execution_status"], "pending")
        self.assertEqual(data["prepared_by_user_id"], str(self.compliance.pk))
        self.assertIsNone(data["verified_by_user_id"])
        self.assertNotIn("document_download_url", data)

        replay = self.client.post(url, payload, content_type="application/json", **self._auth(self.compliance))
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], data)
        self.assertEqual(PowerOfAttorney.objects.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="security.poa.created").count(), 1)

        second_compliance = self.fixture._user(
            "compliance_team_member",
            "Second PoA Compliance",
            "security.poa.manage",
            "security.package.read",
        )
        changed = {
            **payload,
            "purpose_summary": (
                "Authorise Company Secretary to initiate sale of shares on default. "
                "This does not waive unrelated statutory protections."
            ),
        }
        changed_response = self.client.patch(
            f"/api/v1/power-of-attorneys/{data['power_of_attorney_id']}/",
            changed,
            content_type="application/json",
            **self._auth(second_compliance),
        )
        self.assertEqual(changed_response.status_code, 200, changed_response.content)
        self.assertEqual(
            changed_response.json()["data"]["prepared_by_user_id"],
            str(second_compliance.pk),
        )
        data = changed_response.json()["data"]
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="power_of_attorney").count(), 2)

        read = self.client.get(url, **self._auth(self.compliance))
        self.assertEqual(read.status_code, 200, read.content)
        public = read.json()["data"]
        for key in ("power_of_attorney_id", "purpose_summary", "execution_status", "status"):
            self.assertEqual(public[key], data[key])
        self.assertFalse(
            {"prepared_by_user_id", "verified_by_user_id", "activation_evidence"}
            .intersection(public)
        )
        self.poa_item.refresh_from_db()
        self.assertEqual(self.poa_item.completion_status, "pending")
        self.assertEqual(self.poa_item.poa_execution_status, "pending")
        self.assertEqual(self.poa_item.poa_status, "draft")

    def test_company_secretary_activates_only_with_current_maker_checker_and_signatures(self):
        package = self._refresh_package()
        attorney = self._user(
            "company_secretary", "security.poa.manage", "security.package.read",
            "documents.stamp.record", "documents.notary.record",
        )
        document, stamp, notary = self._poa_evidence()
        draft = {
            "borrower_member_id": str(self.member.pk),
            "nominee_id": str(self.nominee.pk),
            "attorney_user_id": str(attorney.pk),
            "purpose_summary": "Authorise Company Secretary to initiate sale of shares on default.",
            "loan_document_id": str(document.pk),
            "stamp_duty_record_id": str(stamp.pk),
            "notarisation_record_id": str(notary.pk),
            "execution_status": "pending",
            "effective_from": None,
            "status": "draft",
        }
        created = self.client.post(
            f"/api/v1/security-packages/{package['security_package_id']}/power-of-attorney/",
            draft, content_type="application/json", **self._auth(self.compliance),
        )
        self.assertEqual(created.status_code, 200, created.content)
        poa_id = created.json()["data"]["power_of_attorney_id"]

        stamp_notary.record_stamp(
            actor=attorney, loan_document_id=document.pk,
            payload={
                "stamp_paper_amount": "500.00", "stamp_type": "physical",
                "stamp_number": "MH-POA-001", "stamp_purchase_date": "2026-07-13",
                "executed_date": "2026-07-14", "status": "adequate",
                "remarks": "Verified through 008D2.",
            },
            metadata=stamp_notary.RequestMetadata("poa-stamp-verify", "", ""),
        )
        notary_evidence = self._notary_evidence()
        stamp_notary.record_notary(
            actor=attorney, loan_document_id=document.pk,
            payload={
                "notary_name": "Verified Notary",
                "notary_registration_number": "NOT-POA-001",
                "notarised_date": "2026-07-14", "status": "completed",
                "evidence_document_id": notary_evidence.pk,
                "remarks": "Verified through 008D2.",
            },
            metadata=stamp_notary.RequestMetadata("poa-notary-verify", "", ""),
        )
        signed_at = timezone.now()
        signature_rows = []
        for party_type, party_id, party_name in (
            ("borrower", self.member.pk, self.member.legal_name),
            ("nominee", self.nominee.pk, self.nominee.nominee_name),
        ):
            signatures.record(
                actor=self.compliance, loan_document_id=document.pk,
                payload={
                    "signer_party_type": party_type,
                    "signer_party_id": party_id,
                    "signer_name_snapshot": party_name,
                    "signature_method": "wet_ink", "signature_status": "signed",
                    "signed_at": signed_at.isoformat(), "signature_mismatch_flag": False,
                },
                metadata=signatures.RequestMetadata(
                    f"poa-{party_type}-signature", "", ""
                ),
            )
            signature_rows.append(SignatureRecord.objects.get(
                loan_document=document, signer_party_type=party_type
            ))
        for row in signature_rows:
            row.captured_by_user = None
            row.save(update_fields=["captured_by_user"])

        active = {**draft, "execution_status": "executed", "effective_from": "2026-07-14", "status": "active"}
        url = f"/api/v1/power-of-attorneys/{poa_id}/"
        legacy_denied = self.client.patch(
            url, active, content_type="application/json", **self._auth(attorney),
        )
        self.assertEqual(legacy_denied.status_code, 400, legacy_denied.content)
        self.assertEqual(
            VersionHistory.objects.filter(versioned_entity_type="power_of_attorney").count(), 1
        )
        for row in signature_rows:
            row.captured_by_user = self.compliance
            row.save(update_fields=["captured_by_user"])
        Member.objects.filter(pk=self.member.pk).update(legal_name="Renamed Borrower")
        Nominee.objects.filter(pk=self.nominee.pk).update(nominee_name="Renamed Nominee")
        before_counts = {
            "audit": AuditLog.objects.filter(action="security.poa.activated").count(),
            "version": VersionHistory.objects.filter(
                versioned_entity_type="power_of_attorney"
            ).count(),
            "workflow": WorkflowEvent.objects.filter(
                workflow_name="power_of_attorney", to_state="active"
            ).count(),
        }
        for wrong_value in ("1.00", "499.99", "500.01"):
            with self.subTest(stamp_paper_amount=wrong_value):
                StampDutyRecord.objects.filter(pk=stamp.pk).update(
                    stamp_paper_amount=wrong_value
                )
                wrong_amount = self.client.patch(
                    url, active, content_type="application/json",
                    HTTP_X_REQUEST_ID=f"req-poa-wrong-stamp-{wrong_value}",
                    **self._auth(attorney),
                )
                self.assertEqual(
                    wrong_amount.status_code, 400, wrong_amount.content
                )
                self.assertIn(
                    "exact ₹500.00",
                    wrong_amount.json()["error"]["field_errors"][
                        "stamp_duty_record_id"
                    ],
                )
                self.assertEqual(
                    PowerOfAttorney.objects.get(pk=poa_id).status, "draft"
                )
                self.assertEqual(
                    {
                        "audit": AuditLog.objects.filter(
                            action="security.poa.activated"
                        ).count(),
                        "version": VersionHistory.objects.filter(
                            versioned_entity_type="power_of_attorney"
                        ).count(),
                        "workflow": WorkflowEvent.objects.filter(
                            workflow_name="power_of_attorney", to_state="active"
                        ).count(),
                    },
                    before_counts,
                )
        StampDutyRecord.objects.filter(pk=stamp.pk).update(stamp_paper_amount="500.00")
        response = self.client.patch(
            url, active, content_type="application/json",
            HTTP_X_REQUEST_ID="req-poa-active", **self._auth(attorney),
        )
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["entity_type"], "power_of_attorney")
        self.assertEqual(data["entity_id"], poa_id)
        self.assertEqual(data["previous_status"], "draft")
        self.assertEqual(data["new_status"], "active")
        self.assertIsNotNone(data["workflow_event_id"])
        self.assertEqual(data["available_actions"], [])

        replay = self.client.patch(url, active, content_type="application/json", **self._auth(attorney))
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], data)
        self.assertEqual(VersionHistory.objects.filter(versioned_entity_type="power_of_attorney").count(), 2)
        self.assertEqual(AuditLog.objects.filter(action="security.poa.activated").count(), 1)
        self.poa_item.refresh_from_db()
        self.assertEqual(self.poa_item.completion_status, "pending")
        self.assertIsNone(self.poa_item.verified_by_user_id)
        self.assertEqual(self.poa_item.poa_execution_status, "executed")
        self.assertEqual(self.poa_item.poa_status, "active")
        package_read = self.client.get(
            f"/api/v1/loan-applications/{self.application.pk}/security-package/",
            **self._auth(attorney),
        )
        self.assertEqual(package_read.json()["data"]["security_status"], "pending")
        self.assertFalse(package_read.json()["data"]["security_ready_flag"])
        retained = package_read.json()["data"]["power_of_attorney"]
        self.assertEqual(retained["status"], "active")
        self.assertEqual(retained["execution_status"], "executed")
        forbidden = {
            "prepared_by_user_id",
            "verified_by_user_id",
            "activation_evidence",
            "legacy_activation_evidence",
            "loan_document_id",
            "stamp_duty_record_id",
            "notarisation_record_id",
        }
        self.assertFalse(forbidden.intersection(retained))
        serialized = str(retained)
        for secret in ("request_id", "ip_address", "user_agent", "signer_name_snapshot"):
            self.assertNotIn(secret, serialized)

        consumed_signature = signature_rows[0]
        with self.assertRaises(signatures.InvalidState):
            signatures.record(
                actor=self.compliance,
                loan_document_id=document.pk,
                payload={
                    "signer_party_type": consumed_signature.signer_party_type,
                    "signer_party_id": consumed_signature.signer_party_id,
                    "signer_name_snapshot": consumed_signature.signer_name_snapshot,
                    "signature_method": "wet_ink",
                    "signature_status": "pending",
                    "signed_at": None,
                    "signature_mismatch_flag": False,
                },
                metadata=signatures.RequestMetadata("blocked-signature-rewrite", "", ""),
            )
        with self.assertRaises(ValidationError):
            stamp_notary.record_stamp(
                actor=attorney,
                loan_document_id=document.pk,
                payload={
                    "stamp_paper_amount": "500.00",
                    "stamp_type": "physical",
                    "stamp_number": "MH-POA-001",
                    "stamp_purchase_date": "2026-07-13",
                    "executed_date": "2026-07-14",
                    "status": "insufficient",
                    "remarks": "Must not replace consumed evidence.",
                },
                metadata=stamp_notary.RequestMetadata("blocked-stamp-rewrite", "", ""),
            )
        self.assertEqual(AuditLog.objects.filter(action="documents.signature.changed").count(), 0)
        self.assertEqual(AuditLog.objects.filter(action="documents.stamp.changed").count(), 1)

        downgrade = self.client.patch(
            url, draft, content_type="application/json", **self._auth(self.compliance),
        )
        self.assertEqual(downgrade.status_code, 409, downgrade.content)

        forbidden_state = self.client.patch(
            url, {**active, "status": "invoked"}, content_type="application/json",
            **self._auth(attorney),
        )
        self.assertEqual(forbidden_state.status_code, 400, forbidden_state.content)
        self.assertEqual(AuditLog.objects.filter(action="security.poa.activated").count(), 1)

    def _refresh_package(self):
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/security-package/refresh/",
            {}, content_type="application/json", **self._auth(self.compliance)
        )
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()["data"]

    def _poa_evidence(self, document_type="power_of_attorney"):
        generation_tests = import_module(
            "sfpcl_credit.tests.test_loan_document_generation_api"
        )
        template_bytes = generation_tests.LoanDocumentGenerationApiTests._genuine_docx_fixture(
            ["borrower_name"]
        )
        storage = LocalDocumentStorage()
        stored_template = storage.store(
            SimpleUploadedFile("poa-template.docx", template_bytes)
        )
        template_file = DocumentFile.objects.create(
            file_name="poa-template.docx", file_extension=".docx",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            file_size_bytes=stored_template.file_size_bytes,
            storage_provider=stored_template.storage_provider,
            storage_key=stored_template.storage_key,
            checksum_sha256=stored_template.checksum_sha256,
            uploaded_by_user=self.compliance, sensitivity_level="internal",
        )
        AuditLog.objects.create(
            actor_user=self.compliance,
            actor_type="user",
            action="documents.file.uploaded",
            entity_type="document_file",
            entity_id=template_file.pk,
            new_value_json={
                "document_id": str(template_file.pk),
                "file_name": template_file.file_name,
                "file_extension": template_file.file_extension,
                "mime_type": template_file.mime_type,
                "file_size_bytes": template_file.file_size_bytes,
                "storage_provider": template_file.storage_provider,
                "storage_key": template_file.storage_key,
                "checksum_sha256": template_file.checksum_sha256,
                "sensitivity_level": template_file.sensitivity_level,
                "document_category": "template_source",
                "related_entity_type": "global",
                "related_entity_id": None,
            },
        )
        template = DocumentTemplate.objects.create(
            template_code=f"{document_type}-workflow-v1",
            template_name=f"{document_type.replace('_', ' ').title()} Workflow",
            document_type=document_type, borrower_type="individual_farmer",
            template_version="1.0", template_file=template_file,
            approval_status="approved", effective_from="2026-01-01",
            merge_fields_json=["borrower_name"],
        )
        generated = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/loan-documents/generate/",
            {
                "document_type": document_type,
                "template_id": str(template.pk),
                "output_format": "docx",
            },
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-public-poa-generation",
            **self._auth(self.compliance),
        )
        self.assertEqual(generated.status_code, 200, generated.content)
        document = LoanDocument.objects.get(
            pk=generated.json()["data"]["loan_document_id"]
        )
        self.poa_item.loan_document = document
        self.poa_item.save(update_fields=["loan_document"])
        stamp_notary.record_stamp(
            actor=self.compliance, loan_document_id=document.pk,
            payload={
                "stamp_paper_amount": "500.00", "stamp_type": "physical",
                "stamp_number": None, "stamp_purchase_date": None,
                "executed_date": None, "status": "pending",
                "remarks": "Prepared through 008D2.",
            },
            metadata=stamp_notary.RequestMetadata("poa-stamp-prepare", "", ""),
        )
        stamp_notary.record_notary(
            actor=self.compliance, loan_document_id=document.pk,
            payload={
                "notary_name": None, "notary_registration_number": None,
                "notarised_date": None, "status": "pending",
                "evidence_document_id": None, "remarks": "Prepared through 008D2.",
            },
            metadata=stamp_notary.RequestMetadata("poa-notary-prepare", "", ""),
        )
        stamp = StampDutyRecord.objects.get(loan_document=document)
        notary = NotarisationRecord.objects.get(loan_document=document)
        return document, stamp, notary

    def _notary_evidence(self):
        evidence = DocumentFile.objects.create(
            file_name="poa-notary-evidence.pdf", file_extension=".pdf",
            mime_type="application/pdf", file_size_bytes=8,
            storage_provider="local", storage_key="tests/poa-notary-evidence.pdf",
            checksum_sha256="7" * 64, uploaded_by_user=self.compliance,
            sensitivity_level="confidential",
        )
        AuditLog.objects.create(
            actor_user=self.compliance, actor_type="user",
            action="documents.file.uploaded", entity_type="document_file",
            entity_id=evidence.pk,
            new_value_json={
                "document_id": str(evidence.pk), "file_name": evidence.file_name,
                "file_extension": evidence.file_extension, "mime_type": evidence.mime_type,
                "file_size_bytes": evidence.file_size_bytes,
                "storage_provider": evidence.storage_provider,
                "storage_key": evidence.storage_key,
                "checksum_sha256": evidence.checksum_sha256,
                "sensitivity_level": evidence.sensitivity_level,
                "document_category": "legal", "related_entity_type": "application",
                "related_entity_id": str(self.application.pk),
            },
        )
        return evidence

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
                    "module_name": "security",
                    "risk_level": "high",
                },
            )
            RolePermission.objects.create(role=role, permission=permission)
        user = User.objects.create(
            full_name=role.role_name,
            email=f"{role_code}@poa.example",
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

    def _auth_header(self, user):
        from sfpcl_credit.identity.models import UserSession
        from sfpcl_credit.identity.modules.tokens import access_claims, encode_token

        session = UserSession.objects.create(
            user=user,
            refresh_token_hash="inactive-test",
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )
        return {
            "HTTP_AUTHORIZATION": f"Bearer {encode_token(access_claims(user, session))}"
        }


@skipUnless(connection.vendor == "postgresql", "PostgreSQL row-lock acceptance only")
class PowerOfAttorneyConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = PowerOfAttorneyApiTests(
            methodName="test_company_secretary_activates_only_with_current_maker_checker_and_signatures"
        )
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture = fixture
        self.actor = fixture.compliance
        self.attorney = fixture._user("company_secretary", "security.poa.manage")
        package = fixture._refresh_package()
        self.package = SecurityPackage.objects.get(pk=package["security_package_id"])
        document, stamp, notary = fixture._poa_evidence()
        StampDutyRecord.objects.filter(pk=stamp.pk).update(
            status="adequate", stamp_paper_amount="500.00",
            stamp_purchase_date="2026-07-13", executed_date="2026-07-14",
            verified_by_user=self.attorney,
        )
        notary_evidence = fixture._notary_evidence()
        NotarisationRecord.objects.filter(pk=notary.pk).update(
            status="completed", notarised_date="2026-07-14",
            notary_name="Race Notary",
            notary_registration_number="RACE-NOTARY-001",
            evidence_document=notary_evidence,
            verified_by_user=self.attorney,
        )
        now = timezone.now()
        for party_type, party_id, name in (
            ("borrower", fixture.member.pk, fixture.member.legal_name),
            ("nominee", fixture.nominee.pk, fixture.nominee.nominee_name),
        ):
            SignatureRecord.objects.create(
                loan_document=document,
                signer_party_type=party_type,
                signer_party_id=party_id,
                signer_name_snapshot=name,
                signature_method="wet_ink",
                signature_status="signed",
                signed_at=now,
                signature_mismatch_flag=False,
                captured_by_user=self.actor,
                verified_by_user=self.actor,
                verified_at=now,
            )
        stamp.refresh_from_db()
        notary.refresh_from_db()
        self.values = {
            "borrower_member_id": fixture.member.pk, "nominee_id": fixture.nominee.pk,
            "attorney_user_id": self.attorney.pk,
            "purpose_summary": "Authorise Company Secretary to initiate sale of shares on default.",
            "loan_document_id": document.pk, "stamp_duty_record_id": stamp.pk,
            "notarisation_record_id": notary.pk, "execution_status": "pending",
            "effective_from": None, "status": "draft",
        }

    def _draft(self):
        security_instrument_evidence.create_poa(
            actor=self.actor, security_package_id=self.package.pk, values=self.values,
            metadata=power_of_attorney.RequestMetadata("race-seed", "", ""),
        )
        return PowerOfAttorney.objects.get()

    def test_five_changed_activations_retain_one_terminal_activation(self):
        poa = self._draft()
        barrier = Barrier(5)

        def worker(index):
            close_old_connections()
            actor = User.objects.get(pk=self.attorney.pk)
            values = {
                **self.values,
                "execution_status": "executed",
                "effective_from": timezone.localdate().replace(day=10 + index),
                "status": "active",
            }
            barrier.wait()
            try:
                security_instrument_evidence.update_poa(
                    actor=actor, power_of_attorney_id=poa.pk, values=values,
                    metadata=power_of_attorney.RequestMetadata(f"race-activate-{index}", "", ""),
                )
                return f"race-activate-{index}"
            except power_of_attorney.Conflict:
                return None
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(worker, range(5)))
        winner_request_ids = [result for result in results if result is not None]
        self.assertEqual(len(winner_request_ids), 1)
        winner_request_id = winner_request_ids[0]
        poa.refresh_from_db()
        self.assertEqual(poa.status, "active")
        self.assertEqual(
            poa.activation_evidence_json["request_id"], winner_request_id
        )
        activation_audit = AuditLog.objects.get(action="security.poa.activated")
        activation_version = VersionHistory.objects.get(
            versioned_entity_type="power_of_attorney",
            change_summary="security.poa.activated",
        )
        activation_event = WorkflowEvent.objects.get(
            pk=poa.activation_workflow_event_id
        )
        consumed_audit = AuditLog.objects.get(
            action="documents.execution.consumed"
        )
        self.assertEqual(
            activation_audit.new_value_json["activation_evidence"]["request_id"],
            winner_request_id,
        )
        self.assertEqual(
            activation_version.new_value_json["activation_evidence"]["request_id"],
            winner_request_id,
        )
        self.assertEqual(
            consumed_audit.new_value_json["request_id"], winner_request_id
        )
        self.assertEqual(
            consumed_audit.new_value_json["workflow_event_id"],
            str(activation_event.pk),
        )
        self.assertEqual(activation_event.from_state, "draft")
        self.assertEqual(activation_event.to_state, "active")
        self.assertEqual(activation_event.triggered_by_user_id, self.attorney.pk)
        success_evidence = str(
            list(
                AuditLog.objects.filter(
                    action__in={
                        "security.poa.activated",
                        "documents.execution.consumed",
                    }
                ).values_list("new_value_json", flat=True)
            )
            + list(
                VersionHistory.objects.filter(
                    versioned_entity_type="power_of_attorney"
                ).values_list("new_value_json", flat=True)
            )
        )
        for index in range(5):
            request_id = f"race-activate-{index}"
            self.assertEqual(
                request_id in success_evidence, request_id == winner_request_id
            )

    def test_five_downgrades_cannot_change_terminal_activation(self):
        poa = self._draft()
        security_instrument_evidence.update_poa(
            actor=self.attorney,
            power_of_attorney_id=poa.pk,
            values={
                **self.values,
                "execution_status": "executed",
                "effective_from": timezone.localdate(),
                "status": "active",
            },
            metadata=power_of_attorney.RequestMetadata("race-activate-seed", "", ""),
        )
        barrier = Barrier(5)
        baseline = {
            "audit": AuditLog.objects.count(),
            "version": VersionHistory.objects.count(),
            "workflow": WorkflowEvent.objects.count(),
        }

        def worker(index):
            close_old_connections()
            actor = User.objects.get(pk=self.actor.pk)
            barrier.wait()
            try:
                security_instrument_evidence.update_poa(
                    actor=actor, power_of_attorney_id=poa.pk, values=self.values,
                    metadata=power_of_attorney.RequestMetadata(f"race-downgrade-{index}", "", ""),
                )
                return "changed"
            except power_of_attorney.Conflict:
                return "conflict"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(worker, range(5)))
        self.assertEqual(results, ["conflict"] * 5)
        poa.refresh_from_db()
        self.assertEqual(poa.status, "active")
        self.assertEqual(AuditLog.objects.filter(action="security.poa.activated").count(), 1)
        self.assertEqual(
            {
                "audit": AuditLog.objects.count(),
                "version": VersionHistory.objects.count(),
                "workflow": WorkflowEvent.objects.count(),
            },
            baseline,
        )
        retained_evidence = str(
            list(AuditLog.objects.values_list("new_value_json", flat=True))
            + list(VersionHistory.objects.values_list("new_value_json", flat=True))
        )
        for index in range(5):
            self.assertNotIn(f"race-downgrade-{index}", retained_evidence)
