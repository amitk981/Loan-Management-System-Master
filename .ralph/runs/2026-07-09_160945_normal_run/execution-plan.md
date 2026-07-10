# Execution Plan

Selected slice: 004K-borrower-360-kyc-panel-and-masking-ui-wiring

## Scope
- Wire `Borrower360` to existing Epic 004 APIs through the frontend client: member detail, nominees, shareholdings, land holdings, crop plans, KYC profile/documents, bank accounts, and cancelled cheques.
- Keep loan, repayment, communication, security-instrument, and audit sections as source-backed empty/deferred states because no real APIs exist for those surfaces in this slice.
- Reuse existing `MemberProfile`/`Borrower360` card, tab, status, alert, field, loading, empty, error, and masked/reveal patterns. No visual redesign or new styling system.
- Do not add backend models, migrations, reveal permissions, bank-account reveal, duplicate-bank warnings, signature-mismatch workflow, payment initiation, or disbursement-readiness UI.

## Source Trace
- `screen-spec.md` S07 requires a consolidated borrower profile view across membership, KYC, documents, loans, risk, and audit. This run will show the implemented member-master facts and defer missing API-backed modules as empty states.
- `screen-spec.md` S17 requires borrower KYC, CKYC consent, re-KYC status, document verification status, and verify actions. Existing 004H endpoints provide profile/document metadata and verification.
- `api-contracts.md` §13.5 and `auth-permissions.md` sensitive-data rules require reason capture, explicit reveal endpoint use, no full-value caching, and masked display by default.
- Prior slice facts require 004J bank/cancelled-cheque metadata to stay masked with no reveal affordance.

## TDD Plan
1. Add failing frontend tests for `Borrower360` API client coverage: bank-account/cancelled-cheque fetches use 004J endpoints and preserve masked account-number objects.
2. Add failing view tests for `Borrower360View`: renders API-backed member/KYC/share/land/crop/bank metadata, masks PAN/Aadhaar and bank numbers, hides reveal for unauthorized fields, blocks blank reveal reason without an API call, and renders loading/empty/error states.
3. Implement minimal client methods and `Borrower360` state orchestration to pass those tests.
4. Refactor only within the page/client if needed, then run focused tests and full Ralph gates.

## Evidence Plan
- Save red and green vitest output in `evidence/terminal-logs/`.
- Save frontend lint/typecheck/test/build logs and backend check/test/migration/coverage logs.
- Save visual evidence for masked and reveal-capable borrower states.
- Finish with changed files, risk assessment, review packet, final summary, handoff/progress/state, slice status, and next-slice sharpening.
