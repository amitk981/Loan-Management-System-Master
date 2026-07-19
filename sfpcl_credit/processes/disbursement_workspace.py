"""Read-only staff projection for SAP, readiness, and disbursement actions."""

from math import ceil

from django.db import transaction

from sfpcl_credit.disbursements.models import Disbursement
from sfpcl_credit.disbursements.modules.disbursement_readiness import (
    DisbursementReadinessModule,
)
from sfpcl_credit.disbursements.modules.disbursement_authorisation import (
    can_authorise_disbursement,
    has_current_authorisation_authority,
)
from sfpcl_credit.disbursements.modules.current_disbursement_evidence import (
    filter_current_pending_disbursements,
    resolve_current_disbursement_evidence,
)
from sfpcl_credit.disbursements.modules.post_transfer_evidence import (
    resolve_post_transfer_evidence,
)
from sfpcl_credit.disbursements.modules.disbursement_transfer_success import (
    can_mark_transfer_success,
)
from sfpcl_credit.disbursements.modules.disbursement_advice import (
    can_send_disbursement_advice,
)
from sfpcl_credit.domain_errors import DomainPermissionDenied
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.models import LoanAccount
from sfpcl_credit.processes.loan_account_360 import (
    eligible_initiation_account_candidates,
    list_initiation_account_window,
)
from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
    assigned_workspace_row_count,
    assigned_workspace_rows,
    get_account_customer_code,
    staff_workspace_row_count,
    staff_workspace_rows,
)


class DisbursementWorkspaceValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


@transaction.atomic
def list_workspace(*, actor, query_params):
    page, page_size = _pagination(query_params)
    roles = set(auth_service.effective_role_codes(actor))
    permissions = set(auth_service.effective_permission_codes(actor))
    can_initiate = (
        "senior_manager_finance" in roles
        and "finance.disbursement.initiate" in permissions
    )
    can_authorise = has_current_authorisation_authority(actor)
    can_create_sap = (
        "credit_manager" in roles
        and "finance.sap_request.create" in permissions
    )
    can_complete_sap = (
        "senior_manager_finance" in roles
        and "finance.sap_request.complete" in permissions
    )
    if not (can_initiate or can_authorise or can_create_sap or can_complete_sap):
        raise DomainPermissionDenied(
            "Active Senior Manager Finance or CFC disbursement authority is required."
        )

    if can_create_sap:
        total_count = staff_workspace_row_count(actor=actor)
        total_pages = ceil(total_count / page_size) if total_count else 1
        if page > total_pages:
            raise DisbursementWorkspaceValidation({"page": "Page is out of range."})
        projections = [
            _project_s36(row)
            for row in staff_workspace_rows(
                actor=actor,
                offset=(page - 1) * page_size,
                limit=page_size,
            )
        ]
        return projections, {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        }
    elif can_initiate:
        filters = {"search": "", "status": "", "member_id": None}
        account_total = eligible_initiation_account_candidates(
            actor=actor, filters=filters
        ).count()
        sap_total = (
            assigned_workspace_row_count(
                actor=actor, without_loan_account=True
            )
            if can_complete_sap
            else 0
        )
        total_count = sap_total + account_total
        total_pages = ceil(total_count / page_size) if total_count else 1
        if page > total_pages:
            raise DisbursementWorkspaceValidation({"page": "Page is out of range."})
        start = (page - 1) * page_size
        sap_offset = min(start, sap_total)
        sap_limit = min(page_size, max(0, sap_total - sap_offset))
        projections = [
            _project_s36(row)
            for row in assigned_workspace_rows(
                actor=actor,
                without_loan_account=True,
                offset=sap_offset,
                limit=sap_limit,
            )
        ]
        account_limit = page_size - len(projections)
        account_offset = max(0, start - sap_total)
        if account_limit and account_offset < account_total:
            account_rows = list_initiation_account_window(
                actor=actor,
                filters=filters,
                offset=account_offset,
                limit=account_limit,
            )
            projections.extend(
                _project_account_rows(
                    actor=actor,
                    account_rows=account_rows,
                    permissions=permissions,
                )
            )
        return projections, {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        }
    elif can_complete_sap:
        total_count = assigned_workspace_row_count(actor=actor)
        total_pages = ceil(total_count / page_size) if total_count else 1
        if page > total_pages:
            raise DisbursementWorkspaceValidation({"page": "Page is out of range."})
        projections = [
            _project_s36(row)
            for row in assigned_workspace_rows(
                actor=actor,
                offset=(page - 1) * page_size,
                limit=page_size,
            )
        ]
        return projections, {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        }
    else:
        candidates = filter_current_pending_disbursements(
            Disbursement.objects.select_related(
                "loan_account__sap_customer_code",
                "loan_application",
                "member",
                "borrower_bank_account",
                "source_bank_account",
                "initiated_by_user",
                "cfc_task",
            )
            .filter(cfc_task__recipient_role_code="chief_financial_controller")
            .filter(authorisation_status="pending")
        ).order_by("-initiated_at", "-disbursement_id")
        total_count = candidates.count()
        total_pages = ceil(total_count / page_size) if total_count else 1
        if page > total_pages:
            raise DisbursementWorkspaceValidation({"page": "Page is out of range."})
        start = (page - 1) * page_size
        projections = [
            _project_disbursement(actor=actor, row=row, permissions=permissions)
            for row in candidates[start : start + page_size]
        ]
        return projections, {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        }

