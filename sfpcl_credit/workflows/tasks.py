from dataclasses import dataclass
from datetime import datetime, time
from decimal import Decimal, InvalidOperation
from math import ceil
from types import SimpleNamespace
import uuid

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone

from sfpcl_credit.workflows.models import WorkflowTask
from sfpcl_credit.workflows.models import WorkflowTaskComment


class TaskNotFound(Exception):
    pass


class TaskPermissionDenied(Exception):
    pass


@dataclass(frozen=True)
class TaskRule:
    task_type: str
    assigned_role_code: str
    assigned_team_code: str = ""


_APPLICATION_RULES = {
    "submitted": TaskRule(
        WorkflowTask.TYPE_COMPLETENESS_CHECK, "deputy_manager_finance"
    ),
    "reference_generated": TaskRule(
        WorkflowTask.TYPE_APPRAISAL, "deputy_manager_finance"
    ),
    "submitted_to_sanction_committee": TaskRule(
        WorkflowTask.TYPE_SANCTION, "cfo", "sanction_committee"
    ),
}

_ENTITY_RULES = {
    "document_checklist": {
        "in_progress": TaskRule(
            WorkflowTask.TYPE_DOCUMENT_VERIFICATION,
            "compliance_team_member",
            "compliance",
        ),
    },
    "sap_customer_profile_request": {
        "draft": TaskRule(
            WorkflowTask.TYPE_SAP_SETUP,
            "senior_manager_finance",
            "treasury",
        ),
        "sent": TaskRule(
            WorkflowTask.TYPE_SAP_SETUP,
            "senior_manager_finance",
            "treasury",
        ),
    },
    "disbursement": {
        "ready_for_disbursement": TaskRule(
            WorkflowTask.TYPE_DISBURSEMENT,
            "senior_manager_finance",
            "treasury",
        ),
        "pending": TaskRule(
            WorkflowTask.TYPE_DISBURSEMENT,
            "chief_financial_controller",
            "treasury",
        ),
        "authorisation_pending": TaskRule(
            WorkflowTask.TYPE_DISBURSEMENT,
            "chief_financial_controller",
            "treasury",
        ),
        "initiated": TaskRule(
            WorkflowTask.TYPE_DISBURSEMENT,
            "chief_financial_controller",
            "treasury",
        ),
    },
    "repayment": {
        "received": TaskRule(
            WorkflowTask.TYPE_REPAYMENT_POSTING,
            "credit_manager",
            "treasury",
        ),
        "pending_posting": TaskRule(
            WorkflowTask.TYPE_REPAYMENT_POSTING,
            "credit_manager",
            "treasury",
        ),
    },
    "default_case": {
        "grace_period_expired": TaskRule(
            WorkflowTask.TYPE_DEFAULT_REVIEW,
            "credit_manager",
            "credit_assessment",
        ),
        "assessment_in_progress": TaskRule(
            WorkflowTask.TYPE_DEFAULT_REVIEW,
            "credit_manager",
            "credit_assessment",
        ),
    },
}

_LIST_FILTERS = {
    "task_type",
    "due_today",
    "overdue",
    "borrower_type",
    "minimum_amount",
    "special_case",
    "exception_required",
    "assigned_to_user_id",
    "assigned_to_my_team",
    "status",
    "page",
    "page_size",
}
_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100


def task_state_mapping():
    """Return the stable, serializable source state/role mapping."""
    mapping = {}
    for entity_type, rules in {
        "loan_application": _APPLICATION_RULES,
        **_ENTITY_RULES,
    }.items():
        for state, rule in rules.items():
            item = mapping.setdefault(
                rule.task_type,
                {
                    "entity_type": entity_type,
                    "entry_states": [],
                    "assigned_role_code": rule.assigned_role_code,
                    "assigned_team_code": rule.assigned_team_code,
                },
            )
            item["entry_states"].append(state)
    return mapping


