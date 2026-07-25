import json
import os
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
POSTGRES_ENVIRONMENT_KEYS = (
    "SFPCL_POSTGRES_DB",
    "SFPCL_POSTGRES_USER",
    "SFPCL_POSTGRES_PASSWORD",
    "SFPCL_POSTGRES_HOST",
    "SFPCL_POSTGRES_PORT",
    "SFPCL_POSTGRES_TEST_DB",
)


class DatabaseSettingsTests(SimpleTestCase):
    def _database_settings(self, **overrides):
        environment = os.environ.copy()
        for key in POSTGRES_ENVIRONMENT_KEYS:
            environment.pop(key, None)
        environment.update(overrides)
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import json;"
                    "from sfpcl_credit.config.settings import DATABASES;"
                    "print(json.dumps(DATABASES['default'], default=str))"
                ),
            ],
            cwd=REPOSITORY_ROOT,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def test_sqlite_remains_the_default_without_postgres_host(self):
        database = self._database_settings()

        self.assertEqual(database["ENGINE"], "django.db.backends.sqlite3")
        self.assertTrue(database["NAME"].endswith("sfpcl_credit/db.sqlite3"))

    def test_explicit_postgres_environment_selects_postgres(self):
        database = self._database_settings(
            SFPCL_POSTGRES_DB="local_credit",
            SFPCL_POSTGRES_USER="local_user",
            SFPCL_POSTGRES_PASSWORD="local_password",
            SFPCL_POSTGRES_HOST="postgres",
            SFPCL_POSTGRES_PORT="5544",
            SFPCL_POSTGRES_TEST_DB="test_local_credit",
        )

        self.assertEqual(database["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual(database["NAME"], "local_credit")
        self.assertEqual(database["USER"], "local_user")
        self.assertEqual(database["PASSWORD"], "local_password")
        self.assertEqual(database["HOST"], "postgres")
        self.assertEqual(database["PORT"], "5544")
        self.assertEqual(database["TEST"]["NAME"], "test_local_credit")
