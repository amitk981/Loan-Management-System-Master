# Execution Plan

Selected slice: `007G-general-meeting-evidence-for-special-cases`

## Scope and existing seam

- Extend the approvals module's public HTTP interface with the source §25.11 application-scoped
  general-meeting evidence endpoint. Keep validation, immutable history, audit/workflow evidence,
  and serialization behind one approvals-owned module interface.
- Extend the existing `approval_actions` transaction only at the point where canonical conflict,
  assignment, distinct effective authority, and final-action completion have already been proved.
  Do not change conflict replacement, Exception Register identity/projection, or frontend code.
- Use the existing document metadata module as the document-existence and access seam; referenced
  metadata must exist and the recorder must hold the existing document-download authority.

## TDD tracer sequence

1. RED then GREEN: POST an approved Director-relative meeting record through §25.11, proving all
   three accessible document references, immutable record identity, and audit/workflow evidence.
2. RED then GREEN: prove exact replay is zero-write and a changed payload creates an explicit
   superseding row without overwriting history; validate bounded party/status vocabulary and
   required fields.
3. RED then GREEN: prove missing documents, inaccessible documents, missing Critical permission,
   and unrelated/out-of-scope applications fail with standard envelopes and zero business writes.
4. RED then GREEN: prove the final sanction action for a frozen related-party cycle is blocked by
   missing, pending, or rejected current evidence after conflict/authority checks, while a
   non-related case is unchanged and approved evidence permits completion.
5. RED then GREEN: project the exact evidence reference into the successful case cycle so returned
   and later cycles remain isolated; keep route approvers, effective approvers, action history, and
   Exception Register evidence unchanged.

## Persistence and contract work

- Add one migration for immutable `general_meeting_approvals`, including application/document/user
  foreign keys, status/type checks, supersession linkage, timestamps/indexes, and a nullable frozen
  reference from each approval case to the evidence it consumed.
- Add the route/view and update `docs/working/API_CONTRACTS.md` with request, response, permission,
  idempotency/supersession, object/document access, projection, and final-gate error contracts.
- Add distilled 007G source decisions to the Epic 007 digest and record any source-silent default
  in `docs/working/ASSUMPTIONS.md`.

## Verification and handoff

- Preserve each targeted RED and GREEN command under `evidence/terminal-logs/`, using only the
  orchestrator-managed backend interpreter.
- Run backend check, migration sync, targeted/full coverage suite, and frontend build, typecheck,
  lint, and tests. Save API examples and final gate logs in the run evidence folder.
- Review the diff against the slice and source references, check diff limits/protected paths,
  sharpen the next one or two Not Started slices from already-opened Epic 007 material, and finish
  the required Ralph state/progress/handoff/slice/run artifacts.
