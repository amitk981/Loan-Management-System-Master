# Slice 010E3: Servicing Financial Owner and Replay Convergence

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Converge the Epic 010 financial owner boundary so statement matching, allocation replay, effective
rates, loan-rate history, and ledger reads consume immutable canonical decisions rather than
recomputing truth from mutable rows or private test fixtures.

## User Value
Finance and borrowers receive reproducible servicing results: an ambiguous receipt cannot be
auto-matched, an idempotent replay cannot change later, and a consumed rate period cannot be
rewritten by a backdated successor.

## Depends On
- 010E2

## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-ALLOCATION-001 | ROOT-010-ALLOCATION-ADMISSION | .ralph/runs/2026-07-20_054053_architecture_review/evidence/review-probes/financial-owner.log | AC-FIN-1 |
| AR-010-STATEMENT-001 | ROOT-010-STATEMENT-EVIDENCE | .ralph/runs/2026-07-20_054053_architecture_review/evidence/review-probes/statement-ambiguity.log | AC-FIN-2 |
| AR-010-RATE-001 | ROOT-010-RATE-VERSION-OWNER | .ralph/runs/2026-07-20_054053_architecture_review/evidence/review-probes/financial-owner.log | AC-FIN-3, AC-FIN-4, AC-FIN-5 |
| AR-010-LEDGER-001 | ROOT-010-LEDGER-PAGINATION | .ralph/runs/2026-07-20_054053_architecture_review/evidence/review-probes/architecture-drift.log | AC-FIN-6 |
| AR-010-SERVICING-SEAM-001 | ROOT-010-SERVICING-OWNER-SEAM | .ralph/runs/2026-07-20_054053_architecture_review/evidence/review-probes/architecture-drift.log | AC-FIN-7 |

## Source References
- `docs/source/functional-spec.md` M09-FR-007–011 and M10-FR-001–002
- `docs/source/api-contracts.md` §§41.4 and 45.2
- `docs/source/data-model.md` §§18.1, 18.5, 25.3, 30, and 34
- `docs/source/codebase-design.md` §§17–18.2, 26, 38.1–38.2, and 42
- `docs/slices/010C2-manual-allocation-and-financial-reversal-controls.md`
- `docs/slices/010D2-statement-evidence-owner-and-scope-closure.md`
- `docs/slices/010E2-effective-rate-versioning-and-borrower-notices.md`
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md`

## Concrete Requirements
1. Persist the exact original success projection for ordinary/manual allocation and rate activation;
   an exact replay returns the §45.2 wrapper around that frozen response even after reversal or
   communication delivery changes, while changed/cross-owner keys remain zero-write conflicts.
2. Make subsidiary narration ambiguity symmetric. Correct borrower/application facts plus any
   competing borrower or application identity remain unmatched; prove borrower-only,
   application-only, account-only, exact, conflicting-borrower, conflicting-application, multiple,
   and missing branches through public APIs.
3. Route interest calculation through the canonical configuration resolver and enforce coherent
   proposed/active evidence. Active or consumed rate fields cannot be mutated through model,
   queryset, service, or API paths without an append-only successor decision.
4. Before closing an open predecessor, reject a successor whose start would exclude any retained
   consumption date. Keep approved periods contiguous, overlap-free, and deterministic under races.
5. Keep each active floating loan's `current_interest_rate` and append-only `InterestRateHistory`
   old/new chain coherent with the canonical effective version, without rewriting prior consumption
   snapshots, notices, invoices, or accruals.
6. Make rate-consumption creation concurrency-safe: exact concurrent consumers retain one snapshot;
   changed loan/date reuse conflicts through a domain error rather than leaking `IntegrityError`.
7. Replace full-history ledger materialisation with database count/window pagination across combined
   allocation/reversal movements, preserving deterministic order and proving 1/21/101 cardinalities.
8. Move shared servicing fixtures behind public builders/facades and remove cross-`TestCase`
   construction/private-helper chains from the changed acceptance and PostgreSQL suites.

## Scope Boundaries / Non-Goals
- No new allocation rule, statement fuzzy matching, rate formula, benchmark/spread policy, invoice,
  accrual, frontend, or visual redesign.
- Do not change historical financial values merely to make the new invariants pass; retain explicit
  migration exceptions where legacy truth cannot be proven.

## Trusted PostgreSQL Acceptance
- Test: `sfpcl_credit.tests.test_servicing_financial_owner_closure.ServicingFinancialOwnerPostgreSQLAcceptanceTests`
- Expected tests: 5

## Acceptance Criteria
- [AC-FIN-1] Allocation replay after reversal returns its byte-stable original response; changed and
  cross-receipt replays remain zero-write conflicts.
- [AC-FIN-2] Public subsidiary matching rejects every conflicting borrower/application ambiguity and
  closes AC-STATEMENT-3 without weakening exact direct-receipt matching.
- [AC-FIN-3] Active and consumed rate versions are immutable through every supported write path and
  resolve through the canonical configuration interface.
- [AC-FIN-4] A successor cannot backdate an open predecessor across a consumed date; contiguous
  boundary, overlap, gap, and competing-successor races fail closed.
- [AC-FIN-5] Loan current-rate projection, sequential old/new histories, notice obligations,
  byte-stable activation replay, and immutable consumer snapshots remain one coherent rate decision.
- [AC-FIN-6] Ledger count/page/body truth is database-windowed and deterministic for mixed
  allocation/reversal histories at 1, 21, and 101 rows.
- [AC-FIN-7] Permanent tests use public fixture/owner seams, cover exact replay and denial edges, and
  the focused, twice-run PostgreSQL, reverse-consumer, migration, and full gates pass.

## Risk Level
High

## Done Checklist
- [ ] Execution plan and impact map written
- [ ] Failing public RED probes retained before implementation
- [ ] Code, migration, API contract, and owner seams implemented
- [ ] Exact acceptance IDs mapped in `review-closure-evidence.md`
- [ ] PostgreSQL acceptance passed twice
- [ ] Reverse consumers and full gates passed
- [ ] Risk/review evidence completed and commit delegated to the orchestrator
