# backend-coverage Results

Command: "/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python" -m coverage run --source=sfpcl_credit sfpcl_credit/manage.py test sfpcl_credit.tests && "/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python" -m coverage report --fail-under=85

Creating test database for alias 'default'...
Found 52 test(s).
System check identified no issues (0 silenced).
....................................Catalogue seeded: 171 permissions, 20 roles, 8 teams, 134 role-permission links.
Catalogue seeded: 171 permissions, 20 roles, 8 teams, 134 role-permission links.
................
----------------------------------------------------------------------
Ran 52 tests in 6.735s

OK
Destroying test database for alias 'default'...
Name                                                                          Stmts   Miss  Cover
-------------------------------------------------------------------------------------------------
sfpcl_credit/__init__.py                                                          0      0   100%
sfpcl_credit/api.py                                                              23      3    87%
sfpcl_credit/config/__init__.py                                                   0      0   100%
sfpcl_credit/config/asgi.py                                                       4      4     0%
sfpcl_credit/config/settings.py                                                  28      2    93%
sfpcl_credit/config/urls.py                                                       4      0   100%
sfpcl_credit/config/wsgi.py                                                       4      4     0%
sfpcl_credit/identity/__init__.py                                                 0      0   100%
sfpcl_credit/identity/catalogue.py                                               28      0   100%
sfpcl_credit/identity/management/__init__.py                                      0      0   100%
sfpcl_credit/identity/management/commands/__init__.py                             0      0   100%
sfpcl_credit/identity/management/commands/seed_role_catalogue.py                  7      0   100%
sfpcl_credit/identity/migrations/0001_initial.py                                  8      0   100%
sfpcl_credit/identity/migrations/0002_permission_rolepermission_and_more.py       7      0   100%
sfpcl_credit/identity/migrations/__init__.py                                      0      0   100%
sfpcl_credit/identity/models.py                                                 139      6    96%
sfpcl_credit/identity/modules/__init__.py                                         0      0   100%
sfpcl_credit/identity/modules/auth_service.py                                    88      7    92%
sfpcl_credit/identity/modules/tokens.py                                          36      4    89%
sfpcl_credit/identity/views.py                                                   72     11    85%
sfpcl_credit/manage.py                                                           10      0   100%
sfpcl_credit/ops.py                                                              16      0   100%
sfpcl_credit/tests/__init__.py                                                    0      0   100%
sfpcl_credit/tests/base.py                                                        8      0   100%
sfpcl_credit/tests/test_api_envelope.py                                          42      0   100%
sfpcl_credit/tests/test_auth_api.py                                             164      0   100%
sfpcl_credit/tests/test_auth_module.py                                          148      0   100%
sfpcl_credit/tests/test_backend_infrastructure.py                                29      0   100%
sfpcl_credit/tests/test_catalogue_seed.py                                        59      0   100%
sfpcl_credit/tests/test_health_api.py                                            28      0   100%
-------------------------------------------------------------------------------------------------
TOTAL                                                                           952     41    96%
