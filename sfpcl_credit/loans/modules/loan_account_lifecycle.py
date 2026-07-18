from dataclasses import dataclass
from decimal import Decimal
import re
import uuid

from django.db import IntegrityError, transaction

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.applications.modules.application_authority import (
    evaluate_application_object_access,
)
from sfpcl_credit.approvals.models import (
    ApprovalCase,
    ApprovalCaseReadScopeGrant,
    SanctionDecision,
)
from sfpcl_credit.domain_errors import (
    DomainInvalidStateError,
    DomainObjectAccessDenied,
    DomainPermissionDenied,
    DomainValidationError,
)
from sfpcl_credit.identity.models import AuditLog, User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.legal_documents.selectors import (
    current_loan_term_document_for_update,
)
from sfpcl_credit.loans.models import LoanAccount, LoanStatusHistory, LoanTerms
from sfpcl_credit.members.models import Member, Nominee, Shareholding
from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
    SapCustomerProfileModule,
)
from sfpcl_credit.workflows.events import record_workflow_event
from sfpcl_credit.workflows.models import WorkflowEvent


CREATE_PERMISSION = "finance.loan_account.create"
CREATED_ACTION = "finance.loan_account.created"
_CREDIT_MONITORING_STATUSES = {
    "sanctioned",
    "ready_for_disbursement",
    "disbursement_in_progress",
    "active",
    "partially_repaid",
    "overdue",
    "grace_period",
    "extended",
    "non_recoverable_under_review",
}


class LoanAccountConflict(Exception):
    pass


@dataclass(frozen=True)
class RequestMetadata:
    request_id: str | None
    ip_address: str
    user_agent: str


@dataclass(frozen=True)
class ReadinessAccountFacts:
    loan_account_id: uuid.UUID
    loan_application_id: uuid.UUID
    member_id: uuid.UUID
    sanction_decision_id: uuid.UUID
    sap_customer_code_id: uuid.UUID | None
    loan_account_status: str
    sanctioned_amount: Decimal
    disbursement_amount: Decimal
    member_kyc_status: str
    relationships_coherent: bool


@dataclass(frozen=True)
class DisbursementAccountDecision:
    loan_account_id: uuid.UUID
    loan_application_id: uuid.UUID
    member_id: uuid.UUID
    sanction_decision_id: uuid.UUID
    sap_customer_code_id: uuid.UUID | None
    loan_terms_id: uuid.UUID
    creation_status_history_id: uuid.UUID
    creation_audit_id: uuid.UUID
    creation_workflow_event_id: uuid.UUID
    loan_account_status: str
    sanctioned_amount: Decimal
    loan_amount: Decimal
    disbursed_amount: Decimal
    principal_outstanding: Decimal
    interest_outstanding: Decimal
    charges_outstanding: Decimal
    total_outstanding: Decimal


