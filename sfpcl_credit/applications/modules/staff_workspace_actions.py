"""Application-owned bank action decision for the staff documentation workspace."""
from functools import partial
from django.core.exceptions import ValidationError
from sfpcl_credit.applications.modules import bank_verification

class OwnerAccessDenied(Exception):
    pass

class OwnerNotFound(Exception):
    pass

class OwnerConflict(Exception):
    pass

def bank_verification_action(*, actor, application, fact):
    if fact.valid or not application.bank_account_id or (not application.cancelled_cheque_id):
        return None
    try:
        bank_verification.require_verifier(actor)
    except bank_verification.AccessDenied:
        return None
    return {'action_code': 'verify_bank_sources', 'label': 'Verify bank sources', 'enabled': True, 'disabled_reason': None, 'required_permission': 'documents.checklist.update', 'action_url': f'/api/v1/loan-applications/{application.pk}/bank-verification-decision/', 'method': 'POST', '_owner_execute': partial(_execute_bank_verification, actor, application.pk, application.bank_account_id, application.cancelled_cheque_id), 'fixed_payload': {'bank_account_id': str(application.bank_account_id), 'cancelled_cheque_id': str(application.cancelled_cheque_id)}, 'fields': [{'name': 'decision_status', 'label': 'Decision', 'type': 'select', 'required': True, 'options': ['verified', 'rejected']}]}

def _metadata(request):
    return bank_verification.RequestMetadata(request_id=request.headers.get('X-Request-ID'), ip_address=request.META.get('REMOTE_ADDR', ''), user_agent=request.headers.get('User-Agent', ''))

def _execute_bank_verification(actor, application_id, bank_id, cheque_id, values, _file, request):
    try:
        decision = bank_verification.record_decision(actor=actor, application_id=application_id, payload={'bank_account_id': str(bank_id), 'cancelled_cheque_id': str(cheque_id), **values}, metadata=_metadata(request))
        return bank_verification.action_response(decision)
    except ValidationError:
        raise
    except bank_verification.AccessDenied as exc:
        raise OwnerAccessDenied from exc
    except bank_verification.NotFound as exc:
        raise OwnerNotFound from exc
    except bank_verification.Conflict as exc:
        raise OwnerConflict(str(exc)) from exc
