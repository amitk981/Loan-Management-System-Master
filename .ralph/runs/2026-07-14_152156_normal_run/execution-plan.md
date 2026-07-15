# Execution Plan

Selected slice: 008E-signature-mismatch-workflow

1. Confirm the source contract and existing legal-document seams: current-renderer Stage 4 target
   authority, documents-owned retained-upload provenance, application-owned signature facts, and
   checklist applicability-only projection. Keep all frontend surfaces unchanged.
2. Add public-interface tests one tracer at a time for signature capture, exact replay/change,
   validation, permissions/object scope, evidence resolution, checklist projection preservation,
   and concurrent writes. Save each required failing and passing command output under
   `evidence/terminal-logs/`.
3. Add the `signature_records` model and one migration with bounded database vocabularies,
   signed/mismatch/resolution consistency, protected document/verifier/evidence links, and indexes
   for document/status/signer access. Replace only the checklist signature null-only constraint
   necessary for real signature links; do not set checklist approval signatures.
4. Implement one legal-documents-owned signature mutation module behind the two specified POST
   adapters. Centralise action-specific permission, sanctioned application scope, renderer and
   evidence provenance, replay/change locking, attributable history, audit/workflow/version facts,
   and atomic checklist reconciliation. Responses expose evidence identity metadata only.
5. Update routes and the working API contract. Run focused tests after each red/green increment,
   then Django check, migration sync, full backend coverage, and unchanged frontend build,
   typecheck, lint, and tests.
6. Save API response examples and final evidence; perform a standards/spec review; write
   `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; update the
   selected slice, state, progress, handoff, assumptions/digest if required; and sharpen the next
   one or two Not Started slices from already-opened Epic 008 material.
