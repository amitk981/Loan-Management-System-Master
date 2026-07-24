import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from sfpcl_credit.identity.catalogue import seed_catalogue
from sfpcl_credit.identity.models import (
    Permission,
    Role,
    RolePermission,
    Team,
    User,
    UserTeamMembership,
)


DEMO_PASSWORD = "DemoStaff123!"
TRACER_PERMISSION_CODE = "tracer.lifecycle.run"
DEMO_TRACER_ROLE_CODE = "local_demo_tracer_user"

DEMO_USERS = [
    {
        "email": "demo.cfo@sfpcl.example",
        "full_name": "Demo CFO",
        "role_code": "cfo",
        "team_codes": ["sanction_committee"],
        "approval_authority_type": "cfo",
    },
    {
        "email": "demo.director1@sfpcl.example",
        "full_name": "Demo Director One",
        "role_code": "director",
        "team_codes": ["sanction_committee"],
        "approval_authority_type": "director",
    },
    {
        "email": "demo.director2@sfpcl.example",
        "full_name": "Demo Director Two",
        "role_code": "director",
        "team_codes": ["sanction_committee"],
        "approval_authority_type": "director",
    },
    {
        "email": "demo.system_admin@sfpcl.example",
        "full_name": "Demo System Administrator",
        "role_code": "system_admin",
        "team_codes": ["it"],
    },
    {
        "email": "demo.credit_manager@sfpcl.example",
        "full_name": "Demo Credit Manager",
        "role_code": "credit_manager",
        "team_codes": ["credit_assessment"],
    },
    {
        "email": "demo.compliance@sfpcl.example",
        "full_name": "Demo Compliance User",
        "role_code": "compliance_team_member",
        "team_codes": ["compliance"],
    },
    {
        "email": "demo.treasury@sfpcl.example",
        "full_name": "Demo Treasury Finance User",
        "role_code": "senior_manager_finance",
        "team_codes": ["treasury"],
    },
    {
        "email": "demo.internal_auditor@sfpcl.example",
        "full_name": "Demo Internal Auditor",
        "role_code": "internal_auditor",
        "team_codes": ["audit"],
    },
    {
        "email": "demo.tracer@sfpcl.example",
        "full_name": "Demo Tracer User",
        "role_code": DEMO_TRACER_ROLE_CODE,
        "team_codes": ["sales"],
        "exact_permission_codes": [TRACER_PERMISSION_CODE],
    },
    {
        "email": "demo.zero@sfpcl.example",
        "full_name": "Demo Zero Permission User",
        "role_code": "it_head",
        "team_codes": [],
        "exact_permission_codes": [],
    },
]


class Command(BaseCommand):
    help = (
        "Idempotently seed deterministic local/demo staff users. Refuses to run "
        "unless SFPCL_DEBUG=true and SFPCL_ALLOW_DEMO_SEED=true."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self._enforce_demo_guard()
        seed_catalogue()
        self._ensure_tracer_permission()

        seeded = []
        for spec in DEMO_USERS:
            role = self._required_active_role(spec["role_code"])
            self._enforce_exact_role_permissions(
                role, spec.get("exact_permission_codes")
            )
            teams = [self._required_active_team(code) for code in spec["team_codes"]]
            user = self._ensure_user(spec, role)
            self._sync_memberships(user, teams)
            seeded.append(user.email)


        self.stdout.write(
            "Demo users seeded: "
            + ", ".join(seeded)
            + " (predictable local/dev password set; do not use in production)."
        )

    @staticmethod
    def _env_true(name):
        return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}

    @classmethod
    def _enforce_demo_guard(cls):
        if not settings.ENABLE_DEMO_SURFACES:
            raise CommandError(
                "seed_demo_users is disabled by deployment settings."
            )
        if not cls._env_true("SFPCL_DEBUG") or not cls._env_true(
            "SFPCL_ALLOW_DEMO_SEED"
        ):
            raise CommandError(
                "seed_demo_users is for local/demo databases only. "
                "Set SFPCL_DEBUG=true and SFPCL_ALLOW_DEMO_SEED=true to run it."
            )

    @staticmethod
    def _ensure_tracer_permission():
        permission, _created = Permission.objects.update_or_create(
            permission_code=TRACER_PERMISSION_CODE,
            defaults={
                "permission_name": "Run MVP tracer",
                "module_name": "tracer",
                "risk_level": Permission.RISK_HIGH,
            },
        )
        tracer_role, _created = Role.objects.update_or_create(
            role_code=DEMO_TRACER_ROLE_CODE,
            defaults={
                "role_name": "Local Demo Tracer User",
                "description": (
                    "Local/dev-only role for the guarded demo tracer account. "
                    "Not part of the source RBAC catalogue."
                ),
                "is_system_role": False,
                "status": "active",
            },
        )
        RolePermission.objects.get_or_create(role=tracer_role, permission=permission)
        RolePermission.objects.filter(permission=permission).exclude(
            role=tracer_role
        ).delete()

    @staticmethod
    def _required_active_role(role_code):
        try:
            role = Role.objects.get(role_code=role_code)
        except Role.DoesNotExist as exc:
            raise CommandError(
                f"Required role '{role_code}' is missing. Run seed_role_catalogue first."
            ) from exc
        if role.status != "active":
            raise CommandError(f"Required role '{role_code}' is not active.")
        return role

    @staticmethod
    def _required_active_team(team_code):
        try:
            team = Team.objects.get(team_code=team_code)
        except Team.DoesNotExist as exc:
            raise CommandError(
                f"Required team '{team_code}' is missing. Run seed_role_catalogue first."
            ) from exc
        if team.status != "active":
            raise CommandError(f"Required team '{team_code}' is not active.")
        return team

    @staticmethod
    def _enforce_exact_role_permissions(role, expected_codes):
        if expected_codes is None:
            return
        actual_codes = set(
            Permission.objects.filter(role_permissions__role=role).values_list(
                "permission_code", flat=True
            )
        )
        if actual_codes != set(expected_codes):
            raise CommandError(
                f"Role '{role.role_code}' must have exactly "
                f"{sorted(expected_codes)} for demo seeding; found {sorted(actual_codes)}."
            )

    @staticmethod
    def _ensure_user(spec, role):
        user, _created = User.objects.get_or_create(
            email=spec["email"],
            defaults={
                "full_name": spec["full_name"],
                "status": User.ACTIVE_STATUS,
                "primary_role": role,
            },
        )
        user.full_name = spec["full_name"]
        user.primary_role = role
        user.status = User.ACTIVE_STATUS
        user.approval_authority_type = spec.get("approval_authority_type", "")
        user.set_password(DEMO_PASSWORD)
        user.save()
        return user


    @staticmethod
    def _sync_memberships(user, teams):
        target_team_ids = {team.team_id for team in teams}
        UserTeamMembership.objects.filter(user=user).exclude(
            team_id__in=target_team_ids
        ).update(status="inactive")

        for team in teams:
            membership, _created = UserTeamMembership.objects.get_or_create(
                user=user,
                team=team,
                defaults={"status": "active", "team_role": "member"},
            )
            if membership.status != "active" or membership.team_role != "member":
                membership.status = "active"
                membership.team_role = "member"
                membership.save(update_fields=["status", "team_role"])
