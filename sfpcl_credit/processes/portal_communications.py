"""Member-scoped portal projections for communications and grievance surfaces."""

from datetime import timedelta
from math import ceil

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from sfpcl_credit.compliance.models import Grievance
from sfpcl_credit.compliance.modules.compliance_control_tracker import (
    ComplianceConflict,
    ComplianceInvalid,
)
from sfpcl_credit.compliance.modules.grievance_workflow import GrievanceWorkflow
from sfpcl_credit.communications import services as communication_services
from sfpcl_credit.communications.models import Communication
from sfpcl_credit.identity.models import PortalAccount, User
from sfpcl_credit.members.modules.member_authority import evaluate_member_authority

def portal_account_for(actor):
    return (
        PortalAccount.objects.select_related("member")
        .filter(
            user=actor,
            status=PortalAccount.STATUS_ACTIVE,
            member__is_deleted=False,
        )
        .first()
    )


def create_grievance(*, actor, payload, idempotency_key):
    account = portal_account_for(actor)
    if account is None:
        raise PermissionError
    if not isinstance(payload, dict):
        raise ComplianceInvalid({"request": "A JSON object is required."})
    allowed = {
        "grievance_category",
        "subject",
        "description",
        "loan_account_id",
        "loan_application_id",
    }
    unknown = set(payload) - allowed
    if unknown:
        raise ComplianceInvalid(
            {field: "Unsupported grievance field." for field in unknown}
        )
    subject = _required_text(payload, "subject", max_length=255)
    description = _required_text(payload, "description")
    category = _required_text(payload, "grievance_category", max_length=100)
    if category not in Grievance.CATEGORIES:
        raise ComplianceInvalid({"grievance_category": "Unsupported grievance category."})
    tat_days = getattr(settings, "PORTAL_GRIEVANCE_TAT_DAYS", None)
    owner_role = getattr(settings, "PORTAL_GRIEVANCE_OWNER_ROLE_CODE", None)
    if not isinstance(tat_days, int) or tat_days < 1 or not owner_role:
        raise ComplianceConflict(
            "Portal grievance owner and TAT configuration is required."
        )
    owner = _configured_owner(account=account, role_code=owner_role)
    if owner is None:
        raise ComplianceConflict(
            "No active configured grievance owner is available for this member."
        )
    today = timezone.localdate()
    owner_payload = {
        "grievance_category": category,
        "description": f"[Portal subject] {subject}\n\n{description}",
        "received_date": today.isoformat(),
        "received_channel": "portal",
        "assigned_to_user_id": str(owner.pk),
        "resolution_due_date": (today + timedelta(days=tat_days)).isoformat(),
        "supporting_document_ids": [],
    }
    for field in ("loan_account_id", "loan_application_id"):
        if payload.get(field):
            owner_payload[field] = payload[field]
    return GrievanceWorkflow.create_for_borrower(
        portal_account=account,
        payload=owner_payload,
        idempotency_key=idempotency_key,
    )


def list_grievances(*, actor, query):
    account = portal_account_for(actor)
    if account is None:
        raise PermissionError
    return GrievanceWorkflow.list_for_borrower(portal_account=account, query=query)


def grievance_detail(*, actor, grievance_id):
    account = portal_account_for(actor)
    if account is None:
        raise PermissionError
    return GrievanceWorkflow.retrieve_for_borrower(
        portal_account=account, grievance_id=grievance_id
    )


def list_notifications(*, actor, query):
    if portal_account_for(actor) is None:
        raise PermissionError
    return communication_services.paginated_portal_notifications(actor, query)


def mark_notification_read(*, actor, notification_id, payload, request):
    if portal_account_for(actor) is None:
        raise PermissionError
    return communication_services.mark_portal_notification_read(
        actor, request, notification_id, payload
    )


def list_notices(*, actor, query):
    account = portal_account_for(actor)
    if account is None:
        raise PermissionError
    page, page_size = _pagination(query)
    queryset = (
        Communication.objects.filter(
            recipient_party_id=account.member_id,
            recipient_party_type__in=("borrower", "member"),
        )
        .select_related("content_template")
        .order_by("-sent_at", "-communication_id")
    )
    total = queryset.count()
    total_pages = max(1, ceil(total / page_size))
    rows = queryset[(page - 1) * page_size : page * page_size]
    return (
        [_notice_projection(row) for row in rows],
        {
            "page": page,
            "page_size": page_size,
            "total_count": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        },
    )


def list_closures(*, actor, query):
    account = portal_account_for(actor)
    if account is None:
        raise PermissionError
    page, page_size = _pagination(query)
    from sfpcl_credit.loans.models import LoanAccount

    queryset = (
        LoanAccount.objects.filter(member_id=account.member_id)
        .select_related("loan_closure")
        .prefetch_related(
            "loan_closure__requirements",
            "loan_closure__security_return__items",
        )
        .order_by("-created_at", "-loan_account_id")
    )
    total = queryset.count()
    total_pages = max(1, ceil(total / page_size))
    rows = queryset[(page - 1) * page_size : page * page_size]
    return (
        [_closure_projection(row) for row in rows],
        {
            "page": page,
            "page_size": page_size,
            "total_count": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        },
    )


