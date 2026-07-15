"""Locked, redacted staff projection for S26-S35 documentation work."""
from dataclasses import dataclass
from urllib.parse import urlencode
from django.core.exceptions import ValidationError; from django.db import models, transaction; from django.utils import timezone
from sfpcl_credit.applications.models import LoanApplication; from sfpcl_credit.approvals.modules import document_checklist_access
from sfpcl_credit.documents import services as document_services; from sfpcl_credit.documents.models import DocumentTemplate; from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.identity.modules import auth_service; from sfpcl_credit.legal_documents import selectors
from sfpcl_credit.legal_documents.models import ChecklistAction, ChecklistItem, DocumentChecklist, LoanDocument; from sfpcl_credit.legal_documents.modules import checklist_actions
from sfpcl_credit.processes import document_checklist_actions; from sfpcl_credit.security_instruments.models import SecurityPackage
DOCUMENT_TYPES = {"witness_pan_aadhaar": "witness_pan_aadhaar", "cancelled_cheque": "cancelled_cheque", "blank_dated_cheque": "blank_dated_cheque", "poa": "power_of_attorney", "tri_party_agreement": "tri_party_agreement", "sh4": "sh4", "cdsl_pledge": "cdsl_pledge_evidence", "term_sheet": "term_sheet", "loan_agreement": "loan_agreement", "bank_verification_letter": "bank_verification_letter", "final_checklist": "document_checklist"}
APPROVALS = {ChecklistAction.TYPE_COMPANY_SECRETARY_APPROVAL: ("approve_as_company_secretary", "approve-as-company-secretary"), ChecklistAction.TYPE_CREDIT_MANAGER_APPROVAL: ("approve_as_credit_manager", "approve-as-credit-manager"), ChecklistAction.TYPE_SANCTION_COMMITTEE_APPROVAL: ("approve_as_sanction_committee", "approve-as-sanction-committee")}
SECURITY_ACTIONS = {"power_of_attorney": ("security.poa.manage", "power-of-attorney", "power-of-attorneys"), "sh4": ("security.sh4.manage", "sh4-share-transfer-form", "sh4-share-transfer-forms"), "cdsl_pledge": ("security.cdsl_pledge.manage", "cdsl-share-pledge", "cdsl-share-pledges"), "blank_dated_cheque": ("security.blank_cheque.manage", "blank-dated-cheque", "blank-dated-cheques")}
WORKSPACE = "/api/v1/loan-applications/{}/documentation-workspace/"
class AccessDenied(Exception):
    def __init__(self, error_code="FORBIDDEN"): self.error_code = error_code; super().__init__(error_code)
class NotFound(Exception): pass
@dataclass(frozen=True)
class DocumentContent: body: bytes; file_name: str; mime_type: str
@transaction.atomic
def read(*, actor, application_id):
    scope = document_checklist_access.resolve_read_access(actor=actor, application_id=application_id)
    if scope.error_code == "NOT_FOUND": raise NotFound
    if scope.error_code or scope.route != document_checklist_access.ROUTE_POST_SANCTION: raise AccessDenied(scope.error_code or "OBJECT_ACCESS_DENIED")
    application = LoanApplication.objects.select_for_update().select_related("member").filter(pk=application_id).first(); checklist = DocumentChecklist.objects.select_for_update().filter(loan_application=application).first()
    if application is None or checklist is None: raise NotFound
    items = tuple(ChecklistItem.objects.select_for_update().filter(document_checklist=checklist).order_by("display_order", "checklist_item_id")); package = SecurityPackage.objects.select_for_update().filter(loan_application=application).first()
    return _serialize(actor, application, checklist, items, package)
