"""Borrower-safe projection of current disbursement and advice owner truth."""

import re
from dataclasses import dataclass
from datetime import timedelta

from django.core import signing
from django.db import transaction
from django.utils import timezone

from sfpcl_credit.approvals.modules.document_checklist_facts import resolve_approved_facts
from sfpcl_credit.communications.modules.communication_dispatcher import (
    FinalizedAdviceArtifact,
    resolve_finalized_advice_artifact,
)
from sfpcl_credit.communications.models import CommunicationDeliveryOutbox
from sfpcl_credit.disbursements.models import Disbursement
from sfpcl_credit.disbursements.modules.post_transfer_evidence import (
    resolve_post_transfer_evidence,
)
from sfpcl_credit.disbursements.modules.current_disbursement_evidence import (
    resolve_current_disbursement_evidence,
)
from sfpcl_credit.disbursements.modules.disbursement_advice import (
    resolve_current_advice_context,
)
from sfpcl_credit.disbursements.modules.disbursement_authorisation import (
    is_current_terminal_authorisation,
)
from sfpcl_credit.legal_documents.modules.disbursement_readiness import (
    resolve_legal_readiness,
)
from sfpcl_credit.loans.models import LoanAccount
from sfpcl_credit.loans.modules.loan_account_lifecycle import (
    resolve_disbursement_account,
)
from sfpcl_credit.processes import portal_application_scope
from sfpcl_credit.processes.security_instrument_evidence import (
    terminal_checklist_evidence,
)
from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
    get_customer_code_for_member,
)
from sfpcl_credit.identity.models import AuditLog, PortalAccount, User
from sfpcl_credit.api import request_ip, request_user_agent


class PortalDisbursementNotFound(Exception):
    pass


@dataclass(frozen=True)
class PortalAdviceContent:
    body: bytes
    file_name: str
    mime_type: str = "text/plain; charset=utf-8"


@dataclass(frozen=True)
class _TerminalAdvice:
    context: object
    row: Disbursement
    account: LoanAccount
    artifact: FinalizedAdviceArtifact


_CAPABILITY_SALT = "sfpcl.portal-disbursement-advice.v1"
_CAPABILITY_TTL_SECONDS = 15 * 60


_TIMELINE = (
    ("documentation_complete", "Documents completed."),
    ("sap_setup", "Finance setup complete."),
    ("payment_initiated", "Payment processing started."),
    ("cfc_authorisation", "Payment approved."),
    ("transfer_completed", "Loan amount transferred."),
    ("advice_issued", "Disbursement advice issued."),
)


