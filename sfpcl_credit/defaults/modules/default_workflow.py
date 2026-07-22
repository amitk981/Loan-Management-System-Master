import calendar
from datetime import date, datetime, time, timedelta
from math import ceil
from uuid import UUID, uuid4

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant
from sfpcl_credit.defaults.models import DefaultAssessment, DefaultCase, ExtensionNote
from sfpcl_credit.legal_documents.models import LoanDocument
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.models import LoanAccount
from sfpcl_credit.loans.modules.dpd_source_decision import (
    DpdSourcePermissionDenied,
    resolve_locked_dpd_source_decision,
)
from sfpcl_credit.scheduler.services import enqueue_scheduled_job
from sfpcl_credit.workflows.events import record_workflow_event


READ_PERMISSION = "defaults.case.read"
OPEN_PERMISSION = "defaults.case.open"
ASSESS_PERMISSION = "defaults.assessment.create"
EXTENSION_PERMISSION = "defaults.extension.grant"


class DefaultValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class DefaultPermissionDenied(Exception):
    pass


class DefaultNotFound(Exception):
    pass


class DefaultConflict(Exception):
    pass


class DefaultWorkflow:
    @classmethod
    def open_if_missed_repayment(
        cls,
        *,
        actor,
        loan_account_id,
        as_of_date,
        scheduled_due_date,
        trigger_event=DefaultCase.TRIGGER_MISSED_PRINCIPAL,
        reason="",
        request=None,
    ):
        _require_open_authority(actor)
        cleaned = _validate_open_input(
            as_of_date=as_of_date,
            scheduled_due_date=scheduled_due_date,
            trigger_event=trigger_event,
            reason=reason,
        )
        with transaction.atomic():
            try:
                decision = resolve_locked_dpd_source_decision(
                    actor=actor,
                    loan_account_id=loan_account_id,
                    as_of_date=cleaned["as_of_date"],
                )
            except DpdSourcePermissionDenied as exc:
                raise DefaultNotFound from exc
            obligation = next(
                (
                    line
                    for line in decision.schedule_lines
                    if line.due_date == cleaned["scheduled_due_date"]
                    and line.principal_due > 0
                ),
                None,
            )
            if obligation is None:
                raise DefaultConflict(
                    "No scheduled principal obligation exists for the supplied due date."
                )
            existing = DefaultCase.objects.filter(
                repayment_schedule_id=obligation.repayment_schedule_id,
                trigger_event=cleaned["trigger_event"],
            ).first()
            if existing is not None:
                return existing
            if obligation.principal_paid_as_of >= obligation.principal_due:
                return None

            account = LoanAccount.objects.select_related("member").get(
                pk=decision.loan_account_id
            )
            case_id = uuid4()
            new_state = {
                "loan_account_id": str(account.pk),
                "member_id": str(account.member_id),
                "default_case_id": str(case_id),
                "trigger_event": cleaned["trigger_event"],
                "scheduled_due_date": cleaned["scheduled_due_date"].isoformat(),
                "default_case_status": DefaultCase.STATUS_GRACE_PERIOD_ACTIVE,
            }
            audit = AuditLog.objects.create(
                actor_user=actor,
                action="default.case_opened",
                entity_type="default_case",
                entity_id=case_id,
                old_value_json=None,
                new_value_json=new_state,
                ip_address=request_ip(request) if request is not None else "",
                user_agent=request_user_agent(request) if request is not None else "",
            )
            row = DefaultCase.objects.create(
                default_case_id=case_id,
                loan_account=account,
                member=account.member,
                repayment_schedule_id=obligation.repayment_schedule_id,
                trigger_event=cleaned["trigger_event"],
                scheduled_due_date=cleaned["scheduled_due_date"],
                grace_period_start_date=cleaned["scheduled_due_date"],
                grace_period_end_date=_add_calendar_months(
                    cleaned["scheduled_due_date"], 3
                ),
                default_case_status=DefaultCase.STATUS_GRACE_PERIOD_ACTIVE,
                reason=cleaned["reason"],
                opened_by_user=actor,
                opening_audit=audit,
            )
            record_workflow_event(
                actor=actor,
                workflow_name="default_case",
                entity_type="default_case",
                entity_id=row.pk,
                from_state=None,
                to_state=row.default_case_status,
                trigger_reason=row.reason,
                action_code="default.case_opened",
            )
            return row

    @classmethod
    def process_grace_expiries(cls, *, as_of_date, actor=None, limit=100):
        """Reconcile bounded active grace cases from canonical loan truth."""
        as_of_date = _parse_date("as_of_date", as_of_date)
        case_ids = list(
            DefaultCase.objects.filter(
                default_case_status=DefaultCase.STATUS_GRACE_PERIOD_ACTIVE
            )
            .order_by("grace_period_end_date", "default_case_id")
            .values_list("pk", flat=True)[:limit]
        )
        counts = {
            "processed_count": 0,
            "cured_count": 0,
            "expired_count": 0,
            "assessment_tasks_created_count": 0,
            "failure_count": 0,
        }
        for case_id in case_ids:
            result = None
            task_created = False
            try:
                with transaction.atomic():
                    row = (
                        DefaultCase.objects.select_for_update()
                        .select_related("loan_account")
                        .get(pk=case_id)
                    )
                    if row.default_case_status != DefaultCase.STATUS_GRACE_PERIOD_ACTIVE:
                        continue
                    counts["processed_count"] += 1
                    if row.loan_account.principal_outstanding == 0:
                        _record_grace_transition(
                            row=row,
                            actor=actor,
                            to_state="resolved_by_repayment",
                            action="default.grace_cured",
                            as_of_date=as_of_date,
                            reason="Canonical principal outstanding reached zero.",
                        )
                        result = "cured"
                    elif as_of_date > row.grace_period_end_date:
                        _, task_created = enqueue_scheduled_job(
                            job_type="default_assessment",
                            due_at=timezone.make_aware(
                                datetime.combine(
                                    row.grace_period_end_date + timedelta(days=1),
                                    time.min,
                                )
                            ),
                            idempotency_key=f"default-assessment:{row.pk}",
                            related_entity_type="default_case",
                            related_entity_id=row.pk,
                        )
                        _record_grace_transition(
                            row=row,
                            actor=actor,
                            to_state="grace_period_expired",
                            action="default.grace_expired",
                            as_of_date=as_of_date,
                            reason="Grace period elapsed with principal outstanding.",
                        )
                        result = "expired"
            except Exception:  # A portfolio run records a bounded case failure and continues.
                counts["failure_count"] += 1
                continue
            if result == "cured":
                counts["cured_count"] += 1
            elif result == "expired":
                counts["expired_count"] += 1
                counts["assessment_tasks_created_count"] += int(task_created)
        return counts

    @classmethod
    def process_extension_expiries(cls, *, as_of_date, actor=None, limit=100):
        """Reconcile active extensions without creating recovery artifacts."""
        as_of_date = _parse_date("as_of_date", as_of_date)
        note_ids = list(
            ExtensionNote.objects.filter(status=ExtensionNote.STATUS_ACTIVE)
            .order_by("extension_end_date", "extension_note_id")
            .values_list("pk", flat=True)[:limit]
        )
        counts = {
            "processed_count": 0,
            "cured_count": 0,
            "expired_count": 0,
            "review_tasks_created_count": 0,
            "failure_count": 0,
        }
        for note_id in note_ids:
            result = None
            task_created = False
            try:
                with transaction.atomic():
                    note = (
                        ExtensionNote.objects.select_for_update()
                        .select_related("default_case__loan_account")
                        .get(pk=note_id)
                    )
                    if note.status != ExtensionNote.STATUS_ACTIVE:
                        continue
                    row = DefaultCase.objects.select_for_update().get(
                        pk=note.default_case_id
                    )
                    if row.default_case_status != "extension_granted":
                        continue
                    counts["processed_count"] += 1
                    if row.loan_account.principal_outstanding == 0:
                        _record_extension_transition(
                            note=note,
                            row=row,
                            actor=actor,
                            to_state=DefaultCase.STATUS_RESOLVED_BY_REPAYMENT,
                            action="extension.cured",
                            as_of_date=as_of_date,
                            expire_note=False,
                        )
                        result = "cured"
                    elif as_of_date > note.extension_end_date:
                        _, task_created = enqueue_scheduled_job(
                            job_type="default_assessment",
                            due_at=timezone.make_aware(
                                datetime.combine(
                                    note.extension_end_date + timedelta(days=1), time.min
                                )
                            ),
                            idempotency_key=f"extension-review:{row.pk}",
                            related_entity_type="default_case",
                            related_entity_id=row.pk,
                        )
                        _record_extension_transition(
                            note=note,
                            row=row,
                            actor=actor,
                            to_state="extension_expired",
                            action="extension.expired",
                            as_of_date=as_of_date,
                            expire_note=True,
                        )
                        result = "expired"
            except Exception:
                counts["failure_count"] += 1
                continue
            if result == "cured":
                counts["cured_count"] += 1
            elif result == "expired":
                counts["expired_count"] += 1
                counts["review_tasks_created_count"] += int(task_created)
        return counts

    @classmethod
    def assess(
        cls, *, actor, default_case_id, payload, request=None, as_of_date=None
    ):
        _require_assessment_authority(actor)
        if not _scoped_case_candidates(actor=actor).filter(pk=default_case_id).exists():
            raise DefaultNotFound
        cleaned = _validate_assessment_input(payload)
        assessment_date = as_of_date or timezone.localdate()
        with transaction.atomic():
            row = (
                DefaultCase.objects.select_for_update()
                .select_related("loan_account")
                .get(pk=default_case_id)
            )
            if (
                row.default_case_status != DefaultCase.STATUS_GRACE_PERIOD_EXPIRED
                or assessment_date <= row.grace_period_end_date
                or row.loan_account.principal_outstanding == 0
                or row.loan_account.closed_at is not None
            ):
                raise DefaultConflict(
                    "Only an unpaid, open case after grace expiry can be assessed."
                )
            if row.current_assessment_id is not None:
                raise DefaultConflict("The default case already has a current assessment.")
            _require_case_evidence(row=row, document_ids=cleaned["evidence_document_ids"])
            assessment = DefaultAssessment.objects.create(
                default_case=row,
                assessment_type=cleaned["assessment_type"],
                payment_failure_classification=cleaned[
                    "payment_failure_classification"
                ],
                reason_summary=cleaned["reason_summary"],
                evidence_document_ids_json=[
                    str(value) for value in cleaned["evidence_document_ids"]
                ],
                borrower_interaction_summary=cleaned[
                    "borrower_interaction_summary"
                ],
                assessed_by_user=actor,
                recommended_action=cleaned["recommended_action"],
            )
            old_state = row.default_case_status
            row.default_case_status = DefaultCase.STATUS_ASSESSMENT_IN_PROGRESS
            row.current_assessment = assessment
            evidence = serialize_default_assessment(assessment)
            AuditLog.objects.create(
                actor_user=actor,
                action="default.assessed",
                entity_type="default_case",
                entity_id=row.pk,
                old_value_json={"default_case_status": old_state},
                new_value_json=evidence,
                ip_address=request_ip(request) if request is not None else "",
                user_agent=request_user_agent(request) if request is not None else "",
            )
            row.save(update_fields=["default_case_status", "current_assessment"])
            record_workflow_event(
                actor=actor,
                workflow_name="default_case",
                entity_type="default_case",
                entity_id=row.pk,
                from_state=old_state,
                to_state=row.default_case_status,
                trigger_reason=assessment.reason_summary,
                action_code="default.assessed",
            )
            return assessment

    @classmethod
    def grant_extension(
        cls, *, actor, default_case_id, payload, request=None
    ):
        _require_extension_authority(actor)
        if not _scoped_case_candidates(actor=actor).filter(pk=default_case_id).exists():
            raise DefaultNotFound
        cleaned = _validate_extension_input(payload)
        with transaction.atomic():
            row = (
                DefaultCase.objects.select_for_update()
                .select_related("loan_account")
                .get(pk=default_case_id)
            )
            existing = row.extension_note
            if existing is not None:
                if _extension_replay_matches(existing, cleaned):
                    return existing
                raise DefaultConflict("The default case already has a different extension note.")
            assessment = row.current_assessment
            if (
                row.default_case_status != DefaultCase.STATUS_ASSESSMENT_IN_PROGRESS
                or assessment is None
                or assessment.assessment_type != DefaultAssessment.TYPE_POST_GRACE
                or assessment.payment_failure_classification != "non_intentional"
                or assessment.recommended_action != "grant_extension"
                or row.loan_account.principal_outstanding == 0
                or row.loan_account.closed_at is not None
            ):
                raise DefaultConflict(
                    "Only an unpaid, open case with a current non-intentional extension recommendation is eligible."
                )
            expected_start = row.grace_period_end_date + timedelta(days=1)
            expected_end = _add_calendar_months(expected_start, 12) - timedelta(days=1)
            date_errors = {}
            if cleaned["extension_start_date"] != expected_start:
                date_errors["extension_start_date"] = "Must be the day after grace expiry."
            if cleaned["extension_end_date"] != expected_end:
                date_errors["extension_end_date"] = "Must end after exactly one calendar year."
            if date_errors:
                raise DefaultValidation(date_errors)
            document = LoanDocument.objects.filter(
                pk=cleaned["document_id"],
                loan_application_id=row.loan_account.loan_application_id,
                document_type="extension_note",
                generation_status=LoanDocument.GENERATION_GENERATED,
                document_id__isnull=False,
            ).first()
            if document is None:
                raise DefaultValidation(
                    {"document_id": "Must identify a generated Extension Note in this loan file."}
                )
            note = ExtensionNote.objects.create(
                default_case=row,
                loan_account=row.loan_account,
                extension_reason=cleaned["extension_reason"],
                extension_start_date=cleaned["extension_start_date"],
                extension_end_date=cleaned["extension_end_date"],
                prepared_by_user=actor,
                approved_by_user=None,
                loan_document=document,
                status=ExtensionNote.STATUS_ACTIVE,
            )
            old_state = row.default_case_status
            row.extension_note = note
            row.default_case_status = "extension_granted"
            row.save(update_fields=["extension_note", "default_case_status"])
            evidence = serialize_extension_note(note)
            AuditLog.objects.create(
                actor_user=actor,
                action="extension.granted",
                entity_type="extension_note",
                entity_id=note.pk,
                old_value_json={"default_case_status": old_state},
                new_value_json=evidence,
                ip_address=request_ip(request) if request is not None else "",
                user_agent=request_user_agent(request) if request is not None else "",
            )
            record_workflow_event(
                actor=actor,
                workflow_name="default_case",
                entity_type="default_case",
                entity_id=row.pk,
                from_state=old_state,
                to_state=row.default_case_status,
                trigger_reason=note.extension_reason,
                action_code="extension.granted",
            )
            return note


