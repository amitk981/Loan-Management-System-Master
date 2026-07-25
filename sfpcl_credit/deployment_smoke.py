WORKFLOW_READS = (
    ("dashboard", "/api/v1/dashboard/", False),
    ("member directory", "/api/v1/members/?page=1&page_size=1", True),
    (
        "loan applications",
        "/api/v1/loan-applications/?page=1&page_size=1",
        True,
    ),
    ("approval cases", "/api/v1/approval-cases/?page=1&page_size=1", True),
    (
        "documentation readiness",
        "/api/v1/reports/documentation-readiness/?page=1&page_size=1",
        True,
    ),
    ("default cases", "/api/v1/default-cases/?page=1&page_size=1", True),
    ("compliance tasks", "/api/v1/compliance-tasks/?page=1&page_size=1", True),
    ("audit logs", "/api/v1/audit-logs/?page=1&page_size=1", True),
)

REQUIRED_SMOKE_PERMISSIONS = frozenset(
    {
        "management_readonly",
        "members.member.read",
        "applications.loan_application.read",
        "approvals.case.read",
        "documents.checklist.read",
        "defaults.case.read",
        "compliance.task.read",
        "audit.audit_log.read",
    }
)


def validate_smoke_identity(payload, expected_email):
    if not isinstance(payload, dict) or payload.get("success") is not True:
        return False
    data = payload.get("data")
    if not isinstance(data, dict) or data.get("email") != expected_email:
        return False
    role_codes = data.get("role_codes")
    permissions = data.get("permissions")
    return (
        isinstance(role_codes, list)
        and set(role_codes) == {"deployment_smoke_reader"}
        and isinstance(permissions, list)
        and set(permissions) == REQUIRED_SMOKE_PERMISSIONS
    )
