from collections import Counter
import importlib


class MatrixValidationError(ValueError):
    pass


def required_control_ids():
    return {
        *(f"SEC-AUTH-{number:03d}" for number in range(1, 11)),
        *(f"SEC-AUTHZ-{number:03d}" for number in range(1, 8)),
        *(f"SEC-PII-{number:03d}" for number in range(1, 13)),
        *(f"SEC-WEB-{number:03d}" for number in range(1, 11)),
        *(f"AUD-{number:03d}" for number in range(1, 17)),
    }


def _test(control_id, label):
    return {"control_id": control_id, "test_labels": [label]}


def _label(module, test_class, method):
    return f"sfpcl_credit.tests.{module}.{test_class}.{method}"


AUTH = "test_auth_api"
AUTH_CLASS = "AuthApiTests"
SECURITY_CLASS = "SecurityBoundaryRegressionTests"

CONTROL_MATRIX = (
    _test("SEC-AUTH-001", _label(AUTH, AUTH_CLASS, "test_active_user_can_login_and_receives_tokens")),
    _test("SEC-AUTH-002", _label(AUTH, AUTH_CLASS, "test_invalid_credentials_do_not_issue_tokens_and_are_audited")),
    _test("SEC-AUTH-003", _label("test_security_regression", SECURITY_CLASS, "test_unknown_and_known_login_failures_use_the_same_public_error")),
    _test("SEC-AUTH-004", _label(AUTH, AUTH_CLASS, "test_inactive_user_cannot_login")),
    _test("SEC-AUTH-005", _label(AUTH, AUTH_CLASS, "test_inactive_user_cannot_login")),
    _test("SEC-AUTH-006", _label(AUTH, AUTH_CLASS, "test_expired_access_token_is_rejected")),
    _test("SEC-AUTH-007", _label(AUTH, AUTH_CLASS, "test_refresh_rotates_refresh_token_and_rejects_old_token")),
    _test("SEC-AUTH-008", _label(AUTH, AUTH_CLASS, "test_logout_revokes_session_and_blocks_future_refresh")),
    _test("SEC-AUTH-009", _label("test_portal_auth_api", "PortalAuthApiTests", "test_security_settings_password_change_audits_and_revokes_other_sessions")),
    {
        "control_id": "SEC-AUTH-010",
        "blocking_finding": "SECURITY-012F-LOGIN-RATE-LIMIT",
    },
    _test("SEC-AUTHZ-001", _label("test_appraisal_api", "AppraisalApiTests", "test_permission_and_object_scope_denials_create_no_success_evidence")),
    _test("SEC-AUTHZ-002", _label("test_security_regression", SECURITY_CLASS, "test_unknown_permission_and_admin_without_business_role_are_denied")),
    _test("SEC-AUTHZ-003", _label("test_admin_users_api", "AdminUsersApiTests", "test_create_only_role_cannot_assign_roles_teams_or_suspend")),
    _test("SEC-AUTHZ-004", _label("test_object_permissions", "ObjectPermissionHelperTests", "test_owner_mismatch_with_no_matching_team_is_denied")),
    _test("SEC-AUTHZ-005", _label("test_approval_case_routing_api", "ApprovalCaseRoutingApiTests", "test_conflicted_approval_returns_exact_source_error_and_denial_audit")),
    _test("SEC-AUTHZ-006", _label("test_appraisal_api", "AppraisalApiTests", "test_review_enforces_independent_permission_object_scope_and_maker_checker")),
    _test("SEC-AUTHZ-007", _label("test_security_regression", SECURITY_CLASS, "test_unknown_permission_and_admin_without_business_role_are_denied")),
    _test("SEC-PII-001", _label("test_member_directory_api", "MemberDirectoryApiTests", "test_authenticated_user_can_list_members_with_paginated_masked_fields")),
    _test("SEC-PII-002", _label("test_member_profile_api", "MemberProfileApiTests", "test_authenticated_user_can_retrieve_masked_member_profile_detail")),
    _test("SEC-PII-003", _label("test_member_bank_accounts_api", "MemberBankAccountApiTests", "test_bank_account_can_be_created_and_listed_with_masked_number")),
    _test("SEC-PII-004", _label("test_blank_dated_cheque_api", "BlankDatedChequeApiTests", "test_compliance_collects_one_encrypted_masked_cheque_from_canonical_bank_facts")),
    _test("SEC-PII-005", _label("test_member_profile_api", "MemberProfileApiTests", "test_pan_reveal_returns_temporary_value_and_audits_metadata_only")),
    _test("SEC-PII-006", _label("test_member_profile_api", "MemberProfileApiTests", "test_reveal_validates_field_reason_member_and_available_value")),
    _test("SEC-PII-007", _label("test_document_files_api", "DocumentFilesApiTests", "test_actor_without_download_permission_is_forbidden_and_not_audited")),
    _test("SEC-PII-008", _label("test_audit_observations_api", "AuditObservationApiTests", "test_restricted_compliance_evidence_uses_a_scoped_signed_download")),
    _test("SEC-PII-009", _label("test_report_exports_api", "ReportExportApiTests", "test_requested_columns_mask_all_sensitive_families_in_every_format")),
    _test("SEC-PII-010", _label("test_communication_channel_contract", "CommunicationChannelContractTests", "test_channel_template_recipient_and_sms_safety_fail_before_writes")),
    _test("SEC-PII-011", _label("test_security_regression", SECURITY_CLASS, "test_logs_errors_and_urls_do_not_contain_sensitive_fixtures")),
    _test("SEC-PII-012", _label("test_security_regression", SECURITY_CLASS, "test_logs_errors_and_urls_do_not_contain_sensitive_fixtures")),
    _test("SEC-WEB-001", _label("test_security_regression", SECURITY_CLASS, "test_search_injection_is_data_not_executable_syntax")),
    _test("SEC-WEB-002", _label("test_security_regression", SECURITY_CLASS, "test_untrusted_text_is_json_escaped_and_never_rendered_as_html")),
    _test("SEC-WEB-003", _label("test_security_regression", SECURITY_CLASS, "test_untrusted_text_is_json_escaped_and_never_rendered_as_html")),
    {
        "control_id": "SEC-WEB-004",
        "blocking_finding": "SECURITY-012F-UPLOAD-FILENAME",
    },
    {
        "control_id": "SEC-WEB-005",
        "blocking_finding": "SECURITY-012F-UPLOAD-CONTENT",
    },
    _test("SEC-WEB-006", _label("test_security_regression", SECURITY_CLASS, "test_unapproved_cors_origin_receives_no_allow_header")),
    _test("SEC-WEB-007", _label("test_security_regression", SECURITY_CLASS, "test_production_error_response_never_contains_traceback")),
    _test("SEC-WEB-008", _label("test_security_regression", SECURITY_CLASS, "test_logs_errors_and_urls_do_not_contain_sensitive_fixtures")),
    _test("SEC-WEB-009", _label("test_report_exports_api", "ReportExportApiTests", "test_excessive_export_attempts_are_actor_rate_limited_and_audited")),
    _test("SEC-WEB-010", _label("test_document_files_api", "DocumentFilesApiTests", "test_download_response_never_exposes_storage_metadata_or_raw_bytes")),
    _test("AUD-001", _label("test_loan_applications_api", "LoanApplicationDraftApiTests", "test_submit_draft_transitions_to_submitted_and_records_metadata_only_evidence")),
    _test("AUD-002", _label("test_credit_modules", "CreditEligibilityModuleTests", "test_eligible_assessment_runs_through_source_named_module_interface")),
    _test("AUD-003", _label("test_credit_modules", "CreditEligibilityModuleTests", "test_loan_limit_calculates_through_module_with_one_public_audit_projection")),
    _test("AUD-004", _label("test_appraisal_api", "AppraisalApiTests", "test_credit_manager_reviews_submitted_appraisal_with_metadata_only_evidence")),
    _test("AUD-005", _label("test_approval_case_routing_api", "ApprovalCaseRoutingApiTests", "test_assigned_approver_can_record_partial_approval_through_canonical_case_projection")),
    _test("AUD-006", _label("test_audit_observations_api", "AuditObservationApiTests", "test_restricted_compliance_evidence_uses_a_scoped_signed_download")),
    _test("AUD-007", _label("test_member_profile_api", "MemberProfileApiTests", "test_pan_reveal_returns_temporary_value_and_audits_metadata_only")),
    _test("AUD-008", _label("test_final_documentation_approval_api", "FinalDocumentationApprovalApiTests", "test_ordered_approval_sequence_retains_meanings_and_exact_replay")),
    _test("AUD-009", _label("test_disbursement_initiation_api", "DisbursementInitiationApiTests", "test_current_ready_payment_is_recorded_once_without_transfer_side_effects")),
    _test("AUD-010", _label("test_disbursement_authorisation_api", "DisbursementAuthorisationApiTests", "test_cfc_approves_exact_frozen_lesser_amount")),
    _test("AUD-011", _label("test_repayment_allocation_api", "RepaymentAllocationApiTests", "test_partial_receipt_reduces_principal_and_appends_immutable_evidence")),
    _test("AUD-012", _label("test_interest_capitalisation_api", "InterestCapitalisationApiTests", "test_may_first_finalisation_moves_principal_once_and_retains_intimation_chain")),
    _test("AUD-013", _label("test_recovery_action_api", "RecoveryActionApiTests", "test_company_secretary_initiates_exact_approved_sh4_with_governed_evidence")),
    _test("AUD-014", _label("test_admin_users_api", "AdminUsersApiTests", "test_admin_can_assign_existing_role_add_and_remove_team_and_audit_changes")),
    _test("AUD-015", _label("test_configurations_api", "LoanPolicyConfigApiTests", "test_create_draft_policy_persists_source_fields_and_writes_audit")),
    _test("AUD-016", _label("test_audit_explorer_api", "AuditExplorerApiTests", "test_invalid_date_boolean_and_all_mutation_methods_are_rejected")),
)


