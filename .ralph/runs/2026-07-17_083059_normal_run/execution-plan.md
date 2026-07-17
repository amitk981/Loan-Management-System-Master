# Execution Plan

Selected slice: `008M7-current-correction-tail-closure`

## Contract

Keep the existing immutable signed-copy succession behavior: an ordinary later upload creates a
successor with no inherited correction identity. Tighten the legal-document owner decision so a
correction is resolved only when its exact resolving signed copy is the unique, fully reconciled
current tail for the current renderer. Historical rows remain immutable and reviewable.

## TDD Sequence

1. Add the failing architecture-probe regression through the staff workspace interface: initial
   copy -> correction -> linked corrected copy -> ordinary unlinked successor. Assert that the
   successor retains no resolution id and that workspace/current-owner truth reopens the blocker.
2. Extend that public-path regression to prove downstream consistency and zero writes: checklist
   completion, ordered approval, and disbursement readiness must all fail after the unlinked tail.
3. Implement the smallest owner-local fix in
   `legal_documents.modules.documentation_actions`: the exact resolving copy must equal the unique
   current chain tail, while retaining every existing file/checksum/uploader/action/audit/workflow/
   version/current-renderer reconciliation check.
4. Run the focused legal/checklist/approval/readiness tests, Django check, migration sync, and the
   impacted frontend gates. Save failing-first and green evidence under `evidence/terminal-logs/`.
5. Save a sanitized tail/resolution manifest, changed-file and risk/review artifacts; update the
   Epic 008 digest, API contract note only if the external contract changes, slice status, progress,
   state, and handoff. Sharpen the next one or two Not Started slices only if they are still stubs.

## Scope / Risk Controls

- No schema, endpoint, permission, download, renderer, or frontend composition changes are planned.
- No historical correction or signed-copy row will be rewritten or deleted.
- The change stays behind the existing deep legal-owner interface already consumed by all named
  downstream modules.
- Diff limits: target two production/test files plus Ralph evidence and required state/docs.
