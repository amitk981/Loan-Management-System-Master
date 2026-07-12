from dataclasses import dataclass
from datetime import date, timedelta
import hashlib
import json
import uuid

from django.db import transaction
from django.utils import timezone

from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.members.models import (
    ActiveMemberStatus,
    Member,
    MemberChangeHistory,
    MemberServiceEvidence,
    ProduceSupplyRecord,
)
from sfpcl_credit.members.modules.member_authority import evaluate_member_authority


QUALIFYING_ENTITY_TYPES = frozenset({"sfpcl", "subsidiary", "step_down_subsidiary"})
QUALIFYING_ROUTES = frozenset({"direct", "producer_institution"})
VERIFY_PERMISSION = "members.active_status.verify"


class ActiveMemberStatusConflict(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


class ActiveMemberObjectAccessDenied(Exception):
    pass


@dataclass(frozen=True)
class SupplyRowProjection:
    produce_supply_record_id: str
    financial_year: str
    supplied_to_entity_type: str
    supplied_to_entity_id: str | None
    supply_route: str
    producer_institution_member_id: str | None
    evidence_reference: str
    verified_by_user_id: str | None
    verified_at: str | None
    verified: bool
    qualifying: bool
    non_qualifying_reason: str | None


@dataclass(frozen=True)
class ServiceEvidenceProjection:
    member_service_evidence_id: str
    service_type: str
    service_from: str
    service_to: str
    recipient_entity_type: str
    recipient_entity_id: str | None
    evidence_reference: str
    verified_by_user_id: str
    verified_at: str


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
    service_evidence_rows: tuple[ServiceEvidenceProjection, ...]
    relaxation_evidence: dict | None

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
            "service_evidence_rows": [row.__dict__ for row in self.service_evidence_rows],
            "relaxation_evidence": self.relaxation_evidence,
        }