def get_default_case(*, actor, default_case_id):
    row = _scoped_case_candidates(actor=actor).filter(pk=default_case_id).first()
    if row is None:
        raise DefaultNotFound
    return serialize_default_case(row, actor=actor)


def list_default_cases(*, actor, query_params):
    allowed = {
        "default_case_status",
        "member_id",
        "loan_account_id",
        "page",
        "page_size",
    }
    unknown = set(query_params) - allowed
    if unknown:
        raise DefaultValidation(
            {field: "Unknown query parameter." for field in sorted(unknown)}
        )
    filters = {}
    status = query_params.get("default_case_status")
    if status:
        if status not in _DEFAULT_CASE_STATUSES:
            raise DefaultValidation(
                {"default_case_status": "Must be a valid default case status."}
            )
        filters["default_case_status"] = status
    for field in ("member_id", "loan_account_id"):
        value = query_params.get(field)
        if value:
            try:
                filters[field] = UUID(str(value))
            except (TypeError, ValueError, AttributeError) as exc:
                raise DefaultValidation({field: "Must be a valid UUID."}) from exc
    page = _positive_int("page", query_params.get("page"), default=1, maximum=None)
    page_size = _positive_int(
        "page_size", query_params.get("page_size"), default=20, maximum=100
    )
    queryset = _scoped_case_candidates(actor=actor).filter(**filters)
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    rows = queryset[offset : offset + page_size]
    return [serialize_default_case(row, actor=actor) for row in rows], {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def serialize_default_case(row, *, actor):
    from sfpcl_credit.recovery.modules.recovery_workflow import (
        can_read_non_payment_note,
        serialize_non_payment_note,
    )

    return {
        "default_case_id": str(row.pk),
        "loan_account_id": str(row.loan_account_id),
        "member_id": str(row.member_id),
        "trigger_event": row.trigger_event,
        "scheduled_due_date": row.scheduled_due_date.isoformat(),
        "repayment_schedule_id": str(row.repayment_schedule_id),
        "default_case_status": row.default_case_status,
        "grace_period_start_date": row.grace_period_start_date.isoformat(),
        "grace_period_end_date": row.grace_period_end_date.isoformat(),
        "grace_state": _derived_grace_state(row, as_of_date=timezone.localdate()),
        "current_assessment": (
            serialize_default_assessment(row.current_assessment)
            if row.current_assessment_id is not None
            else None
        ),
        "extension_note": (
            serialize_extension_note(row.extension_note)
            if row.extension_note_id is not None
            else None
        ),
        "non_payment_note": (
            serialize_non_payment_note(row.non_payment_note)
            if hasattr(row, "non_payment_note")
            and can_read_non_payment_note(actor=actor, note=row.non_payment_note)
            else None
        ),
        "reason": row.reason,
        "available_actions": _available_actions(row, actor=actor),
    }


def serialize_default_assessment(row):
    return {
        "default_assessment_id": str(row.pk),
        "default_case_id": str(row.default_case_id),
        "assessment_type": row.assessment_type,
        "payment_failure_classification": row.payment_failure_classification,
        "reason_summary": row.reason_summary,
        "evidence_document_ids": list(row.evidence_document_ids_json),
        "borrower_interaction_summary": row.borrower_interaction_summary,
        "recommended_action": row.recommended_action,
        "assessed_by_user_id": str(row.assessed_by_user_id),
        "assessed_at": row.assessed_at.isoformat().replace("+00:00", "Z"),
    }


def serialize_extension_note(row):
    return {
        "extension_note_id": str(row.pk),
        "default_case_id": str(row.default_case_id),
        "loan_account_id": str(row.loan_account_id),
        "extension_reason": row.extension_reason,
        "extension_start_date": row.extension_start_date.isoformat(),
        "extension_end_date": row.extension_end_date.isoformat(),
        "document_id": str(row.loan_document_id),
        "prepared_by_user_id": str(row.prepared_by_user_id),
        "approved_by_user_id": (
            str(row.approved_by_user_id) if row.approved_by_user_id else None
        ),
        "status": row.status,
    }


def _derived_grace_state(row, *, as_of_date):
    if row.default_case_status == "resolved_by_repayment":
        return "cured"
    if row.loan_account.principal_outstanding == 0:
        return "cured"
    return "expired" if as_of_date > row.grace_period_end_date else "active"


def _record_grace_transition(*, row, actor, to_state, action, as_of_date, reason):
    from_state = row.default_case_status
    evidence = {
        "default_case_id": str(row.pk),
        "loan_account_id": str(row.loan_account_id),
        "from_state": from_state,
        "to_state": to_state,
        "as_of_date": as_of_date.isoformat(),
    }
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user" if actor is not None else "system",
        action=action,
        entity_type="default_case",
        entity_id=row.pk,
        old_value_json={"default_case_status": from_state},
        new_value_json=evidence,
    )
    row.default_case_status = to_state
    if to_state == "resolved_by_repayment":
        row.closed_at = timezone.now()
    row.save(update_fields=["default_case_status", "closed_at"])
    record_workflow_event(
        actor=actor,
        workflow_name="default_case",
        entity_type="default_case",
        entity_id=row.pk,
        from_state=from_state,
        to_state=to_state,
        trigger_reason=reason,
        action_code=action,
    )