def _serialize(actor, application, checklist, items, package):
    permissions = set(auth_service.effective_permission_codes(actor)); roles = set(auth_service.effective_role_codes(actor)); completed = frozenset(document_checklist_actions.borrower_safe_completed_item_ids(checklist))
    ids = selectors.latest_generated_metadata_by_type(application_id=application.pk, document_types=set(DOCUMENT_TYPES.values())); documents = {row.document_type: row for row in LoanDocument.objects.select_for_update().select_related("document", "document_template").filter(pk__in=ids.values())}
    rows = [_item(actor, application, item, documents.get(DOCUMENT_TYPES[item.item_code]), item.pk in completed, permissions, roles) for item in items]
    approval = checklist_actions.available_approval_action(actor=actor, checklist=checklist, completed_item_ids=completed); actions = []
    if approval: action, suffix = APPROVALS[approval]; actions = [{"action": action, "action_url": f"/api/v1/document-checklists/{checklist.pk}/{suffix}/"}]
    applicable = [row for row in rows if row["applicable"]]; stages = [("company_secretary", checklist.company_secretary_signature_id), ("credit_manager", checklist.credit_manager_signature_id), ("sanction_committee", checklist.sanction_committee_signature_id)]
    return {"snapshot_id": f"{checklist.pk}:{checklist.updated_at.isoformat()}", "loan_application_id": str(application.pk), "application_reference_number": application.application_reference_number, "borrower_name": application.member.display_name, "checklist_status": checklist.checklist_status, "items": rows, "pack_summary": {"status": "ready" if all(row["status"] == "complete" for row in applicable) else "incomplete", "available_count": sum(bool(row["document"]) for row in rows), "missing_count": sum(not row["document"] for row in applicable), "pending_review_count": sum(bool(row["document"] and row["status"] != "complete") for row in applicable)}, "blockers": [{"item_code": row["item_code"], "label": row["item_label"], "reason": row["blocker"] or row["status"]} for row in applicable if row["status"] != ChecklistItem.STATUS_COMPLETE], "security_workflows": _security(package, rows, permissions), "approval_stages": [{"role": role, "status": "signed" if signature else "pending"} for role, signature in stages] + [{"role": "senior_manager_finance", "status": "signed" if checklist.senior_manager_finance_signature_id else "blocked_until_disbursement"}], "available_actions": actions}
def _item(actor, application, item, document, reconciled, permissions, roles):
    status, blocker = item.completion_status, item.applicability_blocker
    if status == ChecklistItem.STATUS_COMPLETE and not reconciled: status, blocker = "blocked", "completion_evidence_stale"
    elif item.applicable_flag and document is None: blocker = blocker or "current_document_missing"
    actions = []
    if document is None: action = _generation(application, item.item_code, permissions, roles); actions = [action] if action else []
    elif status == ChecklistItem.STATUS_PENDING and item.required_flag and item.applicable_flag and "documents.checklist.update" in permissions and roles.intersection({"compliance_team_member", "company_secretary"}): actions.append({"action": "complete_item", "action_url": f"/api/v1/checklist-items/{item.pk}/complete/", "loan_document_id": str(document.pk)})
    if document and document.verification_status != "verified" and "documents.loan_document.verify" in permissions and roles.intersection({"compliance_team_member", "company_secretary"}): actions.append({"action": "verify_document", "action_url": f"/api/v1/loan-documents/{document.pk}/verify/"})
    download = {"file_name": document.document.file_name, "mime_type": document.document.mime_type or "application/octet-stream", "action_url": WORKSPACE.format(application.pk) + f"{item.item_code}/download/"} if document and document_services.user_can_download_documents(actor) else None
    metadata = None if document is None else {"loan_document_id": str(document.pk), "version": document.document_template.template_version, "generation_status": document.generation_status, "execution_status": document.execution_status, "verification_status": document.verification_status, "download": download}
    return {"checklist_item_id": str(item.pk), "item_code": item.item_code, "item_label": item.item_label, "required": item.required_flag, "applicable": item.applicable_flag, "status": status, "blocker": blocker, "stamp_status": item.stamp_status, "notarisation_status": item.notarisation_status, "poa_status": item.poa_status, "document": metadata, "available_actions": actions}