def resolve_disbursement_account(*, loan_account_id):
    """Return immutable initiation facts only for a genuine lifecycle-created account."""
    account = (
        LoanAccount.objects.select_for_update(of=("self",))
        .select_related("terms", "loan_application", "member", "sanction_decision")
        .filter(pk=loan_account_id)
        .first()
    )
    if account is None:
        return None
    histories = list(
        LoanStatusHistory.objects.select_for_update()
        .filter(loan_account=account)
        .order_by("changed_at", "loan_status_history_id")[:2]
    )
    audits = list(
        AuditLog.objects.select_for_update()
        .filter(
            action=CREATED_ACTION,
            entity_type="loan_account",
            entity_id=account.pk,
        )
        .order_by("created_at", "audit_log_id")[:2]
    )
    workflows = list(
        WorkflowEvent.objects.select_for_update()
        .filter(
            workflow_name="LoanAccountCreated",
            entity_type="loan_account",
            entity_id=account.pk,
        )
        .order_by("created_at", "workflow_event_id")[:2]
    )
    if len(histories) != 1 or len(audits) != 1 or len(workflows) != 1:
        return None
    history, audit, workflow = histories[0], audits[0], workflows[0]
    evidence = audit.new_value_json or {}
    expected = {
        "loan_account_id": str(account.pk),
        "loan_application_id": str(account.loan_application_id),
        "member_id": str(account.member_id),
        "sanction_decision_id": str(account.sanction_decision_id),
        "sap_customer_code_id": (
            str(account.sap_customer_code_id) if account.sap_customer_code_id else None
        ),
        "loan_terms_id": str(account.terms.pk),
        "loan_account_status": LoanAccount.STATUS_SANCTIONED,
        "replay": False,
        "outcome": "created",
    }
    if (
        account.loan_account_status != LoanAccount.STATUS_SANCTIONED
        or account.loan_application.member_id != account.member_id
        or account.sanction_decision.loan_application_id != account.loan_application_id
        or account.terms.loan_account_id != account.pk
        or history.from_status is not None
        or history.to_status != LoanAccount.STATUS_SANCTIONED
        or history.reason != "Created from exact current terminal sanction."
        or history.changed_by_user_id != audit.actor_user_id
        or history.changed_by_user_id != workflow.triggered_by_user_id
        or history.loan_application_id_snapshot != account.loan_application_id
        or history.member_id_snapshot != account.member_id
        or history.sanction_decision_id_snapshot != account.sanction_decision_id
        or history.sap_customer_code_id_snapshot != account.sap_customer_code_id
        or history.loan_terms_id_snapshot != account.terms.pk
        or history.replay_flag is not False
        or history.outcome != "created"
        or audit.old_value_json != {}
        or set(evidence)
        != set(expected) | {"actor_role_codes", "actor_team_codes", "request_id"}
        or any(evidence.get(key) != value for key, value in expected.items())
        or not isinstance(evidence.get("actor_role_codes"), list)
        or not evidence.get("actor_role_codes")
        or not isinstance(evidence.get("actor_team_codes"), list)
        or evidence.get("request_id") is not None
        and not isinstance(evidence.get("request_id"), str)
        or workflow.from_state is not None
        or workflow.to_state != LoanAccount.STATUS_SANCTIONED
        or workflow.trigger_reason != "Created from exact current terminal sanction."
    ):
        return None
    return DisbursementAccountDecision(
        loan_account_id=account.pk,
        loan_application_id=account.loan_application_id,
        member_id=account.member_id,
        sanction_decision_id=account.sanction_decision_id,
        sap_customer_code_id=account.sap_customer_code_id,
        loan_terms_id=account.terms.pk,
        creation_status_history_id=history.pk,
        creation_audit_id=audit.pk,
        creation_workflow_event_id=workflow.pk,
        loan_account_status=account.loan_account_status,
        sanctioned_amount=account.sanctioned_amount,
        loan_amount=account.terms.loan_amount,
        disbursed_amount=account.disbursed_amount,
        principal_outstanding=account.principal_outstanding,
        interest_outstanding=account.interest_outstanding,
        charges_outstanding=account.charges_outstanding,
        total_outstanding=account.total_outstanding,
    )


def resolve_readiness_account(*, actor, loan_account_id, cfc_scope_resolver=None):
    """Resolve Stage-5 loan scope without reusing origination assignment."""
    actor = _locked_actor(actor)
    permissions = set(auth_service.effective_permission_codes(actor))
    permission = "finance.disbursement.readiness"
    readiness_roles = {
        "senior_manager_finance",
        "chief_financial_controller",
        "credit_manager",
        "cfo",
        "internal_auditor",
    }
    roles = set(auth_service.effective_role_codes(actor)).intersection(
        readiness_roles
    )
    if permission not in permissions or not roles:
        raise DomainPermissionDenied("Disbursement readiness permission is required.")
    account = (
        LoanAccount.objects.select_for_update(of=("self",))
        .select_related(
            "loan_application",
            "member",
            "sanction_decision",
            "terms",
        )
        .filter(pk=loan_account_id)
        .first()
    )
    if account is None:
        raise DomainObjectAccessDenied(None)
    scope_decisions = (
        (
            "senior_manager_finance" in roles
            and SapCustomerProfileModule.is_current_finance_assignee(
                application_id=account.loan_application_id,
                member_id=account.member_id,
                actor_id=actor.pk,
            )
        ),
        (
            "chief_financial_controller" in roles
            and bool(
                cfc_scope_resolver
                and cfc_scope_resolver(actor_id=actor.pk, loan_account_id=account.pk)
            )
        ),
        (
            "credit_manager" in roles
            and account.loan_account_status in _CREDIT_MONITORING_STATUSES
        ),
        "cfo" in roles,
        (
            "internal_auditor" in roles
            and ApprovalCaseReadScopeGrant.objects.filter(
                role__role_code="internal_auditor",
                scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
                status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
            ).exists()
        ),
    )
    if not any(scope_decisions):
        raise DomainObjectAccessDenied(None)
    if (
        account.loan_application.member_id != account.member_id
        or account.terms.loan_account_id != account.pk
        or account.sanction_decision.loan_application_id
        != account.loan_application_id
    ):
        raise DomainObjectAccessDenied(None)
    return ReadinessAccountFacts(
        loan_account_id=account.pk,
        loan_application_id=account.loan_application_id,
        member_id=account.member_id,
        sanction_decision_id=account.sanction_decision_id,
        sap_customer_code_id=account.sap_customer_code_id,
        loan_account_status=account.loan_account_status,
        sanctioned_amount=account.sanctioned_amount,
        disbursement_amount=account.terms.loan_amount,
        member_kyc_status=account.member.kyc_status,
        relationships_coherent=(
            account.loan_application.member_id == account.member_id
            and account.terms.loan_account_id == account.pk
        ),
    )


