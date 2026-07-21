from datetime import date
from decimal import Decimal
import hashlib
import json
import re

from django.core.files.base import ContentFile
from django.db import IntegrityError, connection, transaction
from django.db.models import Prefetch
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.models import User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.interest.models import InterestCapitalisationLedgerEntry, InterestInvoice
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.disbursements.models import Disbursement
from sfpcl_credit.loans.models import LoanStatusHistory, RepaymentLedgerEntry, RepaymentReversalLedgerEntry
from sfpcl_credit.loans.modules.loan_account_read import LoanAccountReadPermissionDenied, scoped_account_candidates
from sfpcl_credit.monitoring.models import DpdStatus, PortfolioSnapshot, QuarterlyMisReport, Reminder
from sfpcl_credit.monitoring.modules.mis_exports import XLSX_MIME, render_pdf, render_xlsx

GENERATE_PERMISSION = "monitoring.mis.generate"
READ_PERMISSION = "finance.loan_account.read"
SUBMIT_PERMISSION = "monitoring.mis.submit"
REVIEW_PERMISSION = "monitoring.mis.review"
SERVICEABLE_STATUSES = {
    "active", "partially_repaid", "overdue", "grace_period", "extended",
    "non_recoverable_under_review",
}
MONEY = Decimal("0.01")
FY_PATTERN = re.compile(r"^FY(?P<start>\d{4})-(?P<end>\d{2})$")
QUARTER_BOUNDARIES = {
    "Q1": ((4, 1), (6, 30)),
    "Q2": ((7, 1), (9, 30)),
    "Q3": ((10, 1), (12, 31)),
    "Q4": ((1, 1), (3, 31)),
}
UNAVAILABLE_FIELDS = (
    "grace_period_count", "extension_count", "non_recoverable_review_count",
    "recovery_approved_count", "closure_pending_count", "grievances_open_count",
    "compliance_alert_count", "exceptions_approved_count", "director_related_party_cases_count",
    "kyc_overdue_cases_count", "pending_documentation_issues_count",
    "sap_posting_exceptions_count", "pending_noc_count",
)

class QuarterlyMisValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors

class QuarterlyMisPermissionDenied(Exception):
    pass

class QuarterlyMisConflict(Exception):
    pass

class QuarterlyMisNotFound(Exception):
    pass

