# Review Packet: 2026-07-14_185927_architecture_review

## Result

Success

## Slice and Range

Architecture review of `git diff 7e119610...12e2dea4`, covering completed slices 008D2, 008E2,
008F, and 008G. No production code changed.

## Standards

The isolated Standards pass found security package/PoA ownership in `legal_documents` rather than
the source-defined `security_instruments` app, domain modules importing HTTP request serializers,
duplicated permission/evidence seams, and nonstandard §26.6/mismatch error responses. 008G2 closes
shared legal evidence/action seams; 008F2 establishes the security owner before SH-4/CDSL.

## Spec

The isolated Spec pass found that later material editors retain the first maker id and can then act
as checker. Root integration additionally reproduced HTTP 200 for fake-status package creation,
active-PoA downgrade by Compliance, and post-verification borrower-signature rewrite. 008G had no
retained PostgreSQL execution and F/G's claimed public tracers manually inserted provenance rows.

## Traceability and Architecture Outcome

- Auth §§15.4-15.5/18 require actual maker/checker separation; 008G2 tracks the latest material
  maker and database-backs positive/adverse evidence integrity.
- API §§6-8/26 require action/error contracts and atomic legal workflows; 008G2 closes transport,
  §26.6 response, mismatch error, consumed-signature, public generation, and race gaps.
- Codebase-design §§8.2/36.2 and data-model §17 assign PoA/security to `security_instruments`; 008F2
  moves ownership without changing tables, ids, retained rows, or v1 routes.
- M06-FR-007/008/009 remain partial until F2/G2; M06-FR-016/017 retain substantive E2 identity and
  resolution behavior but remain current-maker partial until G2. A-101 is unchanged.

## Corrective Queue

1. 008G2 stage-4 maker and verification contract closure — depends on completed 008G.
2. 008F2 security-instrument boundary and PoA lifecycle closure — depends on 008G2.
3. 008H now depends on 008F2; 008H/008I declare and sharpen their PostgreSQL acceptance.

No Blocked slice is stale. No ADR was required because existing source documents already decide
ownership, maker-checker, action, and integrity rules.

## Validation

- Frontend build, typecheck, lint, and 293/293 tests pass.
- Django check and migration sync pass.
- Backend 803/803 tests pass with 29 expected PostgreSQL-only skips.
- Coverage is 93%, exceeding the 85% floor.
- Queue drain, state JSON, `git diff --check`, status-transition, and protected-path checks pass.

## Recommended Next Action

Run 008G2, then 008F2. Continue to 008H only after both corrections pass.
