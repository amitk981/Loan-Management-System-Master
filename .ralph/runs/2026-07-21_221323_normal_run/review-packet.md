# Review Packet: 2026-07-21_221323_normal_run

## Result
Ready for independent validation

## Slice
010N4-global-search-sensitive-authority-closure

## Outcome

- Replaced aggregate-owned cross-domain model queries with public member/bank, application, account/
  repayment, document, audit, SAP, and security-instrument search facades.
- Enforced blank-cheque, SH-4, CDSL, SAP, bank-suffix, PAN, and Aadhaar input authority before an
  owner/member identity can enter any group, count, or action projection.
- Applied application/account object scope before matching, ordering, the 100-result cap, counts, and
  pagination, while allowing each group to search its own permitted borrower/reference fields.
- Added five-minute actor-bound opaque continuations and cleared raw query values from the Header,
  App handoff, search form, and completed request state before any pagination request.
- Preserved the existing frontend visual system and grouped card/action contract without new styling.

## Acceptance Review

- AC-E10-S1: the permanent CFO denial and real authorised cheque regressions prove canonical security
  authority, while PAN/Aadhaar, SAP, bank, group, and action tests prove nondisclosing denial.
- AC-E10-S2: the application test retains one older authorised result behind 100 newer denied rows
  with no member group, proving independent authority and scope-before-cap/count/page.
- AC-E10-S3: backend continuation tests prove raw-sensitive-free replay; frontend RED/GREEN tests
  prove the textbox and parent handoff clear while the next page sends only the opaque token.
- AC-E10-S4: 19 backend tests cover the input/group/action matrix, 1/20/21/100/101 boundaries,
  wildcard/continuation errors, real restricted-owner acceptance, and representative index plans.

## Traceability

The source says S02 supports the named borrower, application, account, SAP, security, bank, and
identity inputs but must return only records inside the actor's authorised role scope
(`screen-spec.md` S02 and §4.4). It classifies PAN, Aadhaar, bank, cheque, BO-account, and security
evidence as sensitive and requires explicit permission plus object access (`auth-permissions.md`
§§21 and 22.1). The code now delegates those inputs to domain-owned facades, applies owner scope
before caps/counts, and uses actor-bound opaque continuation after the first POST. This is verified
by `GlobalSearchApiTests`, `GlobalSearchResults.test.tsx`, and `Header.search.test.tsx`.

## Two-Axis Review

- Standards review: no hard repository-standard violations were found. The compatibility-only
  `BlankDatedCheque` alias in the coordinator is retained solely so the immutable original review
  probe can patch its historical seam; production search never queries through that alias.
- Spec review initially found sensitive-input fallthrough, continuation page-size reset, and an
  incomplete real-record/denial/boundary matrix. All three were corrected before validation with
  sensitive-input classification, token-retained page size, real cheque/CDSL/SH-4 fixtures, added
  denial/action tests, and the shared six-group 1/20/21/100/101 pagination contract.
- Scope review found no unrelated product changes or new visual styling.

## Evidence

- `review-closure-evidence.md`
- `evidence/terminal-logs/original-reproducer-replay.log`
- `evidence/terminal-logs/global-search-authority-red.log`
- `evidence/terminal-logs/global-search-authority-green.log`
- `evidence/terminal-logs/global-search-acceptance-matrix.log`
- `evidence/terminal-logs/global-search-client-clearing-red.log`
- `evidence/terminal-logs/global-search-client-clearing-green.log`
- `evidence/terminal-logs/frontend-tests.log`
- `evidence/terminal-logs/frontend-typecheck.log`
- `evidence/terminal-logs/frontend-lint.log`
- `evidence/terminal-logs/frontend-build.log`
- `evidence/terminal-logs/backend-check.log`
- `evidence/terminal-logs/backend-migrations-check.log`

## Recommended Next Action

Run Ralph's independent High-risk complete backend coverage, frontend, artifact, closure, and
protected-path validation. The orchestrator alone may update status/state and commit the slice.
