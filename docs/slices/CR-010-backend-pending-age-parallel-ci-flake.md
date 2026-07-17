# Slice CR-010: Pending-age clock makes parallel backend CI intermittently fail

## Status
Complete

## Origin
Change request (maintenance stage), accepted 2026-07-17 from docs/change-requests/accepted/CR-010-backend-pending-age-parallel-ci-flake.md.

## Risk Level
High

## Change Request (verbatim)

# Pending-age clock makes parallel backend CI intermittently fail

## Type
bug-backend

## Severity
High

## What Is Happening
The four-worker backend CI suite intermittently fails in `ApprovalCaseRoutingApiTests.test_live_appraisal_policy_change_preserves_pending_case_reads_and_action`. The test compares complete approval-case detail and queue payloads captured before and after a live policy edit. Those payloads contain the intentionally live `workbench_summary.pending_age.elapsed_seconds` field. When the requests cross a one-second clock boundary, the value advances (observed from 10 to 11) and the otherwise valid response comparison fails. Django then emits the secondary error `TypeError: cannot pickle 'traceback' object` while reporting the worker failure.

## Expected Behaviour
The regression test must verify that the approval case's stable routing, provenance, read scope, queue membership, and allowed action are unchanged by the live policy edit while treating pending age as a live, monotonically increasing value. Parallel CI failures must retain a readable original traceback rather than being replaced by traceback-pickling noise.

## Steps To Reproduce
1. Run the backend test suite with the configured parallel coverage workers.
2. Let `ApprovalCaseRoutingApiTests.test_live_appraisal_policy_change_preserves_pending_case_reads_and_action` execute under enough load for its before and after requests to cross a one-second boundary.
3. Observe that the complete payload equality at `test_approval_case_routing_api.py:931` fails only because `pending_age.elapsed_seconds` increased.
4. Observe the subsequent `TypeError: cannot pickle 'traceback' object` from Django's parallel test runner.

## Where It Appears
Approval-case detail endpoint `/api/v1/approval-cases/{case_id}/`, assigned approval-case queue endpoint `/api/v1/approval-cases/?assigned_to_me=true`, and the parallel backend CI test lane.

## Source Document Reference
unknown

## Acceptance Criteria
- A deterministic regression test exercises approval-case reads across an advancing clock and proves that the stable detail and queue fields remain unchanged.
- The test separately proves that pending-age labels remain valid and elapsed seconds are non-decreasing; it does not require a live elapsed-time value to remain byte-for-byte identical.
- The policy edit still preserves routing snapshot coherence, frozen provenance, frozen appraisal facts, queue membership, and the approval action.
- The focused approval-case routing tests pass.
- The configured four-worker backend coverage command passes without this timing flake.
- Parallel backend test failures preserve the actionable original failure instead of being obscured by traceback-pickling errors.

## Mandatory First Step: Impact Analysis
Before changing ANY code, write impact-analysis.md in the run folder covering:
- Affected backend models/endpoints/services, with grep evidence.
- Affected frontend screens/components/routes.
- Blast radius: every OTHER module that consumes the affected pieces.
- Existing tests covering the affected pieces, and the regression tests to add in EACH affected module.
- FRONTEND_DESIGN_RULES compliance note for any UI change.
Validation fails this run if impact-analysis.md is missing.

## Observed Follow-up Failure And Run Discipline
- The complete six-worker gate also reproduced the same defect in
  `ApprovalCaseRoutingApiTests.test_detail_is_unchanged_when_live_configuration_rows_change`:
  `pending_age.elapsed_seconds` advanced from 2 to 3 while the remaining detail payload stayed
  unchanged. Correct this known assertion as part of the same deterministic public-API regression
  treatment; do not hide changes to any stable field.
- Coding-agent feedback for the focused approval-routing class must run serially (omit `--parallel`
  or use `--parallel 1`). A coding-agent `--parallel 4` probe under the Rosetta-hosted sandbox caused
  spawned x86_64 workers to import the arm64 `_cffi_backend`, crash before test execution, and leave
  Django's parent pool waiting for dead workers. Do not repeat that non-authoritative probe.
- The orchestrator-owned `scripts/ralph-parallel-backend-coverage.sh` gate remains the only
  authoritative parallel proof. It must still run the complete configured suite and coverage floor
  before the slice can merge.

## Acceptance Criteria
- The change request's own acceptance criteria are met.
- Both known live-configuration before/after regressions isolate only `pending_age`, compare all
  stable detail/queue fields exactly, and assert the live age separately and monotonically.
- Regression tests added for every module named in the impact analysis.
- All quality gates pass.

## Done Checklist
- [x] Impact analysis and execution plan written before code changes
- [x] Deterministic pending-age RED/GREEN evidence saved
- [x] Both known approval-case regressions isolate only the live age
- [x] Parallel traceback dependency and pickle round-trip regression added
- [x] Focused serial tests, Django check, dependency check, and migration sync pass
- [x] Risk assessment, review packet, handoff, state, progress, and evidence updated
- [x] Complete parallel coverage delegated to the orchestrator
