import hashlib
import json
import re
import uuid
from calendar import monthrange
from io import BytesIO
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.db import IntegrityError, transaction
from django.db.models import F, Q, Sum
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.configurations.modules.interest_rate_configuration import (
    AmbiguousEffectiveRate,
    InterestRateConflict,
    MissingEffectiveRate,
    consume_effective_rate,
    get_approved_rate_decision,
    resolve_effective_rate,
)
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.interest.models import (
    AccrualEntry,
    AccrualSapPostingObligation,
    InterestCapitalisation,
    InterestCapitalisationHardCopyTask,
    InterestCapitalisationInvoiceEvidence,
    InterestCapitalisationLedgerEntry,
    InterestCapitalisationPaymentEvidence,
    InterestCapitalisationScheduleEvidence,
    InterestInvoice,
    InterestInvoiceConfiguration,
    InterestInvoicePaymentEvidence,
)
from sfpcl_credit.interest.modules.as_of_accounting import decide_interest_as_of
from sfpcl_credit.loans.models import (
    LoanAccount,
    RepaymentAllocation,
    RepaymentSchedule,
    RepaymentScheduleAllocation,
)
from sfpcl_credit.loans.modules.loan_account_read import (
    LoanAccountReadPermissionDenied,
    principal_balance_as_of,
    scoped_account_candidates,
)


CREATE_PERMISSION = "finance.interest_invoice.create"
ISSUE_PERMISSION = "finance.interest_invoice.issue"
SERVICEABLE_STATUSES = {"active", "partially_repaid", "overdue", "grace_period", "extended"}
_FY_PATTERN = re.compile(r"^FY(\d{4})-(\d{2})$")
_MONEY = Decimal("0.01")
_ACCRUAL_MONTH_PATTERN = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")


class InterestInvoiceValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class InterestInvoicePermissionDenied(Exception):
    pass


class InterestInvoiceNotFound(Exception):
    pass


class InterestInvoiceConflict(Exception):
    pass


class InterestAccrualValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class InterestAccrualPermissionDenied(Exception):
    pass


class InterestAccrualNotFound(Exception):
    pass


class InterestAccrualConflict(Exception):
    pass


class InterestCapitalisationValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class InterestCapitalisationPermissionDenied(Exception):
    pass


class InterestCapitalisationConflict(Exception):
    pass


def preview_interest_capitalisations(*, actor, payload):
    financial_year, as_of_date = _validate_capitalisation_preview(payload)
    try:
        _require_permission(actor, "finance.interest_capitalise")
        accounts = _scoped_accounts(actor).filter(
            loan_account_status__in=SERVICEABLE_STATUSES
        )
    except InterestInvoicePermissionDenied as exc:
        raise InterestCapitalisationPermissionDenied from exc
    return {
        "financial_year": financial_year,
        "as_of_date": as_of_date.isoformat(),
        "dry_run": True,
        "results": [
            _capitalisation_preview_result(
                account=account,
                financial_year=financial_year,
                as_of_date=as_of_date,
            )
            for account in accounts.order_by("loan_account_id")
        ],
    }


def capitalise_unpaid_interest(
    *, actor, loan_account_id, payload, idempotency_key, request=None
):
    financial_year, capitalisation_date = _validate_capitalisation(
        payload, idempotency_key
    )
    key_digest = _digest_text(idempotency_key.strip())
    payload_digest = _digest(
        {
            "actor_id": str(actor.pk),
            "loan_account_id": str(loan_account_id),
            "financial_year": financial_year,
            "capitalisation_date": capitalisation_date.isoformat(),
        }
    )
    try:
        return _capitalise(
            actor=actor,
            loan_account_id=loan_account_id,
            financial_year=financial_year,
            capitalisation_date=capitalisation_date,
            key_digest=key_digest,
            payload_digest=payload_digest,
            request=request,
        )
    except IntegrityError as exc:
        retained = InterestCapitalisation.objects.filter(
            idempotency_key_digest=key_digest
        ).first()
        if retained is not None and retained.payload_digest == payload_digest:
            return _replay_capitalisation(retained)
        raise InterestCapitalisationConflict(
            "Interest has already been capitalised for this loan and financial year."
        ) from exc


