# Execution Plan

Selected slice: `006X3-credit-visual-and-real-browser-closure`

## Repair diagnosis

- Use the twice-reproduced trusted-browser failures from `2026-07-11_234515_repair` as the
  red-capable feedback loop: the empty matrix state never appears and the real-role navigation
  never reaches the Appraisal Workbench.
- Inspect the routed shell, initial four-read semantics, and the prior test's response fixtures to
  distinguish a bad empty response, a wrong navigation control, and a fatal forbidden read.
- Treat the previous 6,498-line diff as a separate hard failure. Rebuild the slice narrowly from
  the current clean integration state and remain under 2,000 changed lines.

## Implementation

1. Consolidate the legacy visual and fully mocked Epic 006 browser files into the one declared
   `e2e/epic-006-closure.e2e.spec.ts` contract, with exactly two collectable tests and the twenty
   declared screenshot names.
2. Preserve the approved workbench composition. Correct only slice-owned reachability defects
   demonstrated by the browser feedback loop; do not add client-owned financial, permission, or
   workflow decisions.
3. Build deterministic visual response fixtures around the real authenticated container and its
   canonical four reads. Add committed Chromium baselines for the eighteen `appraisal-*` states.
4. Add the smallest debug/E2E-guarded synthetic setup needed for a real Django, real-login,
   Deputy Manager Finance/Credit Manager path. For backend setup behavior, save failing-first and
   green focused test evidence before implementation.
5. Assert exact six-field resource actions before cross-role mutations, exact writable appraisal
   PATCH keys, one four-read refresh per successful write, no refresh on `409`, shared server IDs,
   metadata-only evidence, and exactly one pending sanction case after repeat submission.
6. Remove or narrow the old fully mocked tracer so it cannot be presented as real-backend proof;
   preserve the authoritative backend API tracer.

## Verification and handoff

- Run Playwright collection and the focused contract locally. If Chromium launch is denied by the
  sandbox, save the honest launch log; the orchestrator's two trusted runs remain authoritative.
- Run frontend lint, typecheck, unit tests, and build. Run backend check, migration sync, focused
  tests, and full coverage only with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Save self-contained evidence, `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and
  `final-summary.md`; update slice status, Ralph state/progress, handoff, and Epic 006 digest only
  after local gates pass.
- Sharpen the next one or two `Not Started` slices using already-opened digest/source material.
