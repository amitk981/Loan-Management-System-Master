# Review Packet: 2026-07-22_122436_normal_run

## Result
Ready for independent validation

## Slice
011C-extension-note-workflow

## Implementation summary

- Added the `ExtensionNote` model/migration, one-note uniqueness, bounded states, immutable effective dates, exact loan-file document linkage, Credit Manager permission seed, and the current note pointer on `DefaultCase`.
- Added `DefaultWorkflow.grant_extension` and `POST /api/v1/default-cases/{id}/grant-extension/` with backend-owned eligibility, exact inclusive one-year dates, authority/object scope, replay convergence, audit/workflow evidence, and standard error envelopes.
- Added default-case read/action projection plus retry-safe extension cure/expiry reconciliation. Unpaid expiry queues review only; it does not create a Non-Payment Note.
- Documented the public contract and the source-silent conditional approval gap in A-156. No checker or sanction route was inferred.

## Traceability

- The source says a non-intentional unpaid case may receive one one-year extension and must retain an Extension Note (`docs/source/product-requirements.md` §11.26, `DEFAULT-AC-003-004`; `component-spec.md` §17.4). The code enforces those facts in `DefaultWorkflow.grant_extension`, verified by `test_eligible_case_grants_one_audited_extension_with_exact_loan_file_note` and the negative eligibility/document matrix.
- The source says the start follows grace, the end covers one year, approval is conditional, and status/evidence remain visible (`screen-spec.md` S54; `data-model.md` §21.3). The code derives 2026-07-01 through 2027-06-30 from the retained grace end, rejects caller deviations, retains preparer/optional approver/status/document IDs, and blocks effective-date mutation; verified by the date, projection, and immutability tests.
- The source says Credit Manager grants while Credit Assessment and Auditor remain read-only (`auth-permissions.md` §§12.10, 20.3, 25.8, 26.7). The code requires both permission and role plus existing case scope; verified by the unauthorized mutation test and unchanged object-permission regressions.
- The slice says exact replay/concurrency must converge and expiry must be retry-safe without automatic Non-Payment Note creation. PostgreSQL tests `test_five_concurrent_exact_grants_converge_on_one_note_and_transition` and `test_five_concurrent_expiry_runs_create_one_review_transition` pass with the exact expected class count of two.

## Evidence

- TDD tracer: `evidence/terminal-logs/extension-tracer-red.log` → `extension-tracer-green.log`
- Read projection: `evidence/terminal-logs/extension-detail-red.log` → `extension-detail-green.log`
- Expiry/retry: `evidence/terminal-logs/extension-expiry-red.log` → `extension-expiry-green.log`
- PostgreSQL defect/proof: `evidence/terminal-logs/extension-postgresql-red.log` → `extension-postgresql-green.log`
- Focused 011A/B/C regression: `evidence/terminal-logs/focused-backend-green.log` (24 tests)
- Document/permission reverse consumers: `evidence/terminal-logs/reverse-consumers-green.log` (23 tests)
- Django/schema/static checks: `evidence/terminal-logs/backend-checks-green.log`, `static-review-green.log`

## Tested response/document metadata

The success contract returns `extension_note_id`, `default_case_id`, `loan_account_id`, reason,
ISO start/end dates, the exact governed `LoanDocument` ID, preparer ID, nullable approver ID, and
`status=active`. Default-case detail returns the same retained object. Tests use confidential PDF
metadata with `document_type=extension_note`, `document_category=recovery`,
`generation_status=generated`, and reject missing, assessment-type, or foreign-loan documents.

## Review focus

- Confirm A-156 is the intended fail-safe treatment of source-conditional approval until a governed extension checker configuration exists.
- Independently rerun the exact PostgreSQL class twice as required by the slice capability.
- Confirm the independently mapped backend lane includes defaults route/model/migration tests and document/object-permission reverse consumers.

## Recommended Next Action
Run Ralph's independent protected-path, migration, impacted/full backend, and trusted PostgreSQL validation; commit only if all gates pass.
