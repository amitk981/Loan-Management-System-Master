"""Shallow S26-S35 composition over bounded selectors and deep action owners."""

from dataclasses import dataclass
import json
from urllib.parse import urlencode

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.crypto import salted_hmac

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.applications.modules import (
    document_checklist_facts,
    staff_workspace_actions as application_workspace_actions,
)
from sfpcl_credit.approvals.modules import document_checklist_access, document_checklist_facts as approval_facts
from sfpcl_credit.documents import services as document_services
from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.legal_documents import selectors
from sfpcl_credit.legal_documents.models import (
    ChecklistAction,
    ChecklistItem,
    DocumentChecklist,
    LoanDocument,
)
from sfpcl_credit.legal_documents.modules import (
    staff_workspace_actions as legal_workspace_actions,
    staff_workspace_facts,
)
from sfpcl_credit.processes import (
    document_checklist_actions,
    security_instrument_evidence,
    staff_documentation_queue,
)
from sfpcl_credit.security_instruments.models import SecurityPackage
from sfpcl_credit.security_instruments.modules import staff_workspace_actions as security_workspace_actions


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
WORKSPACE = "/api/v1/loan-applications/{}/documentation-workspace/"
ACTION_SALT = "sfpcl.staff-documentation-action.v1"


def _checklist_gateways():
    return legal_workspace_actions.ChecklistGateways(
        item_completion_decision=document_checklist_actions.item_completion_decision,
        complete_item=document_checklist_actions.complete_item,
        approve_company_secretary=document_checklist_actions.approve_company_secretary,
        approve_credit_manager=document_checklist_actions.approve_credit_manager,
        approve_sanction_committee=document_checklist_actions.approve_sanction_committee,
        borrower_safe_completed_item_ids=(
            document_checklist_actions.borrower_safe_completed_item_ids
        ),
    )


class AccessDenied(Exception):
    def __init__(self, error_code="FORBIDDEN"):
        self.error_code = error_code
        super().__init__(error_code)


class NotFound(Exception):
    pass


class ActionConflict(Exception):
    def __init__(self, message, error_code="CONFLICT"):
        self.error_code = error_code
        super().__init__(message)


@dataclass(frozen=True)
class DocumentContent:
    body: bytes
    file_name: str
    mime_type: str


def list_queue(*, actor, query_params):
    return staff_documentation_queue.list_queue(
        actor=actor,
        query_params=query_params,
        projector=project_queue_rows,
        access_denied=AccessDenied,
    )


@transaction.atomic
def read(*, actor, application_id, _include_private_commands=False):
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
    return _serialize(
        actor, application, checklist, items, package,
        include_private_commands=_include_private_commands,
    )


