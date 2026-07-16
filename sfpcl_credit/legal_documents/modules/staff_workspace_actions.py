"""Legal/checklist action decisions for the S26-S35 staff workspace."""
from dataclasses import dataclass
from functools import partial
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from sfpcl_credit.applications.models import Witness
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.documents.models import DocumentTemplate
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.legal_documents.models import ChecklistAction, ChecklistItem, DocumentChecklist, SignatureRecord
from sfpcl_credit.legal_documents.modules import checklist_actions, document_generation, documentation_actions, loan_document_verification, signatures, stamp_notary
DOCUMENT_TYPES = {'witness_pan_aadhaar': 'witness_pan_aadhaar', 'cancelled_cheque': 'cancelled_cheque', 'blank_dated_cheque': 'blank_dated_cheque', 'poa': 'power_of_attorney', 'tri_party_agreement': 'tri_party_agreement', 'sh4': 'sh4', 'cdsl_pledge': 'cdsl_pledge_evidence', 'term_sheet': 'term_sheet', 'loan_agreement': 'loan_agreement', 'bank_verification_letter': 'bank_verification_letter', 'final_checklist': 'document_checklist'}
APPROVALS = {ChecklistAction.TYPE_COMPANY_SECRETARY_APPROVAL: ('approve_as_company_secretary', 'Approve as Company Secretary', 'documents.checklist.approve_cs', 'company_secretary', 'approve-as-company-secretary'), ChecklistAction.TYPE_CREDIT_MANAGER_APPROVAL: ('approve_as_credit_manager', 'Approve as Credit Manager', 'documents.checklist.approve_credit', 'credit_manager', 'approve-as-credit-manager'), ChecklistAction.TYPE_SANCTION_COMMITTEE_APPROVAL: ('approve_as_sanction_committee', 'Approve as Sanction Committee', 'documents.checklist.approve_sanction', 'director', 'approve-as-sanction-committee')}

class OwnerAccessDenied(Exception):

    def __init__(self, error_code='FORBIDDEN'):
        self.error_code = error_code
        super().__init__(error_code)

class OwnerNotFound(Exception):
    pass

class OwnerConflict(Exception):

    def __init__(self, message, error_code='CONFLICT'):
        self.error_code = error_code
        super().__init__(message)

@dataclass(frozen=True)
class ChecklistGateways:
    item_completion_decision: object
    complete_item: object
    approve_company_secretary: object
    approve_credit_manager: object
    approve_sanction_committee: object
    borrower_safe_completed_item_ids: object

def _execute_with_translation(callback, values, uploaded_file, request):
    try:
        return callback(values, uploaded_file, request)
    except ValidationError:
        raise
    except checklist_actions.AccessDenied as exc:
        raise OwnerAccessDenied(exc.error_code) from exc
    except checklist_actions.NotFound as exc:
        raise OwnerNotFound from exc
    except checklist_actions.Conflict as exc:
        raise OwnerConflict(str(exc), exc.error_code) from exc
    except documentation_actions.AccessDenied as exc:
        raise OwnerAccessDenied from exc
    except documentation_actions.NotFound as exc:
        raise OwnerNotFound from exc
    except documentation_actions.Conflict as exc:
        raise OwnerConflict(str(exc)) from exc
    except (document_generation.LegalDocumentAccessDenied, loan_document_verification.AccessDenied, signatures.AccessDenied, stamp_notary.AccessDenied) as exc:
        raise OwnerAccessDenied from exc
    except (document_generation.LegalDocumentNotFound, loan_document_verification.NotFound, signatures.NotFound, stamp_notary.NotFound) as exc:
        raise OwnerNotFound from exc
    except (document_generation.RendererProvenanceConflict, loan_document_verification.Conflict, signatures.InvalidState, signatures.ProjectionConflict, signatures.EvidenceConflict, stamp_notary.ProjectionConflict) as exc:
        raise OwnerConflict(str(exc)) from exc

def _action(action_code, label, required_permission, action_url, *, owner_execute, method='POST', required_role=None, fixed_payload=None, fields=None, **options):
    result = {'action_code': action_code, 'label': label, 'enabled': True, 'disabled_reason': None, 'required_permission': required_permission, 'action_url': action_url, 'method': method, '_owner_execute': partial(_execute_with_translation, owner_execute)}
    if required_role:
        result['required_role'] = required_role
    if fixed_payload:
        result['fixed_payload'] = fixed_payload
    if fields:
        result['fields'] = fields
    result.update(options)
    return result

