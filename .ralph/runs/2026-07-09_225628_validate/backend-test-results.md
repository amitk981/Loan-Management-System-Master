# backend-test Results

Command: "python3" sfpcl_credit/manage.py test sfpcl_credit.tests -v 2

Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Found 207 test(s).
Operations to perform:
  Synchronize unmigrated apps: corsheaders
  Apply all migrations: applications, communications, configurations, contenttypes, documents, identity, members, scheduler, tracer, workflows
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying identity.0001_initial... OK
  Applying identity.0002_permission_rolepermission_and_more... OK
  Applying documents.0001_initial... OK
  Applying members.0001_initial... OK
  Applying members.0002_profile_shells... OK
  Applying members.0003_individual_profile_details... OK
  Applying members.0004_nominee... OK
  Applying members.0005_shareholding_and_more... OK
  Applying members.0006_landholding_cropplan_and_more... OK
  Applying members.0007_kycprofile_kycdocument_and_more... OK
  Applying members.0008_cancelledcheque_bankaccount_and_more... OK
  Applying applications.0001_initial... OK
  Applying applications.0002_loanapplication_submitted_by_user... OK
  Applying applications.0003_systemsequence_loanrequestregisterentry... OK
  Applying applications.0004_applicationdocument_and_more... OK
  Applying applications.0005_application_deficiency... OK
  Applying communications.0001_initial... OK
  Applying communications.0002_communication... OK
  Applying communications.0003_notification... OK
  Applying configurations.0001_initial... OK
  Applying contenttypes.0001_initial... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying identity.0003_portal_member_auth... OK
  Applying scheduler.0001_initial... OK
  Applying tracer.0001_initial... OK
  Applying workflows.0001_canonical_workflow_event... OK
  Applying tracer.0002_remove_tracer_workflowevent_state... OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Traceback (most recent call last):
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-09_222250_normal_run/sfpcl_credit/manage.py", line 17, in <module>
    main()
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-09_222250_normal_run/sfpcl_credit/manage.py", line 13, in main
    execute_from_command_line(sys.argv)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/core/management/__init__.py", line 442, in execute_from_command_line
    utility.execute()
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/core/management/__init__.py", line 436, in execute
    self.fetch_command(subcommand).run_from_argv(self.argv)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/core/management/commands/test.py", line 24, in run_from_argv
    super().run_from_argv(argv)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/core/management/base.py", line 413, in run_from_argv
    self.execute(*args, **cmd_options)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/core/management/base.py", line 459, in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/core/management/commands/test.py", line 68, in handle
    failures = test_runner.run_tests(test_labels)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/test/runner.py", line 1067, in run_tests
    self.run_checks(databases)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/test/runner.py", line 989, in run_checks
    call_command("check", verbosity=self.verbosity, databases=databases)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/core/management/__init__.py", line 194, in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/core/management/base.py", line 459, in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/core/management/commands/check.py", line 76, in handle
    self.check(
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/core/management/base.py", line 486, in check
    all_issues = checks.run_checks(
                 ^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/core/checks/registry.py", line 88, in run_checks
    new_errors = check(app_configs=app_configs, databases=databases)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/core/checks/urls.py", line 14, in check_url_config
    return check_resolver(resolver)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/core/checks/urls.py", line 24, in check_resolver
    return check_method()
           ^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/urls/resolvers.py", line 519, in check
    for pattern in self.url_patterns:
                   ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/utils/functional.py", line 47, in __get__
    res = instance.__dict__[self.name] = self.func(instance)
                                         ^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/urls/resolvers.py", line 738, in url_patterns
    patterns = getattr(self.urlconf_module, "urlpatterns", self.urlconf_module)
                       ^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/utils/functional.py", line 47, in __get__
    res = instance.__dict__[self.name] = self.func(instance)
                                         ^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/urls/resolvers.py", line 731, in urlconf_module
    return import_module(self.urlconf_name)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/importlib/__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1206, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1178, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1149, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-09_222250_normal_run/sfpcl_credit/config/urls.py", line 3, in <module>
    from sfpcl_credit.applications import views as application_views
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-09_222250_normal_run/sfpcl_credit/applications/views.py", line 5, in <module>
    from sfpcl_credit.applications import services
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-09_222250_normal_run/sfpcl_credit/applications/services.py", line 18, in <module>
    from sfpcl_credit.identity.modules import auth_service
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-09_222250_normal_run/sfpcl_credit/identity/modules/auth_service.py", line 18, in <module>
    from sfpcl_credit.identity.modules.tokens import (
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-09_222250_normal_run/sfpcl_credit/identity/modules/tokens.py", line 12, in <module>
    import jwt
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/jwt/__init__.py", line 1, in <module>
    from .api_jwk import PyJWK, PyJWKSet
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/jwt/api_jwk.py", line 7, in <module>
    from .algorithms import get_default_algorithms, has_crypto, requires_cryptography
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/jwt/algorithms.py", line 11, in <module>
    from .utils import (
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/jwt/utils.py", line 7, in <module>
    from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurve
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/cryptography/hazmat/primitives/asymmetric/ec.py", line 11, in <module>
    from cryptography.exceptions import UnsupportedAlgorithm, _Reasons
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/cryptography/exceptions.py", line 9, in <module>
    from cryptography.hazmat.bindings._rust import exceptions as rust_exceptions
ImportError: dlopen(/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/_cffi_backend.cpython-311-darwin.so, 0x0002): tried: '/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/_cffi_backend.cpython-311-darwin.so' (mach-o file, but is an incompatible architecture (have 'arm64', need 'x86_64')), '/System/Volumes/Preboot/Cryptexes/OS/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/_cffi_backend.cpython-311-darwin.so' (no such file), '/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/_cffi_backend.cpython-311-darwin.so' (mach-o file, but is an incompatible architecture (have 'arm64', need 'x86_64'))
