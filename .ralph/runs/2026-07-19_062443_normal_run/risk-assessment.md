# Risk Assessment

Risk level: High

- Selected slice: `009L-epic-009-staff-workflow-and-sap-posting-closure`
- Mode: `normal_run`
- Manual review required: yes; the slice changes finance authority projection, successful-transfer atomicity, and durable SAP-posting evidence.

## Material risks and controls

- **Financial/data-integrity:** transfer success now creates one initial-payment SAP posting obligation in the same transaction as the bank-transfer and loan-register evidence. Database singular relations and replay/coherence tests prevent duplicate or cross-object posting rows.
- **Authorization:** S36/S37 actions are emitted only by the SAP owner facade after effective role, permission, assignment, and current-state checks. The retained workspace probes cover the former internal-permission 500 and incoherent-disbursement projection.
- **External-system truth:** no source-backed posting actor or SAP adapter exists. Posting remains honestly `pending`; no confirmation endpoint or invented external acceptance was added. This is recorded as assumption A-135.
- **Privacy:** workspace choices and rows use safe identifiers and masked SAP values; PAN, Aadhaar, bank details, workbook locations, and internal evidence ids are not projected.
- **Frontend truth:** Loan Account 360 no longer combines a real account identity with mock repayment, interest, default, or closure history. Those Epic 010 views are explicitly unavailable.
- **Time correctness:** `datetime-local` values are converted to aware ISO-8601 instants at the HTTP transport boundary and exact request bytes are covered by Vitest.

## Residual validation risk

- The local Chromium worker stalled after startup and produced no screenshots. The spec collects and declares all eight exact outputs, but Ralph's trusted external browser run must establish the real screenshot result twice.
- The two five-way transfer race cases are PostgreSQL-only and were skipped by the local SQLite-focused run; they remain part of independent validation.
- The build retains the pre-existing Vite large-chunk warning; this slice adds no package or styling system.
