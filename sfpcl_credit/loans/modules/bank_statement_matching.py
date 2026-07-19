import csv
import hashlib
import io
import json
import unicodedata
import uuid
from decimal import Decimal, InvalidOperation
from math import ceil

from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.dateparse import parse_date

from sfpcl_credit.api import request_ip, request_user_agent
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.loans.models import (
    BankStatementImport,
    BankStatementLine,
    Repayment,
)


READ_PERMISSION = "finance.bank_statement.read"
IMPORT_PERMISSION = "finance.bank_statement.import"
MATCH_PERMISSION = "finance.bank_statement.match"
FINANCE_ROLES = {"credit_manager", "accounts_head", "senior_manager_finance"}
MAX_FILE_BYTES = 1_000_000
MAX_LINES = 500
REQUIRED_COLUMNS = {
    "transaction_date",
    "value_date",
    "amount",
    "narration",
    "reference",
    "loan_account_number",
}


class BankStatementValidation(Exception):
    def __init__(self, field_errors):
        self.field_errors = field_errors


class BankStatementPermissionDenied(Exception):
    pass


class BankStatementConflict(Exception):
    pass


class BankStatementNotFound(Exception):
    pass


def import_statement(*, actor, request):
    _require_authority(actor, IMPORT_PERMISSION)
    cleaned = _validate_upload(request, actor)
    retained = BankStatementImport.objects.filter(
        idempotency_key_digest=cleaned["idempotency_key_digest"]
    ).first()
    if retained is not None:
        if retained.payload_digest == cleaned["payload_digest"]:
            return _serialize_import(retained, replayed=True)
        raise BankStatementConflict(
            "The idempotency key was already used for a different statement import."
        )
    retained = BankStatementImport.objects.filter(
        sfpcl_bank_account=cleaned["sfpcl_bank_account"],
        source_checksum_sha256=cleaned["checksum"],
    ).first()
    if retained is not None:
        return _serialize_import(retained, replayed=True)
    try:
        return _create_import(actor=actor, request=request, cleaned=cleaned)
    except IntegrityError as exc:
        retained = BankStatementImport.objects.filter(
            idempotency_key_digest=cleaned["idempotency_key_digest"]
        ).first()
        if retained is not None and retained.payload_digest == cleaned["payload_digest"]:
            return _serialize_import(retained, replayed=True)
        retained = BankStatementImport.objects.filter(
            sfpcl_bank_account=cleaned["sfpcl_bank_account"],
            source_checksum_sha256=cleaned["checksum"],
        ).first()
        if retained is not None:
            return _serialize_import(retained, replayed=True)
        raise BankStatementConflict(
            "The statement import conflicts with retained evidence."
        ) from exc


def list_statement_lines(*, actor, query_params):
    _require_authority(actor, READ_PERMISSION)
    unknown = set(query_params) - {"match_status", "page", "page_size"}
    errors = {key: "Unknown query parameter." for key in sorted(unknown)}
    match_status = str(query_params.get("match_status", "")).strip()
    if match_status and match_status not in {"unmatched", "matched", "exception"}:
        errors["match_status"] = "Must be unmatched, matched, or exception."
    page = _positive_int("page", query_params.get("page"), default=1, maximum=None)
    page_size = _positive_int(
        "page_size", query_params.get("page_size"), default=20, maximum=100
    )
    if errors:
        raise BankStatementValidation(errors)
    rows = BankStatementLine.objects.select_related("matched_repayment").order_by(
        "created_at", "bank_statement_line_id"
    )
    if match_status:
        rows = rows.filter(match_status=match_status)
    total_count = rows.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    if page > total_pages:
        raise BankStatementValidation({"page": "Page is out of range."})
    window = rows[(page - 1) * page_size : page * page_size]
    return [_serialize_line(line) for line in window], {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def manual_match_statement_line(*, actor, line_id, payload, request=None):
    _require_authority(actor, MATCH_PERMISSION)
    cleaned = _validate_manual_match(payload)
    return _manual_match_statement_line(
        actor=actor,
        line_id=line_id,
        cleaned=cleaned,
        request=request,
    )


@transaction.atomic
def record_statement_exception(*, actor, line_id, payload, request=None):
    _require_authority(actor, MATCH_PERMISSION)
    cleaned = _validate_exception(payload)
    line = BankStatementLine.objects.select_for_update().filter(pk=line_id).first()
    if line is None:
        raise BankStatementNotFound
    if line.match_status == "matched":
        raise BankStatementConflict("A matched statement line cannot be marked exceptional.")
    if line.match_status == "exception" and line.match_reason_code == cleaned["reason_code"]:
        return _serialize_line(line)
    if line.match_status == "exception":
        raise BankStatementConflict("The statement line already has a retained exception decision.")
    decided_at = timezone.now()
    evidence = {
        "bank_statement_line_id": str(line.pk),
        "bank_statement_import_id": str(line.statement_import_id),
        "actor_user_id": str(actor.pk),
        "actor_role_codes": auth_service.effective_role_codes(actor),
        "match_reason_code": cleaned["reason_code"],
        "decided_at": decided_at.isoformat().replace("+00:00", "Z"),
        "request_id": request.headers.get("X-Request-ID", "") if request else "",
    }
    manifest = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action="bank_statement.line_exception_recorded",
        entity_type="bank_statement_line",
        entity_id=line.pk,
        old_value_json=None,
        new_value_json=evidence,
        selector_manifest_json=manifest,
        selector_manifest_sha256=hashlib.sha256(manifest.encode()).hexdigest(),
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )
    line.match_status = "exception"
    line.match_reason_code = cleaned["reason_code"]
    line.matched_by_user = actor
    line.match_decision_reason = cleaned["reason"]
    line.save(
        update_fields=[
            "match_status",
            "match_reason_code",
            "matched_by_user",
            "match_decision_reason",
        ]
    )
    return _serialize_line(line)


