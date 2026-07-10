# Execution Plan

Selected slice: `004E2-witness-evidence-snapshot-and-input-hardening`

## Outcome

Make witness verification evidence immutable and malformed witness POST bodies envelope-safe,
without changing witness permissions, object access, masking, or qualification rules.

## Implementation sequence

1. Add one public-interface regression for malformed/non-object JSON and capture the failing API
   output (including zero witness/audit/workflow writes), then minimally translate parser/shape
   errors into the standard `400 VALIDATION_ERROR` envelope.
2. Add one stable-evidence API regression, then persist and serialize the exact qualifying
   shareholding UUID and folio snapshot selected at create time. Move witness list query and
   serialization composition behind the application service seam so the view only authenticates,
   parses, calls, and translates.
3. Add migration tests for conservative unambiguous backfill, ambiguous/no-match nullable legacy
   provenance, reverse safety/idempotency, and physical index inspection. Implement one additive
   migration that adds the protected nullable FK/snapshot, backfills only from matching witness
   creation-audit folio + member/shareholding facts, and removes redundant explicit indexes while
   retaining named application/PAN-hash/Aadhaar-hash indexes exactly once.
4. Run focused tests after every red/green cycle, then run Django check, migration sync, full
   backend coverage, and all configured frontend gates. Save terminal logs and response/index
   evidence under this run folder.
5. Record changed files, risk, traceability/review packet, final summary, and update API contract,
   digest, progress, handoff, state, and slice status. Sharpen the next one or two Not Started
   slices using only source material already opened.

## Permissions and boundaries

- Planned writable paths are limited to `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`,
  `.ralph/state.json`, `.ralph/progress.md`, and this run folder; all are allowed by
  `.ralph/permissions.json`.
- No frontend or dependency change is planned. Protected files and `docs/source/**` remain
  untouched.
- Medium risk: additive nullable provenance columns plus a conservative data migration and index
  cleanup; no destructive data rewrite or permission/business-rule expansion.
