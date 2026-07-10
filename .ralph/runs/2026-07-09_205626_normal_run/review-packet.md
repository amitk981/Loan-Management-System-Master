# Review Packet: 2026-07-09_205626_normal_run

## Result

Success.

## Slice

`005F-deficiency-creation-and-resolution`

## What Changed

- Added `ApplicationDeficiency` model and migration `0005_application_deficiency.py`.
- Added staff return/list/resolve deficiency endpoints.
- Added service logic to derive valid deficiency items from the existing 005E completeness
  workbench and persist open/resolved metadata-only deficiency records.
- Updated API contracts, assumptions, Epic 005 digest, and sharpened `005FA`/`005FB`.

## Traceability

- Source says incomplete applications can be returned with deficiencies
  (`implementation-roadmap.md` §11.7 R2-AC-004; `screen-spec.md` §9.1). Code does this via
  `return_application_with_deficiencies(...)`; verified by
  `test_return_with_deficiencies_creates_open_records_from_blocking_checklist_items`.
- Source defines `deficiencies` with type, description, raised/resolved actor stamps and resolution
  status (`data-model.md` §13.5). Code stores those fields in `ApplicationDeficiency`; verified by
  return and resolve tests.
- Source names return/list/resolve APIs (`api-contracts.md` §19.7 and §21.1-§21.2). Code exposes
  the three endpoints; verified by API tests.
- Source requires appraisal to wait for complete applications or resolved deficiencies
  (`data-model.md` §28.2). Code does not advance returned applications to credit assessment or
  generate references/register rows; verified by side-effect assertions.
- Source requires critical actions to be audit/workflow logged (`implementation-roadmap.md`
  R2-AC-010; `data-model.md` §33.1/§34.1). Code writes return and resolve audit/workflow evidence;
  verified by tests.

## Verification

- TDD red: `tdd-red-return-with-deficiencies.log`.
- TDD green: `tdd-green-return-with-deficiencies.log`.
- Focused deficiency tests: `deficiency-targeted-tests.log`, 3/3 passed.
- Backend: `manage.py check`, full tests 256/256, migrations check, coverage 95%.
- Frontend: lint, typecheck, tests 80/80, build.
- `git diff --check` passed.

## Not Included

- Borrower portal deficiency response/re-upload/resubmission.
- Rejection note generation.
- Eligibility, appraisal, sanction, disbursement, or real communication delivery.
