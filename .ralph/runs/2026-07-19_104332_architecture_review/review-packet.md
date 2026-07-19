# Review Packet: 2026-07-19_104332_architecture_review

## Result
Ready for independent validation

## Slice
architecture-review

## Review Boundary

- Fixed point: successful architecture-review commit `eacf85e3`.
- Reviewed product slice: `547c6835` (`009L3`).
- `692589f5` retains only the candidate-hash proof; Ralph-infrastructure commit `755525c2` is not
  treated as a completed product slice.

## Standards

- **Medium judgment call:** `loan_account_360.list_accounts` materializes and deep-validates every
  eligible account before Python slicing, while `_database_coherent_candidates` reconstructs a
  partial copy of lifecycle/SAP/transfer invariants. The staff workspace repeats that full scan for
  each nominal account page. This weakens locality and selector ownership under codebase-design
  §§16/42 and makes evidence work scale with the entire portfolio. One-row ceilings cannot detect it.
- **Low judgment call:** the exact PostgreSQL label is an empty subclass of an already discovered
  race class, so the full suite runs the same observable tests twice rather than replacing the old
  surface under codebase-design §26.2. The “every governed tab” browser test opens only Loan Ledger
  and checks two more buttons, so its title overstates exercised tab bodies.

No hard Standards-axis violation was found; formatting, protected paths, migration sync, masking,
pending-only constraints, and use of the established `Tabs` component conform to documented rules.

## Spec

- **High:** requirement 3 did not replace parallel SAP record selection. The member facade selects
  the newest member request; the account facade independently selects an application-specific
  completion. A review-only public-facade probe proves that newer incoherent cross-application truth
  is rejected by the member owner while the account owner accepts the older decision, violating
  M07-FR-010 and the exact “reject identically” requirement.
- **Medium:** requirements 4/7 require bounded database pagination and populated 1/21/101 matrices.
  The implementation projects all eligible accounts, walks all account pages in the workspace, and
  then slices. Only one-row query ceilings exist.
- **Medium:** the full action-parity, SAP-component/consumer, exact transport/error, and opposite-
  order unit matrices required by requirement 7 are partial. `CR-012` correctly remains the separate
  owner of the final nine-state real-Django browser proof.

No scope creep was found. Pending-only posting, singular PostgreSQL assertions, masked SAP output,
S36 reachability, governed CFC admission, and the restored tab shell match their stated requirements.

Axis summary: Standards has 2 findings (worst: Medium selector locality/scalability); Spec has 3
findings (worst: High canonical SAP completion disagreement).

## Corrective Work

- Added `009L4-epic-009-canonical-read-and-bounded-pagination-closure` as one root-owner corrective.
  It is numeric, `Not Started`, depends on completed `009L3`, and owns one canonical SAP decision,
  bounded selectors, action/mutation matrices, 1/21/101 portfolios, and omitted unit/transport proof.
- Existing `CR-012` now depends on 009L4 and retains sole ownership of real-Django Epic 009 browser
  evidence. `010A` also waits on 009L4 and CR-012.
- Queue lint and 009L4 runtime-capability validation pass; no dependency is dangling or cyclic.

## Convergence Metrics

- Findings closed: 3
- New Critical: 0
- New High: 1
- New Medium: 2
- New Low: 1
- Corrective slices added: 1

This review closes scope-first count correctness, evidence-free `posted` acceptance, and the S42
layout regression. Corrective additions do not exceed closures, so the two-review root-boundary
escalation rule is not triggered.

## Traceability

- Functional spec M07-FR-010 requires confirmed SAP truth before disbursement; the current account
  facade accepts a decision the member facade rejects, verified by the retained failing review probe.
- 009L3 requirements 4/7 require bounded eligible pagination and 1/21/101 matrices; current list and
  workspace coordinators compose the whole portfolio before slicing, verified by static line evidence.
- A-135/M07-FR-009 remains honest: the database and current-success resolver accept one pending
  obligation only, and both retained PostgreSQL races assert it.
- M07-FR-001-010 and M08-FR-001-011 otherwise retain implemented owners or explicit A-135 governance;
  M07-FR-010 remains conditional on 009L4. `CONTEXT.md` remains truthful, no slice is `Blocked`, and
  no ADR is needed because the corrective restores existing contracts rather than choosing a new one.

## Verification

- Review-only probe: 1 test discovered, 1 intended failure reproducing cross-facade SAP disagreement.
- Retained 009L3 independent gates: complete backend coverage green; 349 frontend tests green;
  exact two-test PostgreSQL contract passed twice; exact two-test browser contract passed twice.
- Architecture-review docs checks: queue lint, runtime-capability validation, and `git diff --check`
  pass. Product gates were not repeated because production code is unchanged in this review.
- Evidence: `.ralph/runs/2026-07-19_104332_architecture_review/evidence/`.

## Recommended Next Action
Run independent architecture-review validation, then execute 009L4 before CR-012 and Epic 010.
