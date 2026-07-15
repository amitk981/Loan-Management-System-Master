"""Locked, redacted staff projection for the S26-S35 documentation workspace."""

from dataclasses import dataclass
from urllib.parse import urlencode

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from sfpcl_credit.applications.models import LoanApplication, Witness
from sfpcl_credit.applications.modules import bank_verification, document_checklist_facts
from sfpcl_credit.approvals.models import SanctionDecision
from sfpcl_credit.approvals.modules import document_checklist_access, document_checklist_facts as approval_facts
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.documents.models import DocumentTemplate
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.identity.models import User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.legal_documents import selectors
from sfpcl_credit.legal_documents.models import (
    ChecklistAction,
    ChecklistItem,
    DocumentChecklist,
    LoanDocument,
    NotarisationRecord,
    SignatureRecord,
    StampDutyRecord,
)
from sfpcl_credit.legal_documents.modules import (
    checklist_actions,
    document_generation,
    loan_document_verification,
    signatures,
    stamp_notary,
)
from sfpcl_credit.members.models import Shareholding
from sfpcl_credit.processes import document_checklist_actions
from sfpcl_credit.security_instruments.models import SecurityPackage
from sfpcl_credit.security_instruments.modules import (
    blank_dated_cheque,
    cdsl_share_pledge,
    power_of_attorney,
    sh4,
)


DOCUMENT_TYPES = {
    "witness_pan_aadhaar": "witness_pan_aadhaar",
    "cancelled_cheque": "cancelled_cheque",
    "blank_dated_cheque": "blank_dated_cheque",
    "poa": "power_of_attorney",
    "tri_party_agreement": "tri_party_agreement",
    "sh4": "sh4",
    "cdsl_pledge": "cdsl_pledge_evidence",
    "term_sheet": "term_sheet",
    "loan_agreement": "loan_agreement",
    "bank_verification_letter": "bank_verification_letter",
    "final_checklist": "document_checklist",
}
APPROVALS = {
    ChecklistAction.TYPE_COMPANY_SECRETARY_APPROVAL: (
        "approve_as_company_secretary", "Approve as Company Secretary",
        "documents.checklist.approve_cs", "company_secretary", "approve-as-company-secretary",
    ),
    ChecklistAction.TYPE_CREDIT_MANAGER_APPROVAL: (
        "approve_as_credit_manager", "Approve as Credit Manager",
        "documents.checklist.approve_credit", "credit_manager", "approve-as-credit-manager",
    ),
    ChecklistAction.TYPE_SANCTION_COMMITTEE_APPROVAL: (
        "approve_as_sanction_committee", "Approve as Sanction Committee",
        "documents.checklist.approve_sanction", "director", "approve-as-sanction-committee",
    ),
}
WORKSPACE = "/api/v1/loan-applications/{}/documentation-workspace/"
QUEUE_PAGE_SIZE = 20


class AccessDenied(Exception):
    def __init__(self, error_code="FORBIDDEN"):
        self.error_code = error_code
        super().__init__(error_code)


class NotFound(Exception):
    pass


@dataclass(frozen=True)
class DocumentContent:
    body: bytes
    file_name: str
    mime_type: str


def _action(
    action_code, label, required_permission, action_url, *, method="POST",
    required_role=None, fixed_payload=None, fields=None, **options,
):
    result = {
        "action_code": action_code, "label": label, "enabled": True,
        "disabled_reason": None, "required_permission": required_permission,
        "action_url": action_url, "method": method,
    }
    if required_role:
        result["required_role"] = required_role
    if fixed_payload:
        result["fixed_payload"] = fixed_payload
    if fields:
        result["fields"] = fields
    result.update(options)
    return result


def _owner_allows(authorizer, actor):
    try:
        authorizer(actor)
    except Exception as exc:  # each owner exports a different access-denial type
        if exc.__class__.__name__ in {
            "AccessDenied",
            "LegalDocumentAccessDenied",
            "RoleAuthorityDenied",
        }:
            return False
        raise
    return True


def _positive_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