def _record_extension_transition(
    *, note, row, actor, to_state, action, as_of_date, expire_note
):
    from_state = row.default_case_status
    evidence = {
        "extension_note_id": str(note.pk),
        "default_case_id": str(row.pk),
        "loan_account_id": str(row.loan_account_id),
        "from_state": from_state,
        "to_state": to_state,
        "as_of_date": as_of_date.isoformat(),
    }
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user" if actor is not None else "system",
        action=action,
        entity_type="extension_note",
        entity_id=note.pk,
        old_value_json={"status": note.status, "default_case_status": from_state},
        new_value_json=evidence,
    )
    if expire_note:
        note.status = ExtensionNote.STATUS_EXPIRED
        note.save(update_fields=["status"])
    row.default_case_status = to_state
    if to_state == DefaultCase.STATUS_RESOLVED_BY_REPAYMENT:
        row.closed_at = timezone.now()
    row.save(update_fields=["default_case_status", "closed_at"])
    record_workflow_event(
        actor=actor,
        workflow_name="default_case",
        entity_type="default_case",
        entity_id=row.pk,
        from_state=from_state,
        to_state=to_state,
        trigger_reason=(
            "Canonical principal outstanding reached zero."
            if to_state == DefaultCase.STATUS_RESOLVED_BY_REPAYMENT
            else "Extension elapsed with principal outstanding; review is required."
        ),
        action_code=action,
    )


