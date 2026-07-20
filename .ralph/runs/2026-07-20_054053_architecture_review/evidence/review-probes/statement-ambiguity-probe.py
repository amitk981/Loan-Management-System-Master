"""Static fail-closed probe for the subsidiary statement ambiguity contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
module = (
    ROOT / "sfpcl_credit/loans/modules/bank_statement_matching.py"
).read_text()
tests = (
    ROOT / "sfpcl_credit/tests/test_statement_evidence_owner_scope_closure.py"
).read_text()

ambiguity_owner = module.split(
    "def _subsidiary_narration_is_ambiguous", 1
)[1].split("def _bounded", 1)[0]
matrix = tests.split(
    "def test_subsidiary_auto_match_requires_borrower_and_application_facts", 1
)[1].split("def test_statement_list_hides", 1)[0]

failures = []
if "application_model" in ambiguity_owner and "member" not in ambiguity_owner:
    failures.append(
        "the owner checks conflicting application references but never conflicting borrower identities"
    )
if "conflicting_application" in matrix and "conflicting_member" not in matrix:
    failures.append(
        "AC-STATEMENT-3's ambiguity matrix asserts only the application-conflict branch"
    )

print("Finding ID: AR-010-STATEMENT-001")
print("Root ID: ROOT-010-STATEMENT-EVIDENCE")
for failure in failures:
    print(f"FAILING SIGNAL: {failure}")
print(f"REVIEW_PROBE_EXIT: {1 if failures else 0}")
raise SystemExit(1 if failures else 0)