@transaction.atomic
def _capitalise(
    *, actor, loan_account_id, financial_year, capitalisation_date,
    key_digest, payload_digest, request
):
    from sfpcl_credit.communications.modules.communication_dispatcher import (
        CommunicationDispatchConflict,
        CommunicationDispatcher,
    )
    from sfpcl_credit.documents.services import DocumentAuditSpec, store_document_upload

    try:
        _require_permission(actor, "finance.interest_capitalise")
    except InterestInvoicePermissionDenied as exc:
        raise InterestCapitalisationPermissionDenied from exc
    retained = InterestCapitalisation.objects.select_for_update().filter(
        idempotency_key_digest=key_digest
    ).first()
    if retained is not None:
        if retained.payload_digest == payload_digest:
            return _replay_capitalisation(retained)
        raise InterestCapitalisationConflict(
            "The idempotency key was used for a different capitalisation request."
        )
    try:
        account = (
            _scoped_accounts(actor)
            .select_for_update()
            .select_related("member")
            .filter(pk=loan_account_id)
            .first()
        )
    except InterestInvoicePermissionDenied as exc:
        raise InterestCapitalisationPermissionDenied from exc
    if account is None:
        raise InterestCapitalisationPermissionDenied
    retained = InterestCapitalisation.objects.filter(
        idempotency_key_digest=key_digest
    ).first()
    if retained is not None:
        if retained.payload_digest == payload_digest:
            return _replay_capitalisation(retained)
        raise InterestCapitalisationConflict(
            "The idempotency key was used for a different capitalisation request."
        )
    if account.loan_account_status not in SERVICEABLE_STATUSES:
        raise InterestCapitalisationConflict(
            "Only a serviceable loan can capitalise unpaid interest."
        )
    if account.total_outstanding != (
        account.principal_outstanding
        + account.interest_outstanding
        + account.charges_outstanding
    ):
        raise InterestCapitalisationConflict(
            "The loan balance components conflict with retained account truth."
        )
    if InterestCapitalisation.objects.filter(
        loan_account=account, financial_year=financial_year
    ).exists():
        raise InterestCapitalisationConflict(
            "Interest has already been capitalised for this loan and financial year."
        )
    if not account.member.email:
        raise InterestCapitalisationConflict(
            "A retained borrower email is required for capitalisation intimation."
        )
    start_year = int(_FY_PATTERN.fullmatch(financial_year).group(1))
    period_start = date(start_year, 4, 1)
    period_end = date(start_year + 1, 3, 31)
    eligibility_cutoff = date(start_year + 1, 4, 30)
    invoices = list(
        InterestInvoice.objects.select_for_update(of=("self",))
        .select_related("calculation_configuration")
        .filter(
            loan_account=account,
            financial_year=financial_year,
            invoice_status=InterestInvoice.STATUS_ISSUED,
            capitalisation_evidence__isnull=True,
            invoice_date__lte=eligibility_cutoff,
            interest_period_end__lte=period_end,
        )
        .order_by("interest_invoice_id")
    )
    invoice_amounts = []
    for invoice in invoices:
        outstanding = (
            invoice.gross_interest_amount - invoice.interest_paid_amount
        ).quantize(_MONEY)
        applications = []
        exact_allocation_ids = RepaymentScheduleAllocation.objects.filter(
            repayment_schedule__due_date__range=(
                invoice.interest_period_start,
                invoice.interest_period_end,
            ),
            interest_applied__gt=0,
        ).values("allocation_id")
        allocations = RepaymentAllocation.objects.select_for_update(of=("self",)).filter(
            pk__in=exact_allocation_ids,
            loan_account=account,
            repayment__received_date__gt=invoice.invoice_date,
            repayment__received_date__lte=eligibility_cutoff,
            allocated_to_interest__gt=0,
            reversal__isnull=True,
            interest_capitalisation_evidence__isnull=True,
        ).order_by(
            "repayment__received_date", "allocated_at", "repayment_allocation_id"
        )
        for allocation in allocations:
            exact_interest = allocation.schedule_applications.filter(
                repayment_schedule__due_date__range=(
                    invoice.interest_period_start,
                    invoice.interest_period_end,
                )
            ).aggregate(total=Sum("interest_applied"))["total"] or Decimal("0.00")
            applied = min(exact_interest, outstanding)
            if applied <= 0:
                break
            applications.append((allocation, applied))
            outstanding = (outstanding - applied).quantize(_MONEY)
        if outstanding > 0:
            invoice_amounts.append((invoice, outstanding, applications))
    if not invoice_amounts:
        raise InterestCapitalisationConflict(
            "No eligible issued unpaid interest invoice exists for this loan and financial year."
        )
    accruals = list(
        AccrualEntry.objects.select_for_update()
        .filter(
            loan_account=account,
            interest_period_start__gte=period_start,
            interest_period_end__lte=period_end,
        )
        .order_by("accrual_entry_id")
    )
    unpaid = sum(
        (amount for _, amount, _ in invoice_amounts), Decimal("0.00")
    ).quantize(_MONEY)
    old_principal = account.principal_outstanding.quantize(_MONEY)
    new_principal = (old_principal + unpaid).quantize(_MONEY)
    interest_reclassified = min(account.interest_outstanding, unpaid).quantize(_MONEY)
    new_interest = (account.interest_outstanding - interest_reclassified).quantize(_MONEY)
    new_total = (
        new_principal + new_interest + account.charges_outstanding
    ).quantize(_MONEY)
    schedule_transfers = []
    remaining_reclassification = interest_reclassified
    if remaining_reclassification > 0:
        schedule_rows = RepaymentSchedule.objects.select_for_update().filter(
            loan_account=account,
            due_date__range=(period_start, period_end),
        ).order_by("due_date", "installment_number", "repayment_schedule_id")
        for schedule in schedule_rows:
            outstanding_schedule_interest = schedule.interest_due - schedule.paid_interest
            applied = min(outstanding_schedule_interest, remaining_reclassification)
            if applied <= 0:
                continue
            before_status = schedule.schedule_status
            schedule.paid_interest += applied
            remaining_reclassification -= applied
            if (
                schedule.paid_principal == schedule.principal_due
                and schedule.paid_interest == schedule.interest_due
                and schedule.paid_charges == schedule.charges_due
            ):
                schedule.schedule_status = "paid"
            schedule.save(update_fields=["paid_interest", "schedule_status"])
            schedule_transfers.append(
                (schedule, applied, before_status, schedule.schedule_status)
            )
    capitalisation_id = uuid.uuid4()
    merge_data = {
        "financial_year": financial_year,
        "unpaid_interest_amount": f"{unpaid:.2f}",
        "new_principal_amount": f"{new_principal:.2f}",
    }
    communication_key = f"interest-capitalisation:{capitalisation_id}:email"
    try:
        communication = CommunicationDispatcher.create_from_template(
            actor=actor,
            template_code="interest_capitalisation_notice",
            recipient={
                "party_type": "borrower",
                "party_id": account.member_id,
                "address": account.member.email,
                "channel": "email",
            },
            context={
                "request": request,
                "idempotency_key": f"{communication_key}:snapshot",
                "merge_data": merge_data,
            },
            related_entity={
                "type": "interest_capitalisation",
                "id": capitalisation_id,
            },
        )
        CommunicationDispatcher.send(
            communication_id=communication.pk,
            idempotency_key=f"{communication_key}:delivery",
        )
    except (CommunicationDispatchConflict, ValidationError) as exc:
        raise InterestCapitalisationConflict(
            "Approved borrower intimation configuration is required."
        ) from exc
    letter = store_document_upload(
        user=actor,
        request=request,
        uploaded_file=ContentFile(
            _render_capitalisation_letter_pdf(
                account=account,
                financial_year=financial_year,
                unpaid=unpaid,
                new_principal=new_principal,
                capitalisation_date=capitalisation_date,
            ),
            name=f"interest-capitalisation-{account.loan_account_number}-{financial_year}.pdf",
        ),
        document_category="interest_capitalisation_letter",
        sensitivity_level="confidential",
        related_entity_type="interest_capitalisation",
        related_entity_id=capitalisation_id,
        provenance_metadata={
            "financial_year": financial_year,
            "loan_account_id": str(account.pk),
            "unpaid_interest_amount": f"{unpaid:.2f}",
            "new_principal_amount": f"{new_principal:.2f}",
        },
        audit_spec=DocumentAuditSpec(
            action="interest.capitalisation.letter_created",
            actor_type="user",
            metadata={
                "interest_capitalisation_id": str(capitalisation_id),
                "financial_year": financial_year,
            },
        ),
    )
    capitalised_at = timezone.now()
    audit = AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action="interest.capitalisation.completed",
        entity_type="interest_capitalisation",
        entity_id=capitalisation_id,
        old_value_json={
            "principal_outstanding": f"{old_principal:.2f}",
            "financial_year": financial_year,
        },
        new_value_json={
            "interest_capitalisation_id": str(capitalisation_id),
            "principal_outstanding": f"{new_principal:.2f}",
            "unpaid_interest_amount": f"{unpaid:.2f}",
            "actor_user_id": str(actor.pk),
            "borrower_intimation_email_id": str(communication.pk),
            "borrower_intimation_letter_document_id": str(letter.pk),
        },
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )
    capitalisation = InterestCapitalisation.objects.create(
        interest_capitalisation_id=capitalisation_id,
        loan_account=account,
        financial_year=financial_year,
        eligibility_as_of_date=eligibility_cutoff,
        capitalisation_date=capitalisation_date,
        old_principal_amount=old_principal,
        unpaid_interest_amount=unpaid,
        new_principal_amount=new_principal,
        rate_versions_json=sorted(
            {invoice.rate_version_number for invoice, _, _ in invoice_amounts}
            | {accrual.rate_version_number for accrual in accruals}
        ),
        calculation_versions_json=sorted(
            {invoice.calculation_version for invoice, _, _ in invoice_amounts}
            | {accrual.calculation_version for accrual in accruals}
        ),
        source_accrual_ids_json=[str(accrual.pk) for accrual in accruals],
        borrower_intimation_email=communication,
        borrower_intimation_letter_document=letter,
        capitalised_by_user=actor,
        capitalised_at=capitalised_at,
        idempotency_key_digest=key_digest,
        payload_digest=payload_digest,
        capitalisation_audit=audit,
    )
    for invoice, amount, applications in invoice_amounts:
        InterestCapitalisationInvoiceEvidence.objects.create(
            capitalisation=capitalisation,
            interest_invoice=invoice,
            unpaid_interest_amount=amount,
        )
        for allocation, applied in applications:
            InterestCapitalisationPaymentEvidence.objects.create(
                capitalisation=capitalisation,
                interest_invoice=invoice,
                repayment_allocation=allocation,
                interest_applied_amount=applied,
            )
    for schedule, applied, before_status, after_status in schedule_transfers:
        InterestCapitalisationScheduleEvidence.objects.create(
            capitalisation=capitalisation,
            repayment_schedule=schedule,
            interest_reclassified_amount=applied,
            schedule_status_before=before_status,
            schedule_status_after=after_status,
        )
    InterestCapitalisationHardCopyTask.objects.create(
        capitalisation=capitalisation,
        letter_document=letter,
        created_at=capitalised_at,
    )
    account.principal_outstanding = new_principal
    account.interest_outstanding = new_interest
    account.total_outstanding = new_total
    account.save(
        update_fields=[
            "principal_outstanding", "interest_outstanding", "total_outstanding"
        ]
    )
    InterestCapitalisationLedgerEntry.objects.create(
        capitalisation=capitalisation,
        loan_account=account,
        transaction_date=capitalisation_date,
        debit_amount=unpaid,
        principal_balance=new_principal,
        interest_balance=new_interest,
        charges_balance=account.charges_outstanding,
        total_outstanding=new_total,
        actor_user=actor,
        actor_display_name=actor.full_name,
        created_at=capitalised_at,
    )
    original_response = serialize_capitalisation(capitalisation)
    InterestCapitalisation.objects.filter(
        pk=capitalisation.pk,
        original_response_json={},
    )._store_original_response(original_response_json=original_response)
    capitalisation.original_response_json = original_response
    return original_response