def create_loan_account(*, actor, application_id, payload, request=None, metadata=None):
    cleaned = _validate_payload(payload)
    metadata = metadata or RequestMetadata(
        request.headers.get("X-Request-ID") if request else None,
        request_ip(request) if request else "",
        request_user_agent(request) if request else "",
    )
    with transaction.atomic():
        actor = _locked_actor(actor)
        permissions = set(auth_service.effective_permission_codes(actor))
        if CREATE_PERMISSION not in permissions:
            raise DomainPermissionDenied("Loan account creation permission is required.")
        application = (
            LoanApplication.objects.select_for_update(of=("self",))
            .select_related("member", "nominee", "created_by_user", "received_by_user")
            .filter(pk=application_id)
            .first()
        )
        if application is None:
            raise DomainObjectAccessDenied(None)
        access = evaluate_application_object_access(
            application=application,
            actor=actor,
            required_permission=CREATE_PERMISSION,
            actor_permissions=permissions,
        )
        if not access.allowed:
            raise DomainObjectAccessDenied(access)

        retained = (
            LoanAccount.objects.select_for_update(of=("self",))
            .select_related("terms")
            .filter(loan_application=application)
            .first()
        )
        if retained is not None:
            if (
                retained.sanction_decision_id == cleaned["sanction_decision_id"]
                and retained.loan_account_number_normalized
                == cleaned["normalized_number"]
            ):
                return serialize_loan_account(retained, retained.terms)
            raise LoanAccountConflict(
                "A loan account already exists for this application with different facts."
            )
        if LoanAccount.objects.filter(
            loan_account_number_normalized=cleaned["normalized_number"]
        ).exists():
            raise LoanAccountConflict("The loan account number is already in use.")

        case = (
            ApprovalCase.objects.select_for_update()
            .filter(loan_application=application)
            .order_by("-cycle_number", "-submitted_at", "-approval_case_id")
            .first()
        )
        sanction = (
            SanctionDecision.objects.select_for_update()
            .filter(pk=cleaned["sanction_decision_id"], loan_application=application)
            .first()
        )
        _require_current_terminal_source(application, case, sanction)
        snapshots = _locked_term_snapshots(application, case)
        documents = _locked_current_documents(application)
        sap_code_id = _coherent_sap_code_id(application)

        try:
            with transaction.atomic():
                account = LoanAccount.objects.create(
                    loan_application=application,
                    loan_account_number=cleaned["loan_account_number"],
                    loan_account_number_normalized=cleaned["normalized_number"],
                    member=application.member,
                    sap_customer_code_id=sap_code_id,
                    sanction_decision=sanction,
                    sanctioned_amount=sanction.sanctioned_amount,
                    loan_type=snapshots["facility_type"],
                    interest_rate_type=sanction.interest_rate_type,
                    current_interest_rate=sanction.interest_rate_value,
                    repayment_date=sanction.repayment_date,
                )
        except IntegrityError as exc:
            raise LoanAccountConflict(
                "The application or loan account number already has an account."
            ) from exc
        terms = LoanTerms.objects.create(
            loan_account=account,
            borrower_details_snapshot_json=snapshots["borrower"],
            nominee_details_snapshot_json=snapshots["nominee"],
            shareholding_snapshot_json=snapshots["shareholding"],
            facility_type=snapshots["facility_type"],
            loan_amount=sanction.sanctioned_amount,
            purpose=snapshots["purpose"],
            rate_of_interest=sanction.interest_rate_value,
            interest_rate_type=sanction.interest_rate_type,
            interest_tenure=f"{sanction.sanctioned_tenure_months} months",
            repayment_date=sanction.repayment_date,
            penalty_interest_rate=sanction.penal_interest_rate,
            other_charges_fees_json=sanction.charges_json,
            security_details_json={"summary": sanction.security_required_summary},
            dispute_resolution_text=snapshots["dispute_resolution"],
            term_sheet_document_id=documents["term_sheet"].document_id,
            loan_agreement_document_id=documents["loan_agreement"].document_id,
        )
        LoanStatusHistory.objects.create(
            loan_account=account,
            from_status=None,
            to_status=LoanAccount.STATUS_SANCTIONED,
            reason="Created from exact current terminal sanction.",
            changed_by_user=actor,
            loan_application_id_snapshot=application.pk,
            member_id_snapshot=application.member_id,
            sanction_decision_id_snapshot=sanction.pk,
            sap_customer_code_id_snapshot=sap_code_id,
            loan_terms_id_snapshot=terms.pk,
            replay_flag=False,
            outcome="created",
        )
        evidence = _evidence(account, terms, actor, metadata)
        AuditLog.objects.create(
            actor_user=actor,
            actor_type="user",
            action=CREATED_ACTION,
            entity_type="loan_account",
            entity_id=account.pk,
            old_value_json={},
            new_value_json=evidence,
            ip_address=metadata.ip_address,
            user_agent=metadata.user_agent,
        )
        record_workflow_event(
            actor=actor,
            workflow_name="LoanAccountCreated",
            entity_type="loan_account",
            entity_id=account.pk,
            from_state=None,
            to_state=LoanAccount.STATUS_SANCTIONED,
            trigger_reason="Created from exact current terminal sanction.",
            action_code=CREATED_ACTION,
            metadata=evidence,
        )
        return serialize_loan_account(account, terms)


