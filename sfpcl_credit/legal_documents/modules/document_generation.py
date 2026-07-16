import json
import re
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.utils import timezone

from sfpcl_credit.applications.modules import document_generation_facts as application_facts
from sfpcl_credit.applications.modules import application_authority
from sfpcl_credit.approvals.modules import document_generation_facts as approval_facts
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
from sfpcl_credit.documents.modules import document_templates
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.legal_documents.models import ChecklistAction, LoanDocument
from sfpcl_credit.legal_documents import selectors as legal_document_selector
from sfpcl_credit.legal_documents.modules import document_renderer
from sfpcl_credit.workflows.events import record_workflow_event


GENERATE_PERMISSION = "documents.loan_document.generate"
READ_PERMISSION = "documents.loan_document.read"
GENERATED_ACTION = "documents.loan_document.generated"
ALLOWED_FORMATS = {"pdf", "docx"}
_REQUEST_FIELDS = {"document_type", "template_id", "output_format"}
_SUPPORTED_MERGE_FIELDS = {
    "borrower_name",
    "nominee_name",
    "witness_name",
    "shares_held",
    "facility",
    "loan_amount",
    "loan_purpose",
    "interest_rate",
    "interest_tenure",
    "repayment_date",
    "penal_interest_rate",
    "charges_and_fees",
    "security",
    "dispute_resolution",
}


@dataclass(frozen=True)
class RequestMetadata:
    request_id: str | None
    ip_address: str
    user_agent: str


class LegalDocumentAccessDenied(Exception):
    def __init__(self, error_code="FORBIDDEN"):
        self.error_code = error_code
        super().__init__(error_code)


class RendererProvenanceConflict(Exception):
    def __init__(self):
        self.details = {
            "renderer_validation_status": LoanDocument.RENDERER_LEGACY_UNVERIFIED,
            "remediation": "Generate a governed successor before using this retained output.",
        }
        super().__init__("Retained output is not bound to the current renderer contract.")


class LegalDocumentNotFound(Exception):
    pass


def can_generate(*, actor, application_id):
    """Return the same global/object authority decision used by ``generate``."""
    permissions = auth_service.effective_permission_codes(actor)
    if (
        not actor.can_authenticate()
        or GENERATE_PERMISSION not in permissions
        or document_services.TEMPLATE_FILE_REFERENCE_PERMISSION not in permissions
    ):
        return False
    application, access = application_authority.resolve_documentation_application_access(
        application_id=application_id,
        actor=actor,
        required_permission=GENERATE_PERMISSION,
        actor_permissions=permissions,
    )
    return bool(application and access.allowed)


def executable_output_formats(
    *, actor, application_id, document_type, template_id, storage=None
):
    """Return formats whose current locked owner prerequisites can reach rendering."""
    permissions = auth_service.effective_permission_codes(actor)
    if not can_generate(actor=actor, application_id=application_id):
        return ()
    storage = storage or LocalDocumentStorage()
    try:
        with transaction.atomic():
            application = application_facts.resolve_for_generation(
                application_id=application_id, for_update=True
            )
            if (
                application is None
                or application.application_status != application_facts.sanctioned_status()
            ):
                return ()
            variant = document_templates.resolve_borrower_template_variant(
                application.borrower_type
            )
            template = _resolve_template(
                {
                    "document_type": document_type,
                    "template_id": str(template_id),
                    "output_format": "pdf",
                },
                variant,
            )
            document_services.resolve_template_source_reference(
                actor_permissions=permissions,
                document_id=template.template_file_id,
            )
            _require_document_prerequisites(
                application_id=application.application_id,
                document_type=document_type,
            )
            _require_generation_not_terminal(
                application_id=application.application_id,
                document_type=document_type,
            )
            source = storage.read_verified(template.template_file)
            sanction = approval_facts.resolve_for_generation(
                application_id=application.application_id
            )
            if sanction is None:
                return ()
            merge_values = _project_merge_values(application, sanction)
            declared = template.merge_fields_json or []
            _validate_declared_merge_fields(declared, merge_values)
            formats = []
            for output_format in ("pdf", "docx"):
                try:
                    document_renderer.render(
                        output_format=output_format,
                        template_bytes=source,
                        merge_values={field: merge_values[field] for field in declared},
                    )
                except (ValidationError, ValueError, OSError):
                    continue
                formats.append(output_format)
            return tuple(formats)
    except (
        ValidationError,
        InvalidGenerationState,
        OSError,
        ValueError,
    ):
        return ()