def project_workflow_event(event):
    """Project one canonical workflow event into the source-defined task inbox."""
    entity_type, entity_id = _task_owner(event.entity_type, event.entity_id)
    rules = _rules_for(event.entity_type)
    active_rule = rules.get(event.to_state)
    task_types = {rule.task_type for rule in rules.values()}
    if not task_types:
        return None
    if (entity_type, entity_id) != (event.entity_type, event.entity_id):
        _close_tasks(
            event.entity_type,
            event.entity_id,
            task_types,
            event.to_state,
        )

    if active_rule is None:
        _close_tasks(entity_type, entity_id, task_types, event.to_state)
        return None

    _close_tasks(
        entity_type,
        entity_id,
        task_types - {active_rule.task_type},
        event.to_state,
    )
    return _open_task(
        entity_type=entity_type,
        entity_id=entity_id,
        rule=active_rule,
        current_status=event.to_state,
    )


def reconcile_workflow_tasks():
    """Backfill current actionable states and refresh derived SLA standing."""
    from sfpcl_credit.applications.models import LoanApplication
    from sfpcl_credit.approvals.models import ApprovalCase
    from sfpcl_credit.credit.models import LoanAppraisalNote
    from sfpcl_credit.defaults.models import DefaultCase
    from sfpcl_credit.disbursements.models import Disbursement
    from sfpcl_credit.legal_documents.models import DocumentChecklist
    from sfpcl_credit.loans.models import Repayment
    from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest

    refreshed = 0
    for application in LoanApplication.objects.only(
        "loan_application_id", "application_status"
    ).iterator(chunk_size=200):
        task = project_workflow_event(
            SimpleNamespace(
                entity_type="loan_application",
                entity_id=application.pk,
                to_state=application.application_status,
            )
        )
        refreshed += int(task is not None)

    # More-specific owners run after the application projection so review and
    # downstream terminal states close any stale broad application task.
    for note in LoanAppraisalNote.objects.only(
        "loan_appraisal_note_id", "appraisal_status"
    ).iterator(chunk_size=200):
        refreshed += int(
            _project_state("loan_appraisal_note", note.pk, note.appraisal_status)
            is not None
        )
    for case in ApprovalCase.objects.only(
        "approval_case_id", "loan_application_id", "current_status"
    ).iterator(chunk_size=200):
        state = (
            "submitted_to_sanction_committee"
            if case.current_status in {
                ApprovalCase.STATUS_PENDING,
                ApprovalCase.STATUS_RETURNED,
                ApprovalCase.STATUS_BLOCKED_CONFLICT,
            }
            else case.current_status
        )
        refreshed += int(
            _project_state("loan_application", case.loan_application_id, state)
            is not None
        )
    for checklist in DocumentChecklist.objects.only(
        "document_checklist_id", "checklist_status"
    ).iterator(chunk_size=200):
        refreshed += int(
            _project_state("document_checklist", checklist.pk, checklist.checklist_status)
            is not None
        )
    for request in SapCustomerProfileRequest.objects.only(
        "sap_customer_profile_request_id", "request_status"
    ).iterator(chunk_size=200):
        refreshed += int(
            _project_state(
                "sap_customer_profile_request", request.pk, request.request_status
            )
            is not None
        )
    for disbursement in Disbursement.objects.only(
        "disbursement_id", "authorisation_status"
    ).iterator(chunk_size=200):
        state = (
            Disbursement.INITIATED
            if disbursement.authorisation_status == Disbursement.AUTHORISATION_PENDING
            else disbursement.authorisation_status
        )
        refreshed += int(
            _project_state("disbursement", disbursement.pk, state) is not None
        )
    for repayment in Repayment.objects.only(
        "repayment_id", "sap_posting_status"
    ).iterator(chunk_size=200):
        state = (
            "pending_posting"
            if repayment.sap_posting_status == "pending"
            else repayment.sap_posting_status
        )
        refreshed += int(
            _project_state("repayment", repayment.pk, state) is not None
        )
    for default_case in DefaultCase.objects.only(
        "default_case_id", "default_case_status"
    ).iterator(chunk_size=200):
        refreshed += int(
            _project_state(
                "default_case", default_case.pk, default_case.default_case_status
            )
            is not None
        )

    now = timezone.now()
    for task in WorkflowTask.objects.filter(
        status=WorkflowTask.STATUS_OPEN,
        due_at__isnull=False,
    ).only("workflow_task_id", "due_at", "overdue_days"):
        overdue_days = max(
            0,
            (timezone.localdate(now) - timezone.localdate(task.due_at)).days,
        )
        if task.overdue_days != overdue_days:
            task.overdue_days = overdue_days
            task.updated_at = now
            task.save(update_fields=["overdue_days", "updated_at"])
    return {"tasks_opened_or_refreshed": refreshed}


