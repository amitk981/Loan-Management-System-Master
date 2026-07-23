import json
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from sfpcl_credit.identity.models import (
    AuditLog,
    Permission,
    PortalAccount,
    Role,
    RolePermission,
    User,
)
from sfpcl_credit.members.models import (
    KycCorrectionRequest,
    KycProfile,
    Member,
    MemberChangeHistory,
    MemberIdentityChangeRequest,
    MemberScopeAssignment,
)
from sfpcl_credit.workflows.models import WorkflowEvent


class PortalKycCorrectionApiTests(TestCase):
    password = "PortalKycCorrection123!"

    def setUp(self):
        self.storage_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.storage_directory.cleanup)
        storage_override = override_settings(DOCUMENT_STORAGE_ROOT=self.storage_directory.name)
        storage_override.enable()
        self.addCleanup(storage_override.disable)
        role = Role.objects.create(
            role_code="borrower_portal_user",
            role_name="Borrower Portal User",
            is_system_role=True,
            status="active",
        )
        self.user = User.objects.create(
            full_name="Synthetic Portal Member",
            email="portal-kyc-correction@example.test",
            status="active",
            primary_role=role,
        )
        self.user.set_password(self.password)
        self.user.save(update_fields=["password_hash"])
        self.member = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Synthetic Portal Member",
            display_name="Synthetic Portal Member",
            folio_number="SYN-KYC-001",
            membership_status="active",
            pan_encrypted="protected:pan:1234",
            pan_hash="synthetic-pan-hash",
            aadhaar_encrypted="protected:aadhaar:5678",
            aadhaar_hash="synthetic-aadhaar-hash",
            aadhaar_last4="5678",
            kyc_status="verified",
            default_status="no_default",
            created_by_user=self.user,
        )
        self.profile = KycProfile.objects.create(
            party_type="member",
            party_id=self.member.pk,
            kyc_status="verified",
            ckyc_consent_flag=True,
            last_verified_at=timezone.now(),
            last_verified_by_user=self.user,
        )
        self.portal_account = PortalAccount.objects.create(
            member=self.member,
            user=self.user,
            status=PortalAccount.STATUS_ACTIVE,
            activated_at=timezone.now(),
        )
        self.client = Client()

    def test_member_submits_owned_evidence_without_mutating_verified_kyc(self):
        evidence = self.client.post(
            "/api/v1/portal/kyc-corrections/evidence/",
            data={
                "file": SimpleUploadedFile(
                    "corrected-pan.pdf", b"%PDF-1.4 synthetic corrected PAN", "application/pdf"
                ),
                "document_type": "pan",
                "self_attested_flag": "true",
            },
            **self._auth(),
        )
        self.assertEqual(evidence.status_code, 200, evidence.content)

        response = self.client.post(
            "/api/v1/portal/kyc-corrections/",
            data=json.dumps(
                {
                    "changes": {"pan": "ABCDE1234F"},
                    "reason": "My verified PAN record is stale.",
                    "evidence_document_ids": [evidence.json()["data"]["document_id"]],
                }
            ),
            content_type="application/json",
            **self._auth(),
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["status"], "submitted")
        self.assertEqual(data["changes"], {"pan": "******234F"})
        self.assertEqual(data["evidence"][0]["file_name"], "corrected-pan.pdf")
        self.assertNotIn("reviewer", json.dumps(data).lower())
        self.member.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.member.kyc_status, "verified")
        self.assertEqual(self.profile.kyc_status, "verified")
        correction = KycCorrectionRequest.objects.get(pk=data["kyc_correction_request_id"])
        self.assertEqual(correction.member, self.member)
        self.assertEqual(correction.portal_account, self.portal_account)
        self.assertTrue(
            AuditLog.objects.filter(
                action="portal.kyc_correction.submitted", entity_id=correction.pk
            ).exists()
        )
        self.assertTrue(
            WorkflowEvent.objects.filter(
                workflow_name="portal_kyc_correction",
                entity_id=correction.pk,
                to_state="submitted",
            ).exists()
        )

    def test_cross_member_submit_is_blocked_and_audited_without_writes(self):
        other = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Other Synthetic Member",
            display_name="Other Synthetic Member",
            folio_number="SYN-KYC-OTHER",
            membership_status="active",
            pan_encrypted="protected:pan:9999",
            pan_hash="other-synthetic-pan-hash",
            kyc_status="verified",
            default_status="no_default",
        )

        response = self.client.post(
            "/api/v1/portal/kyc-corrections/",
            data=json.dumps(
                {
                    "member_id": str(other.pk),
                    "changes": {"pan": "ABCDE1234F"},
                    "reason": "Attempted cross-member correction.",
                    "evidence_document_ids": ["10000000-0000-0000-0000-000000000001"],
                }
            ),
            content_type="application/json",
            **self._auth(),
        )

        self.assertEqual(response.status_code, 403, response.content)
        self.assertEqual(response.json()["error"]["code"], "OBJECT_ACCESS_DENIED")
        self.assertEqual(KycCorrectionRequest.objects.count(), 0)
        self.assertEqual(MemberIdentityChangeRequest.objects.count(), 0)
        denied = AuditLog.objects.get(action="portal.kyc_correction.access_denied")
        self.assertEqual(denied.entity_id, other.pk)
        self.assertEqual(denied.new_value_json["authenticated_member_id"], str(self.member.pk))
        self.assertNotIn("ABCDE1234F", json.dumps(denied.new_value_json))
        cross_read = self.client.get(
            "/api/v1/portal/kyc-corrections/",
            {"member_id": str(other.pk)},
            **self._auth(),
        )
        self.assertEqual(cross_read.status_code, 403, cross_read.content)
        self.assertEqual(
            AuditLog.objects.filter(action="portal.kyc_correction.access_denied").count(), 2
        )

    def test_staff_approval_applies_locked_identity_through_governed_reverification(self):
        correction_id = self._submit_pan_correction()
        reviewer = self._staff_user(
            "kyc-correction-reviewer@example.test",
            "members.member.update",
            "members.member.identity_change.approve",
            "kyc.document.verify",
        )

        review = self.client.post(
            f"/api/v1/kyc-correction-requests/{correction_id}/review/",
            data=json.dumps({"internal_notes": "Evidence is readable."}),
            content_type="application/json",
            **self._staff_auth(reviewer),
        )
        self.assertEqual(review.status_code, 200, review.content)
        self.assertEqual(review.json()["data"]["status"], "under_review")
        blocked = self.client.post(
            f"/api/v1/kyc-correction-requests/{correction_id}/approve/",
            data=json.dumps({}),
            content_type="application/json",
            **self._staff_auth(reviewer),
        )
        self.assertEqual(blocked.status_code, 409, blocked.content)
        kyc_document_id = review.json()["data"]["kyc_documents"][0]["kyc_document_id"]
        verified = self.client.post(
            f"/api/v1/kyc-documents/{kyc_document_id}/verify/",
            data=json.dumps(
                {
                    "verification_status": "verified",
                    "remarks": "Correction evidence verified against the submitted copy.",
                }
            ),
            content_type="application/json",
            **self._staff_auth(reviewer),
        )
        self.assertEqual(verified.status_code, 200, verified.content)

        approval = self.client.post(
            f"/api/v1/kyc-correction-requests/{correction_id}/approve/",
            data=json.dumps({}),
            content_type="application/json",
            **self._staff_auth(reviewer),
        )

        self.assertEqual(approval.status_code, 200, approval.content)
        self.assertEqual(approval.json()["data"]["status"], "approved")
        self.member.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.member.kyc_status, "pending")
        self.assertEqual(self.profile.kyc_status, "pending")
        self.assertEqual(self.member.version, 3)
        self.assertEqual(self.member.email, "corrected.portal@example.test")
        history = MemberChangeHistory.objects.get(
            member=self.member, change_type="identity_change_approved"
        )
        self.assertEqual(history.changed_fields, ["pan"])
        self.assertEqual(history.new_value_json["pan"], "******234F")
        self.assertNotIn("ABCDE1234F", json.dumps(history.new_value_json))
        contact_history = MemberChangeHistory.objects.get(
            member=self.member, change_type="update"
        )
        self.assertEqual(contact_history.changed_fields, ["email"])
        portal = self.client.get("/api/v1/portal/kyc-corrections/", **self._auth())
        self.assertEqual(portal.status_code, 200, portal.content)
        borrower_item = portal.json()["data"]["items"][0]
        self.assertEqual(borrower_item["status"], "approved")
        self.assertIsNotNone(borrower_item["decided_at"])
        self.assertNotIn("internal_notes", borrower_item)
        self.assertTrue(
            AuditLog.objects.filter(
                action="members.kyc_correction.approved",
                entity_id=correction_id,
            ).exists()
        )

    def test_staff_rejection_requires_borrower_reason_and_hides_internal_notes(self):
        correction_id = self._submit_pan_correction()
        reviewer = self._staff_user(
            "kyc-correction-rejecter@example.test", "members.member.update"
        )
        review = self.client.post(
            f"/api/v1/kyc-correction-requests/{correction_id}/review/",
            data=json.dumps({"internal_notes": "The scan does not match the request."}),
            content_type="application/json",
            **self._staff_auth(reviewer),
        )
        self.assertEqual(review.status_code, 200, review.content)

        missing_reason = self.client.post(
            f"/api/v1/kyc-correction-requests/{correction_id}/reject/",
            data=json.dumps({"rejection_reason": ""}),
            content_type="application/json",
            **self._staff_auth(reviewer),
        )
        self.assertEqual(missing_reason.status_code, 400, missing_reason.content)
        rejection = self.client.post(
            f"/api/v1/kyc-correction-requests/{correction_id}/reject/",
            data=json.dumps(
                {"rejection_reason": "Please upload a clearer self-attested PAN copy."}
            ),
            content_type="application/json",
            **self._staff_auth(reviewer),
        )

        self.assertEqual(rejection.status_code, 200, rejection.content)
        self.member.refresh_from_db()
        self.assertEqual(self.member.kyc_status, "verified")
        self.assertEqual(self.member.version, 1)
        self.assertEqual(MemberChangeHistory.objects.count(), 0)
        identity_change = MemberIdentityChangeRequest.objects.get(
            portal_kyc_correction__pk=correction_id
        )
        self.assertEqual(identity_change.status, "rejected")
        portal = self.client.get("/api/v1/portal/kyc-corrections/", **self._auth())
        borrower_item = portal.json()["data"]["items"][0]
        self.assertEqual(borrower_item["status"], "rejected")
        self.assertEqual(
            borrower_item["rejection_reason"],
            "Please upload a clearer self-attested PAN copy.",
        )
        self.assertNotIn("internal_notes", borrower_item)
        self.assertNotIn("scan does not match", json.dumps(borrower_item).lower())

    def test_staff_queue_enforces_permission_and_member_scope(self):
        correction_id = self._submit_pan_correction()
        scoped = self._staff_user(
            "kyc-correction-queue@example.test", "members.member.update"
        )
        unscoped = self._staff_user(
            "kyc-correction-unscoped@example.test", "members.member.update"
        )
        MemberScopeAssignment.objects.filter(user=unscoped).delete()
        plain = self._staff_user("kyc-correction-plain@example.test")

        allowed = self.client.get(
            "/api/v1/kyc-correction-requests/", **self._staff_auth(scoped)
        )
        hidden = self.client.get(
            "/api/v1/kyc-correction-requests/", **self._staff_auth(unscoped)
        )
        forbidden = self.client.get(
            "/api/v1/kyc-correction-requests/", **self._staff_auth(plain)
        )

        self.assertEqual(allowed.status_code, 200, allowed.content)
        self.assertEqual(allowed.json()["data"]["items"][0]["kyc_correction_request_id"], correction_id)
        self.assertEqual(hidden.status_code, 200, hidden.content)
        self.assertEqual(hidden.json()["data"]["items"], [])
        self.assertEqual(forbidden.status_code, 403, forbidden.content)

    def _auth(self):
        login = self.client.post(
            "/api/v1/portal/auth/login/",
            data={"identifier": self.user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(login.status_code, 200, login.content)
        return {"HTTP_AUTHORIZATION": f"Bearer {login.json()['data']['access_token']}"}

    def _submit_pan_correction(self):
        evidence = self.client.post(
            "/api/v1/portal/kyc-corrections/evidence/",
            data={
                "file": SimpleUploadedFile(
                    "corrected-pan.pdf", b"%PDF-1.4 synthetic corrected PAN", "application/pdf"
                ),
                "document_type": "pan",
                "self_attested_flag": "true",
            },
            **self._auth(),
        )
        self.assertEqual(evidence.status_code, 200, evidence.content)
        response = self.client.post(
            "/api/v1/portal/kyc-corrections/",
            data=json.dumps(
                {
                    "changes": {
                        "pan": "ABCDE1234F",
                        "email": "corrected.portal@example.test",
                    },
                    "reason": "My verified PAN record is stale.",
                    "evidence_document_ids": [evidence.json()["data"]["document_id"]],
                }
            ),
            content_type="application/json",
            **self._auth(),
        )
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()["data"]["kyc_correction_request_id"]

    def _staff_user(self, email, *permission_codes):
        role = Role.objects.create(
            role_code=email.split("@")[0],
            role_name=email,
            is_system_role=True,
            status="active",
        )
        for code in permission_codes:
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "members",
                    "risk_level": "high",
                },
            )
            RolePermission.objects.create(role=role, permission=permission)
        user = User.objects.create(
            full_name=email,
            email=email,
            status="active",
            primary_role=role,
        )
        user.set_password(self.password)
        user.save(update_fields=["password_hash"])
        for code in permission_codes:
            MemberScopeAssignment.objects.create(
                user=user,
                permission_code=code,
                scope_type="assigned",
                member=self.member,
            )
        return user

    def _staff_auth(self, user):
        login = self.client.post(
            "/api/v1/auth/login/",
            data={"email": user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(login.status_code, 200, login.content)
        return {"HTTP_AUTHORIZATION": f"Bearer {login.json()['data']['access_token']}"}
