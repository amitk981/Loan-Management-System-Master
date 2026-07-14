# Review Packet: 2026-07-14_234031_architecture_review

## Result

Success

## Slice and Range

Architecture review of `git diff e046a9d3...bacc285d`, covering completed slices 008G2, 008F2,
008H, and 008I. No production code changed.

## Standards

The isolated Standards pass found three High and one Medium issue. `security_instruments` uses a
PoA forwarding shell and imports legal/approval owners in the source-forbidden direction; reversible
BO protection and reveal policy bypass the central encryption/sensitive-access owners; package
reads omit source-authorised roles; and repeated ledger code/races do not always prove exact winner
and loser identities. The codebase-design deep-module vocabulary drove the I2/I3/I4 seam boundaries.

## Spec

The isolated Spec pass found three High and one Medium issue. A public-path regression activated a
PoA with an otherwise adequate ₹1 stamp despite M06-FR-008's exact ₹500 rule. A second public-path
regression showed a source-valid pending CDSL request with null evidence raises `AttributeError`.
The implemented owner/sensitive seams contradict their slice contracts, and complete changed-
payload race proof remains partial.

## Traceability and Architecture Outcome

- Codebase-design §§28.1/36.2 require real security ownership, not a pass-through/inverse import.
- Auth §§12.8/14.1/19.2-19.4 require canonically scoped masked reads for Credit, finance approver,
  director, and auditor roles without granting mutation/reveal/download.
- Functional M06-FR-008 and V10 p.14 §4.3 require exactly ₹500 plus notarisation for PoA.
- Data-model §17.4 makes pending CDSL evidence nullable; terminal acceptance still requires it.
- Codebase-design §§9.4/39 require independently keyed/versioned central encryption and sensitive
  access. M06-FR-007/008 and security reads remain partial until I2; M06-FR-010/011/012 remain
  partial across I3/I4. No epic completed.

## Corrective Queue

1. 008I2 — move real PoA ownership; enforce exact ₹500; restore the source read matrix.
2. 008I3 — restore legal/security dependency direction and complete ledger/race evidence.
3. 008I4 — centralise encryption/reveal and restore nullable pending CDSL evidence.
4. 008J now waits for I4; 008K and 012E3 were sharpened against the corrected seams.

No Blocked slice is stale. No ADR was required because existing source documents already decide
the relevant ownership, role, nullability, stamp, and encryption boundaries.

## Validation

- Both independent review reports and both expected-failing regression reproductions are retained.
- Frontend build, typecheck, lint, and 293/293 tests pass.
- Django check and migration sync pass.
- Backend 826/826 tests pass with 36 expected PostgreSQL-only skips.
- Coverage is 92%, exceeding the 85% floor.
- Queue drain, capability vocabulary, JSON, `git diff --check`, diff-limit, and protected-path
  checks pass.

## Recommended Next Action

Run 008I2, then 008I3, then 008I4. Do not start 008J first.