@transaction.atomic
def list_queue(*, actor, query_params):
    """Return one strictly paginated, role-scoped S26 operational queue."""
    permissions = set(auth_service.effective_permission_codes(actor))
    if not actor.can_authenticate() or document_checklist_access.READ_PERMISSION not in permissions:
        raise AccessDenied
    page = _positive_int(query_params.get("page"), 1)
    page_size = min(_positive_int(query_params.get("page_size"), QUEUE_PAGE_SIZE), QUEUE_PAGE_SIZE)
    candidates = list(
        DocumentChecklist.objects.select_for_update()
        .select_related("loan_application__member")
        .order_by("created_at", "document_checklist_id")
    )
    visible = []
    for checklist in candidates:
        scope = document_checklist_access.resolve_read_access(
            actor=actor, application_id=checklist.loan_application_id,
        )
        if not scope.error_code and scope.route == document_checklist_access.ROUTE_POST_SANCTION:
            visible.append(checklist)
    total_count = len(visible)
    start = (page - 1) * page_size
    rows = [_queue_row(actor, checklist) for checklist in visible[start : start + page_size]]
    total_pages = max(1, (total_count + page_size - 1) // page_size)
    return {
        "items": rows,
        "pagination": {
            "page": page, "page_size": page_size, "total_count": total_count,
            "total_pages": total_pages, "has_next": page < total_pages,
            "has_previous": page > 1,
        },
    }


@transaction.atomic
def read(*, actor, application_id):
    scope = document_checklist_access.resolve_read_access(
        actor=actor,
        application_id=application_id,
    )
    if scope.error_code == "NOT_FOUND":
        raise NotFound
    if scope.error_code or scope.route != document_checklist_access.ROUTE_POST_SANCTION:
        raise AccessDenied(scope.error_code or "OBJECT_ACCESS_DENIED")
    application = (
        LoanApplication.objects.select_for_update()
        .select_related("member", "nominee")
        .filter(pk=application_id)
        .first()
    )
    checklist = (
        DocumentChecklist.objects.select_for_update()
        .filter(loan_application=application)
        .first()
    )
    if application is None or checklist is None:
        raise NotFound
    items = tuple(
        ChecklistItem.objects.select_for_update()
        .filter(document_checklist=checklist)
        .order_by("display_order", "checklist_item_id")
    )
    package = (
        SecurityPackage.objects.select_for_update()
        .filter(loan_application=application)
        .first()
    )
    return _serialize(actor, application, checklist, items, package)


def _serialize(actor, application, checklist, items, package):
    completed = frozenset(document_checklist_actions.borrower_safe_completed_item_ids(checklist))
    latest_ids = selectors.latest_generated_metadata_by_type(
        application_id=application.pk,
        document_types=set(DOCUMENT_TYPES.values()),
    )
    documents = {
        row.document_type: row
        for row in LoanDocument.objects.select_for_update()
        .select_related("document", "document_template")
        .filter(pk__in=latest_ids.values())
    }
    rows = [
        _serialize_item(actor, application, item, documents.get(DOCUMENT_TYPES[item.item_code]), item.pk in completed)
        for item in items
    ]
    actions = _approval_actions(actor, checklist, completed)
    applicable = [row for row in rows if row["applicable"]]
    bank_fact = document_checklist_facts.resolve_blank_cheque_bank_fact(
        application_id=application.pk
    )
    bank_action = _bank_verification_action(actor, application, bank_fact)
    if bank_action:
        actions.append(bank_action)
    stages = [
        ("company_secretary", checklist.company_secretary_signature_id),
        ("credit_manager", checklist.credit_manager_signature_id),
        ("sanction_committee", checklist.sanction_committee_signature_id),
    ]
    return {
        "snapshot_id": f"{checklist.pk}:{checklist.updated_at.isoformat()}",
        "loan_application_id": str(application.pk),
        "application_reference_number": application.application_reference_number,
        "borrower_name": application.member.display_name,
        "checklist_status": checklist.checklist_status,
        "bank_verification_status": "complete" if bank_fact.valid else "blocked",
        "items": rows,
        "pack_summary": {
            "status": "ready" if all(row["status"] == "complete" for row in applicable) else "incomplete",
            "available_count": sum(bool(row["document"]) for row in rows),
            "missing_count": sum(not row["document"] for row in applicable),
            "pending_review_count": sum(
                bool(row["document"] and row["status"] != "complete") for row in applicable
            ),
        },
        "blockers": [
            {"item_code": row["item_code"], "label": row["item_label"], "reason": row["blocker"] or row["status"]}
            for row in applicable
            if row["status"] != ChecklistItem.STATUS_COMPLETE
        ],
        "security_workflows": _security_workflows(actor, package, rows),
        "approval_stages": [
            {"role": role, "status": "signed" if signature else "pending"}
            for role, signature in stages
        ]
        + [
            {"role": "senior_manager_finance", "status": (
                "signed" if checklist.senior_manager_finance_signature_id else "blocked_until_disbursement"
            )}
        ],
        "timeline": _timeline(checklist),
        "available_actions": actions,
    }


def _serialize_item(actor, application, item, document, reconciled):
    status = item.completion_status
    blocker = item.applicability_blocker
    if status == ChecklistItem.STATUS_COMPLETE and not reconciled:
        status, blocker = "blocked", "completion_evidence_stale"
    elif item.applicable_flag and document is None:
        blocker = blocker or "current_document_missing"
    actions = _item_actions(actor, application, item, document, status)
    download = None
    if document and document_services.user_can_download_documents(actor):
        download = {
            "file_name": document.document.file_name,
            "mime_type": document.document.mime_type or "application/octet-stream",
            "action_url": WORKSPACE.format(application.pk) + f"{item.item_code}/download/",
        }
    metadata = None
    if document:
        metadata = {
            "loan_document_id": str(document.pk),
            "version": document.document_template.template_version,
            "generation_status": document.generation_status,
            "execution_status": document.execution_status,
            "verification_status": document.verification_status,
            "download": download,
        }
    return {
        "checklist_item_id": str(item.pk),
        "item_code": item.item_code,
        "item_label": item.item_label,
        "required": item.required_flag,
        "applicable": item.applicable_flag,
        "status": status,
        "blocker": blocker,
        "stamp_status": item.stamp_status,
        "notarisation_status": item.notarisation_status,
        "poa_status": item.poa_status,
        "document": metadata,
        "available_actions": actions,
    }


def _item_actions(actor, application, item, document, status):
    if not item.applicable_flag:
        return []
    if document is None:
        generation = _generation_action(actor, application, item.item_code)
        return [generation] if generation else []
    actions = []
    if status == ChecklistItem.STATUS_PENDING and _owner_allows(
        checklist_actions.require_item_completion_actor, actor
    ):
        actions.append(
            _action(
                "complete_item",
                "Mark complete",
                "documents.checklist.update",
                f"/api/v1/checklist-items/{item.pk}/complete/",
                required_role="compliance_team_member",
                fixed_payload={"loan_document_id": str(document.pk)},
                fields=[{"name": "remarks", "label": "Remarks", "type": "textarea", "required": True}],
            )
        )
    if (
        document.document_type == "tri_party_agreement"
        and document.verification_status != "verified"
        and _owner_allows(loan_document_verification.require_verify_actor, actor)
    ):
        actions.append(
            _action(
                "verify_document",
                "Verify document",
                "documents.loan_document.verify",
                f"/api/v1/loan-documents/{document.pk}/verify/",
                required_role="company_secretary",
                fixed_payload={"verification_status": "verified"},
                fields=[{"name": "remarks", "label": "Remarks", "type": "textarea", "required": True}],
            )
        )
    if status == ChecklistItem.STATUS_PENDING:
        actions.extend(_legal_evidence_actions(actor, application, document))
    return actions


def _legal_evidence_actions(actor, application, document):
    actions = []
    if _owner_allows(signatures.require_record_actor, actor):
        actions.append(
            _action(
                "record_signature",
                "Record signature",
                signatures.RECORD_PERMISSION,
                f"/api/v1/loan-documents/{document.pk}/signatures/",
                required_role="compliance_team_member",
                fixed_payload={
                    "signer_party_type": "borrower",
                    "signer_party_id": str(application.member_id),
                    "signer_name_snapshot": application.member.display_name,
                    "signature_status": "signed",
                    "signature_mismatch_flag": False,
                },
                fields=[
                    {"name": "signature_method", "label": "Method", "type": "select", "required": True, "options": ["wet_ink", "digital", "scanned"]},
                    {"name": "signed_at", "label": "Signed at", "type": "datetime-local", "required": True},
                ],
            )
        )
    if _owner_allows(stamp_notary.require_stamp_actor, actor):
        actions.append(
            _action(
                "record_stamp",
                "Record stamp",
                stamp_notary.STAMP_PERMISSION,
                f"/api/v1/loan-documents/{document.pk}/stamp-duty-record/",
                fixed_payload={
                    "stamp_number": None,
                    "stamp_purchase_date": None,
                    "executed_date": None,
                    "remarks": None,
                },
                fields=[
                    {"name": "stamp_paper_amount", "label": "Stamp amount", "type": "text", "required": True},
                    {"name": "stamp_type", "label": "Stamp type", "type": "select", "required": True, "options": ["physical", "electronic"]},
                    {"name": "status", "label": "Status", "type": "select", "required": True, "options": ["pending", "adequate", "insufficient"]},
                    {"name": "remarks", "label": "Remarks", "type": "textarea", "required": False},
                ],
            )
        )
    if _owner_allows(stamp_notary.require_notary_actor, actor):
        actions.append(
            _action(
                "record_notarisation",
                "Record notarisation",
                stamp_notary.NOTARY_PERMISSION,
                f"/api/v1/loan-documents/{document.pk}/notarisation-record/",
                fixed_payload={
                    "notary_name": None,
                    "notary_registration_number": None,
                    "notarised_date": None,
                    "evidence_document_id": None,
                    "remarks": None,
                },
                fields=[
                    {"name": "notary_name", "label": "Notary name", "type": "text", "required": False},
                    {"name": "notary_registration_number", "label": "Registration number", "type": "text", "required": False},
                    {"name": "notarised_date", "label": "Notarised date", "type": "date", "required": False},
                    {"name": "status", "label": "Status", "type": "select", "required": True, "options": ["pending", "completed", "rejected"]},
                ],
            )
        )
    unresolved = SignatureRecord.objects.filter(
        loan_document=document,
        signature_status="mismatch",
        signature_mismatch_flag=True,
        mismatch_resolution_type__isnull=True,
    ).first()
    if unresolved and _owner_allows(signatures.require_resolve_actor, actor):
        actions.append(
            _action(
                "resolve_signature_mismatch",
                "Resolve signature mismatch",
                signatures.RESOLVE_PERMISSION,
                f"/api/v1/signature-records/{unresolved.pk}/resolve-mismatch/",
                required_role="company_secretary",
                fields=[
                    {"name": "mismatch_resolution_type", "label": "Resolution", "type": "select", "required": True, "options": ["bank_verification_letter", "borrower_declaration"]},
                    {"name": "mismatch_resolution_document_id", "label": "Evidence document", "type": "text", "required": True},
                    {"name": "remarks", "label": "Remarks", "type": "textarea", "required": True},
                ],
            )
        )
    return actions


def _generation_action(actor, application, item_code):
    if not document_generation.can_generate(actor=actor, application_id=application.pk):
        return None
    try:
        variant = document_generation.resolve_borrower_template_variant(application.borrower_type)
    except ValidationError:
        return None
    document_type = DOCUMENT_TYPES[item_code]
    today = timezone.localdate()
    template = (
        DocumentTemplate.objects.filter(
            document_type=document_type,
            borrower_type=variant,
            approval_status=DocumentTemplate.STATUS_APPROVED,
            effective_from__lte=today,
            template_file__isnull=False,
        )
        .filter(models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=today))
        .order_by("-effective_from", "-created_at")
        .first()
    )
    if template is None:
        return None
    return _action(
        "generate_document",
        "Generate document",
        document_generation.GENERATE_PERMISSION,
        f"/api/v1/loan-applications/{application.pk}/loan-documents/generate/",
        required_role="compliance_team_member",
        fixed_payload={"document_type": document_type, "template_id": str(template.pk)},
        fields=[{"name": "output_format", "label": "Output format", "type": "select", "required": True, "options": ["pdf", "docx"]}],
        template_version=template.template_version,
    )


