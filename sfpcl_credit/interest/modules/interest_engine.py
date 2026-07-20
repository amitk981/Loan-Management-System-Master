import hashlib
import json
import re
import uuid
from io import BytesIO
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.db import IntegrityError, transaction
from django.db.models import Q, Sum
from django.core.files.base import ContentFile
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.configurations.models import InterestRateConfig
from sfpcl_credit.configurations.modules.interest_rate_configuration import consume_effective_rate
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.interest.models import InterestInvoice, InterestInvoiceConfiguration
from sfpcl_credit.loans.models import LoanAccount, RepaymentAllocation
from sfpcl_credit.loans.modules.loan_account_read import (
    LoanAccountReadPermissionDenied,
    scoped_account_candidates,
)


CREATE_PERMISSION = "finance.interest_invoice.create"
ISSUE_PERMISSION = "finance.interest_invoice.issue"
SERVICEABLE_STATUSES = {"active", "partially_repaid", "overdue", "grace_period", "extended"}
_FY_PATTERN = re.compile(r"^FY(\d{4})-(\d{2})$")
_MONEY = Decimal("0.01")


class InterestInvoiceValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class InterestInvoicePermissionDenied(Exception):
    pass


class InterestInvoiceNotFound(Exception):
    pass


class InterestInvoiceConflict(Exception):
    pass


def generate_invoice(*, actor, loan_account_id, payload, idempotency_key, request=None):
    financial_year, period_start, period_end = _validate_generation(payload, idempotency_key)
    key_digest = _digest_text(idempotency_key.strip())
    payload_digest = _digest({
        "actor_id": str(actor.pk),
        "loan_account_id": str(loan_account_id),
        "financial_year": financial_year,
    })
    try:
        return _generate(
            actor=actor,
            loan_account_id=loan_account_id,
            financial_year=financial_year,
            period_start=period_start,
            period_end=period_end,
            key_digest=key_digest,
            payload_digest=payload_digest,
            request=request,
        )
    except IntegrityError as exc:
        retained = InterestInvoice.objects.filter(
            generation_idempotency_key_digest=key_digest
        ).first()
        if retained is not None and retained.generation_payload_digest == payload_digest:
            return _replay(retained)
        raise InterestInvoiceConflict(
            "An invoice already exists for this request or loan period."
        ) from exc


