# Review Packet: 2026-07-16_023011_architecture_review

## Result

Success — independent architecture review complete; corrective work is queued.

## Slice

architecture-review

## Review Boundary

- Fixed point: `e1e3c665a969bfc0993140100ddab6dcb1220ca8`
- Reviewed product commits: `6d389b43` (008K5), `7dfea592` (008L4), `0eae53d7`
  (CR-008), and `74440c6d` (008M)
- Ancillary commits examined separately: `bf78775b` and `88072f45`
- Standards and Spec passes were performed independently and aggregated without collapsing the two
  axes.

## Findings

Standards: 1 Critical, 3 High, 1 Medium.

- 008M was compressed to fit the 2,000-line gate, leaving production and test modules densely
  minified and defeating the maintainability purpose of the safety limit.
- 008M exposes a private action shape, can render an error alongside a false all-complete state, and
  lacks adequate staff signed-download security coverage.
- Stage-4 bank decisions accept stale approval authority after the latest ApprovalCase is no longer
  terminal.

Spec: 3 High, 2 Medium.

- S28-S34 staff actions are dead or missing despite being projected; the required trusted-browser
  screenshots are absent.
- S26 queue truth and S35 audit behavior are incomplete.
- Deficiency response state defaults to `responded` when its workflow evidence is missing, and the
  document-pack modal hides mutation controls when a download exists.

The full newest-first record is in `docs/working/REVIEW_FINDINGS.md`.

## Executable Evidence

Two focused probes were expected to fail and did:

- A bank verification decision returned HTTP 200 and created a successor ledger after the latest
  sanction ApprovalCase had been rejected; the expected fail-closed result was HTTP 403.
- A deficiency response continued to serialize as `responded` after its response WorkflowEvent was
  deleted.

Probe details are in `evidence/terminal-logs/review-probes.md`.

## Corrective Queue

- 008L5 closes current Stage-4 sanction authority and coherent deficiency-response evidence.
- 008M2 restores a readable deep module, the canonical action contract, reachable S28-S34 actions,
  complete S26/S35 truth, download security tests, and the missing browser contract/screenshots.
- 009B was sharpened from the already-open Epic 009 sources for SAP customer-code completion and
  reuse, including exact permissions, validation, idempotency, and race behavior.

No ADR was created because the source documents already decide the affected contracts. No slice was
blocked.

## Verification

- Slice queue lint: pass
- Capability validation for 008L5 and 008M2: pass
- State JSON validation: pass
- `git diff --check`: pass
- Protected-path scan: pass
- Frontend build, typecheck, lint: pass
- Frontend tests: 311 passed
- Backend Django check and migration drift check: pass
- Backend tests: 905 passed, 46 skipped
- Backend coverage: 91% total; required threshold 85%

## Recommended Next Action

Run 008L5, then 008M2. Resume Epic 009 with 009A and the sharpened 009B only after both corrective
slices pass.
