"""Cross-owner coordinator for schedule and immutable financial ledger reads."""

from math import ceil

from sfpcl_credit.disbursements.modules.post_transfer_evidence import (
    resolve_historical_post_transfer_evidence,
)
from sfpcl_credit.loans.models import LoanAccount
from sfpcl_credit.loans.modules.loan_account_lifecycle import filter_created_accounts
from sfpcl_credit.loans.modules.loan_account_read import (
    LoanAccountReadPermissionDenied,
    scoped_account_candidates,
)
from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
    SapCustomerProfileModule,
)


class LoanServicingReadNotFound(Exception):
    pass


class LoanServicingReadValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


def get_schedule(*, actor, loan_account_id, query_params):
    account, _ = _scoped_account(actor=actor, loan_account_id=loan_account_id)
    page, page_size = _pagination(query_params)
    rows = account.repayment_schedule_lines.order_by(
        "installment_number", "repayment_schedule_id"
    )
    total_count = rows.count()
    pagination = _pagination_result(
        page=page, page_size=page_size, total_count=total_count
    )
    window = rows[(page - 1) * page_size : page * page_size]
    return [_schedule_row(row) for row in window], pagination


def get_ledger(*, actor, loan_account_id, query_params):
    account, transfer = _scoped_account(actor=actor, loan_account_id=loan_account_id)
    page, page_size = _pagination(query_params)
    rows = [_disbursement_ledger_row(transfer)] if transfer is not None else []
    rows.extend(
        _repayment_ledger_row(entry)
        for entry in account.repayment_ledger_entries.select_related(
            "allocation__repayment", "actor_user"
        ).order_by("created_at", "repayment_ledger_entry_id")
    )
    pagination = _pagination_result(
        page=page, page_size=page_size, total_count=len(rows)
    )
    return rows[(page - 1) * page_size : page * page_size], pagination


def _scoped_account(*, actor, loan_account_id):
    candidates = scoped_account_candidates(actor=actor)
    candidates = filter_created_accounts(candidates)
    candidates = SapCustomerProfileModule.filter_current_account_completions(candidates)
    account = candidates.filter(pk=loan_account_id).first()
    if account is None:
        raise LoanServicingReadNotFound
    transfer = resolve_historical_post_transfer_evidence(
        application_id=account.loan_application_id
    )
    if account.loan_account_status == LoanAccount.STATUS_SANCTIONED:
        if transfer is not None:
            raise LoanServicingReadNotFound
    elif transfer is None or transfer.loan_account_id != account.pk:
        raise LoanServicingReadNotFound
    return account, transfer


def _pagination(query_params):
    unknown = set(query_params) - {"page", "page_size"}
    if unknown:
        raise LoanServicingReadValidation(
            {key: "Unknown query parameter." for key in sorted(unknown)}
        )
    return (
        _positive_int("page", query_params.get("page"), 1),
        _positive_int("page_size", query_params.get("page_size"), 20, maximum=100),
    )


def _positive_int(name, raw, default, maximum=None):
    if raw in (None, ""):
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise LoanServicingReadValidation(
            {name: "Must be a positive integer."}
        ) from exc
    if value < 1 or maximum is not None and value > maximum:
        message = (
            f"Must be at most {maximum}."
            if maximum and value > maximum
            else "Must be a positive integer."
        )
        raise LoanServicingReadValidation({name: message})
    return value


def _pagination_result(*, page, page_size, total_count):
    total_pages = ceil(total_count / page_size) if total_count else 1
    if page > total_pages:
        raise LoanServicingReadValidation({"page": "Page is out of range."})
    return {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def _schedule_row(row):
    return {
        "repayment_schedule_id": str(row.pk),
        "installment_number": row.installment_number,
        "due_date": row.due_date.isoformat(),
        "principal_due": _decimal(row.principal_due),
        "interest_due": _decimal(row.interest_due),
        "charges_due": _decimal(row.charges_due),
        "total_due": _decimal(row.total_due),
        "paid_principal": _decimal(row.paid_principal),
        "paid_interest": _decimal(row.paid_interest),
        "paid_charges": _decimal(row.paid_charges),
        "amount_received": _decimal(
            row.paid_principal + row.paid_interest + row.paid_charges
        ),
        "schedule_status": row.schedule_status,
        "extended_due_date": (
            row.extended_due_date.isoformat() if row.extended_due_date else None
        ),
        "created_at": row.created_at.isoformat().replace("+00:00", "Z"),
    }


def _disbursement_ledger_row(transfer):
    amount = _decimal(transfer.amount)
    return {
        "transaction_date": transfer.disbursed_at.date().isoformat(),
        "transaction_type": "disbursement",
        "owner_reference": {
            "entity_type": "disbursement",
            "entity_id": str(transfer.disbursement_id),
        },
        "reference": transfer.bank_reference_number,
        "debit": amount,
        "credit": "0.00",
        "principal_balance": amount,
        "interest_balance": "0.00",
        "total_outstanding": amount,
        "actor": {
            "user_id": str(transfer.transfer_actor_user_id),
            "display_name": transfer.transfer_actor_display_name,
        },
        "sap_status": transfer.sap_posting_status,
        "remarks": "Initial loan disbursement.",
    }


def _repayment_ledger_row(entry):
    repayment = entry.allocation.repayment
    return {
        "transaction_date": entry.transaction_date.isoformat(),
        "transaction_type": "repayment",
        "owner_reference": {
            "entity_type": "repayment_allocation",
            "entity_id": str(entry.allocation_id),
        },
        "reference": repayment.bank_reference_number,
        "debit": "0.00",
        "credit": _decimal(entry.credit_amount),
        "principal_balance": _decimal(entry.principal_balance),
        "interest_balance": _decimal(entry.interest_balance),
        "total_outstanding": _decimal(entry.total_outstanding),
        "actor": {
            "user_id": str(entry.actor_user_id),
            "display_name": entry.actor_display_name,
        },
        "sap_status": repayment.sap_posting_status,
        "remarks": "Repayment allocated principal first.",
    }


def _decimal(value):
    return f"{value:.2f}"


__all__ = [
    "LoanAccountReadPermissionDenied",
    "LoanServicingReadNotFound",
    "LoanServicingReadValidation",
    "get_ledger",
    "get_schedule",
]