def list_invoices(*, actor, loan_account_id=None, query_params):
    allowed = {"financial_year", "invoice_status", "page", "page_size"}
    errors = {field: "Unknown query parameter." for field in sorted(set(query_params) - allowed)}
    financial_year = query_params.get("financial_year")
    if financial_year is not None and _FY_PATTERN.fullmatch(financial_year) is None:
        errors["financial_year"] = "Use the format FY2026-27."
    status = query_params.get("invoice_status")
    if status is not None and status not in InterestInvoice.STATUSES:
        errors["invoice_status"] = "Must be draft or issued."
    page = _positive_int(query_params.get("page"), 1, "page", errors)
    page_size = min(_positive_int(query_params.get("page_size"), 20, "page_size", errors), 100)
    if errors:
        raise InterestInvoiceValidation(errors)
    scoped_accounts = _scoped_accounts(actor)
    if loan_account_id is not None:
        account = scoped_accounts.filter(pk=loan_account_id).first()
        if account is None:
            raise InterestInvoiceNotFound
        rows = InterestInvoice.objects.filter(loan_account=account)
    else:
        rows = InterestInvoice.objects.filter(loan_account__in=scoped_accounts)
    if financial_year:
        rows = rows.filter(financial_year=financial_year)
    if status:
        rows = rows.filter(invoice_status=status)
    total_count = rows.count()
    total_pages = max(1, (total_count + page_size - 1) // page_size)
    page = min(page, total_pages)
    start = (page - 1) * page_size
    return [serialize_invoice(row) for row in rows[start:start + page_size]], {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def issue_invoice(*, actor, interest_invoice_id, payload, idempotency_key, request=None):
    cleaned = _validate_issuance(payload, idempotency_key)
    key_digest = _digest_text(idempotency_key.strip())
    payload_digest = _digest({
        "actor_id": str(actor.pk),
        "interest_invoice_id": str(interest_invoice_id),
        **cleaned,
    })
    return _issue(
        actor=actor,
        interest_invoice_id=interest_invoice_id,
        cleaned=cleaned,
        key_digest=key_digest,
        payload_digest=payload_digest,
        request=request,
    )


@transaction.atomic
def _issue(*, actor, interest_invoice_id, cleaned, key_digest, payload_digest, request):
    from sfpcl_credit.communications.modules.communication_dispatcher import (
        CommunicationDispatchConflict,
        CommunicationDispatcher,
    )
    from sfpcl_credit.documents.services import DocumentAuditSpec, store_document_upload

    _require_permission(actor, ISSUE_PERMISSION)
    invoice = (
        InterestInvoice.objects.select_for_update()
        .select_related("loan_account", "member", "calculation_configuration")
        .filter(pk=interest_invoice_id)
        .first()
    )
    if invoice is None or not _scoped_accounts(actor).filter(
        pk=invoice.loan_account_id
    ).exists():
        raise InterestInvoiceNotFound
    _require_configured_owner(actor, invoice.calculation_configuration)
    if invoice.invoice_status == InterestInvoice.STATUS_ISSUED:
        if (
            invoice.issuance_idempotency_key_digest == key_digest
            and invoice.issuance_payload_digest == payload_digest
        ):
            return {"idempotency_replayed": True, "original_response": serialize_invoice(invoice)}
        raise InterestInvoiceConflict("The invoice has already been issued.")
    if invoice.invoice_status != InterestInvoice.STATUS_DRAFT:
        raise InterestInvoiceConflict("Only a valid draft invoice can be issued.")
    if cleaned["recipient_email"].casefold() != (invoice.member.email or "").casefold():
        raise InterestInvoiceValidation(
            {"recipient_email": "Must match the borrower's retained email address."}
        )
    template = invoice.calculation_configuration.communication_template
    if template is None:
        raise InterestInvoiceConflict("An approved invoice communication template is required.")

    document = store_document_upload(
        user=actor,
        request=request,
        uploaded_file=ContentFile(
            _render_invoice_pdf(invoice), name=f"{invoice.invoice_number}.pdf"
        ),
        document_category="interest_invoice",
        sensitivity_level="confidential",
        related_entity_type="interest_invoice",
        related_entity_id=invoice.pk,
        provenance_metadata={
            "invoice_number": invoice.invoice_number,
            "financial_year": invoice.financial_year,
            "calculation_version": invoice.calculation_version,
            "rate_version": invoice.rate_version_number,
        },
        audit_spec=DocumentAuditSpec(
            action="interest.invoice.document_created",
            actor_type="user",
            metadata={
                "interest_invoice_id": str(invoice.pk),
                "invoice_number": invoice.invoice_number,
                "financial_year": invoice.financial_year,
            },
        ),
    )
    snapshot_key = f"interest-invoice:{invoice.pk}:communication"
    communication = CommunicationDispatcher.create_from_template(
        actor=actor,
        template_code=template.template_code,
        recipient={
            "party_type": "borrower",
            "party_id": invoice.member_id,
            "address": cleaned["recipient_email"],
            "channel": cleaned["channel"],
        },
        context={
            "request": request,
            "idempotency_key": f"{snapshot_key}:snapshot",
            "merge_data": {
                "financial_year": invoice.financial_year,
                "invoice_number": invoice.invoice_number,
                "interest_amount": f"{invoice.interest_amount:.2f}",
            },
        },
        related_entity={"type": "interest_invoice", "id": invoice.pk},
    )
    try:
        CommunicationDispatcher.send(
            communication_id=communication.pk,
            idempotency_key=f"{snapshot_key}:delivery",
        )
    except CommunicationDispatchConflict as exc:
        raise InterestInvoiceConflict("Invoice delivery evidence conflicts with retained truth.") from exc
    issued_at = timezone.now()
    audit = AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action="interest.invoice.issued",
        entity_type="interest_invoice",
        entity_id=invoice.pk,
        old_value_json={"invoice_status": "draft"},
        new_value_json={
            "interest_invoice_id": str(invoice.pk),
            "invoice_status": "issued",
            "document_id": str(document.pk),
            "communication_id": str(communication.pk),
            "actor_user_id": str(actor.pk),
            "channel": cleaned["channel"],
        },
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )
    invoice.invoice_status = InterestInvoice.STATUS_ISSUED
    invoice.document = document
    invoice.communication = communication
    invoice.issued_by_user = actor
    invoice.issued_at = issued_at
    invoice.issuance_idempotency_key_digest = key_digest
    invoice.issuance_payload_digest = payload_digest
    invoice.issuance_audit = audit
    invoice.save(update_fields=[
        "invoice_status", "document", "communication", "issued_by_user", "issued_at",
        "issuance_idempotency_key_digest", "issuance_payload_digest", "issuance_audit",
    ])
    return serialize_invoice(invoice)


@transaction.atomic
def _generate(*, actor, loan_account_id, financial_year, period_start, period_end,
              key_digest, payload_digest, request):
    _require_permission(actor, CREATE_PERMISSION)
    retained = InterestInvoice.objects.select_for_update().filter(
        generation_idempotency_key_digest=key_digest
    ).first()
    if retained is not None:
        if retained.generation_payload_digest == payload_digest:
            return _replay(retained)
        raise InterestInvoiceConflict("The idempotency key was used for a different request.")
    account = (
        _scoped_accounts(actor)
        .select_for_update()
        .select_related("member")
        .filter(pk=loan_account_id)
        .first()
    )
    if account is None:
        raise InterestInvoiceNotFound
    if (
        account.loan_account_status not in SERVICEABLE_STATUSES
        or account.disbursed_amount <= 0
        or account.principal_outstanding <= 0
        or (account.tenure_start_date and account.tenure_start_date > period_end)
        or (account.closed_at and account.closed_at.date() <= period_end)
    ):
        raise InterestInvoiceConflict("The loan is not eligible for this invoice period.")
    if InterestInvoice.objects.filter(
        loan_account=account,
        interest_period_start=period_start,
        interest_period_end=period_end,
    ).exists():
        raise InterestInvoiceConflict("An invoice already exists for this loan period.")
    config = _resolve_configuration(period_end)
    _require_configured_owner(actor, config)
    invoice_id = uuid.uuid4()
    rate_snapshot = consume_effective_rate(
        consumer_kind="interest_invoice",
        consumer_reference_id=invoice_id,
        loan_account_id=account.pk,
        calculation_date=period_end,
    )
    rate_config = InterestRateConfig.objects.get(pk=rate_snapshot.rate_config_id)
    if not rate_config.benchmark_name or rate_config.spread_rate is None or not rate_config.reset_frequency:
        raise InterestInvoiceConflict("Approved benchmark, spread, and reset configuration is required.")
    days = (period_end - period_start).days + 1
    principal = account.principal_outstanding.quantize(_MONEY)
    gross = (
        principal * rate_snapshot.effective_rate * Decimal(days)
        / (Decimal("100") * Decimal(config.day_count_basis))
    ).quantize(_MONEY, rounding=ROUND_HALF_UP)
    paid = (
        RepaymentAllocation.objects.filter(
            loan_account=account,
            repayment__received_date__range=(period_start, period_end),
            reversal__isnull=True,
        ).aggregate(total=Sum("allocated_to_interest"))["total"]
        or Decimal("0.00")
    ).quantize(_MONEY)
    unpaid = max(gross - paid, Decimal("0.00"))
    tax = (unpaid * config.tax_rate / Decimal("100")).quantize(
        _MONEY, rounding=ROUND_HALF_UP
    )
    total = (unpaid + tax + config.fixed_fee_amount).quantize(_MONEY)
    generated_at = timezone.now()
    invoice_number = f"INT-{period_start.year}-{str(invoice_id).split('-')[0].upper()}"
    evidence = {
        "interest_invoice_id": str(invoice_id),
        "loan_account_id": str(account.pk),
        "member_id": str(account.member_id),
        "financial_year": financial_year,
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "principal_base_amount": f"{principal:.2f}",
        "rate_version": rate_snapshot.version_number,
        "calculation_version": config.version_number,
        "interest_amount": f"{total:.2f}",
        "actor_user_id": str(actor.pk),
    }
    audit = AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action="interest.invoice.generated",
        entity_type="interest_invoice",
        entity_id=invoice_id,
        new_value_json=evidence,
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )
    invoice = InterestInvoice.objects.create(
        interest_invoice_id=invoice_id,
        loan_account=account,
        member=account.member,
        loan_account_number=account.loan_account_number,
        member_number=account.member.member_number or "",
        member_display_name=account.member.display_name,
        financial_year=financial_year,
        invoice_number=invoice_number,
        invoice_date=period_end,
        interest_period_start=period_start,
        interest_period_end=period_end,
        principal_base_amount=principal,
        interest_rate=rate_snapshot.effective_rate,
        rate_config=rate_config,
        rate_version_number=rate_snapshot.version_number,
        calculation_configuration=config,
        calculation_version=config.version_number,
        calculation_method=config.calculation_method,
        day_count_basis=config.day_count_basis,
        calculation_days=days,
        gross_interest_amount=gross,
        interest_paid_amount=paid,
        tax_rate=config.tax_rate,
        tax_amount=tax,
        fixed_fee_amount=config.fixed_fee_amount,
        interest_amount=total,
        generated_by_user=actor,
        generated_at=generated_at,
        generation_idempotency_key_digest=key_digest,
        generation_payload_digest=payload_digest,
        generation_audit=audit,
    )
    return serialize_invoice(invoice)


