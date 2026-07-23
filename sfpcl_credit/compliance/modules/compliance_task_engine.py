from dataclasses import dataclass
from calendar import monthrange
from datetime import datetime, time

from django.db import transaction
from django.utils import timezone

from sfpcl_credit.communications.models import Notification
from sfpcl_credit.compliance.models import (
    ComplianceControl,
    ComplianceEvidence,
    ComplianceEvidenceReview,
    ComplianceTask,
)
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.scheduler.models import ScheduledJob


@dataclass(frozen=True)
class ComplianceTaskRun:
    created_count: int
    replayed_count: int


class ComplianceTaskEngine:
    SUBMIT_PERMISSION = "compliance.evidence.submit"
    REVIEW_PERMISSION = "compliance.evidence.review"

    @staticmethod
    def create_control(**kwargs):
        from sfpcl_credit.compliance.modules.compliance_control_tracker import create_control
        return create_control(**kwargs)

    @staticmethod
    def list_controls(**kwargs):
        from sfpcl_credit.compliance.modules.compliance_control_tracker import list_controls
        return list_controls(**kwargs)

    @staticmethod
    def update_control(**kwargs):
        from sfpcl_credit.compliance.modules.compliance_control_tracker import update_control
        return update_control(**kwargs)

    @staticmethod
    def create_task(**kwargs):
        from sfpcl_credit.compliance.modules.compliance_control_tracker import create_task
        return create_task(**kwargs)

    @staticmethod
    def list_tasks(**kwargs):
        from sfpcl_credit.compliance.modules.compliance_control_tracker import list_tasks
        return list_tasks(**kwargs)

    @staticmethod
    def update_task(**kwargs):
        from sfpcl_credit.compliance.modules.compliance_control_tracker import update_task
        return update_task(**kwargs)

    @staticmethod
    def serialize_task(*args, **kwargs):
        from sfpcl_credit.compliance.modules.compliance_control_tracker import serialize_task
        return serialize_task(*args, **kwargs)

    @staticmethod
    def create_money_lending_review(**kwargs):
        from sfpcl_credit.compliance.modules.compliance_control_tracker import create_money_lending_review
        return create_money_lending_review(**kwargs)

    @classmethod
    def generate_due_tasks(cls, *, as_of_date):
        job, _created = ScheduledJob.objects.get_or_create(
            idempotency_key=f"compliance-task-generation:{as_of_date.isoformat()}",
            defaults={
                "job_type": "compliance_reminder",
                "status": ScheduledJob.STATUS_RUNNING,
                "due_at": timezone.make_aware(datetime.combine(as_of_date, time.min)),
                "started_at": timezone.now(),
                "attempts": 1,
            },
        )
        created_count = 0
        replayed_count = 0
        controls = ComplianceControl.objects.filter(
            status=ComplianceControl.STATUS_ACTIVE,
            first_due_date__lte=as_of_date,
        ).order_by("control_code")
        try:
            plan = [
                (control, due_date, period)
                for control in controls
                for due_date, period in cls._occurrences(control, as_of_date)
            ]
            cls._validate_replay(plan, as_of_date)
            with transaction.atomic():
                for control, due_date, period in plan:
                    task, created = ComplianceTask.objects.get_or_create(
                        control=control,
                        task_period=period,
                        defaults={
                            "due_date": due_date,
                            "assigned_to_user": control.owner_user,
                            "reviewer_user": control.reviewer_user,
                            "task_status": (
                                ComplianceTask.STATUS_OVERDUE
                                if due_date < as_of_date
                                else ComplianceTask.STATUS_DUE
                            ),
                        },
                    )
                    created_count += int(created)
                    replayed_count += int(not created)
                    if created:
                        cls._record_created(task)
                        if task.task_status == ComplianceTask.STATUS_OVERDUE:
                            cls._queue_overdue_escalation(task)
                        else:
                            cls._queue_due_reminder(task)
                    elif task.task_status == ComplianceTask.STATUS_DUE and due_date < as_of_date:
                        advanced = ComplianceTask.objects.filter(
                            pk=task.pk, task_status=ComplianceTask.STATUS_DUE
                        ).update(
                            task_status=ComplianceTask.STATUS_OVERDUE,
                            updated_at=timezone.now(),
                        )
                        if advanced:
                            task.task_status = ComplianceTask.STATUS_OVERDUE
                            cls._queue_overdue_escalation(task)
                            cls._record_overdue(task)
                from sfpcl_credit.compliance.modules.grievance_workflow import (
                    GrievanceWorkflow,
                )

                GrievanceWorkflow.process_escalations(as_of_date=as_of_date)
                ScheduledJob.objects.filter(pk=job.pk).update(
                    status=ScheduledJob.STATUS_SUCCEEDED,
                    completed_at=timezone.now(),
                    last_error_summary="",
                )
        except Exception as exc:
            ScheduledJob.objects.filter(pk=job.pk).update(
                status=ScheduledJob.STATUS_FAILED,
                completed_at=timezone.now(),
                last_error_summary=str(exc)[:500],
            )
            raise
        return ComplianceTaskRun(created_count, replayed_count)

    @staticmethod
    def _validate_replay(plan, as_of_date):
        for control, due_date, period in plan:
            existing = ComplianceTask.objects.filter(control=control, task_period=period).first()
            if existing is None:
                continue
            if (
                existing.due_date != due_date
                or existing.assigned_to_user_id != control.owner_user_id
                or existing.reviewer_user_id != control.reviewer_user_id
            ):
                raise ValueError("Changed compliance task replay was rejected.")

    @classmethod
    def submit_evidence(cls, *, actor, task_id, payload):
        cls._require_permission(actor, cls.SUBMIT_PERMISSION)
        with transaction.atomic():
            task = ComplianceTask.objects.select_for_update().select_related(
                "assigned_to_user"
            ).get(pk=task_id)
            if task.assigned_to_user_id != actor.pk:
                raise PermissionError("Only the assigned compliance owner may submit evidence.")
            if task.task_status == ComplianceTask.STATUS_COMPLETED:
                raise ValueError("Completed compliance tasks cannot accept new evidence.")
            document = DocumentFile.objects.get(pk=payload.get("document_id"))
            if document.sensitivity_level not in {
                DocumentFile.SENSITIVITY_CONFIDENTIAL,
                DocumentFile.SENSITIVITY_RESTRICTED,
            }:
                raise ValueError("Compliance evidence must use a governed restricted document.")
            source = cls._validated_source_reference(
                actor=actor, task=task, document=document, payload=payload
            )
            evidence_type = str(payload.get("evidence_type") or "").strip()
            summary = str(payload.get("summary") or "").strip()
            if not evidence_type or not summary:
                raise ValueError("Evidence type and summary are required.")
            if task.evidence_submissions.filter(review_status=ComplianceEvidence.REVIEW_PENDING).exists():
                raise ValueError("The task already has evidence pending review.")
            evidence = ComplianceEvidence.objects.create(
                task=task,
                evidence_type=evidence_type,
                document=document,
                summary=summary,
                **source,
                submitted_by_user=actor,
            )
            task.task_status = ComplianceTask.STATUS_EVIDENCE_SUBMITTED
            task.current_evidence = evidence
            task.save(update_fields=["task_status", "current_evidence", "updated_at"])
            cls._audit(
                actor=actor,
                action="compliance.evidence.submitted",
                entity_type="compliance_evidence",
                entity_id=evidence.pk,
                values={"task_id": str(task.pk), "document_id": str(document.pk)},
            )
            cls._audit(
                actor=actor, action="compliance.evidence.restricted_file_accessed",
                entity_type="document_file", entity_id=document.pk,
                values={"purpose": "compliance_evidence_submit", "task_id": str(task.pk)},
            )
        return task

    @classmethod
    def review_evidence(cls, *, actor, task_id, decision, comments, evidence_id=None):
        cls._require_permission(actor, cls.REVIEW_PERMISSION)
        decision = str(decision or "").strip().lower()
        comments = str(comments or "").strip()
        if decision not in {ComplianceEvidence.REVIEW_ACCEPTED, ComplianceEvidence.REVIEW_REJECTED}:
            raise ValueError("Review decision must be accepted or rejected.")
        if not comments:
            raise ValueError("Review comments are required.")
        with transaction.atomic():
            task = ComplianceTask.objects.select_for_update().get(pk=task_id)
            if task.reviewer_user_id != actor.pk:
                raise PermissionError("Only the configured reviewer may review evidence.")
            pending = task.evidence_submissions.select_for_update().filter(
                review_status=ComplianceEvidence.REVIEW_PENDING
            )
            if evidence_id is not None:
                pending = pending.filter(pk=evidence_id)
            evidence = pending.order_by("-submitted_at").first()
            if evidence is None:
                raise ValueError("No pending evidence exists for this task.")
            if evidence.submitted_by_user_id == actor.pk:
                raise PermissionError("Evidence maker and checker must be distinct.")
            reviewed_at = timezone.now()
            ComplianceEvidence.objects.filter(pk=evidence.pk).update(
                review_status=decision,
                reviewed_by_user=actor,
                reviewed_at=reviewed_at,
                review_comments=comments,
            )
            ComplianceEvidenceReview.objects.create(
                evidence=evidence,
                decision=decision,
                comments=comments,
                reviewed_by_user=actor,
                reviewed_at=reviewed_at,
            )
            if decision == ComplianceEvidence.REVIEW_ACCEPTED:
                task.task_status = ComplianceTask.STATUS_COMPLETED
                task.closed_at = reviewed_at
            else:
                task.task_status = (
                    ComplianceTask.STATUS_OVERDUE
                    if task.due_date < timezone.localdate()
                    else ComplianceTask.STATUS_DUE
                )
            task.save(update_fields=["task_status", "closed_at", "current_evidence", "updated_at"])
            cls._audit(
                actor=actor,
                action="compliance.evidence.reviewed",
                entity_type="compliance_evidence",
                entity_id=evidence.pk,
                values={"task_id": str(task.pk), "review_status": decision},
            )
        return task

    @staticmethod
    def _require_permission(actor, permission):
        if permission not in auth_service.effective_permission_codes(actor):
            raise PermissionError(f"{permission} permission is required.")

    @staticmethod
    def _validated_source_reference(*, actor, task, document, payload):
        if document.uploaded_by_user_id == actor.pk:
            return {
                "source_owner": "documents",
                "source_entity_type": "document_file",
                "source_entity_id": document.pk,
                "source_period": task.task_period,
            }
        source_owner = str(payload.get("source_owner") or "").strip()
        source_entity_type = str(payload.get("source_entity_type") or "").strip()
        from sfpcl_credit.closure import compliance_evidence_facade as archive_facade
        from sfpcl_credit.legal_documents import compliance_evidence_facade as stamp_facade
        from sfpcl_credit.recovery import compliance_evidence_facade as recovery_facade
        allowed = {
            "stamp_duty": ("stamp_duty_record", stamp_facade.contains_document),
            "recovery": ("recovery_action", recovery_facade.contains_document),
            "archive": ("archive_record", archive_facade.contains_document),
        }
        if source_owner not in allowed:
            raise ValueError("Foreign evidence requires a governed source owner.")
        expected_type, contains_document = allowed[source_owner]
        if source_entity_type != expected_type:
            raise ValueError("Foreign evidence source type does not match its owner.")
        try:
            source_entity_id = __import__("uuid").UUID(str(payload.get("source_entity_id")))
        except (TypeError, ValueError, AttributeError) as exc:
            raise ValueError("Foreign evidence source identity is invalid.") from exc
        if not contains_document(source_id=source_entity_id, document=document):
            raise ValueError("Foreign evidence document does not belong to its source record.")
        return {
            "source_owner": source_owner, "source_entity_type": source_entity_type,
            "source_entity_id": source_entity_id, "source_period": task.task_period,
        }

    @staticmethod
    def _audit(*, actor, action, entity_type, entity_id, values):
        AuditLog.objects.create(
            actor_user=actor,
            actor_type="user",
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            new_value_json=values,
        )

    @classmethod
    def _occurrences(cls, control, as_of_date):
        if control.frequency == ComplianceControl.FREQUENCY_ONGOING:
            return [(control.first_due_date, "ongoing")]
        step = {
            ComplianceControl.FREQUENCY_MONTHLY: 1,
            ComplianceControl.FREQUENCY_QUARTERLY: 3,
            ComplianceControl.FREQUENCY_ANNUAL: 12,
        }[control.frequency]
        occurrences = []
        offset = 0
        while True:
            due = cls._add_months(control.first_due_date, offset)
            if due > as_of_date:
                return occurrences
            if control.frequency == ComplianceControl.FREQUENCY_MONTHLY:
                period = due.strftime("%Y-%m")
            elif control.frequency == ComplianceControl.FREQUENCY_QUARTERLY:
                period = f"{due.year}-Q{((due.month - 1) // 3) + 1}"
            else:
                period = cls._financial_year(due)
            occurrences.append((due, period))
            offset += step

    @staticmethod
    def _add_months(value, months):
        month_index = value.month - 1 + months
        year = value.year + month_index // 12
        month = month_index % 12 + 1
        day = min(value.day, monthrange(year, month)[1])
        return value.replace(year=year, month=month, day=day)

    @staticmethod
    def _financial_year(due):
        if due.month <= 3:
            return f"FY{due.year - 1}-{str(due.year)[-2:]}"
        return f"FY{due.year}-{str(due.year + 1)[-2:]}"

    @staticmethod
    def _record_created(task):
        AuditLog.objects.create(
            actor_user=None,
            actor_type="system",
            action="compliance.task.generated",
            entity_type="compliance_task",
            entity_id=task.pk,
            new_value_json={
                "control_id": str(task.control_id),
                "task_period": task.task_period,
                "due_date": task.due_date.isoformat(),
                "task_status": task.task_status,
            },
        )

    @staticmethod
    def _queue_overdue_escalation(task):
        locked = ComplianceTask.objects.select_for_update().get(pk=task.pk)
        if locked.overdue_notification_id:
            return
        notification = Notification.objects.create(
            notification_type="compliance_overdue", related_entity_type="compliance_task",
            related_entity_id=task.pk, recipient_user=task.reviewer_user,
            category="Compliance", severity=Notification.SEVERITY_WARNING,
            title=f"Overdue compliance control: {task.control.control_name}",
            message=f"Evidence for {task.task_period} is overdue.",
            action_label="Review compliance task", action_url=f"/compliance/tasks/{task.pk}",
            recipient_role_code=task.reviewer_user.primary_role.role_code,
        )
        ComplianceTask.objects.filter(pk=task.pk, overdue_notification__isnull=True).update(
            overdue_notification=notification
        )

    @staticmethod
    def _queue_due_reminder(task):
        locked = ComplianceTask.objects.select_for_update().get(pk=task.pk)
        if locked.due_notification_id:
            return
        notification = Notification.objects.create(
            notification_type="compliance_due", related_entity_type="compliance_task",
            related_entity_id=task.pk, recipient_user=task.assigned_to_user,
            category="Compliance", severity=Notification.SEVERITY_INFO,
            title=f"Compliance control due: {task.control.control_name}",
            message=f"Evidence for {task.task_period} is due on {task.due_date.isoformat()}.",
            action_label="Submit compliance evidence", action_url=f"/compliance/tasks/{task.pk}",
            recipient_role_code=task.assigned_to_user.primary_role.role_code,
        )
        ComplianceTask.objects.filter(pk=task.pk, due_notification__isnull=True).update(
            due_notification=notification
        )

    @staticmethod
    def _record_overdue(task):
        AuditLog.objects.create(
            actor_user=None, actor_type="system", action="compliance.task.escalated",
            entity_type="compliance_task", entity_id=task.pk,
            new_value_json={"task_status": "overdue", "task_period": task.task_period},
        )


__all__ = ["ComplianceTaskEngine", "ComplianceTaskRun"]
