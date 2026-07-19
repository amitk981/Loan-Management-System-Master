# Review Packet: 2026-07-19_123045_architecture_review

## Result
Ready for independent validation

## Slice
architecture-review

## Review Boundary

- Fixed point: successful architecture-review commit `f8eb78be`.
- Reviewed product commit: `3b31edc4` (`009L4`).
- The normal run and two repairs retained in that commit are one completed product-slice boundary;
  mechanical state/run artifacts were excluded from the product critique.

## Standards

- **High hard violation:** the new “exact” count selectors are broader than the owner-level
  reconciliation used to project rows. Loan Account, S37, and CFC branches can therefore report
  stale/incoherent identities in totals and offsets after suppressing their bodies, contrary to
  `CONTEXT.md` and codebase-design §42's selector, nondisclosure, and blocked-path rules.
- **Medium architecture drift:** `loan_account_lifecycle.py` now contains two substantially
  duplicated scalar validators for immutable creation evidence. This weakens the central owner
  boundary required by codebase-design §§26/42.
- **Low test-quality concern:** the 101-row fixture copies Django private `_state`/ledger records,
  and the MP14 “surrounding list order” case only swaps one explicit-id prop. The assertions are real
  for narrower behavior but do not prove the interfaces their names imply.

The independent Standards pass excluded tooling-enforced formatting and found no new styling,
dependency, migration, masking, or protected-path violation.

## Spec

- **High:** 009L4 requirements 2-3 require exact eligible identities before count and offset. Four
  retained probes drift creation roles, SAP completion digest, SAP send checksum, and initiation
  evidence; every projector returns no body while every envelope still reports `total_count: 1`.
  Four-row overscan cannot repair false candidates before the page offset.
- **High:** requirement 1 requires every consumer to validate one member/application/customer-code
  edge. The member portal checks only member/status, so a coherent current completion for another
  application marks the requested application's SAP stage complete; a fifth probe reproduces it.
- **Medium carried forward:** staff-workspace 1/21/101 portfolios, more-than-four drift runs, the
  full consumer/action/mutation matrix, exact transport bytes, and independent 400/403/409 surfaces
  remain absent. The prior duplicate PostgreSQL discovery Low also remains open.

No scope creep was found. The exact prior member/account facade divergence and full-portfolio Python
page walk are closed; pending-only A-135 truth, masking, and the restored frontend shell are retained.

Axis summary: Standards has 3 findings (worst: High count/selector disagreement); Spec has 3 active
findings (worst: High exact pagination and cross-application portal truth).

## Corrective Work

- Added `009L5-epic-009-exact-selector-and-consumer-parity-closure` as one numeric `Not Started`
  root corrective depending on completed 009L4.
- 009L5 owns exact count/projection identity parity, the portal canonical application edge, the
  duplicated lifecycle validator, all five review probes, and the retained executable matrices.
- Existing `CR-012` and `010A` now depend on 009L5. CR-012 retains sole ownership of hosted nine-state
  Epic 009 browser/image-hash evidence; 010A remains the first servicing slice.
- Queue lint passes with no dangling reference, ambiguity, stuck chain, or dependency cycle.

## Convergence Metrics

- Findings closed: 2
- New Critical: 0
- New High: 2
- New Medium: 1
- New Low: 1
- Corrective slices added: 1

The previous and current reviews each added one corrective while closing three and two findings,
respectively. Additions do not exceed closures across the two-review window, so no further
root-boundary escalation is triggered.

## Traceability

- Functional spec M07-FR-010 requires confirmed SAP truth before disbursement; 009L4 requirement 1
  requires the exact application edge across all consumers. The portal probe proves another
  application's current completion is accepted for the requested stage.
- 009L4 requirements 2-3 require exact eligible totals and bounded database pagination. Four count
  probes prove broader candidate filters disagree with their owner-level projectors.
- M07-FR-001-009 and M08-FR-001-011 retain implemented owners or explicit A-135 pending governance;
  M07-FR-010 remains conditional on 009L5. `CONTEXT.md` remains truthful, no slice is `Blocked`, and
  no ADR is needed because the corrective restores existing contracts rather than choosing a new one.

## Verification

- Review boundary resolves and contains exactly one product commit after `f8eb78be`.
- Review-only probes: 5 discovered across focused commands, 5 intended failures reproducing the
  selector/count and portal application-edge defects.
- Retained 009L4 independent gates: 1,288 backend tests under coverage, 349 frontend tests, frontend
  build/typecheck/lint, Django check, migration sync, and focused repair evidence passed.
- Architecture-review checks: queue lint and documentation `git diff --check` pass. Product gates
  were not repeated because production code is unchanged in this review.
- Evidence: `.ralph/runs/2026-07-19_123045_architecture_review/evidence/`.

## Recommended Next Action
Run independent architecture-review validation, then execute 009L5 before CR-012 and Epic 010.
