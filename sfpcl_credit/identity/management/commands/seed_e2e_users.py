import os
from datetime import datetime
from uuid import UUID

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from sfpcl_credit.applications.models import ApplicationDocument, LoanApplication
from sfpcl_credit.configurations.models import LoanPolicyConfig
from sfpcl_credit.credit.models import EligibilityAssessment
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import Permission, Role, RolePermission, User
from sfpcl_credit.members.models import CropPlan, IndividualMemberProfile, LandHolding, Member, Nominee, ProduceSupplyRecord, Shareholding

# Non-secret credentials for the local Playwright suite only. The suite logs in
# through the production auth path (POST /auth/login/ + GET /auth/me/), so a real
# backend user with a real password hash is required — no frontend fixtures.
E2E_PASSWORD = "E2eTracer123!"
TRACER_PERMISSION_CODE = "tracer.lifecycle.run"

TRACER_USER_EMAIL = "e2e.tracer@sfpcl.example"
TRACER_ROLE_CODE = "e2e_tracer"

# `it_head` maps to the neutral `backend_staff` frontend role and carries no
# canonical permissions (see identity/catalogue.py), so it drives the
# restricted-UI browser checks (002EY req 9, 11).
ZERO_USER_EMAIL = "e2e.zero@sfpcl.example"
ZERO_ROLE_CODE = "it_head"

EPIC_006_FINANCE_EMAIL = "e2e.credit.finance@sfpcl.example"
EPIC_006_MANAGER_EMAIL = "e2e.credit.manager@sfpcl.example"
EPIC_006_IDS = {
    name: UUID(f"00000000-0000-4000-8000-{number:012d}")
    for name, number in {
        "application": 601, "member": 602, "nominee": 603, "shareholding": 604,
        "land": 605, "crop": 606, "eligibility": 607, "policy": 608,
        "witness_member": 611, "witness_shareholding": 612,
        "supply_2022": 621, "supply_2023": 622, "supply_2024": 623, "supply_2025": 624,
    }.items()
}
EPIC_006_REFERENCE = "LOE2E00601"
EPIC_006_FINANCE_PERMISSIONS = (
    "applications.loan_application.read", "members.member.read",
    "members.member.create", "members.member.update",
    "members.witness.read", "members.witness.create", "members.witness.update", "credit.eligibility.run",
    "credit.loan_limit.calculate", "credit.appraisal.create",
    "credit.appraisal.update", "credit.appraisal.submit_review",
    "credit.appraisal.submit_sanction", "credit.risk_assessment.manage",
)
EPIC_006_MANAGER_PERMISSIONS = (
    "applications.loan_application.read", "members.member.read",
    "members.member.identity_change.approve", "credit.appraisal.review",
    "credit.appraisal.submit_sanction",
)
EPIC_006_DOCUMENT_TYPES = (
    "loan_application_form", "borrower_pan", "borrower_aadhaar_ovd",
    "nominee_pan", "nominee_aadhaar_ovd", "share_certificate_copy",
    "land_document_7_12", "crop_plan", "six_month_bank_statement",
)


