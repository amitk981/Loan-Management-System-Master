"""Immutable Credit Sanction Register generation and read projections."""

from datetime import date
from math import ceil
import re

from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone

from sfpcl_credit.approvals.models import (
    ApprovalCase,
    CreditSanctionRegisterEntry,
    ExceptionRegisterEntry,
    SanctionDecision,
)
from sfpcl_credit.approvals.modules import approval_case_engine
from sfpcl_credit.domain_errors import DomainObjectAccessDenied
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules.object_permissions import ObjectAccessResult


REGISTER_READ_PERMISSION = "approvals.sanction_register.read"
SANCTION_READ_PERMISSION = "approvals.sanction.read"
_LIST_PARAMS = {"page", "page_size", "financial_year", "decision"}
_FINANCIAL_YEAR = re.compile(r"^FY(?P<start>\d{4})-(?P<end>\d{2})$")


def generate_for_terminal_case(
    *, actor, case, sanction_decision, workflow_event, communication, request_meta=None
):
    """Freeze the 15-field source projection for one approved/rejected case."""
    if case.current_status not in {
        ApprovalCase.STATUS_APPROVED,
        ApprovalCase.STATUS_REJECTED,
    }:
        raise ValidationError("Only terminal sanction decisions can be registered.")
    decision = (
        CreditSanctionRegisterEntry.DECISION_SANCTIONED
        if case.current_status == ApprovalCase.STATUS_APPROVED
        else CreditSanctionRegisterEntry.DECISION_REJECTED
    )
    if (decision == CreditSanctionRegisterEntry.DECISION_SANCTIONED) != bool(
        sanction_decision
    ):
        raise ValidationError("Sanction decision linkage does not match the case outcome.")

    case = (
        ApprovalCase.objects.select_related(
            "general_meeting_approval",
        )
        .prefetch_related("actions")
        .get(pk=case.pk)
    )
    authority = approval_case_engine.serialize_case_authority(case)
    terminal_facts = approval_case_engine.validated_frozen_terminal_facts(case)
    action_rows = authority["approval_actions"]
    exception = _case_exception(case)
    meeting = case.general_meeting_approval
    defaults = {
        "loan_application_id": case.loan_application_id,
        "member_id": terminal_facts["member_id"],
        "sanction_decision": sanction_decision,
        "workflow_event": workflow_event,
        "application_number": terminal_facts["application_number"],
        "borrower_name": terminal_facts["borrower_name"],
        "borrower_type": terminal_facts["borrower_type"],
        "requested_amount": terminal_facts["requested_amount"],
        "eligible_amount": terminal_facts["eligible_amount"],
        "recommended_amount": terminal_facts["recommended_amount"],
        "source_review_facts_json": terminal_facts["review_facts"],
        "terminal_facts_json": {
            "rejection_reason": (
                case.reason_for_rejection
                if decision == CreditSanctionRegisterEntry.DECISION_REJECTED
                else None
            ),
            "conditions": (
                sanction_decision.conditions_precedent or None
                if sanction_decision else None
            ),
        },
        "sanctioned_amount": (
            sanction_decision.sanctioned_amount if sanction_decision else None
        ),
        "authority_applied_summary": _authority_summary(
            authority["required_approvers"]
        ),
        "approver_names_json": [
            row["full_name"]
            for row in action_rows
            if row["decision"] in {"approved", "rejected"}
        ],
        "approver_decisions_json": [
            {
                "approval_action_id": row["approval_action_id"],
                "user_id": row["user_id"],
                "full_name": row["full_name"],
                "role_code": row["role_code"],
                "decision": row["decision"],
                "comments": row["comments"],
                "acted_at": row["acted_at"],
            }
            for row in action_rows
            if row["decision"] in {"approved", "rejected"}
        ],
        "approval_date": timezone.localdate(case.closed_at),
        "decision": decision,
        "reasons": (
            case.reason_for_approval
            if decision == CreditSanctionRegisterEntry.DECISION_SANCTIONED
            else case.reason_for_rejection
        ),
        "exception_reference_json": _exception_reference(exception, case),
        "conflict_abstention_details_json": _conflict_details(case, action_rows),
        "general_meeting_approval_reference_json": _meeting_reference(meeting),
        "communication_json": {
            "communication_id": str(communication.pk),
            "status": communication.delivery_status,
            "sent_at": (
                communication.sent_at.isoformat().replace("+00:00", "Z")
                if communication.sent_at else None
            ),
        },
        "recorded_by_user": actor,
    }
    entry, created = CreditSanctionRegisterEntry.objects.get_or_create(
        approval_case=case, defaults=defaults
    )
    if not created:
        return entry

    request_meta = request_meta or {}
    AuditLog.objects.create(
        actor_user=actor,
        action="credit_sanction_register.created",
        entity_type="credit_sanction_register_entry",
        entity_id=entry.pk,
        old_value_json={},
        new_value_json={
            "approval_case_id": str(case.pk),
            "cycle_number": case.cycle_number,
            "loan_application_id": str(case.loan_application_id),
            "sanction_decision_id": (
                str(sanction_decision.pk) if sanction_decision else None
            ),
            "workflow_event_id": str(workflow_event.pk),
            "decision": decision,
            "request_id": request_meta.get("request_id"),
        },
        ip_address=request_meta.get("ip_address", ""),
        user_agent=request_meta.get("user_agent", ""),
    )
    return entry