def schedule_task_reconciliation(*, due_at, idempotency_key):
    from sfpcl_credit.scheduler.services import enqueue_scheduled_job

    return enqueue_scheduled_job(
        job_type="workflow_task_reconciliation",
        due_at=due_at,
        idempotency_key=idempotency_key,
    )


def run_task_reconciliation_job(job_id):
    from sfpcl_credit.scheduler import services as scheduler_services

    job = scheduler_services.mark_job_running(job_id)
    if job.job_type != "workflow_task_reconciliation":
        scheduler_services.mark_job_failed(
            job_id, "Scheduled job is not a workflow task reconciliation."
        )
        raise ValidationError(
            {"job_id": "Scheduled job is not a workflow task reconciliation."}
        )
    try:
        result = reconcile_workflow_tasks()
    except Exception as exc:
        scheduler_services.mark_job_failed(job_id, str(exc))
        raise
    scheduler_services.mark_job_succeeded(job_id)
    return result


def task_inbox(*, actor, query_params):
    from sfpcl_credit.identity.modules import auth_service

    unknown = set(query_params.keys()) - _LIST_FILTERS
    if unknown:
        raise ValidationError(
            {field: "Unknown query parameter." for field in sorted(unknown)}
        )
    roles = auth_service.effective_role_codes(actor)
    teams = actor.team_codes()
    queryset = (
        WorkflowTask.objects.select_related("assigned_to_user")
        .filter(
            Q(assigned_to_user=actor)
            | Q(assigned_role_code__in=roles)
            | Q(assigned_team_code__in=teams)
        )
        .order_by("due_at", "-priority", "task_reference")
    )
    status = query_params.get("status") or WorkflowTask.STATUS_OPEN
    if status not in WorkflowTask.STATUSES:
        raise ValidationError({"status": "Must be open or closed."})
    queryset = queryset.filter(status=status)

    task_type = query_params.get("task_type")
    if task_type:
        if task_type not in WorkflowTask.TASK_TYPES:
            raise ValidationError({"task_type": "Unsupported task type."})
        queryset = queryset.filter(task_type=task_type)
    borrower_type = query_params.get("borrower_type")
    if borrower_type:
        queryset = queryset.filter(borrower_type=borrower_type)
    assigned_user_id = query_params.get("assigned_to_user_id")
    if assigned_user_id:
        queryset = queryset.filter(
            assigned_to_user_id=_parse_uuid("assigned_to_user_id", assigned_user_id)
        )
    minimum_amount = query_params.get("minimum_amount")
    if minimum_amount:
        try:
            amount = Decimal(str(minimum_amount))
        except (InvalidOperation, ValueError):
            raise ValidationError(
                {"minimum_amount": "Must be a valid non-negative amount."}
            )
        if amount < 0:
            raise ValidationError(
                {"minimum_amount": "Must be a valid non-negative amount."}
            )
        queryset = queryset.filter(amount__gte=amount)

    today = timezone.localdate()
    start = timezone.make_aware(datetime.combine(today, time.min))
    end = start + timezone.timedelta(days=1)
    if _bool_filter(query_params, "due_today"):
        queryset = queryset.filter(due_at__gte=start, due_at__lt=end)
    if _bool_filter(query_params, "overdue"):
        queryset = queryset.filter(due_at__lt=start)
    for field in ("special_case", "exception_required"):
        parsed = _optional_bool_filter(query_params, field)
        if parsed is not None:
            queryset = queryset.filter(**{field: parsed})
    if _bool_filter(query_params, "assigned_to_my_team"):
        queryset = queryset.filter(assigned_team_code__in=teams)

    page = _positive_int(query_params.get("page"), 1)
    page_size = min(
        _positive_int(query_params.get("page_size"), _DEFAULT_PAGE_SIZE),
        _MAX_PAGE_SIZE,
    )
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    rows = [_serialize_task(task) for task in queryset[offset : offset + page_size]]
    return rows, {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def dashboard_tasks(actor, limit=10):
    from django.db.models import Subquery
    from sfpcl_credit.identity.models import UserTeamMembership
    from sfpcl_credit.identity.modules import auth_service

    active_team_codes = UserTeamMembership.objects.filter(
        user=actor,
        status="active",
        team__status="active",
    ).values("team__team_code")
    rows = (
        WorkflowTask.objects.filter(
            Q(assigned_to_user=actor)
            | Q(assigned_role_code__in=auth_service.effective_role_codes(actor))
            | Q(assigned_team_code__in=Subquery(active_team_codes)),
            status=WorkflowTask.STATUS_OPEN,
        )
        .order_by("due_at", "-priority", "task_reference")
        .values("task_type", "linked_entity_id", "title", "due_at")[:limit]
    )
    return [
        {
            "task_type": row["task_type"],
            "entity_id": str(row["linked_entity_id"]),
            "title": row["title"],
            "due_at": _iso(row["due_at"]),
        }
        for row in rows
    ]


@transaction.atomic
def reassign_task(*, actor, task_id, assigned_to_user_id, request_meta):
    from sfpcl_credit.identity.models import User
    from sfpcl_credit.identity.modules import auth_service

    task = _locked_scoped_task(actor, task_id)
    if "users.team.manage" not in auth_service.effective_permission_codes(actor):
        raise TaskPermissionDenied
    target_id = _parse_uuid("assigned_to_user_id", assigned_to_user_id)
    target = (
        User.objects.select_related("primary_role")
        .filter(pk=target_id, status=User.ACTIVE_STATUS)
        .first()
    )
    if target is None:
        raise ValidationError(
            {"assigned_to_user_id": "Active assignee was not found."}
        )
    if (
        task.assigned_role_code not in target.role_codes()
        and task.assigned_team_code not in target.team_codes()
    ):
        raise ValidationError(
            {
                "assigned_to_user_id": (
                    "Assignee must belong to the task's assigned role or team."
                )
            }
        )
    old_user_id = task.assigned_to_user_id
    task.assigned_to_user = target
    task.updated_at = timezone.now()
    task.save(update_fields=["assigned_to_user", "updated_at"])
    _audit_task_action(
        actor=actor,
        task=task,
        action="workflow_task.reassigned",
        old_value={"assigned_to_user_id": _string_id(old_user_id)},
        new_value={"assigned_to_user_id": str(target.pk)},
        request_meta=request_meta,
    )
    return _serialize_task(task)


@transaction.atomic
def add_task_comment(*, actor, task_id, comment, request_meta):
    task = _locked_scoped_task(actor, task_id)
    cleaned = str(comment or "").strip()
    if not cleaned:
        raise ValidationError({"comment": "This field must not be blank."})
    if len(cleaned) > 4000:
        raise ValidationError({"comment": "Must not exceed 4000 characters."})
    row = WorkflowTaskComment.objects.create(
        task=task,
        author_user=actor,
        comment=cleaned,
    )
    _audit_task_action(
        actor=actor,
        task=task,
        action="workflow_task.commented",
        old_value=None,
        new_value={"workflow_task_comment_id": str(row.pk)},
        request_meta=request_meta,
    )
    return {
        "workflow_task_comment_id": str(row.pk),
        "task_id": str(task.pk),
        "comment": row.comment,
        "created_at": _iso(row.created_at),
    }


@transaction.atomic
def set_task_blocked(*, actor, task_id, blocked, reason, request_meta):
    task = _locked_scoped_task(actor, task_id)
    if blocked:
        cleaned_reason = str(reason or "").strip()
        if not cleaned_reason:
            raise ValidationError({"reason": "This field must not be blank."})
        if len(cleaned_reason) > 4000:
            raise ValidationError({"reason": "Must not exceed 4000 characters."})
    else:
        cleaned_reason = ""
    old_value = {
        "blocked": task.blocked,
        "blocked_reason": task.blocked_reason or None,
    }
    task.blocked = blocked
    task.blocked_reason = cleaned_reason
    task.updated_at = timezone.now()
    task.save(update_fields=["blocked", "blocked_reason", "updated_at"])
    _audit_task_action(
        actor=actor,
        task=task,
        action=("workflow_task.blocked" if blocked else "workflow_task.unblocked"),
        old_value={
            "blocked": old_value["blocked"],
            "blocked_reason_exists": bool(old_value["blocked_reason"]),
        },
        new_value={
            "blocked": task.blocked,
            "blocked_reason_exists": bool(task.blocked_reason),
        },
        request_meta=request_meta,
    )
    return _serialize_task(task)


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}


