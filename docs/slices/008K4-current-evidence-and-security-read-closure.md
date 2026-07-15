# Slice 008K4: Current Evidence and Security Read Closure

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Depends On
- 008L2

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Close the reviewed gaps in source-owned bank verification, current checklist reconciliation,
generation-versus-approval locking, and ordinary security-reader privacy before staff or portal
surfaces consume final documentation truth.

## Source / Review References

- `docs/source/functional-spec.md` M06-FR-005 through M06-FR-019
- `docs/source/api-contracts.md` §§3, 6-8, 26-28, and 44
- `docs/source/data-model.md` §§16-17, 26, 28-30, and 34
- `docs/source/auth-permissions.md` §§19.2-19.4, 21-23, and 26.4
- `docs/source/codebase-design.md` §§4.2, 9.1-9.4, 20.7, 21, and 39
- `docs/slices/008K2-sensitive-security-contract-closure.md`
- `docs/slices/008K3-final-checklist-evidence-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-15_085859_architecture_review`

## Concrete Requirements

1. Replace mutable bank/cancelled-cheque status as checklist authority with an application/member-
   owned immutable verification decision identity. The current decision must bind exact application,
   member, bank account, cancelled-cheque document/checksum, status, verifier, verified time, request,
   audit, workflow, and version facts. Legacy rows without truthful decision identity remain readable
   history but cannot complete a new K3 item; do not invent a new verifier role or silently upgrade
   status-only rows.
2. Make checklist completion and Company Secretary reconciliation bind the exact `ChecklistAction`,
   `WorkflowEvent`, `AuditLog`, and single `VersionHistory` row. Recompute the current renderer,
   signatures, stamp/notary, security aggregate, bank decision, applicability/case, and terminal
   digest through the top-level coordinator. Missing, extra, changed, deleted, or cross-object
   evidence blocks with zero success writes.
3. Establish one shared lock/version order between document generation and checklist completion/
   approval. A same-type current document generated concurrently cannot make a just-created action
   stale between selection and commit. Prove generation-versus-completion and generation-versus-CS-
   approval changed races twice on PostgreSQL with one coherent winner and no loser success evidence.
4. Split ordinary security read projections from internal terminal-evidence selectors. Package,
   PoA, SH-4, CDSL, and blank-cheque GET responses may return source-documented masked business
   metadata only; they must omit retained evidence blobs, request/IP/user-agent context, role/team
   lists, signer-name snapshots, internal audit/action ids, hashes, ciphertext, and storage keys.
   Checklist coordination may consume exact internal evidence without granting it to ordinary readers.
5. Make the central redactor fail closed for partially masked strings: one `*` must not exempt mixed
   plaintext such as `1234*5678`. Preserve explicit safe fixed masks and source-authorised CDSL
   last-four projections without changing reveal authority or leaking plaintext into ledgers/errors.
6. Replace K2's 404-only finance proof with real PoA, SH-4, CDSL, cheque, package, and checklist rows
   before/after documentation approval. Cover every reader role, stale cycle, permission-only,
   unrelated object, and CFC zero-read state, and scan full ordinary DTOs for internal evidence keys.

## Test Cases

- Status-only/synthetic/mutable bank facts cannot complete cancelled or blank cheque items; an exact
  current immutable decision can, and later bank/document changes block without success evidence.
- Missing/changed workflow, audit, version, action, renderer, signer, stamp, security, case, request,
  verifier, or digest identity blocks item completion/CS approval and borrower-safe projection.
- Five-worker document-generation versus item/approval races pass twice on PostgreSQL and bind the
  retained current document, action, request, workflow, audit, and version to the sole winner.
- Every ordinary security reader gets only the documented masked DTO; internal evidence remains
  available solely through the coordinated checklist/reveal boundary.
- Recursive maps/lists and mixed-mask strings redact completely; fixed masks and explicit CDSL
  projections remain stable, while ciphertext/hash/plaintext scans stay clean.

## Evidence Required

Failing-first bank-decision, current-evidence, ordinary-read, mixed-mask, and generation-race probes;
focused/full gates; response-key/plaintext scans; and all affected PostgreSQL races twice.

## Risk Level
High

## Acceptance Criteria

- Checklist truth is current, action/audit/workflow/version-backed, and race coherent.
- Ordinary security readers receive no internal evidence or audit context.
- Bank verification and masking fail closed without invented legacy truth.
- All configured gates pass.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
