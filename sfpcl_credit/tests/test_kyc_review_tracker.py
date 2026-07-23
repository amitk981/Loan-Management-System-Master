from datetime import date, datetime, timezone as dt_timezone

from django.test import TestCase

from sfpcl_credit.compliance.models import ComplianceControl
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import Permission, Role, RolePermission, User
from sfpcl_credit.members.models import (
    KycDocument,
    KycProfile,
    Member,
    MemberScopeAssignment,
)


class KycReviewTrackerTests(TestCase):
    def setUp(self):
        self.owner_role = Role.objects.create(
            role_code="credit_manager", role_name="Credit Manager"
        )
        self.reviewer_role = Role.objects.create(
            role_code="compliance_team_member", role_name="Compliance Team Member"
        )
        self.owner = User.objects.create(
            full_name="KYC Owner",
            email="kyc-owner@example.test",
            primary_role=self.owner_role,
        )
        self.reviewer = User.objects.create(
            full_name="Compliance Reviewer",
            email="kyc-reviewer@example.test",
            primary_role=self.reviewer_role,
        )
        self.control = ComplianceControl.objects.create(
            control_code="KYC_AML",
            control_name="KYC and AML review",
            control_area="kyc",
            legal_basis="Two-year governed KYC review.",
            control_type=ComplianceControl.TYPE_DETECTIVE,
            frequency=ComplianceControl.FREQUENCY_ONGOING,
            owner_role_code=self.owner_role.role_code,
            owner_user=self.owner,
            reviewer_user=self.reviewer,
            first_due_date=date(2026, 1, 1),
            evidence_required="Governed KYC verification.",
            risk_if_missed="KYC becomes stale.",
        )

    def test_last_completed_individual_kyc_generates_one_two_year_warning_review_and_task(self):
        from sfpcl_credit.compliance.models import ComplianceTask, KYCReview
        from sfpcl_credit.compliance.modules.kyc_review_tracker import KYCReviewTracker

        member = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Test Member",
            display_name="Test Member",
            folio_number="FOLIO-KYC-1",
            membership_status="active",
            pan_encrypted="encrypted-pan",
            pan_hash="pan-hash-kyc-1",
            kyc_status="rekyc_due",
            default_status="no_default",
        )
        verified_at = datetime(2024, 2, 29, 10, 30, tzinfo=dt_timezone.utc)
        profile = KycProfile.objects.create(
            party_type="member",
            party_id=member.pk,
            kyc_status="rekyc_due",
            ckyc_consent_flag=True,
            beneficial_ownership_verified_flag=None,
            risk_rating="low",
            last_verified_at=verified_at,
            last_verified_by_user=self.owner,
            rekyc_due_date=date(2026, 2, 28),
        )
        for document_type in ("pan", "aadhaar", "photo", "ckyc_consent"):
            document = DocumentFile.objects.create(
                file_name=f"{document_type}.pdf",
                storage_provider="local",
                storage_key=f"governed/kyc/{member.pk}/{document_type}.pdf",
                uploaded_by_user=self.owner,
                sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
            )
            KycDocument.objects.create(
                kyc_profile=profile,
                document_type=document_type,
                document_file=document,
                self_attested_flag=document_type in {"pan", "aadhaar"},
                verification_status="verified",
                verified_by_user=self.owner,
                verified_at=verified_at,
            )

        run = KYCReviewTracker.generate_due_reviews(as_of_date=date(2026, 1, 30))

        self.assertEqual(run.created_count, 1)
        review = KYCReview.objects.get(member=member)
        self.assertEqual(review.due_date, date(2026, 2, 28))
        self.assertEqual(review.status, KYCReview.STATUS_WARNING)
        self.assertTrue(review.completeness_snapshot_json["complete"])
        self.assertEqual(review.task.task_status, ComplianceTask.STATUS_DUE)
        self.assertEqual(review.task.assigned_to_user, self.owner)
        self.assertEqual(review.task.reviewer_user, self.reviewer)

    def test_fpc_missing_pan_ckyc_and_beneficial_ownership_projects_incomplete(self):
        from sfpcl_credit.compliance.models import KYCReview
        from sfpcl_credit.compliance.modules.kyc_review_tracker import KYCReviewTracker

        member = Member.objects.create(
            member_type="fpc",
            legal_name="Test FPC",
            display_name="Test FPC",
            folio_number="FOLIO-KYC-FPC",
            membership_status="active",
            pan_encrypted="",
            pan_hash="",
            kyc_status="verified",
            default_status="no_default",
        )
        profile = KycProfile.objects.create(
            party_type="member",
            party_id=member.pk,
            kyc_status="verified",
            ckyc_consent_flag=False,
            beneficial_ownership_verified_flag=False,
            risk_rating="high",
            last_verified_at=datetime(2024, 1, 31, 8, 0, tzinfo=dt_timezone.utc),
            last_verified_by_user=self.owner,
            rekyc_due_date=date(2026, 1, 31),
        )

        KYCReviewTracker.generate_due_reviews(as_of_date=date(2026, 1, 31))

        summary = KYCReview.objects.get(member=member).completeness_snapshot_json
        self.assertFalse(summary["complete"])
        self.assertEqual(summary["pan_status"], "missing")
        self.assertEqual(summary["ckyc_consent_status"], "missing")
        self.assertEqual(summary["beneficial_ownership_status"], "missing")
        self.assertEqual(
            summary["missing_requirements"],
            ["aadhaar", "beneficial_ownership", "ckyc_consent", "pan", "photo"],
        )

    def test_scheduler_replay_advances_one_cycle_to_one_overdue_reminder(self):
        from sfpcl_credit.communications.models import Notification
        from sfpcl_credit.compliance.models import ComplianceTask, KYCReview
        from sfpcl_credit.compliance.modules.kyc_review_tracker import KYCReviewTracker

        member = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Replay Member",
            display_name="Replay Member",
            folio_number="FOLIO-KYC-REPLAY",
            membership_status="active",
            pan_encrypted="encrypted-pan",
            pan_hash="pan-hash-kyc-replay",
            kyc_status="verified",
            default_status="no_default",
        )
        KycProfile.objects.create(
            party_type="member",
            party_id=member.pk,
            kyc_status="verified",
            ckyc_consent_flag=True,
            risk_rating="medium",
            last_verified_at=datetime(2024, 2, 29, 8, 0, tzinfo=dt_timezone.utc),
            last_verified_by_user=self.owner,
            rekyc_due_date=date(2026, 2, 28),
        )

        first = KYCReviewTracker.generate_due_reviews(as_of_date=date(2026, 1, 30))
        replay = KYCReviewTracker.generate_due_reviews(as_of_date=date(2026, 3, 1))
        second_replay = KYCReviewTracker.generate_due_reviews(as_of_date=date(2026, 3, 1))

        review = KYCReview.objects.get(member=member)
        task = review.task
        self.assertEqual(first.created_count, 1)
        self.assertEqual(replay.replayed_count, 1)
        self.assertEqual(second_replay.replayed_count, 1)
        self.assertEqual(KYCReview.objects.count(), 1)
        self.assertEqual(ComplianceTask.objects.count(), 1)
        self.assertEqual(review.status, KYCReview.STATUS_OVERDUE)
        self.assertEqual(task.task_status, ComplianceTask.STATUS_OVERDUE)
        self.assertEqual(
            Notification.objects.filter(notification_type="kyc_review_due").count(), 1
        )
        self.assertEqual(
            Notification.objects.filter(notification_type="kyc_review_overdue").count(), 1
        )

    def test_new_governed_verification_completes_review_and_linked_task(self):
        from sfpcl_credit.compliance.models import ComplianceTask, KYCReview
        from sfpcl_credit.compliance.modules.kyc_review_tracker import KYCReviewTracker

        permission = Permission.objects.create(
            permission_code="compliance.kyc_review.manage",
            permission_name="Manage KYC reviews",
            module_name="compliance",
            risk_level="high",
        )
        RolePermission.objects.create(role=self.owner_role, permission=permission)
        member = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Completion Member",
            display_name="Completion Member",
            folio_number="FOLIO-KYC-COMPLETE",
            membership_status="active",
            pan_encrypted="encrypted-pan",
            pan_hash="pan-hash-kyc-complete",
            kyc_status="verified",
            default_status="no_default",
        )
        MemberScopeAssignment.objects.create(
            user=self.owner,
            permission_code="compliance.kyc_review.manage",
            scope_type="assigned",
            member=member,
        )
        original_verified_at = datetime(2024, 1, 31, 8, 0, tzinfo=dt_timezone.utc)
        profile = KycProfile.objects.create(
            party_type="member",
            party_id=member.pk,
            kyc_status="verified",
            ckyc_consent_flag=True,
            risk_rating="low",
            last_verified_at=original_verified_at,
            last_verified_by_user=self.owner,
            rekyc_due_date=date(2026, 1, 31),
        )
        for document_type in ("aadhaar", "photo"):
            retained_file = DocumentFile.objects.create(
                file_name=f"retained-{document_type}.pdf",
                storage_provider="local",
                storage_key=f"governed/kyc/{member.pk}/retained-{document_type}.pdf",
                uploaded_by_user=self.owner,
                sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
            )
            KycDocument.objects.create(
                kyc_profile=profile,
                document_type=document_type,
                document_file=retained_file,
                self_attested_flag=document_type == "aadhaar",
                verification_status="verified",
                verified_by_user=self.owner,
                verified_at=original_verified_at,
            )
        KYCReviewTracker.generate_due_reviews(as_of_date=date(2026, 1, 31))
        review = KYCReview.objects.get(member=member)
        new_verified_at = datetime(2026, 2, 1, 9, 30, tzinfo=dt_timezone.utc)
        document = DocumentFile.objects.create(
            file_name="updated-pan.pdf",
            storage_provider="local",
            storage_key=f"governed/kyc/{member.pk}/updated-pan.pdf",
            uploaded_by_user=self.reviewer,
            sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
        )
        evidence = KycDocument.objects.create(
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
        profile.kyc_status = "verified"
        profile.rekyc_due_date = date(2028, 2, 1)
        profile.save()

        result = KYCReviewTracker.complete(actor=self.owner, review_id=review.pk)

        review.refresh_from_db()
        self.assertEqual(result["status"], KYCReview.STATUS_COMPLETED)
        self.assertEqual(review.status, KYCReview.STATUS_COMPLETED)
        self.assertEqual(review.kyc_status_before, "verified")
        self.assertEqual(review.kyc_status_after, "verified")
        self.assertEqual(review.reviewed_by_user, self.owner)
        self.assertEqual(review.completion_verified_at, new_verified_at)
        self.assertEqual(
            review.completion_evidence_json,
            [{"kyc_document_id": str(evidence.pk), "document_id": str(document.pk)}],
        )
        self.assertEqual(review.task.task_status, ComplianceTask.STATUS_COMPLETED)
        self.assertIsNotNone(review.task.closed_at)

    def test_retained_review_rejects_direct_cycle_mutation(self):
        from sfpcl_credit.compliance.models import KYCReview
        from sfpcl_credit.compliance.modules.kyc_review_tracker import KYCReviewTracker

        member = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Immutable Member",
            display_name="Immutable Member",
            folio_number="FOLIO-KYC-IMMUTABLE",
            membership_status="active",
            pan_encrypted="encrypted-pan",
            pan_hash="pan-hash-kyc-immutable",
            kyc_status="verified",
            default_status="no_default",
        )
        KycProfile.objects.create(
            party_type="member",
            party_id=member.pk,
            kyc_status="verified",
            ckyc_consent_flag=True,
            risk_rating="low",
            last_verified_at=datetime(2024, 1, 31, 8, 0, tzinfo=dt_timezone.utc),
            last_verified_by_user=self.owner,
            rekyc_due_date=date(2026, 1, 31),
        )
        KYCReviewTracker.generate_due_reviews(as_of_date=date(2026, 1, 31))
        review = KYCReview.objects.get(member=member)

        review.due_date = date(2026, 2, 1)

        with self.assertRaisesMessage(ValueError, "Retained KYC review facts are immutable"):
            review.save()
