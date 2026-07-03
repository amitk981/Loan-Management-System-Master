# backend-test Results

Command: "/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python" sfpcl_credit/manage.py test sfpcl_credit.tests -v 2

Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Found 33 test(s).
Operations to perform:
  Apply all migrations: contenttypes, identity
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying identity.0001_initial... OK
  Applying identity.0002_permission_rolepermission_and_more... OK
System check identified no issues (0 silenced).
test_all_health_endpoints_include_api_version_v1 (sfpcl_credit.tests.test_api_envelope.ApiEnvelopeTests.test_all_health_endpoints_include_api_version_v1) ... ok
test_error_envelope_uses_the_same_standard_meta_keys (sfpcl_credit.tests.test_api_envelope.ApiEnvelopeTests.test_error_envelope_uses_the_same_standard_meta_keys) ... ok
test_health_and_auth_share_the_same_standard_meta_keys (sfpcl_credit.tests.test_api_envelope.ApiEnvelopeTests.test_health_and_auth_share_the_same_standard_meta_keys) ... ok
test_shared_helper_is_the_single_production_envelope_source (sfpcl_credit.tests.test_api_envelope.ApiEnvelopeTests.test_shared_helper_is_the_single_production_envelope_source) ... ok
test_active_user_can_login_and_receives_tokens (sfpcl_credit.tests.test_auth_api.AuthApiTests.test_active_user_can_login_and_receives_tokens) ... ok
test_expired_access_token_is_rejected (sfpcl_credit.tests.test_auth_api.AuthApiTests.test_expired_access_token_is_rejected) ... ok
test_inactive_user_cannot_login (sfpcl_credit.tests.test_auth_api.AuthApiTests.test_inactive_user_cannot_login) ... ok
test_invalid_credentials_do_not_issue_tokens_and_are_audited (sfpcl_credit.tests.test_auth_api.AuthApiTests.test_invalid_credentials_do_not_issue_tokens_and_are_audited) ... ok
test_logout_revokes_session_and_blocks_future_refresh (sfpcl_credit.tests.test_auth_api.AuthApiTests.test_logout_revokes_session_and_blocks_future_refresh) ... ok
test_refresh_rotates_refresh_token_and_rejects_old_token (sfpcl_credit.tests.test_auth_api.AuthApiTests.test_refresh_rotates_refresh_token_and_rejects_old_token) ... ok
test_refresh_token_signed_with_wrong_secret_is_rejected (sfpcl_credit.tests.test_auth_api.AuthApiTests.test_refresh_token_signed_with_wrong_secret_is_rejected) ... ok
test_secret_key_comes_from_environment_with_dev_fallback (sfpcl_credit.tests.test_auth_api.AuthApiTests.test_secret_key_comes_from_environment_with_dev_fallback) ... ok
test_authenticate_user_rejects_inactive_user (sfpcl_credit.tests.test_auth_module.AuthModuleTests.test_authenticate_user_rejects_inactive_user) ... ok
test_authenticate_user_rejects_wrong_password_as_invalid_credentials (sfpcl_credit.tests.test_auth_module.AuthModuleTests.test_authenticate_user_rejects_wrong_password_as_invalid_credentials) ... ok
test_authenticate_user_returns_active_user (sfpcl_credit.tests.test_auth_module.AuthModuleTests.test_authenticate_user_returns_active_user) ... ok
test_issue_login_tokens_and_session_creates_active_session_and_payload (sfpcl_credit.tests.test_auth_module.AuthModuleTests.test_issue_login_tokens_and_session_creates_active_session_and_payload) ... ok
test_record_auth_event_writes_audit_row (sfpcl_credit.tests.test_auth_module.AuthModuleTests.test_record_auth_event_writes_audit_row) ... ok
test_revoke_session_for_logout_blocks_future_refresh (sfpcl_credit.tests.test_auth_module.AuthModuleTests.test_revoke_session_for_logout_blocks_future_refresh) ... ok
test_rotate_refresh_token_replaces_previous_token (sfpcl_credit.tests.test_auth_module.AuthModuleTests.test_rotate_refresh_token_replaces_previous_token) ... ok
test_validate_access_token_rejects_expired_token (sfpcl_credit.tests.test_auth_module.AuthModuleTests.test_validate_access_token_rejects_expired_token) ... ok
test_validate_access_token_rejects_wrong_token_type (sfpcl_credit.tests.test_auth_module.AuthModuleTests.test_validate_access_token_rejects_wrong_token_type) ... ok
test_validate_refresh_session_rejects_access_token_type (sfpcl_credit.tests.test_auth_module.AuthModuleTests.test_validate_refresh_session_rejects_access_token_type) ... ok
test_management_command_runs_seed_idempotently (sfpcl_credit.tests.test_catalogue_seed.CatalogueSeedTests.test_management_command_runs_seed_idempotently) ... Catalogue seeded: 171 permissions, 20 roles, 8 teams, 134 role-permission links.
Catalogue seeded: 171 permissions, 20 roles, 8 teams, 134 role-permission links.
ok
test_prototype_aliases_map_to_canonical_permissions (sfpcl_credit.tests.test_catalogue_seed.CatalogueSeedTests.test_prototype_aliases_map_to_canonical_permissions) ... ok
test_role_permission_links_use_catalogue_and_seed_interface (sfpcl_credit.tests.test_catalogue_seed.CatalogueSeedTests.test_role_permission_links_use_catalogue_and_seed_interface) ... ok
test_seed_creates_representative_permission_per_module_group (sfpcl_credit.tests.test_catalogue_seed.CatalogueSeedTests.test_seed_creates_representative_permission_per_module_group) ... ok
test_seed_creates_standard_role_and_team_codes (sfpcl_credit.tests.test_catalogue_seed.CatalogueSeedTests.test_seed_creates_standard_role_and_team_codes) ... ok
test_seed_is_idempotent (sfpcl_credit.tests.test_catalogue_seed.CatalogueSeedTests.test_seed_is_idempotent) ... ok
test_deep_health_endpoint_reports_dependency_status (sfpcl_credit.tests.test_health_api.HealthApiTests.test_deep_health_endpoint_reports_dependency_status) ... ok
test_health_endpoints_include_request_id_when_provided (sfpcl_credit.tests.test_health_api.HealthApiTests.test_health_endpoints_include_request_id_when_provided) ... ok
test_health_endpoints_only_accept_get (sfpcl_credit.tests.test_health_api.HealthApiTests.test_health_endpoints_only_accept_get) ... ok
test_liveness_endpoint_returns_standard_success_envelope (sfpcl_credit.tests.test_health_api.HealthApiTests.test_liveness_endpoint_returns_standard_success_envelope) ... ok
test_readiness_endpoint_checks_database_connectivity (sfpcl_credit.tests.test_health_api.HealthApiTests.test_readiness_endpoint_checks_database_connectivity) ... ok

----------------------------------------------------------------------
Ran 33 tests in 4.215s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
