# Execution Plan

Selected slice: `006Y14-witness-parent-nondisclosure-and-matrix-closure`

1. Establish the current witness correction HTTP, authority, evidence, mounted, and browser contracts from the selected slice, Epic 004 digest, architecture-review finding, and existing public tests.
2. RED: add a focused parent-application non-disclosure regression proving that existing and missing out-of-scope parent IDs return the identical `403 OBJECT_ACCESS_DENIED` envelope before child lookup, while an owned missing parent remains `404`, with no witness/history/audit/workflow evidence.
3. GREEN: deepen the public application-authority seam so callers can authorize an application identifier without exposing parent existence, use it before witness lookup, and remove the internal mock-call-count compatibility test in favor of HTTP behavior.
4. RED/GREEN incrementally: add independently selectable contact and identity authority-matrix rows covering missing permission, parent scope denial, child non-disclosure, original-verifier maker-checker, stale version, malformed/non-object JSON, unknown/immutable fields, and success. Every applicable row will assert the exact six-field projected action, one public PATCH, stable error category/reason, and unchanged witness/history/audit/workflow evidence for failures.
5. Preserve and run the existing mounted one-PATCH failure / PATCH-plus-canonical-GET success tests and collect the declared Playwright spec. Do not change UI composition or styling; trusted screenshots remain for the orchestrator's two external browser runs.
6. Run dependency scans and focused red/green checks, then all configured frontend/backend gates with the mandated backend interpreter. Save terminal logs and evidence, assess diff/risk, and prepare the review packet and changed-files list.
7. Sharpen the next one or two eligible Not Started slices only from source/digest material already opened, update the Epic 004 digest if this run establishes durable facts, then mark 006Y14 complete and update Ralph state, progress, handoff, and final summary.

Permissions: planned edits are limited to allowed `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`, `.ralph/state.json`, `.ralph/progress.md`, and `.ralph/runs/**`. No protected or source path will be modified.