def create_monthly_accrual(*, actor, loan_account_id, payload, idempotency_key, request=None):
    accrual_month, period_start, period_end = _validate_accrual_creation(
        payload, idempotency_key
    )
    key_digest = _digest_text(idempotency_key.strip())
    payload_digest = _digest(
        {
            "actor_id": str(actor.pk),
            "loan_account_id": str(loan_account_id),
            "accrual_month": accrual_month,
        }
    )
    try:
        return _create_accrual(
            actor=actor,
            loan_account_id=loan_account_id,
            accrual_month=accrual_month,
            period_start=period_start,
            period_end=period_end,
            key_digest=key_digest,
            payload_digest=payload_digest,
            request=request,
            required_permission="finance.accrual.create",
        )
    except IntegrityError as exc:
        retained = AccrualEntry.objects.filter(
            generation_idempotency_key_digest=key_digest
        ).first()
        if retained is not None and retained.generation_payload_digest == payload_digest:
            return _replay_accrual_generation(retained)
        raise InterestAccrualConflict(
            "An accrual already exists for this request or loan month."
        ) from exc


@transaction.atomic
def _create_accrual(
    *, actor, loan_account_id, accrual_month, period_start, period_end,
    key_digest, payload_digest, request, required_permission
):
    _require_accrual_permission(actor, required_permission)
    retained = AccrualEntry.objects.select_for_update().filter(
        generation_idempotency_key_digest=key_digest
    ).first()
    if retained is not None:
        if retained.generation_payload_digest == payload_digest:
            return _replay_accrual_generation(retained)
        raise InterestAccrualConflict("The idempotency key was used for a different request.")
    account = (
        _accrual_scoped_accounts(actor)
        .select_for_update()
        .filter(pk=loan_account_id)
        .first()
    )
    if account is None:
        raise InterestAccrualNotFound
    retained = AccrualEntry.objects.filter(
        generation_idempotency_key_digest=key_digest
    ).first()
    if retained is not None:
        if retained.generation_payload_digest == payload_digest:
            return _replay_accrual_generation(retained)
        raise InterestAccrualConflict(
            "The idempotency key was used for a different request."
        )
    principal = principal_balance_as_of(account=account, as_of_date=period_end).quantize(_MONEY)
    if not _is_accrual_eligible(account, period_start, period_end, principal):
        raise InterestAccrualConflict("The loan is not eligible for this accrual period.")
    if AccrualEntry.objects.filter(
        loan_account=account, accrual_month=accrual_month
    ).exists():
        raise InterestAccrualConflict("An accrual already exists for this loan month.")
    config = _resolve_accrual_configuration(period_end)
    accrual_id = uuid.uuid4()
    rate_snapshot = _consume_accrual_rate(
        accrual_id=accrual_id, account_id=account.pk, calculation_date=period_end
    )
    rate_config = get_approved_rate_decision(rate_snapshot.rate_config_id)
    if not rate_config.benchmark_name or rate_config.spread_rate is None or not rate_config.reset_frequency:
        raise InterestAccrualConflict(
            "Approved benchmark, spread, and reset configuration is required."
        )
    decision = decide_interest_as_of(
        account=account,
        period_start=period_start,
        period_end=period_end,
        configuration=config,
    )
    days = decision.calculation_days
    amount = decision.gross_interest_amount
    generated_at = timezone.now()
    evidence = {
        "accrual_entry_id": str(accrual_id),
        "loan_account_id": str(account.pk),
        "accrual_month": accrual_month,
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "principal_base_amount": f"{principal:.2f}",
        "rate_version": rate_snapshot.version_number,
        "calculation_version": config.version_number,
        "interest_accrued_amount": f"{amount:.2f}",
        "sap_posting_status": "pending",
        "actor_user_id": str(actor.pk),
    }
    audit = AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action="interest.accrual.generated",
        entity_type="accrual_entry",
        entity_id=accrual_id,
        new_value_json=evidence,
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )
    accrual = AccrualEntry.objects.create(
        accrual_entry_id=accrual_id,
        loan_account=account,
        accrual_month=accrual_month,
        interest_period_start=period_start,
        interest_period_end=period_end,
        principal_base_amount=principal,
        interest_rate=rate_snapshot.effective_rate,
        rate_config_id=rate_config.interest_rate_config_id,
        rate_version_number=rate_snapshot.version_number,
        calculation_configuration=config,
        calculation_version=config.version_number,
        calculation_method=config.calculation_method,
        day_count_basis=config.day_count_basis,
        calculation_days=days,
        calculation_segments_json=decision.snapshot(),
        interest_accrued_amount=amount,
        generated_by_user=actor,
        generated_at=generated_at,
        generation_idempotency_key_digest=key_digest,
        generation_payload_digest=payload_digest,
        generation_audit=audit,
    )
    AccrualSapPostingObligation.objects.create(accrual_entry=accrual)
    original_response = serialize_accrual(accrual)
    AccrualEntry.objects.filter(
        pk=accrual.pk,
        generation_original_response_json={},
    )._store_response(generation_original_response_json=original_response)
    accrual.generation_original_response_json = original_response
    return original_response


