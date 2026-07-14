from math import ceil

from django.core.exceptions import ValidationError
from django.db.models import F

from sfpcl_credit.legal_documents.models import (
    LoanDocument,
    NotarisationRecord,
    SignatureRecord,
    StampDutyRecord,
)


_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100
_LIST_PARAMS = {"page", "page_size"}


def list_for_application(*, application_id, query_params):
    """Return one strict, deterministic, exactly counted application page."""
    unknown = set(query_params.keys()) - _LIST_PARAMS
    if unknown:
        raise ValidationError(
            {field: "Unknown query parameter." for field in sorted(unknown)}
        )
    page = _positive_int("page", query_params.get("page"), 1)
    page_size = min(
        _positive_int("page_size", query_params.get("page_size"), _DEFAULT_PAGE_SIZE),
        _MAX_PAGE_SIZE,
    )
    queryset = (
        LoanDocument.objects.select_related("document", "document_template")
        .filter(loan_application_id=application_id)
        .order_by("-created_at", "-loan_document_id")
    )
    total_count = queryset.count()
    total_pages = ceil(total_count / page_size) if total_count else 1
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    return list(queryset[offset : offset + page_size]), {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }


def latest_generated_metadata_by_type(*, application_id, document_types):
    """Return only retained, renderer-validated generation metadata."""
    rows = (
        LoanDocument.objects.filter(
            loan_application_id=application_id,
            document_type__in=document_types,
            generation_status=LoanDocument.GENERATION_GENERATED,
            document_template__isnull=False,
            document__isnull=False,
            renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
            renderer_validated_document_id=F("document_id"),
            renderer_validated_checksum_sha256=F("document__checksum_sha256"),
        )
        .order_by("document_type", "-created_at", "-loan_document_id")
        .values_list("document_type", "loan_document_id")
    )
    latest = {}
    for document_type, loan_document_id in rows:
        latest.setdefault(document_type, loan_document_id)
    return latest


def signature_facts_for_application(*, application_id):
    """Return the single legal-owner projection consumed by downstream application facts."""
    return SignatureRecord.objects.filter(
        loan_document__loan_application_id=application_id
    ).values(
        "signature_status",
        "verified_by_user_id",
        "verified_at",
        "mismatch_resolution_type",
    )


def execution_signature_facts_for_document(
    *, application_id, loan_document_id, for_update=False
):
    """Return canonical-at-capture execution facts without exposing file authority."""
    queryset = SignatureRecord.objects
    if for_update:
        queryset = queryset.select_for_update()
    return list(
        queryset.filter(
            loan_document_id=loan_document_id,
            loan_document__loan_application_id=application_id,
            signer_party_type__in=["borrower", "nominee"],
        ).values(
            "signature_record_id",
            "signer_party_type", "signer_party_id", "signer_name_snapshot",
            "signature_status", "signature_mismatch_flag", "mismatch_resolution_type",
            "signed_at", "captured_by_user_id",
        )
    )


def poa_evidence_for_update(
    *, application_id, loan_document_id, stamp_duty_record_id,
    notarisation_record_id
):
    """Lock and return the exact legal-owner evidence set for a PoA mutation."""
    document = (
        LoanDocument.objects.select_for_update(of=("self",))
        .select_related("document")
        .filter(
            pk=loan_document_id,
            loan_application_id=application_id,
            document_type="power_of_attorney",
        )
        .first()
    )
    if document is None:
        return None, None, None
    stamp = StampDutyRecord.objects.select_for_update().filter(
        pk=stamp_duty_record_id, loan_document=document
    ).first()
    notary = NotarisationRecord.objects.select_for_update().filter(
        pk=notarisation_record_id, loan_document=document
    ).first()
    return document, stamp, notary


def sh4_evidence_for_update(*, application_id, loan_document_id):
    """Lock and return current maker-attributed SH-4 execution evidence."""
    document = (
        LoanDocument.objects.select_for_update(of=("self",))
        .select_related("document")
        .filter(
            pk=loan_document_id,
            loan_application_id=application_id,
            document_type="sh4",
        )
        .first()
    )
    if document is None:
        return None, None, []
    stamp = StampDutyRecord.objects.select_for_update().filter(
        loan_document=document, legacy_maker_attribution=False
    ).first()
    signatures = list(
        SignatureRecord.objects.select_for_update()
        .filter(
            loan_document=document,
            signer_party_type__in=["borrower", "witness"],
            legacy_maker_attribution=False,
        )
        .values(
            "signature_record_id", "signer_party_type", "signer_party_id",
            "signer_name_snapshot", "signature_status", "signature_mismatch_flag",
            "mismatch_resolution_type", "signed_at", "captured_by_user_id",
        )
    )
    return document, stamp, signatures


def cdsl_pledge_evidence_for_update(*, application_id, evidence_document_id):
    """Lock current legal-owned CDSL evidence without granting file access."""
    return (
        LoanDocument.objects.select_for_update(of=("self",))
        .select_related("document")
        .filter(
            loan_application_id=application_id,
            document_id=evidence_document_id,
            document_type="cdsl_pledge_evidence",
            generation_status=LoanDocument.GENERATION_GENERATED,
            renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
            renderer_validated_document_id=F("document_id"),
            renderer_validated_checksum_sha256=F("document__checksum_sha256"),
        )
        .first()
    )


def sh4_projection_for_application(*, application_id):
    """Project retained SH-4 ledger facts without importing security policy/models."""
    from sfpcl_credit.configurations.models import VersionHistory

    row = (
        VersionHistory.objects.filter(
            versioned_entity_type="sh4_share_transfer_form",
            new_value_json__loan_application_id=str(application_id),
        )
        .order_by("-created_at", "-version_history_id")
        .values_list("new_value_json", flat=True)
        .first()
    )
    return row or None


def cdsl_pledge_projection_for_application(*, application_id):
    """Project masked retained CDSL milestones without importing security policy."""
    from sfpcl_credit.configurations.models import VersionHistory

    row = (
        VersionHistory.objects.filter(
            versioned_entity_type="cdsl_share_pledge",
            new_value_json__loan_application_id=str(application_id),
        )
        .order_by("-created_at", "-version_history_id")
        .values_list("new_value_json", flat=True)
        .first()
    )
    return row or None


def _positive_int(field, value, default):
    if value in (None, ""):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError({field: "Must be a positive integer."}) from exc
    if parsed < 1:
        raise ValidationError({field: "Must be a positive integer."})
    return parsed