def _approval_actions(actor, checklist, completed):
    available = checklist_actions.available_approval_action(
        actor=actor,
        checklist=checklist,
        completed_item_ids=completed,
    )
    if not available:
        return []
    code, label, permission, role, suffix = APPROVALS[available]
    return [
        _action(
            code,
            label,
            permission,
            f"/api/v1/document-checklists/{checklist.pk}/{suffix}/",
            required_role=role,
            fields=[{"name": "comments", "label": "Comments", "type": "textarea", "required": True}],
        )
    ]


def _bank_verification_action(actor, application, fact):
    if fact.valid or not application.bank_account_id or not application.cancelled_cheque_id:
        return None
    if not _owner_allows(bank_verification.require_verifier, actor):
        return None
    return _action(
        "verify_bank_sources", "Verify bank sources", "documents.checklist.update",
        f"/api/v1/loan-applications/{application.pk}/bank-verification-decision/",
        fixed_payload={
            "bank_account_id": str(application.bank_account_id),
            "cancelled_cheque_id": str(application.cancelled_cheque_id),
        },
        fields=[{"name": "decision_status", "label": "Decision", "type": "select", "required": True, "options": ["verified", "rejected"]}],
    )


def _security_workflows(actor, package, items):
    by_code = {row["item_code"]: row for row in items}
    result = {
        "tri_party_agreement": _workflow_from_item(by_code["tri_party_agreement"]),
        "cancelled_cheque": _workflow_from_item(by_code["cancelled_cheque"]),
    }
    if package is None:
        result.update(
            {
                "power_of_attorney": _workflow(True, "pending", []),
                "sh4": _workflow_from_item(by_code["sh4"]),
                "cdsl_pledge": _workflow_from_item(by_code["cdsl_pledge"]),
                "blank_dated_cheque": _workflow_from_item(by_code["blank_dated_cheque"]),
            }
        )
        return result
    specs = {
        "power_of_attorney": (
            package.poa_required_flag, getattr(package, "power_of_attorney", None),
            "status", power_of_attorney.require_manage_actor,
            "security.poa.manage", "power-of-attorney",
        ),
        "sh4": (
            package.physical_share_security_required_flag, getattr(package, "sh4_share_transfer_form", None),
            "form_status", sh4.require_manage_actor,
            "security.sh4.manage", "sh4-share-transfer-form",
        ),
        "cdsl_pledge": (
            package.demat_pledge_required_flag, getattr(package, "cdsl_share_pledge", None),
            "pledge_status", cdsl_share_pledge.require_manage_actor,
            "security.cdsl_pledge.manage", "cdsl-share-pledge",
        ),
        "blank_dated_cheque": (
            package.blank_cheque_required_flag, getattr(package, "blank_dated_cheque", None),
            "cheque_status", blank_dated_cheque.require_manage_actor,
            "security.blank_cheque.manage", "blank-dated-cheque",
        ),
    }
    for code, spec in specs.items():
        required, row, field, authorizer, permission, collection = spec
        actions = []
        if required and row is None and _owner_allows(authorizer, actor):
            endpoint = f"/api/v1/security-packages/{package.pk}/{collection}/"
            action = _security_create_action(package, code, permission, endpoint)
            if action:
                actions.append(action)
        result[code] = _workflow(required, getattr(row, field, "pending"), actions)
    return result