def serialize_opened_default_case(row):
    """Return the exact source §35.1 result plus server-owned actions."""
    return {
        "default_case_id": str(row.pk),
        "default_case_status": row.default_case_status,
        "grace_period_start_date": row.grace_period_start_date.isoformat(),
        "grace_period_end_date": row.grace_period_end_date.isoformat(),
        "available_actions": [],
    }


def _require_permission(actor, permission):
    if (
        not actor.can_authenticate()
        or permission not in auth_service.effective_permission_codes(actor)
    ):
        raise DefaultPermissionDenied


def _require_open_authority(actor):
    _require_permission(actor, OPEN_PERMISSION)
    if "credit_manager" not in auth_service.effective_role_codes(actor):
        raise DefaultPermissionDenied


def _require_assessment_authority(actor):
    _require_permission(actor, ASSESS_PERMISSION)
    if "credit_assessment" not in actor.team_codes():
        raise DefaultPermissionDenied


def _require_extension_authority(actor):
    _require_permission(actor, EXTENSION_PERMISSION)
    if "credit_manager" not in auth_service.effective_role_codes(actor):
        raise DefaultPermissionDenied


def _scoped_case_candidates(*, actor):
    _require_permission(actor, READ_PERMISSION)
    roles = set(auth_service.effective_role_codes(actor))
    scope = Q(pk__in=[])
    if "credit_manager" in roles:
        scope |= Q(
            loan_account__loan_account_status__in={
                "active",
                "partially_repaid",
                "overdue",
                "grace_period",
                "extended",
                "non_recoverable_under_review",
                "repaid",
            }
        )
    if "credit_assessment" in actor.team_codes():
        scope |= Q(
            loan_account__loan_account_status__in={
                "active",
                "partially_repaid",
                "overdue",
                "grace_period",
                "extended",
                "non_recoverable_under_review",
                "repaid",
            }
        )
    if "company_secretary" in roles:
        scope |= Q(
            loan_account__loan_application__application_status=
            LoanApplication.STATUS_APPROVED_BY_SANCTION
        )
    scope |= Q(
        loan_account__sanction_decision__approval_case__required_approver_index__user_id=actor.pk
    )
    scope |= Q(non_payment_note__approval_case__required_approver_index__user_id=actor.pk)
    auditor_portfolio = (
        "internal_auditor" in roles
        and ApprovalCaseReadScopeGrant.objects.filter(
            role__role_code="internal_auditor",
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
            status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
        ).exists()
    )
    queryset = DefaultCase.objects.select_related(
        "loan_account",
        "member",
        "current_assessment",
        "extension_note",
        "non_payment_note__loan_document",
        "non_payment_note__approval_case",
    )
    if not auditor_portfolio:
        queryset = queryset.filter(scope)
    return queryset.distinct().order_by("-default_detected_at", "-default_case_id")


