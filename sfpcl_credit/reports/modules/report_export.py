import hashlib
import csv
import io
import json
import uuid
import zipfile
from xml.sax.saxutils import escape as xml_escape

from django.conf import settings
from django.core import signing
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone
from urllib.parse import urlencode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from sfpcl_credit.api import FORBIDDEN, request_ip, request_user_agent
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.reports.errors import ReportPermissionDenied, ReportValidation
from sfpcl_credit.reports.models import ReportExportJob
from sfpcl_credit.reports.registry import REPORTS, run_report
from sfpcl_credit.reports.storage import LocalReportExportStorage


SUPPORTED_FORMATS = ("csv", "xlsx", "pdf", "json")
FORMAT_MATRIX = {
    code: SUPPORTED_FORMATS
    for code, definition in REPORTS.items()
    if definition.selector is not None
}
CONTENT_TYPES = {
    "csv": "text/csv; charset=utf-8",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pdf": "application/pdf",
    "json": "application/json",
}
_DOWNLOAD_TOKEN_SALT = "sfpcl-report-export-download-v1"


def request_export(*, actor, payload, idempotency_key, request=None):
    try:
        cleaned = _validate_request(
            actor=actor,
            payload=payload,
            idempotency_key=idempotency_key,
        )
    except ReportPermissionDenied:
        report_code = (
            payload.get("report_code")
            if isinstance(payload, dict)
            and isinstance(payload.get("report_code"), str)
            else "unknown"
        )
        AuditLog.objects.create(
            actor_user=actor,
            actor_type="user",
            action="report.export.denied",
            entity_type="report_export_job",
            entity_id=None,
            new_value_json={
                "report_code": report_code,
                "outcome": "denied",
                "reason_code": FORBIDDEN,
            },
            ip_address=request_ip(request) if request is not None else "",
            user_agent=request_user_agent(request) if request is not None else "",
        )
        raise
    identity = {
        "actor": actor,
        "report_code": cleaned["report_code"],
        "filters_digest": cleaned["filters_digest"],
        "export_format": cleaned["format"],
        "idempotency_key": cleaned["idempotency_key"],
    }
    existing = ReportExportJob.objects.filter(**identity).first()
    if existing is not None:
        return existing, True
    try:
        with transaction.atomic():
            job = ReportExportJob.objects.create(
                **identity,
                canonical_filters=cleaned["filters"],
            )
    except IntegrityError:
        job = ReportExportJob.objects.get(**identity)
        return job, True
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action="report.export.requested",
        entity_type="report_export_job",
        entity_id=job.pk,
        new_value_json={
            "export_job_id": str(job.pk),
            "report_code": job.report_code,
            "format": job.export_format,
            "outcome": "queued",
        },
        ip_address=request_ip(request) if request is not None else "",
        user_agent=request_user_agent(request) if request is not None else "",
    )
    transaction.on_commit(lambda: _publish_export_job(job.pk), robust=True)
    return job, False


