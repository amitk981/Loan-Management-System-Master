# Review Packet: 2026-07-13_004501_architecture_review

## Result

Complete; independent findings and corrective slices are ready for Ralph validation.

## Slice

architecture-review

## Review Boundary

- Fixed point: `540eef47f5bdec32abf29de0ea629e55c6600d02`
- Commits: 006X9 `8bb60b6`, 006Y14 `47c2cc4`, 006Z6 `0f13c65`, 006Z2 `63136ff`
- Diff: `git diff 540eef4...HEAD`

## Findings

- Standards: 2 High and 2 Medium. Worst: borrower-limit orchestration is duplicated outside credit,
  and caller-controlled member authority returns divergent Registry/active-status decisions.
- Spec: 3 High and 2 Medium. Worst: documented recent-member relaxation is unreachable, promised
  evidence-mutation races are absent, and unchanged verified portal authority expires next day.
- Credit/witness matrices retain paired/static or omitted cases. Portal submit/refetch/error/browser
  proof is partial. No material scope creep was accepted.

## Corrective Queue

- 006X10: executable, one-row-per-selection credit object-scope completeness.
- 006Y15: observable two-kind witness matrix and in-scope missing-parent semantics.
- 006Z7: reachable source relaxation, one member authority, and evidence-mutation races.
- 006Z8: stored-date provenance, credit-owned borrower projection, and real interaction/browser proof.

## Traceability

The source says BR-003/005 allow evidenced recent-member relaxation; the code rejects non-active
membership before that branch; 006Z7 verifies the corrected route with inactive/recent-member and
PostgreSQL evidence-race tests. Codebase-design says financial rules stay local to their deep module;
the portal adapter currently orchestrates the limit; 006Z8 verifies delegation, next-day provenance,
submit errors, canonical refetch, redaction, and trusted screenshots. The completed slices say each
matrix row is independently selectable; paired helpers/static names do not prove that; 006X10 and
006Y15 verify each public row in isolation.

M04-FR-001/002 remain deferred to 012EA by A-053; M04-FR-003 remains under A-054. M04-FR-004..011
retain substantive behavior subject to 006X10/006Z8 proof. M02-FR-004..006 and BR-003..007 remain
partial pending 006Z7. Existing source documents decide all durable directions, so no ADR was needed.

## Validation

Queue/protected/diff checks pass. Frontend build/typecheck/lint and 204 tests pass. Backend check,
migration sync, 478 tests (8 expected skips), and 93% coverage pass.

## Recommended Next Action

Run independent Ralph validation, then execute 006X10.
