# Review Packet: 2026-07-18_004444_normal_run

## Result
Ready for independent validation

## Slice
`CR-010-backend-pending-age-parallel-ci-flake`

## Change review

- Both known flaky approval tests use fixed advancing clocks through the public detail and assigned
  queue endpoints.
- Each response is deep-copied; only `workbench_summary.pending_age` is removed. Every other field,
  queue row, and pagination value is compared exactly.
- Pending ages independently require the canonical label, integer non-negative elapsed seconds,
  non-empty display text, and a non-decreasing after value.
- Existing assertions still prove queue membership, approval action success, routing coherence,
  frozen loan-limit provenance, frozen appraisal facts, and required-approver projection stability.
- `tblib==3.1.0` is pinned only in development requirements. The infrastructure test captures an
  assertion failure in Django `RemoteTestResult`, pickle-round-trips its event, and proves the
  original exception text and traceback survive.
- No production or frontend code changed. API contracts and visual acceptance are unchanged.

## TDD evidence

- `pending-age-red.log`: both old whole-payload assertions fail deterministically only at 10→11 and
  2→3 elapsed seconds.
- `pending-age-green.log`: both corrected regressions pass.
- `parallel-traceback-red.log`: the clean-install contract fails because `tblib` is unpinned.
- `parallel-traceback-green.log`: the dependency and traceback round-trip contract passes.

## Verification

- Approval routing class: 127 tests pass serially.
- Backend infrastructure class: 7 tests pass serially.
- Django system check: clean.
- Migration sync: no changes detected.
- Dependency check: no broken requirements.
- No coding-agent parallel probe or full backend suite was run; the orchestrator owns the complete
  configured parallel coverage and floor.

## Traceability

The CR says stable approval-case detail/queue facts must survive live configuration changes while
pending age remains live and non-decreasing. The two named public-API tests now prove exactly that
under forced advancing clocks. The CR also requires readable worker failures; the development pin
and infrastructure regression prove Django can transport the original traceback.

## Queue review

009H3 and 009G4 were rechecked. Both already contain concrete owner boundaries, fields, migration
behavior, validation rules, tests, and runtime capabilities, so no speculative sharpening was made.

## Recommended next action

Run independent Ralph validation and commit only if the complete parallel coverage gate passes.
