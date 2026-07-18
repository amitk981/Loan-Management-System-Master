# Slice 009H9C: Communication Channel, Interface, and Provider-Evidence Closure

## Status
Complete

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Restore the source-shaped communications facade, route Email and SMS through their real channel
seams, and retain replay/provider truth without treating every channel as email.

## Depends On
- 009H9B

## Source / Review References
- `docs/source/codebase-design.md` §§20.2-20.6, 22.2, 26.1-26.3, 34, 36.1-36.2, 40.1-40.2,
  and 42.4
- `docs/source/integrations.md` §§6.1-6.3, 10, 11, 19.3, 21, 22, 29, and 33.3
- `docs/source/api-contracts.md` §§3, 6-8, 31.5, 39.2, and 45
- `docs/source/functional-spec.md` M16-FR-001-M16-FR-005 and M16-FR-007
- `docs/slices/009H7-communications-dispatcher-interface-and-idempotency-closure.md` requirements 1-5
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-18_204305_architecture_review`
- Review probe `.ralph/runs/2026-07-18_204305_architecture_review/evidence/review-probes/review_contract_probes.py`

## Concrete Requirements
1. Expose one stable source-shaped `CommunicationDispatcher` facade for
   `create_from_template`, `send(communication_id, idempotency_key)`, and `retry_failed(actor=None)`.
   HTTP request parsing, request metadata, job batching, advice finalization, and private worker
   claims remain behind internal owner/coordinator methods rather than widening the public facade.
   Contract tests must call the same facade as production callers, not merely assert method names.
2. Enforce channel/template/recipient coherence before any row/job/audit write. Email uses an
   `EmailAdapter` and validated email recipient; SMS uses a separate `SmsAdapter` and validated
   mobile recipient. SMS rejects PAN, Aadhaar, full bank/cheque/IFSC/ciphertext variables and unsafe
   rendered values. Phone/courier may create an explicit manual task if source-owned, or return a
   stable unsupported-channel validation error; they must never call email or claim provider sent.
3. Generic provider acceptance must be immutable, singular, and reconciled against job,
   communication, channel, payload digest, idempotency key, provider result, and actor before
   `sent`. Email/SMS retries reuse exact accepted evidence without provider re-entry. Store safe
   provider status through the communications/integration evidence owner required by source §42.4,
   not only mutable fields on the job.
4. Generic send and §31.5 advice exact-key replays return the source §45.2 replay shape with
   `idempotency_replayed: true` and the retained original response; changed/cross-actor/cross-object/
   cross-channel reuse remains zero-write conflict. Update the contradictory old no-provider shell
   text in `docs/working/API_CONTRACTS.md` to the current asynchronous contract.
5. Move due-job iteration/evidence shaping behind the deep module so Celery task functions are thin
   wrappers. Preserve H8 on-commit publication, leases, periodic recovery, safe defaults, H6 legacy
   exclusion, H9B exception behavior, and the acyclic communications/process/disbursements seam.

## Test Cases
- Copy the SMS-through-email review probe failing first. Cover Email, SMS, mismatched template,
  malformed recipient, phone/courier, every sensitive SMS variable/value, manual/fake/future
  adapters, and no-provider behavior through public interfaces.
- Freeze the public facade signature/return contract and prove HTTP/advice/worker callers cross it;
  reject direct/private alternate send policy with static and runtime dependency tests.
- Exercise exact/changed/cross-channel idempotency and source §45.2 envelopes plus immutable
  provider-evidence tamper and crash/recovery matrices.
- Run generic Email/SMS five-caller send and five-worker claim races twice on PostgreSQL with one
  provider acceptance, one immutable evidence chain, and no recipient/content leakage.

## 009H9A Sharpening Extract

- Integrations §21.1 requires an idempotency key for both Email and SMS, and §21.2 identifies the
  communication id as their duplicate identity. Preserve that pair through queued, retrying,
  failed, and provider-accepted paths rather than deriving channel-specific duplicate rules.
- INT-COMM-002/003 require asynchronous queueing and retryability; INT-COMM-005 specifically bars
  sensitive values from SMS and logs. Channel tests must therefore assert both the selected adapter
  call and the absence of raw rendered recipient/content values from job, error, and task evidence.

## Runtime Capabilities

postgresql-five-race-acceptance

## Database / Migration Impact
At most one communications migration to generalise or add immutable generic provider-attempt
evidence without rewriting H6 advice attempts/history.

## Risk Level
High

## Acceptance Criteria
- SMS can never cross the Email adapter or carry source-forbidden sensitive content.
- All callers use one source-shaped dispatcher, exact replay is contract-compliant, and provider
  acceptance is immutable and recoverable.

## Done Checklist
- [ ] Execution plan written
- [ ] SMS/interface/replay probes written failing first
- [ ] Channel-specific adapters and validation implemented
- [ ] Public facade and immutable provider evidence implemented
- [ ] API contracts and thin tasks aligned
- [ ] PostgreSQL acceptance green twice
- [ ] Risk, evidence, handoff, state, and digest updated
- [ ] Commit delegated to the orchestrator after gates