@transaction.atomic
def generate(*, actor, payload, idempotency_key, request=None):
    period = _validate_period(payload)
    _begin_cutoff_snapshot()
    _require_permission(actor, GENERATE_PERMISSION)
    key_digest = _idempotency_digest(idempotency_key)
    payload_digest = _payload_digest(payload)
    replay = QuarterlyMisReport.objects.select_related("portfolio_snapshot").filter(
        generation_idempotency_key_digest=key_digest
    ).first()
    if replay is not None:
        if replay.generation_payload_digest != payload_digest:
            raise QuarterlyMisConflict("The idempotency key is already bound to another request.")
        _accessible_report(actor=actor, report_id=replay.pk)
        return replay.generation_original_response_json or serialize_report(replay)
    _lock_report_period(period)
    _require_permission(actor, GENERATE_PERMISSION)
    replay = QuarterlyMisReport.objects.select_related("portfolio_snapshot").filter(
        generation_idempotency_key_digest=key_digest
    ).first()
    if replay is not None:
        if replay.generation_payload_digest != payload_digest:
            raise QuarterlyMisConflict("The idempotency key is already bound to another request.")
        _accessible_report(actor=actor, report_id=replay.pk)
        return replay.generation_original_response_json or serialize_report(replay)
    try:
        accounts = [
            account for account in _snapshot_accounts(actor=actor, period=period)
            if account.mis_status_history
            and account.mis_status_history[0].to_status in SERVICEABLE_STATUSES
        ]
    except LoanAccountReadPermissionDenied as exc:
        raise QuarterlyMisPermissionDenied from exc
    retained = QuarterlyMisReport.objects.select_related("portfolio_snapshot").filter(
        financial_year=period["financial_year"],
        quarter=period["quarter"],
        as_of_date=period["as_of_date"],
        status=QuarterlyMisReport.STATUS_DRAFT,
    ).order_by("-revision").first()
    if retained is not None:
        raise QuarterlyMisConflict("A draft already exists for this report period.")
    rows = [_snapshot_row(account=account, period=period) for account in accounts]
    totals = _totals(rows)
    availability = {field: "unavailable" for field in UNAVAILABLE_FIELDS}
    latest_revision = (
        QuarterlyMisReport.objects.select_for_update()
        .filter(
            financial_year=period["financial_year"],
            quarter=period["quarter"],
            as_of_date=period["as_of_date"],
        )
        .order_by("-revision")
        .values_list("revision", flat=True)
        .first()
        or 0
    )
    audit = AuditLog.objects.create(
        actor_user=actor,
        action="monitoring.mis.generated",
        entity_type="quarterly_mis_period",
        entity_id=None,
        new_value_json={
            "financial_year": period["financial_year"],
            "quarter": period["quarter"],
            "as_of_date": period["as_of_date"].isoformat(),
            "revision": latest_revision + 1,
        },
        ip_address=request_ip(request) if request is not None else "",
        user_agent=request_user_agent(request) if request is not None else "",
    )
    snapshot = PortfolioSnapshot.objects.create(
        as_of_date=period["as_of_date"],
        period_start_date=period["period_start"],
        total_active_loans_count=totals["active_loans_count"],
        total_sanctioned_amount=totals["sanctioned_amount"],
        total_disbursed_amount=totals["disbursed_amount"],
        principal_outstanding_amount=totals["principal_outstanding_amount"],
        interest_outstanding_amount=totals["interest_outstanding_amount"],
        total_overdue_amount=totals["overdue_amount"],
        dpd_bucket_summary_json=totals["dpd_bucket_counts"],
        default_cases_count=None,
        extensions_count=None,
        recovery_cases_count=None,
        closed_loans_count=None,
        totals_json=totals,
        availability_json=availability,
        rows_json=rows,
        source_manifest_json={
            "loan_account_ids": [row["loan_account_id"] for row in rows],
            "dpd_status_ids": [row["source_ids"]["dpd_status_id"] for row in rows],
            "status_history_ids": [row["source_ids"]["loan_status_history_id"] for row in rows],
            "repayment_ledger_entry_ids": _flatten_source_ids(rows, "repayment_ledger_entry_ids"),
            "repayment_reversal_ledger_entry_ids": _flatten_source_ids(rows, "repayment_reversal_ledger_entry_ids"),
            "interest_capitalisation_ledger_entry_ids": _flatten_source_ids(rows, "interest_capitalisation_ledger_entry_ids"),
            "reminder_ids": _flatten_source_ids(rows, "reminder_ids"),
            "calculation_version": "QUARTERLY-MIS-1",
        },
    )
    try:
        report = QuarterlyMisReport.objects.create(
            financial_year=period["financial_year"],
            quarter=period["quarter"],
            as_of_date=period["as_of_date"],
            revision=latest_revision + 1,
            portfolio_snapshot=snapshot,
            prepared_by_user=actor,
            generation_audit=audit,
            generation_idempotency_key_digest=key_digest,
            generation_payload_digest=payload_digest,
        )
        _attach_exports(report=report, actor=actor)
    except IntegrityError:
        raise QuarterlyMisConflict("Another generation completed for this report period.")
    response = serialize_report(report)
    report.generation_original_response_json = response
    report.save(update_fields=["generation_original_response_json"])
    return response

def _lock_report_period(period):
    if connection.vendor != "postgresql":
        return
    identity = f"{period['financial_year']}:{period['quarter']}:{period['as_of_date'].isoformat()}"
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))", [identity])


def _begin_cutoff_snapshot():
    if connection.vendor == "postgresql":
        with connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")

def get_report(*, actor, report_id):
    return serialize_report(_accessible_report(actor=actor, report_id=report_id))