def serialize_invoice(invoice):
    return {
        "interest_invoice_id": str(invoice.pk),
        "loan_account_id": str(invoice.loan_account_id),
        "member_id": str(invoice.member_id),
        "financial_year": invoice.financial_year,
        "invoice_number": invoice.invoice_number,
        "invoice_date": invoice.invoice_date.isoformat(),
        "interest_period_start": invoice.interest_period_start.isoformat(),
        "interest_period_end": invoice.interest_period_end.isoformat(),
        "principal_base_amount": f"{invoice.principal_base_amount:.2f}",
        "interest_rate": f"{invoice.interest_rate:.4f}",
        "gross_interest_amount": f"{invoice.gross_interest_amount:.2f}",
        "interest_paid_amount": f"{invoice.interest_paid_amount:.2f}",
        "tax_amount": f"{invoice.tax_amount:.2f}",
        "fixed_fee_amount": f"{invoice.fixed_fee_amount:.2f}",
        "interest_amount": f"{invoice.interest_amount:.2f}",
        "invoice_status": invoice.invoice_status,
        "rate_version_number": invoice.rate_version_number,
        "calculation_version": invoice.calculation_version,
        "document_id": str(invoice.document_id) if invoice.document_id else None,
        "communication_id": str(invoice.communication_id) if invoice.communication_id else None,
        "delivery_status": _delivery_status(invoice),
        "generated_by_user_id": str(invoice.generated_by_user_id),
        "generated_at": invoice.generated_at.isoformat().replace("+00:00", "Z"),
        "issued_by_user_id": str(invoice.issued_by_user_id) if invoice.issued_by_user_id else None,
        "issued_at": invoice.issued_at.isoformat().replace("+00:00", "Z") if invoice.issued_at else None,
    }


