# Review Packet: 2026-07-19_014802_architecture_review

## Result

Success

## Slice

architecture-review

## Fixed Review Range

The prior reviewed product boundary is `e3d965ad`. The review inspected the product changes in:

- `35dd95ce` — 009H9A queued-advice migration provenance closure
- `4bdff96c` — 009H9B final-attempt and exception-queue closure
- `9b1113af` — 009H9C channel/interface/provider-evidence closure
- `4bebe1af` — 009I2 portal disbursement stage and visual closure

Owner-maintenance commit `4fb0a5af` falls in the chronological range but has no product diff and
was not attributed to these four slices.

## Outcome

Exact-cap recovery, Email/SMS isolation, immutable generic provider evidence, explicit MP14
selection, owner timestamps, and the real-browser contract are substantively implemented. Two
High defects remain: incomplete required queued-template facts can be promoted to verified, and
exception routes allow the wrong job-kind permission to read and resolve assigned exceptions.
Corrective slice `009H9D` is queued before 009J. No production code changed in this review.

## Standards

- **High:** `communications/services.py` grants exception management for the union of generic and
  advice send permissions, while the views/dispatcher do not enforce the exact permission for the
  retained `job_type`. This violates backend-enforced permission rules and the working API contract.
- **Medium:** the exception collection hard-codes page 1/100 and makes later rows unreachable,
  contrary to standard bounded pagination.
- **Medium:** process code selects channel adapters and Celery calls private dispatcher methods,
  although the communications module is required to hide channel/adapter selection. A related
  static test asserts implementation strings instead of the observable module interface.

Standards count: 1 High, 2 Medium. Worst: High exception authorization.

## Spec

- **High:** 009H9A requirement 2 says incomplete frozen snapshots remain legacy-partial, but
  migration 0008 accepts blank required facts when their checksum is recomputed.
- **Medium:** H9B's `provider_code` stores a dotted adapter implementation path rather than the
  source `email`/`sms` provider vocabulary.
- **Medium:** I2's behavior uses the selected id, but its required two-finance-application,
  opposite-order regression is absent.
- **Medium:** H9C lacks the required cross-channel idempotency reuse assertion; implementation
  appears to conflict safely, but the binding edge case is not frozen by a test.
- No material scope creep was found.

Spec count: 1 High, 3 Medium. Worst: High incomplete provenance classification.

## Test and Architecture Quality

- Retained focused backend suites: 74 pass; six PostgreSQL-only races skip locally. The H9B/H9C
  runs retain their independent twice-run PostgreSQL evidence.
- Focused MP14/frontend suites: 10 pass across two files.
- Review-only probes: three intentional failures prove incomplete provenance and cross-kind read/
  resolution authorization. These are defect evidence, not failures of review-authored product code.
- Related communications symptoms are grouped in one root-owner correction rather than leaf slices.

## Source and Repository Fidelity

- Source checks covered codebase-design §§20, 22, 26, 34-36, 40, 42; integrations §§6-7, 10-11,
  19, 21-22, 29, 33; API §§3, 6-8, 31, 39, 45; M08/M16; and MP14 permissions/fields/rules.
- No epic completed in this range, so there is no newly completed epic M##-FR matrix to close.
- `docs/working/CONTEXT.md` remains truthful. `.ralph/state.json` and the slice files contain no
  blocked slice requiring re-parking. No ADR is needed because existing source contracts decide
  the corrections.

## Convergence Metrics

- Findings closed: 5
- New Critical: 0
- New High: 2
- New Medium: 3
- New Low: 0
- Corrective slices added: 1

## Corrective Work

- Added `009H9D-communications-provenance-and-operator-boundary-closure` as High risk with status
  `Not Started`, depending on completed `009H9C`.
- Added `009H9D` to 009J's prerequisites so the significant defects cannot be bypassed by normal
  queue selection.
- MP14's opposite-order test gap remains recorded for Epic 009 closure; it does not justify a
  separate immediate corrective slice because the selected-id behavior is correct.

## Recommended Next Action

Run `009H9D` before 009J, copying the three review probes as TDD red evidence and preserving the
existing PostgreSQL race, provider replay, and portal behavior.