def list_reports(*, actor, query_params):
    _require_permission(actor, READ_PERMISSION)
    allowed = {"financial_year", "quarter", "page", "page_size"}
    unknown = set(query_params) - allowed
    if unknown:
        raise QuarterlyMisValidation({key: "Unknown query parameter." for key in sorted(unknown)})
    financial_year = query_params.get("financial_year", "")
    quarter = query_params.get("quarter", "")
    if not financial_year or quarter not in QUARTER_BOUNDARIES:
        raise QuarterlyMisValidation({"filters": "financial_year and Q1-Q4 quarter are required."})
    try:
        page = int(query_params.get("page", "1"))
        page_size = int(query_params.get("page_size", "20"))
    except (TypeError, ValueError) as exc:
        raise QuarterlyMisValidation({"pagination": "Page values must be integers."}) from exc
    if page < 1 or page_size < 1 or page_size > 100:
        raise QuarterlyMisValidation({"pagination": "Use page >= 1 and page_size between 1 and 100."})
    candidates = list(QuarterlyMisReport.objects.select_related("portfolio_snapshot").filter(
        financial_year=financial_year, quarter=quarter
    ))
    retained_ids = {
        value
        for report in candidates
        for value in report.portfolio_snapshot.source_manifest_json.get("loan_account_ids", [])
    }
    try:
        accessible_ids = {
            str(value) for value in scoped_account_candidates(actor=actor).filter(
                pk__in=retained_ids
            ).values_list("loan_account_id", flat=True)
        }
    except LoanAccountReadPermissionDenied as exc:
        raise QuarterlyMisPermissionDenied from exc
    visible = [
        report for report in candidates
        if set(report.portfolio_snapshot.source_manifest_json.get("loan_account_ids", [])) <= accessible_ids
    ]
    start = (page - 1) * page_size
    return [serialize_report(row) for row in visible[start : start + page_size]], {
        "page": page,
        "page_size": page_size,
        "total_count": len(visible),
        "total_pages": (len(visible) + page_size - 1) // page_size,
    }

def export_report(*, actor, report_id, query_params, request=None):
    _require_permission(actor, "reports.export")
    report = _accessible_report(actor=actor, report_id=report_id)
    if set(query_params) != {"format"} or query_params.get("format") not in {"pdf", "xlsx"}:
        raise QuarterlyMisValidation({"format": "Must be pdf or xlsx."})
    document = report.report_document if query_params["format"] == "pdf" else report.excel_document
    if document is None:
        raise QuarterlyMisConflict("The retained export is unavailable.")
    descriptor = LocalDocumentStorage().download_descriptor(document)
    AuditLog.objects.create(
        actor_user=actor,
        action="monitoring.mis.exported",
        entity_type="quarterly_mis_report",
        entity_id=report.pk,
        new_value_json={
            "format": query_params["format"],
            "document_id": str(document.pk),
            "checksum_sha256": document.checksum_sha256,
        },
        ip_address=request_ip(request) if request is not None else "",
        user_agent=request_user_agent(request) if request is not None else "",
    )
    return {
        "document_id": str(document.pk),
        "file_name": document.file_name,
        "mime_type": document.mime_type,
        "checksum_sha256": document.checksum_sha256,
        "download": descriptor,
        "totals": report.portfolio_snapshot.totals_json,
    }

def _attach_exports(*, report, actor):
    storage = LocalDocumentStorage()
    stored_files = []
    try:
        documents = []
        for output_format, content, mime_type in (
            ("pdf", render_pdf(report=report, snapshot=report.portfolio_snapshot), "application/pdf"),
            ("xlsx", render_xlsx(report=report, snapshot=report.portfolio_snapshot), XLSX_MIME),
        ):
            file_name = (
                f"quarterly-mis-{report.financial_year}-{report.quarter}-r{report.revision}.{output_format}"
            )
            stored = storage.store(ContentFile(content, name=file_name))
            stored_files.append(stored)
            documents.append(DocumentFile.objects.create(
                file_name=file_name,
                file_extension=f".{output_format}",
                mime_type=mime_type,
                file_size_bytes=stored.file_size_bytes,
                storage_provider=stored.storage_provider,
                storage_key=stored.storage_key,
                checksum_sha256=stored.checksum_sha256,
                uploaded_by_user=actor,
                sensitivity_level=DocumentFile.SENSITIVITY_INTERNAL,
            ))
        report.report_document, report.excel_document = documents
        report.save(update_fields=["report_document", "excel_document"])
    except Exception:
        for stored in stored_files:
            storage.delete(stored)
        raise