def _validate_request(*, actor, payload, idempotency_key):
    errors = {}
    if not isinstance(payload, dict):
        raise ReportValidation({"body": "Must be a JSON object."})
    unknown = sorted(set(payload) - {"report_code", "format", "filters"})
    errors.update({key: "Unknown field." for key in unknown})
    report_code = payload.get("report_code")
    if report_code not in FORMAT_MATRIX:
        errors["report_code"] = "Must name a registered exportable report."
    export_format = payload.get("format")
    if export_format not in SUPPORTED_FORMATS:
        errors["format"] = "Must be one of csv, xlsx, pdf, json."
    elif report_code in FORMAT_MATRIX and export_format not in FORMAT_MATRIX[report_code]:
        errors["format"] = "Format is not supported for this report."
    filters = payload.get("filters", {})
    if not isinstance(filters, dict):
        errors["filters"] = "Must be an object."
        filters = {}
    elif "page" in filters or "page_size" in filters:
        errors["filters"] = "Pagination fields are not export filters."
    canonical_filters = {}
    for key in sorted(filters):
        value = filters[key]
        if not isinstance(key, str) or not isinstance(value, str) or not value.strip():
            errors[f"filters.{key}"] = "Filter values must be nonblank strings."
        else:
            canonical_filters[key] = value.strip()
    key = idempotency_key.strip() if isinstance(idempotency_key, str) else ""
    if not key:
        errors["idempotency_key"] = "Idempotency-Key header is required."
    elif len(key) > 255:
        errors["idempotency_key"] = "Idempotency-Key must be at most 255 characters."
    permissions = set(auth_service.effective_permission_codes(actor))
    if not actor.can_authenticate() or "reports.export" not in permissions:
        raise ReportPermissionDenied
    if errors:
        raise ReportValidation(errors)
    try:
        run_report(
            report_code=report_code,
            actor=actor,
            query_params={
                **canonical_filters,
                "page": "1",
                "page_size": "1",
            },
        )
    except ReportValidation as exc:
        raise ReportValidation(
            {f"filters.{field}": message for field, message in exc.field_errors.items()}
        ) from exc
    canonical_json = json.dumps(
        canonical_filters,
        sort_keys=True,
        separators=(",", ":"),
    )
    return {
        "report_code": report_code,
        "format": export_format,
        "filters": canonical_filters,
        "filters_digest": hashlib.sha256(canonical_json.encode()).hexdigest(),
        "idempotency_key": key,
    }


def serialize_job(job, *, replayed=False):
    data = {
        "export_job_id": str(job.pk),
        "report_code": job.report_code,
        "format": job.export_format,
        "filters": job.canonical_filters,
        "status": job.state,
        "failure_code": job.failure_code or None,
        "idempotency_replayed": replayed,
        "requested_at": job.requested_at.isoformat().replace("+00:00", "Z"),
        "started_at": (
            job.started_at.isoformat().replace("+00:00", "Z")
            if job.started_at
            else None
        ),
        "completed_at": (
            job.completed_at.isoformat().replace("+00:00", "Z")
            if job.completed_at
            else None
        ),
    }
    if job.state == ReportExportJob.STATE_COMPLETED:
        data.update(
            {
                "checksum_sha256": job.checksum_sha256,
                "file_size_bytes": job.file_size_bytes,
            }
        )
    return data


