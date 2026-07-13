from datetime import timedelta

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils import timezone


class ApprovalReadScopeMigrationTests(TransactionTestCase):
    migrate_from = [
        ("credit", "0007_eligibility_active_member_snapshot"),
        ("approvals", "0009_sanction_decision_and_case_closure"),
    ]
    migrate_to = [
        ("credit", "0007_eligibility_active_member_snapshot"),
        ("approvals", "0010_approvalcasereadscopegrant_and_more"),
    ]

    def test_migration_backfills_exact_scope_and_coherence_from_historical_state(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps
        fixtures = self._create_historical_cases(old_apps)

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)
        migrated_apps = executor.loader.project_state(self.migrate_to).apps

        ApprovalCase = migrated_apps.get_model("approvals", "ApprovalCase")
        RequiredApprover = migrated_apps.get_model(
            "approvals", "ApprovalCaseRequiredApprover"
        )
        Grant = migrated_apps.get_model("approvals", "ApprovalCaseReadScopeGrant")
        valid = ApprovalCase.objects.get(pk=fixtures["valid_case_id"])
        malformed = ApprovalCase.objects.get(pk=fixtures["malformed_case_id"])
        self.assertTrue(valid.routing_snapshot_is_coherent)
        self.assertFalse(malformed.routing_snapshot_is_coherent)
        self.assertEqual(
            set(
                RequiredApprover.objects.filter(approval_case=valid).values_list(
                    "user_id", flat=True
                )
            ),
            fixtures["required_user_ids"],
        )
        self.assertEqual(
            set(Grant.objects.values_list("role__role_code", "scope_type")),
            {
                ("company_secretary", "legal_readonly"),
                ("internal_auditor", "audit_readonly"),
            },
        )

    @staticmethod
    def _create_historical_cases(apps):
        Role = apps.get_model("identity", "Role")
        User = apps.get_model("identity", "User")
        Member = apps.get_model("members", "Member")
        LoanApplication = apps.get_model("applications", "LoanApplication")
        RiskAssessment = apps.get_model("credit", "RiskAssessment")
        LoanAppraisalNote = apps.get_model("credit", "LoanAppraisalNote")
        Rule = apps.get_model("approvals", "ApprovalMatrixRule")
        Committee = apps.get_model("approvals", "SanctionCommittee")
        ApprovalCase = apps.get_model("approvals", "ApprovalCase")

        roles = {}
        for role_code in (
            "credit_manager",
            "cfo",
            "director",
            "director_2",
            "company_secretary",
            "internal_auditor",
        ):
            roles[role_code] = Role.objects.create(
                role_code=role_code,
                role_name=role_code.replace("_", " ").title(),
                status="active",
            )
        users = {}
        for role_code in ("credit_manager", "cfo", "director", "director_2"):
            users[role_code] = User.objects.create(
                full_name=roles[role_code].role_name,
                email=f"migration-{role_code}@example.test",
                status="active",
                primary_role=roles[role_code],
                password_hash="not-a-real-password",
            )

        decision_date = timezone.localdate()
        rule = Rule.objects.create(
            decision_type="loan_sanction",
            amount_min="0.00",
            amount_max="500000.00",
            required_approver_roles_json=["cfo", "director"],
            required_director_count=1,
            joint_approval_required_flag=True,
            register_required="credit_sanction_register",
            effective_from=decision_date,
            status="active",
            version_number="migration-rule-v1",
        )
        committee = Committee.objects.create(
            committee_name="Migration Committee",
            cfo_user=users["cfo"],
            director_1_user=users["director"],
            director_2_user=users["director_2"],
            board_meeting_reference="BM-MIGRATION",
            effective_from=decision_date,
            status="active",
            version_number="migration-committee-v1",
        )

        case_ids = []
        for ordinal, malformed in ((1, False), (2, True)):
            member = Member.objects.create(
                member_number=f"MIG-MEMBER-{ordinal}",
                member_type="individual_farmer",
                legal_name=f"Migration Member {ordinal}",
                display_name=f"Migration Member {ordinal}",
                membership_status="active",
                folio_number=f"MIG-FOLIO-{ordinal}",
                kyc_status="verified",
                default_status="no_default",
            )
            application = LoanApplication.objects.create(
                application_reference_number=f"MIG-APP-{ordinal}",
                member=member,
                borrower_type="individual_farmer",
                received_by_user=users["credit_manager"],
                required_loan_amount="500000.00",
                requested_tenure_months=12,
                declared_purpose="Migration acceptance",
                purpose_category="crop_production",
                current_stage="credit_assessment",
                application_status="submitted_to_sanction_committee",
                completeness_status="complete",
                terms_acceptance_flag=True,
                created_by_user=users["credit_manager"],
            )
            risk = RiskAssessment.objects.create(
                loan_application=application,
                market_risk_rating="low",
                operational_risk_rating="low",
                borrower_risk_rating="low",
                overall_risk_rating="low",
                assessed_by_user=users["credit_manager"],
            )
            calculated_at = timezone.now() - timedelta(hours=1)
            provenance = {
                "loan_limit_assessment_id": f"20000000-0000-0000-0000-00000000000{ordinal}",
                "loan_application_id": str(application.pk),
                "exception_required_flag": False,
                "calculation_rule_version": "migration-limit-v1",
                "policy_config_id": f"30000000-0000-0000-0000-00000000000{ordinal}",
                "policy_name": "Migration Policy",
                "calculated_at": calculated_at.isoformat(),
            }
            note = LoanAppraisalNote.objects.create(
                loan_application=application,
                prepared_by_user=users["credit_manager"],
                reviewed_by_user=users["credit_manager"],
                reviewed_at=timezone.now(),
                last_review_decision="reviewed",
                tat_due_at=timezone.now() + timedelta(days=1),
                tat_status="within_tat",
                eligibility_assessment_id_snapshot=f"10000000-0000-0000-0000-00000000000{ordinal}",
                loan_limit_assessment_id_snapshot=provenance["loan_limit_assessment_id"],
                eligibility_snapshot_json={"overall_result": "eligible"},
                loan_limit_snapshot_json={
                    **provenance,
                    "final_eligible_loan_amount": "500000.00",
                },
                prerequisite_provenance="verified",
                borrower_summary="Migration history",
                eligibility_summary="Eligible",
                loan_limit_summary="Within limit",
                recommended_amount="500000.00",
                recommended_tenure_months=12,
                recommended_interest_type="floating",
                recommended_security_summary="Standard security",
                repayment_capacity_notes="Adequate",
                risk_assessment=risk,
                recommendation="approve",
                appraisal_status="submitted_to_sanction_committee",
            )
            matrix_projection = {
                "approval_matrix_rule_id": str(rule.pk),
                "version_number": rule.version_number,
                "decision_type": "loan_sanction",
                "amount": "499999.99" if malformed else "500000.00",
                "amount_min": "0.00",
                "amount_max": "500000.00",
                "condition_code": None,
                "decision_date": decision_date.isoformat(),
                "required_approver_roles": ["cfo", "director"],
                "required_director_count": 1,
                "joint_approval_required": True,
                "register_required": "credit_sanction_register",
            }
            case = ApprovalCase.objects.create(
                loan_application=application,
                loan_appraisal_note=note,
                submitted_by_user=users["credit_manager"],
                submission_remarks="Migration case",
                approval_matrix_rule=rule,
                approval_matrix_rule_version=rule.version_number,
                sanction_committee=committee,
                sanction_committee_version=committee.version_number,
                required_approvers_json=[
                    {
                        "role_code": "cfo",
                        "user_id": str(users["cfo"].pk),
                        "full_name": users["cfo"].full_name,
                    },
                    {
                        "role_code": "director",
                        "user_id": str(users["director"].pk),
                        "full_name": users["director"].full_name,
                    },
                ],
                excluded_approvers_json=[],
                amount="500000.00",
                related_entity_type="loan_application",
                related_entity_id=application.pk,
                reason_for_approval="Migration approval",
                matrix_projection_json=matrix_projection,
                committee_projection_json={
                    "sanction_committee_id": str(committee.pk),
                    "version_number": committee.version_number,
                    "decision_date": decision_date.isoformat(),
                    "cfo_user_id": str(users["cfo"].pk),
                    "director_user_ids": [
                        str(users["director"].pk),
                        str(users["director_2"].pk),
                    ],
                },
                loan_limit_provenance_json=provenance,
                decision_date=decision_date,
                version=2,
            )
            case_ids.append(case.pk)

        return {
            "valid_case_id": case_ids[0],
            "malformed_case_id": case_ids[1],
            "required_user_ids": {users["cfo"].pk, users["director"].pk},
        }