def drill_down(*, actor, report_id, query_params):
    report = _accessible_report(actor=actor, report_id=report_id)
    unknown = set(query_params) - {"page", "page_size"}
    if unknown:
        raise QuarterlyMisValidation({key: "Unknown query parameter." for key in sorted(unknown)})
    try:
        page = int(query_params.get("page", "1"))
        page_size = int(query_params.get("page_size", "20"))
    except (TypeError, ValueError) as exc:
        raise QuarterlyMisValidation({"pagination": "Page values must be integers."}) from exc
    if page < 1 or page_size < 1 or page_size > 100:
        raise QuarterlyMisValidation({"pagination": "Use page >= 1 and page_size between 1 and 100."})
    rows = report.portfolio_snapshot.rows_json
    start = (page - 1) * page_size
    return rows[start : start + page_size], {
        "page": page,
        "page_size": page_size,
        "total_count": len(rows),
        "total_pages": (len(rows) + page_size - 1) // page_size,
    }

def submit_to_cfo(*, actor, report_id, payload, idempotency_key, request=None):
    _require_permission(actor, SUBMIT_PERMISSION)
    if set(payload) != {"submitted_to_user_id"}:
        raise QuarterlyMisValidation({"body": "Provide only submitted_to_user_id."})
    key_digest = _idempotency_digest(idempotency_key)
    payload_digest = _payload_digest({"report_id": str(report_id), **payload})
    replay = QuarterlyMisReport.objects.filter(
        submission_idempotency_key_digest=key_digest
    ).first()
    if replay is not None:
        if replay.submission_payload_digest != payload_digest:
            raise QuarterlyMisConflict("The idempotency key is already bound to another request.")
        _accessible_report(actor=actor, report_id=replay.pk)
        return replay.submission_original_response_json
    try:
        cfo = User.objects.get(pk=payload["submitted_to_user_id"], status=User.ACTIVE_STATUS)
    except (User.DoesNotExist, ValueError, TypeError):
        raise QuarterlyMisValidation({"submitted_to_user_id": "Select an active CFO."})
    if "cfo" not in set(auth_service.effective_role_codes(cfo)):
        raise QuarterlyMisValidation({"submitted_to_user_id": "Select an active CFO."})
    conflict = None
    with transaction.atomic():
        replay = QuarterlyMisReport.objects.filter(
            submission_idempotency_key_digest=key_digest
        ).first()
        if replay is not None:
            if replay.submission_payload_digest != payload_digest:
                raise QuarterlyMisConflict("The idempotency key is already bound to another request.")
            _accessible_report(actor=actor, report_id=replay.pk)
            return replay.submission_original_response_json
        report = _locked_accessible_report(actor=actor, report_id=report_id)
        _require_permission(actor, SUBMIT_PERMISSION)
        if report.status != QuarterlyMisReport.STATUS_DRAFT:
            _audit_rejected_transition(
                actor=actor, report=report, requested="submitted", request=request
            )
            conflict = "Only a draft report can be submitted."
        else:
            audit = AuditLog.objects.create(
                actor_user=actor,
                action="monitoring.mis.submitted",
                entity_type="quarterly_mis_report",
                entity_id=report.pk,
                old_value_json={"status": report.status},
                new_value_json={
                    "status": QuarterlyMisReport.STATUS_SUBMITTED,
                    "submitted_to_user_id": str(cfo.pk),
                },
                ip_address=request_ip(request) if request is not None else "",
                user_agent=request_user_agent(request) if request is not None else "",
            )
            report.status = QuarterlyMisReport.STATUS_SUBMITTED
            report.submitted_to_user = cfo
            report.submitted_by_user = actor
            report.submitted_at = timezone.now()
            report.submission_audit = audit
            report.submission_idempotency_key_digest = key_digest
            report.submission_payload_digest = payload_digest
            response = serialize_report(report)
            report.submission_original_response_json = response
            report.save(update_fields=[
                "status", "submitted_to_user", "submitted_by_user", "submitted_at",
                "submission_audit", "submission_idempotency_key_digest",
                "submission_payload_digest", "submission_original_response_json",
            ])
    if conflict:
        raise QuarterlyMisConflict(conflict)
    return response