@transaction.atomic
def _manual_match_statement_line(*, actor, line_id, cleaned, request):
    line = (
        BankStatementLine.objects.select_for_update(of=("self",))
        .select_related("matched_repayment")
        .filter(pk=line_id)
        .first()
    )
    if line is None:
        raise BankStatementNotFound
    repayment = (
        Repayment.objects.select_for_update()
        .select_related(
            "loan_account",
            "loan_account__loan_application",
            "loan_account__member",
        )
        .filter(pk=cleaned["repayment_id"])
        .first()
    )
    if repayment is None or not _repayment_in_scope(actor, repayment):
        raise BankStatementNotFound
    if line.matched_repayment_id == repayment.pk:
        return _serialize_line(line)
    if line.matched_repayment_id is not None:
        raise BankStatementConflict("The statement line is already matched.")
    if repayment.bank_statement_line_id is not None:
        raise BankStatementConflict("The repayment is already matched to another statement line.")
    _match(
        line=line,
        repayment=repayment,
        actor=actor,
        reason_code="authorised_manual_evidence_match",
        decision_reason=cleaned["reason"],
        action="bank_statement.line_manually_matched",
        receipt_statement_status="manual_match_exception",
        request=request,
    )
    line.refresh_from_db()
    return _serialize_line(line)


@transaction.atomic
def _create_import(*, actor, request, cleaned):
    document = document_services.store_document_upload(
        user=actor,
        request=request,
        uploaded_file=cleaned["file"],
        document_category="finance",
        sensitivity_level="restricted",
        audit_spec=document_services.DocumentAuditSpec(
            action="bank_statement.file_stored",
            actor_type="user",
            metadata={
                "workflow_scope": "bank_statement_reconciliation",
                "sensitivity_level": "restricted",
            },
        ),
    )
    statement_import = BankStatementImport.objects.create(
        source_document=document,
        sfpcl_bank_account=cleaned["sfpcl_bank_account"],
        source_checksum_sha256=cleaned["checksum"],
        idempotency_key_digest=cleaned["idempotency_key_digest"],
        payload_digest=cleaned["payload_digest"],
        imported_by_user=actor,
    )
    has_exception = False
    for line_number, row in enumerate(cleaned["rows"], start=1):
        line = _create_line(statement_import, line_number, row)
        if line.parse_status == "parsed":
            _attempt_exact_match(line=line, actor=actor, request=request)
            line.refresh_from_db()
        has_exception = has_exception or line.match_status == "exception"
    if has_exception:
        statement_import.import_status = "parsed_with_exceptions"
        statement_import.save(update_fields=["import_status"])
    counts = {
        status: statement_import.lines.filter(match_status=status).count()
        for status in ("matched", "unmatched", "exception")
    }
    evidence = {
        "bank_statement_import_id": str(statement_import.pk),
        "source_document_id": str(document.pk),
        "actor_user_id": str(actor.pk),
        "actor_role_codes": auth_service.effective_role_codes(actor),
        "line_count": statement_import.lines.count(),
        "matched_count": counts["matched"],
        "unmatched_count": counts["unmatched"],
        "exception_count": counts["exception"],
        "import_status": statement_import.import_status,
        "request_id": request.headers.get("X-Request-ID", ""),
    }
    manifest = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action="bank_statement.imported",
        entity_type="bank_statement_import",
        entity_id=statement_import.pk,
        old_value_json=None,
        new_value_json=evidence,
        selector_manifest_json=manifest,
        selector_manifest_sha256=hashlib.sha256(manifest.encode()).hexdigest(),
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )
    return _serialize_import(statement_import)


