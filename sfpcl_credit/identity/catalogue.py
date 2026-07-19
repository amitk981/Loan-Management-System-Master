"""Canonical role, team, permission, and role-permission catalogue seed.

Single source of truth for backend RBAC codes, transcribed from
``docs/source/auth-permissions.md``:

* Permissions   -> §12.1-12.13 (module_name is the code's leading segment).
* Roles         -> §13.1 (internal) and §4.2 (external; future-only roles remain inactive).
* Teams         -> §9.3 / §38.2.
* Role links    -> §15.1-15.12 "Key Permissions" (filtered to codes present in §12;
                   codes §15 references but §12 omits are recorded in ASSUMPTIONS A-007).

``seed_catalogue()`` is the one interface used by both the management command
(``seed_role_catalogue``) and the tests. It is idempotent: rerunning it never
duplicates rows and keeps display fields in sync with this module.
"""

from django.db import transaction

from .models import Permission, Role, RolePermission, Team


# --- Permissions -------------------------------------------------------------
# (permission_code, permission_name, risk_level). module_name is derived from
# the leading segment of the code (auth-permissions §11 naming convention).
PERMISSIONS = [
    # §12.1 Authentication and User Administration
    ("auth.session.read_own", "View own sessions", "low"),
    ("auth.session.revoke_own", "Revoke own session", "low"),
    ("auth.session.read_all", "View all user sessions", "high"),
    ("auth.session.revoke_any", "Revoke any user session", "high"),
    ("users.user.read", "View users", "medium"),
    ("users.user.create", "Create users", "high"),
    ("users.user.update", "Update users", "high"),
    ("users.user.disable", "Disable users", "critical"),
    ("users.role.read", "View roles", "medium"),
    ("users.role.create", "Create roles", "critical"),
    ("users.role.update", "Update roles", "critical"),
    ("users.permission.assign", "Assign permissions", "critical"),
    ("users.team.manage", "Manage teams", "high"),
    # §12.2 Member
    ("members.member.read", "View member list / details", "medium"),
    ("members.member.create", "Create member", "high"),
    ("members.member.update", "Update member", "high"),
    ("members.member.identity_change.approve", "Approve member identity change", "high"),
    ("members.member.deactivate", "Deactivate member", "critical"),
    ("members.sensitive.reveal_pan", "Reveal full PAN", "critical"),
    ("members.sensitive.reveal_aadhaar", "Reveal full Aadhaar", "critical"),
    ("members.nominee.read", "View nominees", "medium"),
    ("members.nominee.create", "Create nominee", "high"),
    ("members.nominee.update", "Update nominee", "high"),
    # A-062: source stage matrix names witness read/capture roles while the
    # canonical catalogue omits the atomic codes.
    ("members.witness.read", "View witnesses", "medium"),
    ("members.witness.create", "Create witnesses", "high"),
    ("members.witness.update", "Update witnesses", "high"),
    ("members.shareholding.read", "View shareholding", "medium"),
    ("members.shareholding.create", "Create shareholding", "high"),
    ("members.shareholding.update", "Update shareholding", "high"),
    ("members.active_status.calculate", "Calculate active member status", "medium"),
    ("members.active_status.verify", "Verify / override active status", "high"),
    # §12.3 KYC
    ("kyc.profile.read", "View KYC status", "medium"),
    ("kyc.profile.create", "Create KYC profile", "high"),
    ("kyc.profile.update", "Update KYC profile", "high"),
    ("kyc.document.upload", "Upload KYC document", "high"),
    ("kyc.document.read", "View KYC document metadata", "high"),
    ("kyc.document.download", "Download KYC document", "critical"),
    ("kyc.document.verify", "Verify KYC document", "high"),
    ("kyc.rekyc.manage", "Manage periodic re-KYC", "high"),
    ("kyc.sensitive.reveal", "Reveal sensitive KYC fields", "critical"),
    # §12.4 Loan Application
    ("applications.loan_application.read", "View applications", "medium"),
    ("applications.loan_application.create", "Create loan application", "high"),
    ("applications.loan_application.update", "Update draft application", "high"),
    ("applications.loan_application.submit", "Submit application", "high"),
    ("applications.loan_application.complete_check", "Mark completeness result", "high"),
    (
        "applications.loan_application.return_deficiency",
        "Return application with deficiencies",
        "high",
    ),
    ("applications.loan_application.cancel", "Cancel application", "high"),
    ("applications.document.upload", "Upload application documents", "high"),
    ("applications.document.verify", "Verify application documents", "high"),
    ("applications.deficiency.create", "Create deficiencies", "high"),
    ("applications.deficiency.resolve", "Resolve deficiencies", "high"),
    ("applications.rejection_note.create", "Create rejection note", "high"),
    ("applications.rejection_note.send", "Send rejection note", "high"),
    # §12.5 Credit Assessment
    ("credit.eligibility.run", "Run eligibility assessment", "high"),
    ("credit.eligibility.override", "Override eligibility result", "critical"),
    ("credit.loan_limit.calculate", "Calculate loan limit", "high"),
    ("credit.loan_limit.override", "Override loan limit", "critical"),
    ("credit.appraisal.create", "Create appraisal note", "high"),
    ("credit.appraisal.update", "Update appraisal note", "high"),
    ("credit.appraisal.submit_review", "Submit appraisal for review", "high"),
    ("credit.appraisal.review", "Review appraisal as Credit Manager", "high"),
    ("credit.appraisal.submit_sanction", "Submit to Sanction Committee", "high"),
    ("credit.risk_assessment.manage", "Create / update risk assessment", "high"),
    ("credit.borrowing_history.read", "View borrowing history", "medium"),
    ("credit.borrowing_history.update", "Update borrowing history", "high"),
    # §12.6 Approval
    ("approvals.matrix.read", "View approval matrix", "medium"),
    ("approvals.matrix.manage", "Manage approval matrix", "critical"),
    ("approvals.case.read", "View approval cases", "medium"),
    ("approvals.case.create", "Create approval case", "high"),
    ("approvals.case.approve", "Approve assigned case", "critical"),
    ("approvals.case.reject", "Reject assigned case", "critical"),
    ("approvals.case.return", "Return case for clarification", "high"),
    ("approvals.sanction.read", "View sanction decision", "medium"),
    ("approvals.sanction.create", "Create sanction decision", "critical"),
    ("approvals.sanction_register.read", "View Credit Sanction Register", "medium"),
    ("approvals.exception_register.read", "View Exception Register", "medium"),
    ("approvals.exception.create", "Create exception entry", "critical"),
    ("approvals.general_meeting.record", "Record general meeting approval", "critical"),
    # §12.7 Documentation
    ("documents.template.read", "View templates", "medium"),
    ("documents.template.manage", "Manage templates", "critical"),
    (
        "documents.template.file_reference",
        "Reference globally provenanced template files",
        "critical",
    ),
    ("documents.file.upload", "Upload files", "high"),
    # §12.7: "High / Critical depending sensitivity" -> stored at the higher level.
    ("documents.file.download", "Download files", "critical"),
    ("documents.file.delete", "Delete file metadata where allowed", "critical"),
    ("documents.loan_document.generate", "Generate loan document", "high"),
    ("documents.loan_document.read", "View loan document metadata", "medium"),
    ("documents.loan_document.verify", "Verify loan document", "high"),
    ("documents.signature.record", "Record signature", "high"),
    ("documents.signature.resolve_mismatch", "Resolve signature mismatch", "high"),
    ("documents.stamp.record", "Record stamp duty", "high"),
    ("documents.notary.record", "Record notarisation", "high"),
    ("documents.checklist.read", "View checklist", "medium"),
    ("documents.checklist.update", "Update checklist items", "high"),
    ("documents.checklist.approve_cs", "CS checklist approval", "critical"),
    ("documents.checklist.approve_credit", "Credit Manager checklist approval", "critical"),
    (
        "documents.checklist.approve_sanction",
        "Sanction Committee checklist approval",
        "critical",
    ),
    (
        "documents.checklist.sign_disbursement_complete",
        "Senior Manager Finance disbursement signature",
        "critical",
    ),
    # A-022: source classifies content templates as Communication / Compliance
    # owned, but §12 omits exact content-template permission codes.
    ("communications.content_template.read", "View content templates", "medium"),
    ("communications.content_template.manage", "Manage content templates", "medium"),
    # A-025: source defines communication send/list APIs and role details mention
    # communication creation, but §12 omits exact communication permission codes.
    ("communications.communication.read", "View communication history", "medium"),
    ("communications.communication.send", "Create communication snapshots", "medium"),
    # A-026: S04 is an all-internal-user in-app inbox, but §12 omits a narrow
    # notification permission code.
    ("communications.notification.read", "View own notifications", "medium"),
    # §12.8 Security
    ("security.package.read", "View security package", "medium"),
    ("security.package.create", "Create / refresh security package", "high"),
    ("security.package.update", "Update security package", "high"),
    ("security.poa.manage", "Manage Power of Attorney", "critical"),
    ("security.sh4.manage", "Manage SH-4", "critical"),
    ("security.cdsl_pledge.manage", "Manage CDSL pledge", "critical"),
    ("security.cdsl_pledge.reveal", "Reveal CDSL BO accounts", "critical"),
    ("security.blank_cheque.manage", "Manage blank-dated cheque", "critical"),
    ("security.blank_cheque.reveal", "Reveal cheque details", "critical"),
    ("security.custody.record", "Record custody movement", "critical"),
    ("security.instrument.invoke", "Invoke security instrument", "critical"),
    ("security.instrument.release", "Release security instrument", "critical"),
    # §12.9 SAP and Finance
    ("finance.sap_request.create", "Create SAP customer request", "high"),
    ("finance.sap_request.send", "Send SAP request", "high"),
    ("finance.sap_request.complete", "Mark SAP code created", "critical"),
    ("finance.sap_code.read", "View SAP customer code", "medium"),
    ("finance.loan_account.create", "Create loan account from sanction", "critical"),
    ("finance.loan_account.read", "View loan accounts", "medium"),
    ("finance.loan_account.update_terms", "Update loan terms", "critical"),
    ("finance.disbursement.readiness", "View disbursement readiness", "medium"),
    ("finance.disbursement.initiate", "Initiate disbursement", "critical"),
    ("finance.disbursement.authorise", "Authorise disbursement", "critical"),
    ("finance.disbursement.mark_success", "Mark bank transfer successful", "critical"),
    ("finance.disbursement.send_advice", "Send disbursement advice", "high"),
    ("finance.repayment.create", "Capture repayment", "high"),
    ("finance.repayment.allocate", "Allocate repayment", "critical"),
    ("finance.repayment.mark_sap_posted", "Mark SAP posting", "high"),
    ("finance.bank_statement.read", "View bank statement reconciliation", "medium"),
    ("finance.bank_statement.import", "Import bank statements", "high"),
    ("finance.bank_statement.match", "Match bank statement evidence", "critical"),
    ("finance.interest_invoice.create", "Generate interest invoice", "high"),
    ("finance.interest_invoice.issue", "Issue interest invoice", "high"),
    ("finance.accrual.create", "Create monthly accrual", "high"),
    ("finance.accrual.bulk_generate", "Bulk-generate accruals", "high"),
    ("finance.interest_capitalise", "Capitalise unpaid interest", "critical"),
    # A-126: source-bank configuration is deliberately grantable but no role owns it.
    (
        "config.source_bank_account.activate",
        "Activate governed source bank account",
        "critical",
    ),
    # §12.10 Monitoring and Default
    ("monitoring.dpd.read", "View DPD status", "medium"),
    ("monitoring.dpd.calculate", "Calculate DPD", "high"),
    ("monitoring.reminder.create", "Send / record reminder", "high"),
    ("monitoring.mis.generate", "Generate quarterly MIS", "high"),
    ("monitoring.mis.submit", "Submit MIS to CFO", "high"),
    ("monitoring.mis.review", "Review MIS", "high"),
    ("defaults.case.read", "View default cases", "medium"),
    ("defaults.case.open", "Open default case", "high"),
    ("defaults.assessment.create", "Create default assessment", "high"),
    ("defaults.extension.grant", "Grant one-year extension", "critical"),
    ("defaults.non_payment_note.create", "Create non-payment note", "high"),
    ("defaults.non_payment_note.submit", "Submit to Sanction Committee", "high"),
    ("recovery.decision.create", "Create recovery decision", "critical"),
    ("recovery.action.initiate", "Initiate recovery action", "critical"),
    ("recovery.action.complete", "Complete recovery action", "critical"),
    # §12.11 Closure
    ("closure.readiness.read", "View closure readiness", "medium"),
    ("closure.loan.close", "Close loan", "critical"),
    ("closure.noc.issue", "Issue NOC", "critical"),
    ("closure.security_return.record", "Record security return", "critical"),
    ("closure.archive.create", "Archive loan file", "high"),
    ("closure.archive.read", "View archive metadata", "medium"),
    # §12.12 Compliance
    ("compliance.control.read", "View compliance controls", "medium"),
    ("compliance.control.manage", "Manage compliance controls", "critical"),
    ("compliance.task.read", "View compliance tasks", "medium"),
    ("compliance.task.create", "Create compliance task", "high"),
    ("compliance.task.update", "Update compliance task", "high"),
    ("compliance.evidence.submit", "Submit evidence", "high"),
    ("compliance.evidence.review", "Review evidence", "high"),
    ("compliance.section186.create", "Create Section 186 tracker", "critical"),
    ("compliance.section186.read", "View Section 186 tracker", "high"),
    ("compliance.nbfc_test.create", "Create NBFC principal test", "critical"),
    ("compliance.nbfc_test.read", "View NBFC principal test", "high"),
    ("compliance.kyc_review.manage", "Manage KYC reviews", "high"),
    (
        "compliance.money_lending_review.manage",
        "Manage money-lending law review",
        "high",
    ),
    ("compliance.stamp_duty_review.manage", "Manage stamp duty compliance", "high"),
    # §12.13 Reports, Audit and Configuration
    ("reports.application_pipeline.read", "View application pipeline report", "medium"),
    ("reports.portfolio.read", "View portfolio report", "high"),
    ("reports.dpd.read", "View DPD report", "high"),
    ("reports.compliance.read", "View compliance dashboard", "high"),
    ("reports.export", "Export reports", "high"),
    # A-023: source §19.1 names management_readonly as the dashboard/summary
    # access scope; §12 does not define a narrower dashboard.read code.
    ("management_readonly", "View dashboard summaries", "medium"),
    ("audit.audit_log.read", "View audit logs", "high"),
    ("audit.workflow_event.read", "View workflow events", "medium"),
    ("audit.version_history.read", "View version history", "medium"),
    ("config.loan_policy.read", "View loan policy config", "medium"),
    ("config.loan_policy.manage", "Manage loan policy config", "critical"),
    ("config.share_valuation.manage", "Manage share valuation", "critical"),
    ("config.scale_of_finance.manage", "Manage scale of finance", "critical"),
    ("config.interest_rate.manage", "Manage interest rate", "critical"),
]


