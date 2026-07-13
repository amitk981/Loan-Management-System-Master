# Execution Plan

Selected slice: 007H3-frozen-case-provenance-and-read-scope-parity-closure

## Scope and interface

- Keep the public HTTP interfaces unchanged: approval-case collection/detail/actions, sanction
  decision, and Credit Sanction Register.
- Deepen the approvals-owned case validity/actor-scope seam so all four boundaries validate the
  immutable case snapshots and then apply the same actor decision. Live appraisal rows may be
  consulted only while enriching a new case, never while validating an existing frozen cycle.
- Preserve the explicit projection/index as database narrowing only; it is not authority and no
  model-save signal or cross-table save side effect will be introduced.

## TDD tracer bullets

1. Add one focused public regression proving a pending enriched case remains byte-for-byte
   readable and actionable after only the live appraisal policy name changes. Run it alone and
   retain the expected RED output.
2. Implement the smallest frozen-only provenance validation change and retain GREEN output.
3. Add focused public parity tests for terminal detail/decision/register reads, malformed frozen
   snapshots with stale true projection/index, and returned/new-cycle provenance separation; use
   one RED -> GREEN cycle at a time and retain logs.
4. Extend the existing actor matrix only where needed to prove original/effective/conflicted/acted
   and persisted legal/audit/management readers retain scope exclusively for frozen-valid cycles.

## Verification and documentation

- Run the focused approvals tests, then backend check, migration sync, and the full backend suite
  under coverage with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Run all configured frontend gates unchanged because Ralph validates the whole repository.
- Update `docs/working/API_CONTRACTS.md` and the Epic 007 digest with the frozen-versus-live
  ownership rule.
- Sharpen the next one or two Not Started slices using only already-opened Epic 007 material.
- Save terminal evidence, changed-files, risk assessment, review packet, final summary, progress,
  handoff, state, and mark only 007H3 Complete after all gates pass.

## Risk controls

- High risk: read-scope nondisclosure and approval authority can diverge if any endpoint retains a
  Boolean/index shortcut. Tests will assert counts/pagination and zero writes, not only status.
- No schema change is planned. Stop if the implementation requires protected-file edits, a source
  rule invention, or exceeds Ralph diff limits.
