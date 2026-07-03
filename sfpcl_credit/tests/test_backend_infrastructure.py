import os
import subprocess
import sys
from pathlib import Path

from django.test import Client, SimpleTestCase


REPO_ROOT = Path(__file__).resolve().parents[2]
TEST_MODULES_WITH_MIGRATED_SCHEMA = [
    "sfpcl_credit/tests/test_auth_api.py",
    "sfpcl_credit/tests/test_auth_module.py",
    "sfpcl_credit/tests/test_api_envelope.py",
    "sfpcl_credit/tests/test_catalogue_seed.py",
]


def settings_value_with_env(env_overrides, expression):
    env = os.environ.copy()
    env.update(env_overrides)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            f"import sfpcl_credit.config.settings as settings; print({expression})",
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


class BackendInfrastructureTests(SimpleTestCase):
    def test_secret_key_comes_from_environment_with_dev_fallback(self):
        self.assertEqual(
            settings_value_with_env(
                {"SFPCL_SECRET_KEY": "test-env-secret-key"},
                "settings.SECRET_KEY",
            ),
            "test-env-secret-key",
        )

    def test_allowed_hosts_are_read_as_comma_separated_environment_values(self):
        self.assertEqual(
            settings_value_with_env(
                {"SFPCL_ALLOWED_HOSTS": "localhost,127.0.0.1,api.testserver"},
                "settings.ALLOWED_HOSTS",
            ),
            "['localhost', '127.0.0.1', 'api.testserver']",
        )

    def test_cors_origins_are_read_as_comma_separated_environment_values(self):
        self.assertEqual(
            settings_value_with_env(
                {
                    "SFPCL_CORS_ORIGINS": (
                        "http://localhost:5173,http://127.0.0.1:5173"
                    )
                },
                "settings.CORS_ALLOWED_ORIGINS",
            ),
            "['http://localhost:5173', 'http://127.0.0.1:5173']",
        )

    def test_frontend_dev_origin_receives_cors_allow_origin_header(self):
        response = Client().get(
            "/api/v1/health/live/",
            headers={"Origin": "http://localhost:5173"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Access-Control-Allow-Origin"], "http://localhost:5173"
        )

    def test_backend_tests_use_migrated_test_database_not_manual_schema_setup(self):
        forbidden_snippets = [
            "django." + "setup()",
            "schema_editor." + "create_model",
            "ensure_" + "identity_tables",
            "ensure_" + "catalogue_tables",
        ]

        for module in TEST_MODULES_WITH_MIGRATED_SCHEMA:
            source = (REPO_ROOT / module).read_text(encoding="utf-8")
            for snippet in forbidden_snippets:
                self.assertNotIn(snippet, source, module)
