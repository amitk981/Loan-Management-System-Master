"""Fail closed when the reviewed financial owners retain known contract defects."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
RATE_MODULE = ROOT / "sfpcl_credit/configurations/modules/interest_rate_configuration.py"
RATE_MODELS = ROOT / "sfpcl_credit/configurations/models.py"
ALLOCATOR = ROOT / "sfpcl_credit/loans/modules/repayment_allocator.py"


def section(text, start, end):
    return text.split(start, 1)[1].split(end, 1)[0]


rate_module = RATE_MODULE.read_text()
rate_models = RATE_MODELS.read_text()
allocator = ALLOCATOR.read_text()

activate = section(rate_module, "def activate(", "def resolve_effective_rate(")
fanout = section(
    rate_module,
    "def _create_rate_histories_and_notices(",
    "\n\n",
)
rate_config_model = section(
    rate_models,
    "class InterestRateConfig(models.Model):",
    "class InterestRateHistory(models.Model):",
)
allocation_serializer = section(
    allocator,
    "def _serialize(allocation):",
    "\n\n__all__",
)

failures = []
if "InterestRateConsumptionSnapshot.objects" not in activate:
    failures.append(
        "AR-010-RATE-001: activation closes an open predecessor without checking consumed dates"
    )
if "objects =" not in rate_config_model and "def save(" not in rate_config_model:
    failures.append(
        "AR-010-RATE-001: InterestRateConfig has no immutable manager/save boundary for active rows"
    )
if "current_interest_rate" not in fanout:
    failures.append(
        "AR-010-RATE-001: rate fan-out records history but never advances LoanAccount.current_interest_rate"
    )
if "allocation.repayment.allocation_status" in allocation_serializer:
    failures.append(
        "AR-010-ALLOCATION-001: allocation replay recomputes mutable receipt status instead of the original response"
    )
if "return serialize(row)" in activate and "row.status == InterestRateConfig.STATUS_ACTIVE" in activate:
    failures.append(
        "AR-010-RATE-001: activation replay recomputes mutable notice summaries instead of the original response"
    )

print("Finding ID: AR-010-RATE-001")
print("Root ID: ROOT-010-RATE-VERSION-OWNER")
print("Finding ID: AR-010-ALLOCATION-001")
print("Root ID: ROOT-010-ALLOCATION-ADMISSION")
for failure in failures:
    print(f"FAILING SIGNAL: {failure}")
print(f"REVIEW_PROBE_EXIT: {1 if failures else 0}")
raise SystemExit(1 if failures else 0)
