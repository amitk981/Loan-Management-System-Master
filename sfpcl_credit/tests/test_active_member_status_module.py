from datetime import date
from concurrent.futures import ThreadPoolExecutor
from unittest import skipUnless
import uuid

from django.db import close_old_connections, connection
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.members.models import (
    ActiveMemberStatus,
    IndividualMemberProfile,
    Member,
    MemberChangeHistory,
    MemberServiceEvidence,
    ProducerInstitutionProfile,
    ProduceSupplyRecord,
)
from sfpcl_credit.members.modules.active_member_status import (
    ActiveMemberStatusConflict,
    ActiveMemberStatusModule,
)


class ActiveMemberStatusModuleTests(TestCase):
    def setUp(self):
        role = Role.objects.create(
            role_code="active_module_maker",
            role_name="Active Module Maker",
            status="active",
        )
        self.actor = User.objects.create(
            full_name="Synthetic Supply Maker",
            email="active-module-maker@sfpcl.example",
            status="active",
            primary_role=role,
        )
        self.member = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Synthetic Active Member",
            display_name="Synthetic Active Member",
            folio_number="FOL-ACTIVE-MODULE",
            membership_status="active",
            pan_encrypted="ABCDE1234F",
            pan_hash="active-module-pan",
            kyc_status="verified",
            default_status="no_default",
        )
        IndividualMemberProfile.objects.create(
            member=self.member,
            first_name="Synthetic",
            last_name="Member",
            services_availed_flag=True,
        )

    def _supply(self, financial_year, **overrides):
        values = {
            "member": self.member,
            "financial_year": financial_year,
            "supplied_to_entity_type": "sfpcl",
            "supply_route": "direct",
            "evidence_reference": f"ERP-{financial_year}",
            "captured_by_user": self.actor,
            "verified_flag": True,
        }
        values.update(overrides)
        return ProduceSupplyRecord.objects.create(**values)

    def test_continuity_stops_at_gaps_and_keeps_every_classified_row(self):
        for financial_year in (
            "2020-21",
            "2022-23",
            "2023-24",
            "2025-26",
            "2026-27",
            "2027-28",
        ):
            self._supply(financial_year)

        result = ActiveMemberStatusModule().calculate(
            member_id=self.member.member_id,
            as_of_date=date(2028, 3, 31),
        )

        self.assertEqual(len(result.supply_rows), 6)
        self.assertEqual(sum(row.qualifying for row in result.supply_rows), 6)
        self.assertEqual(result.continuous_supply_years, 3)
        self.assertEqual(result.member_active_check, "manual_evidence_required")

    def test_as_of_date_keeps_future_and_incomplete_rows_visible_but_non_qualifying(self):
        for financial_year in ("2021-22", "2022-23", "2023-24", "2024-25", "2025-26"):
            self._supply(financial_year)

        result = ActiveMemberStatusModule().calculate(
            member_id=self.member.member_id,
            as_of_date=date(2025, 6, 30),
        )

        self.assertEqual(result.continuous_supply_years, 4)
        future = next(row for row in result.supply_rows if row.financial_year == "2025-26")
        self.assertFalse(future.qualifying)
        self.assertEqual(future.non_qualifying_reason, "financial_year_not_complete_as_of_date")
        self.assertEqual(result.member_active_check, "pass")

    def test_verify_enforces_permission_maker_checker_reason_version_and_current_result(self):
        for financial_year in ("2022-23", "2023-24", "2024-25", "2025-26"):
            self._supply(financial_year)
        result = ActiveMemberStatusModule().calculate(
            member_id=self.member.member_id,
            as_of_date=date(2026, 3, 31),
        )
        permission = Permission.objects.create(
            permission_code="members.active_status.verify",
            permission_name="Verify active status",
            module_name="members",
            risk_level="high",
        )
        checker_role = Role.objects.create(
            role_code="active_module_checker",
            role_name="Active Module Checker",
            status="active",
        )
        RolePermission.objects.create(role=checker_role, permission=permission)
        checker = User.objects.create(
            full_name="Synthetic Status Checker",
            email="active-module-checker@sfpcl.example",
            status="active",
            primary_role=checker_role,
        )

        with self.assertRaisesRegex(PermissionError, "permission"):
            ActiveMemberStatusModule().verify(
                actor=self.actor,
                member_id=self.member.member_id,
                result_id=result.result_id,
                decision="active",
                reason="Source evidence reviewed.",
                version=self.member.version,
                as_of_date=date(2026, 3, 31),
            )
        with self.assertRaisesRegex(ValueError, "reason"):
            ActiveMemberStatusModule().verify(
                actor=checker,
                member_id=self.member.member_id,
                result_id=result.result_id,
                decision="active",
                reason=" ",
                version=self.member.version,
                as_of_date=date(2026, 3, 31),
            )
        with self.assertRaisesRegex(PermissionError, "maker"):
            RolePermission.objects.create(role=self.actor.primary_role, permission=permission)
            ActiveMemberStatusModule().verify(
                actor=self.actor,
                member_id=self.member.member_id,
                result_id=result.result_id,
                decision="active",
                reason="Self review is forbidden.",
                version=self.member.version,
                as_of_date=date(2026, 3, 31),
            )
        self.assertEqual(AuditLog.objects.filter(action="members.active_status.verified").count(), 0)
        self.assertEqual(MemberChangeHistory.objects.filter(change_type="active_status_verified").count(), 0)

        verified = ActiveMemberStatusModule().verify(
            actor=checker,
            member_id=self.member.member_id,
            result_id=result.result_id,
            decision="active",
            reason="Source evidence reviewed.",
            version=self.member.version,
            as_of_date=date(2026, 3, 31),
        )
        self.assertEqual(verified["result"], result.to_snapshot())
        self.assertEqual(verified["decision"], "active")
        self.member.refresh_from_db()
        self.assertNotEqual(str(self.member.active_member_status_id), result.result_id)
        self.assertTrue(ActiveMemberStatus.objects.filter(active_member_status_id=self.member.active_member_status_id).exists())
        self.assertEqual(AuditLog.objects.filter(action="members.active_status.verified").count(), 1)
        self.assertEqual(MemberChangeHistory.objects.filter(change_type="active_status_verified").count(), 1)

        with self.assertRaises(ActiveMemberStatusConflict):
            ActiveMemberStatusModule().verify(
                actor=checker,
                member_id=self.member.member_id,
                result_id=result.result_id,
                decision="active",
                reason="Repeated decision.",
                version=self.member.version,
                as_of_date=date(2026, 3, 31),
            )
        self.assertEqual(AuditLog.objects.filter(action="members.active_status.verified").count(), 1)

    def test_individual_three_year_service_and_recorded_one_year_relaxation_routes(self):
        profile = self.member.individual_profile
        profile.services_availed_flag = False
        profile.employment_or_service_years = "3.00"
        profile.save(update_fields=["services_availed_flag", "employment_or_service_years"])

        service_result = ActiveMemberStatusModule().calculate(member_id=self.member.member_id)
        self.assertEqual(service_result.member_active_check, "manual_evidence_required")

        profile.employment_or_service_years = "2.99"
        profile.save(update_fields=["employment_or_service_years"])
        self._supply("2025-26")
        self.member.active_member_status = "relaxation"
        self.member.active_member_verified_at = timezone.now()
        self.member.save(update_fields=["active_member_status", "active_member_verified_at"])

        relaxation = ActiveMemberStatusModule().calculate(member_id=self.member.member_id)
        self.assertEqual(relaxation.member_active_check, "manual_evidence_required")

    def test_institution_requires_services_and_four_continuous_eligible_rows(self):
        institution = Member.objects.create(
            member_type="producer_institution",
            legal_name="Synthetic Producer Institution",
            display_name="Synthetic Producer Institution",
            folio_number="FOL-INSTITUTION-MODULE",
            membership_status="active",
            pan_encrypted="ABCDE5678F",
            pan_hash="institution-module-pan",
            kyc_status="verified",
            default_status="no_default",
        )
        profile = ProducerInstitutionProfile.objects.create(
            member=institution,
            institution_type="Producer Institution",
            authorised_signatory_name="Synthetic Signatory",
            services_availed_flag=True,
        )
        for financial_year in ("2022-23", "2023-24", "2024-25", "2025-26"):
            ProduceSupplyRecord.objects.create(
                member=institution,
                financial_year=financial_year,
                supplied_to_entity_type="sfpcl",
                supply_route="direct",
                evidence_reference=f"ERP-INST-{financial_year}",
                captured_by_user=self.actor,
                verified_flag=True,
            )

        result = ActiveMemberStatusModule().calculate(member_id=institution.member_id)
        self.assertEqual(result.member_active_check, "pass")
        self.assertEqual(result.continuous_supply_years, 4)

        profile.services_availed_flag = False
        profile.save(update_fields=["services_availed_flag"])
        self.assertEqual(
            ActiveMemberStatusModule().calculate(member_id=institution.member_id).member_active_check,
            "manual_evidence_required",
        )


