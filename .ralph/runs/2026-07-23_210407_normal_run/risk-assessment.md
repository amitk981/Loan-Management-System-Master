# Risk Assessment

Risk level: Medium

Selected slice: `011O-auditor-read-only-views`

## Risk Drivers

- Adds a cross-module auditor projection spanning default/recovery, closure/archive, compliance/KYC,
  statutory calculations, evidence metadata, and grievances.
- Tightens the Internal Auditor contract on existing GET and mutation endpoints.
- Changes the seeded Internal Auditor permission catalogue by removing evidence-review authority.
- Adds a role-specific frontend route and a new authenticated aggregate API.
- The aggregate is intentionally bounded to 100 records per contributing collection; broad exports
  and Audit Explorer remain Epic 012 work.

## Controls Applied

- Active `audit_readonly` scope is required in addition to the Internal Auditor role and existing
  read permissions.
- Auditor projections recursively omit `available_actions`; the aggregate contains only safe
  summaries, immutable audit/workflow IDs, and classified evidence metadata.
- Evidence content remains behind the existing document-download endpoint and its permission,
  object-scope, reason, audit, and signed-delivery controls.
- The Internal Auditor catalogue contains no operational create/manage/update/review/resolve/close/
  issue/return/archive authority, including no compliance evidence review permission.
- A 31-request HTTP method matrix proves representative Epic 011 mutations return 403 without
  creating default, closure, control, or grievance records.
- Focused RED/GREEN evidence covers the empty aggregate, missing scope, populated lifecycle families,
  mutation denial, and all four frontend states.
- The impacted backend lane passed 118 tests; all 424 frontend unit tests, typecheck, lint, build,
  Django checks, migration drift check, and whitespace validation passed.

## Residual Risk

- The cross-module aggregate deliberately uses bounded snapshots rather than export-grade pagination;
  exports and broad audit exploration are excluded by the slice.
- Immutable references are resolved from existing audit/workflow entity IDs. Historical rows that
  predate those ledgers correctly show an empty reference list rather than synthesized history.
- The exact Playwright acceptance spec was executed, but the installed Chrome process aborted with
  `SIGABRT` before creating a page. No screenshot was fabricated. Trusted validation must rerun the
  exact spec in a browser-capable environment and produce the three declared PNG files.
- The slice cites nonexistent `test-plan.md` §§37.2-37.5. Implementation used the applicable cited
  test-plan sections and the slice's explicit acceptance matrix without inferring a new business rule.

Manual review required: independent Ralph validation should run the authoritative backend lane and
trusted browser acceptance. No product-code blocker was identified.
