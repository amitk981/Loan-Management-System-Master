"""Permission-scoped exports over canonical immutable loan-ledger reads."""

import csv
import hashlib
import io
import json
from dataclasses import dataclass
from datetime import date, timedelta

from django.core import signing
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from django.utils import timezone

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.models import PortalAccount
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.models import LoanAccount
from sfpcl_credit.disbursements.modules.post_transfer_evidence import (
    resolve_historical_post_transfer_evidence,
)
from sfpcl_credit.processes.loan_servicing import get_ledger, get_ledger_for_scoped_account
from sfpcl_credit.scheduler.models import ScheduledJob
from sfpcl_credit.scheduler.services import (
    enqueue_scheduled_job,
    mark_job_running,
    mark_job_succeeded,
)


EXPORT_PERMISSION = "reports.export"
FORMAT_CSV = "csv"
MIME_CSV = "text/csv; charset=utf-8"
REQUESTED_ACTION = "loans.ledger_statement.requested"
GENERATED_ACTION = "loans.ledger_statement.generated"
DOWNLOAD_ACTION = "loans.ledger_statement.downloaded"
_CAPABILITY_SALT = "sfpcl.loan-ledger-statement.v1"
_CAPABILITY_TTL_SECONDS = 15 * 60


class LoanLedgerStatementDenied(Exception):
    pass


class LoanLedgerStatementNotFound(Exception):
    pass


class LoanLedgerStatementValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


@dataclass(frozen=True)
class StatementContent:
    body: bytes
    file_name: str
    mime_type: str = MIME_CSV


