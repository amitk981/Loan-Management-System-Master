import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from sfpcl_credit.security_regression.lane import run_security_regression
from sfpcl_credit.security_regression.matrix import required_control_ids
from sfpcl_credit.security_regression.runner import write_controlled_failure


class Command(BaseCommand):
    help = "Run the deterministic security/privacy release-hardening lane."

    def add_arguments(self, parser):
        parser.add_argument("--output", type=Path, required=True)
        parser.add_argument("--force-failure")

    def handle(self, *args, **options):
        forced_control = options["force_failure"]
        if forced_control:
            if forced_control not in required_control_ids():
                raise CommandError("Unknown security regression control")
            write_controlled_failure(options["output"], forced_control)
            raise CommandError(
                f"Security regression failed: {forced_control}"
            )
        summary = run_security_regression()
        output_path = options["output"]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(summary, separators=(",", ":"), sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self.stdout.write(
            f"security_regression result={summary['result']} "
            f"sha256={summary['summary_sha256']}"
        )
        if summary["result"] != "pass":
            failures = (
                summary["failing_controls"]
                + summary["failing_scanners"]
                + summary["failing_checks"]
            )
            raise CommandError(
                "Security regression failed: " + ", ".join(failures)
            )