def mark_reviewed(*, actor, report_id, payload, idempotency_key, request=None):
    _require_permission(actor, REVIEW_PERMISSION)
    if payload:
        raise QuarterlyMisValidation({"body": "The review body must be empty."})
    key_digest = _idempotency_digest(idempotency_key)
    payload_digest = _payload_digest({"report_id": str(report_id)})
    replay = QuarterlyMisReport.objects.filter(review_idempotency_key_digest=key_digest).first()
    if replay is not None:
        if replay.review_payload_digest != payload_digest:
            raise QuarterlyMisConflict("The idempotency key is already bound to another request.")
        _accessible_report(actor=actor, report_id=replay.pk)
        if replay.submitted_to_user_id != actor.pk:
            raise QuarterlyMisPermissionDenied
        return replay.review_original_response_json
    conflict = None
    with transaction.atomic():
        replay = QuarterlyMisReport.objects.filter(
            review_idempotency_key_digest=key_digest
        ).first()
        if replay is not None:
            if replay.review_payload_digest != payload_digest:
                raise QuarterlyMisConflict("The idempotency key is already bound to another request.")
            _accessible_report(actor=actor, report_id=replay.pk)
            if replay.submitted_to_user_id != actor.pk:
                raise QuarterlyMisPermissionDenied
            return replay.review_original_response_json
        report = _locked_accessible_report(actor=actor, report_id=report_id)
        _require_permission(actor, REVIEW_PERMISSION)
        if report.status != QuarterlyMisReport.STATUS_SUBMITTED:
            _audit_rejected_transition(
                actor=actor, report=report, requested="reviewed", request=request
            )
            conflict = "Only a submitted report can be reviewed."
        elif report.submitted_to_user_id != actor.pk:
            raise QuarterlyMisPermissionDenied
        else:
            audit = AuditLog.objects.create(
                actor_user=actor,
                action="monitoring.mis.reviewed",
                entity_type="quarterly_mis_report",
                entity_id=report.pk,
                old_value_json={"status": report.status},
                new_value_json={"status": QuarterlyMisReport.STATUS_REVIEWED},
                ip_address=request_ip(request) if request is not None else "",
                user_agent=request_user_agent(request) if request is not None else "",
            )
            report.status = QuarterlyMisReport.STATUS_REVIEWED
            report.reviewed_by_user = actor
            report.reviewed_at = timezone.now()
            report.review_audit = audit
            report.review_idempotency_key_digest = key_digest
            report.review_payload_digest = payload_digest
            response = serialize_report(report)
            report.review_original_response_json = response
            report.save(update_fields=[
                "status", "reviewed_by_user", "reviewed_at", "review_audit",
                "review_idempotency_key_digest", "review_payload_digest",
                "review_original_response_json",
            ])
    if conflict:
        raise QuarterlyMisConflict(conflict)
    return response

def _audit_rejected_transition(*, actor, report, requested, request):
    AuditLog.objects.create(
        actor_user=actor,
        action="monitoring.mis.transition_rejected",
        entity_type="quarterly_mis_report",
        entity_id=report.pk,
        old_value_json={"status": report.status},
        new_value_json={"requested_status": requested, "outcome": "rejected"},
        ip_address=request_ip(request) if request is not None else "",
        user_agent=request_user_agent(request) if request is not None else "",
    )

def _locked_accessible_report(*, actor, report_id):
    report = _accessible_report(actor=actor, report_id=report_id)
    locked = QuarterlyMisReport.objects.select_for_update().select_related(
        "portfolio_snapshot"
    ).get(pk=report.pk)
    _accessible_report(actor=actor, report_id=locked.pk)
    return locked

def _accessible_report(*, actor, report_id):
    _require_permission(actor, READ_PERMISSION)
    report = QuarterlyMisReport.objects.select_related("portfolio_snapshot").filter(pk=report_id).first()
    if report is None:
        raise QuarterlyMisNotFound
    try:
        accessible_ids = set(
            str(value) for value in scoped_account_candidates(actor=actor).filter(
                pk__in=report.portfolio_snapshot.source_manifest_json.get("loan_account_ids", [])
            ).values_list("loan_account_id", flat=True)
        )
    except LoanAccountReadPermissionDenied as exc:
        raise QuarterlyMisPermissionDenied from exc
    retained_ids = set(report.portfolio_snapshot.source_manifest_json.get("loan_account_ids", []))
    if accessible_ids != retained_ids:
        raise QuarterlyMisNotFound
    return report