class ActiveMemberStatusModule:
    """Public member-owned projection for BR-004/BR-007 evidence."""

    def calculate(self, *, member_id, as_of_date=None, lock_evidence=False):
        calculated_as_of_date = as_of_date or timezone.localdate()
        member = (
            Member.objects.select_related("individual_profile", "producer_institution_profile")
            .filter(member_id=member_id, is_deleted=False)
            .first()
        )
        if member is None:
            raise Member.DoesNotExist("Member was not found.")
        services_availed = self._services_availed(member)
        supply_query = member.produce_supply_records.select_related("producer_institution_member")
        service_query = member.service_evidence.order_by("service_from", "member_service_evidence_id")
        if lock_evidence:
            supply_query = supply_query.select_for_update(of=("self",))
            service_query = service_query.select_for_update()
        rows = tuple(
            self._project_row(row, calculated_as_of_date)
            for row in supply_query.all()
        )
        service_rows = tuple(self._project_service_evidence(row) for row in service_query.all())
        qualifying_service_rows = tuple(
            row for row in service_rows if self._service_evidence_qualifies(row, calculated_as_of_date)
        )
        relaxation_evidence = next(
            (row.__dict__ for row in qualifying_service_rows if row.service_type == "relaxation"), None
        )
        qualifying_years = [row.financial_year for row in rows if row.qualifying]
        continuity = longest_continuous_financial_years(qualifying_years)
        if member.membership_status != "active":
            return self._result(
                member, calculated_as_of_date, "fail", "ineligible",
                f"BR-003 requires active member status or relaxation evidence; member status is {member.membership_status}.",
                services_availed, continuity, None, rows, qualifying_service_rows, relaxation_evidence,
            )
        if services_availed and continuity >= 4:
            return self._result(
                member, calculated_as_of_date, "pass", "pending",
                "Active-member status is supported by services availed and four continuous verified financial years of qualifying produce supply. Default, document, terms, purpose, and nominee checks are pending.",
                services_availed, continuity, "four_year_supply", rows, qualifying_service_rows, relaxation_evidence,
            )
        employment_years = self._employment_or_service_years(member)
        service_evidence = next((row for row in qualifying_service_rows if row.service_type != "relaxation"), None)
        if member.member_type == "individual_farmer" and service_evidence is not None:
            return self._result(
                member, calculated_as_of_date, "relaxation", "pending",
                "BR-006 active-member status is supported by three continuous years of recorded employment or service.",
                services_availed, continuity, "three_year_service", rows, qualifying_service_rows, relaxation_evidence,
            )
        if (
            relaxation_evidence is not None
            and continuity >= 1
        ):
            return self._result(
                member, calculated_as_of_date, "relaxation", "pending",
                "Recorded one-year active-member relaxation is supported by qualifying verified produce supply evidence.",
                services_availed, continuity, "recorded_one_year_relaxation", rows, qualifying_service_rows, relaxation_evidence,
            )
        return self._result(
            member, calculated_as_of_date, "manual_evidence_required", "pending_manual_evidence",
            "BR-004 through BR-007 require persisted service usage and continuous qualifying verified supply history or relaxation evidence; manual evidence is required.",
            services_availed, continuity, None, rows, qualifying_service_rows, relaxation_evidence,
        )

    @transaction.atomic
    def verify(self, *, actor, member_id, result_id, decision, reason, version, as_of_date=None):
        if as_of_date is None:
            raise ValueError("as_of_date is required.")
        if as_of_date > timezone.localdate():
            raise ValueError("as_of_date cannot be in the future.")
        if VERIFY_PERMISSION not in auth_service.effective_permission_codes(actor):
            raise PermissionError("You do not have permission to verify active-member status.")
        if decision not in {"active", "inactive", "relaxation"}:
            raise ValueError("decision must be active, inactive, or relaxation.")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("A verification reason is required.")
        member = Member.objects.select_for_update().filter(
            member_id=member_id, is_deleted=False
        ).first()
        if member is None:
            raise ActiveMemberObjectAccessDenied("You cannot access this member.")
        access = evaluate_member_authority(
            actor_user=actor, member=member, permission=VERIFY_PERMISSION
        )
        if not access.allowed:
            raise ActiveMemberObjectAccessDenied("You cannot access this member.")
        if version != member.version:
            raise ActiveMemberStatusConflict("STALE_WRITE", "Member has changed; refresh and retry.")
        current = self.calculate(member_id=member.member_id, as_of_date=as_of_date, lock_evidence=True)
        if str(result_id) != current.result_id:
            raise ActiveMemberStatusConflict("STALE_RESULT", "Active-member result has changed; recalculate before verifying.")
        prior = ActiveMemberStatus.objects.select_for_update().filter(
            member=member, effective_to__isnull=True
        ).first()
        if prior is not None and as_of_date <= prior.effective_from:
            raise ActiveMemberStatusConflict(
                "INVALID_EFFECTIVE_DATE", "A new active-member decision must start after the current decision."
            )
        if ActiveMemberStatus.objects.filter(
            member=member, effective_to__isnull=True, result_id=current.result_id
        ).exists():
            raise ActiveMemberStatusConflict("INVALID_STATE_TRANSITION", "This active-member result is already verified.")
        qualifying_ids = [row.produce_supply_record_id for row in current.supply_rows if row.qualifying]
        if ProduceSupplyRecord.objects.filter(
            produce_supply_record_id__in=qualifying_ids,
            captured_by_user=actor,
        ).exists():
            raise PermissionError("The evidence maker cannot verify this active-member result.")
        if decision == "active" and current.member_active_check not in {"pass", "relaxation"}:
            raise ActiveMemberStatusConflict("INVALID_DECISION", "The dated evidence result does not support an active decision.")
        if decision == "relaxation" and current.continuous_supply_years < 1:
            raise ActiveMemberStatusConflict(
                "INVALID_DECISION", "A relaxation requires at least one complete qualifying supply year."
            )
        if decision == "relaxation" and current.relaxation_evidence is None:
            raise ActiveMemberStatusConflict(
                "MISSING_RELAXATION_EVIDENCE", "A relaxation requires distinct persisted source evidence."
            )

        old_projection = {
            "active_member_status_id": str(member.active_member_status_id) if member.active_member_status_id else None,
            "active_member_status": member.active_member_status or None,
            "version": member.version,
        }
        instant = timezone.now()
        if prior is not None:
            prior.effective_to = as_of_date - timedelta(days=1)
            prior.save(update_fields=["effective_to"])
        snapshot = current.to_snapshot()
        entity_types = {
            row.supplied_to_entity_type for row in current.supply_rows if row.qualifying
        }
        effective = ActiveMemberStatus.objects.create(
            member=member, result_id=current.result_id, status=decision,
            member_type=current.member_type, services_availed_flag=current.services_availed,
            continuous_supply_years=current.continuous_supply_years,
            supplied_to_company_flag="sfpcl" in entity_types,
            supplied_to_subsidiary_flag="subsidiary" in entity_types,
            supplied_to_stepdown_flag="step_down_subsidiary" in entity_types,
            supplied_through_producer_institution_flag=any(
                row.qualifying and row.supply_route == "producer_institution" for row in current.supply_rows
            ),
            employment_service_years=current.employment_or_service_years,
            relaxation_reason=reason.strip() if decision == "relaxation" else "",
            evidence_summary=reason.strip(), evidence_snapshot=snapshot,
            verified_by_user=actor, verified_at=instant, effective_from=as_of_date,
        )
        member.active_member_status_id = effective.active_member_status_id
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
            "active_member_status_id": str(effective.active_member_status_id),
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
    def _result(member, as_of_date, active_check, overall_result, notes, services, continuity, route, rows, service_rows, relaxation_evidence):
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
            "service_evidence_rows": [row.__dict__ for row in service_rows],
            "relaxation_evidence": relaxation_evidence,
        }
        digest = hashlib.sha256(
            json.dumps(projection, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        result_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"sfpcl-active-member:{digest}"))
        return ActiveMemberStatusResult(result_id=result_id, supply_rows=rows, service_evidence_rows=service_rows, **{
            key: value for key, value in projection.items() if key not in {"supply_rows", "service_evidence_rows"}
        })

    @staticmethod
    def _project_service_evidence(record):
        return ServiceEvidenceProjection(
            member_service_evidence_id=str(record.member_service_evidence_id),
            service_type=record.service_type, service_from=record.service_from.isoformat(),
            service_to=record.service_to.isoformat(), recipient_entity_type=record.recipient_entity_type,
            recipient_entity_id=str(record.recipient_entity_id) if record.recipient_entity_id else None,
            evidence_reference=record.evidence_reference,
            verified_by_user_id=str(record.verified_by_user_id), verified_at=record.verified_at.isoformat(),
        )

    @staticmethod
    def _service_evidence_qualifies(row, as_of_date):
        try:
            threshold = as_of_date.replace(year=as_of_date.year - 3)
        except ValueError:
            threshold = as_of_date.replace(year=as_of_date.year - 3, day=28)
        if row.service_type == "relaxation":
            threshold = as_of_date
        return (
            row.recipient_entity_type in QUALIFYING_ENTITY_TYPES
            and date.fromisoformat(row.service_from) <= threshold
            and date.fromisoformat(row.service_to) >= as_of_date
            and bool(row.evidence_reference.strip())
        )

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
    def _qualifying_service_evidence(member, as_of_date):
        try:
            threshold = as_of_date.replace(year=as_of_date.year - 3)
        except ValueError:
            threshold = as_of_date.replace(year=as_of_date.year - 3, day=28)
        return MemberServiceEvidence.objects.filter(
            member=member, recipient_entity_type__in=QUALIFYING_ENTITY_TYPES,
            service_from__lte=threshold, service_to__gte=as_of_date,
            verified_at__isnull=False,
        ).exclude(evidence_reference="").order_by("service_from").first()

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
            produce_supply_record_id=str(record.produce_supply_record_id),
            financial_year=record.financial_year,
            supplied_to_entity_type=record.supplied_to_entity_type,
            supplied_to_entity_id=str(record.supplied_to_entity_id) if record.supplied_to_entity_id else None,
            supply_route=record.supply_route,
            producer_institution_member_id=(
                str(record.producer_institution_member_id) if record.producer_institution_member_id else None
            ),
            evidence_reference=record.evidence_reference,
            verified_by_user_id=str(record.verified_by_user_id) if record.verified_by_user_id else None,
            verified_at=record.verified_at.isoformat() if record.verified_at else None,
            verified=record.verified_flag, qualifying=reason is None, non_qualifying_reason=reason,
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