def _create_line(statement_import, line_number, row):
    raw_reference = str(row.get("reference") or "").strip()
    raw_narration = str(row.get("narration") or "").strip()
    raw_account_reference = str(row.get("loan_account_number") or "").strip()
    reference = _bounded(raw_reference, 120)
    narration = _bounded(raw_narration, 500)
    account_reference = _bounded(raw_account_reference, 120)
    transaction_date = parse_date(str(row.get("transaction_date", "")).strip())
    value_date = parse_date(str(row.get("value_date", "")).strip())
    try:
        amount = Decimal(str(row.get("amount", "")).strip())
        if (
            not amount.is_finite()
            or amount <= 0
            or amount.as_tuple().exponent < -2
            or len(amount.as_tuple().digits) > 18
        ):
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        amount = None
    parse_failed = (
        transaction_date is None
        or value_date is None
        or amount is None
        or len(raw_reference) > 120
        or len(raw_narration) > 500
        or len(raw_account_reference) > 120
    )
    return BankStatementLine.objects.create(
        statement_import=statement_import,
        line_number=line_number,
        transaction_date=transaction_date,
        value_date=value_date,
        amount=amount,
        narration=narration,
        reference=reference,
        reference_normalized=_normalize(reference),
        loan_account_reference=account_reference,
        parse_status="parse_failed" if parse_failed else "parsed",
        match_status="exception" if parse_failed else "unmatched",
        match_reason_code="parse_failed" if parse_failed else "candidate_pending",
    )


def _attempt_exact_match(*, line, actor, request):
    if not line.reference_normalized:
        _set_unmatched(line, "missing_reference")
        return
    if not line.loan_account_reference:
        _set_unmatched(line, "missing_loan_reference")
        return
    candidates = list(
        Repayment.objects.select_for_update()
        .select_related("loan_account")
        .filter(
            bank_reference_number_normalized=line.reference_normalized,
            amount_received=line.amount,
            received_date=line.transaction_date,
            loan_account__loan_account_number_normalized=_normalize_account(
                line.loan_account_reference
            ),
        )[:2]
    )
    if not candidates:
        _set_unmatched(line, "no_exact_receipt_candidate")
        return
    if len(candidates) != 1:
        _set_exception(line, "ambiguous_receipt_candidates")
        return
    repayment = candidates[0]
    if not _narration_supports_candidate(line.narration, repayment):
        _set_unmatched(line, "missing_borrower_or_application_narration")
        return
    if repayment.bank_statement_line_id is not None:
        _set_exception(line, "counterpart_already_matched")
        return
    _match(
        line=line,
        repayment=repayment,
        actor=actor,
        reason_code="exact_reference_amount_date_account",
        decision_reason="Automatic exact evidence match.",
        action="bank_statement.line_auto_matched",
        receipt_statement_status="matched_exact",
        request=request,
    )


