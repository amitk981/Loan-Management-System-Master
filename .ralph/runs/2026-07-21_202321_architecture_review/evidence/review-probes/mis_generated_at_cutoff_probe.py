"""Review-only reproducer for the CR-015 MIS cutoff-owner recurrence."""

import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from types import SimpleNamespace


sys.path.insert(0, str(Path(__file__).resolve().parents[5]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sfpcl_credit.config.settings")

import django

django.setup()

from sfpcl_credit.monitoring.modules.quarterly_mis import _invoice_status_at_cutoff


FINDING_ID = "AR-010-MIS-001"
ROOT_ID = "ROOT-010-MIS-AS-OF-OWNER"

print(f"Finding ID: {FINDING_ID}")
print(f"Root ID: {ROOT_ID}")

invoice = SimpleNamespace(
    generated_at=datetime(2026, 7, 2, 10, 0, tzinfo=timezone.utc),
    issued_at=None,
    invoice_status="draft",
)
actual = _invoice_status_at_cutoff(invoice=invoice, cutoff=date(2026, 6, 30))
print(f"Observed cutoff status: {actual}")
print("Expected cutoff status: not_generated")
assert actual == "not_generated", (
    "FAIL: CR-015 reads nonexistent InterestInvoice.created_at and admits an invoice "
    "generated after the historical cutoff."
)