def _delivery_status(invoice):
    if invoice.communication_id is None:
        return None
    from sfpcl_credit.communications.models import CommunicationDeliveryJob
    return CommunicationDeliveryJob.objects.filter(
        communication_id=invoice.communication_id
    ).values_list("status", flat=True).first() or "pending"


def _validate_generation(payload, idempotency_key):
    errors = {field: "Unknown field." for field in sorted(set(payload) - {"financial_year"})}
    value = payload.get("financial_year")
    match = _FY_PATTERN.fullmatch(value) if isinstance(value, str) else None
    if match is None or int(match.group(2)) != (int(match.group(1)) + 1) % 100:
        errors["financial_year"] = "Use the format FY2026-27 for one financial year."
    if not isinstance(idempotency_key, str) or not idempotency_key.strip():
        errors["idempotency_key"] = "Idempotency-Key header is required."
    if errors:
        raise InterestInvoiceValidation(errors)
    start_year = int(match.group(1))
    return value, date(start_year, 4, 1), date(start_year + 1, 3, 31)


def _validate_issuance(payload, idempotency_key):
    allowed = {"channel", "recipient_email", "remarks"}
    errors = {field: "Unknown field." for field in sorted(set(payload) - allowed)}
    if payload.get("channel") != "email":
        errors["channel"] = "Only the configured email delivery channel is supported."
    recipient = payload.get("recipient_email")
    if not isinstance(recipient, str) or "@" not in recipient or len(recipient) > 255:
        errors["recipient_email"] = "A valid retained borrower email is required."
    remarks = payload.get("remarks")
    if not isinstance(remarks, str) or not remarks.strip() or len(remarks.strip()) > 500:
        errors["remarks"] = "Remarks are required and must not exceed 500 characters."
    if not isinstance(idempotency_key, str) or not idempotency_key.strip():
        errors["idempotency_key"] = "Idempotency-Key header is required."
    if errors:
        raise InterestInvoiceValidation(errors)
    return {
        "channel": "email",
        "recipient_email": recipient.strip().casefold(),
        "remarks": remarks.strip(),
    }