def _snapshot_row(*, account, period):
    dpd = account.mis_dpd_statuses[0] if account.mis_dpd_statuses else None
    if dpd is None:
        raise QuarterlyMisConflict(
            f"Loan account {account.loan_account_number} has no DPD truth for the cutoff."
        )
    balance = _latest_prefetched_balance(account)
    principal = balance["principal"] if balance is not None else account.disbursed_amount
    interest = balance["interest"] if balance is not None else account.interest_outstanding
    repayments = sum(
        (row.credit_amount for row in account.mis_repayment_entries if row.transaction_date >= period["period_start"]),
        Decimal("0.00"),
    )
    reversals = sum(
        (row.debit_amount for row in account.mis_reversal_entries if row.transaction_date >= period["period_start"]),
        Decimal("0.00"),
    )
    last_repayment = account.mis_repayment_entries[0].transaction_date if account.mis_repayment_entries else None
    reminder_count = len(account.mis_reminders)
    invoice = account.mis_interest_invoices[0] if account.mis_interest_invoices else None
    disbursement = account.mis_disbursements[0] if account.mis_disbursements else None
    disbursed_amount = sum(
        (row.disbursement_amount for row in account.mis_disbursements),
        Decimal("0.00"),
    )
    terms_security = account.terms.security_details_json or {}
    security_type = terms_security.get("security_type") if isinstance(terms_security, dict) else None
    return {
        "loan_account_id": str(account.pk),
        "loan_account_number": account.loan_account_number,
        "loan_application_number": account.loan_application.application_reference_number,
        "borrower_name": account.member.display_name,
        "borrower_type": account.loan_application.borrower_type,
        "region": account.member.registered_district or None,
        "crop": getattr(account.loan_application.crop_plan, "crop_type", None)
        if account.loan_application.crop_plan_id else None,
        "security_type": security_type,
        "loan_status": account.mis_status_history[0].to_status,
        "sanctioned_amount": _money(account.sanctioned_amount),
        "disbursed_amount": _money(disbursed_amount),
        "disbursement_date": (
            disbursement.disbursed_at.date().isoformat() if disbursement else None
        ),
        "principal_outstanding_amount": _money(principal),
        "revised_principal_amount": (
            _money(principal) if account.mis_capitalisation_entries else None
        ),
        "interest_outstanding_amount": _money(interest),
        "repayments_received_in_quarter": _money(max(Decimal("0.00"), repayments - reversals)),
        "days_past_due": dpd.days_past_due,
        "dpd_bucket": dpd.sop_bucket,
        "overdue_amount": _money(dpd.total_overdue_amount),
        "last_repayment_date": last_repayment.isoformat() if last_repayment else None,
        "reminder_count": reminder_count,
        "interest_invoice_status": _invoice_status_at_cutoff(
            invoice=invoice, cutoff=period["as_of_date"]
        ),
        "default_status": "unavailable",
        "recommended_action": "unavailable",
        "source_ids": {
            "loan_account_id": str(account.pk),
            "loan_application_id": str(account.loan_application_id),
            "member_id": str(account.member_id),
            "loan_terms_id": str(account.terms.pk),
            "sanction_decision_id": str(account.sanction_decision_id),
            "loan_status_history_id": str(account.mis_status_history[0].pk),
            "disbursement_id": str(disbursement.pk) if disbursement else None,
            "dpd_status_id": str(dpd.pk),
            "dpd_calculation_version": dpd.calculation_version,
            "interest_invoice_id": str(invoice.pk) if invoice else None,
            "interest_invoice_calculation_version": (
                invoice.calculation_version if invoice else None
            ),
            "repayment_ledger_entry_ids": [
                str(row.pk) for row in account.mis_repayment_entries
            ],
            "repayment_reversal_ledger_entry_ids": [
                str(row.pk) for row in account.mis_reversal_entries
            ],
            "interest_capitalisation_ledger_entry_ids": [
                str(row.pk) for row in account.mis_capitalisation_entries
            ],
            "reminder_ids": [str(row.pk) for row in account.mis_reminders],
        },
    }


def _invoice_status_at_cutoff(*, invoice, cutoff):
    """Project the retained invoice lifecycle decision that was true at cutoff."""
    if invoice is None:
        return "not_generated"
    generated_at = getattr(invoice, "generated_at", None)
    if generated_at is not None and generated_at.date() > cutoff:
        return "not_generated"
    issued_at = getattr(invoice, "issued_at", None)
    if issued_at is None or issued_at.date() > cutoff:
        return "draft"
    return "issued"

