# Slice 009H9D: Communications Provenance and Operator-Boundary Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Reject incomplete queued-advice provenance and make the communication exception queue enforce the
exact exhausted job's authority, provider vocabulary, pagination, and deep-module boundary.

## Depends On
- 009H9C

## Source / Review References
- `docs/source/codebase-design.md` §§26.1-26.3, 34.1, 35.2, 40.1-40.2, and 42.1-42.4
- `docs/source/integrations.md` §§6.1-6.3, 7.3, 21-22, 29, and 33.3
- `docs/source/api-contracts.md` §§3, 6-8, 39.2, and 45
- `docs/slices/009H9A-queued-advice-migration-provenance-closure.md` requirement 2
- `docs/slices/009H9B-communication-final-attempt-and-exception-queue-closure.md` requirements 3-4
- `docs/slices/009H9C-communication-channel-interface-and-provider-evidence-closure.md` requirements 1-5
- `docs/working/API_CONTRACTS.md` communication exception queue
- `.ralph/runs/2026-07-19_014802_architecture_review/evidence/review-probes/review_contract_probes.py`

## Concrete Requirements
1. At the existing 0007-to-0008 provenance decision boundary, a queued job is `verified` only when
   every required template snapshot fact is complete, internally coherent, and checksummed. Blank
   or invalid code/name/type/audience/version/approval/subject/body facts, malformed variable
   collections, and one-field drift with a recomputed checksum remain `legacy_partial` /
   `ambiguous_legacy`; clear their untrusted snapshot facts and preserve H6 nondispatch exclusions.
2. Exception collection, detail, and resolution require both the assigned-owner match and the
   exact current permission for `job_type`: `communications.communication.send` for generic jobs,
   `finance.disbursement.send_advice` for advice jobs. Either permission alone never grants the
   other job type. Missing, inactive, cross-owner, cross-kind, and permission-revoked cases are
   nondisclosing and zero-write.
3. Store and project the source provider vocabulary (`email` or `sms`) independently from the
   configured adapter implementation identity. Normalize retained exception rows without losing
   job, retry, assignment, audit, workflow, or resolution truth; never expose dotted class paths,
   secrets, recipient/content, keys, payloads, or network facts.
4. Implement strict bounded page/page-size pagination for the exception collection with stable
   ordering and truthful totals. Unknown query parameters and invalid bounds use the standard
   validation envelope, and every reachable page applies the same exact job-kind authority.
5. Keep channel selection, configured adapter resolution, due-job iteration, and safe evidence
   shaping behind the communications owner. Process/Celery functions are thin delegators and do
   not read `Communication` to choose adapters or call underscore-prefixed dispatcher methods.
   Preserve the exact source-shaped public facade and all H6/H8/H9B/H9C retry, replay, lease,
   provider-evidence, and advice-finalization behavior.

## Test Cases
- Copy all three review probes failing first. Add one-field recomputed-checksum matrices for every
  required queued snapshot fact and preserve the genuine queued-job forward/reverse/reapply proof.
- Exercise generic and advice exceptions through list/detail/resolve for exact permission,
  opposite permission, revoked permission, inactive actor, cross-owner, stale version, and changed
  job evidence; assert denied calls disclose nothing and write nothing.
- Cover `email`/`sms` provider vocabulary, legacy normalization, deterministic pagination beyond
  100 rows, strict query validation, and redaction on every page.
- Add observable public-interface tests for Email/SMS execution and exact/changed/cross-channel
  idempotency. Replace source-string assertions with behavior or a dedicated dependency-boundary
  test that executes independently of implementation spelling.

## Runtime Capabilities

postgresql-five-race-acceptance

## Database / Migration Impact
At most one communications migration to normalize retained exception provider vocabulary and any
constraint needed to keep it stable. Preserve the already-required 0008 historical correction at
the earliest boundary where 0007 snapshot/job facts still exist.

## Risk Level
High

## Acceptance Criteria
- No incomplete queued snapshot can become verified even when its checksum is recomputed.
- No operator can read or resolve an exception without the exact current authority for that job.
- Exception provider, pagination, and deep-module behavior match the source contracts without
  regressing singular retry/provider/advice evidence.

## Done Checklist
- [ ] Execution plan written
- [ ] Review probes copied failing first
- [ ] Provenance completeness and migration matrices green
- [ ] Exact exception authority, provider, pagination, and redaction green
- [ ] Communications owner boundary and cross-channel replay tests green
- [ ] PostgreSQL acceptance green twice
- [ ] Risk, evidence, API contract, handoff, and digest updated
- [ ] Commit delegated to the orchestrator after gates
