from dataclasses import dataclass
from datetime import datetime, time, timedelta
import hashlib
from math import ceil

from django.db import models, transaction
from django.utils import timezone

from sfpcl_credit.communications.models import Notification
from sfpcl_credit.compliance.models import ComplianceControl, ComplianceTask, KYCReview
from sfpcl_credit.identity.models import AuditLog, User
from sfpcl_credit.members.models import KycProfile, Member
from sfpcl_credit.scheduler.models import ScheduledJob


@dataclass(frozen=True)
class KYCReviewRun:
    created_count: int
    replayed_count: int


class KYCReviewTracker:
    CONTROL_CODE = "KYC_AML"
    MANAGE_PERMISSION = "compliance.kyc_review.manage"

    @classmethod
    def list_reviews(cls, *, actor, query):
        from sfpcl_credit.compliance.modules.compliance_control_tracker import (
            ComplianceInvalid,
            require_auditor_scope,
        )
        from sfpcl_credit.identity.modules import auth_service
        from sfpcl_credit.members.modules.member_authority import member_scope_predicate

        require_auditor_scope(actor)
        allowed = {
            "status",
            "due_within_days",
            "member_type",
            "member_status",
            "assigned_to_me",
            "page",
            "page_size",
        }
        unknown = set(query.keys()) - allowed
        if unknown:
            raise ComplianceInvalid({field: "Unsupported KYC review filter." for field in unknown})
        permissions = set(auth_service.effective_permission_codes(actor))
        queryset = KYCReview.objects.select_related("member", "task")
        if cls.MANAGE_PERMISSION in permissions:
            queryset = queryset.filter(
                member__in=Member.objects.filter(
                    member_scope_predicate(actor_user=actor, permission=cls.MANAGE_PERMISSION)
                )
            )
        elif (
            "compliance.task.read" in permissions
            and actor.primary_role.role_code
            in {"compliance_team_member", "cfo", "internal_auditor"}
        ):
            if actor.primary_role.role_code != "internal_auditor":
                queryset = queryset.filter(
                    models.Q(task__assigned_to_user=actor)
                    | models.Q(task__reviewer_user=actor)
                )
        else:
            raise PermissionError("KYC review authority is required.")
        status = str(query.get("status") or "").strip()
        if status:
            if status not in KYCReview.STATUSES:
                raise ComplianceInvalid({"status": "Unsupported KYC review status."})
            queryset = queryset.filter(status=status)
        due_within = str(query.get("due_within_days") or "").strip()
        if due_within:
            if due_within != "30":
                raise ComplianceInvalid({"due_within_days": "Only the governed 30-day window is supported."})
            as_of = timezone.localdate()
            queryset = queryset.filter(
                due_date__gte=as_of,
                due_date__lte=as_of + timedelta(days=30),
            ).exclude(status=KYCReview.STATUS_COMPLETED)
        member_type = str(query.get("member_type") or "").strip()
        if member_type:
            if member_type not in Member.MEMBER_TYPES:
                raise ComplianceInvalid({"member_type": "Unsupported member type."})
            queryset = queryset.filter(member__member_type=member_type)
        member_status = str(query.get("member_status") or "").strip()
        if member_status:
            if member_status not in Member.MEMBERSHIP_STATUSES:
                raise ComplianceInvalid({"member_status": "Unsupported member status."})
            queryset = queryset.filter(member__membership_status=member_status)
        assigned = str(query.get("assigned_to_me") or "").strip().lower()
        if assigned:
            if assigned not in {"true", "false"}:
                raise ComplianceInvalid({"assigned_to_me": "Must be true or false."})
            if assigned == "true":
                queryset = queryset.filter(task__assigned_to_user=actor)
        try:
            page = int(query.get("page", 1))
            page_size = int(query.get("page_size", 20))
        except (TypeError, ValueError) as exc:
            raise ComplianceInvalid({"page": "Pagination values must be positive integers."}) from exc
        if page < 1 or page_size < 1 or page_size > 100:
            raise ComplianceInvalid({"page": "Pagination values are out of range."})
        queryset = queryset.order_by("due_date", "kyc_review_id")
        total = queryset.count()
        pages = max(1, ceil(total / page_size))
        rows = queryset[(page - 1) * page_size : page * page_size]
        pagination = {
            "page": page,
            "page_size": page_size,
            "total_count": total,
            "total_pages": pages,
            "has_next": page < pages,
            "has_previous": page > 1,
        }
        return [cls._serialize_summary(row, actor) for row in rows], pagination

    @classmethod
    def search_reviews(cls, *, actor, search, member_ids):
        """Canonical object-scoped KYC selector for safe search projections."""
        from sfpcl_credit.compliance.modules.compliance_control_tracker import (
            require_auditor_scope,
        )
        from sfpcl_credit.identity.modules import auth_service
        from sfpcl_credit.members.modules.member_authority import member_scope_predicate

        require_auditor_scope(actor)
        permissions = set(auth_service.effective_permission_codes(actor))
        queryset = KYCReview.objects.select_related(
            "member", "task__assigned_to_user", "reviewed_by_user"
        )
        if cls.MANAGE_PERMISSION in permissions:
            queryset = queryset.filter(
                member__in=Member.objects.filter(
                    member_scope_predicate(
                        actor_user=actor, permission=cls.MANAGE_PERMISSION
                    )
                )
            )
        elif (
            "compliance.task.read" in permissions
            and actor.primary_role.role_code
            in {"compliance_team_member", "cfo", "internal_auditor"}
        ):
            if actor.primary_role.role_code != "internal_auditor":
                queryset = queryset.filter(
                    models.Q(task__assigned_to_user=actor)
                    | models.Q(task__reviewer_user=actor)
                )
        else:
            return queryset.none()
        return queryset.filter(
            models.Q(member__display_name__icontains=search)
            | models.Q(member__legal_name__icontains=search)
            | models.Q(member__member_number__icontains=search)
            | models.Q(member_id__in=member_ids)
        ).order_by("due_date", "kyc_review_id")

    @classmethod
    def _serialize_summary(cls, review, actor):
        from sfpcl_credit.compliance.modules.compliance_control_tracker import (
            auditor_read_projection,
        )
        from sfpcl_credit.identity.modules import auth_service

        today = timezone.localdate()
        days_overdue = max(0, (today - review.due_date).days)
        actions = []
        if (
            cls.MANAGE_PERMISSION in auth_service.effective_permission_codes(actor)
            and review.task.assigned_to_user_id == actor.pk
            and review.status != KYCReview.STATUS_COMPLETED
        ):
            actions = ["complete", "send_reminder", "assign"]
        return auditor_read_projection(actor, {
            "kyc_review_id": str(review.pk),
            "member_id": str(review.member_id),
            "member_name": review.member.display_name,
            "member_type": review.member.member_type,
            "member_status": review.member.membership_status,
            "kyc_status": review.kyc_status_after or review.kyc_status_before,
            "risk_rating": review.completeness_snapshot_json.get("risk_rating"),
            "due_date": review.due_date.isoformat(),
            "days_overdue": days_overdue,
            "status": review.status,
            "assigned_to_user_id": str(review.task.assigned_to_user_id),
            "completeness": review.completeness_snapshot_json,
            "available_actions": actions,
        })

    @classmethod
    def generate_due_reviews(cls, *, as_of_date):
        job, _created = ScheduledJob.objects.get_or_create(
            idempotency_key=f"kyc-review-generation:{as_of_date.isoformat()}",
            defaults={
                "job_type": "kyc_review_generation",
                "status": ScheduledJob.STATUS_RUNNING,
                "due_at": timezone.make_aware(datetime.combine(as_of_date, time.min)),
                "started_at": timezone.now(),
                "attempts": 1,
            },
        )
        created_count = 0
        replayed_count = 0
        try:
            control = ComplianceControl.objects.select_related(
                "owner_user", "reviewer_user"
            ).get(control_code=cls.CONTROL_CODE, status=ComplianceControl.STATUS_ACTIVE)
            profiles = KycProfile.objects.filter(
                party_type="member",
                last_verified_at__isnull=False,
                party_id__in=Member.objects.filter(is_deleted=False).values("member_id"),
            ).order_by("party_id")
            for profile in profiles:
                due_date = cls._two_years_after(profile.last_verified_at.date())
                if due_date > as_of_date + timedelta(days=30):
                    continue
                member = Member.objects.get(pk=profile.party_id)
                cycle_key = cls._cycle_key(profile)
                task_period = cls._task_period(member, cycle_key)
                status = cls._status(due_date, as_of_date)
                completeness = cls._completeness(member, profile)
                with transaction.atomic():
                    task, task_created = ComplianceTask.objects.get_or_create(
                        control=control,
                        task_period=task_period,
                        defaults={
                            "due_date": due_date,
                            "assigned_to_user": control.owner_user,
                            "reviewer_user": control.reviewer_user,
                            "task_status": (
                                ComplianceTask.STATUS_OVERDUE
                                if status == KYCReview.STATUS_OVERDUE
                                else ComplianceTask.STATUS_DUE
                            ),
                        },
                    )
                    cls._validate_task_replay(task, control, due_date)
                    review, created = KYCReview.objects.get_or_create(
                        member=member,
                        cycle_key=cycle_key,
                        defaults={
                            "kyc_profile": profile,
                            "review_type": KYCReview.TYPE_REKYC,
                            "source_verified_at": profile.last_verified_at,
                            "due_date": due_date,
                            "kyc_status_before": profile.kyc_status,
                            "status": status,
                            "completeness_snapshot_json": completeness,
                            "task": task,
                        },
                    )
                    cls._validate_review_replay(review, profile, task, due_date, completeness)
                    if created:
                        cls._queue_reminder(review, task, overdue=status == KYCReview.STATUS_OVERDUE)
                        cls._audit(review, "compliance.kyc_review.generated")
                    created_count += int(created)
                    replayed_count += int(not created)
                    if not task_created and not created and review.status != KYCReview.STATUS_COMPLETED:
                        if (
                            status == KYCReview.STATUS_OVERDUE
                            and task.task_status == ComplianceTask.STATUS_DUE
                        ):
                            advanced = ComplianceTask.objects.filter(
                                pk=task.pk, task_status=ComplianceTask.STATUS_DUE
                            ).update(task_status=ComplianceTask.STATUS_OVERDUE)
                            if advanced:
                                task.task_status = ComplianceTask.STATUS_OVERDUE
                                cls._queue_reminder(review, task, overdue=True)
                                cls._audit(review, "compliance.kyc_review.overdue")
                        KYCReview.objects.filter(pk=review.pk).update(status=status)
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
        return KYCReviewRun(created_count=created_count, replayed_count=replayed_count)

    @classmethod
    def complete(cls, *, actor, review_id):
        cls._require_member_authority(actor=actor, review_id=review_id)
        with transaction.atomic():
            review = KYCReview.objects.select_for_update().select_related(
                "member", "kyc_profile", "task"
            ).get(pk=review_id)
            if review.status == KYCReview.STATUS_COMPLETED:
                return cls.serialize(review)
            profile = KycProfile.objects.select_for_update().get(pk=review.kyc_profile_id)
            if (
                profile.kyc_status != "verified"
                or profile.last_verified_at is None
                or profile.last_verified_at <= review.source_verified_at
                or profile.last_verified_by_user_id is None
            ):
                raise ValueError("A newer governed KYC verification is required.")
            current_completeness = cls._completeness(review.member, profile)
            if not current_completeness["complete"]:
                raise ValueError("The newer governed KYC verification remains incomplete.")
            evidence = list(
                profile.documents.filter(
                    verification_status="verified",
                    verified_at=profile.last_verified_at,
                    verified_by_user_id=profile.last_verified_by_user_id,
                ).order_by("kyc_document_id")
            )
            if not evidence:
                raise ValueError("A newer governed KYC verification record is required.")
            completed_at = timezone.now()
            evidence_links = [
                {
                    "kyc_document_id": str(item.pk),
                    "document_id": str(item.document_file_id),
                }
                for item in evidence
            ]
            KYCReview.objects.filter(
                pk=review.pk, status__in=(
                    KYCReview.STATUS_PENDING,
                    KYCReview.STATUS_WARNING,
                    KYCReview.STATUS_DUE,
                    KYCReview.STATUS_OVERDUE,
                )
            ).update(
                status=KYCReview.STATUS_COMPLETED,
                completed_at=completed_at,
                completion_verified_at=profile.last_verified_at,
                kyc_status_after=profile.kyc_status,
                reviewed_by_user_id=profile.last_verified_by_user_id,
                completion_evidence_json=evidence_links,
            )
            ComplianceTask.objects.filter(
                pk=review.task_id,
                task_status__in=(ComplianceTask.STATUS_DUE, ComplianceTask.STATUS_OVERDUE),
            ).update(
                task_status=ComplianceTask.STATUS_COMPLETED,
                closed_at=completed_at,
            )
            review.refresh_from_db()
            cls._audit(
                review,
                "compliance.kyc_review.completed",
                actor=actor,
                extra={
                    "completion_verified_at": profile.last_verified_at.isoformat(),
                    "kyc_document_ids": [str(item.pk) for item in evidence],
                    "completion_requirements": current_completeness,
                },
            )
            return cls.serialize(review)

    @classmethod
    def retrieve(cls, *, actor, review_id):
        cls._require_read_authority(actor=actor, review_id=review_id)
        review = KYCReview.objects.select_related("member", "task").get(pk=review_id)
        data = cls.serialize(review)
        data.update(
            {
                "member_name": review.member.display_name,
                "member_type": review.member.member_type,
                "member_status": review.member.membership_status,
                "assigned_to_user_id": str(review.task.assigned_to_user_id),
                "reviewer_user_id": str(review.task.reviewer_user_id),
                "delivery_status": cls._delivery_status(review),
            }
        )
        return data

    @classmethod
    def assign(cls, *, actor, review_id, assigned_to_user_id):
        from sfpcl_credit.compliance.modules.compliance_control_tracker import (
            ComplianceInvalid,
        )
        from sfpcl_credit.members.modules.member_authority import evaluate_member_authority

        cls._require_member_authority(actor=actor, review_id=review_id)
        try:
            assignee = User.objects.select_related("primary_role").get(pk=assigned_to_user_id)
        except (User.DoesNotExist, ValueError, TypeError) as exc:
            raise ComplianceInvalid(
                {"assigned_to_user_id": "An active KYC owner is required."}
            ) from exc
        if assignee.status != "active" or assignee.primary_role.status != "active":
            raise ComplianceInvalid(
                {"assigned_to_user_id": "An active KYC owner is required."}
            )
        with transaction.atomic():
            review = KYCReview.objects.select_for_update().select_related(
                "member", "task"
            ).get(pk=review_id)
            task = ComplianceTask.objects.select_for_update().get(pk=review.task_id)
            if review.status == KYCReview.STATUS_COMPLETED:
                raise ValueError("Completed KYC reviews cannot be assigned.")
            if task.assigned_to_user_id != actor.pk:
                raise PermissionError("Only the assigned KYC owner may reassign the review.")
            if assignee.pk == task.reviewer_user_id:
                raise ComplianceInvalid(
                    {"assigned_to_user_id": "Assignee must differ from the reviewer."}
                )
            authority = evaluate_member_authority(
                actor_user=assignee,
                member=review.member,
                permission=cls.MANAGE_PERMISSION,
            )
            if not authority.allowed:
                raise ComplianceInvalid(
                    {"assigned_to_user_id": "Assignee lacks KYC authority for this member."}
                )
            previous = task.assigned_to_user_id
            task.assigned_to_user = assignee
            task.save(update_fields=["assigned_to_user", "updated_at"])
            review.task = task
            cls._audit(
                review,
                "compliance.kyc_review.assigned",
                actor=actor,
                extra={
                    "previous_assigned_to_user_id": str(previous),
                    "assigned_to_user_id": str(assignee.pk),
                },
            )
            return cls.retrieve(actor=assignee, review_id=review.pk)

    @classmethod
    def send_reminder(cls, *, actor, review_id, idempotency_key, request):
        from sfpcl_credit.communications.models import Communication
        from sfpcl_credit.communications.modules.communication_dispatcher import (
            CommunicationDispatcher,
        )

        cls._require_member_authority(actor=actor, review_id=review_id)
        review = KYCReview.objects.select_related("member", "task").get(pk=review_id)
        if review.task.assigned_to_user_id != actor.pk:
            raise PermissionError("Only the assigned KYC owner may send a reminder.")
        if review.status not in {
            KYCReview.STATUS_WARNING,
            KYCReview.STATUS_DUE,
            KYCReview.STATUS_OVERDUE,
        }:
            raise ValueError("Only due or overdue KYC reviews can send reminders.")
        if review.member.email:
            channel = Communication.CHANNEL_EMAIL
            address = review.member.email
            template_code = "kyc_rekyc_request_email"
        elif review.member.mobile_number:
            channel = Communication.CHANNEL_SMS
            address = review.member.mobile_number
            template_code = "kyc_rekyc_request_sms"
        else:
            raise ValueError("The member has no governed reminder destination.")
        queued = CommunicationDispatcher.queue_from_template(
            actor=actor,
            template_code=template_code,
            recipient={
                "party_type": "member",
                "party_id": review.member_id,
                "address": address,
                "channel": channel,
            },
            context={
                "merge_data": {
                    "member_name": review.member.display_name,
                    "due_date": review.due_date.isoformat(),
                    "status": review.status,
                },
                "idempotency_key": idempotency_key,
                "request": request,
            },
            related_entity={"type": "kyc_review", "id": review.pk},
            delivery_idempotency_key=idempotency_key,
        )
        if not AuditLog.objects.filter(
            action="compliance.kyc_review.reminder_queued",
            entity_id=review.pk,
            new_value_json__communication_id=str(queued.communication_id),
        ).exists():
            cls._audit(
                review,
                "compliance.kyc_review.reminder_queued",
                actor=actor,
                extra={
                    "communication_id": str(queued.communication_id),
                    "communication_job_id": str(queued.communication_job_id),
                    "delivery_status": queued.delivery_status,
                    "channel": channel,
                },
            )
        return {
            "kyc_review_id": str(review.pk),
            "communication_id": str(queued.communication_id),
            "communication_job_id": str(queued.communication_job_id),
            "delivery_status": queued.delivery_status,
            "channel": channel,
        }

    @staticmethod
    def _delivery_status(review):
        from sfpcl_credit.communications.models import Communication, CommunicationDeliveryJob

        communication_ids = Communication.objects.filter(
            related_entity_type="kyc_review",
            related_entity_id=review.pk,
        ).values("communication_id")
        job = CommunicationDeliveryJob.objects.filter(
            communication_id__in=communication_ids,
        ).order_by("-created_at").first()
        if job is None:
            return None
        return {
            CommunicationDeliveryJob.STATUS_SENT: "sent",
            CommunicationDeliveryJob.STATUS_FAILED: "failed",
        }.get(job.status, "queued")

    @classmethod
    def _require_member_authority(cls, *, actor, review_id):
        from sfpcl_credit.identity.modules import auth_service
        from sfpcl_credit.members.modules.member_authority import evaluate_member_authority

        if cls.MANAGE_PERMISSION not in auth_service.effective_permission_codes(actor):
            raise PermissionError("KYC review management authority is required.")
        review = KYCReview.objects.select_related("member").filter(pk=review_id).first()
        if review is None:
            raise KYCReview.DoesNotExist
        authority = evaluate_member_authority(
            actor_user=actor,
            member=review.member,
            permission=cls.MANAGE_PERMISSION,
        )
        if not authority.allowed:
            raise PermissionError("KYC review member scope is required.")

    @classmethod
    def _require_read_authority(cls, *, actor, review_id):
        from sfpcl_credit.compliance.modules.compliance_control_tracker import (
            require_auditor_scope,
        )
        from sfpcl_credit.identity.modules import auth_service

        require_auditor_scope(actor)
        permissions = set(auth_service.effective_permission_codes(actor))
        if cls.MANAGE_PERMISSION in permissions:
            cls._require_member_authority(actor=actor, review_id=review_id)
            return
        review = KYCReview.objects.select_related("task").filter(pk=review_id).first()
        if review is None:
            raise KYCReview.DoesNotExist
        role = actor.primary_role.role_code
        if "compliance.task.read" not in permissions or role not in {
            "compliance_team_member",
            "cfo",
            "internal_auditor",
        }:
            raise PermissionError("KYC review read authority is required.")
        if role != "internal_auditor" and actor.pk not in {
            review.task.assigned_to_user_id,
            review.task.reviewer_user_id,
        }:
            raise PermissionError("KYC review read scope is required.")

    @staticmethod
    def serialize(review):
        return {
            "kyc_review_id": str(review.pk),
            "member_id": str(review.member_id),
            "kyc_profile_id": str(review.kyc_profile_id),
            "review_type": review.review_type,
            "due_date": review.due_date.isoformat(),
            "status": review.status,
            "kyc_status_before": review.kyc_status_before,
            "kyc_status_after": review.kyc_status_after,
            "completed_at": review.completed_at.isoformat() if review.completed_at else None,
            "completion_verified_at": (
                review.completion_verified_at.isoformat()
                if review.completion_verified_at
                else None
            ),
            "reviewed_by_user_id": (
                str(review.reviewed_by_user_id) if review.reviewed_by_user_id else None
            ),
            "completeness": review.completeness_snapshot_json,
            "completion_evidence": review.completion_evidence_json,
            "compliance_task_id": str(review.task_id),
        }

    @staticmethod
    def _two_years_after(value):
        try:
            return value.replace(year=value.year + 2)
        except ValueError:
            return value.replace(month=2, day=28, year=value.year + 2)

    @staticmethod
    def _cycle_key(profile):
        return f"{profile.kyc_profile_id}:{profile.last_verified_at.isoformat()}"

    @staticmethod
    def _task_period(member, cycle_key):
        digest = hashlib.sha256(f"{member.pk}:{cycle_key}".encode()).hexdigest()[:24]
        return f"RK-{digest}"

    @staticmethod
    def _status(due_date, as_of_date):
        if due_date < as_of_date:
            return KYCReview.STATUS_OVERDUE
        if due_date == as_of_date:
            return KYCReview.STATUS_DUE
        if due_date <= as_of_date + timedelta(days=30):
            return KYCReview.STATUS_WARNING
        return KYCReview.STATUS_PENDING

    @staticmethod
    def _completeness(member, profile):
        verified_types = set(
            profile.documents.filter(verification_status="verified").values_list(
                "document_type", flat=True
            )
        )
        required_types = {"pan", "aadhaar", "photo"}
        missing = sorted(required_types - verified_types)
        if not member.pan_encrypted or "pan" not in verified_types:
            missing = sorted(set(missing) | {"pan"})
        if not profile.ckyc_consent_flag:
            missing.append("ckyc_consent")
        if member.member_type in {"fpc", "producer_institution"} and not (
            profile.beneficial_ownership_verified_flag
        ):
            missing.append("beneficial_ownership")
        if member.nominees.exclude(kyc_status="verified").exists():
            missing.append("nominee_kyc")
        if not profile.risk_rating:
            missing.append("risk_rating")
        missing = sorted(set(missing))
        return {
            "complete": not missing,
            "missing_requirements": missing,
            "member_type": member.member_type,
            "member_status": member.membership_status,
            "pan_status": (
                "verified"
                if member.pan_encrypted and "pan" in verified_types
                else "missing"
            ),
            "ckyc_consent_status": (
                "available" if profile.ckyc_consent_flag else "missing"
            ),
            "beneficial_ownership_status": (
                "verified"
                if profile.beneficial_ownership_verified_flag
                else (
                    "missing"
                    if member.member_type in {"fpc", "producer_institution"}
                    else "not_applicable"
                )
            ),
            "nominee_kyc_status": (
                "incomplete"
                if member.nominees.exclude(kyc_status="verified").exists()
                else "complete"
            ),
            "risk_rating": profile.risk_rating,
            "verified_document_types": sorted(verified_types),
        }

    @staticmethod
    def _validate_task_replay(task, control, due_date):
        if (
            task.due_date != due_date
            or task.assigned_to_user_id != control.owner_user_id
            or task.reviewer_user_id != control.reviewer_user_id
        ):
            raise ValueError("Changed re-KYC task replay was rejected.")

    @staticmethod
    def _validate_review_replay(review, profile, task, due_date, completeness):
        if (
            review.kyc_profile_id != profile.pk
            or review.source_verified_at != profile.last_verified_at
            or review.due_date != due_date
            or review.task_id != task.pk
            or review.completeness_snapshot_json != completeness
        ):
            raise ValueError("Changed re-KYC review replay was rejected.")

    @staticmethod
    def _queue_reminder(review, task, *, overdue):
        if overdue and task.overdue_notification_id:
            return task.overdue_notification
        if not overdue and task.due_notification_id:
            return task.due_notification
        notification = Notification.objects.create(
            notification_type="kyc_review_overdue" if overdue else "kyc_review_due",
            category="compliance",
            severity=(Notification.SEVERITY_URGENT if overdue else Notification.SEVERITY_WARNING),
            title="Re-KYC review overdue" if overdue else "Re-KYC review due",
            message="A governed re-KYC review requires action.",
            related_entity_type="kyc_review",
            related_entity_id=review.pk,
            action_label="Review KYC",
            action_url=f"/compliance/kyc-reviews/{review.pk}",
            recipient_user=task.assigned_to_user,
        )
        field = "overdue_notification" if overdue else "due_notification"
        setattr(task, field, notification)
        task.save(update_fields=[field, "updated_at"])
        return notification

    @staticmethod
    def _audit(review, action, *, actor=None, extra=None):
        values = {
            "member_id": str(review.member_id),
            "kyc_profile_id": str(review.kyc_profile_id),
            "task_id": str(review.task_id),
            "due_date": review.due_date.isoformat(),
            "status": review.status,
        }
        values.update(extra or {})
        AuditLog.objects.create(
            actor_user=actor,
            action=action,
            entity_type="kyc_review",
            entity_id=review.pk,
            new_value_json=values,
        )
