"""Security-instrument decisions for the S26-S35 staff workspace."""
from dataclasses import dataclass
from functools import partial
from sfpcl_credit.applications.models import Witness
from sfpcl_credit.applications.modules import document_checklist_facts
from sfpcl_credit.members.models import Shareholding
from sfpcl_credit.security_instruments.modules import blank_dated_cheque, cdsl_share_pledge, power_of_attorney, sh4
from sfpcl_credit.security_instruments.request_contracts import BlankDatedChequeRequest, CDSLSharePledgeRequest, PowerOfAttorneyRequest, SH4ShareTransferFormRequest

class OwnerAccessDenied(Exception):
    pass

class OwnerNotFound(Exception):
    pass

class OwnerConflict(Exception):
    pass

@dataclass(frozen=True)
class CreationGateways:
    create_poa: object
    create_sh4: object
    create_pledge: object
    create_blank_cheque: object

def _action(action_code, label, required_permission, action_url, *, owner_execute, fixed_payload=None, fields=None):
    result = {'action_code': action_code, 'label': label, 'enabled': True, 'disabled_reason': None, 'required_permission': required_permission, 'action_url': action_url, 'method': 'POST', '_owner_execute': owner_execute}
    if fixed_payload:
        result['fixed_payload'] = fixed_payload
    if fields:
        result['fields'] = fields
    return result

def _owner_allows(authorizer, actor):
    try:
        authorizer(actor)
    except (power_of_attorney.AccessDenied, sh4.AccessDenied, cdsl_share_pledge.AccessDenied, blank_dated_cheque.AccessDenied):
        return False
    return True

def project_workflows(actor, package, items, *, legal_facts, gateways):
    by_code = {row['item_code']: row for row in items}
    result = {'tri_party_agreement': _workflow_from_item(by_code['tri_party_agreement']), 'cancelled_cheque': _workflow_from_item(by_code['cancelled_cheque'])}
    if package is None:
        result.update({'power_of_attorney': _workflow(True, 'pending', []), 'sh4': _workflow_from_item(by_code['sh4']), 'cdsl_pledge': _workflow_from_item(by_code['cdsl_pledge']), 'blank_dated_cheque': _workflow_from_item(by_code['blank_dated_cheque'])})
        return result
    specs = {'power_of_attorney': (package.poa_required_flag, getattr(package, 'power_of_attorney', None), 'status', power_of_attorney.require_manage_actor, 'security.poa.manage', 'power-of-attorney'), 'sh4': (package.physical_share_security_required_flag, getattr(package, 'sh4_share_transfer_form', None), 'form_status', sh4.require_manage_actor, 'security.sh4.manage', 'sh4-share-transfer-form'), 'cdsl_pledge': (package.demat_pledge_required_flag, getattr(package, 'cdsl_share_pledge', None), 'pledge_status', cdsl_share_pledge.require_manage_actor, 'security.cdsl_pledge.manage', 'cdsl-share-pledge'), 'blank_dated_cheque': (package.blank_cheque_required_flag, getattr(package, 'blank_dated_cheque', None), 'cheque_status', blank_dated_cheque.require_manage_actor, 'security.blank_cheque.manage', 'blank-dated-cheque')}
    for code, spec in specs.items():
        required, row, field, authorizer, permission, collection = spec
        actions = []
        if required and row is None and _owner_allows(authorizer, actor):
            endpoint = f'/api/v1/security-packages/{package.pk}/{collection}/'
            action = _security_create_action(actor, package, code, permission, endpoint, legal_facts=legal_facts, gateways=gateways)
            if action:
                actions.append(action)
        result[code] = _workflow(required, getattr(row, field, 'pending'), actions)
    return result