def _project_account(
    *, actor, account_row, permissions, account=None, disbursement=None
):
    if account is None:
        return None
    if disbursement is not None:
        if not _disbursement_is_current(disbursement):
            return None
        return _project_disbursement(
            actor=actor, row=disbursement, permissions=permissions
        )

    readiness = DisbursementReadinessModule.evaluate(
        actor=actor, loan_account_id=account.pk
    )
    decision = DisbursementReadinessModule.evaluate_for_initiation(
        actor=actor, loan_account_id=account.pk
    )
    sap_request = _sap_request(account)
    actions = []
    if "finance.disbursement.initiate" in permissions:
        actions.append(
            _action(
                "initiate_disbursement",
                "Initiate payment",
                f"/api/v1/loan-accounts/{account.pk}/disbursements/initiate/",
                "finance.disbursement.initiate",
                readiness["ready_for_disbursement"],
                None
                if readiness["ready_for_disbursement"]
                else "Every current readiness check must pass.",
                [
                    _field(
                        "disbursement_amount",
                        "Disbursement amount",
                        "money",
                        value=f"{account.sanctioned_amount:.2f}",
                    ),
                    _field(
                        "final_verification_comments",
                        "Final verification comments",
                        "textarea",
                    ),
                ],
                fixed_payload={
                    "borrower_bank_account_id": _string(
                        decision.borrower_bank_account_id
                    ),
                    "source_bank_account_id": _string(
                        decision.source_bank_account_id
                    ),
                },
            )
        )
    return _base_projection(
        workspace_id=account.pk,
        account=account,
        disbursement=None,
        readiness=readiness,
        sap_request=sap_request,
        beneficiary=_bank_account(decision.borrower_bank_account_id),
        source=_bank_account(decision.source_bank_account_id),
        actions=actions,
    )


def _project_account_rows(*, actor, account_rows, permissions):
    account_ids = [row["loan_account_id"] for row in account_rows]
    accounts = {
        str(row.pk): row
        for row in LoanAccount.objects.select_related(
            "loan_application", "member", "sap_customer_code"
        ).filter(pk__in=account_ids)
    }
    disbursements = {}
    for row in (
        Disbursement.objects.select_related(
            "loan_account__loan_application",
            "loan_account__member",
            "loan_account__sap_customer_code",
            "borrower_bank_account",
            "source_bank_account",
            "initiated_by_user",
        )
        .filter(loan_account_id__in=account_ids)
        .order_by("loan_account_id", "-initiated_at", "-disbursement_id")
    ):
        disbursements.setdefault(str(row.loan_account_id), row)
    return [
        projection
        for row in account_rows
        if (
            projection := _project_account(
                actor=actor,
                account_row=row,
                permissions=permissions,
                account=accounts.get(row["loan_account_id"]),
                disbursement=disbursements.get(row["loan_account_id"]),
            )
        )
        is not None
    ]


