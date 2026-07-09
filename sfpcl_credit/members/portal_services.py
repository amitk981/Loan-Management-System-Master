from sfpcl_credit.applications.models import ApplicationDeficiency, LoanApplication
from sfpcl_credit.identity.models import PortalAccount
from sfpcl_credit.members import services as member_services
from sfpcl_credit.members.models import BankAccount, KycProfile


PORTAL_PERMISSION_ERROR = "Borrower portal data is available only to active member portal users."


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
    return {
        "member_id": str(member.member_id),
        "records": [],
        "summary": {"continuous_supply_years": None, "total_quantity": None, "total_value": None},
        "source_status": "model_not_implemented",
    }


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