@transaction.atomic
def request_statement(*, actor, loan_account_id, payload, idempotency_key, request):
    cleaned = _validate_request(payload, idempotency_key)
    _require_export_permission(actor)
    all_rows = _canonical_rows(actor=actor, loan_account_id=loan_account_id)
    digest = hashlib.sha256(
        f"{actor.pk}:{loan_account_id}:{cleaned['idempotency_key']}".encode("utf-8")
    ).hexdigest()
    scheduler_key = f"loan-ledger-statement:{digest}"
    request_digest = hashlib.sha256(
        json.dumps(
            {
                "format": cleaned["format"],
                "from_date": cleaned["from_date"].isoformat(),
                "to_date": cleaned["to_date"].isoformat(),
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    existing = ScheduledJob.objects.filter(idempotency_key=scheduler_key).first()
    if existing is not None:
        requested = AuditLog.objects.filter(
            action=REQUESTED_ACTION,
            entity_type="scheduled_job",
            entity_id=existing.pk,
        ).first()
        if (requested.new_value_json or {}).get("request_digest") != request_digest:
            raise LoanLedgerStatementValidation(
                {"Idempotency-Key": "This key was already used with a different request."}
            )
        return _serialize(job=existing, generated=_generated_audit(existing.pk))
    job, _ = enqueue_scheduled_job(
        job_type="report_export",
        due_at=timezone.now(),
        idempotency_key=scheduler_key,
        related_entity_type="loan_account",
        related_entity_id=loan_account_id,
    )
    mark_job_running(job.pk)
    generated_at = timezone.now()
    statement = _statement_projection(
        rows=all_rows,
        from_date=cleaned["from_date"],
        to_date=cleaned["to_date"],
        generated_at=generated_at,
        job_id=job.pk,
        loan_account_id=loan_account_id,
    )
    body = _render_csv(statement)
    stored = LocalDocumentStorage().store(
        SimpleUploadedFile(
            f"loan-ledger-{loan_account_id}.csv",
            body,
            content_type=MIME_CSV,
        )
    )
    document = DocumentFile.objects.create(
        file_name=f"loan-ledger-{loan_account_id}.csv",
        file_extension=".csv",
        mime_type=MIME_CSV,
        file_size_bytes=stored.file_size_bytes,
        storage_provider=stored.storage_provider,
        storage_key=stored.storage_key,
        checksum_sha256=stored.checksum_sha256,
        uploaded_by_user=actor,
        sensitivity_level=DocumentFile.SENSITIVITY_CONFIDENTIAL,
    )
    _audit(
        actor=actor,
        request=request,
        action=REQUESTED_ACTION,
        job=job,
        metadata={
            "loan_account_id": str(loan_account_id),
            "format": FORMAT_CSV,
            "from_date": cleaned["from_date"].isoformat(),
            "to_date": cleaned["to_date"].isoformat(),
            "request_digest": request_digest,
        },
    )
    _audit(
        actor=actor,
        request=request,
        action=GENERATED_ACTION,
        job=job,
        metadata={
            "loan_account_id": str(loan_account_id),
            "document_id": str(document.pk),
            "checksum_sha256": document.checksum_sha256,
            "format": FORMAT_CSV,
            "row_count": statement["row_count"],
            "opening_balance": statement["opening_balance"],
            "closing_balance": statement["closing_balance"],
            "generated_at": _iso(generated_at),
        },
    )
    job = mark_job_succeeded(job.pk)
    return _serialize(job=job, generated=_generated_audit(job.pk))


@transaction.atomic
def statement_status(*, actor, statement_job_id):
    job, generated = _scoped_job(actor=actor, statement_job_id=statement_job_id)
    job.save(update_fields=["updated_at"])
    job.refresh_from_db()
    claims = _capability_claims(actor=actor, job=job, generated=generated)
    token = signing.dumps(claims, salt=_CAPABILITY_SALT, compress=True)
    data = _serialize(job=job, generated=generated)
    data.update(
        {
            "download_url": (
                f"/api/v1/loan-ledger-statements/{job.pk}/download/"
                f"?capability={token}"
            ),
            "expires_at": _iso(
                timezone.now() + timedelta(seconds=_CAPABILITY_TTL_SECONDS)
            ),
        }
    )
    return data


def download_statement(*, actor, statement_job_id, capability, request):
    try:
        claims = signing.loads(
            capability,
            salt=_CAPABILITY_SALT,
            max_age=_CAPABILITY_TTL_SECONDS,
        )
    except (signing.BadSignature, signing.SignatureExpired) as exc:
        raise LoanLedgerStatementNotFound from exc
    job, generated = _scoped_job(actor=actor, statement_job_id=statement_job_id)
    if claims != _capability_claims(actor=actor, job=job, generated=generated):
        raise LoanLedgerStatementNotFound
    document = DocumentFile.objects.filter(
        pk=generated["document_id"],
        checksum_sha256=generated["checksum_sha256"],
    ).first()
    if document is None:
        raise LoanLedgerStatementNotFound
    try:
        body = LocalDocumentStorage().read_verified(document)
    except (OSError, ValueError) as exc:
        raise LoanLedgerStatementNotFound from exc
    _audit(
        actor=actor,
        request=request,
        action=DOWNLOAD_ACTION,
        job=job,
        metadata={
            "loan_account_id": str(job.related_entity_id),
            "document_id": str(document.pk),
            "checksum_sha256": document.checksum_sha256,
            "outcome": "accepted",
        },
    )
    return StatementContent(body=body, file_name=document.file_name)


def record_download_denial(*, actor, statement_job_id, request):
    """Retain a nondisclosing denial without echoing a capability or statement data."""
    return AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=DOWNLOAD_ACTION,
        entity_type="scheduled_job",
        entity_id=statement_job_id,
        old_value_json=None,
        new_value_json={
            "statement_job_id": str(statement_job_id),
            "request_id": request.headers.get("X-Request-ID"),
            "outcome": "denied",
        },
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )


def _validate_request(payload, idempotency_key):
    errors = {}
    if set(payload) - {"format", "from_date", "to_date"}:
        for field in sorted(set(payload) - {"format", "from_date", "to_date"}):
            errors[field] = "Unknown field."
    statement_format = str(payload.get("format") or "").strip().lower()
    if statement_format != FORMAT_CSV:
        errors["format"] = "Must be csv."
    from_date = _date_field("from_date", payload.get("from_date"), errors)
    to_date = _date_field("to_date", payload.get("to_date"), errors)
    if from_date and to_date and from_date > to_date:
        errors["to_date"] = "Must be on or after from_date."
    cleaned_key = str(idempotency_key or "").strip()
    if not cleaned_key or len(cleaned_key) > 200:
        errors["Idempotency-Key"] = "A nonblank value of at most 200 characters is required."
    if errors:
        raise LoanLedgerStatementValidation(errors)
    return {
        "format": statement_format,
        "from_date": from_date,
        "to_date": to_date,
        "idempotency_key": cleaned_key,
    }


def _date_field(name, value, errors):
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        errors[name] = "Must be a valid ISO date."
        return None


def _require_export_permission(actor):
    permissions = set(auth_service.effective_permission_codes(actor))
    portal = PortalAccount.objects.filter(
        user=actor, status=PortalAccount.STATUS_ACTIVE, member__is_deleted=False
    ).exists()
    required = {EXPORT_PERMISSION, "portal.loan_account.read_own"} if portal else {EXPORT_PERMISSION}
    if not required.issubset(permissions):
        raise LoanLedgerStatementDenied


def _canonical_rows(*, actor, loan_account_id):
    portal = PortalAccount.objects.filter(
        user=actor, status=PortalAccount.STATUS_ACTIVE, member__is_deleted=False
    ).first()
    projection = get_ledger
    base = {"actor": actor, "loan_account_id": loan_account_id}
    if portal is not None:
        account = LoanAccount.objects.filter(pk=loan_account_id, member_id=portal.member_id).first()
        transfer = (
            resolve_historical_post_transfer_evidence(application_id=account.loan_application_id)
            if account is not None
            else None
        )
        if account is None or transfer is None or transfer.loan_account_id != account.pk:
            raise LoanLedgerStatementNotFound
        projection = get_ledger_for_scoped_account
        base = {"account": account, "transfer": transfer}
    rows, pagination = projection(
        **base, query_params={"page": "1", "page_size": "100"}
    )
    for page in range(2, pagination["total_pages"] + 1):
        page_rows, _ = projection(
            **base, query_params={"page": str(page), "page_size": "100"}
        )
        rows.extend(page_rows)
    return rows


def _statement_projection(*, rows, from_date, to_date, generated_at, job_id, loan_account_id):
    before = [row for row in rows if date.fromisoformat(row["transaction_date"]) < from_date]
    selected = [
        row
        for row in rows
        if from_date <= date.fromisoformat(row["transaction_date"]) <= to_date
    ]
    through_end = [
        row for row in rows if date.fromisoformat(row["transaction_date"]) <= to_date
    ]
    opening = before[-1]["total_outstanding"] if before else "0.00"
    closing = through_end[-1]["total_outstanding"] if through_end else "0.00"
    return {
        "statement_job_id": str(job_id),
        "loan_account_id": str(loan_account_id),
        "format": FORMAT_CSV,
        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat(),
        "as_of_date": to_date.isoformat(),
        "generated_at": _iso(generated_at),
        "opening_balance": opening,
        "closing_balance": closing,
        "row_count": len(selected),
        "rows": selected,
    }


def _render_csv(statement):
    fieldnames = [
        "statement_job_id", "loan_account_id", "from_date", "to_date",
        "as_of_date", "generated_at", "opening_balance", "closing_balance",
        "transaction_date", "transaction_type", "owner_reference", "reference",
        "debit", "credit", "principal_balance", "interest_balance",
        "total_outstanding", "posted_by", "sap_status", "remarks",
    ]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    common = {key: statement[key] for key in fieldnames[:8]}
    for row in statement["rows"]:
        writer.writerow(
            {
                **common,
                "transaction_date": row["transaction_date"],
                "transaction_type": row["transaction_type"],
                "owner_reference": json.dumps(row["owner_reference"], sort_keys=True),
                "reference": _mask_reference(row["reference"]),
                "debit": row["debit"],
                "credit": row["credit"],
                "principal_balance": row["principal_balance"],
                "interest_balance": row["interest_balance"],
                "total_outstanding": row["total_outstanding"],
                "posted_by": row["actor"]["display_name"],
                "sap_status": row["sap_status"],
                "remarks": row["remarks"],
            }
        )
    return output.getvalue().encode("utf-8")


def _mask_reference(value):
    cleaned = str(value or "")
    if len(cleaned) <= 4:
        return "*" * len(cleaned)
    return f"{'*' * (len(cleaned) - 4)}{cleaned[-4:]}"


def _scoped_job(*, actor, statement_job_id):
    _require_export_permission(actor)
    job = ScheduledJob.objects.filter(
        pk=statement_job_id,
        job_type="report_export",
        related_entity_type="loan_account",
        status=ScheduledJob.STATUS_SUCCEEDED,
    ).first()
    if job is None:
        raise LoanLedgerStatementNotFound
    requested = AuditLog.objects.filter(
        action=REQUESTED_ACTION,
        entity_type="scheduled_job",
        entity_id=job.pk,
        actor_user=actor,
    ).first()
    if requested is None:
        raise LoanLedgerStatementNotFound
    _canonical_rows(actor=actor, loan_account_id=job.related_entity_id)
    return job, _generated_audit(job.pk)


def _generated_audit(job_id):
    audit = AuditLog.objects.filter(
        action=GENERATED_ACTION,
        entity_type="scheduled_job",
        entity_id=job_id,
    ).first()
    if audit is None:
        raise LoanLedgerStatementNotFound
    return audit.new_value_json or {}


def _serialize(*, job, generated):
    return {
        "statement_job_id": str(job.pk),
        "loan_account_id": str(job.related_entity_id),
        "status": job.status,
        "format": generated["format"],
        "row_count": generated["row_count"],
        "opening_balance": generated["opening_balance"],
        "closing_balance": generated["closing_balance"],
        "checksum_sha256": generated["checksum_sha256"],
        "generated_at": generated["generated_at"],
    }


def _capability_claims(*, actor, job, generated):
    return {
        "actor_user_id": str(actor.pk),
        "statement_job_id": str(job.pk),
        "loan_account_id": str(job.related_entity_id),
        "document_id": generated["document_id"],
        "checksum_sha256": generated["checksum_sha256"],
        "version": _iso(job.updated_at),
    }


def _audit(*, actor, request, action, job, metadata):
    return AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=action,
        entity_type="scheduled_job",
        entity_id=job.pk,
        old_value_json=None,
        new_value_json={
            "statement_job_id": str(job.pk),
            "request_id": request.headers.get("X-Request-ID"),
            **metadata,
        },
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )


def _iso(value):
    return value.isoformat().replace("+00:00", "Z")


__all__ = [
    "LoanLedgerStatementDenied",
    "LoanLedgerStatementNotFound",
    "LoanLedgerStatementValidation",
    "StatementContent",
    "download_statement",
    "request_statement",
    "record_download_denial",
    "statement_status",
]
