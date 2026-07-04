from django.core.management.base import BaseCommand
from django.db import transaction

from sfpcl_credit.identity.models import Permission, Role, RolePermission, User

# Non-secret credentials for the local Playwright suite only. The suite logs in
# through the production auth path (POST /auth/login/ + GET /auth/me/), so a real
# backend user with a real password hash is required — no frontend fixtures.
E2E_PASSWORD = "E2eTracer123!"
TRACER_PERMISSION_CODE = "tracer.lifecycle.run"

TRACER_USER_EMAIL = "e2e.tracer@sfpcl.example"
TRACER_ROLE_CODE = "e2e_tracer"

# `it_head` maps to the neutral `backend_staff` frontend role and carries no
# canonical permissions (see identity/catalogue.py), so it drives the
# restricted-UI browser checks (002EY req 9, 11).
ZERO_USER_EMAIL = "e2e.zero@sfpcl.example"
ZERO_ROLE_CODE = "it_head"


class Command(BaseCommand):
    help = (
        "Idempotently seed the deterministic staff users the Playwright E2E suite "
        "logs in as: a tracer-only staff user and a zero-permission staff user."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        tracer_permission, _ = Permission.objects.get_or_create(
            permission_code=TRACER_PERMISSION_CODE,
            defaults={
                "permission_name": "Run MVP tracer",
                "module_name": "tracer",
                "risk_level": Permission.RISK_HIGH,
            },
        )

        tracer_role = self._ensure_role(
            TRACER_ROLE_CODE,
            role_name="E2E Tracer Staff",
            description="Automated E2E staff role: tracer lifecycle permission only.",
        )
        RolePermission.objects.get_or_create(
            role=tracer_role, permission=tracer_permission
        )

        zero_role = self._ensure_role(
            ZERO_ROLE_CODE,
            role_name="IT Head",
            description="Access control and system security oversight",
        )

        tracer_user = self._ensure_user(
            email=TRACER_USER_EMAIL,
            full_name="E2E Tracer Staff",
            role=tracer_role,
        )
        zero_user = self._ensure_user(
            email=ZERO_USER_EMAIL,
            full_name="E2E Zero Permission Staff",
            role=zero_role,
        )

        self.stdout.write(
            "E2E users seeded: "
            f"{tracer_user.email} (role {tracer_role.role_code}, "
            f"permission {TRACER_PERMISSION_CODE}); "
            f"{zero_user.email} (role {zero_role.role_code}, no permissions)."
        )

    @staticmethod
    def _ensure_role(role_code, *, role_name, description):
        role, _created = Role.objects.get_or_create(
            role_code=role_code,
            defaults={
                "role_name": role_name,
                "description": description,
                "is_system_role": False,
                "status": "active",
            },
        )
        # A pre-existing role (e.g. it_head from the catalogue) must stay active so
        # its user can authenticate and expose permissions.
        if role.status != "active":
            role.status = "active"
            role.save(update_fields=["status"])
        return role

    @staticmethod
    def _ensure_user(*, email, full_name, role):
        user, _created = User.objects.get_or_create(
            email=email,
            defaults={
                "full_name": full_name,
                "status": "active",
                "primary_role": role,
            },
        )
        # Keep the deterministic role, status, and password even if the row existed.
        user.full_name = full_name
        user.primary_role = role
        user.status = "active"
        user.set_password(E2E_PASSWORD)
        user.save()
        return user