def serialize_accrual(accrual):
    return {
        "accrual_entry_id": str(accrual.pk),
        "loan_account_id": str(accrual.loan_account_id),
        "accrual_month": accrual.accrual_month,
        "interest_period_start": accrual.interest_period_start.isoformat(),
        "interest_period_end": accrual.interest_period_end.isoformat(),
        "principal_base_amount": f"{accrual.principal_base_amount:.2f}",
        "interest_rate": f"{accrual.interest_rate:.4f}",
        "calculation_days": accrual.calculation_days,
        "day_count_basis": accrual.day_count_basis,
        "interest_accrued_amount": f"{accrual.interest_accrued_amount:.2f}",
        "rate_version_number": accrual.rate_version_number,
        "calculation_version": accrual.calculation_version,
        "sap_posting_status": accrual.posted_status,
        "sap_entry_reference": accrual.sap_entry_reference or None,
        "generated_by_user_id": str(accrual.generated_by_user_id),
        "generated_at": accrual.generated_at.isoformat().replace("+00:00", "Z"),
        "posted_by_user_id": str(accrual.posted_by_user_id) if accrual.posted_by_user_id else None,
        "posted_at": (
            accrual.posted_at.isoformat().replace("+00:00", "Z")
            if accrual.posted_at else None
        ),
    }


