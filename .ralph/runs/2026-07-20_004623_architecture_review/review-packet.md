# Review Packet: 2026-07-20_004623_architecture_review

## Result
Ready for independent validation

## Slice
architecture-review

## Boundary

- Fixed point: `0b5be35c`, the post-Epic-009-finalizer semantic-review baseline.
- Product commits: `dc666672` (010A), `41f3034d` (010B), `bdae40f4` (010C), and
  `6883816b` (010D).
- Diff: `git diff 0b5be35c...HEAD`; mechanical run/state/progress/handoff changes were evidence,
  not independently ranked product behavior.

## Standards

- **High — allocation command admission violates critical-action contracts.** The allocation view
  omits the source-required `Idempotency-Key`; replay ignores changed remarks; mandatory remarks are
  validated then discarded; and the source-authorised Accounts Head lacks default capture/allocation
  grants. This conflicts with API §45.1, the working 010B/010C contracts, and critical-action audit
  evidence requirements.
- **High — statement linkage has two unconstrained truths.** A raw unique UUID on `Repayment` and a
  separate OneToOne relationship on `BankStatementLine` can be orphaned or disagree. This conflicts
  with data-model §19.5's relationship, immutable evidence direction, and the working contract's
  “links each side once” promise.
- **Medium — owner/test seams are shallow.** Repayment capture creates a communications-owned
  Notification directly, servicing modules duplicate low-level AuditLog construction, and all five
  new test modules instantiate other TestCase classes/private helpers through deep fixture chains.
- Clean areas: versioned response/error/list envelopes remain central; views are thin; Decimal and
  database constraints are substantive; financial mutations use atomic row locks; document storage
  uses the restricted central facade; and PostgreSQL contention tests assert one retained effect.

## Spec

- **High — ordinary allocation accepts ineligible financial effects.** Public probes show that a
  receipt with pending SAP posting and a posted receipt carrying `manual_match_exception` both reduce
  balances through ordinary `/allocate/`. This contradicts M09-FR-010/flow §27 ordering and 010D's
  explicit deferral of manual exception allocation to 010C2 approval. Schedule capacity can also be
  smaller than the account allocation while the account/ledger still report the full reduction.
- **High — the statement evidence owner accepts false or under-authorised truth.** Public probes show
  arbitrary nonexistent line UUIDs are retained and import-only, out-of-scope automatic matches
  succeed. The generic narration predicate also implements M09-FR-007's subsidiary borrower **and**
  application requirement as an OR. The raw collection-account field can retain/return a sensitive
  bank value without the central encryption/masking seam.
- **Medium — ledger pagination is not row-bounded.** The implementation materializes all repayment
  ledger entries before Python slicing; the query-ceiling test has only one ledger row and therefore
  cannot prove the slice's bounded-pagination requirement.
- No material scope creep was found. M09-FR-008's unmatched queue, 010A read contracts, 010B capture
  duplicate races, 010C arithmetic/one-effect contention, and 010D match-only zero-financial-write
  assertions are real and substantive.

## Traceability

- Functional spec M09-FR-010 and user flow §27 say balances update after posting; the public pending-
  SAP probe receives `200` and reduces principal, so existing Not Started slice 010C2 now owns the
  admission/idempotency/schedule/reason/role regression contract.
- Slice 010D and M09-FR-009 reserve manual exception allocation for terminal approval in 010C2; the
  posted manual-exception probe receives `200` without approval and is mapped to the same root.
- Data model §19.5 requires a statement-line relationship and 010D requires one counterpart; the
  orphan and import-scope probes both fail, so grouped corrective 010D2 owns one canonical link,
  permission/scope parity, M09-FR-007's AND rule, migration safety, and privacy.
- No epic completed in the four-slice interval, so no completed-epic functional-ID audit was due.
  The current Epic 010 spot-check covers M09-FR-007–011; M09-FR-008 is implemented, while the two
  High roots keep M09-FR-007/009/010/011 conditional on corrective closure.

## Review Evidence

- Both review-only test programs used the required backend interpreter, created isolated Django test
  databases, and failed exactly four public assertions: two allocation-admission and two statement-
  evidence assertions. No production file was changed.
- Reproducers and executable probes are retained under
  `.ralph/runs/2026-07-20_004623_architecture_review/evidence/review-probes/`.
- Independent Standards and Spec passes reviewed the same fixed diff in parallel and agreed on the
  allocation and statement-evidence roots; their clean-area observations are retained above.
- `CONTEXT.md` now truthfully records Epic 009 closure and active Epic 010 servicing. The Epic 010
  digest retains the missing posting-order, canonical-link, and subsidiary AND facts. State reports
  no Blocked slices, so no stale prerequisite needed re-parking. No ADR was added: both correctives
  restore binding source/owner contracts rather than choose a new durable architecture.

## Convergence Metrics
- Findings closed: 0
- New Critical: 0
- New High: 2
- New Medium: 2
- New Low: 0
- Corrective slices added: 1
- Existing corrective slice: 010C2

The prior review reported one closure and no corrective addition; this review adds one grouped
statement-owner corrective and maps the allocation root to existing work. Across the two reviews,
additions do not exceed closures, so no further root-boundary recommendation is required.

## Finding Closure Manifest
| Finding ID | Root ID | Severity | Disposition | Reproducer | Corrective Slice | Closure Evidence |
|---|---|---|---|---|---|---|
| AR-010-ALLOCATION-001 | ROOT-010-ALLOCATION-ADMISSION | High | New | .ralph/runs/2026-07-20_004623_architecture_review/evidence/review-probes/allocation-admission.log | 010C2 | - |
| AR-010-STATEMENT-001 | ROOT-010-STATEMENT-EVIDENCE | High | New | .ralph/runs/2026-07-20_004623_architecture_review/evidence/review-probes/statement-evidence-boundary.log | 010D2 | - |
| AR-010-LEDGER-001 | ROOT-010-LEDGER-PAGINATION | Medium | New | .ralph/runs/2026-07-20_004623_architecture_review/evidence/review-probes/ledger-pagination-inspection.log | - | - |
| AR-010-SERVICING-SEAM-001 | ROOT-010-SERVICING-OWNER-SEAM | Medium | New | .ralph/runs/2026-07-20_004623_architecture_review/evidence/review-probes/servicing-seam-inspection.log | - | - |

## Recommended Next Action
Run independent architecture-review scope, semantic-manifest, queue, and artifact validation. If it
passes, execute existing 010C2, then new 010D2, before 010E resumes Epic 010 delivery.
