# Review Packet: 2026-07-19_180917_architecture_review

## Result
Ready for independent validation

## Slice
architecture-review

## Review Boundary

- Last successful architecture review: `399fb954`
- Product slice: `50d91369` (009L6)
- Product change request: `fe4b0ecb` (CR-012)
- Excluded infrastructure-only boundary: `d17954b8`

## Standards

- High: 009L6 lets `finance.disbursement.initiate` replace the binding
  `finance.loan_account.read` grant and gives Senior Finance portfolio scope on public list/detail
  reads, contrary to auth §34.7, `API_CONTRACTS.md`, and codebase-design §42.
- High retained root: SAP completion/S37/CFC database selectors still copy subsets of stricter
  scalar owners. Send/file/actor/frozen-owner drift can be counted and then dropped, contrary to
  codebase-design §§26/42 and the 009L6 exact-owner contract.
- Medium: CR-012's guarded runtime seed imports a `TestCase` and private test helpers; ordinary
  `npm run e2e` collects Epic 009 while choosing the non-Epic-009 seed family.
- Low: JSON selector helpers and private fixture composition remain duplicated across owners.

## Spec

- 009L6 requirements 1-4 remain partial: three public probes prove count/projector disagreement
  and permission/scope widening.
- Requirement 5's five-branch 1/21/101, adjacent-drift, action/mutation, consumer, query-ceiling,
  and error matrix remains materially incomplete.
- CR-012 passes its targeted spec: real form authentication and owned Django endpoints, nine
  state-specific captures, two verified manifests, and nine distinct hashes in each run.

## Convergence Metrics

- Findings closed: 3
- New Critical: 0
- New High: 1
- New Medium: 2
- New Low: 1
- Corrective slices added: 1

## Corrective Action

Added numeric `Not Started` slice `009L7-epic-009-read-boundary-convergence-closure`, depending on
009L6 and CR-012. It is the one final grouped repair admitted for this corrective cycle and owns the
retained selector root, new authorization regression, carried matrix, and CR-012 fixture/config
boundary. `010A` now depends on 009L7. Another recurrence of this root after 009L7 must fail closed.

## Evidence

- `evidence/standards-review.md` and `evidence/spec-review.md`: independent review axes.
- `evidence/review-probes/test_009l6_closure_probes.py`: three public contract probes.
- `evidence/terminal-logs/009l6-closure-probes.log`: all three probes fail on the intended
  assertions (`(1, [])` twice; public `200` instead of `403`).
- `evidence/terminal-logs/009l6-retained-focused-green.log`: 14 retained closure tests pass.
- `evidence/terminal-logs/cr012-retained-browser-evidence.log`: both nine-file manifests match and
  each has nine distinct hashes.
- `evidence/terminal-logs/playwright-full-collection-with-evidence.log`: ordinary Playwright
  collection includes the Epic 009 spec among 35 tests, supporting the seed-selection finding.
- `evidence/terminal-logs/review-validation.log`: exact result/metrics, dependency resolution,
  downstream ordering, blocked-slice audit, and whitespace checks pass.

## Traceability

The source contract says `GET /loan-accounts/` requires `finance.loan_account.read`
(`auth-permissions.md` §34.7) and Senior Finance is scoped to SAP/disbursement-linked accounts
(§19.3); the current public API returns a portfolio row with initiation permission alone, verified
by the review probe. 009L6 says every selected identity must share one complete owner decision; two
additional probes show send/file drift still reports a stale count before scalar projection. CR-012
says the nine real-Django states must be asserted, distinct, and rerun twice; the retained PNGs and
manifests verify that contract exactly.

## Recommended Next Action
Independently validate and merge this documentation-only review, then execute 009L7 before Epic 010.
