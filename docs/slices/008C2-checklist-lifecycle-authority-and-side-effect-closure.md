# Slice 008C2: Checklist Lifecycle, Authority, and Side-Effect Closure

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Depends On
- 008B4
- 008C

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Make automatic checklist creation unavoidable at the sanction-decision boundary and make every
later refresh preserve independently owned completion evidence, canonical authority, and honest
conditional facts.

## Source / Review References

- `docs/source/functional-spec.md` M06-FR-001/M06-FR-009-M06-FR-018
- `docs/source/api-contracts.md` §§6-8 and 27.1
- `docs/source/data-model.md` §§16.4-16.6, 30, and 34
- `docs/source/auth-permissions.md` §§19.2/19.4, 26.4, 30.2, and 34.6
- `docs/source/codebase-design.md` §§6.3, 9.1-9.2, 14.2-14.3, 27.1, 36.1-37.2, and 42.2
- `docs/slices/008C-documentation-checklist-applicability.md`
- `docs/working/ASSUMPTIONS.md` A-104/A-105
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_124337_architecture_review`

## Concrete Requirements

1. A final approval may not create a `SanctionDecision` without invoking the legal-checklist
   coordinator in the same transaction. Make the completion callback mandatory for terminal
   approval (or make the low-level terminal writer non-public); direct calls, tasks, tests, and HTTP
   adapters must cross the same process boundary. Missing orchestration fails zero-write.
2. Replace the stored `routing_snapshot_is_coherent` shortcut with the approval owner's canonical
   latest-cycle/frozen-package/terminal-decision decision. Malformed or stale-true cases create and
   refresh nothing even when shallow status flags look approved.
3. Separate applicability synchronisation from completion/verification ownership. An unchanged
   applicability refresh preserves `completion_status`, verifier, time, remarks, checklist status,
   and signature facts byte-for-byte. A changed applicability decision that conflicts with completed
   evidence returns an explicit zero-write conflict until its owning correction workflow resolves it;
   it must never reopen or erase completion silently.
4. Treat a generated-document link update as metadata linkage, not
   `document_checklist.applicability_changed`. Link only 008B4 current renderer-provenance rows,
   preserve completion, and record no false applicability evidence; any real linkage evidence must
   use its own honest action semantics.
5. Obtain cancelled-cheque/mismatch facts through an application- or member-owned public fact seam;
   `legal_documents` must not import/query the `members` ORM. Only an authoritative verified mismatch
   decision counts. Pending/unverified/default-false, missing, malformed, or conflicting rows retain
   A-105's visible blocker and cannot be called `persisted_signature_match`.
6. Treat subsidiary routing as authoritative only when the frozen snapshot contains the complete
   boolean flag set. Missing/partial/malformed flags remain blocked rather than collapsing through
   Python truthiness to a direct route.
7. Resolve checklist reads through one owner-facing permission/object-scope boundary before
   checklist/item existence, counts, metadata, or serialization. Preserve A-104's pre-sanction route
   compatibility, but prevent role branches and 403/404 differences from becoming an existence
   oracle for unrelated post-sanction records.
8. Carry request id, IP, user agent, actor role, and actor team from sanction completion/refresh into
   checklist audit evidence. Creation, genuine applicability change, linkage change, denial, replay,
   and rollback must each have accurate zero/one-write semantics.

## Test Cases

- Direct final approval without the coordinator is zero-write; HTTP and direct process success each
  create exactly one sanction/checklist/item/evidence ledger atomically.
- A genuine five-worker final-sanction race (not only five refreshes of an already approved fixture)
  passes twice with one decision, checklist, eleven items, and exact winner/loser evidence.
- Replaying or correcting applicability after pending, completed, and completed+verified items
  preserves independent state; conflicting applicability is explicit and zero-write.
- New current-provenance generated metadata links without completion changes or a false
  applicability audit; legacy-unverified rows remain unlinked.
- Pending/verified-match/verified-mismatch/conflicting cheque facts and complete/partial subsidiary
  snapshots exercise distinct exact outcomes through owner-facing seams.
- Compliance, Company Secretary, Credit Manager, attributable committee, auditor, permission-only,
  unrelated, unknown, and inactive actor matrices prove nondisclosure before checklist queries.
- Checklist creation/change audit content asserts request, network, role/team, approval case,
  sanction decision, old/new facts, and source reason; rollback removes the entire ledger.

## Evidence Required

Backend RED/GREEN logs, authority/fact matrices, exact audit examples, dependency proof, twice-run
PostgreSQL final-sanction race output, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Every sanctioned decision owns exactly one atomic checklist; no public/internal bypass remains.
- Applicability refresh cannot destroy completion/verification or mislabel metadata changes.
- Conditional facts, object scope, dependencies, and audit evidence follow their canonical owners.
- All configured gates pass.
