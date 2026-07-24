import hashlib
import os
from datetime import timedelta

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from sfpcl_credit.applications.models import ApplicationDeficiency, LoanApplication
from sfpcl_credit.approvals.models import (
    ApprovalCase,
    ApprovalMatrixRule,
    SanctionCommittee,
    SanctionDecision,
)
from sfpcl_credit.approvals.modules.approval_case_projection import (
    refresh_approval_case_projection,
)
from sfpcl_credit.credit.models import (
    AppraisalReviewDecision,
    LoanAppraisalNote,
    RiskAssessment,
)
from sfpcl_credit.credit.modules.appraisal_workflow import (
    project_approval_case_review_facts,
)
from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.identity.models import Permission, PortalAccount, Role, RolePermission, User
from sfpcl_credit.legal_documents.models import LoanDocument, SignatureRecord
from sfpcl_credit.legal_documents.modules import document_checklist
from sfpcl_credit.members.models import Member, Nominee, Shareholding
from sfpcl_credit.processes import document_checklist_actions
from sfpcl_credit.legal_documents.modules.checklist_actions import RequestMetadata


PORTAL_EMAIL = "e2e.portal@sfpcl.example"
PORTAL_PASSWORD = "E2eTracer123!"


class Command(BaseCommand):
    help = "Seed isolated real-boundary MP07/MP11 Playwright fixtures."

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.ENABLE_DEMO_SURFACES:
            raise CommandError(
                "seed_portal_e2e_fixture is disabled by deployment settings."
            )
        if not self._env_true("SFPCL_DEBUG") or not self._env_true(
            "SFPCL_ALLOW_E2E_SEED"
        ):
            raise CommandError(
                "seed_portal_e2e_fixture requires the isolated E2E seed guards."
            )
        if PortalAccount.objects.filter(user__email=PORTAL_EMAIL).exists():
            self.stdout.write("Portal E2E fixture already exists.")
            return

        portal_role = Role.objects.get(role_code="borrower_portal_user")
        compliance_role = self._role_with_permissions(
            "compliance_team_member",
            [
                "documents.checklist.update",
                "documents.file.upload",
                "documents.signature.record",
                "documents.stamp.record",
                "documents.notary.record",
            ],
        )
        cfo_role = Role.objects.get(role_code="cfo")
        director_role = Role.objects.get(role_code="director")
        compliance = self._user("e2e.portal.compliance@sfpcl.example", compliance_role)
        cfo = self._user("e2e.portal.cfo@sfpcl.example", cfo_role)
        director_one = self._user("e2e.portal.director1@sfpcl.example", director_role)
        director_two = self._user("e2e.portal.director2@sfpcl.example", director_role)
        portal_user = self._user(PORTAL_EMAIL, portal_role, "Portal Contract Member")

        member = Member.objects.create(
            member_number="MEM-E2E-PORTAL",
            member_type="individual_farmer",
            legal_name="Portal Contract Member",
            display_name="Portal Contract Member",
            folio_number="FOL-E2E-PORTAL",
            membership_status="active",
            kyc_status="verified",
            default_status="no_default",
            active_member_status="active",
            active_member_verified_at=timezone.now(),
            created_by_user=compliance,
        )
        PortalAccount.objects.create(
            member=member,
            user=portal_user,
            status=PortalAccount.STATUS_ACTIVE,
            activated_at=timezone.now(),
        )
        nominee = Nominee.objects.create(
            member=member,
            nominee_name="Portal Contract Nominee",
            age_at_application=35,
            gender="other",
            relationship_to_borrower="family",
            pan_encrypted="e2e-nominee-pan",
            pan_hash="e2e-portal-nominee-pan-hash",
            aadhaar_encrypted="e2e-nominee-aadhaar",
            aadhaar_hash="e2e-portal-nominee-aadhaar-hash",
            kyc_status="verified",
        )
        shareholding = Shareholding.objects.create(
            member=member,
            folio_number=member.folio_number,
            number_of_shares=10,
            holding_mode="physical",
            pledged_share_count=0,
            available_share_count=10,
            status="active",
        )
        approved, case = self._approved_application(
            member, nominee, shareholding, compliance, cfo, director_one, director_two
        )
        checklist = document_checklist.refresh_for_approved_sanction(
            actor=compliance,
            application_id=approved.pk,
            source_reason="portal_e2e_fixture",
        )
        term_sheet = self._term_sheet(approved, compliance)
        self._power_of_attorney(approved, compliance)
        signed_at = timezone.now()
        for party_type, party_id, name in (
            ("borrower", member.pk, member.display_name),
            ("nominee", nominee.pk, nominee.nominee_name),
            ("user", cfo.pk, cfo.full_name),
        ):
            SignatureRecord.objects.create(
                loan_document=term_sheet,
                signer_party_type=party_type,
                signer_party_id=party_id,
                signer_name_snapshot=name,
                signature_method="wet_ink",
                signature_status="signed",
                signature_mismatch_flag=False,
                signed_at=signed_at,
                captured_by_user=compliance,
            )
        term_item = checklist.items.get(item_code="term_sheet")
        document_checklist_actions.complete_item(
            actor=compliance,
            checklist_item_id=term_item.pk,
            payload={
                "loan_document_id": str(term_sheet.pk),
                "remarks": "Published signed Term Sheet for portal proof.",
            },
            metadata=RequestMetadata(
                request_id="e2e-term-sheet-complete",
                ip_address="127.0.0.1",
                user_agent="seed_portal_e2e_fixture",
            ),
        )

        returned = LoanApplication.objects.create(
            member=member,
            nominee=nominee,
            borrower_type=member.member_type,
            received_by_user=compliance,
            created_by_user=portal_user,
            application_reference_number="LO000008L4-R",
            required_loan_amount="250000.00",
            requested_tenure_months=12,
            declared_purpose="Crop production",
            purpose_category="crop_production",
            application_status=LoanApplication.STATUS_INCOMPLETE_RETURNED,
            completeness_status=LoanApplication.COMPLETENESS_INCOMPLETE,
            current_stage=LoanApplication.STAGE_INITIAL,
        )
        ApplicationDeficiency.objects.create(
            loan_application=returned,
            item_code="six_month_bank_statement",
            deficiency_type=ApplicationDeficiency.TYPE_MISSING_DOCUMENT,
            source_reason_code="missing_metadata",
            description="Upload the missing six-month bank statement.",
            remarks="Internal fixture note.",
            resolution_status=ApplicationDeficiency.STATUS_OPEN,
            raised_by_user=compliance,
            communication_mode="portal",
            message="Please attach the complete statement.",
        )
        self.stdout.write(
            f"Portal E2E fixture seeded for {PORTAL_EMAIL}: "
            f"{approved.application_reference_number}, {returned.application_reference_number}."
        )

    @staticmethod
    def _env_true(name):
        return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _role_with_permissions(role_code, permission_codes):
        role = Role.objects.get(role_code=role_code)
        for code in permission_codes:
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": code.split(".", 1)[0],
                    "risk_level": Permission.RISK_HIGH,
                },
            )
            RolePermission.objects.get_or_create(role=role, permission=permission)
        return role

    @staticmethod
    def _user(email, role, full_name=None):
        user = User.objects.create(
            email=email,
            full_name=full_name or role.role_name,
            status="active",
            primary_role=role,
        )
        user.set_password(PORTAL_PASSWORD)
        user.save(update_fields=["password_hash"])
        return user

    @staticmethod
    def _approved_application(
        member, nominee, shareholding, compliance, cfo, director_one, director_two
    ):
        now = timezone.now()
        application = LoanApplication.objects.create(
            member=member,
            nominee=nominee,
            borrower_type=member.member_type,
            received_by_user=compliance,
            created_by_user=compliance,
            application_reference_number="LO000008L4",
            required_loan_amount="400000.00",
            requested_tenure_months=12,
            declared_purpose="Crop production",
            purpose_category="crop_production",
            application_status=LoanApplication.STATUS_APPROVED_BY_SANCTION,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            terms_acceptance_flag=True,
        )
        risk = RiskAssessment.objects.create(
            loan_application=application,
            market_risk_rating="low",
            operational_risk_rating="low",
            borrower_risk_rating="low",
            overall_risk_rating="low",
            assessed_by_user=compliance,
        )
        note = LoanAppraisalNote.objects.create(
            loan_application=application,
            prepared_by_user=compliance,
            reviewed_by_user=compliance,
            reviewed_at=now,
            last_review_decision="reviewed",
            tat_due_at=now + timedelta(days=1),
            tat_status=LoanAppraisalNote.TAT_WITHIN,
            eligibility_assessment_id_snapshot="10000000-0000-0000-0000-000000000001",
            loan_limit_assessment_id_snapshot="20000000-0000-0000-0000-000000000002",
            eligibility_snapshot_json={
                "eligibility_assessment_id": "10000000-0000-0000-0000-000000000001",
                "loan_application_id": str(application.pk),
                "overall_result": "eligible",
                "member_active_check": "pass",
                "default_check": "pass",
                "document_check": "pass",
                "terms_acceptance_check": "pass",
                "purpose_check": "pass",
                "nominee_check": "pass",
                "assessment_notes": "Eligible portal fixture.",
                "active_member_snapshot": {
                    "supplied_to_subsidiary_flag": False,
                    "supplied_to_stepdown_flag": False,
                },
                "assessed_by_user_id": str(compliance.pk),
                "assessed_at": now.isoformat(),
            },
            loan_limit_snapshot_json={
                "loan_limit_assessment_id": "20000000-0000-0000-0000-000000000002",
                "loan_application_id": str(application.pk),
                "shareholding_id": str(shareholding.pk),
                "number_of_shares": shareholding.number_of_shares,
                "final_eligible_loan_amount": "400000.00",
                "exception_required_flag": False,
                "calculation_rule_version": "portal-e2e-limit-v1",
                "policy_config_id": "30000000-0000-0000-0000-000000000003",
                "policy_name": "Portal E2E Policy",
                "calculated_at": now.isoformat(),
            },
            prerequisite_provenance="verified",
            borrower_summary="Eligible portal fixture.",
            eligibility_summary="Eligible.",
            loan_limit_summary="Within limit.",
            recommended_amount="400000.00",
            recommended_tenure_months=12,
            recommended_interest_type="floating",
            recommended_security_summary="Standard security.",
            repayment_capacity_notes="Adequate.",
            risk_assessment=risk,
            recommendation="approve",
            appraisal_status=LoanAppraisalNote.STATUS_SUBMITTED_TO_SANCTION,
        )
        review = AppraisalReviewDecision.objects.create(
            loan_appraisal_note=note,
            decision="reviewed",
            review_comments="Portal fixture review.",
            reviewer_user=compliance,
            decided_at=now,
            from_state=LoanAppraisalNote.STATUS_REVIEW_PENDING,
            to_state=LoanAppraisalNote.STATUS_REVIEWED,
        )
        today = timezone.localdate()
        rule = ApprovalMatrixRule.objects.create(
            decision_type="loan_sanction",
            amount_min="0.00",
            amount_max="500000.00",
            required_approver_roles_json=["cfo", "director"],
            required_director_count=1,
            joint_approval_required_flag=True,
            register_required="credit_sanction_register",
            effective_from=today,
            status="active",
            version_number="portal-e2e-rule-v1",
        )
        committee = SanctionCommittee.objects.create(
            committee_name="Portal E2E Committee",
            cfo_user=cfo,
            director_1_user=director_one,
            director_2_user=director_two,
            board_meeting_reference="BM-PORTAL-E2E",
            effective_from=today,
            status="active",
            version_number="portal-e2e-committee-v1",
        )
        case = ApprovalCase.objects.create(
            loan_application=application,
            loan_appraisal_note=note,
            appraisal_review_decision=review,
            submitted_by_user=compliance,
            submission_remarks="Portal fixture sanction.",
            approval_matrix_rule=rule,
            approval_matrix_rule_version=rule.version_number,
            sanction_committee=committee,
            sanction_committee_version=committee.version_number,
            required_approvers_json=[
                {"role_code": "cfo", "user_id": str(cfo.pk), "full_name": cfo.full_name},
                {"role_code": "director", "user_id": str(director_one.pk), "full_name": director_one.full_name},
            ],
            excluded_approvers_json=[],
            current_status=ApprovalCase.STATUS_APPROVED,
            amount="400000.00",
            related_entity_type="loan_application",
            related_entity_id=application.pk,
            reason_for_approval="Approved portal fixture.",
            closed_at=now,
            matrix_projection_json={
                "approval_matrix_rule_id": str(rule.pk),
                "version_number": rule.version_number,
                "decision_type": "loan_sanction", "amount": "400000.00",
                "amount_min": "0.00", "amount_max": "500000.00",
                "condition_code": None, "decision_date": today.isoformat(),
                "required_approver_roles": ["cfo", "director"],
                "required_director_count": 1, "joint_approval_required": True,
                "register_required": "credit_sanction_register",
            },
            committee_projection_json={
                "sanction_committee_id": str(committee.pk),
                "version_number": committee.version_number,
                "decision_date": today.isoformat(),
                "cfo_user_id": str(cfo.pk),
                "director_user_ids": [str(director_one.pk), str(director_two.pk)],
            },
            loan_limit_provenance_json={
                "loan_limit_assessment_id": str(note.loan_limit_assessment_id_snapshot),
                "loan_application_id": str(application.pk),
                "final_eligible_loan_amount": "400000.00",
                "exception_required_flag": False,
                "calculation_rule_version": "portal-e2e-limit-v1",
                "policy_config_id": "30000000-0000-0000-0000-000000000003",
                "policy_name": "Portal E2E Policy",
                "calculated_at": now.isoformat(),
            },
            decision_date=today,
            version=2,
        )
        application.refresh_from_db()
        note.refresh_from_db()
        case.appraisal_facts_json = project_approval_case_review_facts(
            application=application, appraisal_note=note, review=review
        )
        case.appraisal_facts_json["shareholding"] = {"holding_mode": "physical"}
        case.save(update_fields=["appraisal_facts_json"])
        refresh_approval_case_projection(case)
        SanctionDecision.objects.create(
            loan_application=application,
            approval_case=case,
            decision="sanctioned",
            sanctioned_amount="400000.00",
            sanctioned_tenure_months=12,
            interest_rate_type="floating",
            security_required_summary="Standard security.",
            decision_reason="Approved.",
        )
        return application, case

    @staticmethod
    def _term_sheet(application, actor):
        body = b"%PDF-1.4\nPortal current Term Sheet\n%%EOF\n"
        stored = LocalDocumentStorage().store(ContentFile(body, name="term-sheet-LO000008L4.pdf"))
        output = DocumentFile.objects.create(
            file_name="term-sheet-LO000008L4.pdf",
            file_extension=".pdf",
            mime_type="application/pdf",
            file_size_bytes=stored.file_size_bytes,
            storage_provider=stored.storage_provider,
            storage_key=stored.storage_key,
            checksum_sha256=stored.checksum_sha256,
            uploaded_by_user=actor,
            sensitivity_level="confidential",
        )
        template, _ = DocumentTemplate.objects.get_or_create(
            document_type="term_sheet",
            borrower_type="individual_farmer",
            template_version="1.0",
            defaults={
                "template_code": "portal-e2e-term-sheet-v1",
                "template_name": "Portal E2E Term Sheet",
                "merge_fields_json": [],
                "approval_status": "approved",
                "effective_from": timezone.localdate(),
            },
        )
        return LoanDocument.objects.create(
            loan_application=application,
            document_type="term_sheet",
            document_category="legal",
            party_required="borrower",
            document_template=template,
            document=output,
            output_format="pdf",
            generation_status="generated",
            execution_status="pending",
            verification_status="verified",
            renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
            renderer_validated_document_id=output.pk,
            renderer_validated_checksum_sha256=hashlib.sha256(body).hexdigest(),
        )

    @staticmethod
    def _power_of_attorney(application, actor):
        body = b"%PDF-1.4\nE2E pending Power of Attorney\n%%EOF\n"
        stored = LocalDocumentStorage().store(
            ContentFile(body, name="power-of-attorney-LO000008L4.pdf")
        )
        output = DocumentFile.objects.create(
            file_name="power-of-attorney-LO000008L4.pdf",
            file_extension=".pdf",
            mime_type="application/pdf",
            file_size_bytes=stored.file_size_bytes,
            storage_provider=stored.storage_provider,
            storage_key=stored.storage_key,
            checksum_sha256=stored.checksum_sha256,
            uploaded_by_user=actor,
            sensitivity_level="confidential",
        )
        template, _ = DocumentTemplate.objects.get_or_create(
            document_type="power_of_attorney",
            borrower_type="individual_farmer",
            template_version="1.0",
            defaults={
                "template_code": "portal-e2e-power-of-attorney-v1",
                "template_name": "Portal E2E Power of Attorney",
                "merge_fields_json": [],
                "approval_status": "approved",
                "effective_from": timezone.localdate(),
            },
        )
        return LoanDocument.objects.create(
            loan_application=application,
            document_type="power_of_attorney",
            document_category="legal",
            party_required="borrower",
            document_template=template,
            document=output,
            output_format="pdf",
            generation_status="generated",
            execution_status="pending",
            verification_status="pending",
            renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
            renderer_validated_document_id=output.pk,
            renderer_validated_checksum_sha256=hashlib.sha256(body).hexdigest(),
        )