def bulk_generate_monthly_accruals(*, actor, payload, idempotency_key, request=None):
    cleaned = _validate_bulk_accrual(payload, idempotency_key)
    _require_accrual_permission(actor, "finance.accrual.bulk_generate")
    scoped = _accrual_scoped_accounts(actor)
    if cleaned["loan_account_ids"] is None:
        accounts = list(
            scoped.filter(loan_account_status__in=SERVICEABLE_STATUSES)
            .order_by("loan_account_id")[:101]
        )
        if len(accounts) > 100:
            raise InterestAccrualValidation(
                {"loan_account_ids": "All-active generation is limited to 100 loans; select a batch."}
            )
    else:
        by_id = {str(row.pk): row for row in scoped.filter(pk__in=cleaned["loan_account_ids"])}
        accounts = [by_id.get(account_id) for account_id in cleaned["loan_account_ids"]]
    results = []
    for account_id, account in zip(
        cleaned["loan_account_ids"] or [str(row.pk) for row in accounts], accounts
    ):
        if account is None:
            results.append(_bulk_result(account_id, "failed", False, reason="inaccessible"))
            continue
        existing = AccrualEntry.objects.filter(
            loan_account=account, accrual_month=cleaned["accrual_month"]
        ).first()
        if existing is not None:
            results.append(
                _bulk_result(
                    account_id,
                    "existing",
                    True,
                    amount=existing.interest_accrued_amount,
                )
            )
            continue
        principal = principal_balance_as_of(
            account=account, as_of_date=cleaned["period_end"]
        ).quantize(_MONEY)
        if not _is_accrual_eligible(
            account, cleaned["period_start"], cleaned["period_end"], principal
        ):
            results.append(_bulk_result(account_id, "skipped", False, reason="ineligible_period"))
            continue
        if cleaned["dry_run"]:
            try:
                amount = _preview_accrual_amount(
                    account, cleaned["period_start"], cleaned["period_end"], principal
                )
            except (
                AmbiguousEffectiveRate,
                InterestAccrualConflict,
                MissingEffectiveRate,
            ):
                results.append(
                    _bulk_result(account_id, "failed", False, reason="calculation_unavailable")
                )
            else:
                results.append(_bulk_result(account_id, "created", False, amount=amount))
            continue
        child_key = f"{idempotency_key.strip()}:{account_id}:{cleaned['accrual_month']}"
        child_key_digest = _digest_text(child_key)
        child_payload_digest = _digest(
            {
                "actor_id": str(actor.pk),
                "loan_account_id": account_id,
                "accrual_month": cleaned["accrual_month"],
            }
        )
        try:
            created = _create_accrual(
                actor=actor,
                loan_account_id=account.pk,
                accrual_month=cleaned["accrual_month"],
                period_start=cleaned["period_start"],
                period_end=cleaned["period_end"],
                key_digest=child_key_digest,
                payload_digest=child_payload_digest,
                request=request,
                required_permission="finance.accrual.bulk_generate",
            )
        except (IntegrityError, InterestAccrualConflict, InterestAccrualNotFound):
            results.append(_bulk_result(account_id, "failed", False, reason="calculation_unavailable"))
        else:
            data = created.get("original_response", created)
            results.append(
                _bulk_result(account_id, "created", True, amount=data["interest_accrued_amount"])
            )
    return {"accrual_month": cleaned["accrual_month"], "dry_run": cleaned["dry_run"], "results": results}


def _validate_bulk_accrual(payload, idempotency_key):
    allowed = {"accrual_month", "loan_account_ids", "dry_run"}
    errors = {field: "Unknown field." for field in sorted(set(payload) - allowed)}
    try:
        accrual_month, period_start, period_end = _validate_accrual_creation(
            {"accrual_month": payload.get("accrual_month")}, idempotency_key
        )
    except InterestAccrualValidation as exc:
        errors.update(exc.field_errors)
        accrual_month = period_start = period_end = None
    dry_run = payload.get("dry_run")
    if not isinstance(dry_run, bool):
        errors["dry_run"] = "A boolean dry_run value is required."
    ids = payload.get("loan_account_ids")
    cleaned_ids = None
    if ids is not None:
        if not isinstance(ids, list) or not ids or len(ids) > 100:
            errors["loan_account_ids"] = "Provide between 1 and 100 unique loan account UUIDs."
        else:
            cleaned_ids = []
            for value in ids:
                try:
                    canonical = str(uuid.UUID(value))
                except (TypeError, ValueError, AttributeError):
                    errors["loan_account_ids"] = "Every loan account id must be a UUID."
                    break
                cleaned_ids.append(canonical)
            if len(set(cleaned_ids)) != len(cleaned_ids):
                errors["loan_account_ids"] = "Loan account ids must be unique."
    if errors:
        raise InterestAccrualValidation(errors)
    return {
        "accrual_month": accrual_month,
        "period_start": period_start,
        "period_end": period_end,
        "loan_account_ids": cleaned_ids,
        "dry_run": dry_run,
    }


def _is_accrual_eligible(account, period_start, period_end, principal):
    serviceable_for_period = (
        account.loan_account_status in SERVICEABLE_STATUSES
        or (account.closed_at and account.closed_at.date() > period_end)
    )
    return not (
        not serviceable_for_period
        or account.disbursed_amount <= 0
        or principal <= 0
        or account.tenure_start_date is None
        or account.tenure_start_date > period_start
        or (account.closed_at and account.closed_at.date() <= period_end)
    )


def _preview_accrual_amount(account, period_start, period_end, principal):
    config = _resolve_accrual_configuration(period_end)
    rate = resolve_effective_rate(period_end)
    rate_config = get_approved_rate_decision(rate.interest_rate_config_id)
    if not rate_config.benchmark_name or rate_config.spread_rate is None or not rate_config.reset_frequency:
        raise InterestAccrualConflict("Approved rate metadata is required.")
    return _calculate_accrual_values(
        principal=principal,
        effective_rate=rate.effective_rate,
        config=config,
        period_start=period_start,
        period_end=period_end,
    )[1]


def _calculate_accrual_values(*, principal, effective_rate, config, period_start, period_end):
    days = (period_end - period_start).days + 1
    amount = (
        principal * effective_rate * Decimal(days)
        / (Decimal("100") * Decimal(config.day_count_basis))
    ).quantize(_MONEY, rounding=ROUND_HALF_UP)
    return days, amount


def _resolve_accrual_configuration(calculation_date):
    try:
        return _resolve_configuration(calculation_date)
    except InterestInvoiceConflict as exc:
        raise InterestAccrualConflict(
            "One approved interest calculation configuration is required."
        ) from exc


def _consume_accrual_rate(*, accrual_id, account_id, calculation_date):
    try:
        return consume_effective_rate(
            consumer_kind="interest_accrual",
            consumer_reference_id=accrual_id,
            loan_account_id=account_id,
            calculation_date=calculation_date,
        )
    except (AmbiguousEffectiveRate, InterestRateConflict, MissingEffectiveRate) as exc:
        raise InterestAccrualConflict(
            "One approved effective interest rate is required for the accrual period."
        ) from exc


def _bulk_result(account_id, outcome, persisted, amount=None, reason=None):
    result = {"loan_account_id": account_id, "outcome": outcome, "persisted": persisted}
    if amount is not None:
        result["interest_accrued_amount"] = f"{Decimal(amount):.2f}"
    if reason is not None:
        result["reason"] = reason
    return result


