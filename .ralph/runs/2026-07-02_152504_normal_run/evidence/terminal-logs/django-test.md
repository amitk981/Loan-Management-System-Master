Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Found 5 test(s).
Operations to perform:
  Apply all migrations: contenttypes
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
System check identified no issues (0 silenced).
test_deep_health_endpoint_reports_dependency_status (sfpcl_credit.tests.test_health_api.HealthApiTests.test_deep_health_endpoint_reports_dependency_status) ... ok
test_health_endpoints_include_request_id_when_provided (sfpcl_credit.tests.test_health_api.HealthApiTests.test_health_endpoints_include_request_id_when_provided) ... ok
test_health_endpoints_only_accept_get (sfpcl_credit.tests.test_health_api.HealthApiTests.test_health_endpoints_only_accept_get) ... ok
test_liveness_endpoint_returns_standard_success_envelope (sfpcl_credit.tests.test_health_api.HealthApiTests.test_liveness_endpoint_returns_standard_success_envelope) ... ok
test_readiness_endpoint_checks_database_connectivity (sfpcl_credit.tests.test_health_api.HealthApiTests.test_readiness_endpoint_checks_database_connectivity) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.002s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