def _project_s36(row):
    return {
        "workspace_id": row["workspace_id"],
        "loan_account_id": None,
        "disbursement_id": None,
        "loan_application_id": row["loan_application_id"],
        "application_reference_number": row["application_reference_number"],
        "loan_account_number": None,
        "member": row["member"],
        "sanctioned_amount": row["sanctioned_amount"],
        "disbursement_amount": row["sanctioned_amount"],
        "sap": {
            "request_id": row["request_id"],
            "status": row["request_status"],
            "customer_code_masked": row.get("customer_code_masked"),
        },
        "readiness": {
            "ready_for_disbursement": False,
            "evaluated_at": None,
            "checks": [],
        },
        "beneficiary_bank": None,
        "source_bank": None,
        "initiation_status": None,
        "authorisation_status": None,
        "bank_transfer_status": None,
        "advice_status": "not_started",
        "bank_reference_masked": None,
        "initiated_by": None,
        "initiated_at": None,
        "authorised_at": None,
        "disbursed_at": None,
        "available_actions": row["available_actions"],
    }


def _project_disbursement(*, actor, row, permissions):
    try:
        readiness = DisbursementReadinessModule.evaluate(
            actor=actor, loan_account_id=row.loan_account_id
        )
    except DomainPermissionDenied:
        # The accepted initiation is retained proof that the canonical gate
        # passed at initiation time. The authorisation owner revalidates the
        # current evidence; this read projection never substitutes for it.
        readiness = {
            "loan_account_id": str(row.loan_account_id),
            "loan_application_id": str(row.loan_application_id),
            "ready_for_disbursement": True,
            "evaluated_at": _timestamp(row.initiated_at),
            "checks": [],
        }
    actions = []
    if can_authorise_disbursement(actor=actor, row=row):
        fields = [_field("comments", "CFC comments", "textarea")]
        actions.extend(
            [
                _action(
                    "authorise_disbursement", "Authorise payment",
                    f"/api/v1/disbursements/{row.pk}/authorise/",
                    "finance.disbursement.authorise", True, None, fields,
                ),
                _action(
                    "reject_disbursement", "Reject payment",
                    f"/api/v1/disbursements/{row.pk}/authorise/",
                    "finance.disbursement.authorise", True, None, fields,
                ),
            ]
        )
    if can_mark_transfer_success(actor=actor, row=row):
        actions.append(
            _action(
                "mark_transfer_successful", "Record transfer success",
                f"/api/v1/disbursements/{row.pk}/mark-transfer-successful/",
                "finance.disbursement.mark_success", True, None,
                [
                    _field("bank_reference_number", "UTR / bank reference", "text"),
                    _field("disbursed_at", "Transfer date and time", "datetime-local"),
                    _field("bank_transfer_evidence_document_id", "Bank evidence document ID", "text"),
                ],
            )
        )
    if can_send_disbursement_advice(actor=actor, row=row):
        actions.append(
            _action(
                "send_disbursement_advice", "Send disbursement advice",
                f"/api/v1/disbursements/{row.pk}/send-advice/",
                "finance.disbursement.send_advice", True, None,
                [_field("recipient_email", "Borrower email", "email")],
                fixed_payload={"channel": "email"},
            )
        )
    return _base_projection(
        workspace_id=row.pk,
        account=row.loan_account,
        disbursement=row,
        readiness=readiness,
        sap_request=_sap_request(row.loan_account),
        beneficiary=row.borrower_bank_account,
        source=row.source_bank_account,
        actions=actions,
    )


