# Slice 008F2: Security-Instrument Boundary and PoA Lifecycle Closure

## Status
Complete

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Depends On
- 008G2

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Place the security package and Power of Attorney behind the source-defined security-instruments
boundary and make PoA preparation/activation a terminal, canonical-sanction maker-checker workflow.

## Source / Review References

- `docs/source/codebase-design.md` §§8.2, 15.1, and 36.1-36.2
- `docs/source/api-contracts.md` §§6-8 and 28.1-28.3
- `docs/source/data-model.md` §§17.1-17.2, 30, and 34
- `docs/source/auth-permissions.md` §§15.4-15.5, 18.1-18.2, 19.2-19.4, and 26.4
- `docs/source/functional-spec.md` M06-FR-007/M06-FR-008
- Epic 008 digest: V10 p.14 §4.3 and Deck p.7
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_185927_architecture_review`

## Concrete Requirements

1. Establish `security_instruments` as the deep owner of `SecurityPackage`, `PowerOfAttorney`,
   their selectors/modules/routes, and future SH-4/CDSL/cheque seams. Preserve existing table names,
   ids, protected relations, API URLs, and retained rows. Use staged migration state if necessary;
   do not duplicate live model ownership or make `legal_documents` depend back on security policy.
2. Create/read a package only for the approval owner's canonical latest-cycle frozen terminal
   sanction truth and the matching Stage-4 checklist/application scope. Mutable
   `application_status=approved_by_sanction` alone must create nothing. Preserve authority-first,
   nondisclosing unknown/wrong-stage/unrelated behavior.
3. Only Compliance may create or materially change draft preparation facts. A real draft change
   records that actor as the current maker under 008G2 semantics. Company Secretary may verify and
   activate only the exact retained draft; activation must not silently change purpose, parties,
   attorney, document, stamp, notary, or other maker-owned facts.
4. Activation is terminal in this slice. Compliance and Company Secretary cannot downgrade active
   to draft, erase verifier/effective/execution facts, or replace consumed evidence. `invoked` and
   `released` remain forbidden. Retain an immutable activation evidence snapshot containing exact
   document renderer/file, stamp/notary current maker/checker, borrower/nominee signature, PoA
   maker/checker, request/network/role/team identities.
5. Upstream correction must not leave an apparently active PoA backed by rewritten signatures or
   adverse stamp/notary truth. With no source-defined supersession path in this slice, fail the
   conflicting upstream mutation atomically and preserve the active activation ledger.
6. Resolve an active Company Secretary attorney through canonical active role membership, including
   governed secondary roles, rather than primary-role shape alone. Replace the over-broad global
   `not`/`never` purpose rejection with a bounded affirmative-authority decision that accepts
   unrelated lawful negative clauses and does not invent generated legal wording.
7. Replace manual `LoanDocument`/renderer-provenance construction with one genuine public sanctioned
   generation -> 008G2 maker/checker stamp/notary/signature -> PoA activation tracer. Add twice-run
   PostgreSQL changed activation/downgrade races; draft create/change races alone are insufficient.

## Test Cases

- Migration/state/table preservation and an import-dependency guard proving security ownership and
  no `legal_documents -> security_instruments` reverse policy dependency.
- Status-only fake sanction, stale-cycle sanction, unknown, wrong-stage, unrelated package, and
  canonical final-sanction create/read matrices.
- Compliance-only create/change, current-maker handoff, CS exact-draft activation, same-user/
  multi-role denial, checker-changed preparation denial, and active-to-draft zero-write conflict.
- Linked signature/stamp/notary post-activation mutation attempts fail atomically; exact activation
  replay remains zero-write and complete frozen evidence remains reviewable.
- Secondary-role attorney, affirmative purpose with unrelated negative wording, forbidden states,
  projection rollback, genuine public tracer, and twice-run PostgreSQL activation races.

## Evidence Required

Boundary/import proof, retained-table migration proof, backend RED/GREEN lifecycle matrices,
genuine public tracer, API examples, twice-run PostgreSQL races, and all gates.

## Risk Level
High

## Acceptance Criteria

- Security-package and PoA ownership follows the source architecture without data/API breakage.
- Only canonical sanctioned applications can own a package.
- PoA maker/checker and active-state evidence cannot be bypassed or downgraded.
- All configured gates pass.

## 008G2 Completion Sharpening (2026-07-14)

- Consume legal execution facts only through the retained legal selector: each current signature
  now carries the latest material `captured_by_user_id`, while verified tri-party evidence freezes
  consumed ids/names/makers/times and blocks later capture mutation.
- Stamp/notary/signature rows migrated from truthful non-null makers remain current; only historical
  null-maker rows carry `legacy_maker_attribution=true` and are ineligible for changed or new PoA
  activation truth. Do not treat the legacy flag as remediation authority.
- Keep security HTTP adapters above the domain seam established by `request_contracts`; permission
  must be checked before transport parsing, and activation must return a durable §6.3 workflow
  action identity on success/replay.
