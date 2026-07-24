# Execution Plan

Selected slice: 012D2-auditor-observation-workflow

## Permission and scope check

- Product edits are limited to `sfpcl_credit/**`; contract documentation is limited to
  `docs/working/API_CONTRACTS.md`; run evidence is limited to this run folder.
- No protected path or `docs/source/**` file will be changed.
- This is a High-risk backend/API/model slice. The agent will run focused tests only; the
  orchestrator owns the authoritative complete-suite coverage lane.

## Public boundary

- Add `/api/v1/audit-observations/` with `POST` and paginated `GET`, plus
  `/api/v1/audit-observations/<uuid>/` with `GET` only.
- Accept a bounded observation, audit-scope identifier, and supported immutable source references.
  Resolve and authorise every reference server-side; project only sanitised identifiers and
  restricted signed-download metadata.
- Permit only an active Internal Auditor with the existing audit-read permission and active audit
  scope. Default-deny all other roles and audit every denial.
- Persist creator/role/team snapshot, scope, sanitised text, immutable references, and timestamp in
  one append-only model. Reject update/delete and caller-supplied lifecycle/classification fields.

## TDD behavior cycles

1. RED then GREEN: a scoped auditor creates one observation through the API and can list/detail it;
   creator, scope, sanitised text, source references, and creation time are durable.
2. RED then GREEN: blank/oversized/injection or sensitive text and unknown lifecycle fields are
   rejected or sanitised without leaking secrets.
3. RED then GREEN: guessed, missing, cross-scope, and unauthorised evidence/source references deny;
   restricted evidence receives only short-lived signed metadata and access is audited.
4. RED then GREEN: operational roles cannot forge observations; inactive/out-of-scope auditors are
   denied and every denial is centrally audited.
5. RED then GREEN: PUT/PATCH/DELETE are unavailable, model rows reject mutation/deletion, and sampled
   audit/workflow/version/business rows remain unchanged.
6. Run reverse-consumer tests for 011O and 012D plus audit/document append-only guarantees.

## Implementation and verification

- Add one non-destructive compliance migration and model ownership/module boundary.
- Wire thin Django views and routes using the standard success/error/pagination envelopes.
- Update `docs/working/API_CONTRACTS.md` with exact request/response/filter/error/immutability rules.
- Save each focused RED/GREEN command output under `evidence/terminal-logs/`.
- Run `manage.py check`, `makemigrations --check`, focused/reverse-consumer tests, and prepare
  permission/API/immutability evidence, `risk-assessment.md`, and `review-packet.md`.
- Finish with review result exactly `Ready for independent validation`.
