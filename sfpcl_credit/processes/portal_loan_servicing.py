"""Borrower-safe, authenticated-member loan-servicing projections."""

from django.conf import settings
from django.core.paginator import EmptyPage, Paginator

from sfpcl_credit.interest.models import InterestInvoice
from sfpcl_credit.loans.models import LoanAccount, RepaymentAllocation, RepaymentSchedule


class PortalLoanNotFound(Exception):
    pass


class PortalLoanQueryInvalid(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors
        super().__init__("Portal loan query failed validation.")


def list_accounts(*, member, query_params):
    page, page_size = _pagination(query_params)
    rows = LoanAccount.objects.filter(member=member).order_by("-created_at", "loan_account_id")
    return _page(rows, page, page_size, _account_summary)


def account_detail(*, member, loan_account_id):
    account = _account(member=member, loan_account_id=loan_account_id)
    summary = _account_summary(account)
    summary.update(
        {
            "interest_outstanding": _money(account.interest_outstanding),
            "charges_outstanding": _money(account.charges_outstanding),
            "total_outstanding": _money(account.total_outstanding),
            "repayment_route": _repayment_route(account),
            "closed_at": _datetime(account.closed_at),
        }
    )
    return summary


def schedule(*, member, loan_account_id, query_params):
    account = _account(member=member, loan_account_id=loan_account_id)
    page, page_size = _pagination(query_params)
    rows = RepaymentSchedule.objects.filter(loan_account=account).order_by(
        "installment_number", "repayment_schedule_id"
    )
    return _page(rows, page, page_size, _schedule_row)


def repayment_history(*, member, loan_account_id, query_params):
    account = _account(member=member, loan_account_id=loan_account_id)
    page, page_size = _pagination(query_params)
    rows = (
        RepaymentAllocation.objects.select_related("repayment")
        .filter(
            loan_account=account,
            repayment__member=member,
            repayment__sap_posting_status="posted",
            repayment__allocation_status__in=("allocated", "allocated_with_exception"),
        )
        .order_by("-allocated_at", "-repayment_allocation_id")
    )
    return _page(rows, page, page_size, _repayment_row)


def invoices(*, member, loan_account_id, query_params):
    account = _account(member=member, loan_account_id=loan_account_id)
    page, page_size = _pagination(query_params)
    rows = InterestInvoice.objects.filter(
        loan_account=account,
        member=member,
        invoice_status=InterestInvoice.STATUS_ISSUED,
    ).order_by("-invoice_date", "-interest_invoice_id")
    return _page(rows, page, page_size, _invoice_row)


def direct_instructions(*, member, loan_account_id):
    account = _account(member=member, loan_account_id=loan_account_id)
    configured = getattr(settings, "PORTAL_REPAYMENT_INSTRUCTIONS", {})
    required = ("beneficiary_name", "bank_name", "account_number_last4", "ifsc")
    available = bool(configured.get("approved") is True and all(configured.get(key) for key in required))
    base = {
        "available": available,
        "beneficiary_name": None,
        "bank_name": None,
        "account_number_masked": None,
        "ifsc": None,
        "required_narration": account.loan_account_number,
        "amount_due": _money(account.total_outstanding),
        "proof_submission_enabled": False,
        "disclaimer": (
            "Repayment will be updated in the portal after SFPCL verifies the bank receipt "
            "and posts the repayment in its records."
        ),
    }
    if available:
        last4 = str(configured["account_number_last4"])[-4:]
        base.update(
            beneficiary_name=str(configured["beneficiary_name"]),
            bank_name=str(configured["bank_name"]),
            account_number_masked=f"********{last4}",
            ifsc=str(configured["ifsc"]),
        )
    return base


def _account(*, member, loan_account_id):
    account = LoanAccount.objects.filter(pk=loan_account_id, member=member).first()
    if account is None:
        raise PortalLoanNotFound
    return account


def _account_summary(account):
    next_due = account.repayment_schedule_lines.filter(schedule_status__in=("pending", "overdue")).order_by(
        "due_date", "installment_number"
    ).first()
    return {
        "loan_account_id": str(account.pk),
        "loan_account_number": account.loan_account_number,
        "application_id": str(account.loan_application_id),
        "application_reference": account.loan_application.application_reference_number,
        "status": account.loan_account_status,
        "closure_status": "closed" if account.closed_at else "active",
        "disbursed_amount": _money(account.disbursed_amount),
        "principal_outstanding": _money(account.principal_outstanding),
        "next_due_date": next_due.due_date.isoformat() if next_due else None,
        "next_due_amount": _money(next_due.total_due) if next_due else None,
    }


def _schedule_row(row):
    paid = row.paid_principal + row.paid_interest + row.paid_charges
    status = "partly_paid" if paid and paid < row.total_due else row.schedule_status
    return {
        "schedule_id": str(row.pk),
        "installment_number": row.installment_number,
        "due_date": row.due_date.isoformat(),
        "principal_due": _money(row.principal_due),
        "interest_due": _money(row.interest_due),
        "charges_due": _money(row.charges_due),
        "total_due": _money(row.total_due),
        "paid_principal": _money(row.paid_principal),
        "paid_interest": _money(row.paid_interest),
        "paid_amount": _money(paid),
        "status": status,
    }


def _repayment_row(allocation):
    repayment = allocation.repayment
    return {
        "repayment_id": str(repayment.pk),
        "receipt_date": repayment.received_date.isoformat(),
        "amount_received": _money(repayment.amount_received),
        "allocated_to_principal": _money(allocation.allocated_to_principal),
        "allocated_to_interest": _money(allocation.allocated_to_interest),
        "payment_mode": repayment.payment_method,
        "repayment_source": repayment.repayment_source,
        "reference": repayment.bank_reference_number,
        "acknowledgement": None,
        "status": "confirmed",
    }


def _invoice_row(row):
    return {
        "invoice_id": str(row.pk),
        "invoice_number": row.invoice_number,
        "invoice_date": row.invoice_date.isoformat(),
        "financial_year": row.financial_year,
        "interest_amount": _money(row.interest_amount),
        "status": "issued",
    }


def _repayment_route(account):
    sources = set(account.repayments.values_list("repayment_source", flat=True))
    if sources == {"direct_farmer", "subsidiary_deduction"}:
        return "both"
    if "subsidiary_deduction" in sources:
        return "subsidiary_deduction"
    return "direct"


def _pagination(query_params):
    unknown = set(query_params) - {"page", "page_size"}
    if unknown:
        raise PortalLoanQueryInvalid({field: "Unknown query parameter." for field in sorted(unknown)})
    errors = {}
    values = {}
    for field, default, maximum in (("page", 1, None), ("page_size", 20, 100)):
        raw = query_params.get(field)
        try:
            value = default if raw in (None, "") else int(raw)
        except (TypeError, ValueError):
            value = 0
        if value < 1 or (maximum and value > maximum):
            errors[field] = f"Must be between 1 and {maximum}." if maximum else "Must be a positive integer."
        values[field] = value
    if errors:
        raise PortalLoanQueryInvalid(errors)
    return values["page"], values["page_size"]


def _page(rows, page, page_size, serializer):
    paginator = Paginator(rows, page_size)
    try:
        selected = paginator.page(page)
    except EmptyPage:
        selected = []
    return [serializer(row) for row in selected], {
        "page": page,
        "page_size": page_size,
        "total_count": paginator.count,
        "total_pages": paginator.num_pages,
    }


def _money(value):
    return f"{value:.2f}"


def _datetime(value):
    return value.isoformat().replace("+00:00", "Z") if value else None
