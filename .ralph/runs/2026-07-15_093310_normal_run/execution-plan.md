# Execution Plan

Selected slice: 008K4-current-evidence-and-security-read-closure

## Scope and constraints

- Implement only 008K4: immutable bank/cancelled-cheque verification decisions, current checklist
  evidence reconciliation, generation/checklist lock coherence, ordinary security DTO privacy, and
  fail-closed mixed-mask handling.
- Preserve the existing top-level process coordinator and module dependency direction. Internal
  terminal selectors may retain exact evidence; ordinary GET serializers must receive explicit
  business projections only.
- Use the orchestrator-managed backend interpreter for every Django/test/coverage command. Do not
  modify protected paths, frontend code, or source documents, and do not commit.

## Test-first implementation sequence

1. Add a focused 008K4 regression suite and run one failing mixed-mask test. Implement the smallest
   canonical redactor change that preserves fixed masks and governed last-four projections.
2. Add one failing public-path bank-decision test. Introduce an application/member-owned immutable
   verification decision with exact bank, cheque file/checksum, verifier, request, audit, workflow,
   version, status, and timestamp identity; add one migration and a narrow service boundary. Prove
   legacy mutable status-only rows cannot complete checklist items.
3. Add failing checklist current-evidence tests for missing/changed action, workflow, audit, version,
   renderer, bank, security, applicability/case, request, and digest facts. Recompute through the
   top-level coordinator under a shared application lock and make borrower-safe projection plus CS
   approval fail closed with zero success writes.
4. Add failing ordinary-read contract scans against real package, PoA, SH-4, CDSL, cheque, and
   checklist rows. Replace raw evidence serialization with explicit masked DTOs and exercise every
   documented reader/state/object-scope combination without weakening internal terminal access.
5. Add generation-versus-item-completion and generation-versus-CS-approval PostgreSQL five-worker
   probes. Establish one application-first lock/version order so exactly one coherent current truth
   wins and loser paths retain no success action/audit/workflow/version identity. Run each affected
   race twice when the declared PostgreSQL capability is available.

## Verification and closeout

- Save failing-first and green focused outputs under `evidence/terminal-logs/`, plus response-key and
  plaintext scans and PostgreSQL race output.
- Run Django check, migration drift, focused backend tests, full backend coverage, and the configured
  frontend lint/typecheck/tests/build gates.
- Review the complete uncommitted diff against repository standards and the selected slice, correct
  findings, then write changed-files, risk assessment, review packet, final summary, progress,
  handoff, state, and slice status. Verify the already-sharpened 008L3 and 008M queue entries remain
  concrete and dependency-correct.
