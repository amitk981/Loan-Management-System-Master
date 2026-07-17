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