def execute_export_job(export_job_id, *, storage=None):
    storage = storage or LocalReportExportStorage()
    attempt_started_at = timezone.now()
    worker_claim_id = uuid.uuid4()
    try:
        with transaction.atomic():
            job = (
                ReportExportJob.objects.select_for_update()
                .select_related("actor")
                .get(pk=export_job_id)
            )
            if job.state in {
                ReportExportJob.STATE_COMPLETED,
                ReportExportJob.STATE_FAILED,
            }:
                return serialize_job(job)
            if job.state == ReportExportJob.STATE_RUNNING and (
                job.worker_lease_expires_at is not None
                and job.worker_lease_expires_at > attempt_started_at
            ):
                return serialize_job(job)
            if job.state not in {
                ReportExportJob.STATE_QUEUED, ReportExportJob.STATE_RUNNING
            }:
                raise ValueError("Unsupported report export lifecycle state.")
            if job.started_at is None:
                job.started_at = attempt_started_at
            job.state = ReportExportJob.STATE_RUNNING
            job.failure_code = ""
            job.worker_claim_id = worker_claim_id
            lease_seconds = getattr(settings, "REPORT_EXPORT_WORKER_LEASE_SECONDS", 300)
            job.worker_lease_expires_at = attempt_started_at + timezone.timedelta(
                seconds=lease_seconds
            )
            job.save(
                update_fields=[
                    "state",
                    "started_at",
                    "failure_code",
                    "worker_claim_id",
                    "worker_lease_expires_at",
                    "updated_at",
                ]
            )

        generated_at = job.started_at
        rows = _collect_rows(job)
        content = _render_export(
            job=job,
            rows=rows,
            generated_at=generated_at,
        )
        stored = storage.store(
            export_job_id=job.pk,
            export_format=job.export_format,
            content=content,
        )
        with transaction.atomic():
            job = ReportExportJob.objects.select_for_update().get(pk=export_job_id)
            if job.state == ReportExportJob.STATE_COMPLETED:
                return serialize_job(job)
            if (
                job.state != ReportExportJob.STATE_RUNNING
                or job.worker_claim_id != worker_claim_id
            ):
                return serialize_job(job)
            completed_at = timezone.now()
            retention_hours = getattr(settings, "REPORT_EXPORT_RETENTION_HOURS", 24)
            job.state = ReportExportJob.STATE_COMPLETED
            job.completed_at = completed_at
            job.storage_key = stored.storage_key
            job.checksum_sha256 = stored.checksum_sha256
            job.file_size_bytes = stored.file_size_bytes
            job.content_type = CONTENT_TYPES[job.export_format]
            job.download_expires_at = completed_at + timezone.timedelta(
                hours=retention_hours
            )
            job.worker_claim_id = None
            job.worker_lease_expires_at = None
            job.save(
                update_fields=[
                    "state",
                    "completed_at",
                    "storage_key",
                    "checksum_sha256",
                    "file_size_bytes",
                    "content_type",
                    "download_expires_at",
                    "worker_claim_id",
                    "worker_lease_expires_at",
                    "updated_at",
                ]
            )
            return serialize_job(job)
    except ReportExportJob.DoesNotExist:
        raise
    except Exception as exc:
        failure_code = _failure_code(exc)
        with transaction.atomic():
            job = ReportExportJob.objects.select_for_update().get(pk=export_job_id)
            if (
                job.state not in {
                    ReportExportJob.STATE_COMPLETED,
                    ReportExportJob.STATE_FAILED,
                }
                and job.worker_claim_id == worker_claim_id
            ):
                job.state = ReportExportJob.STATE_FAILED
                if job.started_at is None:
                    job.started_at = attempt_started_at
                job.failure_code = failure_code
                job.completed_at = timezone.now()
                job.worker_claim_id = None
                job.worker_lease_expires_at = None
                job.save(
                    update_fields=[
                        "state",
                        "started_at",
                        "failure_code",
                        "completed_at",
                        "worker_claim_id",
                        "worker_lease_expires_at",
                        "updated_at",
                    ]
                )
                AuditLog.objects.create(
                    actor_user=job.actor,
                    actor_type="user",
                    action="report.export.failed",
                    entity_type="report_export_job",
                    entity_id=job.pk,
                    new_value_json={
                        "export_job_id": str(job.pk),
                        "report_code": job.report_code,
                        "outcome": "failed",
                        "failure_code": failure_code,
                    },
                )
        return serialize_job(job)


def status_for_actor(*, actor, export_job_id, request=None):
    try:
        job = ReportExportJob.objects.get(pk=export_job_id, actor=actor)
    except ReportExportJob.DoesNotExist:
        raise
    _require_current_access(actor=actor, job=job)
    data = serialize_job(job)
    if job.state == ReportExportJob.STATE_COMPLETED:
        if (
            job.file_deleted_at is not None
            or job.download_expires_at is None
            or job.download_expires_at <= timezone.now()
        ):
            data["download_expired"] = True
            data["download_url"] = None
            data["expires_at"] = (
                job.download_expires_at.isoformat().replace("+00:00", "Z")
                if job.download_expires_at
                else None
            )
        else:
            data.update(_issue_download_grant(actor=actor, job=job, request=request))
    return data


def read_download(*, actor, export_job_id, token, request=None, storage=None):
    storage = storage or LocalReportExportStorage()
    job = ReportExportJob.objects.get(pk=export_job_id, actor=actor)
    _require_current_access(actor=actor, job=job)
    if (
        job.state != ReportExportJob.STATE_COMPLETED
        or job.file_deleted_at is not None
        or job.download_expires_at is None
        or job.download_expires_at <= timezone.now()
    ):
        raise ReportValidation({"download": "Export download has expired."})
    ttl_seconds = getattr(settings, "REPORT_EXPORT_DOWNLOAD_TTL_MINUTES", 15) * 60
    try:
        payload = signing.loads(
            token,
            salt=_DOWNLOAD_TOKEN_SALT,
            max_age=ttl_seconds,
        )
    except (signing.BadSignature, signing.SignatureExpired) as exc:
        raise ReportValidation({"download": "Download grant is invalid or expired."}) from exc
    if payload != {"export_job_id": str(job.pk), "actor_id": str(actor.pk)}:
        raise ReportValidation({"download": "Download grant is invalid or expired."})
    content = storage.read(
        storage_key=job.storage_key,
        checksum_sha256=job.checksum_sha256,
        file_size_bytes=job.file_size_bytes,
    )
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action="report.export.downloaded",
        entity_type="report_export_job",
        entity_id=job.pk,
        new_value_json={
            "export_job_id": str(job.pk),
            "report_code": job.report_code,
            "format": job.export_format,
            "outcome": "downloaded",
            "checksum_sha256": job.checksum_sha256,
        },
        ip_address=request_ip(request) if request is not None else "",
        user_agent=request_user_agent(request) if request is not None else "",
    )
    return job, content


