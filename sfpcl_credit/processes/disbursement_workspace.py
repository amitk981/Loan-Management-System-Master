"""Read-only staff projection for SAP, readiness, and disbursement actions."""

from math import ceil

from django.db import transaction

from sfpcl_credit.disbursements.models import Disbursement
from sfpcl_credit.disbursements.modules.disbursement_readiness import (
    DisbursementReadinessModule,
)
from sfpcl_credit.disbursements.modules.current_disbursement_evidence import (
    resolve_current_disbursement_evidence,
)
from sfpcl_credit.disbursements.modules.post_transfer_evidence import (
    resolve_post_transfer_evidence,
)
from sfpcl_credit.domain_errors import DomainPermissionDenied
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.models import LoanAccount
from sfpcl_credit.processes.loan_account_360 import list_accounts
from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest


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
    can_authorise = (
        _is_cfc(actor, roles)
        and "finance.disbursement.authorise" in permissions
    )
    if not (can_initiate or can_authorise):
        raise DomainPermissionDenied(
            "Active Senior Manager Finance or CFC disbursement authority is required."
        )

    if can_initiate:
        account_rows, account_pagination = list_accounts(
            actor=actor, query_params={"page": "1", "page_size": "100"}
        )
        for account_page in range(2, account_pagination["total_pages"] + 1):
            page_rows, _ = list_accounts(
                actor=actor,
                query_params={"page": str(account_page), "page_size": "100"},
            )
            account_rows.extend(page_rows)
        account_projections = [
            _project_account(actor=actor, account_row=row, permissions=permissions)
            for row in account_rows
        ]
        represented_applications = {
            row["loan_application_id"] for row in account_projections
        }
        sap_requests = (
            SapCustomerProfileRequest.objects.select_related(
                "loan_application", "member", "sap_customer_code"
            )
            .filter(assigned_to_user=actor)
            .order_by("-created_at", "-sap_customer_profile_request_id")
        )
        projections = [
            _project_sap_request(row)
            for row in sap_requests
            if str(row.loan_application_id) not in represented_applications
        ] + account_projections
    else:
        candidates = (
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
            .order_by("-initiated_at", "-disbursement_id")
        )
        projections = [
            _project_disbursement(actor=actor, row=row, permissions=permissions)
            for row in candidates
            if _disbursement_is_current(row)
        ]

    total_count = len(projections)
    total_pages = ceil(total_count / page_size) if total_count else 1
    if page > total_pages:
        raise DisbursementWorkspaceValidation({"page": "Page is out of range."})
    start = (page - 1) * page_size
    return projections[start : start + page_size], {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def _project_account(*, actor, account_row, permissions):
    account = (
        LoanAccount.objects.select_related(
            "loan_application", "member", "sap_customer_code"
        )
        .filter(pk=account_row["loan_account_id"])
        .first()
    )
    disbursement = (
        Disbursement.objects.select_related(
            "borrower_bank_account", "source_bank_account", "initiated_by_user"
        )
        .filter(loan_account_id=account.pk)
        .order_by("-initiated_at", "-disbursement_id")
        .first()
    )
    if disbursement is not None:
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


def _project_sap_request(row):
    actions = []
    if row.request_status == SapCustomerProfileRequest.STATUS_SENT:
        actions.append(
            _action(
                "complete_sap_request", "Confirm SAP customer code",
                f"/api/v1/sap-customer-profile-requests/{row.pk}/complete/",
                "finance.sap_customer_code.complete", True, None,
                [
                    _field("sap_customer_code", "SAP customer code", "text"),
                    _field("sap_vendor_code", "SAP vendor code", "text", required=False),
                    _field("created_at_sap", "SAP creation date and time", "datetime-local"),
                    _field("confirmation_document_id", "Confirmation document ID", "text", required=False),
                    _field("confirmation_notes", "Finance comments", "textarea"),
                ],
            )
        )
    return {
        "workspace_id": str(row.pk),
        "loan_account_id": None,
        "disbursement_id": None,
        "loan_application_id": str(row.loan_application_id),
        "application_reference_number": row.loan_application.application_reference_number,
        "loan_account_number": None,
        "member": {"member_id": str(row.member_id), "display_name": row.member.display_name},
        "sanctioned_amount": f"{row.sanctioned_amount:.2f}",
        "disbursement_amount": f"{row.sanctioned_amount:.2f}",
        "sap": {"request_id": str(row.pk), "status": row.request_status, "customer_code_masked": _mask_code(row.sap_customer_code.sap_customer_code) if row.sap_customer_code_id else None},
        "readiness": {"ready_for_disbursement": False, "evaluated_at": None, "checks": [{"code": "sap_customer_code_present", "label": "SAP customer code present", "status": "fail", "reason": "SAP setup must be completed before the loan account and readiness review are available."}]},
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
        "available_actions": actions,
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
    if row.authorisation_status == "pending" and _is_cfc(
        actor, set(auth_service.effective_role_codes(actor))
    ) and "finance.disbursement.authorise" in permissions:
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
    if row.authorisation_status == "approved" and row.bank_transfer_status == "pending" and "finance.disbursement.mark_success" in permissions:
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
    if row.bank_transfer_status == "successful" and row.disbursement_advice_communication_id is None and "finance.disbursement.send_advice" in permissions:
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
            "request_id": _string(sap_request.pk) if sap_request else None,
            "status": sap_request.request_status if sap_request else "not_started",
            "customer_code_masked": _mask_code(account.sap_customer_code.sap_customer_code) if account.sap_customer_code_id else None,
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
    return SapCustomerProfileRequest.objects.filter(
        loan_application_id=account.loan_application_id,
        member_id=account.member_id,
        sap_customer_code_id=account.sap_customer_code_id,
    ).order_by("-created_at", "-sap_customer_profile_request_id").first()


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
    return "chief_financial_controller" in roles or getattr(actor, "approval_authority_type", None) == "chief_financial_controller"


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


def _mask_code(value):
    return f"******{value[-4:]}" if value else None


def _mask_reference(value):
    return f"******{value[-4:]}" if value else None


__all__ = ["DisbursementWorkspaceValidation", "list_workspace"]