def _base_projection(*, workspace_id, account, disbursement, readiness, sap_request, beneficiary, source, actions):
    amount = disbursement.disbursement_amount if disbursement else account.sanctioned_amount
    return {
        "workspace_id": str(workspace_id),
        "loan_account_id": str(account.pk),
        "disbursement_id": _string(disbursement.pk) if disbursement else None,
        "loan_application_id": str(account.loan_application_id),
        "application_reference_number": account.loan_application.application_reference_number,
        "loan_account_number": account.loan_account_number,
        "member": {"member_id": str(account.member_id), "display_name": account.member.display_name},
        "sanctioned_amount": f"{account.sanctioned_amount:.2f}",
        "disbursement_amount": f"{amount:.2f}",
        "sap": {
            "request_id": _string(sap_request.profile_request_id) if sap_request else None,
            "status": "completed" if sap_request else "not_started",
            "customer_code_masked": sap_request.customer_code_masked if sap_request else None,
        },
        "readiness": readiness,
        "beneficiary_bank": _bank(beneficiary, include_ifsc=True),
        "source_bank": _bank(source, include_ifsc=False),
        "initiation_status": disbursement.initiation_status if disbursement else None,
        "authorisation_status": disbursement.authorisation_status if disbursement else None,
        "bank_transfer_status": disbursement.bank_transfer_status if disbursement else None,
        "advice_status": "sent" if disbursement and disbursement.disbursement_advice_communication_id else "not_started",
        "bank_reference_masked": _mask_reference(disbursement.bank_reference_number) if disbursement else None,
        "initiated_by": ({"user_id": str(disbursement.initiated_by_user_id), "full_name": disbursement.initiated_by_user.full_name} if disbursement else None),
        "initiated_at": _timestamp(disbursement.initiated_at) if disbursement else None,
        "authorised_at": _timestamp(disbursement.authorised_at) if disbursement else None,
        "disbursed_at": _timestamp(disbursement.disbursed_at) if disbursement else None,
        "available_actions": actions,
    }


def _sap_request(account):
    return get_account_customer_code(
        application_id=account.loan_application_id,
        member_id=account.member_id,
        customer_code_id=account.sap_customer_code_id,
    )


def _action(code, label, url, permission, enabled, reason, fields, fixed_payload=None):
    return {"action_code": code, "label": label, "enabled": enabled, "disabled_reason": reason, "required_permission": permission, "action_url": url, "method": "POST", "fields": fields, "fixed_payload": fixed_payload or {}}


def _field(name, label, field_type, *, value=None, required=True):
    return {"name": name, "label": label, "type": field_type, "required": required, "value": value}


def _bank_account(bank_account_id):
    if bank_account_id is None:
        return None
    from sfpcl_credit.members.models import BankAccount
    return BankAccount.objects.filter(pk=bank_account_id).first()


def _bank(bank, *, include_ifsc):
    if bank is None:
        return None
    result = {"account_holder_name": bank.account_holder_name, "account_number_masked": f"******{bank.account_number_last4}", "bank_name": bank.bank_name}
    if include_ifsc:
        result.update({"ifsc_code": bank.ifsc, "branch_name": bank.branch_name})
    return result


def _disbursement_is_current(row):
    if row.bank_transfer_status == "successful":
        evidence = resolve_post_transfer_evidence(
            application_id=row.loan_application_id
        )
        return bool(evidence and evidence.disbursement_id == row.pk)
    evidence = resolve_current_disbursement_evidence(
        disbursement_id=row.pk,
        allowed_authorisation_statuses=(row.authorisation_status,),
    )
    return bool(evidence and evidence.disbursement_id == row.pk)


def _is_cfc(actor, roles):
    return "chief_financial_controller" in roles


def _pagination(query_params):
    unknown = set(query_params) - {"page", "page_size"}
    if unknown:
        raise DisbursementWorkspaceValidation({key: "Unknown query parameter." for key in sorted(unknown)})
    return _positive_int("page", query_params.get("page"), 1), _positive_int("page_size", query_params.get("page_size"), 20, maximum=100)


def _positive_int(name, raw, default, maximum=None):
    if raw in (None, ""):
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise DisbursementWorkspaceValidation({name: "Must be a positive integer."}) from exc
    if value < 1 or maximum is not None and value > maximum:
        raise DisbursementWorkspaceValidation({name: f"Must be at most {maximum}." if maximum and value > maximum else "Must be a positive integer."})
    return value


def _timestamp(value):
    return value.isoformat().replace("+00:00", "Z") if value else None


def _string(value):
    return str(value) if value is not None else None


def _mask_reference(value):
    return f"******{value[-4:]}" if value else None


__all__ = ["DisbursementWorkspaceValidation", "list_workspace"]