resolve_borrower_template_variant = document_templates.resolve_borrower_template_variant


def generate(*, actor, application_id, payload, metadata, storage=None):
    permissions = auth_service.effective_permission_codes(actor)
    if (
        not actor.can_authenticate()
        or GENERATE_PERMISSION not in permissions
        or document_services.TEMPLATE_FILE_REFERENCE_PERMISSION not in permissions
    ):
        raise LegalDocumentAccessDenied()
    scoped_application, access = (
        application_authority.resolve_documentation_application_access(
            application_id=application_id,
            actor=actor,
            required_permission=GENERATE_PERMISSION,
            actor_permissions=permissions,
        )
    )
    if not access.allowed:
        raise LegalDocumentAccessDenied(access.error_code or "OBJECT_ACCESS_DENIED")
    if scoped_application is None:
        raise LegalDocumentNotFound
    cleaned = _validate_request(payload)
    storage = storage or LocalDocumentStorage()
    stored = None
    try:
        with transaction.atomic():
            application = application_facts.resolve_for_generation(
                application_id=application_id, for_update=True
            )
            if application is None:
                raise ValidationError({"loan_application_id": "Loan application was not found."})
            if application.application_status != application_facts.sanctioned_status():
                raise InvalidGenerationState(
                    "Loan documents can be generated only after sanction approval."
                )
            variant = document_templates.resolve_borrower_template_variant(
                application.borrower_type
            )
            template = _resolve_template(cleaned, variant)
            document_services.resolve_template_source_reference(
                actor_permissions=permissions,
                document_id=template.template_file_id,
            )
            _require_document_prerequisites(
                application_id=application.application_id,
                document_type=cleaned["document_type"],
            )
            replay = LoanDocument.objects.select_related("document").filter(
                loan_application_id=application.application_id,
                document_template=template,
                output_format=cleaned["output_format"],
            ).first()
            if replay is not None:
                if (
                    replay.renderer_validation_status
                    != LoanDocument.RENDERER_CURRENT_VALIDATED
                ):
                    raise RendererProvenanceConflict()
                return serialize_generation(replay)

            _require_generation_not_terminal(
                application_id=application.application_id,
                document_type=cleaned["document_type"],
            )

            try:
                template_source = storage.read_verified(template.template_file)
            except (OSError, ValueError):
                raise ValidationError(
                    {"template_file_id": "Template source bytes are unavailable or invalid."}
                )

            sanction = approval_facts.resolve_for_generation(
                application_id=application.application_id
            )
            if sanction is None:
                raise InvalidGenerationState(
                    "A retained sanctioned decision is required for document generation."
                )
            merge_values = _project_merge_values(application, sanction)
            declared = template.merge_fields_json or []
            _validate_declared_merge_fields(declared, merge_values)
            file_name = _safe_output_name(
                cleaned["document_type"],
                application.application_reference_number,
                cleaned["output_format"],
            )
            rendered = document_renderer.render(
                output_format=cleaned["output_format"],
                template_bytes=template_source,
                merge_values={field: merge_values[field] for field in declared},
            )
            stored = storage.store(ContentFile(rendered.content, name=file_name))
            generated_file = DocumentFile.objects.create(
                file_name=file_name,
                file_extension=f".{cleaned['output_format']}",
                mime_type=rendered.mime_type,
                file_size_bytes=stored.file_size_bytes,
                storage_provider=stored.storage_provider,
                storage_key=stored.storage_key,
                checksum_sha256=stored.checksum_sha256,
                uploaded_by_user=actor,
                sensitivity_level=DocumentFile.SENSITIVITY_CONFIDENTIAL,
            )
            loan_document = LoanDocument.objects.create(
                loan_application_id=application.application_id,
                document_type=cleaned["document_type"],
                document_category="legal",
                party_required="borrower",
                document_template=template,
                document=generated_file,
                output_format=cleaned["output_format"],
                generation_status=LoanDocument.GENERATION_GENERATED,
                execution_status=LoanDocument.EXECUTION_PENDING,
                verification_status=LoanDocument.VERIFICATION_PENDING,
                renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
                renderer_validated_document_id=generated_file.pk,
                renderer_validated_checksum_sha256=generated_file.checksum_sha256,
            )
            _record_evidence(
                actor=actor,
                metadata=metadata,
                loan_document=loan_document,
                template=template,
            )
            return serialize_generation(loan_document)
    except Exception:
        if stored is not None:
            storage.delete(stored)
        raise


