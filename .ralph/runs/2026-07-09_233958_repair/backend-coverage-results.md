# backend-coverage Results

Command: "/Users/amitkallapa/LMS/.ralph/venv/bin/python" -m coverage run --source=sfpcl_credit sfpcl_credit/manage.py test sfpcl_credit.tests && "/Users/amitkallapa/LMS/.ralph/venv/bin/python" -m coverage report --fail-under=85

Creating test database for alias 'default'...
Found 262 test(s).
System check identified no issues (0 silenced).
.........................................................................Catalogue seeded: 177 permissions, 20 roles, 8 teams, 161 role-permission links.
Catalogue seeded: 177 permissions, 20 roles, 8 teams, 161 role-permission links.
.......................................................................................................................................Demo users seeded: demo.system_admin@sfpcl.example, demo.credit_manager@sfpcl.example, demo.compliance@sfpcl.example, demo.treasury@sfpcl.example, demo.internal_auditor@sfpcl.example, demo.tracer@sfpcl.example, demo.zero@sfpcl.example (predictable local/dev password set; do not use in production).
.Demo users seeded: demo.system_admin@sfpcl.example, demo.credit_manager@sfpcl.example, demo.compliance@sfpcl.example, demo.treasury@sfpcl.example, demo.internal_auditor@sfpcl.example, demo.tracer@sfpcl.example, demo.zero@sfpcl.example (predictable local/dev password set; do not use in production).
.Demo users seeded: demo.system_admin@sfpcl.example, demo.credit_manager@sfpcl.example, demo.compliance@sfpcl.example, demo.treasury@sfpcl.example, demo.internal_auditor@sfpcl.example, demo.tracer@sfpcl.example, demo.zero@sfpcl.example (predictable local/dev password set; do not use in production).
.Demo users seeded: demo.system_admin@sfpcl.example, demo.credit_manager@sfpcl.example, demo.compliance@sfpcl.example, demo.treasury@sfpcl.example, demo.internal_auditor@sfpcl.example, demo.tracer@sfpcl.example, demo.zero@sfpcl.example (predictable local/dev password set; do not use in production).
Demo users seeded: demo.system_admin@sfpcl.example, demo.credit_manager@sfpcl.example, demo.compliance@sfpcl.example, demo.treasury@sfpcl.example, demo.internal_auditor@sfpcl.example, demo.tracer@sfpcl.example, demo.zero@sfpcl.example (predictable local/dev password set; do not use in production).
.Demo users seeded: demo.system_admin@sfpcl.example, demo.credit_manager@sfpcl.example, demo.compliance@sfpcl.example, demo.treasury@sfpcl.example, demo.internal_auditor@sfpcl.example, demo.tracer@sfpcl.example, demo.zero@sfpcl.example (predictable local/dev password set; do not use in production).
...Demo users seeded: demo.system_admin@sfpcl.example, demo.credit_manager@sfpcl.example, demo.compliance@sfpcl.example, demo.treasury@sfpcl.example, demo.internal_auditor@sfpcl.example, demo.tracer@sfpcl.example, demo.zero@sfpcl.example (predictable local/dev password set; do not use in production).
.Demo users seeded: demo.system_admin@sfpcl.example, demo.credit_manager@sfpcl.example, demo.compliance@sfpcl.example, demo.treasury@sfpcl.example, demo.internal_auditor@sfpcl.example, demo.tracer@sfpcl.example, demo.zero@sfpcl.example (predictable local/dev password set; do not use in production).
.Demo users seeded: demo.system_admin@sfpcl.example, demo.credit_manager@sfpcl.example, demo.compliance@sfpcl.example, demo.treasury@sfpcl.example, demo.internal_auditor@sfpcl.example, demo.tracer@sfpcl.example, demo.zero@sfpcl.example (predictable local/dev password set; do not use in production).
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions).
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions).
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions).
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions).
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions).
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions).
........................................
----------------------------------------------------------------------
Ran 262 tests in 122.456s