@skipUnless(connection.vendor == "postgresql", "Authoritative active-status race requires PostgreSQL.")
class ActiveMemberStatusVerificationConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        permission = Permission.objects.create(
            permission_code="members.active_status.verify",
            permission_name="Verify active status",
            module_name="members",
            risk_level="high",
        )
        maker_role = Role.objects.create(role_code="race_maker", role_name="Race Maker", status="active")
        self.maker = User.objects.create(
            full_name="Race Maker", email="active-race-maker@sfpcl.example",
            status="active", primary_role=maker_role,
        )
        self.checkers = []
        for suffix in ("a", "b"):
            role = Role.objects.create(
                role_code=f"race_checker_{suffix}", role_name=f"Race Checker {suffix}", status="active"
            )
            RolePermission.objects.create(role=role, permission=permission)
            self.checkers.append(User.objects.create(
                full_name=f"Race Checker {suffix}", email=f"active-race-{suffix}@sfpcl.example",
                status="active", primary_role=role,
            ))
        self.member = Member.objects.create(
            member_type="individual_farmer", legal_name="Race Member", display_name="Race Member",
            folio_number="FOL-ACTIVE-RACE", membership_status="active",
            pan_encrypted="ABCDE9876F", pan_hash="active-race-pan", kyc_status="verified",
            default_status="no_default",
        )
        IndividualMemberProfile.objects.create(
            member=self.member, first_name="Race", last_name="Member", services_availed_flag=True
        )
        for financial_year in ("2022-23", "2023-24", "2024-25", "2025-26"):
            ProduceSupplyRecord.objects.create(
                member=self.member, financial_year=financial_year,
                supplied_to_entity_type="sfpcl", supply_route="direct",
                evidence_reference=f"RACE-{financial_year}", captured_by_user=self.maker,
                verified_flag=True,
            )

    def test_two_verifiers_create_one_complete_winner_and_zero_loser_evidence(self):
        as_of = date(2026, 3, 31)
        result = ActiveMemberStatusModule().calculate(member_id=self.member.member_id, as_of_date=as_of)
        version = self.member.version

        def attempt(actor_id):
            close_old_connections()
            actor = User.objects.get(user_id=actor_id)
            try:
                value = ActiveMemberStatusModule().verify(
                    actor=actor, member_id=self.member.member_id, result_id=result.result_id,
                    decision="active", reason="Concurrent source review.", version=version,
                    as_of_date=as_of,
                )
                return "won", value
            except ActiveMemberStatusConflict as exc:
                return exc.code, None
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(attempt, [user.user_id for user in self.checkers]))

        self.assertEqual([code for code, _ in outcomes].count("won"), 1)
        self.assertEqual(AuditLog.objects.filter(action="members.active_status.verified").count(), 1)
        self.assertEqual(MemberChangeHistory.objects.filter(change_type="active_status_verified").count(), 1)
        winner = next(value for code, value in outcomes if code == "won")
        self.assertEqual(winner["result"], result.to_snapshot())
        audit = AuditLog.objects.get(action="members.active_status.verified")
        history = MemberChangeHistory.objects.get(change_type="active_status_verified")
        self.assertEqual(audit.new_value_json, winner)
        self.assertEqual(history.new_value_json, winner)


