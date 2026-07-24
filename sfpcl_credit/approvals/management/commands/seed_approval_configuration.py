from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from sfpcl_credit.approvals.modules import approval_matrix_configuration
from sfpcl_credit.identity.models import User


class Command(BaseCommand):
    help = "Idempotently seed the demo sanction committee from existing demo authority users."

    def handle(self, *args, **options):
        if not settings.ENABLE_DEMO_SURFACES:
            raise CommandError(
                "seed_approval_configuration is disabled by deployment settings."
            )
        try:
            data = approval_matrix_configuration.seed_demo_committee()
        except User.DoesNotExist as exc:
            raise CommandError(
                "Demo CFO/director users are missing. Run seed_demo_users first."
            ) from exc
        self.stdout.write(
            f"Approval configuration seeded: {data['committee_name']} ({data['version_number']})."
        )