def _resolve_configuration(calculation_date):
    configs = list(
        InterestInvoiceConfiguration.objects.filter(
            status="active", effective_from__lte=calculation_date,
            effective_to__gte=calculation_date,
        ).order_by("effective_from", "interest_invoice_configuration_id")[:2]
    )
    if len(configs) != 1:
        raise InterestInvoiceConflict("One approved interest invoice configuration is required.")
    config = configs[0]
    if not isinstance(config.owner_role_codes, list) or not config.owner_role_codes:
        raise InterestInvoiceConflict("An approved invoice owner configuration is required.")
    return config


def _require_permission(actor, permission):
    if not actor.can_authenticate() or permission not in auth_service.effective_permission_codes(actor):
        raise InterestInvoicePermissionDenied


def _require_configured_owner(actor, config):
    if not set(auth_service.effective_role_codes(actor)).intersection(config.owner_role_codes):
        raise InterestInvoicePermissionDenied


def _scoped_accounts(actor):
    try:
        return scoped_account_candidates(actor=actor)
    except LoanAccountReadPermissionDenied as exc:
        raise InterestInvoicePermissionDenied from exc


def _replay(invoice):
    return {"idempotency_replayed": True, "original_response": serialize_invoice(invoice)}


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _digest_text(value):
    return hashlib.sha256(value.encode()).hexdigest()


def _positive_int(value, default, field, errors):
    if value is None:
        return default
    if not isinstance(value, str) or not value.isascii() or not value.isdigit() or int(value) < 1:
        errors[field] = "Must be a positive integer."
        return default
    return int(value)


def _render_invoice_pdf(invoice):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=A4, invariant=1)
    lines = (
        "SFPCL Annual Interest Invoice",
        f"Invoice: {invoice.invoice_number}",
        f"Financial year: {invoice.financial_year}",
        f"Borrower: {invoice.member_display_name}",
        f"Member number: {invoice.member_number or '-'}",
        f"Loan account: {invoice.loan_account_number}",
        f"Period: {invoice.interest_period_start.isoformat()} to {invoice.interest_period_end.isoformat()}",
        f"Principal base: {invoice.principal_base_amount:.2f}",
        f"Interest rate: {invoice.interest_rate:.4f}%",
        f"Interest paid: {invoice.interest_paid_amount:.2f}",
        f"Amount due: {invoice.interest_amount:.2f}",
        f"Rate version: {invoice.rate_version_number}",
        f"Calculation version: {invoice.calculation_version}",
    )
    y = 800
    for line in lines:
        pdf.drawString(50, y, line)
        y -= 24
    pdf.showPage()
    pdf.save()
    return output.getvalue()