def download_notice(*, actor, communication_id, request):
    account = portal_account_for(actor)
    if account is None:
        raise PermissionError
    communication = Communication.objects.filter(
        pk=communication_id,
        recipient_party_id=account.member_id,
        recipient_party_type__in=("borrower", "member"),
    ).first()
    if communication is None:
        raise ObjectDoesNotExist
    document_id = None
    try:
        document_id = communication.noc.document_id
    except ObjectDoesNotExist:
        try:
            invoice = communication.interest_invoice
        except ObjectDoesNotExist:
            invoice = None
        if invoice is not None:
            document_id = invoice.document_id
    if document_id is None:
        raise ObjectDoesNotExist
    from sfpcl_credit.documents.services import download_document_file

    return download_document_file(actor, request, document_id)


def _configured_owner(*, account, role_code):
    candidates = User.objects.filter(
        status="active",
        primary_role__status="active",
        primary_role__role_code=role_code,
    ).order_by("user_id")
    for candidate in candidates:
        authority = evaluate_member_authority(
            actor_user=candidate,
            member=account.member,
            permission=GrievanceWorkflow.READ_PERMISSION,
        )
        if authority.allowed:
            return candidate
    return None

def _required_text(payload, field, *, max_length=None):
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ComplianceInvalid({field: "This field is required."})
    value = value.strip()
    if max_length and len(value) > max_length:
        raise ComplianceInvalid({field: f"Must not exceed {max_length} characters."})
    return value

def _pagination(query):
    unknown = set(query.keys()) - {"page", "page_size"}
    if unknown:
        raise ComplianceInvalid(
            {field: "Unsupported portal filter." for field in unknown}
        )
    try:
        page = int(query.get("page", 1))
        page_size = int(query.get("page_size", 20))
    except (TypeError, ValueError) as exc:
        raise ComplianceInvalid(
            {"page": "Pagination values must be positive integers."}
        ) from exc
    if page < 1 or page_size < 1 or page_size > 100:
        raise ComplianceInvalid({"page": "Pagination values are out of range."})
    return page, page_size

def _notice_projection(row):
    notice_type = _notice_type(row)
    download_url = None
    loan_account_id = None
    related_reference = None
    issued_at = row.sent_at
    if notice_type == "noc":
        noc = row.noc
        loan_account_id = str(noc.loan_account_id)
        related_reference = noc.loan_account_number_snapshot
        issued_at = issued_at or noc.issued_at
        download_url = f"/api/v1/portal/notices/{row.pk}/download/"
    elif notice_type == "interest_invoice":
        invoice = row.interest_invoice
        loan_account_id = str(invoice.loan_account_id)
        related_reference = invoice.loan_account_number
        issued_at = issued_at or invoice.issued_at or invoice.generated_at
        if invoice.document_id is not None:
            download_url = f"/api/v1/portal/notices/{row.pk}/download/"
    elif notice_type == "reminder":
        reminder = row.monitoring_reminder
        loan_account_id = str(reminder.loan_account_id)
        related_reference = reminder.loan_account.loan_account_number
        issued_at = issued_at or reminder.created_at
    return {
        "notice_id": str(row.pk),
        "notice_type": notice_type,
        "title": row.subject_snapshot or notice_type.replace("_", " ").title(),
        "message": row.body_snapshot,
        "status": "sent" if row.sent_at else row.delivery_status,
        "issued_at": issued_at.isoformat() if issued_at else None,
        "related_entity_type": row.related_entity_type,
        "related_entity_id": str(row.related_entity_id),
        "related_loan_account_id": loan_account_id,
        "related_reference": related_reference,
        "download_url": download_url,
    }

def _notice_type(row):
    for relation, notice_type in (
        ("noc", "noc"),
        ("interest_invoice", "interest_invoice"),
        ("monitoring_reminder", "reminder"),
    ):
        try:
            getattr(row, relation)
        except ObjectDoesNotExist:
            continue
        return notice_type
    code = row.content_template.template_code if row.content_template_id else ""
    for token, notice_type in (
        ("deficien", "deficiency_note"),
        ("reject", "rejection_note"),
        ("sanction", "sanction_letter"),
        ("reminder", "reminder"),
        ("invoice", "interest_invoice"),
        ("noc", "noc"),
    ):
        if token in code.lower():
            return notice_type
    return "borrower_communication"

def _closure_projection(loan):
    try:
        closure = loan.loan_closure
    except ObjectDoesNotExist:
        closure = None
    noc = None
    security_return = None
    if closure is not None:
        try:
            noc = closure.noc
        except ObjectDoesNotExist:
            pass
        try:
            security_return = closure.security_return
        except ObjectDoesNotExist:
            pass
    cdsl_status = "pending"
    security_status = "pending"
    security_items = []
    if security_return is not None:
        security_status = security_return.return_status
        security_items = [
            {
                "item_type": item.item_type,
                "status": item.item_status,
                "acknowledgement_available": item.acknowledgement_document_id is not None,
            }
            for item in security_return.items.all()
        ]
        cdsl_item = next(
            (item for item in security_items if item["item_type"] == "cdsl"), None
        )
        if cdsl_item is not None:
            cdsl_status = cdsl_item["status"]
    return {
        "loan_account_id": str(loan.pk),
        "loan_account_number": loan.loan_account_number,
        "full_repayment_status": "confirmed" if closure is not None else "pending",
        "closure_review_status": "complete" if closure is not None else "not_started",
        "closed_at": closure.closed_at.isoformat() if closure is not None else None,
        "noc_status": "issued" if noc is not None else "pending",
        "noc_download_url": (
            f"/api/v1/portal/notices/{noc.communication_id}/download/"
            if noc is not None and noc.communication_id is not None
            else None
        ),
        "security_return_status": security_status,
        "cdsl_unpledge_status": cdsl_status,
        "security_items": security_items,
    }
