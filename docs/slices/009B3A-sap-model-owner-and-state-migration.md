# Slice 009B3A: SAP Model Owner and State Migration

## Status
Complete

## Origin
Oversized slice: `009B3`

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement

## Depends On
- 009B2

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Make `sap_workflow` the canonical Django model owner for existing SAP request, delivery,
completion, code, and retained-workbook state without moving, copying, decrypting, or re-encrypting
any applied Finance business row.

## Source / Review References

- `docs/source/codebase-design.md` §§16.1, 20.1-20.4, 22, 26-28, 36.2, and 42
- `docs/source/integrations.md` §§8.1-8.5 and INT-SAP-001 through INT-SAP-006
- `docs/source/api-contracts.md` §§6-8 and 29
- `docs/source/data-model.md` §§19.1-19.2, 28-30, and 34
- `docs/source/functional-spec.md` BR-047 through BR-050 and M07-FR-001 through M07-FR-008
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-16_143718_architecture_review`
- Failed oversized run `.ralph/runs/2026-07-16_174245_normal_run/`

## Concrete Requirements

1. Define the canonical SAP request, retained workbook/delivery, completion/replay, and customer-code
   model state in `sap_workflow`, retaining the exact existing physical table names, columns, ids,
   constraints, indexes, and relations expected by applied Finance migrations.
2. Use state-only/non-destructive Django migration operations, or an equivalently explicit owner
   transfer, so upgrading an existing database performs no business-row copy, delete, table rename,
   plaintext materialisation, checksum rewrite, or ciphertext re-encryption.
3. Preserve request status/timestamps, canonical supplied/omitted completion digest, delivery and
   workbook checksums, audit/workflow/task foreign keys, member/application links, code identity,
   and every uniqueness/concurrency constraint byte-for-byte where the database exposes it.
4. Keep only a one-way, policy-free compatibility import for legacy callers that cannot move in this
   slice. Compatibility names must resolve to the canonical SAP model classes and may not contain a
   second manager, query, action, storage, or decision implementation.
5. Do not change the public HTTP request/create/send/download/complete/reuse/read contract or move
   executable orchestration policy in this slice; `009B3B` consumes the transferred state and closes
   that dependency seam.

## Test Cases

- A failing-first ownership probe proves that the canonical model metadata belongs to
  `sap_workflow` while retaining the expected physical Finance-era tables and constraints.
- Migration-executor tests load the exact pre-009B3A state, capture row counts, primary keys,
  foreign keys, ciphertext, checksums, delivery/completion digests, and table names, migrate forward
  and backward where supported, and assert exact preservation with no duplicate SAP facts.
- Historical migration-state tests prove old migrations still load and a fresh database reaches the
  same final schema without circular migration dependencies.
- Compatibility tests prove legacy imports are aliases to the canonical SAP models and contain no
  independent query/action/storage policy.
- Focused PostgreSQL uniqueness/race tests prove the ownership transfer does not weaken the existing
  one-winner request and customer-code guarantees.

## Evidence Required

Failing-first owner probe; before/after schema and row-identity manifest; migration graph; sanitized
ciphertext/checksum/digest preservation results; compatibility proof; focused tests; twice-run
PostgreSQL acceptance; full configured gates.

## Risk Level
High

## Acceptance Criteria

- `sap_workflow` is the canonical model-state owner while all applied data and physical identities
  remain unchanged.
- No state migration copies or re-encrypts retained business data.
- The compatibility seam is one-way and policy-free, ready for executable closure in `009B3B`.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] State-only migration implemented
- [x] Existing schema and data identity proved
- [x] Permissions and API behavior proved unchanged
- [x] Audit and workflow relations preserved
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [x] Commit delegated to the orchestrator only after passing configured gates