def _owner_allows(authorizer, actor):
    try:
        authorizer(actor)
    except (checklist_actions.AccessDenied, document_generation.LegalDocumentAccessDenied, loan_document_verification.AccessDenied, signatures.AccessDenied, stamp_notary.AccessDenied):
        return False
    return True

def _item_authorising_role(actor):
    allowed = {'compliance_team_member', 'company_secretary'}
    effective = set(auth_service.effective_role_codes(actor))
    governed = (actor.approval_authority_type or '').strip()
    if governed in allowed and governed in effective:
        return governed
    if actor.primary_role.role_code in allowed and actor.primary_role.role_code in effective:
        return actor.primary_role.role_code
    return None

def item_actions(actor, application, item, document, status, *, gateways):
    if not item.applicable_flag:
        return []
    if document is None:
        generation = _generation_action(actor, application, item.item_code)
        return [generation] if generation else []
    actions = []
    completion = gateways.item_completion_decision(actor=actor, checklist_item_id=item.pk, loan_document_id=document.pk)
    if status == ChecklistItem.STATUS_PENDING and completion.enabled:
        actions.append(_action('complete_item', 'Mark complete', 'documents.checklist.update', f'/api/v1/checklist-items/{item.pk}/complete/', required_role='compliance_team_member', owner_execute=partial(_execute_complete_item, gateways.complete_item, actor, item.pk, document.pk), fixed_payload={'checklist_item_id': str(item.pk), 'loan_document_id': str(document.pk)}, fields=[{'name': 'remarks', 'label': 'Remarks', 'type': 'textarea', 'required': True}]))
    if document.document_type == 'tri_party_agreement' and document.verification_status != 'verified' and _owner_allows(loan_document_verification.require_verify_actor, actor):
        actions.append(_action('verify_document', 'Verify document', 'documents.loan_document.verify', f'/api/v1/loan-documents/{document.pk}/verify/', required_role='company_secretary', owner_execute=partial(_execute_verify_document, actor, document.pk), fixed_payload={'loan_document_id': str(document.pk), 'verification_status': 'verified'}, fields=[{'name': 'remarks', 'label': 'Remarks', 'type': 'textarea', 'required': True}]))
    if status in {ChecklistItem.STATUS_PENDING, 'blocked'}:
        actions.extend(_legal_evidence_actions(actor, application, document))
        actions.extend(_workspace_document_actions(actor, application, item, document))
    return actions

def _workspace_document_actions(actor, application, item, document):
    actions = []
    if document_services.user_can_upload_documents(actor):
        actions.append(_action('upload_signed_copy', 'Upload / re-upload signed copy', document_services.DOCUMENT_UPLOAD_PERMISSION, 'workspace:upload_signed_copy', owner_execute=partial(_execute_signed_copy, actor, application.pk, document.pk), fields=[{'name': 'file', 'label': 'Signed document', 'type': 'file', 'required': True}, {'name': 'remarks', 'label': 'Remarks', 'type': 'textarea', 'required': True}], fixed_payload={'loan_document_id': str(document.pk)}))
    if _owner_allows(checklist_actions.require_item_completion_actor, actor):
        role = _item_authorising_role(actor)
        if role:
            actions.append(_action('request_correction', 'Request correction', checklist_actions.ITEM_COMPLETE_PERMISSION, 'workspace:request_correction', owner_execute=partial(_execute_review_action, actor, item.document_checklist_id, 'request_correction', 'checklist_item', role, item.pk, document.pk), fields=[{'name': 'remarks', 'label': 'Correction required', 'type': 'textarea', 'required': True}], fixed_payload={'loan_document_id': str(document.pk)}))
    return actions