class ApprovalCycleMigrationTests(TransactionTestCase):
    migrate_from = [
        ("credit", "0007_eligibility_active_member_snapshot"),
        ("approvals", "0010_approvalcasereadscopegrant_and_more"),
    ]
    migrate_to = [
        ("credit", "0007_eligibility_active_member_snapshot"),
        ("approvals", "0011_approvalcase_appraisal_facts_json_and_more"),
    ]

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_existing_cases_become_cycle_one_with_frozen_review_facts(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps
        fixtures = ApprovalReadScopeMigrationTests._create_historical_cases(old_apps)
        ApprovalCase = old_apps.get_model("approvals", "ApprovalCase")
        Review = old_apps.get_model("credit", "AppraisalReviewDecision")
        review_ids = {}
        for case in ApprovalCase.objects.order_by("submitted_at"):
            note = case.loan_appraisal_note
            review = Review.objects.create(
                loan_appraisal_note=note,
                decision="reviewed",
                review_comments="Migration-reviewed appraisal.",
                reviewer_user=case.submitted_by_user,
                decided_at=note.reviewed_at,
                from_state="review_pending",
                to_state="reviewed",
            )
            review_ids[case.pk] = review.pk

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)
        migrated_apps = executor.loader.project_state(self.migrate_to).apps
        MigratedCase = migrated_apps.get_model("approvals", "ApprovalCase")
        for case_id in (fixtures["valid_case_id"], fixtures["malformed_case_id"]):
            case = MigratedCase.objects.get(pk=case_id)
            self.assertEqual(case.cycle_number, 1)
            self.assertEqual(case.appraisal_revision, 1)
            self.assertEqual(case.appraisal_review_decision_id, review_ids[case_id])
            self.assertEqual(
                case.appraisal_facts_json["loan_amounts"]["recommended_amount"],
                "500000.00",
            )
            self.assertEqual(
                case.appraisal_facts_json["risk"]["overall_risk_rating"], "low"
            )
