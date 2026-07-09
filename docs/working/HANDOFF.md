# Ralph Handoff

## Last Run
2026-07-09_205626_normal_run

## Current Status
Slice `005F-deficiency-creation-and-resolution` completed successfully.

The deficiency backend now includes:
- `POST /api/v1/loan-applications/{loan_application_id}/return-with-deficiencies/`
- `GET /api/v1/loan-applications/{loan_application_id}/deficiencies/`
- `POST /api/v1/deficiencies/{deficiency_id}/resolve/`

Implemented behavior:
- Return-with-deficiencies is limited to submitted applications that do not yet have an `LO...`
  reference or loan request register row.
- Request `items[].item_code` must match current 005E blocking completeness checklist facts.
  `missing_metadata` maps to `deficiency_type = missing_document`; `not_verified` maps to
  `deficiency_type = not_verified`.
- Successful return sets `completeness_status = incomplete`, keeps `application_status =
  submitted`, creates open deficiency rows with raised actor/time and communication metadata,
  writes metadata-only audit/workflow evidence, and creates no reference, register row, sequence
  advancement, or credit-assessment transition.
- Deficiency list returns metadata-only rows for the application.
- Resolve accepts source §21.2 `resolution_notes`, closes only open rows, stamps resolver/time, and
  writes metadata-only audit/workflow evidence.

Permission and access order:
- Return and resolve require `applications.loan_application.complete_check`.
- List requires `applications.loan_application.read`.
- Unknown applications/deficiencies return `404 NOT_FOUND`.
- Missing global permission returns `403 PERMISSION_DENIED`.
- Application scope uses `applications.services.evaluate_application_object_access(...)`; same
  permission actors outside scope receive `403 OBJECT_ACCESS_DENIED` with no deficiency, audit,
  workflow, register, reference, or sequence side effects.

Sensitive-data boundary:
- Deficiency responses and audit evidence omit raw file bytes, storage keys, checksums, PAN,
  Aadhaar, full bank values, encrypted tokens, and hashes.

## Documentation Updates
- `docs/working/API_CONTRACTS.md` documents the 005F return/list/resolve endpoints, response
  shape, validation order, permission checks, and side-effect boundaries.
- `docs/working/ASSUMPTIONS.md` records A-040 for `items[].item_code` vs source §19.7
  `deficiency_ids`.
- `docs/working/digests/epic-005-application-intake.md` records the implemented 005F facts.
- `005FA` and `005FB` were sharpened with portal member-scope and deficiency-record facts.

## Next Run
Architecture review is due by cadence (`slices_completed_since_architecture_review = 4`). After the
review, run `005FA-member-portal-authentication`.

Key instruction for 005FA: borrower/member portal tokens must carry a linked `member_id` own-data
scope and must not grant staff completeness/pass/deficiency-resolution permissions.

## Evidence
See `.ralph/runs/2026-07-09_205626_normal_run/`.

Key artifacts: `execution-plan.md`, `api-response-examples.md`, `review-packet.md`,
`risk-assessment.md`, `changed-files.txt`, `final-summary.md`, and gate logs under
`evidence/terminal-logs/`.