def _security_create_action(actor, package, code, permission, endpoint, *, legal_facts, gateways):
    """Expose create only when every server-owned prerequisite can be selected."""
    application = package.loan_application
    fixed, fields, request_type, creator = (None, [], None, None)
    if code == 'power_of_attorney':
        attorney = None
        if application.nominee_id and legal_facts.poa_document_id and legal_facts.poa_stamp_id and legal_facts.poa_notary_id and attorney:
            request_type = PowerOfAttorneyRequest
            creator = gateways.create_poa
            fixed = {'borrower_member_id': str(application.member_id), 'nominee_id': str(application.nominee_id), 'attorney_user_id': str(attorney.pk), 'loan_document_id': str(legal_facts.poa_document_id), 'stamp_duty_record_id': str(legal_facts.poa_stamp_id), 'notarisation_record_id': str(legal_facts.poa_notary_id), 'execution_status': 'pending', 'effective_from': None, 'status': 'draft'}
            fields = [{'name': 'purpose_summary', 'label': 'Purpose and authority', 'type': 'textarea', 'required': True}]
    elif code == 'sh4':
        witnesses = list(Witness.objects.filter(loan_application=application, verification_status='verified', shareholder_verified_flag=True).order_by('created_at', 'witness_id')[:2])
        holdings = list(Shareholding.objects.filter(member=application.member, holding_mode='physical', status='active').order_by('created_at', 'shareholding_id')[:2])
        witness = witnesses[0] if len(witnesses) == 1 else None
        holding = holdings[0] if len(holdings) == 1 else None
        if witness and holding and legal_facts.sh4_document_id:
            request_type = SH4ShareTransferFormRequest
            creator = gateways.create_sh4
            fixed = {'member_id': str(application.member_id), 'witness_id': str(witness.pk), 'shareholding_id': str(holding.pk), 'share_count': None, 'loan_document_id': str(legal_facts.sh4_document_id), 'form_status': 'pending', 'custody_location': None, 'signed_at': None}
    elif code == 'cdsl_pledge':
        if Shareholding.objects.filter(member=application.member, holding_mode='demat', status='active', demat_account_id__isnull=False).exists():
            request_type = CDSLSharePledgeRequest
            creator = gateways.create_pledge
            fixed = {'pledgor_member_id': str(application.member_id), 'pledgee_entity_name': cdsl_share_pledge.SFPCL_ENTITY_NAME, 'pledgee_bo_account': None, 'pledgor_dp_name': None, 'pledgee_dp_name': None, 'prf_status': 'prepared', 'pledge_sequence_number': None, 'pledge_acceptance_status': 'pending', 'pledged_share_count': None, 'agreement_number': None, 'pledge_status': 'pending', 'evidence_document_id': None}
            fields = [{'name': 'pledgor_bo_account', 'label': 'Pledgor BO account', 'type': 'text', 'required': True}]
    elif code == 'blank_dated_cheque':
        fact = document_checklist_facts.resolve_blank_cheque_bank_fact(application_id=application.pk)
        if fact.valid:
            request_type = BlankDatedChequeRequest
            creator = gateways.create_blank_cheque
            fixed = {'member_id': str(fact.member_id), 'bank_account_id': str(fact.bank_account_id), 'document_id': None, 'cheque_status': 'collected', 'custody_location': None}
            fields = [{'name': 'cheque_number', 'label': 'Cheque number', 'type': 'text', 'required': True}, {'name': 'collected_at', 'label': 'Collected date', 'type': 'date', 'required': True}]
    if fixed is None or request_type is None or creator is None:
        return None
    fixed['security_package_id'] = str(package.pk)
    return _action(f'manage_{code}', f"Manage {code.replace('_', ' ').title()}", permission, endpoint, owner_execute=partial(_execute_security_create, actor, package.pk, dict(fixed), request_type, creator), fixed_payload=fixed, fields=fields)

def _workflow(required, status, actions):
    return {'required': required, 'status': status if required else 'not_required', 'available_actions': actions}

def _workflow_from_item(item):
    return _workflow(item['applicable'], item['status'], item['available_actions'])

def _metadata(request):
    return power_of_attorney.RequestMetadata(request_id=request.headers.get('X-Request-ID'), ip_address=request.META.get('REMOTE_ADDR', ''), user_agent=request.headers.get('User-Agent', ''))

def _execute_security_create(actor, package_id, fixed, request_type, creator, values, _file, request):
    payload = {**fixed, **values}
    payload.pop('security_package_id', None)
    parsed = request_type.parse(payload)
    try:
        return creator(actor=actor, security_package_id=package_id, values=parsed.as_values(), metadata=_metadata(request))
    except (power_of_attorney.AccessDenied, sh4.AccessDenied, cdsl_share_pledge.AccessDenied, blank_dated_cheque.AccessDenied) as exc:
        raise OwnerAccessDenied from exc
    except (power_of_attorney.NotFound, sh4.NotFound, cdsl_share_pledge.NotFound, blank_dated_cheque.NotFound) as exc:
        raise OwnerNotFound from exc
    except (power_of_attorney.Conflict, sh4.Conflict, cdsl_share_pledge.Conflict, blank_dated_cheque.Conflict) as exc:
        raise OwnerConflict(str(exc)) from exc