def _rules_for(entity_type):
    if entity_type == "loan_application":
        return _APPLICATION_RULES
    if entity_type == "loan_appraisal_note":
        return {
            "draft": _APPLICATION_RULES["reference_generated"],
            "submitted_to_sanction_committee": _APPLICATION_RULES[
                "submitted_to_sanction_committee"
            ],
        }
    return _ENTITY_RULES.get(entity_type, {})


def _task_owner(entity_type, entity_id):
    if entity_type == "loan_appraisal_note":
        from sfpcl_credit.credit.models import LoanAppraisalNote

        owner_id = (
            LoanAppraisalNote.objects.filter(pk=entity_id)
            .values_list("loan_application_id", flat=True)
            .first()
        )
        owner_type = "loan_application"
    elif entity_type == "document_checklist":
        from sfpcl_credit.legal_documents.models import DocumentChecklist

        owner_id = (
            DocumentChecklist.objects.filter(pk=entity_id)
            .values_list("loan_application_id", flat=True)
            .first()
        )
        owner_type = "loan_application"
    elif entity_type == "sap_customer_profile_request":
        from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest

        owner_id = (
            SapCustomerProfileRequest.objects.filter(pk=entity_id)
            .values_list("loan_application_id", flat=True)
            .first()
        )
        owner_type = "loan_application"
    elif entity_type == "disbursement":
        from sfpcl_credit.disbursements.models import Disbursement

        owner_id = (
            Disbursement.objects.filter(pk=entity_id)
            .values_list("loan_account_id", flat=True)
            .first()
        )
        owner_type = "loan_account"
    elif entity_type == "repayment":
        from sfpcl_credit.loans.models import Repayment

        owner_id = (
            Repayment.objects.filter(pk=entity_id)
            .values_list("loan_account_id", flat=True)
            .first()
        )
        owner_type = "loan_account"
    elif entity_type == "default_case":
        from sfpcl_credit.defaults.models import DefaultCase

        owner_id = (
            DefaultCase.objects.filter(pk=entity_id)
            .values_list("loan_account_id", flat=True)
            .first()
        )
        owner_type = "loan_account"
    else:
        return entity_type, entity_id
    return (owner_type, owner_id) if owner_id is not None else (entity_type, entity_id)