def _latest_prefetched_balance(account):
    candidates = []
    for rows, id_field in (
        (account.mis_repayment_entries, "repayment_ledger_entry_id"),
        (account.mis_reversal_entries, "repayment_reversal_ledger_entry_id"),
        (account.mis_capitalisation_entries, "interest_capitalisation_ledger_entry_id"),
    ):
        if rows:
            row = rows[0]
            candidates.append(
                (
                    row.transaction_date,
                    row.created_at,
                    str(getattr(row, id_field)),
                    row.principal_balance,
                    row.interest_balance,
                )
            )
    if not candidates:
        return None
    chosen = max(candidates, key=lambda item: item[:3])
    return {"principal": chosen[3], "interest": chosen[4]}

def _snapshot_accounts(*, actor, period):
    cutoff = period["as_of_date"]
    newest = ("-transaction_date", "-created_at")
    return (
        scoped_account_candidates(actor=actor)
        .select_related("loan_application__crop_plan", "member", "terms")
        .prefetch_related(
            Prefetch(
                "disbursements",
                queryset=Disbursement.objects.filter(
                    disbursed_at__date__lte=cutoff,
                    bank_transfer_status="successful",
                ).order_by("-disbursed_at", "-disbursement_id"),
                to_attr="mis_disbursements",
            ),
            Prefetch(
                "status_history",
                queryset=LoanStatusHistory.objects.filter(changed_at__date__lte=cutoff).order_by(
                    "-changed_at", "-loan_status_history_id"
                ),
                to_attr="mis_status_history",
            ),
            Prefetch(
                "dpd_statuses",
                queryset=DpdStatus.objects.filter(as_of_date=cutoff).order_by(
                    "-created_at", "-dpd_status_id"
                ),
                to_attr="mis_dpd_statuses",
            ),
            Prefetch(
                "repayment_ledger_entries",
                queryset=RepaymentLedgerEntry.objects.filter(
                    transaction_date__lte=cutoff
                ).order_by(*newest, "-repayment_ledger_entry_id"),
                to_attr="mis_repayment_entries",
            ),
            Prefetch(
                "repayment_reversal_ledger_entries",
                queryset=RepaymentReversalLedgerEntry.objects.filter(
                    transaction_date__lte=cutoff
                ).order_by(*newest, "-repayment_reversal_ledger_entry_id"),
                to_attr="mis_reversal_entries",
            ),
            Prefetch(
                "interest_capitalisation_ledger_entries",
                queryset=InterestCapitalisationLedgerEntry.objects.filter(
                    transaction_date__lte=cutoff
                ).order_by(*newest, "-interest_capitalisation_ledger_entry_id"),
                to_attr="mis_capitalisation_entries",
            ),
            Prefetch(
                "reminders",
                queryset=Reminder.objects.filter(
                    quarter_end_date__lte=cutoff, created_at__date__lte=cutoff
                ).order_by("reminder_id"),
                to_attr="mis_reminders",
            ),
            Prefetch(
                "interest_invoices",
                queryset=InterestInvoice.objects.filter(
                    invoice_date__lte=cutoff,
                    generated_at__date__lte=cutoff,
                ).order_by("-generated_at", "-interest_invoice_id"),
                to_attr="mis_interest_invoices",
            ),
        )
        .order_by("loan_account_id")
    )

def _totals(rows):
    bucket_counts = {"current": 0, "one_to_two_years": 0, "two_to_three_years": 0, "more_than_three_years": 0}
    for row in rows:
        bucket_counts[row["dpd_bucket"]] = bucket_counts.get(row["dpd_bucket"], 0) + 1
    return {
        "active_loans_count": len(rows),
        "sanctioned_amount": _sum_money(rows, "sanctioned_amount"),
        "disbursed_amount": _sum_money(rows, "disbursed_amount"),
        "principal_outstanding_amount": _sum_money(rows, "principal_outstanding_amount"),
        "interest_outstanding_amount": _sum_money(rows, "interest_outstanding_amount"),
        "overdue_amount": _sum_money(rows, "overdue_amount"),
        "repayments_received_in_quarter": _sum_money(rows, "repayments_received_in_quarter"),
        "loans_overdue_beyond_one_year_count": sum(row["dpd_bucket"] != "current" for row in rows),
        "reminders_count": sum(row["reminder_count"] for row in rows),
        "dpd_bucket_counts": bucket_counts,
        "dimension_summaries": {
            field: _dimension_summary(rows, field)
            for field in (
                "crop",
                "region",
                "borrower_type",
                "dpd_bucket",
                "security_type",
            )
        },
    }