def list_for_application(*, actor, application_id, query_params):
    permissions = auth_service.effective_permission_codes(actor)
    if not actor.can_authenticate() or READ_PERMISSION not in permissions:
        raise LegalDocumentAccessDenied()
    application, access = application_authority.resolve_documentation_application_access(
        application_id=application_id,
        actor=actor,
        required_permission=READ_PERMISSION,
        actor_permissions=permissions,
    )
    if not access.allowed:
        raise LegalDocumentAccessDenied(access.error_code or "OBJECT_ACCESS_DENIED")
    if application is None:
        raise LegalDocumentNotFound
    rows, pagination = legal_document_selector.list_for_application(
        application_id=application.pk,
        query_params=query_params,
    )
    return [serialize_metadata(row) for row in rows], pagination


def serialize_generation(row):
    return {
        "loan_document_id": str(row.loan_document_id),
        "document_type": row.document_type,
        "generation_status": row.generation_status,
        "document_id": str(row.document_id),
        "file_name": row.document.file_name,
    }


def serialize_metadata(row):
    return {
        **serialize_generation(row),
        "document_category": row.document_category,
        "party_required": row.party_required,
        "template_id": str(row.document_template_id),
        "template_version": row.document_template.template_version,
        "output_format": row.output_format,
        "execution_status": row.execution_status,
        "verification_status": row.verification_status,
        "verified_by_user_id": (
            str(row.verified_by_user_id) if row.verified_by_user_id else None
        ),
        "verified_at": (
            row.verified_at.isoformat().replace("+00:00", "Z")
            if row.verified_at
            else None
        ),
        "verification_remarks": row.verification_remarks,
        "renderer_validation_status": row.renderer_validation_status,
        "stamp_status": row.stamp_status,
        "notarisation_status": row.notarisation_status,
        "created_at": row.created_at.isoformat().replace("+00:00", "Z"),
    }


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}


class InvalidGenerationState(Exception):
    pass


def _validate_request(payload):
    errors = {
        field: "Unknown field." for field in sorted(set(payload.keys()) - _REQUEST_FIELDS)
    }
    cleaned = {}
    for field in ("document_type", "template_id", "output_format"):
        value = str(payload.get(field) or "").strip()
        if not value:
            errors[field] = "This field is required."
        cleaned[field] = value
    cleaned["output_format"] = cleaned["output_format"].lower()
    if cleaned["output_format"] and cleaned["output_format"] not in ALLOWED_FORMATS:
        errors["output_format"] = "Must be pdf or docx."
    if errors:
        raise ValidationError(errors)
    return cleaned


def _resolve_template(cleaned, variant):
    today = timezone.localdate()
    template = DocumentTemplate.objects.select_related("template_file").filter(
        document_template_id=cleaned["template_id"],
        approval_status=DocumentTemplate.STATUS_APPROVED,
        effective_from__lte=today,
        borrower_type=variant,
        document_type=cleaned["document_type"],
        template_file__isnull=False,
    ).filter(
        models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=today)
    ).first()
    if template is None:
        raise ValidationError(
            {"template_id": "Template was not found or is not eligible for generation."}
        )
    return template