def _validate_open_input(*, as_of_date, scheduled_due_date, trigger_event, reason):
    parsed_as_of = _parse_date("as_of_date", as_of_date)
    parsed_due = _parse_date("scheduled_due_date", scheduled_due_date)
    errors = {}
    if trigger_event != DefaultCase.TRIGGER_MISSED_PRINCIPAL:
        errors["trigger_event"] = "Must be missed_principal_repayment."
    if parsed_due >= parsed_as_of:
        errors["scheduled_due_date"] = "Must be before the detection date."
    if not isinstance(reason, str):
        errors["reason"] = "Must be a string."
    elif len(reason) > 2000:
        errors["reason"] = "Must be at most 2000 characters."
    if errors:
        raise DefaultValidation(errors)
    return {
        "as_of_date": parsed_as_of,
        "scheduled_due_date": parsed_due,
        "trigger_event": trigger_event,
        "reason": reason.strip(),
    }


def _parse_date(field, value):
    if isinstance(value, date):
        return value
    parsed = parse_date(value) if isinstance(value, str) else None
    if parsed is None:
        raise DefaultValidation({field: "Must be a valid ISO date."})
    return parsed


def _add_calendar_months(value, months):
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _positive_int(field, value, *, default, maximum):
    if value in (None, ""):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise DefaultValidation({field: "Must be a positive integer."}) from exc
    if parsed < 1 or (maximum is not None and parsed > maximum):
        message = (
            f"Must be between 1 and {maximum}."
            if maximum is not None
            else "Must be a positive integer."
        )
        raise DefaultValidation({field: message})
    return parsed