# --- Roles -------------------------------------------------------------------
# (role_code, role_name, description, is_system_role, status).
# Internal roles: auth-permissions §13.1 / §4.1. External or future roles
# (§4.2) are seeded inactive and non-system so they exist for later slices
# without being usable in the MVP.
INTERNAL_ROLES = [
    ("field_officer", "Field Officer", "Assisted borrower intake and document collection", False),
    ("deputy_manager_finance", "Deputy Manager – Finance", "Completeness check and appraisal preparation", False),
    ("credit_manager", "Credit Manager", "Credit workflow owner, appraisal reviewer and monitoring owner", False),
    ("compliance_team_member", "Compliance Team Member", "Document preparation and checklist coordination", False),
    ("company_secretary", "Company Secretary", "Legal documentation, stamping, security custody and compliance", False),
    ("senior_manager_finance", "Senior Manager – Finance", "SAP customer code and disbursement initiation", False),
    ("chief_financial_controller", "Chief Financial Controller", "Bank transfer authorisation", False),
    ("cfo", "CFO", "Sanction Committee, exceptions and compliance review", False),
    ("director", "Director", "Sanction Committee approval", False),
    ("accounts_head", "Accounts Head", "Interest accrual, accounting and reports", False),
    ("sales_team_user", "Sales Team User", "Interest invoice support if confirmed", False),
    ("it_head", "IT Head", "Access control and system security oversight", False),
    ("internal_auditor", "Internal Auditor", "Read-only audit and compliance evidence review", False),
    ("system_admin", "System Administrator", "User, role, config and platform administration", True),
    ("management_viewer", "Management Viewer", "Read-only dashboards and reports", False),
]