@transaction.atomic
def get_projection(*, actor, application_id):
    try:
        context = portal_application_scope.resolve(
            actor=actor, application_id=application_id
        )
    except portal_application_scope.PortalApplicationScopeNotFound as exc:
        raise PortalDisbursementNotFound from exc
    application = context.application
    sanction = resolve_approved_facts(application_id=application.pk)
    if sanction is None:
        return _projection(application, sanctioned_amount=None)
    stages = _current_pre_payment_stages(
        application_id=application.pk,
        member_id=context.account.member_id,
    )
    account = (
        LoanAccount.objects.select_related("sanction_decision")
        .filter(
            loan_application=application,
            member_id=context.account.member_id,
            sanction_decision_id=sanction.sanction_decision_id,
        )
        .first()
    )
    if account is None or account.sanctioned_amount != sanction.sanctioned_amount:
        return _projection(
            application,
            sanctioned_amount=sanction.sanctioned_amount,
            stage_truth=stages,
        )
    account_decision = resolve_disbursement_account(loan_account_id=account.pk)
    if (
        account_decision is None
        or account_decision.loan_application_id != application.pk
        or account_decision.member_id != context.account.member_id
        or not stages["completed"].get("documentation_complete")
        or not stages["completed"].get("sap_setup")
        or account_decision.sap_customer_code_id
        != stages.get("sap_customer_code_id")
    ):
        return _projection(
            application,
            sanctioned_amount=sanction.sanctioned_amount,
            loan_account_id=account.pk,
            status_code="disbursement_blocked",
            stage_truth=stages,
        )
    transfer = resolve_post_transfer_evidence(application_id=application.pk)
    if transfer is None:
        current = resolve_current_disbursement_evidence(
            loan_account_id=account.pk,
            allowed_authorisation_statuses=("pending", "approved", "rejected"),
        )
        current_row = (
            Disbursement.objects.select_related("borrower_bank_account")
            .filter(pk=current.disbursement_id)
            .first()
            if current is not None
            and current.loan_application_id == application.pk
            and current.member_id == context.account.member_id
            else None
        )
        if current_row is not None and current.authorisation_status in {
            "pending",
            "approved",
        }:
            return _progress_projection(
                application=application,
                account=account,
                row=current_row,
                sanctioned_amount=sanction.sanctioned_amount,
                status_code=(
                    "cfc_authorisation_pending"
                    if current.authorisation_status == "pending"
                    else "payment_processing"
                ),
                completed_count=(
                    3 if current.authorisation_status == "pending" else 4
                ),
                stage_truth=stages,
                initiated_at=current.initiated_at,
                authorised_at=current.authorised_at,
            )
        if (
            current_row is not None
            and current.authorisation_status == "rejected"
            and is_current_terminal_authorisation(
                current_row,
                {
                    "decision": "rejected",
                    "comments": current_row.authorisation_comments or "",
                },
            )
        ):
            return _progress_projection(
                application=application,
                account=account,
                row=current_row,
                sanctioned_amount=sanction.sanctioned_amount,
                status_code="disbursement_blocked",
                completed_count=3,
                blocked_index=3,
                stage_truth=stages,
                initiated_at=current.initiated_at,
            )
        has_terminal_claim = Disbursement.objects.filter(
            loan_application=application,
            loan_account=account,
            member_id=context.account.member_id,
        ).exclude(
            bank_transfer_status="pending",
            bank_reference_number__isnull=True,
            disbursed_at__isnull=True,
        ).exists()
        return _projection(
            application,
            sanctioned_amount=sanction.sanctioned_amount,
            loan_account_id=account.pk,
            status_code=(
                "disbursement_blocked" if has_terminal_claim else "finance_setup_pending"
            ),
            stage_truth=stages,
        )
    row = (
        Disbursement.objects.select_related(
            "borrower_bank_account", "advice_intent"
        )
        .filter(
            pk=transfer.disbursement_id,
            loan_account=account,
            loan_application=application,
            member_id=context.account.member_id,
        )
        .first()
    )
    if row is None or row.disbursement_amount != transfer.amount:
        return _projection(
            application,
            sanctioned_amount=sanction.sanctioned_amount,
            loan_account_id=account.pk,
            status_code="disbursement_blocked",
            stage_truth=stages,
        )
    artifact = None
    if row.disbursement_advice_communication_id:
        advice_context = resolve_current_advice_context(disbursement_id=row.pk)
        artifact = (
            resolve_finalized_advice_artifact(context=advice_context)
            if advice_context is not None
            else None
        )
        if artifact is not None and not _artifact_is_current(row, artifact):
            artifact = None
    completed_at = _iso(transfer.disbursed_at)
    terminal_stage_times = {
        **stages["times"],
        "payment_initiated": transfer.initiated_at,
        "cfc_authorisation": transfer.authorised_at,
        "transfer_completed": transfer.disbursed_at,
        "advice_issued": artifact.sent_at if artifact is not None else None,
    }
    timeline = []
    for index, (code, label) in enumerate(_TIMELINE):
        completed = index < 5 or (index == 5 and artifact is not None)
        timeline.append(
            {
                "code": code,
                "label": label,
                "status": "complete" if completed else "pending",
                "completed_at": (
                    _iso(terminal_stage_times[code])
                    if completed and terminal_stage_times.get(code)
                    else None
                ),
            }
        )
    return {
        "loan_application_id": str(application.pk),
        "loan_account_id": str(account.pk),
        "status_code": "disbursed",
        "status_label": "Loan amount transferred.",
        "sanctioned_amount": f"{sanction.sanctioned_amount:.2f}",
        "disbursement_amount": f"{row.disbursement_amount:.2f}",
        "destination_account_last4": row.borrower_bank_account.account_number_last4 or None,
        "disbursed_at": completed_at,
        "bank_reference_last4": row.bank_reference_number[-4:] if row.bank_reference_number else None,
        "advice_available": artifact is not None,
        "timeline": timeline,
    }


@transaction.atomic
def issue_advice_capability(*, actor, application_id, request):
    terminal = _resolve_terminal_advice(actor=actor, application_id=application_id)
    outbox = CommunicationDeliveryOutbox.objects.select_for_update().get(
        pk=terminal.artifact.outbox_id
    )
    outbox.portal_capability_version += 1
    outbox.portal_capability_expires_at = timezone.now() + timedelta(
        seconds=_CAPABILITY_TTL_SECONDS
    )
    outbox.portal_capability_consumed_at = None
    outbox.save(
        update_fields=[
            "portal_capability_version",
            "portal_capability_expires_at",
            "portal_capability_consumed_at",
        ]
    )
    token = signing.dumps(
        _capability_claims(terminal, outbox), salt=_CAPABILITY_SALT, compress=True
    )
    _record_download_audit(
        actor=actor, terminal=terminal, request=request, outcome="issued"
    )
    return {
        "download_url": (
            f"/api/v1/portal/applications/{application_id}/"
            f"disbursement-advice/content/?capability={token}"
        ),
        "expires_at": _iso(outbox.portal_capability_expires_at),
    }