def _security_create_action(package, code, permission, endpoint):
    """Expose create only when every server-owned prerequisite can be selected."""
    application = package.loan_application
    fixed, fields = None, []
    if code == "power_of_attorney":
        document = LoanDocument.objects.filter(
            loan_application=application, document_type="power_of_attorney",
            renderer_validated_document_id=models.F("document_id"),
        ).order_by("-created_at").first()
        stamp = StampDutyRecord.objects.filter(loan_document=document, status="adequate").first()
        notary = NotarisationRecord.objects.filter(loan_document=document, status="completed").first()
        attorney = User.objects.filter(
            status=User.ACTIVE_STATUS, primary_role__role_code="company_secretary"
        ).first()
        if application.nominee_id and document and stamp and notary and attorney:
            fixed = {
                "borrower_member_id": str(application.member_id),
                "nominee_id": str(application.nominee_id), "attorney_user_id": str(attorney.pk),
                "loan_document_id": str(document.pk), "stamp_duty_record_id": str(stamp.pk),
                "notarisation_record_id": str(notary.pk), "execution_status": "pending",
                "effective_from": None, "status": "draft",
            }
            fields = [{"name": "purpose_summary", "label": "Purpose and authority", "type": "textarea", "required": True}]
    elif code == "sh4":
        witness = Witness.objects.filter(
            loan_application=application,
            verification_status="verified",
            shareholder_verified_flag=True,
        ).first()
        holding = Shareholding.objects.filter(
            member=application.member, holding_mode="physical", status="active"
        ).first()
        document = LoanDocument.objects.filter(
            loan_application=application, document_type="sh4"
        ).order_by("-created_at").first()
        if witness and holding and document:
            fixed = {
                "member_id": str(application.member_id), "witness_id": str(witness.pk),
                "shareholding_id": str(holding.pk), "share_count": None,
                "loan_document_id": str(document.pk), "form_status": "pending",
                "custody_location": None, "signed_at": None,
            }
    elif code == "cdsl_pledge":
        if Shareholding.objects.filter(
            member=application.member, holding_mode="demat", status="active",
            demat_account_id__isnull=False,
        ).exists():
            fixed = {
                "pledgor_member_id": str(application.member_id),
                "pledgee_entity_name": cdsl_share_pledge.SFPCL_ENTITY_NAME,
                "pledgee_bo_account": None, "pledgor_dp_name": None,
                "pledgee_dp_name": None, "prf_status": "prepared",
                "pledge_sequence_number": None, "pledge_acceptance_status": "pending",
                "pledged_share_count": None, "agreement_number": None,
                "pledge_status": "pending", "evidence_document_id": None,
            }
            fields = [{"name": "pledgor_bo_account", "label": "Pledgor BO account", "type": "text", "required": True}]
    elif code == "blank_dated_cheque":
        fact = document_checklist_facts.resolve_blank_cheque_bank_fact(
            application_id=application.pk
        )
        if fact.valid:
            fixed = {
                "member_id": str(fact.member_id), "bank_account_id": str(fact.bank_account_id),
                "document_id": None, "cheque_status": "collected", "custody_location": None,
            }
            fields = [
                {"name": "cheque_number", "label": "Cheque number", "type": "text", "required": True},
                {"name": "collected_at", "label": "Collected date", "type": "date", "required": True},
            ]
    if fixed is None:
        return None
    return _action(
        f"manage_{code}", f"Manage {code.replace('_', ' ').title()}", permission,
        endpoint, fixed_payload=fixed, fields=fields,
    )


