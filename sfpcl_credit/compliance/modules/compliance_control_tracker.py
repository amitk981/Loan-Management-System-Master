from datetime import date
from math import ceil
import uuid

from django.db import models, transaction
from django.utils import timezone

from sfpcl_credit.compliance.models import (
    ComplianceControl, ComplianceControlVersion, ComplianceEvidence, ComplianceTask,
    MoneyLendingLawReview,
)
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import AuditLog, User
from sfpcl_credit.identity.modules import auth_service


class ComplianceDenied(Exception):
    pass


class ComplianceInvalid(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class ComplianceConflict(Exception):
    pass


class ComplianceMissing(Exception):
    pass


def permission_codes(actor):
    return set(auth_service.effective_permission_codes(actor))


def require(actor, code):
    if code not in permission_codes(actor):
        raise ComplianceDenied()
    require_auditor_scope(actor)


def require_auditor_scope(actor):
    if actor.primary_role.role_code != "internal_auditor":
        return
    from sfpcl_credit.approvals.modules.read_scope import (
        has_active_audit_read_scope,
    )

    if not has_active_audit_read_scope(actor):
        raise ComplianceDenied()


def forbid_auditor_mutation(actor):
    if actor.primary_role.role_code == "internal_auditor":
        raise ComplianceDenied()


def auditor_read_projection(actor, data):
    if actor.primary_role.role_code != "internal_auditor":
        return data
    if isinstance(data, dict):
        return {
            key: auditor_read_projection(actor, value)
            for key, value in data.items()
            if key != "available_actions"
        }
    if isinstance(data, list):
        return [auditor_read_projection(actor, value) for value in data]
    return data


def create_control(*, actor, payload):
    require(actor, "compliance.control.manage")
    values = _control_values(payload)
    try:
        with transaction.atomic():
            row = ComplianceControl.objects.create(**values)
            _audit(actor, "compliance.control.created", row.pk, serialize_control(row, actor))
            ComplianceControlVersion.objects.create(
                control=row, version_number=1, snapshot_json=serialize_control(row, actor),
                change_reason="Initial control creation", effective_from=timezone.localdate(),
                changed_by_user=actor,
            )
    except Exception as exc:
        if isinstance(exc, ComplianceInvalid):
            raise
        if ComplianceControl.objects.filter(control_code=values.get("control_code")).exists():
            raise ComplianceConflict("Control code already exists.") from exc
        raise
    return serialize_control(row, actor)


def list_controls(*, actor, query):
    require(actor, "compliance.control.read")
    queryset = ComplianceControl.objects.select_related("owner_user", "reviewer_user")
    if "compliance.control.manage" not in permission_codes(actor) and actor.primary_role.role_code != "internal_auditor":
        queryset = queryset.filter(models.Q(owner_user=actor) | models.Q(reviewer_user=actor))
    for param in ("status", "frequency", "control_area"):
        value = query.get(param)
        if value:
            queryset = queryset.filter(**{param: value})
    rows, pagination = _paginate(queryset.order_by("control_code"), query)
    return [serialize_control(row, actor) for row in rows], pagination


def search_controls(*, actor, search):
    """Canonical object-scoped control selector for safe projections."""
    require(actor, "compliance.control.read")
    queryset = ComplianceControl.objects.select_related("owner_user", "reviewer_user")
    if (
        "compliance.control.manage" not in permission_codes(actor)
        and actor.primary_role.role_code != "internal_auditor"
    ):
        queryset = queryset.filter(models.Q(owner_user=actor) | models.Q(reviewer_user=actor))
    return queryset.filter(
        models.Q(control_code__icontains=search)
        | models.Q(control_name__icontains=search)
        | models.Q(control_area__icontains=search)
    ).order_by("control_code", "compliance_control_id")


def update_control(*, actor, control_id, payload):
    require(actor, "compliance.control.manage")
    try:
        row = ComplianceControl.objects.get(pk=control_id)
    except ComplianceControl.DoesNotExist as exc:
        raise ComplianceMissing() from exc
    immutable = {"control_code", "frequency", "first_due_date", "owner_user_id", "reviewer_user_id"}
    change_reason = _required(payload, "change_reason")
    effective_from = _date(payload, "effective_from")
    if effective_from > timezone.localdate():
        raise ComplianceInvalid({"effective_from": "Future activation requires a future configuration owner."})
    merged = {field: getattr(row, field) for field in (
        "control_code", "control_name", "control_area", "legal_basis", "control_type",
        "frequency", "owner_role_code", "evidence_required", "risk_if_missed", "status",
    )}
    merged.update({k: v for k, v in payload.items() if k in merged})
    merged["owner_user_id"] = payload.get("owner_user_id", row.owner_user_id)
    merged["reviewer_user_id"] = payload.get("reviewer_user_id", row.reviewer_user_id)
    merged["first_due_date"] = payload.get("first_due_date", row.first_due_date)
    values = _control_values(merged)
    with transaction.atomic():
        row = ComplianceControl.objects.select_for_update().get(pk=row.pk)
        if row.tasks.exists() and immutable.intersection(payload):
            raise ComplianceConflict("Scheduled control identity cannot change after task generation.")
        old = serialize_control(row, actor)
        for field, value in values.items():
            setattr(row, field, value)
        row.save()
        new = serialize_control(row, actor)
        ComplianceControlVersion.objects.create(
            control=row, version_number=row.versions.count() + 1,
            snapshot_json=new, change_reason=change_reason,
            effective_from=effective_from, changed_by_user=actor,
        )
        _audit(actor, "compliance.control.updated", row.pk, {
            "old": old, "new": new,
            "change_reason": change_reason, "effective_from": effective_from.isoformat(),
        })
    return serialize_control(row, actor)


def serialize_control(row, actor):
    permissions = permission_codes(actor)
    return auditor_read_projection(actor, {
        "compliance_control_id": str(row.pk), "control_code": row.control_code,
        "control_name": row.control_name, "control_area": row.control_area,
        "legal_basis": row.legal_basis, "control_type": row.control_type,
        "frequency": row.frequency, "owner_role_code": row.owner_role_code,
        "owner_user_id": str(row.owner_user_id), "reviewer_user_id": str(row.reviewer_user_id),
        "first_due_date": row.first_due_date.isoformat(), "evidence_required": row.evidence_required,
        "risk_if_missed": row.risk_if_missed, "status": row.status,
        "available_actions": ["update"] if "compliance.control.manage" in permissions else [],
    })


def create_task(*, actor, payload):
    require(actor, "compliance.task.create")
    try:
        control = ComplianceControl.objects.get(pk=_uuid(payload, "compliance_control_id"))
    except ComplianceControl.DoesNotExist as exc:
        raise ComplianceInvalid({"compliance_control_id": "Active control was not found."}) from exc
    if control.status != ComplianceControl.STATUS_ACTIVE:
        raise ComplianceConflict("Disabled controls cannot receive tasks.")
    if actor.pk != control.owner_user_id:
        raise ComplianceDenied()
    due = _date(payload, "due_date")
    period = _required(payload, "task_period")
    owner = _user(payload, "assigned_to_user_id")
    reviewer = _user(payload, "reviewer_user_id")
    if owner.pk != control.owner_user_id or reviewer.pk != control.reviewer_user_id:
        raise ComplianceInvalid({"assigned_to_user_id": "Task owner and reviewer must match the control."})
    expected_period = _period_for(control, due)
    from sfpcl_credit.compliance.modules.compliance_task_engine import ComplianceTaskEngine
    if (due, expected_period) not in ComplianceTaskEngine._occurrences(control, due):
        raise ComplianceInvalid({"due_date": "Must be a configured control occurrence."})
    if period != expected_period:
        raise ComplianceInvalid({"task_period": f"Must be {expected_period} for the configured due date."})
    status = ComplianceTask.STATUS_OVERDUE if due < timezone.localdate() else ComplianceTask.STATUS_DUE
    try:
        with transaction.atomic():
            row = ComplianceTask.objects.create(
                control=control, task_period=period, due_date=due, assigned_to_user=owner,
                reviewer_user=reviewer, task_status=status, remarks=str(payload.get("remarks") or "").strip(),
            )
            _audit(actor, "compliance.task.created", row.pk, {"control_id": str(control.pk), "period": period})
    except Exception as exc:
        if ComplianceTask.objects.filter(control=control, task_period=period).exists():
            raise ComplianceConflict("A task already exists for this control and period.") from exc
        raise
    return serialize_task(row, actor)


def list_tasks(*, actor, query):
    require(actor, "compliance.task.read")
    queryset = ComplianceTask.objects.select_related("control", "assigned_to_user", "reviewer_user")
    if actor.primary_role.role_code != "internal_auditor":
        queryset = queryset.filter(models.Q(assigned_to_user=actor) | models.Q(reviewer_user=actor))
    if query.get("task_status"):
        queryset = queryset.filter(task_status=query["task_status"])
    if query.get("assigned_to_me", "").lower() == "true":
        queryset = queryset.filter(assigned_to_user=actor)
    if query.get("compliance_control_id"):
        queryset = queryset.filter(control_id=_parse_uuid(query["compliance_control_id"], "compliance_control_id"))
    rows, pagination = _paginate(queryset.order_by("due_date", "compliance_task_id"), query)
    return [serialize_task(row, actor) for row in rows], pagination


def search_tasks(*, actor, search, control_ids):
    """Canonical object-scoped task selector for safe projections."""
    require(actor, "compliance.task.read")
    queryset = ComplianceTask.objects.select_related(
        "control", "assigned_to_user", "reviewer_user"
    )
    if actor.primary_role.role_code != "internal_auditor":
        queryset = queryset.filter(
            models.Q(assigned_to_user=actor) | models.Q(reviewer_user=actor)
        )
    return queryset.filter(
        models.Q(control_id__in=control_ids)
        | models.Q(control__control_code__icontains=search)
        | models.Q(control__control_name__icontains=search)
        | models.Q(task_period__icontains=search)
    ).order_by("control__control_code", "task_period", "compliance_task_id")


def search_evidence(*, actor, search):
    """Canonical evidence selector; restricted payload fields are never searched."""
    require_auditor_scope(actor)
    permissions = permission_codes(actor)
    queryset = ComplianceEvidence.objects.select_related(
        "task__control", "submitted_by_user", "reviewed_by_user"
    )
    if (
        actor.primary_role.role_code == "internal_auditor"
        and "compliance.task.read" in permissions
    ):
        scoped = queryset
    else:
        scope = models.Q(pk__in=[])
        if "compliance.evidence.submit" in permissions:
            scope |= models.Q(task__assigned_to_user=actor, submitted_by_user=actor)
        if "compliance.evidence.review" in permissions:
            scope |= models.Q(task__reviewer_user=actor)
        scoped = queryset.filter(scope)
    return scoped.filter(
        models.Q(task__control__control_code__icontains=search)
        | models.Q(task__control__control_name__icontains=search)
        | models.Q(task__task_period__icontains=search)
    ).order_by(
        "task__control__control_code",
        "task__task_period",
        "submitted_at",
        "compliance_evidence_id",
    )


def search_money_lending_reviews(*, actor, search):
    """Canonical object-scoped annual-review selector for safe projections."""
    require_auditor_scope(actor)
    permissions = permission_codes(actor)
    queryset = MoneyLendingLawReview.objects.select_related(
        "task", "reviewed_by_user"
    )
    if (
        actor.primary_role.role_code == "internal_auditor"
        and "compliance.task.read" in permissions
    ):
        scoped = queryset
    else:
        scope = models.Q(pk__in=[])
        if "compliance.money_lending_review.manage" in permissions:
            scope |= models.Q(reviewed_by_user=actor)
        if "compliance.task.read" in permissions:
            scope |= models.Q(task__assigned_to_user=actor) | models.Q(
                task__reviewer_user=actor
            )
        scoped = queryset.filter(scope)
    return scoped.filter(
        models.Q(financial_year__icontains=search)
        | models.Q(state__icontains=search)
        | models.Q(applicability__iexact=search)
    ).order_by("financial_year", "state", "money_lending_law_review_id")


def update_task(*, actor, task_id, payload):
    require(actor, "compliance.task.update")
    try:
        row = ComplianceTask.objects.get(pk=task_id)
    except ComplianceTask.DoesNotExist as exc:
        raise ComplianceMissing() from exc
    if row.assigned_to_user_id != actor.pk:
        raise ComplianceDenied()
    unknown = set(payload) - {"remarks"}
    if unknown:
        raise ComplianceInvalid({field: "Task schedule, ownership, and state are engine-owned." for field in unknown})
    with transaction.atomic():
        row = ComplianceTask.objects.select_for_update().get(pk=row.pk)
        if row.task_status == ComplianceTask.STATUS_COMPLETED:
            raise ComplianceConflict("Completed compliance tasks are immutable.")
        row.remarks = str(payload.get("remarks") or "").strip()
        row.save(update_fields=["remarks", "updated_at"])
        _audit(actor, "compliance.task.updated", row.pk, serialize_task(row, actor))
    return serialize_task(row, actor)


def serialize_task(row, actor):
    permissions = permission_codes(actor)
    actions = []
    if row.task_status != ComplianceTask.STATUS_COMPLETED and row.assigned_to_user_id == actor.pk and "compliance.task.update" in permissions:
        actions.append("update")
    if row.task_status in {ComplianceTask.STATUS_DUE, ComplianceTask.STATUS_OVERDUE} and row.assigned_to_user_id == actor.pk and "compliance.evidence.submit" in permissions:
        actions.append("submit_evidence")
    if row.reviewer_user_id == actor.pk and row.task_status == ComplianceTask.STATUS_EVIDENCE_SUBMITTED and "compliance.evidence.review" in permissions:
        actions.append("review_evidence")
    latest_evidence = row.evidence_submissions.order_by("-submitted_at").first()
    return auditor_read_projection(actor, {
        "compliance_task_id": str(row.pk), "compliance_control_id": str(row.control_id),
        "control_code": row.control.control_code, "task_period": row.task_period,
        "due_date": row.due_date.isoformat(), "assigned_to_user_id": str(row.assigned_to_user_id),
        "reviewer_user_id": str(row.reviewer_user_id), "task_status": row.task_status,
        "remarks": row.remarks, "closed_at": row.closed_at.isoformat() if row.closed_at else None,
        "compliance_evidence_id": str(latest_evidence.pk) if latest_evidence else None,
        "available_actions": actions,
    })


def create_money_lending_review(*, actor, payload):
    require(actor, "compliance.money_lending_review.manage")
    if actor.primary_role.role_code != "company_secretary":
        raise ComplianceDenied()
    financial_year = _required(payload, "financial_year")
    state = _required(payload, "state")
    legal = _document(payload, "legal_opinion_document_id")
    board = _document(payload, "board_note_document_id")
    for field, document in (("legal_opinion_document_id", legal), ("board_note_document_id", board)):
        if document.sensitivity_level != DocumentFile.SENSITIVITY_RESTRICTED:
            raise ComplianceInvalid({field: "Document must be restricted."})
    task = ComplianceTask.objects.filter(
        control__control_code="MONEY_LENDING_ANNUAL",
        control__control_area="money_lending",
        task_period=financial_year,
        reviewer_user=actor,
    ).first()
    if task is None:
        raise ComplianceConflict("A matching annual money-lending task is required.")
    evidence = task.evidence_submissions.filter(
        review_status=ComplianceEvidence.REVIEW_ACCEPTED
    ).order_by("-reviewed_at").first()
    if evidence is None:
        raise ComplianceConflict("Accepted task evidence is required before recording review.")
    if evidence.document_id != legal.pk:
        raise ComplianceInvalid({"legal_opinion_document_id": "Must match accepted task evidence."})
    exemption = payload.get("exemption_applicable_flag")
    if not isinstance(exemption, bool):
        raise ComplianceInvalid({"exemption_applicable_flag": "Must be true or false."})
    try:
        with transaction.atomic():
            row = MoneyLendingLawReview.objects.create(
                financial_year=financial_year,
                state=state,
                applicability="exempt" if exemption else "applicable",
                exemption_applicable_flag=exemption,
                legal_opinion_document=legal,
                board_note_document=board,
                task=task,
                evidence=evidence,
                reviewed_by_user=actor,
                remarks=str(payload.get("remarks") or "").strip(),
            )
            _audit(actor, "compliance.money_lending_review.created", row.pk, {
                "financial_year": financial_year, "state": state,
                "task_id": str(task.pk), "evidence_id": str(evidence.pk),
                "exemption_applicable_flag": exemption,
            })
            for document, purpose in ((legal, "money_lending_legal_opinion"), (board, "money_lending_board_note")):
                AuditLog.objects.create(
                    actor_user=actor, actor_type="user",
                    action="compliance.evidence.restricted_file_accessed",
                    entity_type="document_file", entity_id=document.pk,
                    new_value_json={"purpose": purpose, "review_id": str(row.pk)},
                )
    except Exception as exc:
        if MoneyLendingLawReview.objects.filter(financial_year=financial_year, state=state).exists():
            raise ComplianceConflict("Review already exists for this financial year and state.") from exc
        raise
    return {
        "money_lending_law_review_id": str(row.pk), "financial_year": row.financial_year,
        "state": row.state, "applicability": row.applicability,
        "exemption_applicable_flag": row.exemption_applicable_flag,
        "legal_opinion_document_id": str(row.legal_opinion_document_id),
        "board_note_document_id": str(row.board_note_document_id),
        "compliance_task_id": str(row.task_id), "compliance_evidence_id": str(row.evidence_id),
        "reviewed_by_user_id": str(row.reviewed_by_user_id),
        "reviewed_at": row.reviewed_at.isoformat(), "remarks": row.remarks,
        "available_actions": [],
    }


def _control_values(payload):
    required = ("control_code", "control_name", "control_area", "legal_basis", "control_type",
                "frequency", "owner_role_code", "evidence_required", "risk_if_missed", "status")
    values = {field: _required(payload, field) for field in required}
    if values["control_type"] not in ComplianceControl.TYPES:
        raise ComplianceInvalid({"control_type": "Invalid control type."})
    if values["frequency"] not in ComplianceControl.FREQUENCIES:
        raise ComplianceInvalid({"frequency": "Invalid frequency."})
    if values["status"] not in ComplianceControl.STATUSES:
        raise ComplianceInvalid({"status": "Invalid status."})
    values["owner_user"] = _user(payload, "owner_user_id")
    values["reviewer_user"] = _user(payload, "reviewer_user_id")
    values["first_due_date"] = _date(payload, "first_due_date")
    if values["owner_user"].primary_role.role_code != values["owner_role_code"]:
        raise ComplianceInvalid({"owner_user_id": "Owner does not hold owner_role_code."})
    if values["owner_user"].pk == values["reviewer_user"].pk:
        raise ComplianceInvalid({"reviewer_user_id": "Reviewer must differ from owner."})
    return values


def _required(payload, field):
    value = str(payload.get(field) or "").strip()
    if not value:
        raise ComplianceInvalid({field: "This field is required."})
    return value


def _uuid(payload, field):
    return _parse_uuid(payload.get(field), field)


def _parse_uuid(value, field):
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError, AttributeError) as exc:
        raise ComplianceInvalid({field: "Must be a valid UUID."}) from exc