def _match(
    *,
    line,
    repayment,
    actor,
    reason_code,
    decision_reason,
    action,
    receipt_statement_status,
    request,
):
    matched_at = timezone.now()
    evidence = {
        "bank_statement_line_id": str(line.pk),
        "bank_statement_import_id": str(line.statement_import_id),
        "repayment_id": str(repayment.pk),
        "loan_account_id": str(repayment.loan_account_id),
        "actor_user_id": str(actor.pk),
        "actor_role_codes": auth_service.effective_role_codes(actor),
        "match_reason_code": reason_code,
        "matched_at": matched_at.isoformat().replace("+00:00", "Z"),
        "request_id": request.headers.get("X-Request-ID", "") if request else "",
    }
    manifest = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
    audit = AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=action,
        entity_type="bank_statement_line",
        entity_id=line.pk,
        old_value_json=None,
        new_value_json=evidence,
        selector_manifest_json=manifest,
        selector_manifest_sha256=hashlib.sha256(manifest.encode()).hexdigest(),
        ip_address=request_ip(request) if request else "",
        user_agent=request_user_agent(request) if request else "",
    )
    line.match_status = "matched"
    line.match_reason_code = reason_code
    line.matched_repayment = repayment
    line.matched_by_user = actor
    line.match_decision_reason = decision_reason
    line.match_audit = audit
    line.matched_at = matched_at
    line.save(
        update_fields=[
            "match_status",
            "match_reason_code",
            "matched_repayment",
            "matched_by_user",
            "match_decision_reason",
            "match_audit",
            "matched_at",
        ]
    )
    repayment.bank_statement_line_id = line.pk
    repayment.statement_match_status = receipt_statement_status
    repayment.save(update_fields=["bank_statement_line_id", "statement_match_status"])


def _set_unmatched(line, reason_code):
    line.match_status = "unmatched"
    line.match_reason_code = reason_code
    line.save(update_fields=["match_status", "match_reason_code"])


def _set_exception(line, reason_code):
    line.match_status = "exception"
    line.match_reason_code = reason_code
    line.save(update_fields=["match_status", "match_reason_code"])