def _dimension_summary(rows, field):
    grouped = {}
    for row in rows:
        label = row[field] or "unavailable"
        aggregate = grouped.setdefault(
            label,
            {
                "loan_count": 0,
                "sanctioned_amount": Decimal("0.00"),
                "principal_outstanding_amount": Decimal("0.00"),
            },
        )
        aggregate["loan_count"] += 1
        aggregate["sanctioned_amount"] += Decimal(row["sanctioned_amount"])
        aggregate["principal_outstanding_amount"] += Decimal(
            row["principal_outstanding_amount"]
        )
    return {
        label: {
            "loan_count": value["loan_count"],
            "sanctioned_amount": _money(value["sanctioned_amount"]),
            "principal_outstanding_amount": _money(
                value["principal_outstanding_amount"]
            ),
        }
        for label, value in sorted(grouped.items())
    }

def _flatten_source_ids(rows, field):
    return [value for row in rows for value in row["source_ids"][field]]

def serialize_report(report):
    snapshot = report.portfolio_snapshot
    return {
        "quarterly_mis_report_id": str(report.pk),
        "portfolio_snapshot_id": str(snapshot.pk),
        "financial_year": report.financial_year,
        "quarter": report.quarter,
        "as_of_date": report.as_of_date.isoformat(),
        "revision": report.revision,
        "status": report.status,
        "totals": snapshot.totals_json,
        "availability": snapshot.availability_json,
        "generated_at": report.generated_at.isoformat().replace("+00:00", "Z"),
        "submitted_at": report.submitted_at.isoformat().replace("+00:00", "Z") if report.submitted_at else None,
        "reviewed_at": report.reviewed_at.isoformat().replace("+00:00", "Z") if report.reviewed_at else None,
        "report_document_id": (
            str(report.report_document_id) if report.report_document_id else None
        ),
        "excel_document_id": (
            str(report.excel_document_id) if report.excel_document_id else None
        ),
    }

def _validate_period(payload):
    errors = {}
    expected = {"financial_year", "quarter", "as_of_date"}
    for field in sorted(set(payload) - expected):
        errors[field] = "Unknown field."
    financial_year = str(payload.get("financial_year", "")).strip()
    quarter = str(payload.get("quarter", "")).strip().upper()
    raw_date = str(payload.get("as_of_date", "")).strip()
    match = FY_PATTERN.fullmatch(financial_year)
    if not match or int(match.group("end")) != (int(match.group("start")) + 1) % 100:
        errors["financial_year"] = "Use FY2026-27 format with consecutive years."
    if quarter not in QUARTER_BOUNDARIES:
        errors["quarter"] = "Must be Q1, Q2, Q3, or Q4."
    try:
        as_of_date = date.fromisoformat(raw_date)
    except ValueError:
        as_of_date = None
        errors["as_of_date"] = "Use YYYY-MM-DD format."
    if not errors:
        start_year = int(match.group("start"))
        start_month_day, end_month_day = QUARTER_BOUNDARIES[quarter]
        period_start_year = start_year if quarter != "Q4" else start_year + 1
        expected_end_year = start_year if quarter in {"Q1", "Q2", "Q3"} else start_year + 1
        period_start = date(period_start_year, *start_month_day)
        expected_end = date(expected_end_year, *end_month_day)
        if as_of_date != expected_end:
            errors["as_of_date"] = f"Must equal the {quarter} quarter end {expected_end.isoformat()}."
    if errors:
        raise QuarterlyMisValidation(errors)
    return {
        "financial_year": financial_year,
        "quarter": quarter,
        "as_of_date": as_of_date,
        "period_start": period_start,
    }

def _require_permission(actor, code):
    if not actor.can_authenticate() or code not in set(auth_service.effective_permission_codes(actor)):
        raise QuarterlyMisPermissionDenied

def _idempotency_digest(value):
    value = str(value or "").strip()
    if not value or len(value) > 200:
        raise QuarterlyMisValidation(
            {"idempotency_key": "Provide a nonblank Idempotency-Key up to 200 characters."}
        )
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def _payload_digest(payload):
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def _money(value):
    return format(Decimal(value).quantize(MONEY), ".2f")

def _sum_money(rows, field):
    return _money(sum((Decimal(row[field]) for row in rows), Decimal("0.00")))
