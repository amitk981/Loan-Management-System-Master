import tempfile
from uuid import uuid4
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import Member
from sfpcl_credit.tests.api_contracts import assert_error_envelope, assert_success_envelope
from sfpcl_credit.workflows.models import WorkflowEvent
KYC_PROFILE_READ = "kyc.profile.read"
KYC_PROFILE_CREATE = "kyc.profile.create"
KYC_PROFILE_UPDATE = "kyc.profile.update"
KYC_DOCUMENT_UPLOAD = "kyc.document.upload"
KYC_DOCUMENT_VERIFY = "kyc.document.verify"
@override_settings(DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-kyc-doc-tests-"))
class MemberKycApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        codes = (KYC_PROFILE_READ, KYC_PROFILE_CREATE, KYC_PROFILE_UPDATE, KYC_DOCUMENT_UPLOAD, KYC_DOCUMENT_VERIFY)
        self.permissions = {
            code: Permission.objects.create(permission_code=code, permission_name=code, module_name="kyc", risk_level="high")
            for code in codes
        }
        self.reader = self._user("kyc.reader@sfpcl.example", "ReaderPass123!", KYC_PROFILE_READ)
        self.creator = self._user("kyc.creator@sfpcl.example", "CreatorPass123!", KYC_PROFILE_CREATE, KYC_PROFILE_READ)
        self.updater = self._user("kyc.updater@sfpcl.example", "UpdaterPass123!", KYC_PROFILE_UPDATE, KYC_PROFILE_READ)
        self.uploader = self._user("kyc.uploader@sfpcl.example", "UploaderPass123!", KYC_DOCUMENT_UPLOAD, KYC_PROFILE_READ)
        self.verifier = self._user("kyc.verifier@sfpcl.example", "VerifierPass123!", KYC_DOCUMENT_VERIFY, KYC_PROFILE_READ)
        self.plain = self._user("kyc.plain@sfpcl.example", "PlainPass123!")
        self.member = Member.objects.create(
            member_number="MEM-004H", member_type="individual_farmer", legal_name="Ramesh Patil",
            display_name="Ramesh Patil", folio_number="FOL-004H", membership_status="active",
            pan_encrypted="enc:v1:10:member-pan:234F", pan_hash="member-pan-hash",
            aadhaar_encrypted="enc:v1:12:member-aadhaar:9012", aadhaar_hash="member-aadhaar-hash",
            kyc_status="pending", default_status="no_default",
        )
    def test_kyc_profile_can_be_created_read_and_updated_for_member_party(self):
        create_response = self.client.post(
            "/api/v1/kyc-profiles/",
            data=self._profile_payload(),
            content_type="application/json",
            headers={
                **self._headers("kyc.creator@sfpcl.example", "CreatorPass123!"),
                "X-Request-ID": "req-create-kyc-profile",
            },
        )
        self.assertEqual(create_response.status_code, 200)
        create_body = create_response.json()
        assert_success_envelope(self, create_body)
        self.assertEqual(create_body["meta"]["request_id"], "req-create-kyc-profile")
        profile = create_body["data"]
        self.assertEqual(
            {key: profile[key] for key in ("party_type", "party_id", "kyc_status", "risk_rating")},
            {
                "party_type": "member",
                "party_id": str(self.member.member_id),
                "kyc_status": "pending",
                "risk_rating": "low",
            },
        )
        self.assertNotIn("ckyc_identifier_encrypted", profile)
        list_response = self.client.get(
            self._profile_list_url(),
            headers=self._headers("kyc.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertEqual(list_response.status_code, 200)
        list_body = list_response.json()
        assert_success_envelope(self, list_body)
        self.assertEqual(list_body["data"]["kyc_profile_id"], profile["kyc_profile_id"])
        patch_response = self.client.patch(
            f"/api/v1/kyc-profiles/{profile['kyc_profile_id']}/",
            data={"risk_rating": "medium", "beneficial_ownership_verified_flag": True},
            content_type="application/json",
            headers=self._headers("kyc.updater@sfpcl.example", "UpdaterPass123!"),
        )
        self.assertEqual(patch_response.status_code, 200)
        patch_body = patch_response.json()
        self.assertEqual(patch_body["data"]["risk_rating"], "medium")
    def test_kyc_profile_requires_auth_permission_member_party_and_existing_member(self):
        unauthenticated = self.client.get(self._profile_list_url())
        self.assertEqual(unauthenticated.status_code, 401)
        assert_error_envelope(self, unauthenticated.json(), "AUTH_REQUIRED")
        denied = self.client.get(
            self._profile_list_url(),
            headers=self._headers("kyc.plain@sfpcl.example", "PlainPass123!"),
        )
        self.assertEqual(denied.status_code, 403)
        assert_error_envelope(self, denied.json(), "PERMISSION_DENIED")
        unsupported_party = self.client.post(
            "/api/v1/kyc-profiles/",
            data={**self._profile_payload(), "party_type": "nominee"},
            content_type="application/json",
            headers=self._headers("kyc.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(unsupported_party.status_code, 400)
        assert_error_envelope(self, unsupported_party.json(), "VALIDATION_ERROR")
        self.assertIn("party_type", unsupported_party.json()["error"]["field_errors"])
        missing_member = self.client.post(
            "/api/v1/kyc-profiles/",
            data={**self._profile_payload(), "party_id": str(uuid4())},
            content_type="application/json",
            headers=self._headers("kyc.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(missing_member.status_code, 404)
        assert_error_envelope(self, missing_member.json(), "NOT_FOUND")
        missing_consent = self.client.post(
            "/api/v1/kyc-profiles/",
            data={**self._profile_payload(), "ckyc_consent_flag": None},
            content_type="application/json",
            headers=self._headers("kyc.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(missing_consent.status_code, 400)
        assert_error_envelope(self, missing_consent.json(), "VALIDATION_ERROR")
        self.assertIn("ckyc_consent_flag", missing_consent.json()["error"]["field_errors"])
    def test_kyc_document_can_be_uploaded_and_verified_with_metadata_only_audit(self):
        profile_id = self._create_profile_id()
        upload_response = self.client.post(
            f"/api/v1/kyc-profiles/{profile_id}/documents/",
            data={
                "document_type": "pan",
                "self_attested_flag": "true",
                "file": SimpleUploadedFile(
                    "borrower-pan.pdf",
                    b"pan document bytes",
                    content_type="application/pdf",
                ),
            },
            headers={
                **self._headers("kyc.uploader@sfpcl.example", "UploaderPass123!"),
                "X-Request-ID": "req-upload-kyc-doc",
            },
        )
        self.assertEqual(upload_response.status_code, 200)
        upload_body = upload_response.json()
        assert_success_envelope(self, upload_body)
        self.assertEqual(upload_body["meta"]["request_id"], "req-upload-kyc-doc")
        document = upload_body["data"]
        self.assertEqual(
            {key: document[key] for key in ("document_type", "self_attested_flag", "verification_status")},
            {"document_type": "pan", "self_attested_flag": True, "verification_status": "pending"},
        )
        self.assertEqual(DocumentFile.objects.get().sensitivity_level, "restricted")
        verify_response = self.client.post(
            f"/api/v1/kyc-documents/{document['kyc_document_id']}/verify/",
            data={
                "verification_status": "verified",
                "remarks": "Document verified against original.",
            },
            content_type="application/json",
            headers=self._headers("kyc.verifier@sfpcl.example", "VerifierPass123!"),
        )
        self.assertEqual(verify_response.status_code, 200)
        verified = verify_response.json()["data"]
        self.assertEqual(
            {key: verified[key] for key in ("verification_status", "remarks", "verified_by_user_id")},
            {
                "verification_status": "verified",
                "remarks": "Document verified against original.",
                "verified_by_user_id": str(self.verifier.user_id),
            },
        )
        actions = set(AuditLog.objects.values_list("action", flat=True))
        self.assertIn("kyc.profile.created", actions)
        self.assertIn("kyc.document.uploaded", actions)
        self.assertIn("kyc.document.verified", actions)
        for audit in AuditLog.objects.filter(action__startswith="kyc."):
            flattened = str(audit.new_value_json)
            self.assertNotIn("ABCDE1234F", flattened)
            self.assertNotIn("123412341234", flattened)
            self.assertNotIn("pan_hash", flattened)
            self.assertNotIn("aadhaar_hash", flattened)
            self.assertNotIn("ckyc_identifier_encrypted", flattened)
        self.assertEqual(WorkflowEvent.objects.count(), 0)
    def test_kyc_document_upload_validates_permission_type_file_and_self_attestation(self):
        profile_id = self._create_profile_id()
        no_permission = self.client.post(
            f"/api/v1/kyc-profiles/{profile_id}/documents/",
            data={
                "document_type": "pan",
                "self_attested_flag": "true",
                "file": SimpleUploadedFile("borrower-pan.pdf", b"bytes"),
            },
            headers=self._headers("kyc.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertEqual(no_permission.status_code, 403)
        assert_error_envelope(self, no_permission.json(), "PERMISSION_DENIED")
        cases = [
            ({"document_type": "driving_license", "self_attested_flag": "true"}, "document_type"),
            ({"document_type": "pan", "self_attested_flag": "false"}, "self_attested_flag"),
            ({"document_type": "aadhaar"}, "self_attested_flag"),
        ]
        for override, field in cases:
            with self.subTest(override=override):
                response = self.client.post(
                    f"/api/v1/kyc-profiles/{profile_id}/documents/",
                    data={
                        **override,
                        "file": SimpleUploadedFile("kyc.pdf", b"bytes"),
                    },
                    headers=self._headers("kyc.uploader@sfpcl.example", "UploaderPass123!"),
                )
                self.assertEqual(response.status_code, 400)
                assert_error_envelope(self, response.json(), "VALIDATION_ERROR")
                self.assertIn(field, response.json()["error"]["field_errors"])
    def test_kyc_document_verification_supports_rejection_and_requires_verify_permission(self):
        profile_id = self._create_profile_id()
        document_id = self._upload_document_id(profile_id, "photo", "false")
        no_permission = self.client.post(
            f"/api/v1/kyc-documents/{document_id}/verify/",
            data={"verification_status": "verified"},
            content_type="application/json",
            headers=self._headers("kyc.reader@sfpcl.example", "ReaderPass123!"),
        )
        self.assertEqual(no_permission.status_code, 403)
        assert_error_envelope(self, no_permission.json(), "PERMISSION_DENIED")
        rejected = self.client.post(
            f"/api/v1/kyc-documents/{document_id}/verify/",
            data={"verification_status": "rejected", "remarks": "Image is unreadable."},
            content_type="application/json",
            headers=self._headers("kyc.verifier@sfpcl.example", "VerifierPass123!"),
        )
        self.assertEqual(rejected.status_code, 200)
        body = rejected.json()["data"]
        self.assertEqual(body["verification_status"], "rejected")
        self.assertEqual(body["remarks"], "Image is unreadable.")
        invalid = self.client.post(
            f"/api/v1/kyc-documents/{document_id}/verify/",
            data={"verification_status": "approved"},
            content_type="application/json",
            headers=self._headers("kyc.verifier@sfpcl.example", "VerifierPass123!"),
        )
        self.assertEqual(invalid.status_code, 400)
        assert_error_envelope(self, invalid.json(), "VALIDATION_ERROR")
        self.assertIn("verification_status", invalid.json()["error"]["field_errors"])
    def _profile_payload(self, **overrides):
        payload = {
            "party_type": "member",
            "party_id": str(self.member.member_id),
            "ckyc_consent_flag": True,
            "beneficial_ownership_verified_flag": False,
            "risk_rating": "low",
        }
        payload.update(overrides)
        return payload
    def _create_profile_id(self):
        response = self.client.post(
            "/api/v1/kyc-profiles/",
            data=self._profile_payload(),
            content_type="application/json",
            headers=self._headers("kyc.creator@sfpcl.example", "CreatorPass123!"),
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["kyc_profile_id"]
    def _upload_document_id(self, profile_id, document_type, self_attested_flag):
        response = self.client.post(
            f"/api/v1/kyc-profiles/{profile_id}/documents/",
            data={
                "document_type": document_type,
                "self_attested_flag": self_attested_flag,
                "file": SimpleUploadedFile("kyc.pdf", b"bytes"),
            },
            headers=self._headers("kyc.uploader@sfpcl.example", "UploaderPass123!"),
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["kyc_document_id"]
    def _profile_list_url(self, member_id=None):
        return (
            "/api/v1/kyc-profiles/"
            f"?party_type=member&party_id={member_id or self.member.member_id}"
        )
    def _user(self, email, password, *permission_codes):
        role = Role.objects.create(
            role_code=email.split("@")[0].replace(".", "_"),
            role_name=email,
            is_system_role=True,
            status="active",
        )
        for code in permission_codes:
            RolePermission.objects.create(role=role, permission=self.permissions[code])
        user = User.objects.create(full_name=email, email=email, status="active", primary_role=role)
        user.set_password(password)
        user.save()
        return user
    def _token(self, email, password):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": email, "password": password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["data"]["access_token"]
    def _headers(self, email, password):
        return {"Authorization": f"Bearer {self._token(email, password)}"}