def get_sanction_decision(*, actor, application_id, actor_permissions):
    cases, _ = approval_case_engine.select_readable_approval_cases(
        actor=actor,
        actor_permissions=actor_permissions,
    )
    application_cases = cases.filter(loan_application_id=application_id)
    if not application_cases.exists():
        raise DomainObjectAccessDenied(
            ObjectAccessResult(
                allowed=False,
                reason="sanction_decision_not_attributable",
                error_code="OBJECT_ACCESS_DENIED",
                required_permission=SANCTION_READ_PERMISSION,
            )
        )
    decision = SanctionDecision.objects.select_related("approval_case").get(
        loan_application_id=application_id,
        approval_case__in=application_cases,
    )
    return serialize_sanction_decision(decision)


def serialize_sanction_decision(decision):
    return {
        "sanction_decision_id": str(decision.pk),
        "decision": decision.decision,
        "sanctioned_amount": _money(decision.sanctioned_amount),
        "sanctioned_tenure_months": decision.sanctioned_tenure_months,
        "interest_rate_type": decision.interest_rate_type or None,
        "interest_rate_value": _rate(decision.interest_rate_value),
        "repayment_date": (
            decision.repayment_date.isoformat() if decision.repayment_date else None
        ),
        "penal_interest_rate": _rate(decision.penal_interest_rate),
        "charges": decision.charges_json,
        "security_required_summary": decision.security_required_summary,
        "conditions_precedent": decision.conditions_precedent or None,
        "decision_reason": decision.decision_reason,
    }


def list_entries(*, actor, query_params, actor_permissions, include_totals=False):
    unknown = set(query_params.keys()) - _LIST_PARAMS
    if unknown:
        raise ValidationError(
            {field: "Unknown query parameter." for field in sorted(unknown)}
        )
    page = _positive_int("page", query_params.get("page"), 1)
    page_size = min(_positive_int("page_size", query_params.get("page_size"), 20), 100)
    decision = query_params.get("decision")
    if decision and decision not in {
        CreditSanctionRegisterEntry.DECISION_SANCTIONED,
        CreditSanctionRegisterEntry.DECISION_REJECTED,
    }:
        raise ValidationError({"decision": "Unknown sanction decision."})
    cases, _ = approval_case_engine.select_readable_approval_cases(
        actor=actor,
        actor_permissions=actor_permissions,
    )
    queryset = CreditSanctionRegisterEntry.objects.filter(approval_case__in=cases)
    financial_year = query_params.get("financial_year")
    if financial_year:
        start, end = _financial_year_dates(financial_year)
        queryset = queryset.filter(approval_date__gte=start, approval_date__lt=end)
    if decision:
        queryset = queryset.filter(decision=decision)
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    rows = [serialize_entry(row) for row in queryset[offset : offset + page_size]]
    pagination = {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }
    if include_totals:
        sanctioned_total = queryset.aggregate(value=Sum("sanctioned_amount"))["value"]
        pagination["totals"] = {
            "sanctioned_amount": f"{(sanctioned_total or 0):.2f}",
        }
    return rows, pagination