def _serialize(
    actor, application, checklist, items, package, *, include_private_commands=False
):
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
    gateways = _checklist_gateways()
    actions = legal_workspace_actions.approval_actions(
        actor,
        checklist,
        completed,
        gateways=gateways,
    )
    actions.extend(
        legal_workspace_actions.record_actions(
            actor,
            checklist,
            gateways=gateways,
        )
    )
    applicable = [row for row in rows if row["applicable"]]
    bank_fact = document_checklist_facts.resolve_blank_cheque_bank_fact(
        application_id=application.pk
    )
    bank_action = application_workspace_actions.bank_verification_action(
        actor=actor,
        application=application,
        fact=bank_fact,
    )
    if bank_action:
        actions.append(bank_action)
    stages = [
        ("company_secretary", checklist.company_secretary_signature_id),
        ("credit_manager", checklist.credit_manager_signature_id),
        ("sanction_committee", checklist.sanction_committee_signature_id),
    ]
    workspace = {
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
        "security_workflows": security_workspace_actions.project_workflows(
            actor,
            package,
            rows,
            legal_facts=staff_workspace_facts.security_creation_facts(
                application_id=application.pk
            ),
            gateways=security_workspace_actions.CreationGateways(
                create_poa=security_instrument_evidence.create_poa,
                create_sh4=security_instrument_evidence.create_sh4,
                create_pledge=security_instrument_evidence.create_pledge,
                create_blank_cheque=security_instrument_evidence.create_blank_cheque,
            ),
        ),
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
    _finalize_workspace_actions(
        actor, application, workspace,
        include_private_commands=include_private_commands,
    )
    return workspace


def _serialize_item(actor, application, item, document, reconciled):
    status = item.completion_status
    blocker = item.applicability_blocker
    if status == ChecklistItem.STATUS_COMPLETE and not reconciled:
        status, blocker = "blocked", "completion_evidence_stale"
    elif item.applicable_flag and document is None:
        blocker = blocker or "current_document_missing"
    actions = legal_workspace_actions.item_actions(
        actor,
        application,
        item,
        document,
        status,
        gateways=_checklist_gateways(),
    )
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


def _finalize_workspace_actions(
    actor, application, workspace, *, include_private_commands=False
):
    groups = [
        (f"item:{item['item_code']}", item["available_actions"])
        for item in workspace["items"]
    ]
    groups.extend(
        (f"security:{code}", workflow["available_actions"])
        for code, workflow in workspace["security_workflows"].items()
    )
    groups.append(("workspace", workspace["available_actions"]))
    for scope, actions in groups:
        for index, action in enumerate(actions):
            action_key = f"{scope}:{action['action_code']}:{index}"
            command = {
                "actor_id": str(actor.pk),
                "application_id": str(application.pk),
                "snapshot_id": workspace["snapshot_id"],
                "action_key": action_key,
                "action_code": action["action_code"],
                "fixed_payload": action.get("fixed_payload", {}),
            }
            canonical = json.dumps(command, sort_keys=True, separators=(",", ":"))
            action_id = salted_hmac(ACTION_SALT, canonical).hexdigest()
            action["action_id"] = action_id
            action["action_key"] = action_key
            action["action_url"] = (
                WORKSPACE.format(application.pk) + f"actions/{action_id}/"
            )
            action["method"] = "POST"
            action.pop("fixed_payload", None)
            owner_execute = action.pop("_owner_execute")
            if include_private_commands:
                action["_owner_execute"] = owner_execute


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
    items = tuple(
        sorted(
            checklist.items.all(),
            key=lambda item: (item.display_order, str(item.pk)),
        )
    )
    completed_ids = frozenset(
        document_checklist_actions.borrower_safe_completed_item_ids(checklist)
    )
    by_code = {item.item_code: item for item in items}
    try:
        package = application.security_package
    except SecurityPackage.DoesNotExist:
        package = None
    terminal = approval_facts.resolve_approved_facts(application_id=application.pk)
    required = [item for item in items if item.required_flag and item.applicable_flag]
    complete = [item for item in required if item.pk in completed_ids]
    bank_fact = document_checklist_facts.resolve_blank_cheque_bank_fact(
        application_id=application.pk
    )
    def item_status(code):
        item = by_code[code]
        if not item.applicable_flag:
            return "not_required"
        return "complete" if item.pk in completed_ids else item.completion_status

    def security_status(relation, field, required_flag):
        if not required_flag:
            return "not_required"
        row = getattr(package, relation, None) if package else None
        return getattr(row, field, "pending")

    return {
        "loan_application_id": str(application.pk),
        "application_reference_number": application.application_reference_number,
        "borrower_name": application.member.display_name,
        "sanctioned_amount": str(terminal.sanctioned_amount) if terminal else None,
        "shareholding_mode": terminal.holding_mode if terminal else None,
        "required_document_summary": {"complete": len(complete), "required": len(required)},
        "poa_status": security_status("power_of_attorney", "status", True),
        "tri_party_status": item_status("tri_party_agreement"),
        "sh4_status": security_status(
            "sh4_share_transfer_form", "form_status",
            bool(package and package.physical_share_security_required_flag),
        ),
        "cdsl_pledge_status": security_status(
            "cdsl_share_pledge", "pledge_status",
            bool(package and package.demat_pledge_required_flag),
        ),
        "term_sheet_status": item_status("term_sheet"),
        "loan_agreement_status": item_status("loan_agreement"),
        "bank_verification_status": "complete" if bank_fact.valid else "blocked",
        "checklist_status": checklist.checklist_status,
        "current_owner": _current_owner(checklist, complete, required),
    }


def project_queue_rows(*, actor, checklists):
    """Project only the already-paged rows; never build detail workspaces."""
    return [_queue_row(actor, checklist) for checklist in checklists]


def _current_owner(checklist, complete, required):
    if checklist.checklist_status == DocumentChecklist.STATUS_CS_APPROVED:
        return "Credit Manager"
    if checklist.checklist_status == DocumentChecklist.STATUS_CREDIT_APPROVED:
        return "Sanction Committee"
    if checklist.checklist_status in {DocumentChecklist.STATUS_SANCTION_APPROVED, DocumentChecklist.STATUS_READY}:
        return "Senior Manager Finance"
    return "Company Secretary" if len(complete) == len(required) else "Compliance Team"


@transaction.atomic
def execute_action(*, actor, application_id, action_id, payload, uploaded_file, request):
    """Execute one current opaque workspace command through its owning module."""
    workspace = read(
        actor=actor,
        application_id=application_id,
        _include_private_commands=True,
    )
    current = next(
        (action for action in _all_actions(workspace) if action["action_id"] == action_id),
        None,
    )
    if current is None or not current["enabled"]:
        raise NotFound
    allowed = {field["name"] for field in current.get("fields", [])}
    unknown = set(payload) - (allowed - {"file"})
    if unknown:
        raise ValidationError({field: "Unknown action field." for field in sorted(unknown)})
    if uploaded_file is not None and "file" not in allowed:
        raise ValidationError({"file": "This action does not accept a file."})
    missing = {
        field["name"]: "This field is required."
        for field in current.get("fields", [])
        if field.get("required")
        and (
            uploaded_file is None
            if field["name"] == "file"
            else not str(payload.get(field["name"], "")).strip()
        )
    }
    if missing:
        raise ValidationError(missing)
    try:
        return current["_owner_execute"](dict(payload), uploaded_file, request)
    except ValidationError:
        raise
    except legal_workspace_actions.OwnerAccessDenied as exc:
        raise AccessDenied(exc.error_code) from exc
    except legal_workspace_actions.OwnerNotFound as exc:
        raise NotFound from exc
    except application_workspace_actions.OwnerAccessDenied as exc:
        raise AccessDenied from exc
    except application_workspace_actions.OwnerNotFound as exc:
        raise NotFound from exc
    except security_workspace_actions.OwnerAccessDenied as exc:
        raise NotFound from exc
    except security_workspace_actions.OwnerNotFound as exc:
        raise NotFound from exc
    except legal_workspace_actions.OwnerConflict as exc:
        raise ActionConflict(str(exc), exc.error_code) from exc
    except security_workspace_actions.OwnerConflict as exc:
        raise ActionConflict(str(exc)) from exc
    except application_workspace_actions.OwnerConflict as exc:
        raise ActionConflict(str(exc)) from exc


def _all_actions(workspace):
    actions = list(workspace["available_actions"])
    for item in workspace["items"]:
        actions.extend(item["available_actions"])
    for workflow in workspace["security_workflows"].values():
        actions.extend(workflow["available_actions"])
    return actions


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