ACTIVE_EXTERNAL_ROLES = [
    ("borrower_portal_user", "Borrower / Member", "Borrower-facing self-service access", False),
]

EXTERNAL_FUTURE_ROLES = [
    ("nominee", "Nominee", "Future limited access for nominee acknowledgment", False),
    ("bank_user", "Bank User", "Not recommended for MVP; bank evidence handled internally", False),
    ("subsidiary_user", "Subsidiary Company User", "Future access for produce deduction confirmation", False),
    ("external_auditor", "External Auditor", "Future limited audit access", False),
]

# Assembled as (code, name, description, is_system_role, status).
ROLES = [
    (code, name, description, is_system, "active")
    for (code, name, description, is_system) in INTERNAL_ROLES
] + [
    (code, name, description, is_system, "active")
    for (code, name, description, is_system) in ACTIVE_EXTERNAL_ROLES
] + [
    (code, name, description, is_system, "inactive")
    for (code, name, description, is_system) in EXTERNAL_FUTURE_ROLES
]


# --- Teams -------------------------------------------------------------------
# (team_code, team_name, description). auth-permissions §9.3 / §38.2.
TEAMS = [
    ("credit_assessment", "Credit Assessment Team", "Credit Manager, Deputy Manager – Finance"),
    ("compliance", "Compliance Team", "Company Secretary, Compliance Team Member"),
    ("treasury", "Treasury Team", "Senior Manager – Finance, CFC"),
    ("sanction_committee", "Sanction Committee", "CFO and two Executive Directors"),
    ("accounts", "Accounts Team", "Accounts Head and accounting users"),
    ("it", "IT Team", "IT Head and system administrators"),
    ("audit", "Audit Team", "Internal Auditor"),
    ("sales", "Sales Team", "Sales Team users, if interest invoice process is assigned"),
]


