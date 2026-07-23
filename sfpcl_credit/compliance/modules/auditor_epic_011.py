from sfpcl_credit.approvals.modules.read_scope import has_active_audit_read_scope
from sfpcl_credit.compliance.modules.compliance_control_tracker import ComplianceDenied
from sfpcl_credit.identity.modules import auth_service


def require_audit_readonly(actor):
    permissions = set(auth_service.effective_permission_codes(actor))
    roles = set(auth_service.effective_role_codes(actor))
    if (
        not actor.can_authenticate()
        or "internal_auditor" not in roles
        or "reports.compliance.read" not in permissions
        or not has_active_audit_read_scope(actor)
    ):
        raise ComplianceDenied()


def project_epic_011(*, actor):
    require_audit_readonly(actor)
    from sfpcl_credit.closure.models import LoanClosure
    from sfpcl_credit.compliance.modules import compliance_control_tracker as tracker
    from sfpcl_credit.compliance.modules.grievance_workflow import GrievanceWorkflow
    from sfpcl_credit.compliance.modules.kyc_review_tracker import KYCReviewTracker
    from sfpcl_credit.compliance.modules.nbfc_principal_business_test import (
        NbfcPrincipalBusinessTestModule,
    )
    from sfpcl_credit.compliance.modules.section186_tracker import (
        Section186TrackerModule,
    )
    from sfpcl_credit.defaults.modules.default_workflow import list_default_cases

    default_cases, _pagination = list_default_cases(
        actor=actor,
        query_params={"page": "1", "page_size": "100"},
    )
    defaults = [
        {
            **_without_actions(row),
            **_immutable_references(
                entity_ids=_entity_ids_for_default(row),
            ),
        }
        for row in default_cases
    ]
    closures = [
        _closure_projection(row)
        for row in LoanClosure.objects.select_related(
            "loan_account",
            "member",
            "close_audit",
            "workflow_event",
        )
        .prefetch_related("requirements")
        .order_by("-closed_at", "-loan_closure_id")[:100]
    ]
    controls, _pagination = tracker.list_controls(
        actor=actor,
        query={"page": "1", "page_size": "100"},
    )
    tasks, _pagination = tracker.list_tasks(
        actor=actor,
        query={"page": "1", "page_size": "100"},
    )
    evidence_rows = list(tracker.search_evidence(actor=actor, search=""))
    evidence_by_task = {}
    for evidence in evidence_rows:
        evidence_by_task.setdefault(str(evidence.task_id), []).append(
            _evidence_metadata(evidence)
        )
    for task in tasks:
        task["evidence_metadata"] = evidence_by_task.get(
            task["compliance_task_id"], []
        )
    kyc_reviews, _pagination = KYCReviewTracker.list_reviews(
        actor=actor,
        query={"page": "1", "page_size": "100"},
    )
    section_186 = [
        Section186TrackerModule.serialize(row, actor)
        for row in Section186TrackerModule.search(actor=actor, search="")
    ]
    nbfc_tests = [
        NbfcPrincipalBusinessTestModule.serialize(row, actor)
        for row in NbfcPrincipalBusinessTestModule.search(actor=actor, search="")
    ]
    compliance_items = [
        _compliance_projection("control", row["compliance_control_id"], row)
        for row in controls
    ]
    compliance_items.extend(
        _compliance_projection("task", row["compliance_task_id"], row)
        for row in tasks
    )
    compliance_items.extend(
        _compliance_projection("kyc_review", row["kyc_review_id"], row)
        for row in kyc_reviews
    )
    compliance_items.extend(
        _compliance_projection("section_186", row["section_186_tracker_id"], row)
        for row in section_186
    )
    compliance_items.extend(
        _compliance_projection("nbfc_test", row["nbfc_principal_test_id"], row)
        for row in nbfc_tests
    )
    compliance_items.extend(
        _compliance_projection(
            "money_lending_review",
            str(row.pk),
            {
                "financial_year": row.financial_year,
                "state": row.state,
                "applicability": row.applicability,
                "exemption_applicable_flag": row.exemption_applicable_flag,
                "reviewed_at": row.reviewed_at.isoformat().replace("+00:00", "Z"),
                "evidence_metadata": [
                    {
                        "evidence_id": str(row.evidence_id),
                        "document_id": str(row.legal_opinion_document_id),
                        "file_name": row.legal_opinion_document.file_name,
                        "sensitivity_level": row.legal_opinion_document.sensitivity_level,
                        "download_path": (
                            f"/api/v1/document-files/{row.legal_opinion_document_id}/download/"
                        ),
                    },
                    {
                        "evidence_id": str(row.evidence_id),
                        "document_id": str(row.board_note_document_id),
                        "file_name": row.board_note_document.file_name,
                        "sensitivity_level": row.board_note_document.sensitivity_level,
                        "download_path": (
                            f"/api/v1/document-files/{row.board_note_document_id}/download/"
                        ),
                    },
                ],
            },
        )
        for row in tracker.search_money_lending_reviews(actor=actor, search="")
        .select_related(
            "evidence",
            "legal_opinion_document",
            "board_note_document",
        )
    )
    grievances, _pagination = GrievanceWorkflow.list(
        actor=actor,
        query={"page": "1", "page_size": "100"},
    )
    grievances = [
        {
            **_without_actions(row),
            **_immutable_references(entity_ids=[row["grievance_id"]]),
        }
        for row in grievances
    ]
    return {
        "summary": {
            "default_cases": len(defaults),
            "closures": len(closures),
            "compliance_items": len(compliance_items),
            "grievances": len(grievances),
        },
        "default_cases": defaults,
        "closures": closures,
        "compliance_items": compliance_items,
        "grievances": grievances,
    }


