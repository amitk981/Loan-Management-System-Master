# Review Packet: 2026-07-10_092630_architecture_review

## Result
Success

## Slice
architecture-review

## Review Window

Pinned comparison: `git diff 1e2d873...HEAD`

Reviewed product commits:
- `e016d2a` - `005I2-application-detail-api-state-hardening`
- `c181819` - `006B-default-document-purpose-and-terms-eligibility-checks`
- `3f066cf` - `006C-loan-limit-configuration-and-calculator`
- `9f9ae0b` - `006D-loan-limit-snapshot-storage`

Config-only commit `c578e87` was inspected but excluded from product findings.

## Standards

- Hard: eligibility, loan-limit calculation, configuration resolution, persistence, serialization,
  and audit projection were added to the 2,789-line generic application service instead of the
  source-named deep credit/configuration modules.
- Hard: Application Detail still owns workflow/readiness decisions in React.
- Hard: the 005I2 render test bypasses the production HTTP seam with a production `initialData`
  prop; pure loan-limit behavior has no deep-module test seam.
- Judgment: response and audit loan-limit snapshot projection is duplicated.
- Watch/disposition: the standards pass also flagged same-UUID explicit rerun replacement. The
  primary-source review retained it as a watch because the source model is one-to-one, 006D
  explicitly requires audited rerun replacement, and passive policy/source mutations leave GET
  unchanged.

Full independent report: `evidence/standards-review.md`.

## Spec

- High: source §19.2 application `nominee_id` is absent from the public staff/portal contract; 006B
  selects the first reverse-linked ORM row, so the normal eligible path is not API-reachable.
- High: BR-020 can calculate from total selected owned acreage while lower crop/profile cultivated
  acreage is ignored; the equal-area fixture misses this material edge.
- Medium: 005I2 still synthesizes later-stage owner, stepper, documentation/disbursement, and
  payment-readiness facts.
- No material scope creep found.

Full independent report: `evidence/spec-review.md`.

## Corrective Slices

- `005I3-application-nominee-selection-contract`: source §19.2 selection, staff/portal wiring,
  deterministic 006B nominee authority, and adult/same-member evidence gates.
- `005I4-application-detail-backend-state-hardening`: backend-owned detail/action state and tests
  through mocked HTTP.
- `006C2-cultivated-acreage-source-hardening`: verified acreage reconciliation blocker under A-049
  without inventing a formula.
- `006D2-credit-assessment-deep-module-boundary`: source-named credit/configuration seams, focused
  module tests, safe model ownership, and one snapshot projection.

`006E` now depends on all four and must implement appraisal through the deep credit module seam.
No ADR was required in this run: the desired seam is already a source architecture decision; 006D2
must create an ADR only if model ownership needs a staged migration.

## Test Quality And Traceability

- Pass: 006B asserts every named blocker, pending evidence, rerun identity, no stage advancement,
  and no-success-evidence denials.
- Pass: 006C/006D assert both lower-of-two branches, below/equal/above limits, missing/ambiguous
  policy, source/object access, immutable GET, old/new audit, and failed-rerun preservation.
- Gaps: no public nominee-selection path, no cultivated-vs-owned acreage mismatch, no later-stage
  API-owner UI conflict, and no pure calculator module seam.
- No parent epic transitioned to Complete. M03-FR-003 remains owned by 005I3; Epic 006 remains in
  progress with M04-FR-004-007 implemented/under correction and M04-FR-001-003/008-011 queued in
  006E-006G.

Supporting evidence: `evidence/source-fidelity-and-test-quality.md` and
`evidence/review-window.md`.

## Validation

- Backend check: `evidence/terminal-logs/backend-check.log`
- Backend migration sync: `evidence/terminal-logs/backend-makemigrations-check.log`
- Backend tests under coverage: `evidence/terminal-logs/backend-tests-coverage.log`
- Backend coverage: `evidence/terminal-logs/backend-coverage-report.log`
- Frontend lint/typecheck/tests/build: corresponding logs in `evidence/terminal-logs/`

Validation summary:
- Backend: 290 tests passed; coverage 95% (floor 85%); check/migration sync passed.
- Frontend: lint/typecheck passed; 98 tests passed; build passed.
- Integrity: state JSON, whitespace, protected paths, production-code boundary, and diff limits
  passed. The optional coverage C tracer was incompatible with the process architecture, so
  coverage used its supported pure-Python tracer and completed successfully.

## Recommended Next Action
Run `005I3-application-nominee-selection-contract`, then 005I4, 006C2, and 006D2 before 006E.