def _project_merge_values(application, sanction):
    tenure = sanction.sanctioned_tenure_months
    interest = None
    if sanction.interest_rate_type and sanction.interest_rate_value:
        interest = f"{sanction.interest_rate_value} {sanction.interest_rate_type}"
    return {
        "borrower_name": sanction.borrower_name,
        "nominee_name": sanction.nominee_name,
        "witness_name": sanction.witness_name,
        "shares_held": sanction.shares_held,
        "facility": ("short_term" if tenure == 12 else "long_term") if tenure else None,
        "loan_amount": sanction.loan_amount,
        "loan_purpose": sanction.purpose,
        "interest_rate": interest,
        "interest_tenure": tenure,
        "repayment_date": sanction.repayment_date.isoformat() if sanction.repayment_date else None,
        "penal_interest_rate": sanction.penal_interest_rate,
        "charges_and_fees": (
            json.dumps(sanction.charges, sort_keys=True) if sanction.charges else None
        ),
        "security": sanction.security,
        "dispute_resolution": sanction.dispute_resolution,
    }


def _require_document_prerequisites(*, application_id, document_type):
    if document_type != "loan_agreement":
        return
    term_sheet_executed = LoanDocument.objects.filter(
        loan_application_id=application_id,
        document_type="term_sheet",
        execution_status="executed",
    ).exists()
    if not term_sheet_executed:
        raise InvalidGenerationState(
            "Loan Agreement generation requires an executed Term Sheet for this application."
        )


def _require_generation_not_terminal(*, application_id, document_type):
    item_code = {
        "power_of_attorney": "poa",
        "cdsl_pledge_evidence": "cdsl_pledge",
        "document_checklist": "final_checklist",
    }.get(document_type, document_type)
    completed = ChecklistAction.objects.filter(
        document_checklist__loan_application_id=application_id,
        checklist_item__item_code=item_code,
        action_type=ChecklistAction.TYPE_ITEM_COMPLETION,
    ).exists()
    approved = ChecklistAction.objects.filter(
        document_checklist__loan_application_id=application_id,
        action_type__in={
            ChecklistAction.TYPE_COMPANY_SECRETARY_APPROVAL,
            ChecklistAction.TYPE_CREDIT_MANAGER_APPROVAL,
            ChecklistAction.TYPE_SANCTION_COMMITTEE_APPROVAL,
        },
    ).exists()
    if completed or approved:
        raise InvalidGenerationState(
            "A terminal checklist action already consumes this document generation boundary."
        )


def _validate_declared_merge_fields(declared, values):
    errors = {}
    for field in declared:
        if field not in _SUPPORTED_MERGE_FIELDS:
            errors[field] = "Unknown template merge field."
        elif values.get(field) in (None, ""):
            errors[field] = "Required authoritative merge fact is missing."
    if errors:
        raise ValidationError(errors)


def _safe_output_name(document_type, application_reference, output_format):
    type_slug = re.sub(r"[^a-z0-9]+", "-", document_type.lower()).strip("-")
    reference = re.sub(r"[^A-Za-z0-9-]+", "-", application_reference or "").strip("-")
    if not type_slug or not reference:
        raise ValidationError(
            {"loan_application_id": "A safe application reference is required."}
        )
    return f"{type_slug}-{reference}.{output_format}"


def _record_evidence(*, actor, metadata, loan_document, template):
    facts = {
        "loan_application_id": str(loan_document.loan_application_id),
        "document_template_id": str(template.pk),
        "template_version": template.template_version,
        "document_type": loan_document.document_type,
        "output_format": loan_document.output_format,
        "document_id": str(loan_document.document_id),
        "renderer_contract_version": loan_document.renderer_contract_version,
        "renderer_validated_checksum_sha256": (
            loan_document.renderer_validated_checksum_sha256
        ),
        "request_id": metadata.request_id,
    }
    AuditLog.objects.create(
        actor_user=actor,
        actor_type="user",
        action=GENERATED_ACTION,
        entity_type="loan_document",
        entity_id=loan_document.pk,
        old_value_json={},
        new_value_json=facts,
        ip_address=metadata.ip_address,
        user_agent=metadata.user_agent,
    )
    record_workflow_event(
        actor=actor,
        workflow_name="loan_document_generation",
        entity_type="loan_document",
        entity_id=loan_document.pk,
        from_state=None,
        to_state=LoanDocument.GENERATION_GENERATED,
        trigger_reason="Generated from retained approved template.",
        action_code=GENERATED_ACTION,
        metadata=facts,
    )