@transaction.atomic
def _open_task(*, entity_type, entity_id, rule, current_status):
    facts = _entity_facts(entity_type, entity_id, rule.task_type)
    defaults = {
        **facts,
        "assigned_role_code": rule.assigned_role_code,
        "assigned_team_code": rule.assigned_team_code,
        "priority": WorkflowTask.PRIORITY_NORMAL,
        "current_status": current_status,
        "updated_at": timezone.now(),
    }
    try:
        task, created = WorkflowTask.objects.get_or_create(
            linked_entity_type=entity_type,
            linked_entity_id=entity_id,
            task_type=rule.task_type,
            status=WorkflowTask.STATUS_OPEN,
            defaults=defaults,
        )
    except IntegrityError:
        task = WorkflowTask.objects.get(
            linked_entity_type=entity_type,
            linked_entity_id=entity_id,
            task_type=rule.task_type,
            status=WorkflowTask.STATUS_OPEN,
        )
        created = False
    if not created:
        for field, value in defaults.items():
            setattr(task, field, value)
        task.save(update_fields=[*defaults])
    return task


def _close_tasks(entity_type, entity_id, task_types, current_status):
    if not task_types:
        return 0
    now = timezone.now()
    return WorkflowTask.objects.filter(
        linked_entity_type=entity_type,
        linked_entity_id=entity_id,
        task_type__in=task_types,
        status=WorkflowTask.STATUS_OPEN,
    ).update(
        status=WorkflowTask.STATUS_CLOSED,
        current_status=current_status,
        closed_at=now,
        updated_at=now,
    )


