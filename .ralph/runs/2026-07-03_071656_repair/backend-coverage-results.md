# backend-coverage Results

Command: python3 -m coverage run --source=sfpcl_credit sfpcl_credit/manage.py test sfpcl_credit.tests && python3 -m coverage report --fail-under=85

Creating test database for alias 'default'...
Found 12 test(s).
System check identified no issues (0 silenced).
............
----------------------------------------------------------------------
Ran 12 tests in 1.351s

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
sfpcl_credit/identity/views.py                       138     23    83%
sfpcl_credit/manage.py                                10      0   100%
sfpcl_credit/ops.py                                   19      0   100%
sfpcl_credit/tests/__init__.py                         0      0   100%
sfpcl_credit/tests/test_auth_api.py                  111      1    99%
sfpcl_credit/tests/test_health_api.py                 32      0   100%
----------------------------------------------------------------------
TOTAL                                                458     36    92%