def _validate_assessment_input(payload):
    allowed = {
        "assessment_type",
        "payment_failure_classification",
        "reason_summary",
        "evidence_document_ids",
        "borrower_interaction_summary",
        "recommended_action",
    }
    errors = {
        field: "Unknown request field." for field in sorted(set(payload) - allowed)
    }
    assessment_type = payload.get("assessment_type")
    if assessment_type != DefaultAssessment.TYPE_POST_GRACE:
        errors["assessment_type"] = "Must be post_grace."
    classification = payload.get("payment_failure_classification")
    if classification not in DefaultAssessment.CLASSIFICATIONS:
        errors["payment_failure_classification"] = (
            "Must be intentional, non_intentional, or unclear."
        )
    reason = _required_text(
        "reason_summary", payload.get("reason_summary"), errors, maximum=5000
    )
    borrower_summary = payload.get("borrower_interaction_summary", "")
    if not isinstance(borrower_summary, str):
        errors["borrower_interaction_summary"] = "Must be a string."
        borrower_summary = ""
    elif len(borrower_summary) > 5000:
        errors["borrower_interaction_summary"] = "Must be at most 5000 characters."
    recommendation = _required_text(
        "recommended_action", payload.get("recommended_action"), errors, maximum=100
    )
    raw_document_ids = payload.get("evidence_document_ids")
    document_ids = []
    if not isinstance(raw_document_ids, list) or not raw_document_ids:
        errors["evidence_document_ids"] = "At least one evidence document is required."
    else:
        try:
            document_ids = [UUID(str(value)) for value in raw_document_ids]
        except (TypeError, ValueError, AttributeError):
            errors["evidence_document_ids"] = "Every item must be a valid UUID."
        if len(document_ids) != len(set(document_ids)):
            errors["evidence_document_ids"] = "Duplicate document ids are not allowed."
    if errors:
        raise DefaultValidation(errors)
    return {
        "assessment_type": assessment_type,
        "payment_failure_classification": classification,
        "reason_summary": reason,
        "evidence_document_ids": document_ids,
        "borrower_interaction_summary": borrower_summary.strip(),
        "recommended_action": recommendation,
    }