class Command(BaseCommand):
    help = (
        "Idempotently seed the deterministic staff users the Playwright E2E suite "
        "logs in as: a tracer-only staff user and a zero-permission staff user. "
        "Refuses to run unless SFPCL_DEBUG=true and SFPCL_ALLOW_E2E_SEED=true."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self._enforce_e2e_guard()

        tracer_permission, _ = Permission.objects.get_or_create(
            permission_code=TRACER_PERMISSION_CODE,
            defaults={
                "permission_name": "Run MVP tracer",
                "module_name": "tracer",
                "risk_level": Permission.RISK_HIGH,
            },
        )

        tracer_role = self._ensure_role(
            TRACER_ROLE_CODE,
            role_name="E2E Tracer Staff",
            description="Automated E2E staff role: tracer lifecycle permission only.",
        )
        RolePermission.objects.get_or_create(
            role=tracer_role, permission=tracer_permission
        )

        zero_role = self._ensure_role(
            ZERO_ROLE_CODE,
            role_name="IT Head",
            description="Access control and system security oversight",
        )

        tracer_user = self._ensure_user(
            email=TRACER_USER_EMAIL,
            full_name="E2E Tracer Staff",
            role=tracer_role,
        )
        zero_user = self._ensure_user(
            email=ZERO_USER_EMAIL,
            full_name="E2E Zero Permission Staff",
            role=zero_role,
        )
        finance_role = self._ensure_credit_role(
            "deputy_manager_finance", "Deputy Manager – Finance",
            EPIC_006_FINANCE_PERMISSIONS,
        )
        manager_role = self._ensure_credit_role(
            "credit_manager", "Credit Manager", EPIC_006_MANAGER_PERMISSIONS,
        )
        finance_user = self._ensure_user(
            email=EPIC_006_FINANCE_EMAIL,
            full_name="E2E Deputy Manager Finance",
            role=finance_role,
        )
        manager_user = self._ensure_user(
            email=EPIC_006_MANAGER_EMAIL,
            full_name="E2E Credit Manager",
            role=manager_role,
        )
        self._seed_epic_006_fixture(finance_user)

        self.stdout.write(
            "E2E users seeded: "
            f"{tracer_user.email} (role {tracer_role.role_code}, "
            f"permission {TRACER_PERMISSION_CODE}); "
            f"{zero_user.email} (role {zero_role.role_code}, no permissions)."
            f" Credit fixture: {EPIC_006_REFERENCE}, {finance_user.email}, "
            f"{manager_user.email}."
        )

    @staticmethod
    def _env_true(name):
        return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}

    @classmethod
    def _enforce_e2e_guard(cls):
        if not cls._env_true("SFPCL_DEBUG") or not cls._env_true(
            "SFPCL_ALLOW_E2E_SEED"
        ):
            raise CommandError(
                "seed_e2e_users is for isolated local Playwright databases only. "
                "Set SFPCL_DEBUG=true and SFPCL_ALLOW_E2E_SEED=true to run it."
            )

    @staticmethod
    def _ensure_role(role_code, *, role_name, description):
        role, _created = Role.objects.get_or_create(
            role_code=role_code,
            defaults={
                "role_name": role_name,
                "description": description,
                "is_system_role": False,
                "status": "active",
            },
        )
        # A pre-existing role (e.g. it_head from the catalogue) must stay active so
        # its user can authenticate and expose permissions.
        if role.status != "active":
            role.status = "active"
            role.save(update_fields=["status"])
        return role

    @staticmethod
    def _ensure_user(*, email, full_name, role):
        user, _created = User.objects.get_or_create(
            email=email,
            defaults={
                "full_name": full_name,
                "status": "active",
                "primary_role": role,
            },
        )
        # Keep the deterministic role, status, and password even if the row existed.
        user.full_name = full_name
        user.primary_role = role
        user.status = "active"
        user.set_password(E2E_PASSWORD)
        user.save()
        return user

    @classmethod
    def _ensure_credit_role(cls, role_code, role_name, permission_codes):
        role = cls._ensure_role(
            role_code,
            role_name=role_name,
            description="Deterministic Epic 006 trusted-browser role.",
        )
        for permission_code in permission_codes:
            permission, _created = Permission.objects.get_or_create(
                permission_code=permission_code,
                defaults={
                    "permission_name": permission_code,
                    "module_name": permission_code.split(".", 1)[0],
                    "risk_level": Permission.RISK_HIGH,
                },
            )
            RolePermission.objects.get_or_create(role=role, permission=permission)
        return role

    @staticmethod
    def _seed_epic_006_fixture(finance_user):
        instant = timezone.make_aware(datetime(2026, 7, 11, 10, 0, 0))
        member, _created = Member.objects.update_or_create(
            member_id=EPIC_006_IDS["member"],
            defaults={
                "member_number": "MEM-E2E-006", "member_type": "individual_farmer",
                "legal_name": "Epic 006 Browser Member",
                "display_name": "Epic 006 Browser Member", "folio_number": "FOL-E2E-006",
                "membership_status": "active", "pan_encrypted": "synthetic-e2e-pan",
                "pan_hash": "synthetic-e2e-pan-hash",
                "aadhaar_encrypted": "synthetic-e2e-aadhaar",
                "aadhaar_hash": "synthetic-e2e-aadhaar-hash", "kyc_status": "verified",
                "default_status": "no_default", "active_member_status": "active",
                "active_member_verified_at": instant, "created_by_user": finance_user,
            },
        )
        IndividualMemberProfile.objects.update_or_create(
            member=member,
            defaults={
                "first_name": "Epic 006", "last_name": "Member",
                "services_availed_flag": True,
            },
        )
        for key, financial_year in (
            ("supply_2022", "2022-23"), ("supply_2023", "2023-24"),
            ("supply_2024", "2024-25"), ("supply_2025", "2025-26"),
        ):
            ProduceSupplyRecord.objects.update_or_create(
                produce_supply_record_id=EPIC_006_IDS[key],
                defaults={
                    "member": member, "financial_year": financial_year,
                    "supplied_to_entity_type": "sfpcl", "supply_route": "direct",
                    "crop_type": "synthetic_crop", "evidence_reference": f"E2E-{financial_year}",
                    "captured_by_user": finance_user, "verified_flag": True,
                    "verified_by_user": finance_user, "verified_at": instant,
                },
            )
        witness_member, _created = Member.objects.update_or_create(
            member_id=EPIC_006_IDS["witness_member"],
            defaults={
                "member_number": "MEM-E2E-006-W",
                "member_type": "individual_farmer",
                "legal_name": "Epic 006 Browser Witness",
                "display_name": "Epic 006 Browser Witness",
                "folio_number": "FOL-E2E-006-W",
                "membership_status": "active",
                "pan_encrypted": "synthetic-e2e-witness-pan",
                "pan_hash": "synthetic-e2e-witness-pan-hash",
                "aadhaar_encrypted": "synthetic-e2e-witness-aadhaar",
                "aadhaar_hash": "synthetic-e2e-witness-aadhaar-hash",
                "kyc_status": "verified",
                "default_status": "no_default",
                "active_member_status": "active",
                "active_member_verified_at": instant,
                "created_by_user": finance_user,
            },
        )
        nominee, _created = Nominee.objects.update_or_create(
            nominee_id=EPIC_006_IDS["nominee"],
            defaults={
                "member": member, "loan_application_id": EPIC_006_IDS["application"],
                "nominee_name": "Epic 006 Synthetic Nominee", "age_at_application": 42,
                "gender": "female", "relationship_to_borrower": "Spouse",
                "pan_encrypted": "synthetic-e2e-nominee-pan",
                "pan_hash": "synthetic-e2e-nominee-pan-hash",
                "aadhaar_encrypted": "synthetic-e2e-nominee-aadhaar",
                "aadhaar_hash": "synthetic-e2e-nominee-aadhaar-hash",
                "kyc_status": "verified", "minor_flag": False,
            },
        )
        land, _created = LandHolding.objects.update_or_create(
            land_holding_id=EPIC_006_IDS["land"],
            defaults={
                "member": member, "document_type": "7_12_extract",
                "survey_number": "E2E-006", "village": "Synthetic Village",
                "area_acres": "5.00", "document_id": UUID(int=609),
                "verification_status": "verified", "verified_by_user": finance_user,
                "verified_at": instant,
            },
        )
        crop, _created = CropPlan.objects.update_or_create(
            crop_plan_id=EPIC_006_IDS["crop"],
            defaults={
                "member": member, "loan_application_id": EPIC_006_IDS["application"],
                "crop_type": "grapes", "season": "FY2026 Kharif",
                "planned_area_acres": "5.00", "estimated_cost_amount": "100000.00",
                "loan_purpose_alignment": "agriculture_aligned", "document_id": UUID(int=610),
                "verification_status": "verified", "verified_by_user": finance_user,
                "verified_at": instant,
            },
        )
        application, _created = LoanApplication.objects.update_or_create(
            loan_application_id=EPIC_006_IDS["application"],
            defaults={
                "application_reference_number": EPIC_006_REFERENCE, "member": member,
                "borrower_type": member.member_type, "application_channel": "assisted_digital",
                "application_date": instant.date(), "received_by_user": finance_user,
                "required_loan_amount": "15000.00", "requested_tenure_months": 12,
                "declared_purpose": "Synthetic crop production browser proof",
                "purpose_category": "crop_production", "nominee": nominee,
                "loan_type_requested": "short_term", "land_holding": land, "crop_plan": crop,
                "current_stage": LoanApplication.STAGE_CREDIT_ASSESSMENT,
                "application_status": LoanApplication.STATUS_REFERENCE_GENERATED,
                "completeness_status": LoanApplication.COMPLETENESS_COMPLETE,
                "terms_acceptance_flag": True, "submitted_at": instant,
                "submitted_by_user": finance_user, "created_at": instant,
                "created_by_user": finance_user, "updated_at": instant,
                "updated_by_user": finance_user,
            },
        )
        Shareholding.objects.update_or_create(
            shareholding_id=EPIC_006_IDS["shareholding"],
            defaults={
                "member": member, "folio_number": member.folio_number,
                "number_of_shares": 100, "holding_mode": "physical",
                "valuation_per_share": "2000.00", "valuation_effective_date": instant.date(),
                "pledged_share_count": 0, "available_share_count": 100, "status": "active",
            },
        )
        Shareholding.objects.update_or_create(
            shareholding_id=EPIC_006_IDS["witness_shareholding"],
            defaults={
                "member": witness_member,
                "folio_number": witness_member.folio_number,
                "number_of_shares": 25,
                "holding_mode": "physical",
                "valuation_per_share": "2000.00",
                "valuation_effective_date": instant.date(),
                "pledged_share_count": 0,
                "available_share_count": 25,
                "status": "active",
            },
        )
        LoanPolicyConfig.objects.update_or_create(
            loan_policy_config_id=EPIC_006_IDS["policy"],
            defaults={
                "policy_name": "Epic 006 synthetic board policy", "policy_version": "e2e-policy-v1",
                "effective_from": instant.date(), "short_term_duration_months": 12,
                "approval_threshold_amount": "500000.00",
                "default_scale_of_finance_per_acre_amount": "20000.00",
                "share_limit_percentage": "10.0000", "per_share_cap_amount": "200.00",
                "interest_rate_type": "floating", "rekyc_frequency_months": 24,
                "record_retention_years": 8, "grace_period_months": 3,
                "non_intentional_extension_months": 3,
                "board_approval_reference": "BOARD/E2E/006",
                "status": LoanPolicyConfig.STATUS_ACTIVE,
            },
        )
        for index, document_type in enumerate(EPIC_006_DOCUMENT_TYPES, start=1):
            document_file, _created = DocumentFile.objects.update_or_create(
                document_id=UUID(f"00000000-0000-4000-8100-{index:012d}"),
                defaults={
                    "file_name": f"{document_type}.pdf", "file_extension": ".pdf",
                    "mime_type": "application/pdf", "file_size_bytes": 256,
                    "storage_provider": "local",
                    "storage_key": f"e2e/epic-006/{document_type}.pdf",
                    "checksum_sha256": f"synthetic-{document_type}",
                    "uploaded_by_user": finance_user, "uploaded_at": instant,
                    "sensitivity_level": DocumentFile.SENSITIVITY_RESTRICTED,
                },
            )
            ApplicationDocument.objects.update_or_create(
                application_document_id=UUID(f"00000000-0000-4000-8200-{index:012d}"),
                defaults={
                    "loan_application": application, "document_type": document_type,
                    "party_type": "borrower", "party_id": member.member_id,
                    "document_file": document_file, "required_flag": True,
                    "submission_status": ApplicationDocument.SUBMISSION_SUBMITTED,
                    "verification_status": ApplicationDocument.VERIFICATION_VERIFIED,
                    "verified_by_user": finance_user, "verified_at": instant,
                    "remarks": "Synthetic E2E completeness evidence.", "version_number": 1,
                    "created_at": instant, "created_by_user": finance_user,
                    "updated_at": instant, "updated_by_user": finance_user,
                },
            )
        EligibilityAssessment.objects.update_or_create(
            eligibility_assessment_id=EPIC_006_IDS["eligibility"],
            defaults={
                "loan_application": application,
                "member_active_check": EligibilityAssessment.CHECK_PENDING,
                "default_check": EligibilityAssessment.CHECK_PENDING,
                "document_check": EligibilityAssessment.CHECK_PENDING,
                "terms_acceptance_check": EligibilityAssessment.CHECK_PENDING,
                "purpose_check": EligibilityAssessment.CHECK_PENDING,
                "nominee_check": EligibilityAssessment.CHECK_PENDING,
                "overall_result": EligibilityAssessment.OVERALL_PENDING,
                "assessment_notes": "Synthetic pre-run assessment for browser action projection.",
                "assessed_by_user": finance_user, "assessed_at": instant,
            },
        )