def serialize_loan_account(account, terms):
    return {
        "loan_account_id": str(account.pk),
        "loan_application_id": str(account.loan_application_id),
        "member_id": str(account.member_id),
        "sanction_decision_id": str(account.sanction_decision_id),
        "sap_customer_code_id": (
            str(account.sap_customer_code_id) if account.sap_customer_code_id else None
        ),
        "loan_account_number": account.loan_account_number,
        "loan_account_status": account.loan_account_status,
        "sanctioned_amount": f"{account.sanctioned_amount:.2f}",
        "loan_type": account.loan_type,
        "interest_rate_type": account.interest_rate_type,
        "current_interest_rate": f"{account.current_interest_rate:.4f}",
        "repayment_date": account.repayment_date.isoformat(),
        "loan_terms_id": str(terms.pk),
    }


def _validate_payload(payload):
    allowed = {"sanction_decision_id", "loan_account_number"}
    errors = {field: "Unknown field." for field in sorted(set(payload) - allowed)}
    try:
        sanction_id = uuid.UUID(str(payload.get("sanction_decision_id") or ""))
    except (ValueError, TypeError, AttributeError):
        sanction_id = None
        errors["sanction_decision_id"] = "Must be a valid UUID."
    number = re.sub(r"\s+", " ", str(payload.get("loan_account_number") or "").strip())
    if not number:
        errors["loan_account_number"] = "This field is required."
    elif len(number) > 80:
        errors["loan_account_number"] = "Must be at most 80 characters."
    if errors:
        raise DomainValidationError(errors)
    return {
        "sanction_decision_id": sanction_id,
        "loan_account_number": number,
        "normalized_number": number.casefold(),
    }


def _locked_actor(actor):
    persisted = (
        User.objects.select_for_update()
        .select_related("primary_role")
        .filter(pk=getattr(actor, "pk", None), status=User.ACTIVE_STATUS)
        .first()
    )
    if persisted is None:
        raise DomainPermissionDenied("An active persisted user is required.")
    return persisted


def _require_current_terminal_source(application, case, sanction):
    if (
        application.application_status
        != LoanApplication.STATUS_APPROVED_BY_SANCTION
        or case is None
        or case.current_status != ApprovalCase.STATUS_APPROVED
        or sanction is None
        or sanction.approval_case_id != case.pk
        or sanction.decision != "sanctioned"
    ):
        raise DomainInvalidStateError("The exact current terminal sanction is required.")
    missing = {}
    required = {
        "sanctioned_amount": sanction.sanctioned_amount,
        "sanction_date": sanction.recorded_at,
        "loan_type": application.loan_type_requested,
        "interest_rate_type": sanction.interest_rate_type,
        "current_interest_rate": sanction.interest_rate_value,
        "sanctioned_tenure_months": sanction.sanctioned_tenure_months,
        "repayment_date": sanction.repayment_date,
        "penalty_interest_rate": sanction.penal_interest_rate,
        "charges": sanction.charges_json,
        "security": sanction.security_required_summary,
    }
    for field, value in required.items():
        if value in (None, "", {}):
            missing[field] = "Current governed sanction evidence is required."
    if sanction.sanctioned_amount is not None and sanction.sanctioned_amount <= Decimal("0"):
        missing["sanctioned_amount"] = "Must be greater than zero."
    if application.loan_type_requested not in LoanAccount.LOAN_TYPES:
        missing["loan_type"] = "Must be short_term or long_term."
    if sanction.interest_rate_type != "floating":
        missing["interest_rate_type"] = "Must be floating."
    if missing:
        raise DomainValidationError(missing)