def _user(payload, field):
    try:
        return User.objects.select_related("primary_role").get(pk=_uuid(payload, field))
    except User.DoesNotExist as exc:
        raise ComplianceInvalid({field: "Active user was not found."}) from exc


def _document(payload, field):
    try:
        return DocumentFile.objects.get(pk=_uuid(payload, field))
    except DocumentFile.DoesNotExist as exc:
        raise ComplianceInvalid({field: "Governed document was not found."}) from exc


def _date(payload, field):
    value = payload.get(field)
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError) as exc:
        raise ComplianceInvalid({field: "Must be an ISO date."}) from exc


def _period_for(control, due):
    if control.frequency == ComplianceControl.FREQUENCY_MONTHLY:
        return due.strftime("%Y-%m")
    if control.frequency == ComplianceControl.FREQUENCY_QUARTERLY:
        return f"{due.year}-Q{((due.month - 1) // 3) + 1}"
    if control.frequency == ComplianceControl.FREQUENCY_ANNUAL:
        return f"FY{due.year - 1}-{str(due.year)[-2:]}" if due.month <= 3 else f"FY{due.year}-{str(due.year + 1)[-2:]}"
    return "ongoing"


def _paginate(queryset, query):
    try:
        page = max(1, int(query.get("page", 1)))
        page_size = min(100, max(1, int(query.get("page_size", 20))))
    except (TypeError, ValueError):
        raise ComplianceInvalid({"page": "Pagination values must be positive integers."})
    total = queryset.count()
    pages = max(1, ceil(total / page_size))
    page = min(page, pages)
    rows = list(queryset[(page - 1) * page_size: page * page_size])
    return rows, {"page": page, "page_size": page_size, "total_count": total,
                  "total_pages": pages, "has_next": page < pages, "has_previous": page > 1}


def _audit(actor, action, entity_id, values):
    AuditLog.objects.create(actor_user=actor, actor_type="user", action=action,
                            entity_type=action.rsplit(".", 1)[0].replace(".", "_"),
                            entity_id=entity_id, new_value_json=values)