def cleanup_expired_exports(*, storage=None, limit=None):
    storage = storage or LocalReportExportStorage()
    limit = limit or getattr(settings, "REPORT_EXPORT_CLEANUP_BATCH_SIZE", 100)
    candidate_ids = list(
        ReportExportJob.objects.filter(
            state=ReportExportJob.STATE_COMPLETED,
            download_expires_at__lte=timezone.now(),
            file_deleted_at__isnull=True,
        )
        .order_by("download_expires_at")
        .values_list("pk", flat=True)[:limit]
    )
    deleted_ids = []
    for export_job_id in candidate_ids:
        with transaction.atomic():
            job = ReportExportJob.objects.select_for_update().get(pk=export_job_id)
            if (
                job.state != ReportExportJob.STATE_COMPLETED
                or job.file_deleted_at is not None
                or job.download_expires_at is None
                or job.download_expires_at > timezone.now()
            ):
                continue
            storage.delete(job.storage_key)
            job.file_deleted_at = timezone.now()
            job.save(update_fields=["file_deleted_at", "updated_at"])
            deleted_ids.append(str(job.pk))
    return {"deleted_count": len(deleted_ids), "export_job_ids": deleted_ids}


def _collect_rows(job):
    rows = []
    page = 1
    while True:
        batch, pagination = run_report(
            report_code=job.report_code,
            actor=job.actor,
            query_params={
                **job.canonical_filters,
                "page": str(page),
                "page_size": "100",
            },
        )
        rows.extend(batch)
        if not pagination["has_next"]:
            return rows
        page += 1


def _render_csv(*, job, rows, generated_at):
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["report_code", job.report_code])
    writer.writerow(["generated_by", str(job.actor_id)])
    writer.writerow(["generated_at", generated_at.isoformat().replace("+00:00", "Z")])
    for key, value in job.canonical_filters.items():
        writer.writerow([f"filter.{key}", value])
    writer.writerow([])
    columns = sorted({key for row in rows for key in row})
    writer.writerow(columns)
    for row in rows:
        writer.writerow([_cell_value(row.get(column)) for column in columns])
    return output.getvalue().encode("utf-8")


def _render_export(*, job, rows, generated_at):
    renderers = {
        "csv": _render_csv,
        "json": _render_json,
        "xlsx": _render_xlsx,
        "pdf": _render_pdf,
    }
    return renderers[job.export_format](
        job=job,
        rows=rows,
        generated_at=generated_at,
    )


def _metadata(job, generated_at):
    return {
        "report_code": job.report_code,
        "generated_by": str(job.actor_id),
        "generated_at": generated_at.isoformat().replace("+00:00", "Z"),
        "filters": job.canonical_filters,
    }