def _locked_term_snapshots(application, case):
    member = Member.objects.select_for_update().get(pk=application.member_id)
    nominee = (
        Nominee.objects.select_for_update().filter(pk=application.nominee_id).first()
        if application.nominee_id
        else None
    )
    facts = case.appraisal_facts_json or {}
    borrower = facts.get("borrower") or {}
    nominee_facts = facts.get("nominee") or {}
    shareholding_facts = facts.get("shareholding") or {}
    purpose = (facts.get("purpose") or {}).get("description")
    dispute_resolution = facts.get("dispute_resolution")
    shareholding = Shareholding.objects.select_for_update().filter(
        pk=shareholding_facts.get("shareholding_id"),
        member=member,
        status="active",
    ).first()
    frozen_borrower = {
        "member_id": str(member.pk),
        "name": member.legal_name,
        "member_type": member.member_type,
        "folio_number": member.folio_number,
    }
    borrower_snapshot = {
        "member_id": str(member.pk),
        "legal_name": member.legal_name,
        "member_type": member.member_type,
        "folio_number": member.folio_number,
    }
    expected_nominee = (
        {
            "nominee_id": str(nominee.pk),
            "name": nominee.nominee_name,
            "relationship": nominee.relationship_to_borrower,
        }
        if nominee
        else None
    )
    expected_shareholding = (
        {
            "shareholding_id": str(shareholding.pk),
            "folio_number": shareholding.folio_number,
            "number_of_shares": shareholding.number_of_shares,
            "holding_mode": shareholding.holding_mode,
        }
        if shareholding
        else None
    )
    errors = {}
    comparisons = (
        (
            "borrower",
            {key: borrower.get(key) for key in frozen_borrower}
            if isinstance(borrower, dict)
            else borrower,
            frozen_borrower,
        ),
        ("nominee", nominee_facts, expected_nominee),
        ("shareholding", shareholding_facts, expected_shareholding),
    )
    for field, actual, expected in comparisons:
        if expected is None or actual != expected:
            errors[field] = "Current facts do not match the frozen sanction review."
    if not purpose:
        errors["purpose"] = "Current governed purpose evidence is required."
    if not isinstance(dispute_resolution, str) or not dispute_resolution.strip():
        errors["dispute_resolution"] = "Current governed dispute term is required."
    if errors:
        raise DomainValidationError(errors)
    return {
        "borrower": borrower_snapshot,
        "nominee": nominee_facts,
        "shareholding": shareholding_facts,
        "purpose": purpose,
        "dispute_resolution": dispute_resolution.strip(),
        "facility_type": application.loan_type_requested,
    }


def _locked_current_documents(application):
    result = {}
    for document_type in ("term_sheet", "loan_agreement"):
        document = current_loan_term_document_for_update(
            application_id=application.pk,
            document_type=document_type,
        )
        if document is None:
            raise DomainValidationError(
                {document_type: "Current executed and verified legal evidence is required."}
            )
        result[document_type] = document
    return result


def _coherent_sap_code_id(application):
    decision = SapCustomerProfileModule.get_customer_code_for_member(
        application.member_id, for_update=True
    )
    if decision is None:
        return None
    if (
        decision.member_id != application.member_id
        or decision.loan_application_id != application.pk
        or decision.status != "active"
    ):
        return None
    return decision.customer_code_id


def _evidence(account, terms, actor, metadata):
    return {
        "loan_account_id": str(account.pk),
        "loan_application_id": str(account.loan_application_id),
        "member_id": str(account.member_id),
        "sanction_decision_id": str(account.sanction_decision_id),
        "sap_customer_code_id": (
            str(account.sap_customer_code_id) if account.sap_customer_code_id else None
        ),
        "loan_terms_id": str(terms.pk),
        "loan_account_status": account.loan_account_status,
        "replay": False,
        "outcome": "created",
        "actor_role_codes": actor.role_codes(),
        "actor_team_codes": actor.team_codes(),
        "request_id": metadata.request_id,
    }


__all__ = [
    "CREATE_PERMISSION",
    "DisbursementAccountDecision",
    "LoanAccountConflict",
    "RequestMetadata",
    "ReadinessAccountFacts",
    "create_loan_account",
    "resolve_readiness_account",
    "resolve_disbursement_account",
    "serialize_loan_account",
]
