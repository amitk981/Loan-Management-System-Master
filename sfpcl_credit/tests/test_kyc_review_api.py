from datetime import datetime, timedelta, timezone as dt_timezone

from django.test import Client, TestCase
from django.utils import timezone

from sfpcl_credit.compliance.models import ComplianceControl
from sfpcl_credit.identity.models import Permission, Role, RolePermission, User
from sfpcl_credit.members.models import KycProfile, Member, MemberScopeAssignment


class KycReviewApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner_role = Role.objects.create(
            role_code="credit_manager", role_name="Credit Manager"
        )
        self.reviewer_role = Role.objects.create(
            role_code="compliance_team_member", role_name="Compliance Team Member"
        )
        self.owner = self._user(self.owner_role, "kyc-api-owner@example.test")
        self.reviewer = self._user(self.reviewer_role, "kyc-api-reviewer@example.test")
        self.permission = Permission.objects.create(
            permission_code="compliance.kyc_review.manage",
            permission_name="Manage KYC reviews",
            module_name="compliance",
            risk_level="high",
        )
        RolePermission.objects.create(role=self.owner_role, permission=self.permission)
        ComplianceControl.objects.create(
            control_code="KYC_AML",
            control_name="KYC and AML review",
            control_area="kyc",
            legal_basis="Two-year governed KYC review.",
            control_type=ComplianceControl.TYPE_DETECTIVE,
            frequency=ComplianceControl.FREQUENCY_ONGOING,
            owner_role_code=self.owner_role.role_code,
            owner_user=self.owner,
            reviewer_user=self.reviewer,
            first_due_date=timezone.localdate(),
            evidence_required="Governed KYC verification.",
            risk_if_missed="KYC becomes stale.",
        )
        self.auth = self._auth(self.owner)

    def test_list_filters_due_member_and_assignment_with_safe_summaries(self):
        from sfpcl_credit.compliance.modules.kyc_review_tracker import KYCReviewTracker

        due_date = timezone.localdate() + timedelta(days=10)
        source_date = due_date.replace(year=due_date.year - 2)
        assigned = self._profile("Assigned Member", "individual_farmer", source_date)
        self._profile("Foreign FPC", "fpc", source_date)
        MemberScopeAssignment.objects.create(
            user=self.owner,
            permission_code="compliance.kyc_review.manage",
            scope_type="assigned",
            member=assigned,
        )
        KYCReviewTracker.generate_due_reviews(as_of_date=timezone.localdate())

        response = self.client.get(
            "/api/v1/kyc-reviews/",
            {
                "due_within_days": "30",
                "member_type": "individual_farmer",
                "member_status": "active",
                "assigned_to_me": "true",
            },
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 1)
        item = response.json()["data"][0]
        self.assertEqual(item["member_id"], str(assigned.pk))
        self.assertEqual(item["member_type"], "individual_farmer")
        self.assertEqual(item["member_status"], "active")
        self.assertEqual(item["due_date"], due_date.isoformat())
        self.assertNotIn("completion_evidence", item)
        self.assertNotIn("document_id", str(item))

    def test_assigned_owner_can_assign_review_to_another_scoped_kyc_owner(self):
        import json

        from sfpcl_credit.compliance.models import KYCReview
        from sfpcl_credit.compliance.modules.kyc_review_tracker import KYCReviewTracker
        from sfpcl_credit.identity.models import AuditLog

        due_date = timezone.localdate()
        source_date = due_date.replace(year=due_date.year - 2)
        member = self._profile("Assignment Member", "individual_farmer", source_date)
        MemberScopeAssignment.objects.create(
            user=self.owner,
            permission_code="compliance.kyc_review.manage",
            scope_type="assigned",
            member=member,
        )
        replacement_role = Role.objects.create(
            role_code="kyc_officer", role_name="KYC Officer"
        )
        replacement = self._user(replacement_role, "replacement-kyc@example.test")
        RolePermission.objects.create(role=replacement_role, permission=self.permission)
        MemberScopeAssignment.objects.create(
            user=replacement,
            permission_code="compliance.kyc_review.manage",
            scope_type="assigned",
            member=member,
        )
        KYCReviewTracker.generate_due_reviews(as_of_date=due_date)
        review = KYCReview.objects.get(member=member)

        response = self.client.patch(
            f"/api/v1/kyc-reviews/{review.pk}/",
            data=json.dumps({"assigned_to_user_id": str(replacement.pk)}),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        review.task.refresh_from_db()
        self.assertEqual(review.task.assigned_to_user, replacement)
        self.assertEqual(response.json()["data"]["assigned_to_user_id"], str(replacement.pk))
        self.assertTrue(
            AuditLog.objects.filter(
                action="compliance.kyc_review.assigned", entity_id=review.pk
            ).exists()
        )

    def test_due_request_queues_one_honest_communication_on_exact_replay(self):
        import json

        from sfpcl_credit.communications.models import (
            Communication,
            CommunicationDeliveryJob,
            ContentTemplate,
        )
        from sfpcl_credit.compliance.models import KYCReview
        from sfpcl_credit.compliance.modules.kyc_review_tracker import KYCReviewTracker

        today = timezone.localdate()
        source_date = today.replace(year=today.year - 2)
        member = self._profile("Reminder Member", "individual_farmer", source_date)
        member.email = "reminder-member@example.test"
        member.save(update_fields=["email"])
        MemberScopeAssignment.objects.create(
            user=self.owner,
            permission_code="compliance.kyc_review.manage",
            scope_type="assigned",
            member=member,
        )
        ContentTemplate.objects.create(
            template_code="kyc_rekyc_request_email",
            template_name="Re-KYC request",
            template_type="email",
            language_code="en",
            audience="borrower",
            subject_template="Re-KYC review due {{due_date}}",
            body_template="Dear {{member_name}}, your re-KYC review is {{status}}.",
            variables_json=["due_date", "member_name", "status"],
            approval_status=ContentTemplate.STATUS_APPROVED,
            template_version="1.0",
            effective_from=today,
        )
        KYCReviewTracker.generate_due_reviews(as_of_date=today)
        review = KYCReview.objects.get(member=member)
        headers = {**self.auth, "HTTP_IDEMPOTENCY_KEY": "rekyc-reminder-001"}

        first = self.client.post(
            f"/api/v1/kyc-reviews/{review.pk}/remind/",
            data=json.dumps({}),
            content_type="application/json",
            **headers,
        )
        replay = self.client.post(
            f"/api/v1/kyc-reviews/{review.pk}/remind/",
            data=json.dumps({}),
            content_type="application/json",
            **headers,
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(first.json()["data"]["delivery_status"], "queued")
        self.assertEqual(replay.json()["data"]["communication_id"], first.json()["data"]["communication_id"])
        self.assertEqual(
            Communication.objects.filter(
                related_entity_type="kyc_review", related_entity_id=review.pk
            ).count(),
            1,
        )
        self.assertEqual(CommunicationDeliveryJob.objects.count(), 1)

    def test_completion_rejects_caller_state_and_requires_new_governed_verification(self):
        import json

        from sfpcl_credit.compliance.models import KYCReview
        from sfpcl_credit.compliance.modules.kyc_review_tracker import KYCReviewTracker
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.members.models import KycDocument

        today = timezone.localdate()
        source_date = today.replace(year=today.year - 2)
        member = self._profile("API Completion Member", "individual_farmer", source_date)
        MemberScopeAssignment.objects.create(
            user=self.owner,
            permission_code="compliance.kyc_review.manage",
            scope_type="assigned",
            member=member,
        )
        KYCReviewTracker.generate_due_reviews(as_of_date=today)
        review = KYCReview.objects.get(member=member)
        url = f"/api/v1/kyc-reviews/{review.pk}/complete/"

        forged = self.client.post(
            url,
            data=json.dumps({"status": "completed"}),
            content_type="application/json",
            **self.auth,
        )
        stale = self.client.post(
            url, data=json.dumps({}), content_type="application/json", **self.auth
        )

        self.assertEqual(forged.status_code, 400, forged.content)
        self.assertEqual(stale.status_code, 409, stale.content)
        profile = KycProfile.objects.get(party_id=member.pk)
        new_verified_at = timezone.now() + timedelta(seconds=1)
        document = DocumentFile.objects.create(
            file_name="api-updated-pan.pdf",
            storage_provider="local",
            storage_key=f"governed/kyc/{member.pk}/api-updated-pan.pdf",
            uploaded_by_user=self.owner,
            sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
        )
        KycDocument.objects.create(
            kyc_profile=profile,
            document_type="pan",
            document_file=document,
            self_attested_flag=True,
            verification_status="verified",
            verified_by_user=self.owner,
            verified_at=new_verified_at,
        )
        profile.last_verified_at = new_verified_at
        profile.last_verified_by_user = self.owner
        profile.rekyc_due_date = new_verified_at.date().replace(
            year=new_verified_at.date().year + 2
        )
        profile.save()

        incomplete = self.client.post(
            url, data=json.dumps({}), content_type="application/json", **self.auth
        )

        self.assertEqual(incomplete.status_code, 409, incomplete.content)
        profile.ckyc_consent_flag = True
        profile.save()
        for document_type in ("aadhaar", "photo"):
            supporting_file = DocumentFile.objects.create(
                file_name=f"api-updated-{document_type}.pdf",
                storage_provider="local",
                storage_key=f"governed/kyc/{member.pk}/api-updated-{document_type}.pdf",
                uploaded_by_user=self.owner,
                sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
            )
            KycDocument.objects.create(
                kyc_profile=profile,
                document_type=document_type,
                document_file=supporting_file,
                self_attested_flag=document_type == "aadhaar",
                verification_status="verified",
                verified_by_user=self.owner,
                verified_at=new_verified_at,
            )

        completed = self.client.post(
            url, data=json.dumps({}), content_type="application/json", **self.auth
        )

        self.assertEqual(completed.status_code, 200, completed.content)
        self.assertEqual(completed.json()["data"]["status"], "completed")

    def test_governed_auditor_reads_safe_summary_but_cannot_mutate(self):
        import json

        from sfpcl_credit.compliance.models import KYCReview
        from sfpcl_credit.compliance.modules.kyc_review_tracker import KYCReviewTracker

        today = timezone.localdate()
        source_date = today.replace(year=today.year - 2)
        member = self._profile("Audit Member", "individual_farmer", source_date)
        KYCReviewTracker.generate_due_reviews(as_of_date=today)
        review = KYCReview.objects.get(member=member)
        auditor_role = Role.objects.create(
            role_code="internal_auditor", role_name="Internal Auditor"
        )
        auditor = self._user(auditor_role, "kyc-auditor@example.test")
        read_permission = Permission.objects.create(
            permission_code="compliance.task.read",
            permission_name="Read compliance tasks",
            module_name="compliance",
            risk_level="medium",
        )
        RolePermission.objects.create(role=auditor_role, permission=read_permission)
        auditor_auth = self._auth(auditor)

        listed = self.client.get("/api/v1/kyc-reviews/", **auditor_auth)
        detail = self.client.get(f"/api/v1/kyc-reviews/{review.pk}/", **auditor_auth)
        mutation = self.client.patch(
            f"/api/v1/kyc-reviews/{review.pk}/",
            data=json.dumps({"assigned_to_user_id": str(auditor.pk)}),
            content_type="application/json",
            **auditor_auth,
        )

        self.assertEqual(listed.status_code, 200, listed.content)
        self.assertEqual(listed.json()["pagination"]["total_count"], 1)
        self.assertEqual(listed.json()["data"][0]["available_actions"], [])
        self.assertEqual(detail.status_code, 200, detail.content)
        self.assertEqual(mutation.status_code, 403, mutation.content)

    def _profile(self, name, member_type, source_date):
        slug = name.lower().replace(" ", "-")
        member = Member.objects.create(
            member_type=member_type,
            legal_name=name,
            display_name=name,
            folio_number=f"FOLIO-{slug}",
            membership_status="active",
            pan_encrypted="encrypted-pan",
            pan_hash=f"pan-hash-{slug}",
            kyc_status="verified",
            default_status="no_default",
        )
        verified_at = datetime.combine(
            source_date, datetime.min.time(), tzinfo=dt_timezone.utc
        )
        KycProfile.objects.create(
            party_type="member",
            party_id=member.pk,
            kyc_status="verified",
            ckyc_consent_flag=True,
            beneficial_ownership_verified_flag=(member_type == "fpc"),
            risk_rating="low",
            last_verified_at=verified_at,
            last_verified_by_user=self.owner,
            rekyc_due_date=source_date.replace(year=source_date.year + 2),
        )
        return member

    @staticmethod
    def _user(role, email):
        user = User.objects.create(
            full_name=role.role_name,
            email=email,
            primary_role=role,
        )
        user.set_password("CompliancePass123!")
        user.save(update_fields=["password_hash"])
        return user

    def _auth(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "CompliancePass123!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {"HTTP_AUTHORIZATION": f"Bearer {response.json()['data']['access_token']}"}
