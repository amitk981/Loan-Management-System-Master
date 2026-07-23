from dataclasses import dataclass
from datetime import date, datetime, time
import hashlib
import json
from math import ceil
import uuid
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db import models
from django.utils import timezone
from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.compliance.models import Grievance, GrievanceDocument, GrievanceHistory
from sfpcl_credit.compliance.modules.compliance_control_tracker import ComplianceConflict, ComplianceDenied, ComplianceInvalid, ComplianceMissing
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import AuditLog, User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.members.models import Member
from sfpcl_credit.members.modules.member_authority import evaluate_member_authority

@dataclass(frozen=True)
class GrievanceEscalationRun:
    escalated_count: int

class GrievanceWorkflow:
    CREATE_PERMISSION = 'compliance.grievance.create'
    READ_PERMISSION = 'compliance.grievance.read'
    ASSIGN_PERMISSION = 'compliance.grievance.assign'
    UPDATE_PERMISSION = 'compliance.grievance.update'
    RESOLVE_PERMISSION = 'compliance.grievance.resolve'
    ESCALATE_PERMISSION = 'compliance.grievance.escalate'

    @classmethod
    def create(cls, *, actor, payload, idempotency_key):
        return cls._create(actor=actor, payload=payload, idempotency_key=idempotency_key)

    @classmethod
    def create_for_borrower(cls, *, portal_account, payload, idempotency_key):
        if 'member_id' in payload:
            raise ComplianceInvalid({'member_id': 'Borrower scope is derived from the portal session.'})
        if not portal_account.can_authenticate() or portal_account.member.is_deleted:
            raise ComplianceDenied()
        scoped = {**payload, 'member_id': str(portal_account.member_id)}
        cls._create(actor=portal_account.user, payload=scoped, idempotency_key=idempotency_key, member_override=portal_account.member)
        return cls._borrower_projection(Grievance.objects.get(idempotency_key=idempotency_key))

    @classmethod
    def _create(cls, *, actor, payload, idempotency_key, member_override=None):
        if member_override is None:
            cls._require_active_permission(actor, cls.CREATE_PERMISSION)
        key = cls._required_text({'idempotency_key': idempotency_key}, 'idempotency_key', max_length=255)
        values, documents = cls._create_values(actor=actor, payload=payload, member_override=member_override)
        digest = cls._request_digest(payload)
        existing = Grievance.objects.filter(idempotency_key=key).first()
        if existing is not None:
            cls._require_replay(existing, digest)
            return cls.serialize(existing, actor=actor)
        grievance_id = uuid.uuid4()
        try:
            with transaction.atomic():
                grievance = Grievance.objects.create(grievance_id=grievance_id, grievance_reference=cls._reference(grievance_id), idempotency_key=key, request_digest=digest, created_by_user=actor, created_by_role_code=actor.primary_role.role_code, **values)
                for document in documents:
                    GrievanceDocument.objects.create(grievance=grievance, document=document, member=grievance.member, purpose=GrievanceDocument.PURPOSE_SUPPORTING, linked_by_user=actor)
                GrievanceHistory.objects.create(grievance=grievance, sequence=1, event_type='created', new_status=Grievance.STATUS_OPEN, actor_user=actor, actor_role_code=actor.primary_role.role_code, evidence_json={'assigned_to_user_id': str(grievance.assigned_to_user_id), 'supporting_document_ids': [str(document.pk) for document in documents]})
                cls._audit(actor, 'compliance.grievance.created', grievance, {'grievance_reference': grievance.grievance_reference, 'member_id': str(grievance.member_id), 'status': grievance.status})
        except IntegrityError:
            existing = Grievance.objects.filter(idempotency_key=key).first()
            if existing is None:
                raise
            cls._require_replay(existing, digest)
            grievance = existing
        return cls.serialize(grievance, actor=actor)

    @classmethod
    def list(cls, *, actor, query):
        cls._require_active_permission(actor, cls.READ_PERMISSION)
        allowed = {'status', 'member_id', 'grievance_category', 'assigned_to_user_id', 'overdue', 'page', 'page_size'}
        unknown = set(query.keys()) - allowed
        if unknown:
            raise ComplianceInvalid({field: 'Unsupported grievance filter.' for field in unknown})
        queryset = cls._read_queryset(actor)
        status = str(query.get('status') or '').strip()
        if status:
            if status not in Grievance.STATUSES:
                raise ComplianceInvalid({'status': 'Unsupported grievance status.'})
            queryset = queryset.filter(status=status)
        category = str(query.get('grievance_category') or '').strip()
        if category:
            if category not in Grievance.CATEGORIES:
                raise ComplianceInvalid({'grievance_category': 'Unsupported grievance category.'})
            queryset = queryset.filter(grievance_category=category)
        for field in ('member_id', 'assigned_to_user_id'):
            value = str(query.get(field) or '').strip()
            if value:
                try:
                    value = uuid.UUID(value)
                except ValueError as exc:
                    raise ComplianceInvalid({field: 'Use a UUID.'}) from exc
                queryset = queryset.filter(**{field: value})
        overdue = str(query.get('overdue') or '').strip().lower()
        if overdue:
            if overdue not in {'true', 'false'}:
                raise ComplianceInvalid({'overdue': 'Must be true or false.'})
            overdue_query = models.Q(resolution_due_date__lt=timezone.localdate()) & ~models.Q(status=Grievance.STATUS_RESOLVED)
            queryset = queryset.filter(overdue_query if overdue == 'true' else ~overdue_query)
        page, page_size = cls._pagination(query)
        total = queryset.count()
        total_pages = max(1, ceil(total / page_size))
        rows = queryset.order_by('-received_date', '-created_at', '-grievance_id')[(page - 1) * page_size:page * page_size]
        return ([cls.serialize(row, actor=actor) for row in rows], {'page': page, 'page_size': page_size, 'total_count': total, 'total_pages': total_pages, 'has_next': page < total_pages, 'has_previous': page > 1})

    @classmethod
    def retrieve(cls, *, actor, grievance_id):
        grievance = cls._read_queryset(actor).filter(pk=grievance_id).first()
        if grievance is None:
            if Grievance.objects.filter(pk=grievance_id).exists():
                raise ComplianceDenied()
            raise ComplianceMissing()
        return cls.serialize(grievance, actor=actor)

    @staticmethod
    def retrieve_for_borrower(*, portal_account, grievance_id):
        if not portal_account.can_authenticate() or portal_account.member.is_deleted:
            raise ComplianceDenied()
        grievance = Grievance.objects.filter(pk=grievance_id, member_id=portal_account.member_id).first()
        if grievance is None:
            raise ComplianceDenied()
        return GrievanceWorkflow._borrower_projection(grievance)

    @staticmethod
    def _borrower_projection(grievance):
        return {'grievance_id': str(grievance.pk), 'grievance_reference': grievance.grievance_reference, 'grievance_category': grievance.grievance_category, 'received_date': grievance.received_date.isoformat(), 'resolution_due_date': grievance.resolution_due_date.isoformat(), 'status': grievance.status, 'is_overdue': grievance.status != Grievance.STATUS_RESOLVED and grievance.resolution_due_date < timezone.localdate(), 'resolution_summary': grievance.resolution_summary, 'closed_at': grievance.closed_at.isoformat() if grievance.closed_at else None, 'borrower_informed': GrievanceWorkflow._borrower_informed(grievance), 'borrower_acknowledged': grievance.borrower_acknowledged_at is not None}

    @classmethod
    def update(cls, *, actor, grievance_id, payload):
        if not isinstance(payload, dict):
            raise ComplianceInvalid({'request': 'A JSON object is required.'})
        allowed = {'assigned_to_user_id', 'status', 'internal_notes'}
        unknown = set(payload) - allowed
        if unknown or not payload:
            raise ComplianceInvalid({field: 'Unsupported grievance update field.' for field in unknown or {'request'}})
        with transaction.atomic():
            grievance = Grievance.objects.select_for_update().select_related('member', 'assigned_to_user').filter(pk=grievance_id).first()
            if grievance is None:
                raise ComplianceMissing()
            if grievance.status == Grievance.STATUS_RESOLVED:
                raise ComplianceConflict('Resolved grievances are read-only.')
            previous_status = grievance.status
            event_type = 'updated'
            audit_action = 'compliance.grievance.updated'
            evidence = {}
            fields = []
            if 'assigned_to_user_id' in payload:
                cls._require_member_permission(actor=actor, member=grievance.member, permission=cls.ASSIGN_PERMISSION)
                if actor.primary_role.role_code != 'company_secretary':
                    raise ComplianceDenied()
                assignee = cls._object(User, payload.get('assigned_to_user_id'), 'assigned_to_user_id', 'Active grievance owner was not found.')
                if assignee.status != 'active' or assignee.primary_role.status != 'active' or cls.READ_PERMISSION not in auth_service.effective_permission_codes(assignee):
                    raise ComplianceInvalid({'assigned_to_user_id': 'Active grievance read authority is required.'})
                authority = evaluate_member_authority(actor_user=assignee, member=grievance.member, permission=cls.READ_PERMISSION)
                if not authority.allowed:
                    raise ComplianceInvalid({'assigned_to_user_id': 'Owner lacks grievance member scope.'})
                if assignee.pk == grievance.assigned_to_user_id:
                    raise ComplianceConflict('Grievance is already assigned to this owner.')
                evidence['previous_assigned_to_user_id'] = str(grievance.assigned_to_user_id)
                evidence['assigned_to_user_id'] = str(assignee.pk)
                grievance.assigned_to_user = assignee
                fields.append('assigned_to_user')
                event_type = 'assigned'
                audit_action = 'compliance.grievance.assigned'
            if set(payload) & {'status', 'internal_notes'}:
                cls._require_member_permission(actor=actor, member=grievance.member, permission=cls.UPDATE_PERMISSION)
                if grievance.assigned_to_user_id != actor.pk:
                    raise ComplianceDenied()
                if 'status' in payload:
                    requested_status = cls._required_text(payload, 'status', max_length=60)
                    if requested_status != Grievance.STATUS_INVESTIGATING:
                        raise ComplianceConflict('Status may advance to investigating only; escalation and resolution use their dedicated interfaces.')
                    if grievance.status != Grievance.STATUS_OPEN:
                        raise ComplianceConflict('Grievance status cannot move backward.')
                    grievance.status = requested_status
                    fields.append('status')
                    evidence['status'] = requested_status
                if 'internal_notes' in payload:
                    notes = cls._required_text(payload, 'internal_notes')
                    grievance.internal_notes = notes
                    fields.append('internal_notes')
                    evidence['internal_notes_updated'] = True
            if not fields:
                raise ComplianceInvalid({'request': 'No grievance change was supplied.'})
            grievance.save(update_fields=[*fields, 'updated_at'])
            cls._append_history(grievance=grievance, event_type=event_type, actor=actor, previous_status=previous_status, note='', evidence=evidence)
            cls._audit(actor, audit_action, grievance, evidence)
        return cls.retrieve(actor=actor, grievance_id=grievance.pk)

    @classmethod
    def resolve(cls, *, actor, grievance_id, payload, idempotency_key, request=None):
        if not isinstance(payload, dict):
            raise ComplianceInvalid({'request': 'A JSON object is required.'})
        allowed = {'resolution_summary', 'resolution_document_id', 'borrower_acknowledgement'}
        unknown = set(payload) - allowed
        if unknown:
            raise ComplianceInvalid({field: 'Unsupported resolution field.' for field in unknown})
        summary = cls._required_text(payload, 'resolution_summary')
        acknowledgement = cls._required_text(payload, 'borrower_acknowledgement') if 'borrower_acknowledgement' in payload else ''
        key = cls._required_text({'idempotency_key': idempotency_key}, 'idempotency_key', max_length=255)
        digest = cls._request_digest(payload)
        with transaction.atomic():
            grievance = Grievance.objects.select_for_update().select_related('member', 'assigned_to_user').filter(pk=grievance_id).first()
            if grievance is None:
                raise ComplianceMissing()
            cls._require_member_permission(actor=actor, member=grievance.member, permission=cls.RESOLVE_PERMISSION)
            if grievance.assigned_to_user_id != actor.pk and actor.primary_role.role_code != 'company_secretary':
                raise ComplianceDenied()
            resolution_documents = cls._documents([payload['resolution_document_id']] if payload.get('resolution_document_id') else [], member=grievance.member)
            resolution_document = resolution_documents[0] if resolution_documents else None
            if grievance.status == Grievance.STATUS_RESOLVED:
                if grievance.resolution_idempotency_key == key and grievance.resolution_request_digest == digest:
                    return cls.serialize(grievance, actor=actor)
                raise ComplianceConflict('Resolved grievance cannot accept a changed replay.')
            used = Grievance.objects.filter(resolution_idempotency_key=key).exclude(pk=grievance.pk)
            if used.exists():
                raise ComplianceConflict('Resolution idempotency key belongs to another grievance.')
            queued = cls._queue_resolution_notice(actor=actor, grievance=grievance, summary=summary, idempotency_key=key, request=request)
            previous_status = grievance.status
            closed_at = timezone.now()
            grievance.status = Grievance.STATUS_RESOLVED
            grievance.resolution_summary = summary
            grievance.resolution_idempotency_key = key
            grievance.resolution_request_digest = digest
            grievance.resolution_document = resolution_document
            grievance.closed_at = closed_at
            grievance.resolved_by_user = actor
            grievance.notice_communication_id = queued.communication_id
            grievance.borrower_acknowledgement = acknowledgement
            grievance.borrower_acknowledged_at = closed_at if acknowledgement else None
            grievance.save(update_fields=['status', 'resolution_summary', 'resolution_idempotency_key', 'resolution_request_digest', 'resolution_document', 'closed_at', 'resolved_by_user', 'notice_communication', 'borrower_acknowledgement', 'borrower_acknowledged_at', 'updated_at'])
            if resolution_document:
                GrievanceDocument.objects.create(grievance=grievance, document=resolution_document, member=grievance.member, purpose=GrievanceDocument.PURPOSE_RESOLUTION, linked_by_user=actor)
            evidence = {'resolution_document_id': str(resolution_document.pk) if resolution_document else None, 'notice_communication_id': str(queued.communication_id), 'notice_delivery_status': queued.delivery_status, 'borrower_informed': False, 'borrower_acknowledged': bool(acknowledgement)}
            cls._append_history(grievance=grievance, event_type='resolved', actor=actor, previous_status=previous_status, note=summary, evidence=evidence)
            cls._audit(actor, 'compliance.grievance.resolved', grievance, evidence)
            cls._audit(actor, 'compliance.grievance.notice_queued', grievance, evidence)
        return cls.retrieve(actor=actor, grievance_id=grievance.pk)

    @classmethod
    def process_escalations(cls, *, as_of_date):
        from sfpcl_credit.communications.models import Notification
        from sfpcl_credit.scheduler.models import ScheduledJob
        job, _created = ScheduledJob.objects.get_or_create(idempotency_key=f'grievance-escalation:{as_of_date.isoformat()}', defaults={'job_type': 'grievance_escalation', 'status': ScheduledJob.STATUS_RUNNING, 'due_at': timezone.make_aware(datetime.combine(as_of_date, time.min)), 'started_at': timezone.now(), 'attempts': 1})
        if job.status == ScheduledJob.STATUS_SUCCEEDED:
            return GrievanceEscalationRun(escalated_count=0)
        escalated_count = 0
        try:
            with transaction.atomic():
                grievances = list(Grievance.objects.select_for_update().select_related('member', 'assigned_to_user').filter(models.Q(resolution_due_date__lt=as_of_date) | models.Q(grievance_category='recovery_conduct_issue')).exclude(status__in=(Grievance.STATUS_ESCALATED, Grievance.STATUS_RESOLVED)).order_by('grievance_id'))
                for grievance in grievances:
                    previous_status = grievance.status
                    grievance.status = Grievance.STATUS_ESCALATED
                    grievance.escalation_count += 1
                    grievance.last_escalated_at = timezone.now()
                    grievance.save(update_fields=['status', 'escalation_count', 'last_escalated_at', 'updated_at'])
                    interaction_log = grievance.recovery_action.interaction_log_json if grievance.recovery_action_id else []
                    evidence = {'as_of_date': as_of_date.isoformat(), 'overdue': grievance.resolution_due_date < as_of_date, 'fair_practice_attention': grievance.grievance_category == 'recovery_conduct_issue', 'loan_account_id': str(grievance.loan_account_id) if grievance.loan_account_id else None, 'default_case_id': str(grievance.default_case_id) if grievance.default_case_id else None, 'recovery_action_id': str(grievance.recovery_action_id) if grievance.recovery_action_id else None, 'fair_practice_log_source': 'recovery_action.interaction_log_json' if grievance.recovery_action_id else None, 'fair_practice_interaction_count': len(interaction_log), 'fair_practice_log_sha256': hashlib.sha256(json.dumps(interaction_log, sort_keys=True, separators=(',', ':')).encode()).hexdigest() if grievance.recovery_action_id else None}
                    cls._append_history(grievance=grievance, event_type='escalated', actor=None, previous_status=previous_status, note='', evidence=evidence)
                    cls._audit(None, 'compliance.grievance.escalated', grievance, evidence)
                    Notification.objects.create(notification_type='grievance_escalated', category='compliance', severity=Notification.SEVERITY_URGENT, title=f'Grievance {grievance.grievance_reference} escalated', message='Recovery-conduct grievance needs fair-practice review.' if evidence['fair_practice_attention'] else 'Grievance resolution TAT is overdue.', related_entity_type='grievance', related_entity_id=grievance.pk, action_label='Review grievance', action_url=f'/grievances/{grievance.pk}', recipient_user=grievance.assigned_to_user, recipient_role_code='company_secretary')
                    escalated_count += 1
                ScheduledJob.objects.filter(pk=job.pk).update(status=ScheduledJob.STATUS_SUCCEEDED, completed_at=timezone.now(), last_error_summary='')
        except Exception as exc:
            ScheduledJob.objects.filter(pk=job.pk).update(status=ScheduledJob.STATUS_FAILED, completed_at=timezone.now(), last_error_summary=str(exc)[:500])
            raise
        return GrievanceEscalationRun(escalated_count=escalated_count)

    @classmethod
    def download_document(cls, *, actor, grievance_id, document_id, request):
        grievance = cls._read_queryset(actor).filter(pk=grievance_id).first()
        if grievance is None:
            if Grievance.objects.filter(pk=grievance_id).exists():
                raise ComplianceDenied()
            raise ComplianceMissing()
        link = grievance.document_links.filter(document_id=document_id).first()
        if link is None:
            raise ComplianceMissing()
        from sfpcl_credit.documents.services import download_document_file
        descriptor = download_document_file(actor, request, link.document_id)
        cls._audit(actor, 'compliance.grievance.document_downloaded', grievance, {'document_id': str(link.document_id), 'purpose': link.purpose, 'expires_at': descriptor['expires_at']})
        return descriptor

    @classmethod
    def serialize(cls, grievance, *, actor, borrower_safe=False):
        history = [{'sequence': event.sequence, 'event_type': event.event_type, 'previous_status': event.previous_status or None, 'new_status': event.new_status, 'note': '' if borrower_safe else event.note, 'created_at': event.created_at.isoformat()} for event in grievance.history.all()]
        data = {'grievance_id': str(grievance.pk), 'grievance_reference': grievance.grievance_reference, 'member_id': str(grievance.member_id), 'loan_account_id': str(grievance.loan_account_id) if grievance.loan_account_id else None, 'loan_application_id': str(grievance.loan_application_id) if grievance.loan_application_id else None, 'default_case_id': str(grievance.default_case_id) if grievance.default_case_id else None, 'recovery_action_id': str(grievance.recovery_action_id) if grievance.recovery_action_id else None, 'grievance_category': grievance.grievance_category, 'description': grievance.description, 'received_date': grievance.received_date.isoformat(), 'received_channel': grievance.received_channel, 'assigned_to_user_id': str(grievance.assigned_to_user_id), 'resolution_due_date': grievance.resolution_due_date.isoformat(), 'status': grievance.status, 'tat_days': (grievance.resolution_due_date - grievance.received_date).days, 'days_overdue': max(0, (timezone.localdate() - grievance.resolution_due_date).days), 'is_overdue': grievance.status != Grievance.STATUS_RESOLVED and grievance.resolution_due_date < timezone.localdate(), 'resolution_summary': grievance.resolution_summary, 'closed_at': grievance.closed_at.isoformat() if grievance.closed_at else None, 'borrower_informed': cls._borrower_informed(grievance), 'borrower_acknowledged': grievance.borrower_acknowledged_at is not None, 'history': history, 'available_actions': cls._available_actions(grievance, actor)}
        if not borrower_safe:
            data.update({'supporting_document_ids': [str(document_id) for document_id in grievance.document_links.filter(purpose=GrievanceDocument.PURPOSE_SUPPORTING).order_by('linked_at', 'grievance_document_id').values_list('document_id', flat=True)], 'resolution_document_id': str(grievance.resolution_document_id) if grievance.resolution_document_id else None, 'internal_notes': grievance.internal_notes, 'borrower_acknowledgement': grievance.borrower_acknowledgement, 'escalation_count': grievance.escalation_count, 'notice_communication_id': str(grievance.notice_communication_id) if grievance.notice_communication_id else None, 'notice_delivery_status': cls._notice_delivery_status(grievance)})
        return data

    @classmethod
    def _create_values(cls, *, actor, payload, member_override=None):
        if not isinstance(payload, dict):
            raise ComplianceInvalid({'request': 'A JSON object is required.'})
        allowed = {'member_id', 'loan_account_id', 'loan_application_id', 'default_case_id', 'recovery_action_id', 'grievance_category', 'description', 'received_date', 'received_channel', 'assigned_to_user_id', 'resolution_due_date', 'supporting_document_ids'}
        unknown = set(payload) - allowed
        if unknown:
            raise ComplianceInvalid({field: 'Unsupported grievance field.' for field in unknown})
        member = cls._object(Member, payload.get('member_id'), 'member_id', 'Member was not found.')
        authority = None if member_override is not None else evaluate_member_authority(actor_user=actor, member=member, permission=cls.CREATE_PERMISSION)
        if (member_override is not None and member.pk != member_override.pk) or (authority is not None and not authority.allowed):
            raise ComplianceDenied()
        category = cls._required_text(payload, 'grievance_category', max_length=100)
        if category not in Grievance.CATEGORIES:
            raise ComplianceInvalid({'grievance_category': 'Unsupported grievance category.'})
        description = cls._required_text(payload, 'description')
        channel = cls._required_text(payload, 'received_channel', max_length=60)
        if channel not in Grievance.CHANNELS:
            raise ComplianceInvalid({'received_channel': 'Unsupported received channel.'})
        received_date = cls._date(payload, 'received_date')
        if received_date > timezone.localdate():
            raise ComplianceInvalid({'received_date': 'Received date cannot be future.'})
        due_date = cls._date(payload, 'resolution_due_date')
        if due_date < received_date:
            raise ComplianceInvalid({'resolution_due_date': 'Resolution due date precedes receipt.'})
        assignee = cls._object(User, payload.get('assigned_to_user_id'), 'assigned_to_user_id', 'Active grievance owner was not found.')
        if assignee.status != 'active' or assignee.primary_role.status != 'active' or cls.READ_PERMISSION not in auth_service.effective_permission_codes(assignee):
            raise ComplianceInvalid({'assigned_to_user_id': 'Active grievance read authority is required.'})
        assignee_authority = evaluate_member_authority(actor_user=assignee, member=member, permission=cls.READ_PERMISSION)
        if not assignee_authority.allowed:
            raise ComplianceInvalid({'assigned_to_user_id': 'Owner lacks grievance member scope.'})
        application = cls._optional_member_object(LoanApplication, payload.get('loan_application_id'), member=member, field='loan_application_id')
        loan_account = cls._optional_member_model('sfpcl_credit.loans.models', 'LoanAccount', payload.get('loan_account_id'), member=member, field='loan_account_id')
        default_case = cls._optional_member_model('sfpcl_credit.defaults.models', 'DefaultCase', payload.get('default_case_id'), member=member, field='default_case_id')
        recovery_action = cls._optional_recovery_action(payload.get('recovery_action_id'), member=member)
        cls._validate_source_chain(member=member, application=application, loan_account=loan_account, default_case=default_case, recovery_action=recovery_action, category=category)
        documents = cls._documents(payload.get('supporting_document_ids', []), member=member)
        return ({'member': member, 'loan_account': loan_account, 'loan_application': application, 'default_case': default_case, 'recovery_action': recovery_action, 'grievance_category': category, 'description': description, 'received_date': received_date, 'received_channel': channel, 'assigned_to_user': assignee, 'resolution_due_date': due_date, 'status': Grievance.STATUS_OPEN}, documents)

    @classmethod
    def _read_queryset(cls, actor):
        from sfpcl_credit.members.modules.member_authority import member_scope_predicate
        cls._require_active_permission(actor, cls.READ_PERMISSION)
        queryset = Grievance.objects.select_related('member', 'assigned_to_user').prefetch_related('history', 'document_links')
        if actor.primary_role.role_code == 'internal_auditor':
            return queryset
        return queryset.filter(member__in=Member.objects.filter(member_scope_predicate(actor_user=actor, permission=cls.READ_PERMISSION)))

    @classmethod
    def _require_member_permission(cls, *, actor, member, permission):
        cls._require_active_permission(actor, permission)
        authority = evaluate_member_authority(actor_user=actor, member=member, permission=permission)
        if not authority.allowed:
            raise ComplianceDenied()

    @staticmethod
    def _append_history(*, grievance, event_type, actor, previous_status, note, evidence):
        sequence = (GrievanceHistory.objects.filter(grievance=grievance).order_by('-sequence').values_list('sequence', flat=True).first() or 0) + 1
        return GrievanceHistory.objects.create(grievance=grievance, sequence=sequence, event_type=event_type, previous_status=previous_status, new_status=grievance.status, note=note, actor_user=actor, actor_role_code=actor.primary_role.role_code if actor is not None else 'system', evidence_json=evidence)

    @staticmethod
    def _queue_resolution_notice(*, actor, grievance, summary, idempotency_key, request):
        from sfpcl_credit.communications.models import Communication
        from sfpcl_credit.communications.modules.communication_dispatcher import CommunicationDispatcher
        if grievance.member.email:
            channel = Communication.CHANNEL_EMAIL
            address = grievance.member.email
            template_code = 'grievance_resolution_email'
        elif grievance.member.mobile_number:
            channel = Communication.CHANNEL_SMS
            address = grievance.member.mobile_number
            template_code = 'grievance_resolution_sms'
        else:
            raise ComplianceConflict('Member has no governed grievance-notice destination.')
        delivery_key = f'grievance-resolution:{grievance.pk}:{idempotency_key}'
        return CommunicationDispatcher.queue_from_template(actor=actor, template_code=template_code, recipient={'party_type': 'member', 'party_id': grievance.member_id, 'address': address, 'channel': channel}, context={'merge_data': {'member_name': grievance.member.display_name, 'grievance_reference': grievance.grievance_reference, 'resolution_summary': summary}, 'idempotency_key': delivery_key, 'request': request}, related_entity={'type': 'grievance', 'id': grievance.pk}, delivery_idempotency_key=delivery_key)

    @staticmethod
    def _notice_delivery_status(grievance):
        if not grievance.notice_communication_id:
            return None
        from sfpcl_credit.communications.models import CommunicationDeliveryJob
        from sfpcl_credit.communications.modules.communication_dispatcher import CommunicationDispatcher
        job = CommunicationDeliveryJob.objects.filter(communication_id=grievance.notice_communication_id).first()
        if job is None:
            return None
        return CommunicationDispatcher.delivery_status(job_id=job.pk)

    @staticmethod
    def _borrower_informed(grievance):
        if grievance.borrower_informed_at is not None:
            return True
        from sfpcl_credit.communications.models import Communication
        return bool(grievance.notice_communication_id and Communication.objects.filter(pk=grievance.notice_communication_id, sent_at__isnull=False, delivery_status='sent').exists())

    @staticmethod
    def _pagination(query):
        try:
            page = int(query.get('page', 1))
            page_size = int(query.get('page_size', 20))
        except (TypeError, ValueError) as exc:
            raise ComplianceInvalid({'page': 'Pagination values must be positive integers.'}) from exc
        if page < 1 or page_size < 1 or page_size > 100:
            raise ComplianceInvalid({'page': 'Pagination values are out of range.'})
        return (page, page_size)

    @staticmethod
    def _request_digest(payload):
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

    @staticmethod
    def _require_replay(grievance, digest):
        if grievance.request_digest != digest:
            raise ComplianceConflict('Idempotency key was already used with a different grievance request.')

    @staticmethod
    def _reference(grievance_id):
        return f'GRV-{timezone.localdate().year}-{grievance_id.hex[:12].upper()}'

    @staticmethod
    def _required_text(payload, field, *, max_length=None):
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ComplianceInvalid({field: 'This field is required.'})
        value = value.strip()
        if max_length and len(value) > max_length:
            raise ComplianceInvalid({field: f'Maximum length is {max_length}.'})
        return value

    @staticmethod
    def _date(payload, field):
        value = payload.get(field)
        try:
            return date.fromisoformat(value)
        except (TypeError, ValueError) as exc:
            raise ComplianceInvalid({field: 'Use YYYY-MM-DD.'}) from exc

    @staticmethod
    def _object(model, object_id, field, message):
        try:
            return model.objects.select_related('primary_role').get(pk=object_id) if model is User else model.objects.get(pk=object_id)
        except (model.DoesNotExist, TypeError, ValueError) as exc:
            raise ComplianceInvalid({field: message}) from exc

    @staticmethod
    def _optional_member_object(model, object_id, *, member, field):
        if not object_id:
            return None
        try:
            value = model.objects.get(pk=object_id)
        except (model.DoesNotExist, TypeError, ValueError) as exc:
            raise ComplianceInvalid({field: 'Matching member source object was not found.'}) from exc
        if value.member_id != member.pk:
            raise ComplianceDenied()
        return value

    @classmethod
    def _optional_member_model(cls, module_name, model_name, object_id, *, member, field):
        if not object_id:
            return None
        module = __import__(module_name, fromlist=[model_name])
        return cls._optional_member_object(getattr(module, model_name), object_id, member=member, field=field)

    @classmethod
    def _optional_recovery_action(cls, object_id, *, member):
        if not object_id:
            return None
        from sfpcl_credit.recovery.models import RecoveryAction
        try:
            value = RecoveryAction.objects.select_related('loan_account').get(pk=object_id)
        except (RecoveryAction.DoesNotExist, TypeError, ValueError) as exc:
            raise ComplianceInvalid({'recovery_action_id': 'Matching member recovery action was not found.'}) from exc
        if value.loan_account.member_id != member.pk:
            raise ComplianceDenied()
        return value

    @staticmethod
    def _validate_source_chain(*, member, application, loan_account, default_case, recovery_action, category):
        implied_loans = {source.loan_account_id for source in (default_case, recovery_action) if source is not None}
        if loan_account:
            implied_loans.add(loan_account.pk)
        if len(implied_loans) > 1:
            raise ComplianceInvalid({'loan_account_id': 'Grievance source objects do not identify one loan.'})
        source_loan_id = next(iter(implied_loans), None)
        if source_loan_id and application:
            from sfpcl_credit.loans.models import LoanAccount
            if not LoanAccount.objects.filter(pk=source_loan_id, loan_application=application).exists():
                raise ComplianceInvalid({'loan_application_id': 'Application does not match the grievance loan source.'})
        if loan_account and application and (loan_account.loan_application_id != application.pk):
            raise ComplianceInvalid({'loan_account_id': 'Loan and application source objects do not match.'})
        if default_case and loan_account and (default_case.loan_account_id != loan_account.pk):
            raise ComplianceInvalid({'default_case_id': 'Default case and loan source objects do not match.'})
        if recovery_action and loan_account and (recovery_action.loan_account_id != loan_account.pk):
            raise ComplianceInvalid({'recovery_action_id': 'Recovery action and loan source objects do not match.'})
        if category == 'recovery_conduct_issue' and not recovery_action:
            raise ComplianceInvalid({'recovery_action_id': 'Recovery conduct grievances require the governed recovery action and its fair-practice interaction log.'})

    @staticmethod
    def _documents(document_ids, *, member):
        if not isinstance(document_ids, list) or any(not isinstance(document_id, str) for document_id in document_ids) or len(document_ids) != len(set(document_ids)):
            raise ComplianceInvalid({'supporting_document_ids': 'Provide unique document identifiers.'})
        from sfpcl_credit.documents.services import resolve_immutable_upload_provenance
        documents = []
        for document_id in document_ids:
            try:
                provenance = resolve_immutable_upload_provenance(document_id=document_id)
                document = provenance.document
            except (ValidationError, TypeError, ValueError) as exc:
                if DocumentFile.objects.filter(pk=document_id).exists():
                    raise ComplianceDenied() from exc
                raise ComplianceInvalid({'supporting_document_ids': 'Supporting document was not found.'}) from exc
            if provenance.related_entity_type != 'member' or provenance.related_entity_id != member.pk:
                raise ComplianceDenied()
            if document.sensitivity_level == DocumentFile.SENSITIVITY_PUBLIC:
                raise ComplianceInvalid({'supporting_document_ids': 'Grievance evidence must use governed non-public storage.'})
            if GrievanceDocument.objects.filter(document=document).exclude(member=member).exists():
                raise ComplianceDenied()
            documents.append(document)
        return documents

    @staticmethod
    def _audit(actor, action, grievance, evidence):
        AuditLog.objects.create(actor_user=actor, actor_type='user', action=action, entity_type='grievance', entity_id=grievance.pk, new_value_json=evidence)

    @staticmethod
    def _require_active_permission(actor, permission):
        if actor.status != 'active' or actor.primary_role.status != 'active' or permission not in auth_service.effective_permission_codes(actor):
            raise ComplianceDenied()

    @classmethod
    def _available_actions(cls, grievance, actor):
        permissions = set(auth_service.effective_permission_codes(actor))
        if grievance.status == Grievance.STATUS_RESOLVED:
            return []
        actions = []
        if cls.ASSIGN_PERMISSION in permissions:
            actions.append('assign')
        if cls.RESOLVE_PERMISSION in permissions and (grievance.assigned_to_user_id == actor.pk or actor.primary_role.role_code == 'company_secretary'):
            actions.append('resolve')
        return actions