# --- Role -> permission links -----------------------------------------------
# auth-permissions §15.1-15.12 "Key Permissions". Only codes present in the §12
# catalogue above are linked; §15 references that §12 omits are recorded in
# ASSUMPTIONS A-007, not invented here. A-023 adds the source-backed
# management_readonly dashboard scope from §19.1. Roles without source-backed
# permission detail (sales_team_user, it_head, and every external/future role)
# are seeded with no links.
ROLE_PERMISSIONS = {
    "field_officer": [
        "members.member.read",
        "members.nominee.create",
        "applications.loan_application.create",
        "applications.loan_application.update",
        "applications.document.upload",
        "kyc.document.upload",
    ],
    "deputy_manager_finance": [
        "applications.loan_application.read",
        "applications.loan_application.complete_check",
        "applications.loan_application.return_deficiency",
        "applications.deficiency.create",
        "applications.deficiency.resolve",
        "credit.eligibility.run",
        "credit.loan_limit.calculate",
        "credit.appraisal.create",
        "credit.appraisal.update",
        "credit.appraisal.submit_review",
        "credit.risk_assessment.manage",
    ],
    "credit_manager": [
        "members.witness.read",
        "security.package.read",
        "documents.checklist.read",
        "documents.checklist.approve_credit",
        "applications.loan_application.read",
        "applications.loan_application.create",
        "applications.loan_application.complete_check",
        "applications.rejection_note.create",
        "applications.rejection_note.send",
        "credit.eligibility.run",
        "credit.loan_limit.calculate",
        "credit.appraisal.review",
        "credit.appraisal.submit_sanction",
        "approvals.case.read",
        "approvals.case.create",
        "approvals.exception.create",
        "finance.sap_request.create",
        "finance.sap_request.send",
        "finance.disbursement.send_advice",
        "finance.loan_account.read",
        "finance.repayment.create",
        "finance.repayment.allocate",
        "finance.bank_statement.read",
        "finance.bank_statement.import",
        "finance.bank_statement.match",
        "monitoring.dpd.calculate",
        "monitoring.reminder.create",
        "monitoring.mis.generate",
        "defaults.case.open",
        "defaults.assessment.create",
        "defaults.extension.grant",
        "defaults.non_payment_note.create",
        "closure.readiness.read",
        "closure.loan.close",
        "management_readonly",
    ],
    "compliance_team_member": [
        "members.witness.read",
        "members.witness.create",
        "members.witness.update",
        "documents.template.file_reference",
        "documents.loan_document.generate",
        "documents.loan_document.read",
        "documents.loan_document.verify",
        "documents.signature.record",
        "documents.stamp.record",
        "documents.notary.record",
        "documents.checklist.read",
        "documents.checklist.update",
        "communications.content_template.read",
        "communications.content_template.manage",
        "communications.communication.read",
        "communications.communication.send",
        "security.package.create",
        "security.package.update",
        "security.package.read",
        "security.poa.manage",
        "management_readonly",
    ],
    "company_secretary": [
        "members.witness.read",
        "members.witness.create",
        "members.witness.update",
        "approvals.case.read",
        "approvals.sanction_register.read",
        "documents.checklist.read",
        "documents.checklist.update",
        "documents.checklist.approve_cs",
        "documents.loan_document.verify",
        "documents.signature.resolve_mismatch",
        "documents.stamp.record",
        "documents.notary.record",
        "security.package.read",
        "security.package.create",
        "security.poa.manage",
        "security.sh4.manage",
        "security.cdsl_pledge.manage",
        "security.cdsl_pledge.reveal",
        "security.blank_cheque.manage",
        "security.custody.record",
        "security.instrument.release",
        "security.instrument.invoke",
        "closure.noc.issue",
        "closure.security_return.record",
        "closure.archive.create",
        "compliance.control.read",
        "compliance.task.update",
        "compliance.evidence.submit",
        "compliance.money_lending_review.manage",
        "compliance.stamp_duty_review.manage",
        "management_readonly",
    ],
    "senior_manager_finance": [
        "security.package.read",
        "documents.checklist.read",
        "finance.sap_request.complete",
        "finance.sap_code.read",
        "finance.disbursement.readiness",
        "finance.disbursement.initiate",
        "finance.disbursement.mark_success",
        "finance.disbursement.send_advice",
        "documents.checklist.sign_disbursement_complete",
        "documents.file.upload",
        "finance.loan_account.read",
        "finance.bank_statement.read",
        "finance.bank_statement.import",
        "finance.bank_statement.match",
        "management_readonly",
    ],
    "chief_financial_controller": [
        "security.package.read",
        "documents.checklist.read",
        "finance.disbursement.readiness",
        "finance.disbursement.authorise",
        "finance.disbursement.mark_success",
        "finance.loan_account.read",
        "reports.portfolio.read",
        "audit.audit_log.read",
        "management_readonly",
    ],
    "cfo": [
        "security.package.read",
        "documents.checklist.read",
        "approvals.case.read",
        "approvals.case.approve",
        "approvals.case.reject",
        "approvals.case.return",
        "approvals.exception.create",
        "approvals.exception_register.read",
        "approvals.sanction.read",
        "approvals.sanction_register.read",
        "reports.portfolio.read",
        "monitoring.mis.review",
        "compliance.section186.read",
        "compliance.nbfc_test.read",
        "compliance.evidence.review",
        "config.loan_policy.read",
        "recovery.decision.create",
        "management_readonly",
    ],
    "director": [
        "security.package.read",
        "documents.checklist.read",
        "documents.checklist.approve_sanction",
        "approvals.case.read",
        "approvals.case.approve",
        "approvals.case.reject",
        "approvals.case.return",
        "approvals.sanction.read",
        "approvals.sanction_register.read",
        "approvals.exception_register.read",
        "documents.loan_document.read",
        "management_readonly",
    ],
    "accounts_head": [
        "finance.loan_account.read",
        "finance.bank_statement.read",
        "finance.bank_statement.import",
        "finance.bank_statement.match",
        "finance.repayment.mark_sap_posted",
        "finance.interest_invoice.create",
        "finance.interest_invoice.issue",
        "finance.accrual.create",
        "finance.accrual.bulk_generate",
        "reports.portfolio.read",
        "compliance.evidence.submit",
        "management_readonly",
    ],
    "internal_auditor": [
        "members.witness.read",
        "security.package.read",
        "documents.checklist.read",
        "approvals.case.read",
        "approvals.exception_register.read",
        "approvals.sanction_register.read",
        "audit.audit_log.read",
        "audit.workflow_event.read",
        "audit.version_history.read",
        "reports.application_pipeline.read",
        "reports.portfolio.read",
        "reports.compliance.read",
        "documents.loan_document.read",
        "compliance.task.read",
        "compliance.evidence.review",
        # A-023 maps internal_auditor to the "compliance" dashboard context; the
        # dashboard endpoint gates on management_readonly, so the auditor needs it
        # to reach the shell the mapping promises (003G2 regression).
        "management_readonly",
    ],
    "system_admin": [
        "users.user.create",
        "users.user.update",
        "users.user.disable",
        "users.role.create",
        "users.role.update",
        "users.permission.assign",
        "users.team.manage",
        "auth.session.read_all",
        "auth.session.revoke_any",
        # §15.12 grants config administration to System Administrator "only if
        # policy allows"; the explicit config codes are expanded from config.*.
        "config.loan_policy.read",
        "config.loan_policy.manage",
        "config.share_valuation.manage",
        "config.scale_of_finance.manage",
        "config.interest_rate.manage",
    ],
    "management_viewer": [
        "management_readonly",
    ],
}