def _legal_evidence_actions(actor, application, document):
    actions = []
    if _owner_allows(signatures.require_record_actor, actor):
        required_parties = {'power_of_attorney': ('borrower', 'nominee'), 'tri_party_agreement': ('borrower', 'nominee'), 'sh4': ('borrower', 'witness'), 'term_sheet': ('borrower', 'nominee'), 'loan_agreement': ('borrower', 'witness')}.get(document.document_type, ())
        blocked_capture = {(row.signer_party_type, str(row.signer_party_id)) for row in SignatureRecord.objects.filter(loan_document=document) if row.signature_status == 'signed' and (not row.signature_mismatch_flag) or (row.signature_status == 'mismatch' and row.signature_mismatch_flag and (row.mismatch_resolution_type is None))}
        for party in required_parties:
            identity = _canonical_signature_identity(application, party)
            if identity is None or (party, identity[0]) in blocked_capture:
                continue
            party_id, party_name = identity
            actions.append(_action(f'record_{party}_signature', f'Record {party} signature', signatures.RECORD_PERMISSION, f'/api/v1/loan-documents/{document.pk}/signatures/', required_role='compliance_team_member', owner_execute=partial(_execute_signature, actor, document.pk, party, party_id, party_name), fixed_payload={'loan_document_id': str(document.pk), 'signer_party_type': party, 'signer_party_id': party_id, 'signer_name_snapshot': party_name}, fields=[{'name': 'signature_method', 'label': 'Method', 'type': 'select', 'required': True, 'options': ['wet_ink', 'digital', 'scanned']}, {'name': 'signature_status', 'label': 'Status', 'type': 'select', 'required': True, 'options': ['signed', 'mismatch']}, {'name': 'signed_at', 'label': 'Signed at', 'type': 'datetime-local', 'required': True}]))
    if _owner_allows(stamp_notary.require_stamp_actor, actor):
        actions.append(_action('record_stamp', 'Record stamp', stamp_notary.STAMP_PERMISSION, f'/api/v1/loan-documents/{document.pk}/stamp-duty-record/', owner_execute=partial(_execute_stamp, actor, document.pk, {'stamp_number': None, 'stamp_purchase_date': None, 'executed_date': None, 'remarks': None}), fixed_payload={'loan_document_id': str(document.pk), 'stamp_number': None, 'stamp_purchase_date': None, 'executed_date': None, 'remarks': None}, fields=[{'name': 'stamp_paper_amount', 'label': 'Stamp amount', 'type': 'text', 'required': True}, {'name': 'stamp_type', 'label': 'Stamp type', 'type': 'select', 'required': True, 'options': ['physical', 'electronic']}, {'name': 'status', 'label': 'Status', 'type': 'select', 'required': True, 'options': ['pending', 'adequate', 'insufficient']}, {'name': 'remarks', 'label': 'Remarks', 'type': 'textarea', 'required': False}]))
    if _owner_allows(stamp_notary.require_notary_actor, actor):
        actions.append(_action('record_notarisation', 'Record notarisation', stamp_notary.NOTARY_PERMISSION, f'/api/v1/loan-documents/{document.pk}/notarisation-record/', owner_execute=partial(_execute_notary, actor, document.pk, {'notary_name': None, 'notary_registration_number': None, 'notarised_date': None, 'evidence_document_id': None, 'remarks': None}), fixed_payload={'loan_document_id': str(document.pk), 'notary_name': None, 'notary_registration_number': None, 'notarised_date': None, 'evidence_document_id': None, 'remarks': None}, fields=[{'name': 'notary_name', 'label': 'Notary name', 'type': 'text', 'required': False}, {'name': 'notary_registration_number', 'label': 'Registration number', 'type': 'text', 'required': False}, {'name': 'notarised_date', 'label': 'Notarised date', 'type': 'date', 'required': False}, {'name': 'status', 'label': 'Status', 'type': 'select', 'required': True, 'options': ['pending', 'completed', 'rejected']}, {'name': 'evidence_document_id', 'label': 'Evidence document', 'type': 'text', 'required': False}]))
    unresolved = SignatureRecord.objects.filter(loan_document=document, signature_status='mismatch', signature_mismatch_flag=True, mismatch_resolution_type__isnull=True).first()
    if unresolved and _owner_allows(signatures.require_resolve_actor, actor):
        actions.append(_action('resolve_signature_mismatch', 'Resolve signature mismatch', signatures.RESOLVE_PERMISSION, f'/api/v1/signature-records/{unresolved.pk}/resolve-mismatch/', required_role='company_secretary', owner_execute=partial(_execute_mismatch, actor, unresolved.pk), fixed_payload={'signature_record_id': str(unresolved.pk)}, fields=[{'name': 'mismatch_resolution_type', 'label': 'Resolution', 'type': 'select', 'required': True, 'options': ['bank_verification_letter', 'borrower_declaration']}, {'name': 'mismatch_resolution_document_id', 'label': 'Evidence document', 'type': 'text', 'required': True}, {'name': 'remarks', 'label': 'Remarks', 'type': 'textarea', 'required': True}]))
    return actions