def serialize_entry(entry):
    source_facts = (
        entry.source_review_facts_json
        if isinstance(entry.source_review_facts_json, dict)
        else {}
    )
    borrower_facts = source_facts.get("borrower")
    borrower_facts = borrower_facts if isinstance(borrower_facts, dict) else {}
    terminal_facts = (
        entry.terminal_facts_json
        if isinstance(entry.terminal_facts_json, dict)
        else {}
    )
    return {
        "credit_sanction_register_entry_id": str(entry.pk),
        "approval_case_id": str(entry.approval_case_id),
        "loan_application_id": str(entry.loan_application_id),
        "sanction_decision_id": (
            str(entry.sanction_decision_id) if entry.sanction_decision_id else None
        ),
        "workflow_event_id": str(entry.workflow_event_id),
        "application_number": entry.application_number,
        "entry_number": entry.entry_number,
        "borrower_name": entry.borrower_name,
        "borrower_type": entry.borrower_type,
        "folio_number": borrower_facts.get("folio_number"),
        "loan_type": borrower_facts.get("loan_type") or None,
        "purpose": source_facts.get("purpose"),
        "risk": source_facts.get("risk"),
        "requested_amount": _money(entry.requested_amount),
        "eligible_amount": _money(entry.eligible_amount),
        "recommended_amount": _money(entry.recommended_amount),
        "sanctioned_amount": _money(entry.sanctioned_amount),
        "approval_authority": entry.authority_applied_summary,
        "approver_names": (
            entry.approver_names_json
            if isinstance(entry.approver_names_json, list)
            else []
        ),
        "approver_decisions": (
            entry.approver_decisions_json
            if isinstance(entry.approver_decisions_json, list)
            else []
        ),
        "approval_date": entry.approval_date.isoformat(),
        "decision": entry.decision,
        "reasons": entry.reasons,
        "rejection_reason": terminal_facts.get("rejection_reason"),
        "conditions": terminal_facts.get("conditions"),
        "communication": (
            entry.communication_json
            if isinstance(entry.communication_json, dict)
            and entry.communication_json
            else None
        ),
        "exception_reference": entry.exception_reference_json,
        "conflict_abstention_details": entry.conflict_abstention_details_json,
        "general_meeting_approval_reference": (
            entry.general_meeting_approval_reference_json
        ),
        "recorded_at": entry.recorded_at.isoformat().replace("+00:00", "Z"),
    }


def _authority_summary(required_approvers):
    return "; ".join(
        f"{'CFO' if row['role_code'] == 'cfo' else 'Director'}: "
        f"{row['full_name']} ({row['decision'] or 'pending'})"
        for row in required_approvers
    )


def _case_exception(case):
    try:
        return case.exception_register_entry
    except ExceptionRegisterEntry.DoesNotExist:
        return None


def _exception_reference(entry, case):
    if entry is None:
        return None
    return {
        "exception_register_entry_id": str(entry.pk),
        "exception_type": entry.exception_type,
        "business_reason": entry.business_reason,
        "status": entry.status,
        "cycle_number": case.cycle_number,
    }


def _conflict_details(case, action_rows):
    action_by_user = {
        row["user_id"]: row for row in action_rows if row["decision"] == "abstained"
    }
    authority = approval_case_engine.serialize_case_authority(case)
    names = {
        str(row["user_id"]): row["full_name"]
        for row in [*authority["route_approvers"], *authority["required_approvers"]]
    }
    details = []
    for excluded in case.excluded_approvers_json:
        user_id = str(excluded["user_id"])
        action = action_by_user.get(user_id)
        details.append(
            {
                "type": "abstention" if action else "conflict",
                "user_id": user_id,
                "full_name": names.get(user_id),
                "conflict_code": excluded["conflict_code"],
                "reason": excluded["reason"],
                "approval_action_id": action["approval_action_id"] if action else None,
                "acted_at": action["acted_at"] if action else None,
            }
        )
    return details


def _meeting_reference(meeting):
    if meeting is None:
        return None
    return {
        "general_meeting_approval_id": str(meeting.pk),
        "approval_status": meeting.approval_status,
        "meeting_date": meeting.meeting_date.isoformat(),
        "related_party_type": meeting.related_party_type,
        "related_party_user_id": (
            str(meeting.related_party_user_id)
            if meeting.related_party_user_id
            else None
        ),
        "notice_document_id": str(meeting.notice_document_id),
        "minutes_document_id": str(meeting.minutes_document_id),
        "resolution_document_id": str(meeting.resolution_document_id),
    }


def _financial_year_dates(value):
    match = _FINANCIAL_YEAR.fullmatch(value or "")
    if not match:
        raise ValidationError({"financial_year": "Use canonical FYyyyy-yy format."})
    start_year = int(match.group("start"))
    if not 1 <= start_year <= 9998:
        raise ValidationError({"financial_year": "Financial year is out of range."})
    if match.group("end") != str((start_year + 1) % 100).zfill(2):
        raise ValidationError({"financial_year": "Use a consecutive financial year."})
    return date(start_year, 4, 1), date(start_year + 1, 4, 1)


def _positive_int(field, value, default):
    if value in (None, ""):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError({field: "Must be a positive integer."}) from exc
    if parsed < 1 or str(parsed) != str(value):
        raise ValidationError({field: "Must be a positive integer."})
    return parsed


def _money(value):
    return f"{value:.2f}" if value is not None else None


def _rate(value):
    return f"{value:.4f}" if value is not None else None