def validate_control_matrix(matrix):
    required = required_control_ids()
    identifiers = [control.get("control_id") for control in matrix]
    duplicates = sorted(
        identifier
        for identifier, count in Counter(identifiers).items()
        if count > 1
    )
    if duplicates:
        raise MatrixValidationError(f"duplicate controls: {duplicates}")
    unknown = sorted(set(identifiers) - required)
    if unknown:
        raise MatrixValidationError(f"unknown controls: {unknown}")
    missing = sorted(required - set(identifiers))
    if missing:
        raise MatrixValidationError(f"missing controls: {missing}")
    incomplete = sorted(
        control["control_id"]
        for control in matrix
        if not control.get("test_labels") and not control.get("blocking_finding")
    )
    if incomplete:
        raise MatrixValidationError(f"unmapped controls: {incomplete}")
    return tuple(sorted(matrix, key=lambda control: control["control_id"]))


def validate_test_labels(matrix):
    unresolved = []
    for control in matrix:
        for label in control.get("test_labels", ()):
            module_name, class_name, method_name = label.rsplit(".", 2)
            try:
                module = importlib.import_module(module_name)
                test_class = getattr(module, class_name)
                test_method = getattr(test_class, method_name)
            except (ImportError, AttributeError, ValueError):
                unresolved.append(label)
                continue
            if not callable(test_method) or not method_name.startswith("test_"):
                unresolved.append(label)
    return tuple(sorted(set(unresolved)))
