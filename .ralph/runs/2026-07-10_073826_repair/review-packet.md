# Review Packet: 2026-07-10_073826_repair

## Result
Success — ready for Ralph independent validation and commit.

## Slice
`006C-loan-limit-configuration-and-calculator` (High risk, backend-only)

## Repair diagnosis
The prior `2026-07-10_073133_normal_run` failed before repository access because the Codex
code-mode host binary was missing. It produced no product changes; baseline gates passed but Ralph
correctly rejected its no-op and unfilled artifacts. This repair used a functional runner and did
not salvage the orphan's ungated files.

## Reviewer walkthrough

1. Inspect `applications/models.py` and migration `0008_loanlimitassessment.py` for the source
   §14.2 one-to-one financial snapshot.
2. Inspect `applications/services.py::calculate_loan_limit` for eligibility gating, same-member
   validation, active/effective Board-policy selection, decimal formulas, atomic update, and
   metadata-only evidence.
3. Inspect the calculate view/URL for authentication, `credit.loan_limit.calculate`, application
   object access, standard envelopes, and failure codes.
4. Inspect the six new public-interface tests in `test_loan_applications_api.py`: formula and
   stored result; equal/below/rerun; pending/ineligible/policy blockers; missing/cross-member facts;
   permission/object scope; and per-share-cap/land-lower branch.
5. Inspect A-047 for the explicit cap interpretation and 006D/006E for sharpened follow-on scope.

## Source traceability

- Source says `shareholding_based_limit = number_of_shares × configured percentage or per-share
  cap`, land limit is scale times acres, and final amount is lower-of-two (`api-contracts.md`
  §23.2; `data-model.md` §35.1; functional BR-019 through BR-021). Code calculates both with
  `Decimal`, applies the configured cap as a ceiling, and stores the lower value. Verified by
  `test_loan_limit_calculation_stores_source_backed_lower_of_two_result` and
  `test_loan_limit_per_share_cap_policy_uses_land_limit_when_lower`.
- Source says the exact percentage/cap, rule version, configuration source, and warnings must be
  returned because 30% vs 10% vs Rs 200 remains unresolved (`api-contracts.md` §23.1-§23.3;
  functional BR-024/BR-025). Code selects only an active/effective Board-referenced config, returns
  its exact values/source/version, and blocks missing/unresolved policy. Verified by the tracer and
  `test_loan_limit_blocks_pending_ineligible_and_missing_policy_without_success_evidence`.
- Source says above-limit requests require an exception flag/warning and equal/below do not
  (`api-contracts.md` §23.1; test-plan MOD-LIMIT-004 through MOD-LIMIT-006). Code sets both flags and
  `REQUESTED_AMOUNT_EXCEEDS_LIMIT` only above the stored final amount. Verified by the tracer and
  equal/below boundary test.
- Source §14.2 requires a one-to-one assessment with all financial/rule/actor/time snapshots, and
  §34.1 requires assessment, audit, and workflow writes atomically. Code adds the one-to-one model
  and transaction; reruns preserve the UUID. Verified by stored-row/evidence assertions and the
  rerun test.
- Slice permissions require `credit.loan_limit.calculate` plus existing application object access,
  and cross-member facts must not broaden authority. Code checks both before calculation and
  filters every fact to the application member. Verified by the access and source-fact tests, which
  also assert no calculation/audit/workflow evidence.

## Validation evidence

- TDD red: `evidence/terminal-logs/006C-red-tracer.log` (`404 != 200`).
- TDD green: `evidence/terminal-logs/006C-green-tracer.log`.
- Focused application API: 37 tests in `006C-green-loan-application-api.log`.
- Backend full: 288 tests in `backend-tests-full.log`.
- Backend coverage: 95% in `backend-coverage-report.log` (floor 85%).
- Backend check and migration sync: `backend-check.log`, `backend-makemigrations-check.log`.
- Frontend lint/typecheck/tests/build: corresponding logs; 98 tests passed.
- Diff check: recorded in final summary; no protected path or debug instrumentation.

## Residual review questions

- Confirm A-047's standard cap-as-ceiling interpretation. Values remain configuration-owned, so a
  future explicit rule-mode field can refine behavior without changing historical snapshots.
- Confirm 006D persists configuration-source metadata needed for immutable GET readback rather
  than resolving it from a current mutable config row.

## Recommended next action
Independently validate, commit/merge this repair, then run `006D-loan-limit-snapshot-storage`.
