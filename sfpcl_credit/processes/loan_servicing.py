"""Cross-owner coordinator for schedule and immutable financial ledger reads."""

from math import ceil

from django.core.exceptions import ObjectDoesNotExist

from sfpcl_credit.disbursements.modules.post_transfer_evidence import (
    resolve_historical_post_transfer_evidence,
)
from sfpcl_credit.loans.models import LoanAccount
from sfpcl_credit.interest.models import InterestCapitalisationLedgerEntry
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
    return get_ledger_for_scoped_account(
        account=account, transfer=transfer, query_params=query_params
    )


def get_repayments(*, actor, loan_account_id, query_params):
    account, _ = _scoped_account(actor=actor, loan_account_id=loan_account_id)
    page, page_size = _pagination(query_params)
    rows = account.repayments.select_related(
        "allocation",
        "matched_bank_statement_line",
        "sap_posting_obligation",
        "subsidiary_deduction_evidence",
    ).order_by("received_date", "created_at", "repayment_id")
    total_count = rows.count()
    pagination = _pagination_result(
        page=page, page_size=page_size, total_count=total_count
    )
    window = rows[(page - 1) * page_size : page * page_size]
    return [_repayment_row(row) for row in window], pagination


def get_ledger_for_scoped_account(*, account, transfer, query_params):
    """Project canonical rows after a caller has proved its own account scope."""
    page, page_size = _pagination(query_params)
    repayment_rows = account.repayment_ledger_entries.select_related(
        "allocation__repayment", "actor_user"
    ).order_by("created_at", "repayment_ledger_entry_id")
    reversal_rows = account.repayment_reversal_ledger_entries.select_related(
        "reversal__repayment", "actor_user"
    ).order_by("created_at", "repayment_reversal_ledger_entry_id")
    capitalisation_rows = account.interest_capitalisation_ledger_entries.select_related(
        "capitalisation", "actor_user"
    ).order_by("created_at", "interest_capitalisation_ledger_entry_id")
    total_count = (
        (1 if transfer is not None else 0)
        + repayment_rows.count()
        + reversal_rows.count()
        + capitalisation_rows.count()
    )
    pagination = _pagination_result(
        page=page, page_size=page_size, total_count=total_count
    )
    start = (page - 1) * page_size
    end = page * page_size
    opening_count = 1 if transfer is not None else 0
    movement_start = max(0, start - opening_count)
    movement_end = max(0, end - opening_count)
    movement_rows = [
        *(
            _repayment_ledger_row(entry)
            for entry in repayment_rows[:movement_end]
        ),
        *(
            _reversal_ledger_row(entry)
            for entry in reversal_rows[:movement_end]
        ),
        *(
            _capitalisation_ledger_row(entry)
            for entry in capitalisation_rows[:movement_end]
        ),
    ]
    movement_rows.sort(key=lambda row: row.pop("_sort_key"))
    rows = []
    if transfer is not None and start == 0:
        rows.append(_disbursement_ledger_row(transfer))
    rows.extend(movement_rows[movement_start:movement_end])
    return rows, pagination


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


def _repayment_row(repayment):
    try:
        allocation = repayment.allocation
    except ObjectDoesNotExist:
        allocation = None
    try:
        subsidiary = repayment.subsidiary_deduction_evidence
    except ObjectDoesNotExist:
        subsidiary = None
    obligation = repayment.sap_posting_obligation
    return {
        "repayment_id": str(repayment.pk),
        "loan_account_id": str(repayment.loan_account_id),
        "repayment_source": repayment.repayment_source,
        "amount_received": _decimal(repayment.amount_received),
        "received_date": repayment.received_date.isoformat(),
        "payment_method": repayment.payment_method,
        "bank_reference_number": repayment.bank_reference_number,
        "bank_statement_line_id": (
            str(repayment.bank_statement_line_id)
            if repayment.bank_statement_line_id
            else None
        ),
        "statement_match_status": repayment.statement_match_status,
        "allocation_status": repayment.allocation_status,
        "sap_posting_status": repayment.sap_posting_status,
        "sap_posting_due_date": obligation.due_date.isoformat(),
        "sap_entry_reference": obligation.sap_entry_reference,
        "sap_posted_at": (
            obligation.posted_at.isoformat().replace("+00:00", "Z")
            if obligation.posted_at
            else None
        ),
        "allocation": (
            {
                "allocated_to_principal": _decimal(allocation.allocated_to_principal),
                "allocated_to_interest": _decimal(allocation.allocated_to_interest),
                "allocated_to_charges": _decimal(allocation.allocated_to_charges),
                "unallocated_amount": _decimal(allocation.unallocated_amount),
                "exception_reason": allocation.exception_reason,
            }
            if allocation
            else None
        ),
        "subsidiary_reconciliation": (
            {
                "subsidiary_company_id": str(subsidiary.subsidiary_company_id),
                "produce_payment_reference": subsidiary.produce_payment_reference,
                "transfer_reference": subsidiary.transfer_reference,
                "tri_party_agreement_id": str(subsidiary.tri_party_agreement_id),
                "reconciliation_status": subsidiary.reconciliation_status,
                "treasury_verification_status": subsidiary.treasury_verification_status,
            }
            if subsidiary
            else None
        ),
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
        "_sort_key": (entry.created_at, "repayment", str(entry.pk)),
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


def _reversal_ledger_row(entry):
    repayment = entry.reversal.repayment
    return {
        "_sort_key": (entry.created_at, "reversal", str(entry.pk)),
        "transaction_date": entry.transaction_date.isoformat(),
        "transaction_type": "reversal",
        "owner_reference": {
            "entity_type": "repayment_reversal",
            "entity_id": str(entry.reversal_id),
        },
        "reference": repayment.bank_reference_number,
        "debit": _decimal(entry.debit_amount),
        "credit": "0.00",
        "principal_balance": _decimal(entry.principal_balance),
        "interest_balance": _decimal(entry.interest_balance),
        "total_outstanding": _decimal(entry.total_outstanding),
        "actor": {
            "user_id": str(entry.actor_user_id),
            "display_name": entry.actor_display_name,
        },
        "sap_status": repayment.sap_posting_status,
        "remarks": "Repayment reversed by compensating entry.",
    }


def _capitalisation_ledger_row(entry: InterestCapitalisationLedgerEntry):
    return {
        "_sort_key": (entry.created_at, "interest_capitalisation", str(entry.pk)),
        "transaction_date": entry.transaction_date.isoformat(),
        "transaction_type": "interest_capitalisation",
        "owner_reference": {
            "entity_type": "interest_capitalisation",
            "entity_id": str(entry.capitalisation_id),
        },
        "reference": entry.capitalisation.financial_year,
        "debit": _decimal(entry.debit_amount),
        "credit": "0.00",
        "principal_balance": _decimal(entry.principal_balance),
        "interest_balance": _decimal(entry.interest_balance),
        "total_outstanding": _decimal(entry.total_outstanding),
        "actor": {
            "user_id": str(entry.actor_user_id),
            "display_name": entry.actor_display_name,
        },
        "sap_status": "not_applicable",
        "remarks": "Unpaid interest capitalised after 30 April.",
    }


def _decimal(value):
    return f"{value:.2f}"


__all__ = [
    "LoanAccountReadPermissionDenied",
    "LoanServicingReadNotFound",
    "LoanServicingReadValidation",
    "get_ledger",
    "get_ledger_for_scoped_account",
    "get_repayments",
    "get_schedule",
]
