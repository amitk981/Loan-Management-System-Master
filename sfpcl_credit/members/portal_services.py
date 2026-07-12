from sfpcl_credit.applications import services as application_services
from sfpcl_credit.applications.models import ApplicationDeficiency, LoanApplication
from sfpcl_credit.identity.models import PortalAccount
from sfpcl_credit.members import services as member_services
from django.db.models import Sum

from sfpcl_credit.members.models import BankAccount, KycProfile, ProduceSupplyRecord
from sfpcl_credit.members.modules.active_member_status import ActiveMemberStatusModule


PORTAL_PERMISSION_ERROR = "Borrower portal data is available only to active member portal users."
PORTAL_OBJECT_ACCESS_ERROR = "This application does not belong to the authenticated portal member."


def portal_member_for_user(user):
    account = (
        PortalAccount.objects.select_related("member")
        .filter(user=user, status=PortalAccount.STATUS_ACTIVE, member__is_deleted=False)
        .first()
    )
    return account.member if account else None


def dashboard_summary(member):
    applications = LoanApplication.objects.filter(member=member)
    open_deficiencies = ApplicationDeficiency.objects.filter(
        loan_application__member=member,
        resolution_status=ApplicationDeficiency.STATUS_OPEN,
    ).count()
    return {
        "member": _member_snapshot(member),
        "application_counts": {
            "total": applications.count(),
            "draft": applications.filter(application_status=LoanApplication.STATUS_DRAFT).count(),
            "submitted": applications.filter(application_status=LoanApplication.STATUS_SUBMITTED).count(),
            "incomplete_returned": applications.filter(
                application_status=LoanApplication.STATUS_INCOMPLETE_RETURNED
            ).count(),
            "reference_generated": applications.filter(
                application_status=LoanApplication.STATUS_REFERENCE_GENERATED
            ).count(),
        },
        "loan_counts": {"active": 0, "closed": 0, "overdue": 0},
        "pending_actions": {
            "open_deficiencies": open_deficiencies,
            "signature_pending": 0,
            "repayment_due": 0,
            "kyc_update_due": 1 if member.kyc_status == "rekyc_due" else 0,
            "closure_actions": 0,
        },
        "notices": [],
    }


def profile(member, user):
    return {
        "member": _portal_masked_member(member, user),
        "nominees": [member_services.serialize_nominee(row) for row in member.nominees.all()],
        "shareholdings": [
            member_services.serialize_shareholding(row) for row in member.shareholdings.all()
        ],
        "land_holdings": [
            member_services.serialize_land_holding(row) for row in member.land_holdings.all()
        ],
        "crop_plans": [
            member_services.serialize_crop_plan(row) for row in member.crop_plans.all()
        ],
        "kyc_profile": _kyc_profile(member),
        "bank_accounts": [
            member_services.serialize_bank_account(row)
            for row in BankAccount.objects.filter(
                owner_party_type="member", owner_party_id=member.member_id
            ).order_by("created_at", "bank_account_id")
        ],
        "cancelled_cheques": [
            member_services.serialize_cancelled_cheque(row)
            for row in member.cancelled_cheques.order_by("created_at", "cancelled_cheque_id")
        ],
    }


def produce_supply(member):
    records = list(
        ProduceSupplyRecord.objects.filter(member=member).order_by("-financial_year", "produce_supply_record_id")
    )
    status = ActiveMemberStatusModule().calculate(member_id=member.member_id)
    qualifying_ids = {row.produce_supply_record_id for row in status.supply_rows if row.qualifying}
    qualifying_records = [row for row in records if str(row.produce_supply_record_id) in qualifying_ids]
    totals = ProduceSupplyRecord.objects.filter(
        produce_supply_record_id__in=[row.produce_supply_record_id for row in qualifying_records]
    ).aggregate(total_quantity=Sum("quantity"), total_value=Sum("value_amount"))
    return {
        "records": [member_services.serialize_produce_supply_record(row, portal=True) for row in records],
        "summary": {
            "continuous_supply_years": str(status.continuous_supply_years),
            "total_quantity": f"{totals['total_quantity']:.3f}" if totals["total_quantity"] is not None else None,
            "total_value": f"{totals['total_value']:.2f}" if totals["total_value"] is not None else None,
        },
        "source_status": "persisted_qualifying_verified_records" if qualifying_records else "persisted_no_qualifying_verified_records",
    }


class PortalObjectAccessError(Exception):
    pass


def list_applications(member):
    applications = (
        LoanApplication.objects.select_related("member")
        .filter(member=member)
        .order_by("-updated_at", "-created_at", "-loan_application_id")
    )
    return {"items": [_portal_application_summary(application) for application in applications]}


def get_application_for_member(member, loan_application_id):
    application = application_services.get_application(loan_application_id)
    if application is None:
        return None
    if application.member_id != member.member_id:
        raise PortalObjectAccessError(PORTAL_OBJECT_ACCESS_ERROR)
    return application


def create_application(member, payload, actor, request_ip="", request_user_agent="", request_id=None):
    requested_member_id = payload.get("member_id")
    if requested_member_id and str(requested_member_id) != str(member.member_id):
        raise PortalObjectAccessError(PORTAL_OBJECT_ACCESS_ERROR)
    scoped_payload = {**payload, "member_id": str(member.member_id)}
    application = application_services.create_draft(
        scoped_payload,
        actor,
        request_ip,
        request_user_agent,
        request_id,
        audit_action="portal.application.draft_created",
    )
    return _portal_application_detail(application)