def _workflow(required, status, actions):
    return {
        "required": required,
        "status": status if required else "not_required",
        "available_actions": actions,
    }


def _workflow_from_item(item):
    return _workflow(item["applicable"], item["status"], item["available_actions"])


def _timeline(checklist):
    labels = {
        ChecklistAction.TYPE_ITEM_COMPLETION: "Checklist Item Completed",
        ChecklistAction.TYPE_COMPANY_SECRETARY_APPROVAL: "Company Secretary Approved",
        ChecklistAction.TYPE_CREDIT_MANAGER_APPROVAL: "Credit Manager Approved",
        ChecklistAction.TYPE_SANCTION_COMMITTEE_APPROVAL: "Sanction Committee Approved",
        ChecklistAction.TYPE_DISBURSEMENT_SIGNATURE: "Disbursement Signed",
    }
    role_aliases = {
        "compliance_team_member": "compliance_team", "internal_auditor": "auditor",
        "chief_financial_controller": "cfc",
    }
    actions = checklist.actions.select_related("actor_user").order_by("-signed_at")
    return [
        {
            "id": f"{action.action_type}:{index}", "entity_type": "document_checklist",
            "entity_id": str(checklist.loan_application_id), "event_type": labels[action.action_type],
            "timestamp": action.signed_at.isoformat(), "actor_name": action.actor_user_name_snapshot,
            "actor_role": role_aliases.get(action.canonical_role_code, action.canonical_role_code),
            "new_state": action.action_type,
            "comment": action.comments,
            "reason": action.meaning,
        }
        for index, action in enumerate(actions)
    ]