def record_accrual_sap_status(
    *, actor, accrual_entry_id, payload, idempotency_key, request=None
):
    cleaned = _validate_accrual_sap_status(payload, idempotency_key)
    key_digest = _digest_text(idempotency_key.strip())
    payload_digest = _digest(
        {
            "actor_id": str(actor.pk),
            "accrual_entry_id": str(accrual_entry_id),
            **cleaned,
        }
    )
    return _record_accrual_sap_status(
        actor=actor,
        accrual_entry_id=accrual_entry_id,
        cleaned=cleaned,
        key_digest=key_digest,
        payload_digest=payload_digest,
        request=request,
    )


@transaction.atomic
def _record_accrual_sap_status(
    *, actor, accrual_entry_id, cleaned, key_digest, payload_digest, request
):
    _require_any_accrual_permission(
        actor, {"finance.accrual.create", "finance.accrual.bulk_generate"}
    )
    accrual = (
        AccrualEntry.objects.select_for_update()
        .select_related("sap_posting_obligation")
        .filter(pk=accrual_entry_id)
        .first()
    )
    if accrual is None or not _accrual_scoped_accounts(actor).filter(
        pk=accrual.loan_account_id
    ).exists():
        raise InterestAccrualNotFound
    if accrual.posted_status != AccrualEntry.STATUS_PENDING:
        if (
            accrual.posting_idempotency_key_digest == key_digest
            and accrual.posting_payload_digest == payload_digest
        ):
            return _replay_accrual_posting(accrual)
        raise InterestAccrualConflict("SAP posting evidence has already been recorded.")
    posted_at = timezone.now()
    audit = AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action="interest.accrual.sap_status_recorded",
        entity_type="accrual_entry",
        entity_id=accrual.pk,
        old_value_json={"posted_status": "pending"},
        new_value_json={
            "accrual_entry_id": str(accrual.pk),
            "loan_account_id": str(accrual.loan_account_id),
            "accrual_month": accrual.accrual_month,
            "posted_status": cleaned["posted_status"],
            "sap_entry_reference_sha256": _digest_text(cleaned["sap_entry_reference"]),
            "remarks_sha256": _digest_text(cleaned["remarks"]),
            "actor_user_id": str(actor.pk),
        },
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )
    accrual.posted_status = cleaned["posted_status"]
    accrual.sap_entry_reference = cleaned["sap_entry_reference"]
    accrual.posted_by_user = actor
    accrual.posted_at = posted_at
    accrual.posting_idempotency_key_digest = key_digest
    accrual.posting_payload_digest = payload_digest
    accrual.posting_audit = audit
    accrual.save(
        update_fields=[
            "posted_status", "sap_entry_reference", "posted_by_user", "posted_at",
            "posting_idempotency_key_digest", "posting_payload_digest", "posting_audit",
        ]
    )
    obligation = accrual.sap_posting_obligation
    obligation.status = cleaned["posted_status"]
    obligation.resolved_at = posted_at
    obligation.save(update_fields=["status", "resolved_at"])
    original_response = serialize_accrual(accrual)
    AccrualEntry.objects.filter(
        pk=accrual.pk,
        posting_original_response_json={},
    )._store_response(posting_original_response_json=original_response)
    accrual.posting_original_response_json = original_response
    return original_response


def _validate_accrual_sap_status(payload, idempotency_key):
    allowed = {"posted_status", "sap_entry_reference", "remarks"}
    errors = {field: "Unknown field." for field in sorted(set(payload) - allowed)}
    posted_status = payload.get("posted_status")
    if posted_status not in {AccrualEntry.STATUS_POSTED, AccrualEntry.STATUS_FAILED}:
        errors["posted_status"] = "Must be posted or failed."
    reference = payload.get("sap_entry_reference", "")
    if not isinstance(reference, str) or len(reference.strip()) > 120:
        errors["sap_entry_reference"] = "Must not exceed 120 characters."
        reference = ""
    reference = reference.strip()
    if posted_status == AccrualEntry.STATUS_POSTED and not reference:
        errors["sap_entry_reference"] = "A SAP entry reference is required for posted status."
    if posted_status == AccrualEntry.STATUS_FAILED and reference:
        errors["sap_entry_reference"] = "Failed status cannot claim a SAP entry reference."
    remarks = payload.get("remarks")
    if not isinstance(remarks, str) or not remarks.strip() or len(remarks.strip()) > 500:
        errors["remarks"] = "Remarks are required and must not exceed 500 characters."
        remarks = ""
    if not isinstance(idempotency_key, str) or not idempotency_key.strip():
        errors["idempotency_key"] = "Idempotency-Key header is required."
    if errors:
        raise InterestAccrualValidation(errors)
    return {
        "posted_status": posted_status,
        "sap_entry_reference": reference,
        "remarks": remarks.strip(),
    }


def _require_any_accrual_permission(actor, permissions):
    if not actor.can_authenticate() or not permissions.intersection(
        auth_service.effective_permission_codes(actor)
    ):
        raise InterestAccrualPermissionDenied


def _validate_accrual_creation(payload, idempotency_key):
    errors = {
        field: "Unknown field." for field in sorted(set(payload) - {"accrual_month"})
    }
    value = payload.get("accrual_month")
    match = _ACCRUAL_MONTH_PATTERN.fullmatch(value) if isinstance(value, str) else None
    if match is None:
        errors["accrual_month"] = "Use the format YYYY-MM."
    if not isinstance(idempotency_key, str) or not idempotency_key.strip():
        errors["idempotency_key"] = "Idempotency-Key header is required."
    if errors:
        raise InterestAccrualValidation(errors)
    year = int(match.group(1))
    month = int(match.group(2))
    return value, date(year, month, 1), date(year, month, monthrange(year, month)[1])


def _require_accrual_permission(actor, permission):
    if not actor.can_authenticate() or permission not in auth_service.effective_permission_codes(actor):
        raise InterestAccrualPermissionDenied


