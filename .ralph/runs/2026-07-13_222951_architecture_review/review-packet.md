# Review Packet: 2026-07-13_222951_architecture_review

## Result
Complete; findings are recorded, 007H3 is queued, and configured gates pass.

## Slice
architecture-review

## Review Window

`c843ea8...5ea122b`: 007F2, CR-004, 007G2, and 007H2.

## Standards

- High: canonical frozen-case validity still compares case provenance with the mutable live
  appraisal snapshot. A live edit makes case detail disappear while the stored projection remains
  true; 007H2 decision/register then disagree with detail.
- Low judgment: valid document sensitivities share the source-named legal audience because source
  auth defines no finer role/sensitivity pairs; A-085 records the decision rather than inventing a
  compliance matrix.
- Low judgment: the full exception tracer has real assertions but weak failure locality; 007H3 will
  split the scope/parity cases while retaining one end-to-end proof.

## Spec

- High: 007F2 requirement 4's frozen-history claim is false at the public HTTP seam, and 007H2
  requirement 5's coherent-reader parity is partial. 007H3 owns both.
- High evidence gap: CR-004 is Complete without repository evidence for its explicit hosted
  staging/PR-green criterion. Local code-side acceptance is substantive; external confirmation is
  still required.
- Medium judgment: 007G2 has no valid-but-role-disallowed sensitivity test because source provides
  no finer matrix; its exact legal audience/application/workflow/permission boundary remains tested.

No material scope creep was found. M05-FR-003/006/009/012 are functionally substantive; 007H3
closes historical ownership and cross-endpoint consistency.

## Corrective Ownership

- Created `007H3-frozen-case-provenance-and-read-scope-parity-closure`.
- Added 007H3 as a 007I dependency and sharpened old/new-cycle UI acceptance.
- Sharpened 007J to exclude unsupported borrower use of internal §25.8; A-089 owns the future
  borrower-safe outcome projection.
- No ADR: existing source and 007F2 already decide frozen ownership.

## Validation

- Two public HTTP diagnostic probes reproduce 200→404 frozen-history loss and terminal
  `(404 detail, 200 decision, 200 register, count 1)` split authority.
- Frontend build/typecheck/lint and 208 tests pass.
- Backend check/migration sync and 677 tests pass with 19 expected SQLite skips; coverage is 93%.
- No production/protected/source path changed; no Blocked slice is stale; CONTEXT remains truthful.

## Recommended Next Action

Run 007H3, then 007I. Confirm CR-004's hosted check before promoting staging.