def _queue_row(actor, checklist):
    application = checklist.loan_application
    items = tuple(checklist.items.order_by("display_order", "checklist_item_id"))
    package = SecurityPackage.objects.filter(loan_application=application).first()
    workspace = _serialize(actor, application, checklist, items, package)
    by_code = {item["item_code"]: item for item in workspace["items"]}
    workflows = workspace["security_workflows"]
    terminal = approval_facts.resolve_approved_facts(application_id=application.pk)
    decision = (
        SanctionDecision.objects.filter(
            loan_application=application,
            approval_case_id=terminal.approval_case_id if terminal else None,
            decision="sanctioned",
        ).first()
        if terminal
        else None
    )
    required = [item for item in workspace["items"] if item["required"] and item["applicable"]]
    complete = [item for item in required if item["status"] == "complete"]
    return {
        "loan_application_id": str(application.pk),
        "application_reference_number": application.application_reference_number,
        "borrower_name": application.member.display_name,
        "sanctioned_amount": str(decision.sanctioned_amount) if decision else None,
        "shareholding_mode": terminal.holding_mode if terminal else None,
        "required_document_summary": {"complete": len(complete), "required": len(required)},
        "poa_status": workflows["power_of_attorney"]["status"], "tri_party_status": workflows["tri_party_agreement"]["status"],
        "sh4_status": workflows["sh4"]["status"], "cdsl_pledge_status": workflows["cdsl_pledge"]["status"],
        "term_sheet_status": by_code["term_sheet"]["status"], "loan_agreement_status": by_code["loan_agreement"]["status"],
        "bank_verification_status": workspace["bank_verification_status"],
        "checklist_status": checklist.checklist_status,
        "current_owner": _current_owner(checklist, complete, required),
    }


