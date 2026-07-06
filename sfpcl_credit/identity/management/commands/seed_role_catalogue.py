from django.core.management.base import BaseCommand

from sfpcl_credit.identity.catalogue import seed_catalogue


class Command(BaseCommand):
    help = "Idempotently seed the role, team, permission, and role-permission catalogue."

    def handle(self, *args, **options):
        summary = seed_catalogue()
        self.stdout.write(
            "Catalogue seeded: "
            f"{summary['permissions']} permissions, "
            f"{summary['roles']} roles, "
            f"{summary['teams']} teams, "
            f"{summary['role_permissions']} role-permission links."
        )