def _validate_upload(request, actor):
    errors = {}
    for name in sorted(set(request.POST) - {"sfpcl_bank_account"}):
        errors[name] = "Unknown field."
    for name in sorted(set(request.FILES) - {"file"}):
        errors[name] = "Unknown field."
    uploaded_file = request.FILES.get("file")
    bank_account = _normalize(request.POST.get("sfpcl_bank_account", ""))
    key = str(request.headers.get("Idempotency-Key", "")).strip()
    if not bank_account or len(bank_account) > 120:
        errors["sfpcl_bank_account"] = "Must be nonblank and at most 120 characters."
    if not key or len(key) > 255:
        errors["idempotency_key"] = "Must be nonblank and at most 255 characters."
    if uploaded_file is None:
        errors["file"] = "A CSV statement file is required."
    elif (
        not uploaded_file.name.lower().endswith(".csv")
        or uploaded_file.content_type not in {"text/csv", "application/csv", "text/plain"}
        or uploaded_file.size <= 0
        or uploaded_file.size > MAX_FILE_BYTES
    ):
        errors["file"] = "Must be a non-empty CSV file of at most 1000000 bytes."
    if errors:
        raise BankStatementValidation(errors)
    content = uploaded_file.read()
    uploaded_file.seek(0)
    try:
        decoded = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(decoded))
        columns = set(reader.fieldnames or ())
        rows = list(reader)
    except (UnicodeDecodeError, csv.Error):
        raise BankStatementValidation({"file": "Must be a valid UTF-8 CSV file."})
    if columns != REQUIRED_COLUMNS:
        raise BankStatementValidation(
            {"file": "CSV columns must exactly match the bank statement template."}
        )
    if not rows or len(rows) > MAX_LINES:
        raise BankStatementValidation(
            {"file": f"CSV must contain between 1 and {MAX_LINES} data lines."}
        )
    if any(None in row for row in rows):
        raise BankStatementValidation(
            {"file": "CSV rows must exactly match the bank statement template."}
        )
    checksum = hashlib.sha256(content).hexdigest()
    key_digest = hashlib.sha256(key.encode()).hexdigest()
    payload_digest = hashlib.sha256(
        json.dumps(
            {
                "actor_id": str(actor.pk),
                "sfpcl_bank_account": bank_account,
                "checksum": checksum,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    return {
        "file": uploaded_file,
        "sfpcl_bank_account": bank_account,
        "rows": rows,
        "checksum": checksum,
        "idempotency_key_digest": key_digest,
        "payload_digest": payload_digest,
    }


def _validate_manual_match(payload):
    allowed = {"repayment_id", "reason"}
    errors = {key: "Unknown field." for key in sorted(set(payload) - allowed)}
    try:
        repayment_id = uuid.UUID(str(payload.get("repayment_id", "")))
    except (TypeError, ValueError, AttributeError):
        repayment_id = None
        errors["repayment_id"] = "Must be a valid repayment UUID."
    reason = str(payload.get("reason", "")).strip()
    if not reason or len(reason) > 500:
        errors["reason"] = "Must be nonblank and at most 500 characters."
    if errors:
        raise BankStatementValidation(errors)
    return {"repayment_id": repayment_id, "reason": reason}


def _validate_exception(payload):
    allowed = {"reason_code", "reason"}
    errors = {key: "Unknown field." for key in sorted(set(payload) - allowed)}
    reason_code = str(payload.get("reason_code", "")).strip()
    if reason_code not in {
        "evidence_conflict",
        "counterpart_not_captured",
        "requires_investigation",
    }:
        errors["reason_code"] = "Must be an allowed reconciliation exception code."
    reason = str(payload.get("reason", "")).strip()
    if not reason or len(reason) > 500:
        errors["reason"] = "Must be nonblank and at most 500 characters."
    if errors:
        raise BankStatementValidation(errors)
    return {"reason_code": reason_code, "reason": reason}


def _serialize_import(statement_import, replayed=False):
    lines = list(statement_import.lines.select_related("matched_repayment").all())
    return {
        "bank_statement_import_id": str(statement_import.pk),
        "source_document_id": str(statement_import.source_document_id),
        "sfpcl_bank_account": statement_import.sfpcl_bank_account,
        "import_status": statement_import.import_status,
        "line_count": len(lines),
        "matched_count": sum(line.match_status == "matched" for line in lines),
        "unmatched_count": sum(line.match_status == "unmatched" for line in lines),
        "exception_count": sum(line.match_status == "exception" for line in lines),
        "idempotency_replayed": replayed,
        "lines": [_serialize_line(line) for line in lines],
    }


def _serialize_line(line):
    repayment = line.matched_repayment if line.matched_repayment_id else None
    return {
        "bank_statement_line_id": str(line.pk),
        "line_number": line.line_number,
        "transaction_date": line.transaction_date.isoformat() if line.transaction_date else None,
        "value_date": line.value_date.isoformat() if line.value_date else None,
        "amount": f"{line.amount:.2f}" if line.amount is not None else None,
        "parse_status": line.parse_status,
        "match_status": line.match_status,
        "match_reason_code": line.match_reason_code,
        "matched_repayment_id": str(line.matched_repayment_id) if line.matched_repayment_id else None,
        "repayment_evidence": (
            {
                "repayment_id": str(repayment.pk),
                "bank_statement_line_id": str(repayment.bank_statement_line_id),
                "statement_match_status": repayment.statement_match_status,
                "allocation_status": repayment.allocation_status,
            }
            if repayment is not None
            else None
        ),
    }


def _require_authority(actor, permission):
    if (
        not actor.can_authenticate()
        or permission not in auth_service.effective_permission_codes(actor)
        or not set(auth_service.effective_role_codes(actor)).intersection(FINANCE_ROLES)
    ):
        raise BankStatementPermissionDenied


def _repayment_in_scope(actor, repayment):
    roles = set(auth_service.effective_role_codes(actor))
    return bool(roles & {"accounts_head", "senior_manager_finance"}) or (
        "credit_manager" in roles
        and repayment.loan_account.loan_account_status
        in {"active", "partially_repaid", "overdue", "grace_period", "extended"}
    )


def _narration_supports_candidate(narration, repayment):
    normalized_narration = _normalize(narration)
    application = repayment.loan_account.loan_application
    member = repayment.loan_account.member
    identifiers = {
        repayment.loan_account.loan_account_number,
        application.application_reference_number,
        member.legal_name,
        member.display_name,
    }
    return any(
        normalized and normalized in normalized_narration
        for normalized in (_normalize(value) for value in identifiers if value)
    )


def _bounded(value, limit):
    return str(value or "").strip()[:limit]


def _normalize(value):
    return " ".join(unicodedata.normalize("NFKC", str(value or "")).split()).upper()


def _normalize_account(value):
    return " ".join(unicodedata.normalize("NFKC", str(value or "")).split()).casefold()


def _positive_int(name, raw, *, default, maximum):
    if raw in (None, ""):
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise BankStatementValidation({name: "Must be a positive integer."}) from exc
    if value < 1 or maximum is not None and value > maximum:
        raise BankStatementValidation(
            {name: f"Must be at most {maximum}." if maximum and value > maximum else "Must be a positive integer."}
        )
    return value


__all__ = [
    "BankStatementConflict",
    "BankStatementPermissionDenied",
    "BankStatementNotFound",
    "BankStatementValidation",
    "import_statement",
    "list_statement_lines",
    "manual_match_statement_line",
    "record_statement_exception",
]