def _generation(application, item_code, permissions, roles):
    if "documents.loan_document.generate" not in permissions or document_services.TEMPLATE_FILE_REFERENCE_PERMISSION not in permissions or not roles.intersection({"compliance_team_member", "company_secretary"}): return None
    from sfpcl_credit.documents.modules import document_templates
    try: variant = document_templates.resolve_borrower_template_variant(application.borrower_type)
    except ValidationError: return None
    kind, today = DOCUMENT_TYPES[item_code], timezone.localdate(); template = DocumentTemplate.objects.filter(document_type=kind, borrower_type=variant, approval_status=DocumentTemplate.STATUS_APPROVED, effective_from__lte=today, template_file__isnull=False).filter(models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=today)).order_by("-effective_from", "-created_at").first()
    return None if template is None else {"action": "generate_document", "action_url": f"/api/v1/loan-applications/{application.pk}/loan-documents/generate/", "document_type": kind, "template_id": str(template.pk), "template_version": template.template_version, "output_formats": ["pdf", "docx"]}
def _workflow(required, status, actions): return {"required": required, "status": status if required else "not_required", "available_actions": actions}
def _from_item(item): return _workflow(item["applicable"], item["status"], item["available_actions"])
def _manage(code, package, row, permissions):
    permission, collection, detail = SECURITY_ACTIONS[code]; return [] if permission not in permissions else [{"action": f"manage_{code}", "action_url": f"/api/v1/{detail}/{row.pk}/" if row else f"/api/v1/security-packages/{package.pk}/{collection}/", "method": "PATCH" if row else "POST"}]
def _security(package, items, permissions):
    by_code = {row["item_code"]: row for row in items}; result = {"tri_party_agreement": _from_item(by_code["tri_party_agreement"]), "cancelled_cheque": _from_item(by_code["cancelled_cheque"])}
    if package is None: result.update({"power_of_attorney": _workflow(True, "pending", []), "sh4": _from_item(by_code["sh4"]), "cdsl_pledge": _from_item(by_code["cdsl_pledge"]), "blank_dated_cheque": _from_item(by_code["blank_dated_cheque"])}); return result
    specs = {"power_of_attorney": (package.poa_required_flag, getattr(package, "power_of_attorney", None), "status"), "sh4": (package.physical_share_security_required_flag, getattr(package, "sh4_share_transfer_form", None), "form_status"), "cdsl_pledge": (package.demat_pledge_required_flag, getattr(package, "cdsl_share_pledge", None), "pledge_status"), "blank_dated_cheque": (package.blank_cheque_required_flag, getattr(package, "blank_dated_cheque", None), "cheque_status")}
    for code, (required, row, field) in specs.items(): result[code] = _workflow(required, getattr(row, field, "pending"), _manage(code, package, row, permissions) if required else [])
    return result
@transaction.atomic
def download(*, actor, application_id, item_code, request, storage=None):
    item = next((row for row in read(actor=actor, application_id=application_id)["items"] if row["item_code"] == item_code), None); document = LoanDocument.objects.select_for_update().select_related("document", "document_template").filter(pk=item["document"]["loan_document_id"]).first() if item and item["document"] and item["document"]["download"] else None
    if document is None: raise NotFound
    scope = {"user_id": str(actor.pk), "loan_application_id": str(application_id), "item_code": item_code, "loan_document_id": str(document.pk)}
    if request.GET.get("content") != "1":
        capability = document_services.issue_download_capability(document=document.document, scope=scope); return {"download_url": WORKSPACE.format(application_id) + f"{item_code}/download/?" + urlencode({"content": "1", "token": capability["token"]}), "expires_at": capability["expires_at"]}
    try: body = document_services.read_with_download_capability(document=document.document, scope=scope, token=request.GET.get("token", ""), storage=storage or LocalDocumentStorage())
    except ValidationError as exc: raise NotFound from exc
    metadata = {"loan_application_id": str(application_id), "loan_document_id": str(document.pk), "document_version": document.document_template.template_version, "document_category": document.document_category, "sensitivity_level": document.document.sensitivity_level, "reason": "staff_documentation_workspace", "request_id": request.headers.get("X-Request-ID"), "outcome": "accepted"}
    document_services.record_document_audit(user=actor, request=request, document=document.document, spec=document_services.DocumentAuditSpec(action=document_services.DOCUMENT_DOWNLOAD_AUDIT_ACTION, actor_type="user", metadata=metadata))
    return DocumentContent(body, document.document.file_name, document.document.mime_type or "application/octet-stream")