def _accrual_scoped_accounts(actor):
    try:
        return scoped_account_candidates(actor=actor)
    except LoanAccountReadPermissionDenied as exc:
        raise InterestAccrualPermissionDenied from exc


def _replay_accrual_generation(accrual):
    if not accrual.generation_original_response_json:
        raise InterestAccrualConflict(
            "The retained accrual has no verifiable original generation response."
        )
    return {
        "idempotency_replayed": True,
        "original_response": accrual.generation_original_response_json,
    }


def _replay_accrual_posting(accrual):
    if not accrual.posting_original_response_json:
        raise InterestAccrualConflict(
            "The retained accrual has no verifiable original posting response."
        )
    return {
        "idempotency_replayed": True,
        "original_response": accrual.posting_original_response_json,
    }


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
    _require_frozen_owner(actor, invoice.owner_role_codes_snapshot_json)
    if invoice.invoice_status == InterestInvoice.STATUS_ISSUED:
        if (
            invoice.issuance_idempotency_key_digest == key_digest
            and invoice.issuance_payload_digest == payload_digest
        ):
            return {
                "idempotency_replayed": True,
                "original_response": _verified_invoice_response(
                    invoice.issuance_original_response_json,
                    "issuance",
                ),
            }
        raise InterestInvoiceConflict("The invoice has already been issued.")
    if invoice.invoice_status != InterestInvoice.STATUS_DRAFT:
        raise InterestInvoiceConflict("Only a valid draft invoice can be issued.")
    if cleaned["recipient_email"].casefold() != (invoice.member.email or "").casefold():
        raise InterestInvoiceValidation(
            {"recipient_email": "Must match the borrower's retained email address."}
        )
    template = invoice.communication_template_snapshot
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
    original_response = serialize_invoice(invoice)
    InterestInvoice.objects.filter(
        pk=invoice.pk,
        issuance_original_response_json={},
    )._store_response(issuance_original_response_json=original_response)
    invoice.issuance_original_response_json = original_response
    return original_response


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
    retained = InterestInvoice.objects.filter(
        generation_idempotency_key_digest=key_digest
    ).first()
    if retained is not None:
        if retained.generation_payload_digest == payload_digest:
            return _replay(retained)
        raise InterestInvoiceConflict(
            "The idempotency key was used for a different request."
        )
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
    rate_config = get_approved_rate_decision(rate_snapshot.rate_config_id)
    if not rate_config.benchmark_name or rate_config.spread_rate is None or not rate_config.reset_frequency:
        raise InterestInvoiceConflict("Approved benchmark, spread, and reset configuration is required.")
    decision = decide_interest_as_of(
        account=account,
        period_start=period_start,
        period_end=period_end,
        configuration=config,
    )
    days = decision.calculation_days
    principal = decision.segments[0].principal_amount
    gross = decision.gross_interest_amount
    payment_applications = list(
        RepaymentScheduleAllocation.objects.filter(
            allocation__loan_account=account,
            allocation__repayment__received_date__lte=period_end,
            allocation__reversal__isnull=True,
            repayment_schedule__due_date__range=(period_start, period_end),
            interest_applied__gt=0,
            interest_invoice_evidence__isnull=True,
        ).order_by(
            "allocation__repayment__received_date",
            "repayment_schedule__due_date",
            "repayment_schedule_allocation_id",
        )
    )
    paid = sum(
        (application.interest_applied for application in payment_applications),
        Decimal("0.00"),
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
        rate_config_id=rate_config.interest_rate_config_id,
        rate_version_number=rate_snapshot.version_number,
        calculation_configuration=config,
        calculation_version=config.version_number,
        calculation_method=config.calculation_method,
        day_count_basis=config.day_count_basis,
        calculation_days=days,
        calculation_segments_json=decision.snapshot(),
        owner_role_codes_snapshot_json=list(config.owner_role_codes),
        communication_template_snapshot=config.communication_template,
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
    for application in payment_applications:
        InterestInvoicePaymentEvidence.objects.create(
            interest_invoice=invoice,
            schedule_application=application,
            interest_applied_amount=application.interest_applied,
        )
    original_response = serialize_invoice(invoice)
    InterestInvoice.objects.filter(
        pk=invoice.pk,
        generation_original_response_json={},
    )._store_response(generation_original_response_json=original_response)
    invoice.generation_original_response_json = original_response
    return original_response


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


def _validate_capitalisation_preview(payload):
    allowed = {"financial_year", "as_of_date", "dry_run"}
    errors = {field: "Unknown field." for field in sorted(set(payload) - allowed)}
    financial_year = payload.get("financial_year")
    match = _FY_PATTERN.fullmatch(financial_year) if isinstance(financial_year, str) else None
    if match is None or int(match.group(2)) != (int(match.group(1)) + 1) % 100:
        errors["financial_year"] = "Use the format FY2026-27 for one financial year."
    try:
        as_of_date = date.fromisoformat(payload.get("as_of_date", ""))
    except (TypeError, ValueError):
        as_of_date = None
        errors["as_of_date"] = "Use an ISO date."
    if payload.get("dry_run") is not True:
        errors["dry_run"] = "Capitalisation checks must be dry runs."
    if errors:
        raise InterestCapitalisationValidation(errors)
    return financial_year, as_of_date


def _validate_capitalisation(payload, idempotency_key):
    allowed = {"financial_year", "capitalisation_date"}
    errors = {field: "Unknown field." for field in sorted(set(payload) - allowed)}
    financial_year = payload.get("financial_year")
    match = _FY_PATTERN.fullmatch(financial_year) if isinstance(financial_year, str) else None
    if match is None or int(match.group(2)) != (int(match.group(1)) + 1) % 100:
        errors["financial_year"] = "Use the format FY2026-27 for one financial year."
    try:
        capitalisation_date = date.fromisoformat(payload.get("capitalisation_date", ""))
    except (TypeError, ValueError):
        capitalisation_date = None
        errors["capitalisation_date"] = "Use an ISO date."
    if match is not None and capitalisation_date is not None:
        cutoff = date(int(match.group(1)) + 1, 4, 30)
        if capitalisation_date <= cutoff:
            errors["capitalisation_date"] = "Capitalisation must be after 30 April."
    if (
        not isinstance(idempotency_key, str)
        or not idempotency_key.strip()
        or len(idempotency_key.strip()) > 200
    ):
        errors["idempotency_key"] = (
            "Idempotency-Key header is required and must not exceed 200 characters."
        )
    if errors:
        raise InterestCapitalisationValidation(errors)
    return financial_year, capitalisation_date


def _capitalisation_preview_result(*, account, financial_year, as_of_date):
    end_year = int(_FY_PATTERN.fullmatch(financial_year).group(1)) + 1
    cutoff = date(end_year, 4, 30)
    invoices = InterestInvoice.objects.filter(
            loan_account=account,
            financial_year=financial_year,
            invoice_status=InterestInvoice.STATUS_ISSUED,
            invoice_date__lte=as_of_date,
            capitalisation_evidence__isnull=True,
        )
    unpaid = Decimal("0.00")
    for invoice in invoices:
        post_invoice_paid = (
            RepaymentScheduleAllocation.objects.filter(
                allocation__loan_account=account,
                allocation__repayment__received_date__gt=invoice.invoice_date,
                allocation__repayment__received_date__lte=as_of_date,
                allocation__reversal__isnull=True,
                allocation__interest_capitalisation_evidence__isnull=True,
                repayment_schedule__due_date__range=(
                    invoice.interest_period_start,
                    invoice.interest_period_end,
                ),
            ).aggregate(total=Sum("interest_applied"))["total"]
            or Decimal("0.00")
        )
        unpaid += max(
            invoice.gross_interest_amount
            - invoice.interest_paid_amount
            - post_invoice_paid,
            Decimal("0.00"),
        )
    unpaid = unpaid.quantize(_MONEY)
    old_principal = account.principal_outstanding.quantize(_MONEY)
    already_capitalised = InterestCapitalisation.objects.filter(
        loan_account=account, financial_year=financial_year
    ).exists()
    eligible = as_of_date >= cutoff and unpaid > 0 and not already_capitalised
    if already_capitalised:
        reason = "already_capitalised"
    elif as_of_date < cutoff:
        reason = "cutoff_not_reached"
    elif unpaid <= 0:
        reason = "no_unpaid_interest"
    else:
        reason = "eligible_unpaid_interest"
    return {
        "loan_account_id": str(account.pk),
        "eligible": eligible,
        "reason_code": reason,
        "old_principal_amount": f"{old_principal:.2f}",
        "unpaid_interest_amount": f"{unpaid:.2f}",
        "new_principal_amount": f"{old_principal + unpaid:.2f}",
    }


def serialize_capitalisation(capitalisation):
    from sfpcl_credit.communications.models import CommunicationDeliveryJob

    delivery_status = (
        CommunicationDeliveryJob.objects.filter(
            communication_id=capitalisation.borrower_intimation_email_id
        ).values_list("status", flat=True).first()
        or "pending"
    )
    return {
        "interest_capitalisation_id": str(capitalisation.pk),
        "loan_account_id": str(capitalisation.loan_account_id),
        "financial_year": capitalisation.financial_year,
        "eligibility_as_of_date": capitalisation.eligibility_as_of_date.isoformat(),
        "capitalisation_date": capitalisation.capitalisation_date.isoformat(),
        "old_principal_amount": f"{capitalisation.old_principal_amount:.2f}",
        "unpaid_interest_amount": f"{capitalisation.unpaid_interest_amount:.2f}",
        "new_principal_amount": f"{capitalisation.new_principal_amount:.2f}",
        "rate_versions": capitalisation.rate_versions_json,
        "calculation_versions": capitalisation.calculation_versions_json,
        "status": capitalisation.status,
        "borrower_intimation": {
            "email_id": str(capitalisation.borrower_intimation_email_id),
            "email_delivery_status": delivery_status,
            "letter_document_id": str(
                capitalisation.borrower_intimation_letter_document_id
            ),
        },
        "capitalised_by_user_id": str(capitalisation.capitalised_by_user_id),
        "capitalised_at": capitalisation.capitalised_at.isoformat().replace("+00:00", "Z"),
        "capitalisation_audit_id": str(capitalisation.capitalisation_audit_id),
    }


def _replay_capitalisation(capitalisation):
    if not capitalisation.original_response_json:
        raise InterestCapitalisationConflict(
            "The retained capitalisation has no verifiable original response."
        )
    return {
        "idempotency_replayed": True,
        "original_response": capitalisation.original_response_json,
    }


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


def _require_frozen_owner(actor, owner_role_codes):
    if not set(auth_service.effective_role_codes(actor)).intersection(owner_role_codes):
        raise InterestInvoicePermissionDenied


def _scoped_accounts(actor):
    try:
        return scoped_account_candidates(actor=actor)
    except LoanAccountReadPermissionDenied as exc:
        raise InterestInvoicePermissionDenied from exc


def _replay(invoice):
    return {
        "idempotency_replayed": True,
        "original_response": _verified_invoice_response(
            invoice.generation_original_response_json,
            "generation",
        ),
    }


def _verified_invoice_response(response, action):
    if not response:
        raise InterestInvoiceConflict(
            f"The retained invoice has no verifiable original {action} response."
        )
    return response


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


def _render_capitalisation_letter_pdf(
    *, account, financial_year, unpaid, new_principal, capitalisation_date
):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=A4, invariant=1)
    lines = (
        "SFPCL Interest Capitalisation Intimation",
        f"Date: {capitalisation_date.isoformat()}",
        f"Borrower: {account.member.display_name}",
        f"Loan account: {account.loan_account_number}",
        f"Financial year: {financial_year}",
        f"Unpaid interest capitalised: {unpaid:.2f}",
        f"Revised principal: {new_principal:.2f}",
        "This letter records the addition of unpaid interest to loan principal.",
    )
    y = 800
    for line in lines:
        pdf.drawString(50, y, line)
        y -= 24
    pdf.showPage()
    pdf.save()
    return output.getvalue()