def _validate_extension_input(payload):
    allowed = {
        "extension_reason",
        "extension_start_date",
        "extension_end_date",
        "document_id",
    }
    errors = {field: "Unknown request field." for field in sorted(set(payload) - allowed)}
    reason = _required_text(
        "extension_reason", payload.get("extension_reason"), errors, maximum=5000
    )
    parsed = {}
    for field in ("extension_start_date", "extension_end_date"):
        try:
            parsed[field] = _parse_date(field, payload.get(field))
        except DefaultValidation as exc:
            errors.update(exc.field_errors)
    try:
        document_id = UUID(str(payload.get("document_id")))
    except (TypeError, ValueError, AttributeError):
        errors["document_id"] = "Must be a valid UUID."
        document_id = None
    if errors:
        raise DefaultValidation(errors)
    return {
        "extension_reason": reason,
        **parsed,
        "document_id": document_id,
    }


def _extension_replay_matches(row, cleaned):
    return (
        row.extension_reason == cleaned["extension_reason"]
        and row.extension_start_date == cleaned["extension_start_date"]
        and row.extension_end_date == cleaned["extension_end_date"]
        and row.loan_document_id == cleaned["document_id"]
    )


def _required_text(field, value, errors, *, maximum):
    if not isinstance(value, str) or not value.strip():
        errors[field] = "This field is required."
        return ""
    if len(value) > maximum:
        errors[field] = f"Must be at most {maximum} characters."
    return value.strip()