def _render_json(*, job, rows, generated_at):
    payload = {
        "metadata": _metadata(job, generated_at),
        "rows": rows,
    }
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _render_xlsx(*, job, rows, generated_at):
    table = [
        ["report_code", job.report_code],
        ["generated_by", str(job.actor_id)],
        ["generated_at", generated_at.isoformat().replace("+00:00", "Z")],
    ]
    table.extend(
        [f"filter.{key}", value] for key, value in job.canonical_filters.items()
    )
    table.append([])
    columns = sorted({key for row in rows for key in row})
    table.append(columns)
    table.extend(
        [_cell_value(row.get(column)) for column in columns]
        for row in rows
    )
    sheet_rows = []
    for row_number, values in enumerate(table, start=1):
        cells = []
        for column_number, value in enumerate(values, start=1):
            reference = f"{_xlsx_column(column_number)}{row_number}"
            safe_value = xml_escape(_xml_text(value))
            cells.append(
                f'<c r="{reference}" t="inlineStr"><is><t xml:space="preserve">'
                f"{safe_value}</t></is></c>"
            )
        sheet_rows.append(f'<row r="{row_number}">{"".join(cells)}</row>')
    sheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(sheet_rows)}</sheetData></worksheet>'
    )
    files = {
        "[Content_Types].xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            "</Types>"
        ),
        "_rels/.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
            'Target="xl/workbook.xml"/></Relationships>'
        ),
        "xl/workbook.xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Report Export" sheetId="1" r:id="rId1"/></sheets></workbook>'
        ),
        "xl/_rels/workbook.xml.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            'Target="worksheets/sheet1.xml"/></Relationships>'
        ),
        "xl/worksheets/sheet1.xml": sheet_xml,
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as workbook:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            workbook.writestr(info, files[name].encode("utf-8"))
    return output.getvalue()


def _render_pdf(*, job, rows, generated_at):
    output = io.BytesIO()
    document = canvas.Canvas(output, pagesize=A4, pageCompression=1)
    document.setTitle(f"{job.report_code} report export")
    document.setAuthor(str(job.actor_id))
    width, height = A4
    y = height - 40

    def write_line(value):
        nonlocal y
        if y < 40:
            document.showPage()
            y = height - 40
        document.drawString(40, y, str(value)[:120])
        y -= 14

    write_line(f"report_code: {job.report_code}")
    write_line(f"generated_by: {job.actor_id}")
    write_line(
        f"generated_at: {generated_at.isoformat().replace('+00:00', 'Z')}"
    )
    for key, value in job.canonical_filters.items():
        write_line(f"filter.{key}: {value}")
    for index, row in enumerate(rows, start=1):
        write_line(f"row {index}")
        for key in sorted(row):
            write_line(f"{key}: {_cell_value(row[key])}")
    document.save()
    return output.getvalue()


def _xlsx_column(number):
    letters = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def _xml_text(value):
    return "".join(
        character
        for character in str(value)
        if character in "\t\n\r" or ord(character) >= 32
    )


def _cell_value(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    if value is None:
        return ""
    return str(value)


def _issue_download_grant(*, actor, job, request=None):
    ttl_minutes = getattr(settings, "REPORT_EXPORT_DOWNLOAD_TTL_MINUTES", 15)
    grant_expires_at = min(
        timezone.now() + timezone.timedelta(minutes=ttl_minutes),
        job.download_expires_at,
    )
    token = signing.dumps(
        {"export_job_id": str(job.pk), "actor_id": str(actor.pk)},
        salt=_DOWNLOAD_TOKEN_SALT,
        compress=True,
    )
    path = reverse("report-export-download", kwargs={"export_job_id": job.pk})
    return {
        "download_url": f"{path}?{urlencode({'token': token})}",
        "expires_at": grant_expires_at.isoformat().replace("+00:00", "Z"),
    }


def _require_current_access(*, actor, job):
    permissions = set(auth_service.effective_permission_codes(actor))
    if not actor.can_authenticate() or "reports.export" not in permissions:
        raise ReportPermissionDenied
    run_report(
        report_code=job.report_code,
        actor=actor,
        query_params={**job.canonical_filters, "page": "1", "page_size": "1"},
    )


def _failure_code(exc):
    if isinstance(exc, ReportPermissionDenied):
        return FORBIDDEN
    if isinstance(exc, ReportValidation):
        return "INVALID_FILTERS"
    if isinstance(exc, (OSError, ValueError)):
        return "STORAGE_ERROR"
    return "GENERATION_FAILED"


def _publish_export_job(export_job_id):
    from sfpcl_credit.processes.tasks import execute_report_export_job

    execute_report_export_job.signature(args=[str(export_job_id)]).apply_async()