@transaction.atomic
def read_advice(*, actor, application_id, capability, request):
    try:
        claims = signing.loads(
            capability, salt=_CAPABILITY_SALT, max_age=_CAPABILITY_TTL_SECONDS
        )
    except (signing.BadSignature, signing.SignatureExpired) as exc:
        raise PortalDisbursementNotFound from exc
    terminal = _resolve_terminal_advice(actor=actor, application_id=application_id)
    outbox = CommunicationDeliveryOutbox.objects.select_for_update().get(
        pk=terminal.artifact.outbox_id
    )
    if (
        claims != _capability_claims(terminal, outbox)
        or outbox.portal_capability_expires_at is None
        or outbox.portal_capability_expires_at <= timezone.now()
        or outbox.portal_capability_consumed_at is not None
    ):
        raise PortalDisbursementNotFound
    outbox.portal_capability_consumed_at = timezone.now()
    outbox.save(update_fields=["portal_capability_consumed_at"])
    _record_download_audit(
        actor=actor,
        terminal=terminal,
        request=request,
        outcome="accepted",
    )
    raw_reference = terminal.context.application.application_reference_number or str(application_id)
    reference = re.sub(r"[^A-Za-z0-9_-]+", "-", raw_reference).strip("-") or str(application_id)
    return PortalAdviceContent(
        body=terminal.artifact.body,
        file_name=f"disbursement-advice-{reference}.txt",
    )


def record_download_denial(*, actor, application_id, request):
    persisted = User.objects.filter(pk=getattr(actor, "pk", None)).first()
    if persisted is None:
        return None
    account = PortalAccount.objects.filter(user=persisted).first()
    return AuditLog.objects.create(
        actor_user=persisted,
        actor_type="portal_account",
        action="portal.document.downloaded",
        entity_type="loan_application",
        entity_id=application_id,
        old_value_json=None,
        new_value_json={
            "portal_account_id": str(account.pk) if account else None,
            "member_id": str(account.member_id) if account else None,
            "loan_application_id": str(application_id),
            "document_category": "disbursement_advice",
            "request_id": request.headers.get("X-Request-ID"),
            "network": {
                "ip_address": request_ip(request),
                "user_agent": request_user_agent(request),
            },
            "outcome": "denied",
        },
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )


def _resolve_terminal_advice(*, actor, application_id):
    try:
        context = portal_application_scope.resolve(
            actor=actor, application_id=application_id
        )
    except portal_application_scope.PortalApplicationScopeNotFound as exc:
        raise PortalDisbursementNotFound from exc
    transfer = resolve_post_transfer_evidence(application_id=context.application.pk)
    if transfer is None or transfer.member_id != context.account.member_id:
        raise PortalDisbursementNotFound
    account = LoanAccount.objects.filter(
        pk=transfer.loan_account_id,
        loan_application=context.application,
        member_id=context.account.member_id,
    ).first()
    row = Disbursement.objects.filter(
        pk=transfer.disbursement_id,
        loan_account=account,
        loan_application=context.application,
        member_id=context.account.member_id,
    ).first()
    if row is None or not row.disbursement_advice_communication_id:
        raise PortalDisbursementNotFound
    advice_context = resolve_current_advice_context(disbursement_id=row.pk)
    artifact = (
        resolve_finalized_advice_artifact(context=advice_context)
        if advice_context is not None
        else None
    )
    if artifact is None or not _artifact_is_current(row, artifact):
        raise PortalDisbursementNotFound
    return _TerminalAdvice(context=context, row=row, account=account, artifact=artifact)


def _capability_claims(terminal, outbox):
    return {
        "portal_account_id": str(terminal.context.account.pk),
        "member_id": str(terminal.context.account.member_id),
        "loan_application_id": str(terminal.context.application.pk),
        "loan_account_id": str(terminal.account.pk),
        "advice_intent_id": str(terminal.row.advice_intent.pk),
        "artifact_id": str(terminal.artifact.outbox_id),
        "communication_id": str(terminal.artifact.communication_id),
        "checksum_sha256": terminal.artifact.checksum_sha256,
        "version": outbox.portal_capability_version,
    }


def _artifact_is_current(row, artifact):
    intent = row.advice_intent
    return bool(
        intent.delivery_status == intent.DELIVERY_SENT
        and intent.delivery_action_id == artifact.action_id
        and intent.delivery_audit_id == artifact.audit_id
        and intent.delivery_workflow_event_id == artifact.workflow_id
        and intent.delivery_evidence_digest == artifact.delivery_evidence_digest
        and row.disbursement_advice_communication_id == artifact.communication_id
    )