def _without_actions(value):
    if isinstance(value, dict):
        return {
            key: _without_actions(item)
            for key, item in value.items()
            if key != "available_actions"
        }
    if isinstance(value, list):
        return [_without_actions(item) for item in value]
    return value


def _entity_ids_for_default(row):
    identifiers = [row["default_case_id"]]
    for key in (
        "current_assessment",
        "extension_note",
        "non_payment_note",
        "recovery_decision",
        "recovery_action",
    ):
        nested = row.get(key)
        if not nested:
            continue
        identifier = next(
            (value for field, value in nested.items() if field.endswith("_id")),
            None,
        )
        if identifier:
            identifiers.append(identifier)
    return identifiers


def _immutable_references(*, entity_ids):
    from sfpcl_credit.identity.models import AuditLog
    from sfpcl_credit.workflows.models import WorkflowEvent

    return {
        "audit_references": [
            str(value)
            for value in AuditLog.objects.filter(entity_id__in=entity_ids)
            .order_by("created_at", "audit_log_id")
            .values_list("audit_log_id", flat=True)
        ],
        "workflow_references": [
            str(value)
            for value in WorkflowEvent.objects.filter(entity_id__in=entity_ids)
            .order_by("created_at", "workflow_event_id")
            .values_list("workflow_event_id", flat=True)
        ],
    }


def _closure_projection(row):
    requirements = [
        {
            "requirement_type": requirement.requirement_type,
            "requirement_status": requirement.requirement_status,
        }
        for requirement in row.requirements.all()
    ]
    return {
        "loan_closure_id": str(row.pk),
        "loan_account_id": str(row.loan_account_id),
        "loan_account_number": row.loan_account.loan_account_number,
        "member_id": str(row.member_id),
        "borrower_name": row.member.display_name or row.member.legal_name,
        "closure_type": row.closure_type,
        "closure_stage": row.closure_stage,
        "closed_at": row.closed_at.isoformat().replace("+00:00", "Z"),
        "closed_by_role_code": row.closed_by_role_code,
        "requirements": requirements,
        **_immutable_references(entity_ids=[str(row.pk)]),
    }


def _compliance_projection(record_type, record_id, row):
    return {
        "record_type": record_type,
        "record_id": record_id,
        "details": _without_actions(row),
        **_immutable_references(entity_ids=[record_id]),
    }


def _evidence_metadata(row):
    return {
        "evidence_id": str(row.pk),
        "document_id": str(row.document_id),
        "file_name": row.document.file_name,
        "sensitivity_level": row.document.sensitivity_level,
        "evidence_type": row.evidence_type,
        "source_owner": row.source_owner,
        "source_period": row.source_period,
        "review_status": row.review_status,
        "submitted_at": row.submitted_at.isoformat().replace("+00:00", "Z"),
        "download_path": f"/api/v1/document-files/{row.document_id}/download/",
    }
