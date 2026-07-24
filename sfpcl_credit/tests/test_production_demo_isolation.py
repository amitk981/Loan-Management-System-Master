import base64
import json
import os
import subprocess
from pathlib import Path

from django.test import SimpleTestCase, TestCase, override_settings

from sfpcl_credit.identity.models import PortalAccount, Role, User, UserSession
from sfpcl_credit.members.models import Member


BACKEND_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PYTHON = "/Users/amitkallapa/LMS/.ralph/venv/bin/python"
PRODUCTION_FIELD_KEY_ENVIRONMENT = {
    "SFPCL_FIELD_ENCRYPTION_CURRENT_VERSION": "production-test-v1",
    "SFPCL_FIELD_ENCRYPTION_KEY_REF": "vault:test/field/production-test-v1",
    "SFPCL_FIELD_ENCRYPTION_KEYS": json.dumps(
        {
            "production-test-v1": base64.urlsafe_b64encode(b"P" * 32).decode(
                "ascii"
            )
        }
    ),
    "SFPCL_FIELD_LOOKUP_KEY": base64.urlsafe_b64encode(b"H" * 32).decode(
        "ascii"
    ),
}


class ProductionDemoIsolationTests(SimpleTestCase):
    def test_production_settings_do_not_register_tracer_application_or_urls(self):
        probe = """
import django
django.setup()

from django.apps import apps
from django.test import Client
from django.urls import URLResolver, NoReverseMatch, get_resolver, reverse

assert not apps.is_installed("sfpcl_credit.tracer")

def flatten(patterns):
    for pattern in patterns:
        yield pattern
        if isinstance(pattern, URLResolver):
            yield from flatten(pattern.url_patterns)

for pattern in flatten(get_resolver().url_patterns):
    route = str(pattern.pattern).lower()
    name = (getattr(pattern, "name", None) or "").lower()
    callback_module = getattr(getattr(pattern, "callback", None), "__module__", "").lower()
    assert "tracer" not in (route + name + callback_module), (
        route,
        name,
        callback_module,
    )

try:
    reverse("tracer-member-create")
except NoReverseMatch:
    pass
else:
    raise AssertionError("production URLconf registered tracer-member-create")

response = Client().post(
    "/api/v1/tracer/members/",
    data={"member_number": "PRODUCTION-PROBE"},
    content_type="application/json",
)
assert response.status_code == 404, response.status_code
"""
        environment = {
            **os.environ,
            "DJANGO_SETTINGS_MODULE": "sfpcl_credit.config.production_settings",
            **PRODUCTION_FIELD_KEY_ENVIRONMENT,
        }

        result = subprocess.run(
            [BACKEND_PYTHON, "-c", probe],
            cwd=BACKEND_ROOT.parent,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class ProductionDemoIdentityTests(TestCase):
    @override_settings(ENABLE_DEMO_SURFACES=False)
    def test_existing_demo_staff_user_cannot_authenticate_in_production(self):
        role = Role.objects.create(
            role_code="local_demo_tracer_user",
            role_name="Local Demo Tracer User",
            status="active",
        )
        user = User.objects.create(
            email="demo.tracer@sfpcl.example",
            full_name="Demo Tracer User",
            primary_role=role,
            status="active",
        )
        user.set_password("DemoStaff123!")
        user.save(update_fields=["password_hash"])

        response = self.client.post(
            "/api/v1/auth/login/",
            data={
                "email": "demo.tracer@sfpcl.example",
                "password": "DemoStaff123!",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401, response.content)
        self.assertFalse(UserSession.objects.filter(user=user).exists())

    @override_settings(ENABLE_DEMO_SURFACES=False)
    def test_existing_e2e_portal_user_cannot_authenticate_in_production(self):
        role = Role.objects.create(
            role_code="borrower_portal_user",
            role_name="Borrower Portal User",
            status="active",
        )
        user = User.objects.create(
            email="e2e.portal@sfpcl.example",
            full_name="E2E Portal User",
            primary_role=role,
            status="active",
        )
        user.set_password("E2eTracer123!")
        user.save(update_fields=["password_hash"])
        member = Member.objects.create(
            member_number="E2E-PRODUCTION-PROBE",
            member_type="individual_farmer",
            legal_name="Synthetic Portal Member",
            display_name="Synthetic Portal Member",
            folio_number="E2E-PRODUCTION-FOLIO",
            membership_status="active",
            pan_encrypted="synthetic-pan",
            pan_hash="synthetic-pan-hash",
            aadhaar_encrypted="synthetic-aadhaar",
            aadhaar_hash="synthetic-aadhaar-hash",
            email=user.email,
            kyc_status="verified",
            default_status="no_default",
        )
        PortalAccount.objects.create(
            member=member,
            user=user,
            status=PortalAccount.STATUS_ACTIVE,
        )

        response = self.client.post(
            "/api/v1/portal/auth/login/",
            data={
                "identifier": user.email,
                "password": "E2eTracer123!",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401, response.content)
        self.assertFalse(UserSession.objects.filter(user=user).exists())

    def test_production_settings_refuse_all_demo_seed_commands(self):
        probe = """
import django
django.setup()

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError

assert settings.ENABLE_DEMO_SURFACES is False
for command_name in (
    "seed_demo_users",
    "seed_e2e_users",
    "seed_portal_e2e_fixture",
    "seed_epic_009_e2e_fixture",
    "seed_approval_configuration",
):
    try:
        call_command(command_name)
    except CommandError as error:
        assert "disabled by deployment settings" in str(error), str(error)
    else:
        raise AssertionError(f"{command_name} ran under production settings")
"""
        environment = {
            **os.environ,
            "DJANGO_SETTINGS_MODULE": "sfpcl_credit.config.production_settings",
            "SFPCL_DEBUG": "true",
            "SFPCL_ALLOW_DEMO_SEED": "true",
            "SFPCL_ALLOW_E2E_SEED": "true",
            **PRODUCTION_FIELD_KEY_ENVIRONMENT,
        }

        result = subprocess.run(
            [BACKEND_PYTHON, "-c", probe],
            cwd=BACKEND_ROOT.parent,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