class ActiveMemberGovernanceTests(TestCase):
    def setUp(self):
        permission = Permission.objects.create(
            permission_code="members.active_status.verify", permission_name="Verify active status",
            module_name="members", risk_level="high",
        )
        maker_role = Role.objects.create(role_code="gov_maker", role_name="Governance Maker", status="active")
        checker_role = Role.objects.create(role_code="gov_checker", role_name="Governance Checker", status="active")
        RolePermission.objects.create(role=checker_role, permission=permission)
        self.maker = User.objects.create(full_name="Governance Maker", email="gov-maker@sfpcl.example", status="active", primary_role=maker_role)
        self.checkers = [User.objects.create(full_name="Governance Checker", email="gov-checker@sfpcl.example", status="active", primary_role=checker_role)]
        self.member = Member.objects.create(
            member_type="individual_farmer", legal_name="Governance Member", display_name="Governance Member",
            folio_number="FOL-GOV", membership_status="active", pan_encrypted="ABCDE4321F",
            pan_hash="governance-pan", kyc_status="verified", default_status="no_default",
        )
        IndividualMemberProfile.objects.create(member=self.member, first_name="Governance", last_name="Member", services_availed_flag=True)
        for financial_year in ("2022-23", "2023-24", "2024-25", "2025-26"):
            ProduceSupplyRecord.objects.create(
                member=self.member, financial_year=financial_year, supplied_to_entity_type="sfpcl",
                supply_route="direct", evidence_reference=f"GOV-{financial_year}",
                captured_by_user=self.maker, verified_flag=True,
            )
    def test_supply_snapshot_contains_every_review_input(self):
        record = ProduceSupplyRecord.objects.create(
            member=self.member, financial_year="2025-26",
            supplied_to_entity_type="subsidiary", supplied_to_entity_id=uuid.uuid4(),
            supply_route="direct", evidence_reference="ERP-COMPLETE",
            captured_by_user=self.maker, verified_flag=True,
            verified_by_user=self.checkers[0], verified_at=timezone.now(),
        )
        rows = ActiveMemberStatusModule().calculate(
            member_id=self.member.member_id, as_of_date=date(2026, 3, 31)
        ).to_snapshot()["supply_rows"]
        row = next(item for item in rows if item["produce_supply_record_id"] == str(record.produce_supply_record_id))
        self.assertEqual(row["produce_supply_record_id"], str(record.produce_supply_record_id))
        self.assertEqual(row["supplied_to_entity_type"], "subsidiary")
        self.assertEqual(row["supplied_to_entity_id"], str(record.supplied_to_entity_id))
        self.assertEqual(row["supply_route"], "direct")
        self.assertEqual(row["evidence_reference"], "ERP-COMPLETE")
        self.assertEqual(row["verified_by_user_id"], str(self.checkers[0].user_id))
        self.assertIsNotNone(row["verified_at"])

    def test_service_scalar_cannot_grant_br006_without_dated_evidence(self):
        profile = self.member.individual_profile
        profile.employment_or_service_years = "3.00"
        profile.services_availed_flag = False
        profile.save(update_fields=["employment_or_service_years", "services_availed_flag"])
        unsupported = ActiveMemberStatusModule().calculate(member_id=self.member.member_id)
        self.assertEqual(unsupported.member_active_check, "manual_evidence_required")
        MemberServiceEvidence.objects.create(
            member=self.member, service_type="employment", recipient_entity_type="sfpcl",
            service_from=date(2023, 3, 31), service_to=date(2026, 3, 31),
            evidence_reference="HR-SYNTHETIC-001", verified_by_user=self.checkers[0],
            verified_at=timezone.now(),
        )
        supported = ActiveMemberStatusModule().calculate(
            member_id=self.member.member_id, as_of_date=date(2026, 3, 31)
        )
        self.assertEqual(supported.member_active_check, "relaxation")
        self.assertEqual(supported.qualification_route, "three_year_service")

    def test_verify_persists_effective_record_and_member_points_to_its_primary_key(self):
        result = ActiveMemberStatusModule().calculate(
            member_id=self.member.member_id, as_of_date=date(2026, 3, 31)
        )
        verified = ActiveMemberStatusModule().verify(
            actor=self.checkers[0], member_id=self.member.member_id, result_id=result.result_id,
            decision="active", reason="Complete source evidence reviewed.",
            version=self.member.version, as_of_date=date(2026, 3, 31),
        )
        effective = ActiveMemberStatus.objects.get()
        self.member.refresh_from_db()
        self.assertEqual(self.member.active_member_status_id, effective.active_member_status_id)
        self.assertNotEqual(str(effective.active_member_status_id), result.result_id)
        self.assertEqual(effective.evidence_snapshot, result.to_snapshot())
        self.assertEqual(verified["active_member_status_id"], str(effective.active_member_status_id))
