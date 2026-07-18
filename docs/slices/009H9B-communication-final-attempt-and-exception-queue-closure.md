# Slice 009H9B: Communication Final-Attempt and Exception-Queue Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Make an expired worker claim at the retry cap terminal and reviewable instead of requeueing a job
that can only violate its attempts constraint.

## Depends On
- 009H9A

## Source / Review References
- `docs/source/codebase-design.md` §§22.1-22.3, 26.1-26.3, 34, 40.1, and 42.4
- `docs/source/integrations.md` §§7.3, 10.5-10.6, 22.1-22.3, 29, and 33.3
- `docs/source/data-model.md` §34
- `docs/slices/009H8-communications-worker-runtime-and-crash-recovery-closure.md` requirements 2-4
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-18_204305_architecture_review`
- Review probe `.ralph/runs/2026-07-18_204305_architecture_review/evidence/review-probes/review_contract_probes.py`

## Concrete Requirements
1. Under the same job lock used for stale recovery, an expired `running` claim with
   `attempts >= max_attempts` becomes terminal `failed`: retain the exact attempt count, clear the
   claim/lease, set terminal time and safe `worker_crash` failure code, increment recovery evidence
   at most once, and never return the job as due or call `start_job` again.
2. An expired claim below the cap remains safely retryable with unchanged attempts until the one
   replacement worker claims it. Concurrent scanners/workers retain one terminal-or-retry winner;
   stale claim tokens cannot defer, complete, mutate exception truth, or enter a provider seam.
3. Replace the notification-only approximation with one communications-owned exception-queue row
   per exhausted job containing the source §22.3 provider/job type/related entity/safe error/retry
   count/assigned owner/resolution action/resolved by/resolved at facts. The ordinary projection is
   redacted; recipient, content, provider secret/id, bank/UTR, key, payload, and actor-network facts
   are never exposed. One reachable operator notification may point to this row without duplicating
   it.
4. Resolution is an explicit authorised action with append-only audit/workflow evidence. It cannot
   mark the communication sent, reset attempts, redispatch accepted evidence, or bypass H6 legacy
   exclusion; an authorised retry creates a new governed attempt only when the source retry policy
   permits it, otherwise resolution records manual closure without fabricating delivery.

## Test Cases
- Copy the final-attempt crash probe failing first. Cover `max_attempts - 1`, exact cap, already
  exhausted, repeated scan, stale loser, and changed/absent job evidence.
- Five scanners and five workers race terminal recovery twice on PostgreSQL; assert one exception,
  one operator task, one audit/workflow chain, no fourth attempt, and no provider call.
- Exercise Email/advice/generic failure classes, safe redaction, authorised resolution, denied and
  stale resolution, and accepted-provider recovery without resend.

## Runtime Capabilities

postgresql-five-race-acceptance

## Database / Migration Impact
At most one communications migration for the protected exception-queue owner and its constraints.

## Risk Level
High

## Acceptance Criteria
- A worker crash on the final allowed attempt is terminal, singular, and operator-reviewable.
- No retry/recovery path can exceed `max_attempts`, strand the job, or fabricate delivery truth.

## Done Checklist
- [ ] Execution plan written
- [ ] Final-attempt crash probe written failing first
- [ ] Terminal recovery and fenced races implemented
- [ ] Exception queue, redaction, resolution, and audit implemented
- [ ] PostgreSQL acceptance green twice
- [ ] Risk, evidence, handoff, state, contract, and digest updated
- [ ] Commit delegated to the orchestrator after gates