def _entity_facts(entity_type, entity_id, task_type):
    if entity_type == "loan_application":
        from sfpcl_credit.applications.models import LoanApplication

        application = (
            LoanApplication.objects.select_related("member")
            .filter(pk=entity_id)
            .first()
        )
        if application is not None:
            due_at = None
            if task_type == WorkflowTask.TYPE_APPRAISAL:
                due_at = application.created_at + timezone.timedelta(days=2)
            reference = application.application_reference_number or str(application.pk)
            from sfpcl_credit.approvals.models import ApprovalCase, GeneralMeetingApproval

            current_case = (
                ApprovalCase.objects.filter(loan_application=application)
                .order_by("-submitted_at", "-approval_case_id")
                .only("exception_required_flag")
                .first()
            )
            return {
                "title": f"{_task_label(task_type)} for {reference}",
                "borrower_name": application.member.display_name,
                "borrower_type": application.borrower_type,
                "amount": application.required_loan_amount,
                "due_at": due_at,
                "exception_required": bool(
                    current_case and current_case.exception_required_flag
                ),
                "special_case": GeneralMeetingApproval.objects.filter(
                    loan_application=application
                ).exists(),
            }
    if entity_type == "loan_account":
        from sfpcl_credit.loans.models import LoanAccount

        account = (
            LoanAccount.objects.select_related("member")
            .filter(pk=entity_id)
            .first()
        )
        if account is not None:
            due_at = _loan_task_due_at(account.pk, task_type)
            return {
                "title": (
                    f"{_task_label(task_type)} for {account.loan_account_number}"
                ),
                "borrower_name": account.member.display_name,
                "borrower_type": account.member.member_type,
                "amount": account.total_outstanding or account.sanctioned_amount,
                "due_at": due_at,
            }
    return {
        "title": f"{_task_label(task_type)} for {entity_id}",
        "borrower_name": "",
        "borrower_type": "",
        "amount": None,
        "due_at": None,
    }


def _task_label(task_type):
    return task_type.replace("_", " ").capitalize()


def _project_state(entity_type, entity_id, to_state):
    return project_workflow_event(
        SimpleNamespace(
            entity_type=entity_type,
            entity_id=entity_id,
            to_state=to_state,
        )
    )


