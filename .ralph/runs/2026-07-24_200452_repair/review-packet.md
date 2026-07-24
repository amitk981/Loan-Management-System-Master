# Review Packet: 2026-07-24_200452_repair

## Result
Ready for independent validation

## Slice
012F2-performance-readiness-evidence

## Demonstrated Failure

The prior trusted validator's real-browser run reached the populated Credit Manager dashboard in
2.2–2.6 seconds but failed both repetitions because the spec expected exactly one dashboard request
and React development Strict Mode produced two. Screenshot/manifests were consequently incomplete.

## Bounded Repair

- Require at least one dashboard request per repetition.
- Require the second repetition's request count to equal the first repetition's count.
- Preserve real authentication, role-correct populated cards, the source-fixed three-second target,
  both required screenshots, and screenshot-size validation.
- Change no production code or contract.

## Traceability

| Requirement | Repair | Verification |
|---|---|---|
| `test-plan.md` §24.1 dashboard target is `< 3 seconds` | The existing elapsed-time assertion remains `< 3_000` | Prior trusted run reached the dashboard in 2.2–2.6 seconds; independent rerun remains required |
| Slice test case requires two repetitions with equivalent scenario counts | The second repetition must equal the first and both must be nonzero | `performance-readiness.e2e.spec.ts`; Playwright collection lists both tests |
| Visual acceptance requires a populated, role-correct usable dashboard | Existing real login, headings/cards, and screenshot captures are unchanged | Independent trusted browser validation owns both PNGs and manifests |

## Verification

- Exact prior validator symptom inspected:
  `../2026-07-24_191534_normal_run/evidence/terminal-logs/trusted-browser-acceptance-1.log`.
- Exact command was reproduced inside the agent sandbox; system Chrome aborted before page creation,
  independently of the candidate. No screenshot was fabricated.
- The repaired spec compiles and collects exactly two tests:
  `evidence/terminal-logs/playwright-spec-collection.log`.
- Focused E2E lint passes: `evidence/terminal-logs/focused-e2e-lint.log`.
- Diagnosis: `evidence/browser-repair-diagnosis.md`.

## Two-Axis Review

- Standards: the repair is confined to the declared E2E spec and expresses the written repeatability
  contract without altering React Strict Mode or weakening the performance/content assertions.
- Spec: two nonzero equivalent scenario counts are now asserted directly; screenshots, populated
  route, role, and fixed response-time evidence remain mandatory.

## Residual Risk

The agent sandbox cannot launch system Chrome after startup, although Ralph's preflight probe passed
outside it. Independent trusted validation must run the repaired spec twice and retain both declared
screenshot manifests before any commit.

## Recommended Next Action
Run full independent Ralph validation. Commit only if the trusted browser validator produces both
green repetitions and complete screenshot manifests.
