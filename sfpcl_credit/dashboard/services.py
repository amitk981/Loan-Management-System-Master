from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.http import QueryDict
from django.utils import timezone

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
            "/applications?status=submitted&current_stage=initial_loan_request",
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
            "/sanctions?current_status=pending",
        ),
        (
            "cases_returned_for_clarification",
            "Cases returned for clarification",
            "/sanctions?current_status=returned_for_clarification",
        ),
        ("exceptions_pending_decision", "Exceptions pending decision", "/sanctions/exceptions"),
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
        ("compliance_tasks_due", "Compliance tasks due", "/compliance/tasks?task_status=due"),
    ],
    "treasury": [
        (
            "sap_requests_pending",
            "SAP requests pending",
            "/finance/sap-requests?request_status=draft",
        ),
        (
            "customer_codes_pending",
            "Customer codes pending",
            "/finance/customer-codes?request_status=sent",
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

_ROLE_CARD_DEFINITIONS = {
    "cfo": [
        *_CARD_DEFINITIONS["sanction_committee"],
        ("loans_above_five_lakh", "Loans above ₹5 lakh", "/reports?report=loan-portfolio&minimum_sanctioned_amount=500000"),
        ("portfolio_outstanding", "Portfolio outstanding", "/reports?report=loan-portfolio"),
        ("dpd_summary", "DPD summary", "/reports?report=dpd"),
        ("section186_items_pending", "Section 186 utilisation", "/reports?report=section-186&review_status=pending"),
        ("nbfc_tests_due", "NBFC principal test", "/reports?report=nbfc-test&review_status=pending"),
        ("recovery_decisions_pending", "Recovery decisions", "/defaults?status=recovery_decision_pending"),
    ],
    "accounts_head": [
        ("repayments_pending_posting", "Repayments pending posting", "/repayments?sap_posting_status=pending"),
        ("interest_invoices_pending", "Interest invoices pending", "/interest?invoice_status=draft"),
        ("accruals_pending", "Accruals pending", "/interest?posted_status=pending"),
        ("reconciliation_breaks", "Reconciliation breaks", "/repayments?match_status=unmatched"),
    ],
    "company_secretary": [
        *_CARD_DEFINITIONS["compliance"],
        ("board_approvals_required", "Board approvals required", "/sanctions?current_status=pending"),
        ("grievance_open_cases", "Grievance open cases", "/compliance/grievances?status=open"),
        ("archival_due", "Archival due", "/compliance/archive?status=due"),
    ],
    "internal_auditor": [
        ("compliance_tasks_due", "Compliance tasks due", "/compliance/tasks?task_status=due"),
        ("section186_items_pending", "Section 186 items pending", "/compliance/section-186"),
        ("nbfc_tests_due", "NBFC principal tests due", "/compliance/nbfc-tests"),
    ],
}

_CARD_PERMISSION = {
    "applications_pending_completeness": "applications.loan_application.read",
    "deficiencies_pending_resolution": "applications.loan_application.read",
    "appraisals_due_today": "credit.appraisal.review",
    "appraisals_breaching_two_day_tat": "credit.appraisal.review",
    "credit_manager_review_queue": "credit.appraisal.review",
    "rejected_applications": "applications.loan_application.read",
    "loans_outstanding_beyond_one_year": "finance.loan_account.read",
    "dpd_buckets": "monitoring.dpd.read",
    "reminder_queue": "monitoring.reminder.create",
    "default_assessment_queue": "defaults.case.read",
    "cases_pending_review": "approvals.case.read",
    "cases_returned_for_clarification": "approvals.case.read",
    "exceptions_pending_decision": "approvals.exception_register.read",
    "sanctions_approved_today": "approvals.case.read",
    "loans_above_five_lakh": "finance.loan_account.read",
    "portfolio_outstanding": "finance.loan_account.read",
    "dpd_summary": "monitoring.dpd.read",
    "section186_items_pending": "compliance.section186.read",
    "nbfc_tests_due": "compliance.nbfc_test.read",
    "recovery_decisions_pending": "defaults.case.read",
    "documents_pending_generation": "documents.checklist.read",
    "documents_pending_signature": "documents.checklist.read",
    "security_items_pending_custody": "security.package.read",
    "compliance_tasks_due": "compliance.task.read",
    "board_approvals_required": "approvals.case.read",
    "grievance_open_cases": "compliance.grievance.read",
    "archival_due": "closure.archive.read",
    "sap_requests_pending": "finance.sap_code.read",
    "customer_codes_pending": "finance.sap_code.read",
    "disbursements_pending_readiness": "finance.disbursement.readiness",
    "disbursements_pending_authorisation": "finance.disbursement.readiness",
    "repayments_pending_allocation": "finance.loan_account.read",
    "interest_invoices_due": "finance.loan_account.read",
    "repayments_pending_posting": "finance.loan_account.read",
    "interest_invoices_pending": "finance.loan_account.read",
    "accruals_pending": "finance.loan_account.read",
    "reconciliation_breaks": "finance.bank_statement.read",
}


class DashboardPermissionDenied(Exception):
    """The actor cannot read the resolved or requested dashboard context."""


def user_can_read_dashboard(user, permission_codes=None):
    permissions = (
        permission_codes
        if permission_codes is not None
        else auth_service.effective_permission_codes(user)
    )
    return DASHBOARD_READ_PERMISSION in permissions


def dashboard_summary(
    user,
    query_params,
    *,
    expected_context=None,
    permission_codes=None,
):
    unknown = set(query_params.keys())
    if unknown:
        raise ValidationError(
            {param: "Unknown query parameter." for param in sorted(unknown)}
        )

    role_context = _role_context_for_user(user)
    if role_context is None or (
        expected_context is not None and role_context != expected_context
    ):
        raise DashboardPermissionDenied
    permissions = set(
        permission_codes
        if permission_codes is not None
        else auth_service.effective_permission_codes(user)
    )
    role_code = user.primary_role.role_code
    definitions = [
        card
        for card in _ROLE_CARD_DEFINITIONS.get(
            role_code,
            _CARD_DEFINITIONS[role_context],
        )
        if (
            _CARD_PERMISSION.get(card[0]) in permissions
            and _card_scope_is_available(user, card[0])
        )
    ]
    requested_codes = {card[0] for card in definitions}
    batched_counts = _batched_card_counts(user, role_context, requested_codes)
    return {
        "role_context": role_context,
        "cards": [
            _card_payload(card, batched_counts)
            for card in definitions
        ],
        "tasks": [],
    }


def validation_field_errors(exc):
    if hasattr(exc, "message_dict"):
        return {field: messages[0] for field, messages in exc.message_dict.items()}
    return {"non_field_errors": str(exc)}


def _role_context_for_user(user):
    role_code = user.primary_role.role_code if user.primary_role_id else ""
    if user.primary_role.status != "active":
        return None
    return _ROLE_CONTEXTS.get(role_code)


def _card_payload(card_definition, batched_counts):
    code, label, link = card_definition
    return {"code": code, "label": label, "count": batched_counts[code], "link": link}


def _card_scope_is_available(user, code):
    if code != "archival_due":
        return True
    from sfpcl_credit.closure.modules.loan_closure import (
        ClosurePermissionDenied,
        pending_archive_requirements,
    )

    try:
        pending_archive_requirements(actor=user)
    except ClosurePermissionDenied:
        return False
    return True


def _selector_total(selector, *, actor, **filters):
    """Count a worklist through its canonical permission and object-scope selector."""
    query_params = QueryDict("", mutable=True)
    query_params.update({key: str(value) for key, value in filters.items()})
    query_params["page_size"] = "1"
    _rows, pagination = selector(actor=actor, query_params=query_params)
    return pagination["total_count"]


def _batched_card_counts(user, role_context, requested_codes):
    if not requested_codes:
        return {}
    if role_context == "credit_manager":
        return _credit_card_counts(user, requested_codes)
    if role_context == "sanction_committee":
        return _sanction_card_counts(user, requested_codes)
    if role_context == "compliance":
        return _compliance_card_counts(user, requested_codes)
    if role_context == "treasury":
        return _treasury_card_counts(user, requested_codes)
    return {}


def _credit_application_scope(user):
    from sfpcl_credit.applications.models import LoanApplication

    return LoanApplication.objects.filter(
        Q(current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT)
        | Q(created_by_user=user)
        | Q(received_by_user=user)
    )


def _credit_card_counts(user, requested_codes):
    from sfpcl_credit.applications.models import (
        ApplicationDeficiency,
        LoanApplication,
    )
    from sfpcl_credit.credit.models import LoanAppraisalNote
    from sfpcl_credit.defaults.models import DefaultCase
    from sfpcl_credit.loans.modules.loan_account_read import scoped_account_candidates
    from sfpcl_credit.monitoring.models import Reminder

    applications = _credit_application_scope(user)
    application_counts = applications.aggregate(
        pending_completeness=Count(
            "pk",
            filter=Q(
                application_status=LoanApplication.STATUS_SUBMITTED,
                current_stage=LoanApplication.STAGE_INITIAL,
            ),
        ),
        rejected=Count(
            "pk",
            filter=Q(
                application_status=LoanApplication.STATUS_REJECTED_BY_SANCTION,
            ),
        ),
    )
    appraisal_counts = LoanAppraisalNote.objects.filter(
        loan_application__in=applications
    ).aggregate(
        due_today=Count(
            "pk",
            filter=Q(
                appraisal_status=LoanAppraisalNote.STATUS_REVIEW_PENDING,
                tat_due_at__date=timezone.localdate(),
            ),
        ),
        breached=Count(
            "pk",
            filter=Q(
                appraisal_status=LoanAppraisalNote.STATUS_REVIEW_PENDING,
                tat_status=LoanAppraisalNote.TAT_BREACHED,
            ),
        ),
        review_queue=Count(
            "pk",
            filter=Q(appraisal_status=LoanAppraisalNote.STATUS_REVIEW_PENDING),
        ),
    )
    counts = {
        "applications_pending_completeness": application_counts["pending_completeness"],
        "deficiencies_pending_resolution": ApplicationDeficiency.objects.filter(
            loan_application__in=applications,
            resolution_status=ApplicationDeficiency.STATUS_OPEN,
        ).count(),
        "appraisals_due_today": appraisal_counts["due_today"],
        "appraisals_breaching_two_day_tat": appraisal_counts["breached"],
        "credit_manager_review_queue": appraisal_counts["review_queue"],
        "rejected_applications": application_counts["rejected"],
        "loans_outstanding_beyond_one_year": 0,
        "dpd_buckets": 0,
        "reminder_queue": 0,
        "default_assessment_queue": 0,
    }
    account_codes = {
        "loans_outstanding_beyond_one_year",
        "dpd_buckets",
        "reminder_queue",
        "default_assessment_queue",
    }
    if not requested_codes.intersection(account_codes):
        return {code: counts[code] for code in requested_codes}
    accounts = scoped_account_candidates(actor=user)
    account_counts = accounts.aggregate(
        old_outstanding=Count(
            "pk",
            filter=Q(
                total_outstanding__gt=0,
                created_at__date__lt=timezone.localdate()
                - timezone.timedelta(days=365),
            ),
        ),
        dpd=Count(
            "pk",
            filter=Q(current_dpd_status__days_past_due__gt=0),
        ),
    )
    counts.update(
        {
            "loans_outstanding_beyond_one_year": account_counts["old_outstanding"],
            "dpd_buckets": account_counts["dpd"],
            "reminder_queue": Reminder.objects.filter(
                loan_account__in=accounts,
                delivery_status__in=(Reminder.STATUS_QUEUED, Reminder.STATUS_FAILED),
            ).count(),
            "default_assessment_queue": DefaultCase.objects.filter(
                loan_account__in=accounts,
                default_case_status=DefaultCase.STATUS_ASSESSMENT_IN_PROGRESS,
            ).count(),
        }
    )
    return {code: counts[code] for code in requested_codes}


def _sanction_card_counts(user, requested_codes):
    from sfpcl_credit.approvals.models import ApprovalCase
    from sfpcl_credit.approvals.modules.approval_case_selector import (
        select_approval_case_candidates,
    )
    counts = {}
    approval_codes = {
        "cases_pending_review",
        "cases_returned_for_clarification",
        "sanctions_approved_today",
        "board_approvals_required",
    }
    if requested_codes.intersection(approval_codes):
        candidates, _scope = select_approval_case_candidates(actor=user)
        approval_counts = candidates.aggregate(
            pending=Count(
                "pk",
                filter=Q(current_status=ApprovalCase.STATUS_PENDING),
                distinct=True,
            ),
            returned=Count(
                "pk",
                filter=Q(current_status=ApprovalCase.STATUS_RETURNED),
                distinct=True,
            ),
            approved_today=Count(
                "pk",
                filter=Q(
                    current_status=ApprovalCase.STATUS_APPROVED,
                    decision_date=timezone.localdate(),
                ),
                distinct=True,
            ),
        )
        counts.update(
            {
                "cases_pending_review": approval_counts["pending"],
                "cases_returned_for_clarification": approval_counts["returned"],
                "sanctions_approved_today": approval_counts["approved_today"],
                "board_approvals_required": approval_counts["pending"],
            }
        )
    if "exceptions_pending_decision" in requested_codes:
        from sfpcl_credit.reports.selectors.exception import select

        counts["exceptions_pending_decision"] = _selector_total(
            select,
            actor=user,
            status="pending",
        )
    account_codes = {
        "loans_above_five_lakh",
        "portfolio_outstanding",
        "dpd_summary",
    }
    if requested_codes.intersection(account_codes):
        from sfpcl_credit.loans.modules.loan_account_read import scoped_account_candidates

        accounts = scoped_account_candidates(actor=user)
        account_counts = accounts.aggregate(
            large=Count(
                "pk",
                filter=Q(sanctioned_amount__gt=500000),
            ),
            outstanding=Count(
                "pk",
                filter=Q(total_outstanding__gt=0),
            ),
            dpd=Count(
                "pk",
                filter=Q(current_dpd_status__days_past_due__gt=0),
            ),
        )
        counts.update(
            {
                "loans_above_five_lakh": account_counts["large"],
                "portfolio_outstanding": account_counts["outstanding"],
                "dpd_summary": account_counts["dpd"],
            }
        )
    if "section186_items_pending" in requested_codes:
        from sfpcl_credit.reports.selectors.statutory import select_section_186

        counts["section186_items_pending"] = _selector_total(
            select_section_186,
            actor=user,
            review_status="pending",
        )
    if "nbfc_tests_due" in requested_codes:
        from sfpcl_credit.reports.selectors.statutory import select_nbfc_test

        counts["nbfc_tests_due"] = _selector_total(
            select_nbfc_test,
            actor=user,
            review_status="pending",
        )
    if "recovery_decisions_pending" in requested_codes:
        from sfpcl_credit.reports.selectors.recovery import select

        counts["recovery_decisions_pending"] = _selector_total(
            select,
            actor=user,
            action_status="pending",
        )
    return {code: counts[code] for code in requested_codes}


def _compliance_card_counts(user, requested_codes):
    from sfpcl_credit.compliance.models import (
        ComplianceTask,
    )
    from sfpcl_credit.legal_documents.models import DocumentChecklist
    from sfpcl_credit.approvals.modules import document_checklist_access

    counts = {}
    document_codes = {
        "documents_pending_generation",
        "documents_pending_signature",
    }
    if requested_codes.intersection(document_codes):
        checklists, error_code = document_checklist_access.scope_post_sanction_checklists(
            actor=user,
            queryset=DocumentChecklist.objects.all(),
        )
        if error_code:
            raise DashboardPermissionDenied
        document_counts = checklists.aggregate(
            generation=Count(
                "pk",
                filter=Q(checklist_status=DocumentChecklist.STATUS_IN_PROGRESS),
            ),
            signature=Count(
                "pk",
                filter=Q(
                    checklist_status__in=(
                        DocumentChecklist.STATUS_CS_APPROVED,
                        DocumentChecklist.STATUS_CREDIT_APPROVED,
                        DocumentChecklist.STATUS_SANCTION_APPROVED,
                    )
                ),
            ),
        )
        counts.update(
            {
                "documents_pending_generation": document_counts["generation"],
                "documents_pending_signature": document_counts["signature"],
            }
        )
    if "security_items_pending_custody" in requested_codes:
        from sfpcl_credit.reports.selectors.security_custody import select

        counts["security_items_pending_custody"] = _selector_total(
            select,
            actor=user,
        )
    if "compliance_tasks_due" in requested_codes:
        counts["compliance_tasks_due"] = ComplianceTask.objects.filter(
            Q(assigned_to_user=user) | Q(reviewer_user=user),
            task_status=ComplianceTask.STATUS_DUE,
        ).count()
    if "section186_items_pending" in requested_codes:
        from sfpcl_credit.reports.selectors.statutory import select_section_186

        counts["section186_items_pending"] = _selector_total(
            select_section_186,
            actor=user,
            review_status="pending",
        )
    if "nbfc_tests_due" in requested_codes:
        from sfpcl_credit.reports.selectors.statutory import select_nbfc_test

        counts["nbfc_tests_due"] = _selector_total(
            select_nbfc_test,
            actor=user,
            review_status="pending",
        )
    if "board_approvals_required" in requested_codes:
        counts.update(
            _sanction_card_counts(user, {"board_approvals_required"})
        )
    if "grievance_open_cases" in requested_codes:
        from sfpcl_credit.reports.selectors.grievance import select

        counts["grievance_open_cases"] = _selector_total(
            select,
            actor=user,
            status="open",
        )
    if "archival_due" in requested_codes:
        from sfpcl_credit.closure.modules.loan_closure import (
            pending_archive_requirements,
        )

        counts["archival_due"] = pending_archive_requirements(actor=user).count()
    return {code: counts[code] for code in requested_codes}


def _treasury_card_counts(user, requested_codes):
    from sfpcl_credit.disbursements.models import Disbursement
    from sfpcl_credit.interest.models import AccrualEntry, InterestInvoice
    from sfpcl_credit.loans.models import BankStatementLine, Repayment
    from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest

    counts = {}
    sap_codes = {"sap_requests_pending", "customer_codes_pending"}
    if requested_codes.intersection(sap_codes):
        sap_counts = SapCustomerProfileRequest.objects.filter(
            assigned_to_user=user,
        ).aggregate(
            draft=Count(
                "pk",
                filter=Q(request_status=SapCustomerProfileRequest.STATUS_DRAFT),
            ),
            sent=Count(
                "pk",
                filter=Q(request_status=SapCustomerProfileRequest.STATUS_SENT),
            ),
        )
        counts.update(
            {
                "sap_requests_pending": sap_counts["draft"],
                "customer_codes_pending": sap_counts["sent"],
            }
        )
    account_codes = requested_codes - sap_codes - {"reconciliation_breaks"}
    if account_codes:
        from sfpcl_credit.loans.modules.loan_account_read import scoped_account_candidates

        accounts = scoped_account_candidates(actor=user)
        if requested_codes.intersection(
            {"disbursements_pending_readiness", "disbursements_pending_authorisation"}
        ):
            disbursement_counts = accounts.aggregate(
                readiness=Count(
                    "pk",
                    filter=Q(disbursements__isnull=True),
                    distinct=True,
                ),
                authorisation=Count(
                    "disbursements",
                    filter=Q(disbursements__authorisation_status="pending"),
                    distinct=True,
                ),
            )
            counts.update(
                {
                    "disbursements_pending_readiness": disbursement_counts["readiness"],
                    "disbursements_pending_authorisation": disbursement_counts["authorisation"],
                }
            )
        repayment_codes = {
            "repayments_pending_allocation",
            "repayments_pending_posting",
        }
        if requested_codes.intersection(repayment_codes):
            repayment_counts = Repayment.objects.filter(
                loan_account__in=accounts,
            ).aggregate(
                allocation=Count(
                    "pk",
                    filter=Q(allocation_status="pending"),
                ),
                posting=Count(
                    "pk",
                    filter=Q(sap_posting_status="pending"),
                ),
            )
            counts.update(
                {
                    "repayments_pending_allocation": repayment_counts["allocation"],
                    "repayments_pending_posting": repayment_counts["posting"],
                }
            )
        invoice_codes = {"interest_invoices_due", "interest_invoices_pending"}
        if requested_codes.intersection(invoice_codes):
            invoice_count = InterestInvoice.objects.filter(
                loan_account__in=accounts,
                invoice_status=InterestInvoice.STATUS_DRAFT,
            ).count()
            counts.update(
                {
                    "interest_invoices_due": invoice_count,
                    "interest_invoices_pending": invoice_count,
                }
            )
        if "accruals_pending" in requested_codes:
            counts["accruals_pending"] = AccrualEntry.objects.filter(
                loan_account__in=accounts,
                posted_status=AccrualEntry.STATUS_PENDING,
            ).count()
    if "reconciliation_breaks" in requested_codes:
        counts["reconciliation_breaks"] = BankStatementLine.objects.filter(
            statement_import__imported_by_user=user,
            match_status__in=("unmatched", "exception"),
        ).count()
    return {code: counts[code] for code in requested_codes}


__all__ = [
    "DASHBOARD_READ_PERMISSION",
    "DashboardPermissionDenied",
    "dashboard_summary",
    "user_can_read_dashboard",
    "validation_field_errors",
]
