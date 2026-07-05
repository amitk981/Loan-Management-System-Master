from django.core.exceptions import ValidationError

from sfpcl_credit.identity.modules import auth_service


DASHBOARD_READ_PERMISSION = "management_readonly"

_ROLE_CONTEXTS = {
    "credit_manager": "credit_manager",
    "cfo": "sanction_committee",
    "director": "sanction_committee",
    "company_secretary": "compliance",
    "compliance_team_member": "compliance",
    "internal_auditor": "compliance",
    "senior_manager_finance": "treasury",
    "chief_financial_controller": "treasury",
    "accounts_head": "treasury",
    "management_viewer": "management",
}

_CARD_DEFINITIONS = {
    "credit_manager": [
        (
            "applications_pending_completeness",
            "Applications pending completeness",
            "/applications?status=pending_completeness",
        ),
        (
            "deficiencies_pending_resolution",
            "Deficiencies pending resolution",
            "/applications/deficiencies",
        ),
        ("appraisals_due_today", "Appraisals due today", "/credit/appraisals?due=today"),
        (
            "appraisals_breaching_two_day_tat",
            "Appraisals breaching two-day TAT",
            "/credit/appraisals?tat=breaching",
        ),
        (
            "credit_manager_review_queue",
            "Credit Manager review queue",
            "/credit/review-queue",
        ),
        (
            "rejected_applications",
            "Rejected applications",
            "/applications?status=rejected",
        ),
        (
            "loans_outstanding_beyond_one_year",
            "Loans outstanding beyond one year",
            "/monitoring/outstanding-beyond-one-year",
        ),
        ("dpd_buckets", "DPD buckets", "/monitoring/dpd"),
        ("reminder_queue", "Reminder queue", "/monitoring/reminders"),
        ("default_assessment_queue", "Default assessment queue", "/defaults/assessments"),
    ],
    "sanction_committee": [
        (
            "cases_pending_review",
            "Cases pending review",
            "/sanctions?status=pending_review",
        ),
        (
            "cases_returned_for_clarification",
            "Cases returned for clarification",
            "/sanctions?status=returned",
        ),
        ("exceptions_pending_decision", "Exceptions pending decision", "/sanctions/exceptions"),
        ("sanctions_approved_today", "Sanctions approved today", "/sanctions?approved=today"),
    ],
    "compliance": [
        (
            "documents_pending_generation",
            "Documents pending generation",
            "/documents?status=pending_generation",
        ),
        (
            "documents_pending_signature",
            "Documents pending signature",
            "/documents?status=pending_signature",
        ),
        (
            "security_items_pending_custody",
            "Security items pending custody",
            "/security/custody",
        ),
        ("compliance_tasks_due", "Compliance tasks due", "/compliance/tasks?due=now"),
        ("section186_items_pending", "Section 186 items pending", "/compliance/section-186"),
        ("nbfc_tests_due", "NBFC principal tests due", "/compliance/nbfc-tests"),
    ],
    "treasury": [
        (
            "sap_requests_pending",
            "SAP requests pending",
            "/finance/sap-requests?status=pending",
        ),
        (
            "customer_codes_pending",
            "Customer codes pending",
            "/finance/customer-codes?status=pending",
        ),
        (
            "disbursements_pending_readiness",
            "Disbursements pending readiness",
            "/finance/disbursements?stage=readiness",
        ),
        (
            "disbursements_pending_authorisation",
            "Disbursements pending authorisation",
            "/finance/disbursements?stage=authorisation",
        ),
        (
            "repayments_pending_allocation",
            "Repayments pending allocation",
            "/finance/repayments?status=pending_allocation",
        ),
        ("interest_invoices_due", "Interest invoices due", "/finance/interest-invoices?due=now"),
    ],
    "management": [
        ("portfolio_outstanding", "Portfolio outstanding", "/reports/portfolio"),
        ("applications_pipeline", "Applications pipeline", "/reports/application-pipeline"),
        ("dpd_summary", "DPD summary", "/reports/dpd"),
        ("compliance_summary", "Compliance summary", "/reports/compliance"),
        ("approvals_summary", "Approvals summary", "/reports/approvals"),
        ("treasury_summary", "Treasury summary", "/reports/treasury"),
    ],
}


def user_can_read_dashboard(user):
    return DASHBOARD_READ_PERMISSION in auth_service.effective_permission_codes(user)


def dashboard_summary(user, query_params):
    unknown = set(query_params.keys())
    if unknown:
        raise ValidationError(
            {param: "Unknown query parameter." for param in sorted(unknown)}
        )

    role_context = _role_context_for_user(user)
    return {
        "role_context": role_context,
        "cards": [_card_payload(card) for card in _CARD_DEFINITIONS[role_context]],
        "tasks": [],
    }


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}


def _role_context_for_user(user):
    role_code = user.primary_role.role_code if user.primary_role_id else ""
    return _ROLE_CONTEXTS.get(role_code, "management")


def _card_payload(card_definition):
    code, label, link = card_definition
    return {"code": code, "label": label, "count": 0, "link": link}


__all__ = [
    "DASHBOARD_READ_PERMISSION",
    "dashboard_summary",
    "user_can_read_dashboard",
    "validation_field_errors",
]
