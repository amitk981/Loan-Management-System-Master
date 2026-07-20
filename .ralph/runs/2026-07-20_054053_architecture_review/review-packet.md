# Review Packet: 2026-07-20_054053_architecture_review

## Result
Ready for independent validation

## Slice
architecture-review

## Reviewed Boundary

- Fixed point: `b66aa3b63aec5ac6dc89819a2ae4efba40c2caad` (previous successful architecture review).
- Product commits: `75411117` (010C2), `a74fd0ca` (010D2), `d4ceb3a9` (010E), and
  `31f4e0f1` (010E2).
- Diff command: `git diff b66aa3b6...HEAD`.
- Product code was reviewed but not modified. Candidate changes are documentation and this run's
  retained review evidence only.

## Standards

- **High:** 010E2 records `InterestRateHistory.new_interest_rate` but never advances
  `LoanAccount.current_interest_rate`; sequential old/new histories and Loan Account projection can
  retain the sanctioned rate. This violates the data-model §§18.1/18.5 current/history relationship
  and the repository's immutable critical-truth direction.
- **High:** allocation replay serializes mutable `repayment.allocation_status`, and activation replay
  serializes mutable notice counts. Both violate API-contracts §45.2's original-response contract.
- **Medium:** `consume_effective_rate` check-then-insert does not translate a concurrent unique-key
  `IntegrityError` into exact retained replay/conflict, and has no PostgreSQL consumer race proof.
- **Judgment calls:** direct and subsidiary capture repeat policy around the same receipt owner;
  interest and servicing acceptance tests instantiate other `TestCase` classes and private helpers,
  while the test named immutable never attempts a mutation.

## Spec

- **High:** 010E2 requires consumed periods to reject retroactive mutation, but activation closes an
  open predecessor without checking `InterestRateConsumptionSnapshot`; the required backdated-
  consumed-period test is absent.
- **High reported by the independent pass:** callers can set `communication_required=false` and
  suppress notices despite M10-FR-002. The main review did not admit this as a stable finding because
  data-model §25.3, domain-model §19.2, and the selected slice explicitly define a communication-
  required flag and conditional fan-out; changing that policy would invent a business rule.
- **Medium:** AC-STATEMENT-3 is partial because subsidiary ambiguity detects a conflicting
  application but not a conflicting borrower; the permanent matrix covers only the former.
- No material 010C2/010E scope creep was found.

## Review Adjudication

The two prior High roots are carried, not closed: their headline public probes now pass, but one
declared acceptance branch remains false in each root. The new rate defects are one owner-boundary
finding rather than separate period, history, model, replay, and race leaves. The ledger and fixture
findings remain Medium and naturally combine with the same executable matrix. Because the previous
review added corrective work and this review closes none, convergence policy calls for one grouped
root-boundary correction rather than further leaf patches: new Not Started slice `010E3`, now a
prerequisite of 010F.

## Finding Closure Manifest

| Finding ID | Root ID | Severity | Disposition | Reproducer | Corrective Slice | Closure Evidence |
|---|---|---|---|---|---|---|
| AR-010-ALLOCATION-001 | ROOT-010-ALLOCATION-ADMISSION | High | Carried | .ralph/runs/2026-07-20_054053_architecture_review/evidence/review-probes/financial-owner.log | 010E3 | - |
| AR-010-STATEMENT-001 | ROOT-010-STATEMENT-EVIDENCE | High | Carried | .ralph/runs/2026-07-20_054053_architecture_review/evidence/review-probes/statement-ambiguity.log | 010E3 | - |
| AR-010-RATE-001 | ROOT-010-RATE-VERSION-OWNER | High | New | .ralph/runs/2026-07-20_054053_architecture_review/evidence/review-probes/financial-owner.log | 010E3 | - |
| AR-010-LEDGER-001 | ROOT-010-LEDGER-PAGINATION | Medium | Carried | .ralph/runs/2026-07-20_054053_architecture_review/evidence/review-probes/architecture-drift.log | 010E3 | - |
| AR-010-SERVICING-SEAM-001 | ROOT-010-SERVICING-OWNER-SEAM | Medium | Carried | .ralph/runs/2026-07-20_054053_architecture_review/evidence/review-probes/architecture-drift.log | 010E3 | - |

## Convergence Metrics

- Findings closed: 0
- New Critical: 0
- New High: 1
- New Medium: 0
- New Low: 0
- Corrective slices added: 1

## Evidence and Repository Checks

- Current-run static probes fail closed with exact finding/root identities for every manifest row.
- The original allocation admission and orphan statement-line public cases independently pass: two
  focused tests, exit code 0, retained in `evidence/review-probes/focused-positive.log`.
- 010C2/010D2's independently validated full-suite, PostgreSQL, migration, and closure evidence was
  inspected; passing coverage does not substitute for the omitted replay/ambiguity branches.
- Epic 010 is not complete. M09-FR-007–011 and M10-FR-001–002 were spot-checked; M09-FR-007 and the
  consumed-period portion of M10-FR-001 remain conditional on 010E3.
- `docs/working/CONTEXT.md` remains truthful. `.ralph/state.json` lists no `Blocked` slices, so no
  stale prerequisite required re-parking.
- No ADR was added: 010E3 restores already binding idempotency, financial-history, ambiguity,
  pagination, and public-module contracts rather than choosing a new durable business rule.

## Recommended Next Action

Run independent architecture-review validation. If it passes, execute `010E3` before 010F and
require its exact semantic closure evidence; do not add another leaf corrective for these roots.