def _loan_task_due_at(loan_account_id, task_type):
    if task_type == WorkflowTask.TYPE_REPAYMENT_POSTING:
        from sfpcl_credit.loans.models import RepaymentSapPostingObligation

        due_date = (
            RepaymentSapPostingObligation.objects.filter(
                repayment__loan_account_id=loan_account_id,
                status="pending",
            )
            .order_by("due_date")
            .values_list("due_date", flat=True)
            .first()
        )
    elif task_type == WorkflowTask.TYPE_DEFAULT_REVIEW:
        from sfpcl_credit.defaults.models import DefaultCase

        due_date = (
            DefaultCase.objects.filter(
                loan_account_id=loan_account_id,
                default_case_status__in=(
                    DefaultCase.STATUS_GRACE_PERIOD_EXPIRED,
                    DefaultCase.STATUS_ASSESSMENT_IN_PROGRESS,
                ),
            )
            .order_by("grace_period_end_date")
            .values_list("grace_period_end_date", flat=True)
            .first()
        )
    else:
        due_date = None
    if due_date is None:
        return None
    return timezone.make_aware(datetime.combine(due_date, time.min))


def _locked_scoped_task(actor, task_id):
    task_uuid = _parse_uuid("task_id", task_id)
    task = (
        WorkflowTask.objects.select_for_update()
        .select_related("assigned_to_user")
        .filter(pk=task_uuid)
        .first()
    )
    if task is None:
        raise TaskNotFound
    if task.status != WorkflowTask.STATUS_OPEN or not _task_in_actor_scope(task, actor):
        raise TaskNotFound
    return task


def _task_in_actor_scope(task, actor):
    from sfpcl_credit.identity.modules import auth_service

    return (
        task.assigned_to_user_id == actor.pk
        or task.assigned_role_code in auth_service.effective_role_codes(actor)
        or task.assigned_team_code in actor.team_codes()
    )


def _audit_task_action(*, actor, task, action, old_value, new_value, request_meta):
    from sfpcl_credit.identity.models import AuditLog

    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=action,
        entity_type="workflow_task",
        entity_id=task.pk,
        old_value_json=old_value,
        new_value_json=new_value,
        ip_address=request_meta.get("ip_address", ""),
        user_agent=request_meta.get("user_agent", ""),
    )


def _string_id(value):
    return str(value) if value is not None else None


def _serialize_task(task):
    assigned_user = None
    if task.assigned_to_user_id:
        assigned_user = {
            "user_id": str(task.assigned_to_user_id),
            "full_name": task.assigned_to_user.full_name,
        }
    due_at = _iso(task.due_at)
    return {
        "task_id": str(task.pk),
        "task_reference": task.task_reference,
        "task_type": task.task_type,
        "title": task.title,
        "application_or_loan_id": str(task.linked_entity_id),
        "linked_entity_type": task.linked_entity_type,
        "borrower": task.borrower_name,
        "borrower_type": task.borrower_type,
        "amount": f"{task.amount:.2f}" if task.amount is not None else None,
        "priority": task.priority,
        "sla_tat": {
            "due_at": due_at,
            "overdue_days": _current_overdue_days(task),
        },
        "current_status": task.current_status,
        "assigned_to": {
            "role_code": task.assigned_role_code,
            "team_code": task.assigned_team_code or None,
            "user": assigned_user,
        },
        "blocked": task.blocked,
        "blocked_reason": task.blocked_reason or None,
        "special_case": task.special_case,
        "exception_required": task.exception_required,
        "created_date": _iso(task.created_at),
        "due_date": due_at,
        "closed_at": _iso(task.closed_at),
        "action": {
            "code": "open",
            "url": f"/tasks/{task.pk}",
        },
    }


def _current_overdue_days(task):
    if task.due_at is None:
        return 0
    return max(
        0,
        (timezone.localdate() - timezone.localdate(task.due_at)).days,
    )


def _iso(value):
    if value is None:
        return None
    return value.isoformat().replace("+00:00", "Z")


def _parse_uuid(field, value):
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValidationError({field: "Must be a valid UUID."}) from exc


def _positive_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _optional_bool_filter(query_params, field):
    value = query_params.get(field)
    if value in (None, ""):
        return None
    lowered = str(value).lower()
    if lowered not in {"true", "false"}:
        raise ValidationError({field: "Must be true or false."})
    return lowered == "true"


def _bool_filter(query_params, field):
    return _optional_bool_filter(query_params, field) is True
