"""Retain current evidence for the carried Epic 010 Medium findings."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
ledger = (ROOT / "sfpcl_credit/processes/loan_servicing.py").read_text()
tests = "\n".join(
    (ROOT / path).read_text()
    for path in (
        "sfpcl_credit/tests/test_repayment_adjustment_api.py",
        "sfpcl_credit/tests/test_statement_evidence_owner_scope_closure.py",
        "sfpcl_credit/tests/test_statement_evidence_owner_migration.py",
        "sfpcl_credit/tests/test_subsidiary_deduction_reconciliation_api.py",
        "sfpcl_credit/tests/test_interest_rate_config_api.py",
    )
)

ledger_findings = []
if "rows.extend(" in ledger and "total_count=len(rows)" in ledger:
    ledger_findings.append(
        "ledger still materializes allocation and reversal histories before count/slice"
    )

seam_findings = []
if ".setUp()" in tests and "from sfpcl_credit.tests.test_" in tests:
    seam_findings.append(
        "changed acceptance tests still instantiate other TestCase fixtures and call setUp directly"
    )

print("Finding ID: AR-010-LEDGER-001")
print("Root ID: ROOT-010-LEDGER-PAGINATION")
for finding in ledger_findings:
    print(f"FAILING SIGNAL: {finding}")
print("Finding ID: AR-010-SERVICING-SEAM-001")
print("Root ID: ROOT-010-SERVICING-OWNER-SEAM")
for finding in seam_findings:
    print(f"FAILING SIGNAL: {finding}")
failed = bool(ledger_findings or seam_findings)
print(f"REVIEW_PROBE_EXIT: {1 if failed else 0}")
raise SystemExit(1 if failed else 0)
