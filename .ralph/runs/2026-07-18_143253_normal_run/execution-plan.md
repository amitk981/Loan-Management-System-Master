# Execution Plan — 009I Member Portal Disbursement Status

## Scope and interface

- Add one borrower-only, application-scoped `GET /api/v1/portal/applications/{id}/disbursement-status/` projection behind the existing active `PortalAccount` self-scope.
- Keep owner evidence behind existing module interfaces: current terminal sanction, legal readiness, SAP code, initiation/CFC evidence, post-transfer evidence, and communications finalization. The new process module will only coordinate their typed decisions and serialize borrower-safe fields.
- Add empty-body POST capability issuance and authenticated GET content routes for the exact current advice. Persist capability version/expiry/consumption on the communications-owned advice outbox so replacement and one-use enforcement are transactional. The downloadable artifact is the exact retained subject/body snapshot encoded as UTF-8 text; its SHA-256 checksum and outbox/communication identities are capability-bound but never returned in the status projection.
- Wire MP14 through the shared portal transport. Preserve its existing composition/classes and replace hard-coded values with loading, empty, blocked, processing, disbursed, advice-download, error, and expired-session states.

## TDD tracer bullets

1. RED then GREEN: own portal status returns a stable pre-loan/sanctioned projection with exact field allowlist, six ordered safe timeline rows, masking, nondisclosing scope, staff denial, zero writes, and rejected unknown query parameters.
2. RED then GREEN: current initiation/CFC/transfer evidence advances only to the last coherent stage; rejected or stale/mixed owner evidence becomes borrower-safe blocked truth without internal identifiers or actors.
3. RED then GREEN: exact communications finalization makes advice available; capability POST rejects non-empty bodies, replaces prior capability, and the content GET is one-use, expiring, tamper/cross-scope/checksum safe with accepted/denied portal download audits and attachment/nosniff headers.
4. RED then GREEN: MP14 loads the eligible own application and canonical projection, renders exact values/timeline/states, enables download only when authorised, handles 401/403/general errors safely, and contains no runtime fixture or `mockData` import.

## Verification and evidence

- Save each focused backend and frontend RED/GREEN command under `evidence/terminal-logs/`.
- Run impacted backend tests with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`, then Django check and migration sync; do not run the full backend suite.
- Run impacted Vitest tests, frontend typecheck, lint, and build.
- Save sanitized processing/disbursed/error envelopes and a fixture-removal proof. Browser screenshots are delegated to the orchestrator's trusted browser gate if Chromium cannot run in the sandbox; never fabricate them.
- Update `docs/working/API_CONTRACTS.md`, slice status, state, progress, handoff, review/risk/final artifacts, and sharpen/recheck the next one or two Not Started slices from already-opened source material.

## Risk controls

- High risk: financial state, portal object scope, sensitive bank reference, and protected borrower advice. Standing approval is active and there is no owner veto.
- No raw SAP code, account/IFSC, full bank reference, recipient, internal actor/comment/status, evidence ID, storage key, checksum, or capability token enters the projection, UI, or audit evidence.
- Status reads remain zero-write. Capability issuance/consumption and safe audit are the only writes, under transactions and exact current-evidence revalidation.
- One migration maximum; no dependency changes and no protected/source file edits.
