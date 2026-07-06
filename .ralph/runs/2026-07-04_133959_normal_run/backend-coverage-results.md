# backend-coverage Results

Command: "/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python" -m coverage run --source=sfpcl_credit sfpcl_credit/manage.py test sfpcl_credit.tests && "/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python" -m coverage report --fail-under=85

Creating test database for alias 'default'...
Found 75 test(s).
System check identified no issues (0 silenced).
.........................................Catalogue seeded: 171 permissions, 20 roles, 8 teams, 134 role-permission links.
Catalogue seeded: 171 permissions, 20 roles, 8 teams, 134 role-permission links.
......E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions).
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions).
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions).
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions).
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions).
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions).
........................
----------------------------------------------------------------------
Ran 75 tests in 12.426s

OK
Destroying test database for alias 'default'...
Name                                                                          Stmts   Miss  Cover
-------------------------------------------------------------------------------------------------
sfpcl_credit/__init__.py                                                          0      0   100%
sfpcl_credit/api.py                                                              25      3    88%
sfpcl_credit/config/__init__.py                                                   0      0   100%
sfpcl_credit/config/asgi.py                                                       4      4     0%
sfpcl_credit/config/settings.py                                                  28      2    93%
sfpcl_credit/config/urls.py                                                       6      0   100%
sfpcl_credit/config/wsgi.py                                                       4      4     0%
sfpcl_credit/identity/__init__.py                                                 0      0   100%
sfpcl_credit/identity/admin_views.py                                             96     22    77%
sfpcl_credit/identity/catalogue.py                                               28      0   100%
sfpcl_credit/identity/management/__init__.py                                      0      0   100%
sfpcl_credit/identity/management/commands/__init__.py                             0      0   100%
sfpcl_credit/identity/management/commands/seed_e2e_users.py                      45      2    96%
sfpcl_credit/identity/management/commands/seed_role_catalogue.py                  7      0   100%
sfpcl_credit/identity/migrations/0001_initial.py                                  8      0   100%
sfpcl_credit/identity/migrations/0002_permission_rolepermission_and_more.py       7      0   100%
sfpcl_credit/identity/migrations/__init__.py                                      0      0   100%
sfpcl_credit/identity/models.py                                                 139      6    96%
sfpcl_credit/identity/modules/__init__.py                                         0      0   100%
sfpcl_credit/identity/modules/admin_users.py                                    111     14    87%
sfpcl_credit/identity/modules/auth_service.py                                    88      7    92%
sfpcl_credit/identity/modules/tokens.py                                          36      4    89%
sfpcl_credit/identity/views.py                                                   72     11    85%
sfpcl_credit/manage.py                                                           10      0   100%
sfpcl_credit/ops.py                                                              16      0   100%
sfpcl_credit/tests/__init__.py                                                    0      0   100%
sfpcl_credit/tests/base.py                                                        8      0   100%
sfpcl_credit/tests/test_admin_users_api.py                                       94      0   100%
sfpcl_credit/tests/test_api_envelope.py                                          42      0   100%
sfpcl_credit/tests/test_auth_api.py                                             164      0   100%
sfpcl_credit/tests/test_auth_module.py                                          148      0   100%
sfpcl_credit/tests/test_backend_infrastructure.py                                29      0   100%
sfpcl_credit/tests/test_catalogue_seed.py                                        59      0   100%
sfpcl_credit/tests/test_health_api.py                                            28      0   100%
sfpcl_credit/tests/test_seed_e2e_users.py                                        59      0   100%
sfpcl_credit/tests/test_tracer_api.py                                           124      0   100%
sfpcl_credit/tests/test_workflow_guard.py                                        28      0   100%
sfpcl_credit/tracer/__init__.py                                                   0      0   100%
sfpcl_credit/tracer/apps.py                                                       4      0   100%
sfpcl_credit/tracer/migrations/0001_initial.py                                    8      0   100%
sfpcl_credit/tracer/migrations/__init__.py                                        0      0   100%
sfpcl_credit/tracer/models.py                                                    59      0   100%
sfpcl_credit/tracer/services.py                                                 117      4    97%
sfpcl_credit/tracer/views.py                                                    113     17    85%
sfpcl_credit/workflows/__init__.py                                                2      0   100%
sfpcl_credit/workflows/guard.py                                                  51      2    96%
-------------------------------------------------------------------------------------------------
TOTAL                                                                          1867    102    95%