_NOTIFICATION_ROLE_EXCLUSIONS = {"it_head", "sales_team_user"}
for _role_code, *_ in INTERNAL_ROLES:
    if _role_code in _NOTIFICATION_ROLE_EXCLUSIONS:
        continue
    ROLE_PERMISSIONS.setdefault(_role_code, [])
    if "communications.notification.read" not in ROLE_PERMISSIONS[_role_code]:
        ROLE_PERMISSIONS[_role_code].append("communications.notification.read")


# --- Prototype alias reconciliation (ASSUMPTIONS A-005) ----------------------
# The frontend prototype called can('export') / can('export_reports') /
# can('view_loans'); these map to canonical backend permission codes below.
PROTOTYPE_PERMISSION_ALIASES = {
    "export": "reports.export",
    "export_reports": "reports.export",
    "view_loans": "finance.loan_account.read",
}


def _module_name(permission_code):
    return permission_code.split(".", 1)[0]


@transaction.atomic
def seed_catalogue():
    """Idempotently seed permissions, roles, teams, and role-permission links.

    Returns a non-secret summary dict of row counts for logging.
    """
    for code, name, risk in PERMISSIONS:
        Permission.objects.update_or_create(
            permission_code=code,
            defaults={
                "permission_name": name,
                "module_name": _module_name(code),
                "risk_level": risk,
            },
        )

    for code, name, description, is_system_role, status in ROLES:
        Role.objects.update_or_create(
            role_code=code,
            defaults={
                "role_name": name,
                "description": description,
                "is_system_role": is_system_role,
                "status": status,
            },
        )

    for code, name, description in TEAMS:
        Team.objects.update_or_create(
            team_code=code,
            defaults={"team_name": name, "description": description},
        )

    permissions_by_code = {p.permission_code: p for p in Permission.objects.all()}
    link_count = 0
    for role_code, permission_codes in ROLE_PERMISSIONS.items():
        role = Role.objects.get(role_code=role_code)
        for permission_code in permission_codes:
            permission = permissions_by_code[permission_code]
            RolePermission.objects.get_or_create(role=role, permission=permission)
            link_count += 1

    from sfpcl_credit.approvals.modules.read_scope import (
        seed_default_read_scope_grants,
    )

    seed_default_read_scope_grants()

    return {
        "permissions": Permission.objects.count(),
        "roles": Role.objects.count(),
        "teams": Team.objects.count(),
        "role_permissions": RolePermission.objects.count(),
        "links_declared": link_count,
    }
