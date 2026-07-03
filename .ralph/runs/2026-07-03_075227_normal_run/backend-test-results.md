# backend-test Results

Command: "/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python" sfpcl_credit/manage.py test sfpcl_credit.tests -v 2

Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Found 13 test(s).
Operations to perform:
  Apply all migrations: contenttypes, identity
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying identity.0001_initial... OK
System check identified no issues (0 silenced).
test_active_user_can_login_and_receives_tokens (sfpcl_credit.tests.test_auth_api.AuthApiTests.test_active_user_can_login_and_receives_tokens) ... ok
test_expired_access_token_is_rejected (sfpcl_credit.tests.test_auth_api.AuthApiTests.test_expired_access_token_is_rejected) ... ok
test_inactive_user_cannot_login (sfpcl_credit.tests.test_auth_api.AuthApiTests.test_inactive_user_cannot_login) ... ok
test_invalid_credentials_do_not_issue_tokens_and_are_audited (sfpcl_credit.tests.test_auth_api.AuthApiTests.test_invalid_credentials_do_not_issue_tokens_and_are_audited) ... ok
test_logout_revokes_session_and_blocks_future_refresh (sfpcl_credit.tests.test_auth_api.AuthApiTests.test_logout_revokes_session_and_blocks_future_refresh) ... ok
test_refresh_rejects_token_signed_with_wrong_secret (sfpcl_credit.tests.test_auth_api.AuthApiTests.test_refresh_rejects_token_signed_with_wrong_secret) ... ok
test_refresh_rotates_refresh_token_and_rejects_old_token (sfpcl_credit.tests.test_auth_api.AuthApiTests.test_refresh_rotates_refresh_token_and_rejects_old_token) ... ok
test_secret_key_can_be_read_from_environment (sfpcl_credit.tests.test_auth_api.AuthSettingsTests.test_secret_key_can_be_read_from_environment) ... ok
test_deep_health_endpoint_reports_dependency_status (sfpcl_credit.tests.test_health_api.HealthApiTests.test_deep_health_endpoint_reports_dependency_status) ... ok
test_health_endpoints_include_request_id_when_provided (sfpcl_credit.tests.test_health_api.HealthApiTests.test_health_endpoints_include_request_id_when_provided) ... ok
test_health_endpoints_only_accept_get (sfpcl_credit.tests.test_health_api.HealthApiTests.test_health_endpoints_only_accept_get) ... ok
test_liveness_endpoint_returns_standard_success_envelope (sfpcl_credit.tests.test_health_api.HealthApiTests.test_liveness_endpoint_returns_standard_success_envelope) ... ok
test_readiness_endpoint_checks_database_connectivity (sfpcl_credit.tests.test_health_api.HealthApiTests.test_readiness_endpoint_checks_database_connectivity) ... ok

----------------------------------------------------------------------
Ran 13 tests in 1.398s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