OK
Destroying test database for alias 'default'...
Name                                                                                   Stmts   Miss  Cover
----------------------------------------------------------------------------------------------------------
sfpcl_credit/__init__.py                                                                   0      0   100%
sfpcl_credit/api.py                                                                       25      3    88%
sfpcl_credit/applications/__init__.py                                                      0      0   100%
sfpcl_credit/applications/apps.py                                                          4      0   100%
sfpcl_credit/applications/migrations/0001_initial.py                                       8      0   100%
sfpcl_credit/applications/migrations/0002_loanapplication_submitted_by_user.py             5      0   100%
sfpcl_credit/applications/migrations/0003_systemsequence_loanrequestregisterentry.py       7      0   100%
sfpcl_credit/applications/migrations/0004_applicationdocument_and_more.py                  7      0   100%
sfpcl_credit/applications/migrations/0005_application_deficiency.py                        7      0   100%
sfpcl_credit/applications/migrations/__init__.py                                           0      0   100%
sfpcl_credit/applications/models.py                                                      198     17    91%
sfpcl_credit/applications/services.py                                                    523     49    91%
sfpcl_credit/applications/views.py                                                       257     40    84%
sfpcl_credit/communications/__init__.py                                                    0      0   100%
sfpcl_credit/communications/apps.py                                                        4      0   100%
sfpcl_credit/communications/migrations/0001_initial.py                                     6      0   100%
sfpcl_credit/communications/migrations/0002_communication.py                               6      0   100%
sfpcl_credit/communications/migrations/0003_notification.py                                6      0   100%
sfpcl_credit/communications/migrations/__init__.py                                         0      0   100%
sfpcl_credit/communications/models.py                                                     80      0   100%
sfpcl_credit/communications/services.py                                                  389     43    89%
sfpcl_credit/communications/views.py                                                      95     12    87%
sfpcl_credit/config/__init__.py                                                            0      0   100%
sfpcl_credit/config/asgi.py                                                                4      4     0%
sfpcl_credit/config/settings.py                                                           29      2    93%
sfpcl_credit/config/urls.py                                                               13      0   100%
sfpcl_credit/config/wsgi.py                                                                4      4     0%
sfpcl_credit/configurations/__init__.py                                                    0      0   100%
sfpcl_credit/configurations/apps.py                                                        4      0   100%
sfpcl_credit/configurations/migrations/0001_initial.py                                     8      0   100%
sfpcl_credit/configurations/migrations/__init__.py                                         0      0   100%
sfpcl_credit/configurations/models.py                                                     48      0   100%
sfpcl_credit/configurations/services.py                                                  224     28    88%
sfpcl_credit/configurations/views.py                                                      71     12    83%
sfpcl_credit/dashboard/__init__.py                                                         0      0   100%
sfpcl_credit/dashboard/apps.py                                                             4      4     0%
sfpcl_credit/dashboard/services.py                                                        24      1    96%
sfpcl_credit/dashboard/views.py                                                           17      0   100%
sfpcl_credit/documents/__init__.py                                                         0      0   100%
sfpcl_credit/documents/apps.py                                                             4      0   100%
sfpcl_credit/documents/migrations/0001_initial.py                                          8      0   100%
sfpcl_credit/documents/migrations/__init__.py                                              0      0   100%
sfpcl_credit/documents/models.py                                                          26      1    96%
sfpcl_credit/documents/services.py                                                        67      1    99%
sfpcl_credit/documents/storage.py                                                         41      0   100%
sfpcl_credit/documents/views.py                                                           29      0   100%
sfpcl_credit/identity/__init__.py                                                          0      0   100%
sfpcl_credit/identity/admin_views.py                                                      97     16    84%
sfpcl_credit/identity/audit_views.py                                                      16      0   100%
sfpcl_credit/identity/catalogue.py                                                        35      0   100%
sfpcl_credit/identity/management/__init__.py                                               0      0   100%
sfpcl_credit/identity/management/commands/__init__.py                                      0      0   100%
sfpcl_credit/identity/management/commands/seed_demo_users.py                              82      7    91%
sfpcl_credit/identity/management/commands/seed_e2e_users.py                               45      2    96%
sfpcl_credit/identity/management/commands/seed_role_catalogue.py                           7      0   100%
sfpcl_credit/identity/migrations/0001_initial.py                                           8      0   100%
sfpcl_credit/identity/migrations/0002_permission_rolepermission_and_more.py                7      0   100%
sfpcl_credit/identity/migrations/0003_portal_member_auth.py                                7      0   100%
sfpcl_credit/identity/migrations/__init__.py                                               0      0   100%
sfpcl_credit/identity/models.py                                                          184      6    97%
sfpcl_credit/identity/modules/__init__.py                                                  0      0   100%
sfpcl_credit/identity/modules/admin_users.py                                             125     13    90%
sfpcl_credit/identity/modules/audit_log.py                                                60      1    98%
sfpcl_credit/identity/modules/auth_service.py                                             93      7    92%
sfpcl_credit/identity/modules/http_auth.py                                                31      0   100%
sfpcl_credit/identity/modules/object_permissions.py                                       36      0   100%
sfpcl_credit/identity/modules/portal_auth_service.py                                     204     31    85%
sfpcl_credit/identity/modules/tokens.py                                                   42      4    90%
sfpcl_credit/identity/views.py                                                           135     33    76%
sfpcl_credit/manage.py                                                                    10      0   100%
sfpcl_credit/members/__init__.py                                                           0      0   100%
sfpcl_credit/members/apps.py                                                               4      0   100%
sfpcl_credit/members/migrations/0001_initial.py                                            8      0   100%
sfpcl_credit/members/migrations/0002_profile_shells.py                                     7      0   100%
sfpcl_credit/members/migrations/0003_individual_profile_details.py                         4      0   100%
sfpcl_credit/members/migrations/0004_nominee.py                                            7      0   100%
sfpcl_credit/members/migrations/0005_shareholding_and_more.py                              8      0   100%
sfpcl_credit/members/migrations/0006_landholding_cropplan_and_more.py                      7      0   100%
sfpcl_credit/members/migrations/0007_kycprofile_kycdocument_and_more.py                    7      0   100%
sfpcl_credit/members/migrations/0008_cancelledcheque_bankaccount_and_more.py               7      0   100%
sfpcl_credit/members/migrations/__init__.py                                                0      0   100%
sfpcl_credit/members/models.py                                                           343     28    92%
sfpcl_credit/members/portal_services.py                                                   27      0   100%
sfpcl_credit/members/portal_views.py                                                      30      1    97%
sfpcl_credit/members/services.py                                                         656     45    93%
sfpcl_credit/members/views.py                                                            282     29    90%
sfpcl_credit/ops.py                                                                       16      0   100%
sfpcl_credit/scheduler/__init__.py                                                         0      0   100%
sfpcl_credit/scheduler/apps.py                                                             4      0   100%
sfpcl_credit/scheduler/migrations/0001_initial.py                                          6      0   100%
sfpcl_credit/scheduler/migrations/__init__.py                                              0      0   100%
sfpcl_credit/scheduler/models.py                                                          25      0   100%
sfpcl_credit/scheduler/services.py                                                        90     22    76%
sfpcl_credit/tests/__init__.py                                                             0      0   100%
sfpcl_credit/tests/api_contracts.py                                                       56      0   100%
sfpcl_credit/tests/base.py                                                                 8      0   100%
sfpcl_credit/tests/test_admin_users_api.py                                               176      0   100%
sfpcl_credit/tests/test_api_contract_harness.py                                          116      0   100%
sfpcl_credit/tests/test_api_envelope.py                                                   42      0   100%
sfpcl_credit/tests/test_audit_logs_api.py                                                130      0   100%
sfpcl_credit/tests/test_auth_api.py                                                      164      0   100%
sfpcl_credit/tests/test_auth_module.py                                                   148      0   100%
sfpcl_credit/tests/test_backend_infrastructure.py                                         29      0   100%
sfpcl_credit/tests/test_catalogue_seed.py                                                 90      0   100%
sfpcl_credit/tests/test_communications_api.py                                            141      0   100%
sfpcl_credit/tests/test_configurations_api.py                                            172      0   100%
sfpcl_credit/tests/test_content_templates_api.py                                         132      0   100%
sfpcl_credit/tests/test_dashboard_api.py                                                 105      0   100%
sfpcl_credit/tests/test_document_files_api.py                                            193      0   100%
sfpcl_credit/tests/test_health_api.py                                                     28      0   100%
sfpcl_credit/tests/test_loan_applications_api.py                                         712      0   100%
sfpcl_credit/tests/test_member_bank_accounts_api.py                                      173      0   100%
sfpcl_credit/tests/test_member_directory_api.py                                           78      0   100%
sfpcl_credit/tests/test_member_kyc_api.py                                                154      0   100%
sfpcl_credit/tests/test_member_land_crop_api.py                                          157      0   100%
sfpcl_credit/tests/test_member_nominees_api.py                                           138      2    99%
sfpcl_credit/tests/test_member_profile_api.py                                            213      0   100%
sfpcl_credit/tests/test_member_shareholdings_api.py                                      113      0   100%
sfpcl_credit/tests/test_notifications_api.py                                             155      1    99%
sfpcl_credit/tests/test_object_permissions.py                                             60      0   100%
sfpcl_credit/tests/test_portal_auth_api.py                                                89      0   100%
sfpcl_credit/tests/test_portal_member_api.py                                              75      0   100%
sfpcl_credit/tests/test_scheduler_services.py                                             48      0   100%
sfpcl_credit/tests/test_seed_demo_users.py                                               140      0   100%
sfpcl_credit/tests/test_seed_e2e_users.py                                                 59      0   100%
sfpcl_credit/tests/test_tracer_api.py                                                    125      0   100%
sfpcl_credit/tests/test_workflow_events_api.py                                           102      0   100%
sfpcl_credit/tests/test_workflow_guard.py                                                 28      0   100%
sfpcl_credit/tracer/__init__.py                                                            0      0   100%
sfpcl_credit/tracer/apps.py                                                                4      0   100%
sfpcl_credit/tracer/migrations/0001_initial.py                                             8      0   100%
sfpcl_credit/tracer/migrations/0002_remove_tracer_workflowevent_state.py                   4      0   100%
sfpcl_credit/tracer/migrations/__init__.py                                                 0      0   100%
sfpcl_credit/tracer/models.py                                                             46      0   100%
sfpcl_credit/tracer/services.py                                                          118      4    97%
sfpcl_credit/tracer/views.py                                                             100     16    84%
sfpcl_credit/workflows/__init__.py                                                         2      0   100%
sfpcl_credit/workflows/apps.py                                                             4      0   100%
sfpcl_credit/workflows/event_views.py                                                     17      0   100%
sfpcl_credit/workflows/events.py                                                          61      2    97%
sfpcl_credit/workflows/guard.py                                                           51      2    96%
sfpcl_credit/workflows/migrations/0001_canonical_workflow_event.py                         8      0   100%
sfpcl_credit/workflows/migrations/__init__.py                                              0      0   100%
sfpcl_credit/workflows/models.py                                                          16      0   100%
----------------------------------------------------------------------------------------------------------
TOTAL                                                                                   9802    493    95%