def _canonical_signature_identity(application, party):
    if party == 'borrower':
        return (str(application.member_id), application.member.legal_name)
    if party == 'nominee' and application.nominee_id:
        return (str(application.nominee_id), application.nominee.nominee_name)
    if party == 'witness':
        witnesses = list(Witness.objects.filter(loan_application=application, verification_status='verified', shareholder_verified_flag=True).order_by('created_at', 'witness_id')[:2])
        if len(witnesses) == 1:
            return (str(witnesses[0].pk), witnesses[0].witness_name)
    return None

def _generation_action(actor, application, item_code):
    if not document_generation.can_generate(actor=actor, application_id=application.pk):
        return None
    try:
        variant = document_generation.resolve_borrower_template_variant(application.borrower_type)
    except ValidationError:
        return None
    document_type = DOCUMENT_TYPES[item_code]
    today = timezone.localdate()
    template = DocumentTemplate.objects.filter(document_type=document_type, borrower_type=variant, approval_status=DocumentTemplate.STATUS_APPROVED, effective_from__lte=today, template_file__isnull=False).filter(models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=today)).order_by('-effective_from', '-created_at').first()
    if template is None:
        return None
    output_formats = document_generation.executable_output_formats(actor=actor, application_id=application.pk, document_type=document_type, template_id=template.pk)
    if not output_formats:
        return None
    return _action('generate_document', 'Generate document', document_generation.GENERATE_PERMISSION, f'/api/v1/loan-applications/{application.pk}/loan-documents/generate/', required_role='compliance_team_member', owner_execute=partial(_execute_generation, actor, application.pk, document_type, template.pk), fixed_payload={'document_type': document_type, 'template_id': str(template.pk)}, fields=[{'name': 'output_format', 'label': 'Output format', 'type': 'select', 'required': True, 'options': list(output_formats)}], template_version=template.template_version)

def approval_actions(actor, checklist, completed, *, gateways):
    available = checklist_actions.available_approval_action(actor=actor, checklist=checklist, completed_item_ids=completed)
    if not available:
        return []
    code, label, permission, role, suffix = APPROVALS[available]
    return [_action(code, label, permission, f'/api/v1/document-checklists/{checklist.pk}/{suffix}/', required_role=role, owner_execute=partial(_execute_approval, actor, checklist.pk, {'approve_as_company_secretary': gateways.approve_company_secretary, 'approve_as_credit_manager': gateways.approve_credit_manager, 'approve_as_sanction_committee': gateways.approve_sanction_committee}[code]), fixed_payload={'document_checklist_id': str(checklist.pk)}, fields=[{'name': 'comments', 'label': 'Comments', 'type': 'textarea', 'required': True}])]

def record_actions(actor, checklist, *, gateways):
    by_status = {DocumentChecklist.STATUS_IN_PROGRESS: ChecklistAction.TYPE_COMPANY_SECRETARY_APPROVAL, DocumentChecklist.STATUS_CS_APPROVED: ChecklistAction.TYPE_CREDIT_MANAGER_APPROVAL, DocumentChecklist.STATUS_CREDIT_APPROVED: ChecklistAction.TYPE_SANCTION_COMMITTEE_APPROVAL}
    action_type = by_status.get(checklist.checklist_status)
    if action_type is None:
        return []
    try:
        checklist_actions.require_stage_actor(actor, action_type)
    except checklist_actions.AccessDenied:
        return []
    if action_type == ChecklistAction.TYPE_SANCTION_COMMITTEE_APPROVAL:
        completed = gateways.borrower_safe_completed_item_ids(checklist)
        if checklist_actions.available_approval_action(actor=actor, checklist=checklist, completed_item_ids=completed) is None:
            return []
    permission = APPROVALS[action_type][2]
    role = APPROVALS[action_type][3]
    stage = 'sanction_committee' if action_type == ChecklistAction.TYPE_SANCTION_COMMITTEE_APPROVAL else role
    final_item = checklist.items.filter(item_code='final_checklist').first()
    return [_action('return_for_correction', 'Return for correction', permission, 'workspace:return_for_correction', owner_execute=partial(_execute_review_action, actor, checklist.pk, 'return_for_correction', stage, role, final_item.pk if final_item else None, final_item.loan_document_id if final_item else None), fields=[{'name': 'remarks', 'label': 'Correction required', 'type': 'textarea', 'required': True}], fixed_payload={'document_checklist_id': str(checklist.pk)}), _action('add_condition', 'Add condition', permission, 'workspace:add_condition', owner_execute=partial(_execute_review_action, actor, checklist.pk, 'add_condition', stage, role, None, None), fields=[{'name': 'condition', 'label': 'Condition', 'type': 'textarea', 'required': True}], fixed_payload={'document_checklist_id': str(checklist.pk)})]

