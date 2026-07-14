# Review Packet: 2026-07-14_120956_normal_run

## Result
Ready for independent validation

## Slice
008C-documentation-checklist-applicability

## Outcome

Approved sanction finalisation now atomically persists one legal checklist and eleven ordered item
facts. The legal owner computes always-required and conditional applicability, exposes source
blockers without guessing, links only selector-approved generated-document ids, and serves a
metadata-only §27.1 response through permission plus object scope. Pre-sanction 005D behavior remains
compatible on the shared GET path; no public legal mutation route was added.

## Traceability

- The source says M06-FR-001 creates the checklist automatically after sanction. The public final
  approval passes a legal-checklist callback into the approval transaction; verified by
  `test_final_joint_approval_creates_source_shaped_sanction_and_completion_evidence` and the forced
  rollback test.
- SOP/API §27.1 say physical needs SH-4, demat needs CDSL, subsidiary route needs tri-party, and a
  mismatch needs Bank Verification. `document_checklist._applicability_specs` applies only frozen or
  persisted facts and exposes blockers; verified by the physical/demat/subsidiary/mismatch and
  missing/conflicting matrix tests.
- Data-model §16.4-§16.5 says one checklist per application and one item code per checklist with
  protected links and bounded states. The migration/model constraints enforce those invariants;
  verified by direct-invalid-state tests and two real PostgreSQL five-worker runs.
- Auth §§12.7/19 and the slice require checklist permission plus application scope. The GET module
  covers Compliance, CS, Credit Manager/application scope, attributable committee, and persisted
  auditor scope while denying permission-only/unrelated actors; verified by the API matrix test.
- 008B3 rendering proves content only. The selector exposes a generated loan-document id without
  file/storage facts and leaves completion pending; verified by the metadata-only link/API test.

## Validation

- TDD: expected import RED, then focused GREEN; final focused set 12/12 with one expected local
  PostgreSQL skip.
- PostgreSQL: the exact five-worker race passed twice, zero skips.
- Backend: Django check and migration sync GREEN; 746 tests GREEN, 23 expected PostgreSQL-only skips,
  93% coverage (85% floor).
- Frontend: build, typecheck, lint GREEN; 33 files and 293 tests GREEN.
- Diff/protected paths: within configured file/line/migration/dependency limits; no protected path.

## Scope Review

No frontend production code, public legal update/approve route, file download, completion decision,
security instrument, stamp/notary/signature action, disbursement readiness, or external side effect
was added. 008D received run-ahead constraints and 008E was sharpened from its template stub.

## Recommended Next Action
Run independent Ralph validation, then let the orchestrator commit/merge/push. The architecture
review cadence is due before 008D.
