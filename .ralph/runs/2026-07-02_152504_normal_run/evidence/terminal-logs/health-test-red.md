setUpClass (test_health_api.HealthApiTests) ... ERROR

======================================================================
ERROR: setUpClass (test_health_api.HealthApiTests)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/test/testcases.py", line 202, in setUpClass
    cls._add_databases_failures()
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/test/testcases.py", line 229, in _add_databases_failures
    for alias in connections:
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/utils/connection.py", line 73, in __iter__
    return iter(self.settings)
                ^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/utils/functional.py", line 47, in __get__
    res = instance.__dict__[self.name] = self.func(instance)
                                         ^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/utils/connection.py", line 45, in settings
    self._settings = self.configure_settings(self._settings)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/db/utils.py", line 148, in configure_settings
    databases = super().configure_settings(databases)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/utils/connection.py", line 50, in configure_settings
    settings = getattr(django_settings, self.settings_name)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/conf/__init__.py", line 89, in __getattr__
    self._setup(name)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/conf/__init__.py", line 76, in _setup
    self._wrapped = Settings(settings_module)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/conf/__init__.py", line 190, in __init__
    mod = importlib.import_module(self.SETTINGS_MODULE)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/importlib/__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1206, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1178, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1128, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "<frozen importlib._bootstrap>", line 1206, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1178, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1142, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'sfpcl_credit.config'

----------------------------------------------------------------------
Ran 0 tests in 0.004s

FAILED (errors=1)
