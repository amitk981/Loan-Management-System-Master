# Ralph Handoff

## Last Run
2026-07-10_092630_architecture_review

## Current Status
Completed the architecture review of the four product slices after commit `1e2d873`:
- `005I2-application-detail-api-state-hardening`
- `006B-default-document-purpose-and-terms-eligibility-checks`
- `006C-loan-limit-configuration-and-calculator`
- `006D-loan-limit-snapshot-storage`

Review outcome:
- High: source §19.2 application nominee selection is absent from the public staff/portal contract,
  so 006B's eligible path currently requires direct ORM fixture writes and chooses the first
  reverse-linked nominee. Created `005I3-application-nominee-selection-contract`.
- High: 006C can use all selected owned acreage even when crop/profile cultivation evidence is
  lower. Created `006C2-cultivated-acreage-source-hardening` and A-049; disagreement must block
  until the source defines a precedence/formula.
- Medium: Application Detail still synthesizes later-stage dates, ownership, readiness, and action
  state and tests through a production data-injection prop. Created
  `005I4-application-detail-backend-state-hardening`.
- Medium: eligibility and loan-limit behavior deepened the generic application service instead of
  the source-named credit/configuration modules. Created
  `006D2-credit-assessment-deep-module-boundary`.
- Pass: 006B-006D tests have substantive formula, boundary, access, audit, immutable-read, and
  failed-rerun preservation assertions.
- Watch: explicit successful reruns replace the current one-to-one loan-limit snapshot with full
  old/new audit. This matches the reviewed slice/data shape; appraisal must consume stored facts and
  must never recalculate as a read/review side effect.

No production code or `docs/source/` file changed. Findings were prepended to
`docs/working/REVIEW_FINDINGS.md`; Epic 005/006 digests carry the distilled review facts.

## Validation
- Backend `manage.py check` passed.
- Backend full suite passed: 290 tests.
- Backend `makemigrations --check --dry-run` passed.
- Backend coverage passed: 95%, above the 85% floor.
- Frontend lint and typecheck passed.
- Frontend tests passed: 98 tests.
- Frontend build passed.
- Final integrity/protected-path/diff-limit checks passed.

Evidence is in `.ralph/runs/2026-07-10_092630_architecture_review/`.

## Next Run
Run `005I3-application-nominee-selection-contract`.

Key instructions for 005I3:
- Add source §19.2 `nominee_id` to staff and portal draft create/update and store one same-member
  nominee on `LoanApplication` through a non-destructive migration.
- Require a selected adult nominee before submit/completeness/normal eligibility; missing legacy
  selection stays pending, and cross-member/minor/missing-age paths create no success evidence.
- Make 006B read only the stored application nominee; remove reverse-query `.first()` selection.
- Wire existing staff/member portal application forms and safe detail summaries using current
  visual patterns; never expose nominee PAN/Aadhaar values.

Then run `005I4`, `006C2`, and `006D2` in order. `006E-appraisal-note-create-edit-submit` now
depends on all four corrective slices and must use the deep credit appraisal module seam.