def _require_case_evidence(*, row, document_ids):
    found = set(
        LoanDocument.objects.filter(
            loan_application_id=row.loan_account.loan_application_id,
            document_id__in=document_ids,
        ).values_list("document_id", flat=True)
    )
    if found != set(document_ids):
        raise DefaultValidation(
            {"evidence_document_ids": "Evidence must belong to this loan application."}
        )


def _available_actions(row, *, actor):
    if (
        row.default_case_status == DefaultCase.STATUS_GRACE_PERIOD_EXPIRED
        and row.current_assessment_id is None
        and row.loan_account.principal_outstanding > 0
        and row.loan_account.closed_at is None
        and ASSESS_PERMISSION in auth_service.effective_permission_codes(actor)
        and "credit_assessment" in actor.team_codes()
    ):
        return ["assess"]
    if (
        row.default_case_status == DefaultCase.STATUS_ASSESSMENT_IN_PROGRESS
        and row.extension_note_id is None
        and row.current_assessment_id is not None
        and row.current_assessment.payment_failure_classification == "non_intentional"
        and row.current_assessment.recommended_action == "grant_extension"
        and row.loan_account.principal_outstanding > 0
        and row.loan_account.closed_at is None
        and EXTENSION_PERMISSION in auth_service.effective_permission_codes(actor)
        and "credit_manager" in auth_service.effective_role_codes(actor)
    ):
        return ["grant_extension"]
    return []


def api_open_default_case(*, actor, loan_account_id, payload, request=None):
    allowed = {"trigger_event", "scheduled_due_date", "reason"}
    unknown = set(payload) - allowed
    if unknown:
        raise DefaultValidation(
            {field: "Unknown request field." for field in sorted(unknown)}
        )
    row = DefaultWorkflow.open_if_missed_repayment(
        actor=actor,
        loan_account_id=loan_account_id,
        as_of_date=timezone.localdate(),
        scheduled_due_date=payload.get("scheduled_due_date"),
        trigger_event=payload.get("trigger_event"),
        reason=payload.get("reason", ""),
        request=request,
    )
    if row is None:
        raise DefaultConflict("The scheduled principal obligation is not missed.")
    return serialize_opened_default_case(row)


def api_assess_default_case(*, actor, default_case_id, payload, request=None):
    assessment = DefaultWorkflow.assess(
        actor=actor,
        default_case_id=default_case_id,
        payload=payload,
        request=request,
    )
    return serialize_default_assessment(assessment)


def api_grant_extension(*, actor, default_case_id, payload, request=None):
    note = DefaultWorkflow.grant_extension(
        actor=actor,
        default_case_id=default_case_id,
        payload=payload,
        request=request,
    )
    return serialize_extension_note(note)


_DEFAULT_CASE_STATUSES = {
    "open",
    "grace_period_active",
    "grace_period_expired",
    "assessment_in_progress",
    "extension_granted",
    "extension_expired",
    "non_payment_under_review",
    "recovery_decision_pending",
    "recovery_approved",
    "recovery_in_progress",
    "resolved_by_repayment",
    "closed",
}