def _metadata(module, request):
    return module.RequestMetadata(request_id=request.headers.get('X-Request-ID'), ip_address=request.META.get('REMOTE_ADDR', ''), user_agent=request.headers.get('User-Agent', ''))

def _execute_complete_item(completer, actor, item_id, document_id, values, _file, request):
    return completer(actor=actor, checklist_item_id=item_id, payload={'loan_document_id': str(document_id), 'remarks': values.get('remarks')}, metadata=_metadata(checklist_actions, request))

def _execute_approval(actor, checklist_id, recorder, values, _file, request):
    return recorder(actor=actor, document_checklist_id=checklist_id, payload={'comments': values.get('comments')}, metadata=_metadata(checklist_actions, request))

def _execute_generation(actor, application_id, document_type, template_id, values, _file, request):
    return document_generation.generate(actor=actor, application_id=application_id, payload={'document_type': document_type, 'template_id': str(template_id), 'output_format': values.get('output_format')}, metadata=_metadata(document_generation, request))

def _execute_verify_document(actor, document_id, values, _file, request):
    return loan_document_verification.verify(actor=actor, loan_document_id=document_id, payload={'verification_status': 'verified', **values}, metadata=_metadata(loan_document_verification, request))

def _execute_signature(actor, document_id, party, party_id, party_name, values, _file, request):
    return signatures.record(actor=actor, loan_document_id=document_id, payload={'signer_party_type': party, 'signer_party_id': party_id, 'signer_name_snapshot': party_name, **values, 'signature_mismatch_flag': values.get('signature_status') == 'mismatch'}, metadata=_metadata(signatures, request))

def _execute_stamp(actor, document_id, fixed, values, _file, request):
    return stamp_notary.record_stamp(actor=actor, loan_document_id=document_id, payload={**fixed, **values}, metadata=_metadata(stamp_notary, request))

def _execute_notary(actor, document_id, fixed, values, _file, request):
    return stamp_notary.record_notary(actor=actor, loan_document_id=document_id, payload={**fixed, **values}, metadata=_metadata(stamp_notary, request))

def _execute_mismatch(actor, signature_id, values, _file, request):
    return signatures.resolve_mismatch(actor=actor, signature_record_id=signature_id, payload=values, metadata=_metadata(signatures, request))

def _execute_signed_copy(actor, application_id, document_id, values, uploaded_file, request):
    return documentation_actions.upload_signed_copy(actor=actor, application_id=application_id, loan_document_id=document_id, remarks=values.get('remarks'), uploaded_file=uploaded_file, request=request, metadata=_metadata(documentation_actions, request))

def _execute_review_action(actor, checklist_id, code, stage, role, item_id, document_id, values, _file, request):
    metadata = documentation_actions.RequestMetadata(request_id=request.headers.get('X-Request-ID'), ip_address=request.META.get('REMOTE_ADDR', ''), user_agent=request.headers.get('User-Agent', ''), workspace_action_id=getattr(request, '_workspace_action_id', None))
    return documentation_actions.record_review_action(actor=actor, checklist_id=checklist_id, action_type=code, reason=values.get('remarks') or values.get('condition'), approval_stage=stage, canonical_role_code=role, checklist_item_id=item_id, loan_document_id=document_id, metadata=metadata)

def replay_action(actor, application_id, action_id, payload, uploaded_file):
    try:
        return documentation_actions.replay_workspace_action(actor=actor, application_id=application_id, workspace_action_id=action_id, payload=payload, uploaded_file=uploaded_file)
    except documentation_actions.Conflict as exc:
        raise OwnerConflict(str(exc)) from exc