def _current_owner(checklist, complete, required):
    if checklist.checklist_status == DocumentChecklist.STATUS_CS_APPROVED:
        return "Credit Manager"
    if checklist.checklist_status == DocumentChecklist.STATUS_CREDIT_APPROVED:
        return "Sanction Committee"
    if checklist.checklist_status in {DocumentChecklist.STATUS_SANCTION_APPROVED, DocumentChecklist.STATUS_READY}:
        return "Senior Manager Finance"
    return "Company Secretary" if len(complete) == len(required) else "Compliance Team"


@transaction.atomic
def download(*, actor, application_id, item_code, request, storage=None):
    item = next(
        (
            row
            for row in read(actor=actor, application_id=application_id)["items"]
            if row["item_code"] == item_code
        ),
        None,
    )
    document = None
    if item and item["document"] and item["document"]["download"]:
        document = (
            LoanDocument.objects.select_for_update()
            .select_related("document", "document_template")
            .filter(pk=item["document"]["loan_document_id"])
            .first()
        )
    if document is None:
        raise NotFound
    scope = {
        "user_id": str(actor.pk),
        "loan_application_id": str(application_id),
        "item_code": item_code,
        "loan_document_id": str(document.pk),
    }
    if request.GET.get("content") != "1":
        capability = document_services.issue_download_capability(document=document.document, scope=scope)
        return {
            "download_url": WORKSPACE.format(application_id)
            + f"{item_code}/download/?"
            + urlencode({"content": "1", "token": capability["token"]}),
            "expires_at": capability["expires_at"],
        }
    try:
        body = document_services.read_with_download_capability(
            document=document.document, scope=scope, token=request.GET.get("token", ""),
            storage=storage or LocalDocumentStorage(),
        )
    except (ValidationError, ValueError, OSError) as exc:
        raise NotFound from exc
    metadata = {
        "loan_application_id": str(application_id),
        "loan_document_id": str(document.pk),
        "document_version": document.document_template.template_version,
        "document_category": document.document_category,
        "sensitivity_level": document.document.sensitivity_level,
        "reason": "staff_documentation_workspace",
        "request_id": request.headers.get("X-Request-ID"),
        "outcome": "accepted",
    }
    document_services.record_document_audit(
        user=actor, request=request, document=document.document,
        spec=document_services.DocumentAuditSpec(
            action=document_services.DOCUMENT_DOWNLOAD_AUDIT_ACTION,
            actor_type="user",
            metadata=metadata,
        ),
    )
    return DocumentContent(body, document.document.file_name,
                           document.document.mime_type or "application/octet-stream")
