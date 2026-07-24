import uuid
from datetime import date
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.test.utils import override_settings

from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant
from sfpcl_credit.compliance.models import (
    AuditObservation,
    ComplianceControl,
    ComplianceEvidence,
    ComplianceTask,
)
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.workflows.models import WorkflowEvent


class AuditObservationApiTests(TestCase):
    URL = "/api/v1/audit-observations/"
    password = "AuditObservationPass123!"

    def setUp(self):
        self.client = Client()
        self.storage_directory = TemporaryDirectory()
        self.addCleanup(self.storage_directory.cleanup)
        storage_override = override_settings(
            DOCUMENT_STORAGE_ROOT=self.storage_directory.name
        )
        storage_override.enable()
        self.addCleanup(storage_override.disable)
        self.role = Role.objects.create(
            role_code="internal_auditor",
            role_name="Internal Auditor",
            is_system_role=True,
            status="active",
        )
        for code in (
            "audit.audit_log.read",
            "audit.workflow_event.read",
            "audit.version_history.read",
            "audit.observation.read",
            "audit.observation.create",
            "reports.compliance.read",
            "documents.file.download",
        ):
            permission = Permission.objects.create(
                permission_code=code,
                permission_name=code,
                module_name="audit",
                risk_level="high",
            )
            RolePermission.objects.create(role=self.role, permission=permission)
        ApprovalCaseReadScopeGrant.objects.create(
            role=self.role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
        )
        self.auditor = User.objects.create(
            full_name="Ivy Observation Auditor",
            email="audit.observation@sfpcl.example",
            status="active",
            primary_role=self.role,
        )
        self.auditor.set_password(self.password)
        self.auditor.save(update_fields=["password_hash"])

    def test_scoped_auditor_creates_and_reads_durable_observation(self):
        sampled = AuditLog.objects.create(
            actor_user=self.auditor,
            action="compliance.evidence_submitted",
            entity_type="compliance_evidence",
            entity_id=uuid.uuid4(),
            new_value_json={"outcome": "accepted"},
        )

        response = self.client.post(
            self.URL,
            {
                "audit_scope": "audit_readonly",
                "observation": "Sampled evidence is complete and traceable.",
                "source_references": [
                    {
                        "source_type": "audit_log",
                        "source_id": str(sampled.pk),
                    }
                ],
            },
            content_type="application/json",
            **self._auth(),
        )

        self.assertEqual(response.status_code, 200, response.content)
        created = response.json()["data"]
        observation_id = created["audit_observation_id"]
        self.assertEqual(created["audit_scope"], "audit_readonly")
        self.assertEqual(
            created["observation"],
            "Sampled evidence is complete and traceable.",
        )
        self.assertEqual(
            created["creator"],
            {
                "user_id": str(self.auditor.pk),
                "full_name": self.auditor.full_name,
                "role_code": "internal_auditor",
                "team_codes": [],
            },
        )
        self.assertEqual(
            created["source_references"],
            [
                {
                    "source_type": "audit_log",
                    "source_id": str(sampled.pk),
                    "entity_type": "compliance_evidence",
                    "entity_id": str(sampled.entity_id),
                }
            ],
        )
        self.assertIsNotNone(created["created_at"])

        self.auditor.full_name = "Renamed After Observation"
        self.auditor.save(update_fields=["full_name"])
        listing = self.client.get(self.URL, **self._auth())
        detail = self.client.get(f"{self.URL}{observation_id}/", **self._auth())

        self.assertEqual(listing.status_code, 200, listing.content)
        self.assertEqual(listing.json()["pagination"]["total_count"], 1)
        self.assertEqual(listing.json()["data"], [created])
        self.assertEqual(detail.status_code, 200, detail.content)
        self.assertEqual(detail.json()["data"], created)
        creation_audit = AuditLog.objects.get(
            action="audit.observation.created",
            entity_id=observation_id,
        )
        self.assertEqual(creation_audit.actor_user_id, self.auditor.pk)
        self.assertEqual(
            creation_audit.new_value_json["source_references"],
            created["source_references"],
        )

    def test_observation_text_and_payload_are_strictly_sanitised(self):
        sampled = AuditLog.objects.create(
            actor_user=self.auditor,
            action="compliance.evidence_submitted",
            entity_type="compliance_evidence",
            entity_id=uuid.uuid4(),
        )
        base = {
            "audit_scope": "audit_readonly",
            "source_references": [
                {"source_type": "audit_log", "source_id": str(sampled.pk)}
            ],
        }
        unsafe_payloads = (
            {**base, "observation": ""},
            {**base, "observation": "x" * 2001},
            {**base, "observation": "<script>alert('sample')</script>"},
            {**base, "observation": "Borrower PAN is ABCDE1234F"},
            {**base, "observation": "Valid note", "status": "open"},
            {**base, "observation": "Valid note", "severity": "high"},
            {**base, "observation": "Valid note", "assigned_to": str(self.auditor.pk)},
            {
                **base,
                "observation": "Duplicate reference.",
                "source_references": base["source_references"] * 2,
            },
            {
                **base,
                "observation": "Unbounded reference list.",
                "source_references": base["source_references"] * 21,
            },
        )

        for payload in unsafe_payloads:
            with self.subTest(payload_keys=sorted(payload)):
                response = self.client.post(
                    self.URL,
                    payload,
                    content_type="application/json",
                    **self._auth(),
                )
                self.assertEqual(response.status_code, 400, response.content)
                self.assertEqual(response.json()["error"]["code"], "VALIDATION_ERROR")

        self.assertEqual(AuditObservation.objects.count(), 0)

    def test_restricted_compliance_evidence_uses_a_scoped_signed_download(self):
        evidence = self._compliance_evidence()

        response = self.client.post(
            self.URL,
            {
                "audit_scope": "audit_readonly",
                "observation": "Restricted evidence was sampled under audit scope.",
                "source_references": [
                    {
                        "source_type": "compliance_evidence",
                        "source_id": str(evidence.pk),
                    }
                ],
            },
            content_type="application/json",
            **self._auth(),
        )

        self.assertEqual(response.status_code, 200, response.content)
        reference = response.json()["data"]["source_references"][0]
        self.assertEqual(reference["source_type"], "compliance_evidence")
        self.assertEqual(reference["source_id"], str(evidence.pk))
        self.assertEqual(reference["entity_type"], "document_file")
        self.assertEqual(reference["entity_id"], str(evidence.document_id))
        self.assertEqual(
            reference["evidence"],
            {
                "document_id": str(evidence.document_id),
                "file_name": "restricted-evidence.pdf",
                "sensitivity_level": "restricted",
                "download_url": reference["evidence"]["download_url"],
                "expires_at": reference["evidence"]["expires_at"],
            },
        )
        self.assertIn("token=", reference["evidence"]["download_url"])
        self.assertNotIn("storage_key", str(reference))

        downloaded = self.client.get(
            reference["evidence"]["download_url"],
            **self._auth(),
        )

        self.assertEqual(downloaded.status_code, 200, downloaded.content)
        self.assertEqual(downloaded.content, b"restricted audit evidence")
        access_audit = AuditLog.objects.get(
            action="audit.observation.evidence_accessed"
        )
        self.assertEqual(access_audit.actor_user_id, self.auditor.pk)
        self.assertEqual(
            access_audit.new_value_json["document_id"],
            str(evidence.document_id),
        )
        self.assertNotIn("storage_key", str(access_audit.new_value_json))

    def test_out_of_scope_auditor_and_operational_role_are_denied_and_audited(self):
        sampled = AuditLog.objects.create(
            actor_user=self.auditor,
            action="compliance.evidence_submitted",
            entity_type="compliance_evidence",
            entity_id=uuid.uuid4(),
        )
        payload = {
            "audit_scope": "audit_readonly",
            "observation": "A governed auditor observation.",
            "source_references": [
                {"source_type": "audit_log", "source_id": str(sampled.pk)}
            ],
        }
        ApprovalCaseReadScopeGrant.objects.filter(role=self.role).update(
            status=ApprovalCaseReadScopeGrant.STATUS_INACTIVE
        )

        denied_auditor = self.client.post(
            self.URL,
            payload,
            content_type="application/json",
            **self._auth(),
        )

        operational_role = Role.objects.create(
            role_code="credit_manager",
            role_name="Credit Manager",
        )
        for code in ("audit.observation.read", "audit.observation.create"):
            RolePermission.objects.create(
                role=operational_role,
                permission=Permission.objects.get(permission_code=code),
            )
        operational_user = User.objects.create(
            full_name="Operational User",
            email="operational.user@sfpcl.example",
            primary_role=operational_role,
        )
        operational_user.set_password(self.password)
        operational_user.save(update_fields=["password_hash"])
        forged = self.client.post(
            self.URL,
            payload,
            content_type="application/json",
            **self._auth_for(operational_user),
        )

        self.assertEqual(denied_auditor.status_code, 403, denied_auditor.content)
        self.assertEqual(forged.status_code, 403, forged.content)
        self.assertEqual(AuditObservation.objects.count(), 0)
        denials = AuditLog.objects.filter(
            action="audit.observation.access_denied"
        ).order_by("created_at")
        self.assertEqual(denials.count(), 2)
        self.assertEqual(
            [row.actor_user_id for row in denials],
            [self.auditor.pk, operational_user.pk],
        )
        for denial in denials:
            self.assertEqual(denial.new_value_json["method"], "POST")
            self.assertEqual(denial.new_value_json["path"], self.URL)
            self.assertEqual(denial.new_value_json["outcome"], "denied")

    def test_observation_and_sampled_truth_reject_all_mutation_paths(self):
        sampled = AuditLog.objects.create(
            actor_user=self.auditor,
            action="compliance.evidence_submitted",
            entity_type="compliance_evidence",
            entity_id=uuid.uuid4(),
            new_value_json={"outcome": "accepted"},
        )
        created = self.client.post(
            self.URL,
            {
                "audit_scope": "audit_readonly",
                "observation": "Immutable sampled-file observation.",
                "source_references": [
                    {"source_type": "audit_log", "source_id": str(sampled.pk)}
                ],
            },
            content_type="application/json",
            **self._auth(),
        ).json()["data"]
        detail_url = f"{self.URL}{created['audit_observation_id']}/"

        for method in ("put", "patch", "delete"):
            with self.subTest(method=method):
                response = getattr(self.client, method)(
                    detail_url,
                    {"observation": "rewritten"},
                    content_type="application/json",
                    **self._auth(),
                )
                self.assertEqual(response.status_code, 405, response.content)

        observation = AuditObservation.objects.get(
            pk=created["audit_observation_id"]
        )
        observation.observation_text = "rewritten"
        with self.assertRaises(ValidationError):
            observation.save()
        with self.assertRaises(ValidationError):
            observation.delete()
        with self.assertRaises(ValidationError):
            AuditObservation.objects.filter(pk=observation.pk).update(
                observation_text="rewritten"
            )
        with self.assertRaises(ValidationError):
            AuditObservation.objects.filter(pk=observation.pk).delete()

        observation.refresh_from_db()
        sampled.refresh_from_db()
        self.assertEqual(
            AuditLog.objects.filter(
                action="audit.observation.access_denied",
                actor_user=self.auditor,
            ).count(),
            3,
        )
        self.assertEqual(
            observation.observation_text,
            "Immutable sampled-file observation.",
        )
        self.assertEqual(sampled.new_value_json, {"outcome": "accepted"})

    def test_workflow_version_and_guessed_or_foreign_references_are_governed(self):
        entity_id = uuid.uuid4()
        workflow = WorkflowEvent.objects.create(
            workflow_name="compliance_review",
            entity_type="compliance_task",
            entity_id=entity_id,
            to_state="completed",
            triggered_by_user=self.auditor,
        )
        version = VersionHistory.objects.create(
            versioned_entity_type="loan_policy_config",
            versioned_entity_id=entity_id,
            version_number="2.0",
            change_summary="Approved retained-control version.",
            effective_from=date(2026, 7, 1),
            author_user=self.auditor,
        )

        created = self.client.post(
            self.URL,
            {
                "audit_scope": "audit_readonly",
                "observation": "Workflow and approved version were sampled.",
                "source_references": [
                    {
                        "source_type": "workflow_event",
                        "source_id": str(workflow.pk),
                    },
                    {
                        "source_type": "version_history",
                        "source_id": str(version.pk),
                    },
                ],
            },
            content_type="application/json",
            **self._auth(),
        )

        self.assertEqual(created.status_code, 200, created.content)
        self.assertEqual(
            created.json()["data"]["source_references"],
            [
                {
                    "source_type": "workflow_event",
                    "source_id": str(workflow.pk),
                    "entity_type": "compliance_task",
                    "entity_id": str(entity_id),
                },
                {
                    "source_type": "version_history",
                    "source_id": str(version.pk),
                    "entity_type": "loan_policy_config",
                    "entity_id": str(entity_id),
                },
            ],
        )

        for source_type, source_id in (
            ("audit_log", workflow.pk),
            ("version_history", uuid.uuid4()),
        ):
            with self.subTest(source_type=source_type):
                denied = self.client.post(
                    self.URL,
                    {
                        "audit_scope": "audit_readonly",
                        "observation": "Guessed reference must not be sampled.",
                        "source_references": [
                            {
                                "source_type": source_type,
                                "source_id": str(source_id),
                            }
                        ],
                    },
                    content_type="application/json",
                    **self._auth(),
                )
                self.assertEqual(denied.status_code, 404, denied.content)

        self.assertEqual(
            AuditLog.objects.filter(
                action="audit.observation.access_denied"
            ).count(),
            2,
        )

    def test_list_filters_creator_and_rejects_unknown_lifecycle_filters(self):
        sampled = AuditLog.objects.create(
            actor_user=self.auditor,
            action="compliance.evidence_submitted",
            entity_type="compliance_evidence",
            entity_id=uuid.uuid4(),
        )
        alternate = User.objects.create(
            full_name="Alternate Auditor",
            email="alternate.auditor@sfpcl.example",
            primary_role=self.role,
        )
        alternate.set_password(self.password)
        alternate.save(update_fields=["password_hash"])
        payload = {
            "audit_scope": "audit_readonly",
            "observation": "Creator-scoped retained observation.",
            "source_references": [
                {"source_type": "audit_log", "source_id": str(sampled.pk)}
            ],
        }
        for actor in (self.auditor, alternate):
            response = self.client.post(
                self.URL,
                payload,
                content_type="application/json",
                **self._auth_for(actor),
            )
            self.assertEqual(response.status_code, 200, response.content)

        filtered = self.client.get(
            self.URL,
            {
                "created_by_user_id": str(alternate.pk),
                "audit_scope": "audit_readonly",
            },
            **self._auth(),
        )
        unknown = self.client.get(
            self.URL,
            {"status": "open"},
            **self._auth(),
        )

        self.assertEqual(filtered.status_code, 200, filtered.content)
        self.assertEqual(filtered.json()["pagination"]["total_count"], 1)
        self.assertEqual(
            filtered.json()["data"][0]["creator"]["user_id"],
            str(alternate.pk),
        )
        self.assertEqual(unknown.status_code, 400, unknown.content)
        self.assertIn("status", unknown.json()["error"]["field_errors"])

    def test_evidence_download_rechecks_permission_and_signed_capability(self):
        evidence = self._compliance_evidence()
        created = self.client.post(
            self.URL,
            {
                "audit_scope": "audit_readonly",
                "observation": "Evidence authority is rechecked at access time.",
                "source_references": [
                    {
                        "source_type": "compliance_evidence",
                        "source_id": str(evidence.pk),
                    }
                ],
            },
            content_type="application/json",
            **self._auth(),
        ).json()["data"]
        signed_url = created["source_references"][0]["evidence"]["download_url"]
        RolePermission.objects.filter(
            role=self.role,
            permission__permission_code="documents.file.download",
        ).delete()

        detail = self.client.get(
            f"{self.URL}{created['audit_observation_id']}/",
            **self._auth(),
        )
        revoked = self.client.get(signed_url, **self._auth())

        self.assertEqual(detail.status_code, 200, detail.content)
        self.assertIsNone(
            detail.json()["data"]["source_references"][0]["evidence"]["download_url"]
        )
        self.assertEqual(revoked.status_code, 404, revoked.content)
        RolePermission.objects.create(
            role=self.role,
            permission=Permission.objects.get(
                permission_code="documents.file.download"
            ),
        )
        tampered = self.client.get(
            signed_url.split("token=", 1)[0] + "token=tampered",
            **self._auth(),
        )
        cross_observation = self.client.get(
            signed_url.replace(
                created["audit_observation_id"],
                str(uuid.uuid4()),
            ),
            **self._auth(),
        )
        self.assertEqual(tampered.status_code, 404, tampered.content)
        self.assertEqual(cross_observation.status_code, 404, cross_observation.content)
        denials = AuditLog.objects.filter(
            action="audit.observation.access_denied"
        )
        self.assertEqual(denials.count(), 3)
        self.assertTrue(
            all(
                denial.new_value_json["outcome"] == "denied"
                for denial in denials
            )
        )

    def _compliance_evidence(self):
        reviewer_role = Role.objects.create(
            role_code="company_secretary",
            role_name="Company Secretary",
        )
        reviewer = User.objects.create(
            full_name="Evidence Reviewer",
            email="evidence.reviewer@sfpcl.example",
            primary_role=reviewer_role,
        )
        control = ComplianceControl.objects.create(
            control_code="ANNUAL_AUDIT_SAMPLE",
            control_name="Annual audit sample",
            control_area="record_retention",
            legal_basis="Annual retained-record review.",
            control_type=ComplianceControl.TYPE_DETECTIVE,
            frequency=ComplianceControl.FREQUENCY_ANNUAL,
            owner_role_code=self.role.role_code,
            owner_user=self.auditor,
            reviewer_user=reviewer,
            first_due_date=date(2026, 12, 31),
            evidence_required="Restricted retained audit file.",
            risk_if_missed="Audit sample unavailable.",
        )
        task = ComplianceTask.objects.create(
            control=control,
            task_period="2026",
            due_date=date(2026, 12, 31),
            assigned_to_user=self.auditor,
            reviewer_user=reviewer,
            task_status=ComplianceTask.STATUS_COMPLETED,
        )
        storage = LocalDocumentStorage()
        stored = storage.store(
            SimpleUploadedFile(
                "ABCDE1234F-bank-statement.pdf",
                b"restricted audit evidence",
                content_type="application/pdf",
            )
        )
        document = DocumentFile.objects.create(
            file_name="ABCDE1234F-bank-statement.pdf",
            file_extension=".pdf",
            mime_type="application/pdf",
            file_size_bytes=stored.file_size_bytes,
            storage_provider=stored.storage_provider,
            storage_key=stored.storage_key,
            checksum_sha256=stored.checksum_sha256,
            uploaded_by_user=reviewer,
            sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
        )
        return ComplianceEvidence.objects.create(
            task=task,
            evidence_type="annual_audit_report",
            document=document,
            summary="Restricted annual audit evidence.",
            source_owner="documents",
            source_entity_type="document_file",
            source_entity_id=document.pk,
            source_period="2026",
            submitted_by_user=reviewer,
            review_status=ComplianceEvidence.REVIEW_ACCEPTED,
            reviewed_by_user=self.auditor,
        )

    def _auth(self):
        return self._auth_for(self.auditor)

    def _auth_for(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {
            "HTTP_AUTHORIZATION": (
                f"Bearer {response.json()['data']['access_token']}"
            )
        }
