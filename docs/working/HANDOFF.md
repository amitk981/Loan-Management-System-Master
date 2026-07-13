# Ralph Handoff

## Last Run

2026-07-14_025903_normal_run

## Current Status

`007M-exception-supporting-evidence-and-register-closure` is complete. Exception enrichment accepts
an optional ordered list of up to 20 distinct document ids. The documents-owned boundary validates
public-upload provenance, exact application attribution, legal category, matching sensitivity,
document permission, source audience, workflow context, and canonical object scope. Approvals does
not import or query `DocumentFile`; it freezes only the returned immutable display metadata on the
exact Exception Register entry/cycle.

Omitted evidence remains an honest empty list. Exact ordered replay is zero-write, changed ids are
an immutable-snapshot conflict, and denied category/sensitivity/permission/role/application/object
rows write no association evidence. Initial association ids are attributable in the locked creation
audit, with the same actor/case/cycle represented by the workflow event.

S25 renders distinct description/business reason, every immutable approval actor/decision/comment/
time, and supporting file metadata in the existing register table composition. Register permission
and metadata create no download affordance or mutation authority. The typed frontend contract and
trusted browser spec cover both the evidence-rich and download-denied states.

## Validation

RED/GREEN evidence is retained in
`.ralph/runs/2026-07-14_025903_normal_run/evidence/terminal-logs/`. Django check and migration sync
pass; all 687 backend tests pass with 19 expected PostgreSQL-only skips and 93% coverage. Frontend
build/typecheck/lint and all 253 tests pass. The named Playwright spec collects successfully. A real
local launch reached Django/Vite but Chromium hit the expected macOS Mach-port sandbox denial; no
screenshots were fabricated, and the orchestrator owns the two trusted browser runs.

## Next Run

Run `007N-register-matrix-settings-contract-and-browser-closure`. It was inspected and is already
concretely sharpened with shared transport, server-projected matrix facts, navigation parity,
Settings fidelity, exact browser scenarios, and six screenshot contracts. Do not close Epic 007
browser/fidelity evidence until 007N completes.
