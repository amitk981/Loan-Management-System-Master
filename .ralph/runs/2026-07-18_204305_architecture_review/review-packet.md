# Review Packet: 2026-07-18_204305_architecture_review

## Result

Success

## Slice

architecture-review

## Fixed Review Range

`git diff fb380227...e3d965ad`

- `056c6cfc` — 009G6 legal migration exception fingerprint closure
- `5ec24d77` — 009H6 legacy advice template provenance closure
- `7c577686` — 009H7 communications dispatcher/interface/idempotency closure
- `c3c9cc0a` — 009H8 communications worker runtime/crash recovery closure
- `6f447a49`, `e3d965ad` — CR-011 migration-test schema isolation intake and completion

## Outcome

The legal complete-state migration fingerprint and CR-011 current-leaf cleanup appear complete.
The communications work has three release-blocking defects: a valid queued H5 job can abort the
0007-to-current migration, a final-attempt crash is requeued beyond its cap, and SMS is delivered
through the Email adapter. No material scope creep was found and no production code changed.

## Standards Review

- High: generic SMS, phone, and courier enter one Email-only worker seam with no channel-specific
  validation. Corrective slice: `009H9C`.
- High: stale recovery ignores `max_attempts`, and exhaustion lacks the source §22.3 exception
  queue/resolution owner. Corrective slice: `009H9B`.
- Medium: the public dispatcher facade is wider than source §40.1, API §45.2 replay and immutable
  generic provider evidence are partial, and API_CONTRACTS contains contradictory old text.
  Corrective slice: `009H9C`.
- Low: periodic Celery tasks still own due-job iteration and result-shaping policy. Corrective
  slice: `009H9C`.

Worst severity: High. Count: 2 High, 1 Medium, 1 Low.

## Spec Review

- Critical: migration 0008 treats a complete queued H5 job as ambiguous because it has no provider
  attempt, after which migration 0009 aborts. Corrective slice: `009H9A`.
- High: H8 does not make final-attempt crash recovery terminal. Corrective slice: `009H9B`.
- High: H7 promises Email/SMS behavior but implements and tests Email only. Corrective slice:
  `009H9C`.
- Medium: H7's exact source interface and API §45 replay promises are asserted only partially.
  Corrective slice: `009H9C`.

Worst severity: Critical. Count: 1 Critical, 2 High, 1 Medium.

## Verification Evidence

- Retained focused backend set: 43 tests, all passing in 50.004 seconds.
- Review contract probes: 3 tests exercise the new paths; the intended assertions fail. The
  migration defect also raises during cleanup, so Django reports 2 failures and 2 errors for the
  three probes.
- Logs: `evidence/terminal-logs/retained-focused-tests.log` and
  `evidence/terminal-logs/review-contract-probes.log`.
- Reproduction source: `evidence/review-probes/review_contract_probes.py`.
- No complete backend suite, frontend gate, or browser run was repeated because the review has no
  production/frontend change; authoritative complete coverage remains an orchestrator gate.

## Documentation and Queue Changes

- Appended the full newest-first review to `docs/working/REVIEW_FINDINGS.md`.
- Created dependency-ordered corrective slices `009H9A`, `009H9B`, and `009H9C` before `009I2`.
- Updated the Epic 009 digest, CONTEXT, architecture-review descriptor, state, progress, and handoff.
- Rechecked the queue: `.ralph/state.json` has no blocked slices and no slice declares `Blocked`.
- No ADR was created because existing source documents already determine the required behavior.

## Recommended Next Action

Run `009H9A-queued-advice-migration-provenance-closure`, then `009H9B` and `009H9C`. Only after
those corrections should the queue proceed to `009I2`, then `009J` and `009K`.
