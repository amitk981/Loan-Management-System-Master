# backend-coverage Results

Command: "/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python" -m coverage run --source=sfpcl_credit sfpcl_credit/manage.py test sfpcl_credit.tests && "/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python" -m coverage report --fail-under=85

Creating test database for alias 'default'...
Found 13 test(s).
System check identified no issues (0 silenced).
.............
----------------------------------------------------------------------
Ran 13 tests in 1.613s

OK
Destroying test database for alias 'default'...
Name                                               Stmts   Miss  Cover
----------------------------------------------------------------------
sfpcl_credit/__init__.py                               0      0   100%
sfpcl_credit/config/__init__.py                        0      0   100%
sfpcl_credit/config/asgi.py                            4      4     0%
sfpcl_credit/config/settings.py                       17      0   100%
sfpcl_credit/config/urls.py                            4      0   100%
sfpcl_credit/config/wsgi.py                            4      4     0%
sfpcl_credit/identity/__init__.py                      0      0   100%
sfpcl_credit/identity/migrations/0001_initial.py       8      0   100%
sfpcl_credit/identity/migrations/__init__.py           0      0   100%
sfpcl_credit/identity/models.py                      111      4    96%
sfpcl_credit/identity/views.py                       135     21    84%
sfpcl_credit/manage.py                                10      0   100%
sfpcl_credit/ops.py                                   19      0   100%
sfpcl_credit/tests/__init__.py                         0      0   100%
sfpcl_credit/tests/test_auth_api.py                  125      1    99%
sfpcl_credit/tests/test_health_api.py                 32      0   100%
----------------------------------------------------------------------
TOTAL                                                469     34    93%
