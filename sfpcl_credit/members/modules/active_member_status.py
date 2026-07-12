from dataclasses import dataclass
from datetime import date
import hashlib
import json
import uuid

from django.db import transaction
from django.utils import timezone

from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.members.models import Member, MemberChangeHistory, ProduceSupplyRecord


QUALIFYING_ENTITY_TYPES = frozenset({"sfpcl", "subsidiary", "step_down_subsidiary"})
QUALIFYING_ROUTES = frozenset({"direct", "producer_institution"})
VERIFY_PERMISSION = "members.active_status.verify"


class ActiveMemberStatusConflict(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class SupplyRowProjection:
    produce_supply_record_id: str
    financial_year: str
    verified: bool
    qualifying: bool
    non_qualifying_reason: str | None


@dataclass(frozen=True)
class ActiveMemberStatusResult:
    result_id: str
    calculated_as_of_date: str
    member_type: str
    member_active_check: str
    overall_result: str
    assessment_notes: str
    services_availed: bool
    employment_or_service_years: str | None
    continuous_supply_years: int
    qualification_route: str | None
    supply_rows: tuple[SupplyRowProjection, ...]

    def to_snapshot(self):
        return {
            "result_id": self.result_id,
            "calculated_as_of_date": self.calculated_as_of_date,
            "member_type": self.member_type,
            "member_active_check": self.member_active_check,
            "overall_result": self.overall_result,
            "assessment_notes": self.assessment_notes,
            "services_availed": self.services_availed,
            "employment_or_service_years": self.employment_or_service_years,
            "continuous_supply_years": self.continuous_supply_years,
            "qualification_route": self.qualification_route,
            "supply_rows": [row.__dict__ for row in self.supply_rows],
        }


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
            self._project_row(row, calculated_as_of_date)
            for row in member.produce_supply_records.select_related("producer_institution_member").all()
        )
        qualifying_years = [row.financial_year for row in rows if row.qualifying]
        continuity = longest_continuous_financial_years(qualifying_years)
        if member.membership_status != "active":
            return self._result(
                member, calculated_as_of_date, "fail", "ineligible",
                f"BR-003 requires active member status or relaxation evidence; member status is {member.membership_status}.",
                services_availed, continuity, None, rows,
            )
        if services_availed and continuity >= 4:
            return self._result(
                member, calculated_as_of_date, "pass", "pending",
                "Active-member status is supported by services availed and four continuous verified financial years of qualifying produce supply. Default, document, terms, purpose, and nominee checks are pending.",
                services_availed, continuity, "four_year_supply", rows,
            )
        employment_years = self._employment_or_service_years(member)
        if member.member_type == "individual_farmer" and employment_years is not None and employment_years >= 3:
            return self._result(
                member, calculated_as_of_date, "relaxation", "pending",
                "BR-006 active-member status is supported by three continuous years of recorded employment or service.",
                services_availed, continuity, "three_year_service", rows,
            )
        if (
            member.active_member_status == "relaxation"
            and member.active_member_verified_at
            and continuity >= 1
        ):
            return self._result(
                member, calculated_as_of_date, "relaxation", "pending",
                "Recorded one-year active-member relaxation is supported by qualifying verified produce supply evidence.",
                services_availed, continuity, "recorded_one_year_relaxation", rows,
            )
        return self._result(
            member, calculated_as_of_date, "manual_evidence_required", "pending_manual_evidence",
            "BR-004 through BR-007 require persisted service usage and continuous qualifying verified supply history or relaxation evidence; manual evidence is required.",
            services_availed, continuity, None, rows,
        )

    @transaction.atomic
    def verify(self, *, actor, member_id, result_id, decision, reason, version, as_of_date=None):
        if VERIFY_PERMISSION not in auth_service.effective_permission_codes(actor):
            raise PermissionError("You do not have permission to verify active-member status.")
        if decision not in {"active", "inactive", "needs_review"}:
            raise ValueError("decision must be active, inactive, or needs_review.")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("A verification reason is required.")
        member = Member.objects.select_for_update().filter(
            member_id=member_id, is_deleted=False
        ).first()
        if member is None:
            raise Member.DoesNotExist("Member was not found.")
        if version != member.version:
            raise ActiveMemberStatusConflict("STALE_WRITE", "Member has changed; refresh and retry.")
        current = self.calculate(member_id=member.member_id, as_of_date=as_of_date)
        if str(result_id) != current.result_id:
            raise ActiveMemberStatusConflict("STALE_RESULT", "Active-member result has changed; recalculate before verifying.")
        if member.active_member_status_id == uuid.UUID(current.result_id):
            raise ActiveMemberStatusConflict("INVALID_STATE_TRANSITION", "This active-member result is already verified.")
        qualifying_ids = [row.produce_supply_record_id for row in current.supply_rows if row.qualifying]
        if ProduceSupplyRecord.objects.filter(
            produce_supply_record_id__in=qualifying_ids,
            captured_by_user=actor,
        ).exists():
            raise PermissionError("The evidence maker cannot verify this active-member result.")
        if decision == "active" and current.member_active_check not in {"pass", "relaxation"}:
            raise ActiveMemberStatusConflict("INVALID_DECISION", "The dated evidence result does not support an active decision.")

        old_projection = {
            "active_member_status_id": str(member.active_member_status_id) if member.active_member_status_id else None,
            "active_member_status": member.active_member_status or None,
            "version": member.version,
        }
        instant = timezone.now()
        member.active_member_status_id = uuid.UUID(current.result_id)
        member.active_member_status = decision
        member.active_member_verified_at = instant
        member.updated_at = instant
        member.updated_by_user = actor
        member.version += 1
        member.save(update_fields=[
            "active_member_status_id", "active_member_status", "active_member_verified_at",
            "updated_at", "updated_by_user", "version",
        ])
        verification = {
            "member_id": str(member.member_id),
            "decision": decision,
            "reason": reason.strip(),
            "verified_by_user_id": str(actor.user_id),
            "verified_at": instant.isoformat(),
            "version": member.version,
            "result": current.to_snapshot(),
        }
        MemberChangeHistory.objects.create(
            member=member,
            actor_user=actor,
            change_type="active_status_verified",
            changed_fields=["active_member_status"],
            old_value_json=old_projection,
            new_value_json=verification,
            reason=reason.strip(),
        )
        AuditLog.objects.create(
            actor_user=actor,
            action="members.active_status.verified",
            entity_type="member",
            entity_id=member.member_id,
            old_value_json=old_projection,
            new_value_json=verification,
        )
        return verification

    @staticmethod
    def _result(member, as_of_date, active_check, overall_result, notes, services, continuity, route, rows):
        employment_years = ActiveMemberStatusModule._employment_or_service_years(member)
        projection = {
            "calculated_as_of_date": as_of_date.isoformat(),
            "member_type": member.member_type,
            "member_active_check": active_check,
            "overall_result": overall_result,
            "assessment_notes": notes,
            "services_availed": services,
            "employment_or_service_years": str(employment_years) if employment_years is not None else None,
            "continuous_supply_years": continuity,
            "qualification_route": route,
            "supply_rows": [row.__dict__ for row in rows],
        }
        digest = hashlib.sha256(
            json.dumps(projection, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        result_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"sfpcl-active-member:{digest}"))
        return ActiveMemberStatusResult(result_id=result_id, supply_rows=rows, **{
            key: value for key, value in projection.items() if key != "supply_rows"
        })

    @staticmethod
    def _services_availed(member):
        if member.member_type == "individual_farmer":
            profile = getattr(member, "individual_profile", None)
        else:
            profile = getattr(member, "producer_institution_profile", None)
        return bool(profile and profile.services_availed_flag)

    @staticmethod
    def _employment_or_service_years(member):
        if member.member_type != "individual_farmer":
            return None
        profile = getattr(member, "individual_profile", None)
        return profile.employment_or_service_years if profile else None

    @staticmethod
    def _project_row(record, as_of_date):
        reason = None
        if not record.verified_flag:
            reason = "pending_verification"
        elif canonical_financial_year_start(record.financial_year) is None:
            reason = "malformed_financial_year"
        elif financial_year_end(record.financial_year) > as_of_date:
            reason = "financial_year_not_complete_as_of_date"
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


def financial_year_end(value):
    start = canonical_financial_year_start(value)
    return date.max if start is None else date(start + 1, 3, 31)


def longest_continuous_financial_years(values):
    starts = {start for value in values if (start := canonical_financial_year_start(value)) is not None}
    return max((length for start in starts for length in [_continuous_run(starts, start)]), default=0)


def _continuous_run(starts, start):
    length = 0
    while start + length in starts:
        length += 1
    return length