def update_application(application, payload, actor, request_ip="", request_user_agent="", request_id=None):
    if "member_id" in payload and str(payload["member_id"]) != str(application.member_id):
        raise PortalObjectAccessError(PORTAL_OBJECT_ACCESS_ERROR)
    scoped_payload = {key: value for key, value in payload.items() if key != "member_id"}
    application = application_services.update_draft(
        application,
        scoped_payload,
        actor,
        request_ip,
        request_user_agent,
        request_id,
        audit_action="portal.application.saved",
    )
    return _portal_application_detail(application)


def submit_application(application, actor, request_ip="", request_user_agent="", request_id=None):
    application = application_services.submit_application(
        application,
        actor,
        request_ip,
        request_user_agent,
        request_id,
        actor_permissions=[application_services.APPLICATION_SUBMIT_PERMISSION],
        audit_action="portal.application.submitted",
    )
    return _portal_application_detail(application)


def application_detail(application):
    return _portal_application_detail(application)


def _member_snapshot(member):
    serialized = member_services.serialize_member(member)
    return {
        "member_id": serialized["member_id"],
        "display_name": serialized["display_name"],
        "member_number": serialized["member_number"],
        "folio_number": serialized["folio_number"],
        "member_type": serialized["member_type"],
        "membership_status": serialized["membership_status"],
        "kyc_status": serialized["kyc_status"],
        "default_status": serialized["default_status"],
        "share_summary": serialized["share_summary"],
        "active_member_status": serialized["active_member_status"],
    }


def _portal_masked_member(member, user):
    data = member_services.serialize_member_profile(member, user)
    data["pan"]["can_view_full"] = False
    data["aadhaar"]["can_view_full"] = False
    return data


def _kyc_profile(member):
    profile = (
        KycProfile.objects.prefetch_related("documents__document_file")
        .filter(party_type="member", party_id=member.member_id)
        .first()
    )
    return member_services.serialize_kyc_profile(profile) if profile else None


def _portal_application_summary(application):
    return {
        "loan_application_id": str(application.loan_application_id),
        "application_reference_number": application.application_reference_number,
        "display_reference": application.application_reference_number
        or str(application.loan_application_id)[:8].upper(),
        "application_date": application.application_date.isoformat(),
        "submitted_at": _datetime(application.submitted_at),
        "required_loan_amount": _money(application.required_loan_amount),
        "declared_purpose": application.declared_purpose,
        "purpose_category": application.purpose_category,
        "loan_type_requested": application.loan_type_requested or None,
        "application_status": application.application_status,
        "current_stage": application.current_stage,
        "completeness_status": application.completeness_status,
        "pending_with": _pending_with(application),
        "borrower_action": _borrower_action(application),
        "open_deficiency_count": _open_deficiency_count(application),
        "created_at": _datetime(application.created_at),
        "updated_at": _datetime(application.updated_at),
    }


def _portal_application_detail(application):
    summary = _portal_application_summary(application)
    deficiencies = [
        application_services.serialize_application_deficiency(deficiency)
        for deficiency in application_services.list_application_deficiencies(application)
        if deficiency.resolution_status == ApplicationDeficiency.STATUS_OPEN
    ]
    return {
        **summary,
        "member": _member_snapshot(application.member),
        "requested_tenure_months": application.requested_tenure_months,
        "nominee": application_services.serialize_application_nominee(application.nominee),
        "borrower_request_notes": application.borrower_request_notes,
        "terms_acceptance_flag": application.terms_acceptance_flag,
        "timeline": _application_timeline(application),
        "deficiencies": deficiencies,
    }


def _pending_with(application):
    if application.application_status in {
        LoanApplication.STATUS_DRAFT,
        LoanApplication.STATUS_INCOMPLETE_RETURNED,
    }:
        return "Borrower"
    return "SFPCL"


def _borrower_action(application):
    if application.application_status == LoanApplication.STATUS_DRAFT:
        return "Continue draft"
    if application.application_status == LoanApplication.STATUS_INCOMPLETE_RETURNED:
        return "Review deficiencies"
    return "No action required"


def _open_deficiency_count(application):
    return ApplicationDeficiency.objects.filter(
        loan_application=application,
        resolution_status=ApplicationDeficiency.STATUS_OPEN,
    ).count()


def _application_timeline(application):
    events = [
        {
            "event": "Draft created",
            "at": _datetime(application.created_at),
            "owner": "Borrower",
        }
    ]
    if application.submitted_at:
        events.append(
            {
                "event": "Application submitted",
                "at": _datetime(application.submitted_at),
                "owner": "Borrower",
            }
        )
    if application.application_status == LoanApplication.STATUS_INCOMPLETE_RETURNED:
        events.append(
            {
                "event": "Deficiency raised",
                "at": _datetime(application.updated_at),
                "owner": "SFPCL",
            }
        )
    return events


def _money(value):
    return f"{value:.2f}" if value is not None else None


def _datetime(value):
    return value.isoformat().replace("+00:00", "Z") if value else None