def _record_download_audit(*, actor, terminal, request, outcome):
    return AuditLog.objects.create(
        actor_user=actor,
        actor_type="portal_account",
        action="portal.document.downloaded",
        entity_type="communication_delivery_outbox",
        entity_id=terminal.artifact.outbox_id,
        old_value_json=None,
        new_value_json={
            "portal_account_id": str(terminal.context.account.pk),
            "member_id": str(terminal.context.account.member_id),
            "loan_application_id": str(terminal.context.application.pk),
            "loan_account_id": str(terminal.account.pk),
            "advice_id": str(terminal.artifact.communication_id),
            "artifact_id": str(terminal.artifact.outbox_id),
            "document_category": "disbursement_advice",
            "request_id": request.headers.get("X-Request-ID"),
            "network": {
                "ip_address": request_ip(request),
                "user_agent": request_user_agent(request),
            },
            "outcome": outcome,
        },
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )


def _iso(value):
    return value.isoformat().replace("+00:00", "Z")


def _current_pre_payment_stages(*, application_id, member_id):
    legal = resolve_legal_readiness(
        application_id=application_id,
        terminal_security_evidence=terminal_checklist_evidence,
    )
    sap = get_customer_code_for_member(member_id)
    sap_is_current = bool(
        sap
        and sap.member_id == member_id
        and sap.status == "active"
    )
    return {
        "completed": {
            "documentation_complete": legal.documentation_complete,
            "sap_setup": sap_is_current,
        },
        "times": {
            "documentation_complete": (
                legal.documentation_completed_at
                if legal.documentation_complete
                else None
            ),
            "sap_setup": sap.completed_at if sap_is_current else None,
        },
        "sap_customer_code_id": sap.customer_code_id if sap_is_current else None,
    }


def _projection(
    application,
    *,
    sanctioned_amount,
    loan_account_id=None,
    status_code="finance_setup_pending",
    stage_truth=None,
):
    labels = {
        "finance_setup_pending": "Finance setup in progress.",
        "disbursement_blocked": "Action required / SFPCL review needed.",
    }
    stage_truth = stage_truth or {"completed": {}, "times": {}}
    prior_complete = True
    timeline = []
    for index, (code, label) in enumerate(_TIMELINE):
        complete = bool(
            index < 2
            and prior_complete
            and stage_truth["completed"].get(code)
        )
        completed_at = stage_truth["times"].get(code) if complete else None
        prior_complete = prior_complete and complete
        timeline.append(
            {
                "code": code,
                "label": label,
                "status": (
                    "complete"
                    if complete
                    else "blocked"
                    if status_code == "disbursement_blocked" and index == 0
                    else "pending"
                ),
                "completed_at": _iso(completed_at) if completed_at else None,
            }
        )
    return {
        "loan_application_id": str(application.pk),
        "loan_account_id": str(loan_account_id) if loan_account_id else None,
        "status_code": status_code,
        "status_label": labels[status_code],
        "sanctioned_amount": f"{sanctioned_amount:.2f}" if sanctioned_amount is not None else None,
        "disbursement_amount": None,
        "destination_account_last4": None,
        "disbursed_at": None,
        "bank_reference_last4": None,
        "advice_available": False,
        "timeline": timeline,
    }


def _progress_projection(
    *,
    application,
    account,
    row,
    sanctioned_amount,
    status_code,
    completed_count,
    blocked_index=None,
    stage_truth=None,
    initiated_at=None,
    authorised_at=None,
):
    labels = {
        "cfc_authorisation_pending": "Payment approval in progress.",
        "payment_processing": "Payment is being processed.",
        "disbursement_blocked": "Action required / SFPCL review needed.",
    }
    stage_times = {
        **((stage_truth or {}).get("times", {})),
        "payment_initiated": initiated_at,
        "cfc_authorisation": authorised_at,
    }
    return {
        "loan_application_id": str(application.pk),
        "loan_account_id": str(account.pk),
        "status_code": status_code,
        "status_label": labels[status_code],
        "sanctioned_amount": f"{sanctioned_amount:.2f}",
        "disbursement_amount": None,
        "destination_account_last4": row.borrower_bank_account.account_number_last4 or None,
        "disbursed_at": None,
        "bank_reference_last4": None,
        "advice_available": False,
        "timeline": [
            {
                "code": code,
                "label": label,
                "status": (
                    "complete"
                    if index < completed_count
                    else "blocked"
                    if index == blocked_index
                    else "pending"
                ),
                "completed_at": (
                    _iso(stage_times.get(code))
                    if index < completed_count and stage_times.get(code)
                    else None
                ),
            }
            for index, (code, label) in enumerate(_TIMELINE)
        ],
    }


__all__ = [
    "PortalAdviceContent",
    "PortalDisbursementNotFound",
    "get_projection",
    "issue_advice_capability",
    "read_advice",
    "record_download_denial",
]
