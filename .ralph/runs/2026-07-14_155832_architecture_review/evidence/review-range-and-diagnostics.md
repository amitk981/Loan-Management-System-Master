# Review Range and Diagnostics

## Pinned range

- Fixed point: `329c3b03e5e25535e84f7469899cac063e5e9404`
- Reviewed head: `092faf7a`
- Diff: `git diff 329c3b03...092faf7a`
- Commits:
  - `a2e541bf` — 008B4 renderer provenance/replay closure
  - `b80c7a19` — 008C2 checklist lifecycle/authority closure
  - `94b3fd1b` — 008D stamp-duty/notarisation tracking
  - `092faf7a` — 008E signature mismatch workflow

## Reproducible diagnostic facts

- `signatures.record` checks only for an existing resolution before permitting a changed capture.
  A Compliance actor can change the same unresolved borrower row from `mismatch` to `signed`, which
  removes the application-owned mismatch fact without Company Secretary resolution evidence.
- `stamp_notary` restricts only `adequate` and `completed` to Company Secretary. Compliance can
  persist the verification outcomes `insufficient` and `rejected`, and can change a verifier-owned
  row back to preparer state while the linked checklist item is incomplete.
- `resolve_mismatch` retrieves a raw signature id before Stage-4 parent scope; absent ids become 404
  while existing wrong-stage/inaccessible ids become 403.
- The 008E suite has no `TransactionTestCase`, thread/barrier, or concurrent capture/resolution
  assertion despite the slice's explicit concurrency acceptance case.
- Stage-4 application/category/role evidence policy lives in the lower-level documents app, simple
  HTTP validation is duplicated in business modules, and §26.8 does not return §6.3 action fields.

## Independent regression result

A temporary module outside the worktree inherited the committed API fixtures and added two expected
invariants. Both failed against reviewed HEAD:

- unresolved mismatch capture overwrite: expected HTTP 409, received HTTP 200 with `signed`;
- Compliance adverse stamp outcome: expected HTTP 403, received HTTP 200 with `insufficient`.

The exact command and failure excerpts are saved in
`evidence/terminal-logs/01-independent-regressions-red.txt`. No production or repository test file
was modified.

## Queue outcome

- Added `008D2-stamp-notary-verification-authority-closure` after completed 008D.
- Added `008E2-signature-identity-mismatch-lifecycle-closure`, dependent on 008D2 and completed 008E.
- Changed 008F to depend on 008E2 and sharpened 008F/008G around the canonical signature seam and a
  genuine generated-document tracer.
- No slice is `Blocked`; no stale prerequisite status required changing.
