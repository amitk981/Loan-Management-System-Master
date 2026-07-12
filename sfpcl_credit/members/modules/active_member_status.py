from dataclasses import dataclass

from django.utils import timezone

from sfpcl_credit.members.models import Member, ProduceSupplyRecord


QUALIFYING_ENTITY_TYPES = frozenset({"sfpcl", "subsidiary", "step_down_subsidiary"})
QUALIFYING_ROUTES = frozenset({"direct", "producer_institution"})


@dataclass(frozen=True)
class SupplyRowProjection:
    produce_supply_record_id: str
    financial_year: str
    verified: bool
    qualifying: bool
    non_qualifying_reason: str | None


@dataclass(frozen=True)
class ActiveMemberStatusResult:
    calculated_as_of_date: str
    member_active_check: str
    overall_result: str
    assessment_notes: str
    services_availed: bool
    continuous_supply_years: int
    supply_rows: tuple[SupplyRowProjection, ...]


class ActiveMemberStatusModule:
    """Public member-owned projection for BR-004/BR-007 evidence."""

    def calculate(self, *, member_id, as_of_date=None):
        calculated_as_of_date = as_of_date or timezone.localdate()
        member = (
            Member.objects.select_related("individual_profile", "producer_institution_profile")
            .filter(member_id=member_id, is_deleted=False)
            .first()
        )
        if member is None:
            raise Member.DoesNotExist("Member was not found.")
        services_availed = self._services_availed(member)
        rows = tuple(
            self._project_row(row)
            for row in member.produce_supply_records.select_related("producer_institution_member").all()
        )
        qualifying_years = [row.financial_year for row in rows if row.qualifying]
        continuity = longest_continuous_financial_years(qualifying_years)
        if member.membership_status != "active":
            return ActiveMemberStatusResult(
                calculated_as_of_date.isoformat(), "fail", "ineligible",
                f"BR-003 requires active member status or relaxation evidence; member status is {member.membership_status}.",
                services_availed, continuity, rows,
            )
        if services_availed and continuity >= 4:
            return ActiveMemberStatusResult(
                calculated_as_of_date.isoformat(), "pass", "pending",
                "Active-member status is supported by services availed and four continuous verified financial years of qualifying produce supply. Default, document, terms, purpose, and nominee checks are pending.",
                services_availed, continuity, rows,
            )
        if member.active_member_status == "relaxation" and member.active_member_verified_at:
            return ActiveMemberStatusResult(
                calculated_as_of_date.isoformat(), "relaxation", "pending_manual_evidence",
                "Active-member relaxation is recorded on the member profile. Manual evidence remains reviewable for BR-004 through BR-007.",
                services_availed, continuity, rows,
            )
        return ActiveMemberStatusResult(
            calculated_as_of_date.isoformat(), "manual_evidence_required", "pending_manual_evidence",
            "BR-004 through BR-007 require persisted service usage and continuous qualifying verified supply history or relaxation evidence; manual evidence is required.",
            services_availed, continuity, rows,
        )

    @staticmethod
    def _services_availed(member):
        if member.member_type == "individual_farmer":
            profile = getattr(member, "individual_profile", None)
        else:
            profile = getattr(member, "producer_institution_profile", None)
        return bool(profile and profile.services_availed_flag)

    @staticmethod
    def _project_row(record):
        reason = None
        if not record.verified_flag:
            reason = "pending_verification"
        elif canonical_financial_year_start(record.financial_year) is None:
            reason = "malformed_financial_year"
        elif record.supplied_to_entity_type not in QUALIFYING_ENTITY_TYPES:
            reason = "ineligible_entity"
        elif record.supply_route not in QUALIFYING_ROUTES:
            reason = "ineligible_route"
        elif record.supply_route == "direct" and record.producer_institution_member_id:
            reason = "inconsistent_direct_route"
        elif record.supply_route == "producer_institution" and not _eligible_producer_institution(record):
            reason = "ineligible_producer_institution_route"
        elif not record.evidence_reference.strip():
            reason = "missing_evidence_reference"
        return SupplyRowProjection(
            str(record.produce_supply_record_id), record.financial_year,
            record.verified_flag, reason is None, reason,
        )


def _eligible_producer_institution(record):
    routed = record.producer_institution_member
    return bool(
        routed
        and routed.member_id != record.member_id
        and routed.member_type in {"fpc", "producer_institution"}
        and routed.membership_status == "active"
        and not routed.is_deleted
    )


def canonical_financial_year_start(value):
    if not isinstance(value, str) or len(value) != 7 or value[4] != "-":
        return None
    try:
        start = int(value[:4])
    except ValueError:
        return None
    return start if value[5:] == str((start + 1) % 100).zfill(2) else None


def longest_continuous_financial_years(values):
    starts = {start for value in values if (start := canonical_financial_year_start(value)) is not None}
    return max((sum(1 for offset in range(len(starts)) if start + offset in starts) for start in starts), default=0)
