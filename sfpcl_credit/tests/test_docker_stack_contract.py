import json
import shutil
import subprocess
import unittest
from pathlib import Path

from django.test import SimpleTestCase


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class DockerStackContractTests(SimpleTestCase):
    def _compose_config(self):
        if shutil.which("docker") is None:
            raise unittest.SkipTest("Docker CLI is not installed")
        try:
            result = subprocess.run(
                ["docker", "compose", "config", "--format", "json"],
                cwd=REPOSITORY_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            raise unittest.SkipTest(f"Docker Compose is unavailable: {exc}") from exc
        return json.loads(result.stdout)

    def test_compose_graph_keeps_runtime_dependencies_and_shared_storage(self):
        config = self._compose_config()
        services = config["services"]

        self.assertEqual(
            set(services),
            {"frontend", "backend", "postgres", "redis", "worker", "beat", "migrate"},
        )
        self.assertEqual(
            services["migrate"]["depends_on"]["postgres"]["condition"],
            "service_healthy",
        )
        for service_name in ("backend", "worker", "beat"):
            self.assertEqual(
                services[service_name]["depends_on"]["migrate"]["condition"],
                "service_completed_successfully",
            )
            self.assertEqual(
                services[service_name]["depends_on"]["redis"]["condition"],
                "service_healthy",
            )
            self.assertIn(
                {
                    "type": "volume",
                    "source": "app_storage",
                    "target": "/var/lib/sfpcl/storage",
                    "volume": {},
                },
                services[service_name]["volumes"],
            )
        self.assertEqual(
            services["frontend"]["depends_on"]["backend"]["condition"],
            "service_healthy",
        )
        self.assertEqual(
            services["backend"]["environment"]["SFPCL_POSTGRES_HOST"],
            "postgres",
        )
        self.assertEqual(
            services["worker"]["environment"]["SFPCL_CELERY_BROKER_URL"],
            "redis://redis:6379/0",
        )
        self.assertEqual(
            services["beat"]["environment"]["SFPCL_CELERY_RESULT_BACKEND"],
            "redis://redis:6379/1",
        )
        self.assertEqual(
            set(config["volumes"]),
            {"postgres_data", "redis_data", "app_storage"},
        )

    def test_nginx_keeps_spa_fallback_and_same_origin_backend_routes(self):
        nginx_config = (
            REPOSITORY_ROOT / "sfpcl-lms" / "docker" / "nginx.conf"
        ).read_text()

        self.assertIn("try_files $uri $uri/ /index.html;", nginx_config)
        self.assertIn("location /api/", nginx_config)
        self.assertIn("location /health/", nginx_config)
        self.assertEqual(nginx_config.count("proxy_pass http://sfpcl_backend;"), 2)
        self.assertIn("proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;", nginx_config)
        self.assertIn("client_max_body_size 25m;", nginx_config)
