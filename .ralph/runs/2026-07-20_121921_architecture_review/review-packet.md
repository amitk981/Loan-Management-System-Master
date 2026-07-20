# Review Packet: 2026-07-20_121921_architecture_review

## Result
Ready for independent validation

## Slice
architecture-review

## Review Boundary

- Fixed point: successful architecture-review commit `2944b3ea`.
- Product endpoint: `34ac6b75`.
- Reviewed slices: `010E3`, `010F`, `010G`, and `010H`.
- Excluded from product critique: later Ralph-only commit `c8b0fa71`.
- Product code was reviewed but not modified.

## Standards

- High: interest generation/accrual/capitalisation replays rebuild `original_response` from live
  issue, SAP, and delivery state; the capitalisation test explicitly expects the later state. This
  violates API §45.2 and the exact-retained-result invariant.
- High, carried: active rate creation still inherits `QuerySet.bulk_create`, and future-effective
  activation immediately overwrites `LoanAccount.current_interest_rate`. Configuration, loan, and
  interest owners also remain coupled through private ORM models.
- High: approved invoice configuration is mutable and issuance reads its live role/template,
  allowing a generated decision's authority/evidence to change retroactively.
- Medium: interest tests race different idempotency keys but do not prove two exact same-key
  responses; serviceable-status and fixture policy remain duplicated.

## Spec

- High: 010H subtracts `interest_paid_amount` twice, capitalises tax/fee, and never resolves payments
  made after invoice issue but by 30 April. Its replay is live rather than original.
- High: 010F/010G apply the period-end rate (and for invoices current principal) to the full period;
  mid-period rate/principal boundaries are neither segmented nor failed closed.
- High, carried: AC-FIN-3 remains partial because active rate rows can bypass the canonical owner and
  future-effective versions become current early.
- Medium, carried: AC-FIN-6 limits prefixes but does not database-window deep combined pages.
- Medium, carried: AC-FIN-7 remains open because changed tests still construct other `TestCase`
  instances, call `setUp`, and traverse private fixture helpers.
- Medium symptoms grouped under the new interest root: 010H creates a document but no durable
  hard-copy task, leaves complete schedule/interest truth unresolved, and 010F–010H share the
  general 1,570-line engine contrary to the digest's owner separation.

## Finding Closure Manifest

| Finding ID | Root ID | Severity | Disposition | Reproducer | Corrective Slice | Closure Evidence |
|---|---|---|---|---|---|---|
| AR-010-INTEREST-001 | ROOT-010-INTEREST-CALCULATION-OWNER | High | New | .ralph/runs/2026-07-20_121921_architecture_review/evidence/review-probes/interest-owner.log | 010H2 | - |
| AR-010-ALLOCATION-001 | ROOT-010-ALLOCATION-ADMISSION | High | Closed | .ralph/runs/2026-07-20_121921_architecture_review/evidence/review-probes/allocation-reproducer.log | - | .ralph/runs/2026-07-20_121921_architecture_review/evidence/review-probes/allocation-closure.log |
| AR-010-STATEMENT-001 | ROOT-010-STATEMENT-EVIDENCE | High | Closed | .ralph/runs/2026-07-20_121921_architecture_review/evidence/review-probes/statement-reproducer.log | - | .ralph/runs/2026-07-20_121921_architecture_review/evidence/review-probes/statement-closure.log |
| AR-010-RATE-001 | ROOT-010-RATE-VERSION-OWNER | High | Carried | .ralph/runs/2026-07-20_121921_architecture_review/evidence/review-probes/rate-owner.log | 010E4 | - |
| AR-010-LEDGER-001 | ROOT-010-LEDGER-PAGINATION | Medium | Carried | .ralph/runs/2026-07-20_121921_architecture_review/evidence/review-probes/ledger-pagination.log | - | - |
| AR-010-SERVICING-SEAM-001 | ROOT-010-SERVICING-OWNER-SEAM | Medium | Carried | .ralph/runs/2026-07-20_121921_architecture_review/evidence/review-probes/servicing-seam.log | - | - |

## Convergence Metrics

- Findings closed: 2
- New Critical: 0
- New High: 1
- New Medium: 0
- New Low: 0
- Corrective slices added: 2

The prior review added one corrective and closed none; this review adds two and closes two, so the
two-review “additions exceed closures” trigger is not met. `010E4` is the one permitted successor
for trusted generation-one root `ROOT-010-RATE-VERSION-OWNER`; another recurrence exhausts its
ordinary corrective budget. `010H2` starts generation one for the distinct interest-calculation
root. `010I` now depends on `010H2`, so monitoring cannot consume known incorrect financial truth.

## Requirement and Repository Audit

- M10-FR-001–011 all have implemented owners, but M10-FR-001/002 remain conditional on `010E4` and
  M10-FR-003/005/007–011 remain conditional on `010H2`. No requirement was silently marked complete
  or newly deferred.
- `docs/working/CONTEXT.md` remains truthful: Epic 010 is active and the current financial owner
  corrections still precede later monitoring work.
- No slice has `Blocked` status, so no stale prerequisite required re-parking.
- No ADR was added: the review restores existing effective-date, unpaid-interest, idempotency, and
  module-owner contracts rather than choosing a new durable business rule.

## Evidence

- Focused closure run: six tests passed in 2.713 seconds with exit code 0, covering allocation replay,
  statement ambiguity, rate immutability/consumption, and ledger cardinality.
- Current bound reproducers are retained under `evidence/review-probes/` with exact Finding ID and
  Root ID lines. Both High open roots contain explicit failing signals.
- Independent Standards and Spec passes reviewed the same fixed product boundary and converged on
  the rate, calculation/replay, pagination, and public-test-seam findings.
- Ralph's semantic validator passed all six stable manifest rows; per-root convergence validation,
  new-corrective count (`2`), runtime-capability checks, queue drain, docs-only scope, and protected-
  path checks all exited zero.

## Recommended Next Action
Run Ralph's independent documentation-only validation. If the manifest, queue, frozen-candidate,
and artifact checks pass, commit the review and execute `010E4` before `010H2`; do not resume `010I`
until both High corrective contracts are complete.
