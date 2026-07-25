# Review Packet — 012DAB Report and Register Export Frontend Wiring

## Scope Delivered

- Added authenticated export request, status, and audited blob-download functions to the existing
  report client.
- Wired Reports & MIS and Registers to backend job identity, refreshable async states, masking
  notice, denial/validation handling, expiry, and completion-only download.
- Replaced the remaining Registers fixture surface with permission-scoped 012A2/012A3 selector
  views while retaining the established S23/S25 panels.
- Removed all `mockData` and inline business fixtures/calculations from both owned screens.
- Extended the exact trusted browser spec with `export-job-status.png` and `masked-export.png`.

## Source Traceability

| Source requirement | Implementation | Verification |
|---|---|---|
| API §40.7-40.8: request, preserve job id, status, completed download | `reportApi.ts`, both owned pages | `reportApi.test.ts`; ReportsMIS/Register tests |
| Security §32.2: separate export permission, masked default, audited/expiring download | permission-gated actions; backend denial; no sensitive request; job-bound capability | denial, masking notice, foreign URL, expiry, and audited-download tests |
| Slice R1-R2: queued/running/failed/ready plus truthful loading/error/validation | explicit queued/running/finalizing/ready/failed/expired and safe error states | focused 18-test green log |
| Slice R3-R4: no restricted leak; backend authority remains final | no raw detail echo; backend calls remain authoritative even after action visibility | denial tests and browser route assertions |
| Owned mock removal | `ReportsMIS.tsx` and `RegistersHub.tsx` contain no mock import or inline fixtures | source-regression test and `rg` check |

## Two-Axis Review

Standards review initially found the generic register presentation, two incorrect permission
predicates, and a non-contract browser fixture. The candidate now uses existing StatusBadge,
money/link/table patterns; canonical any-of permissions; records page-local composition A-174; and
removes the non-contract fixture.

Spec review initially found unstable retry keys, false-ready completed jobs without a capability,
and a missing validation state. The candidate now retains one retry key, labels grant-less
completion `finalizing` with Refresh, and renders/tests validation distinctly. The reported
catalogue-read concern is not applicable: `docs/working/API_CONTRACTS.md` 012A2/012A3 records the
implemented GET routes used by the remaining register views.

## Validation

- Focused export/register/report tests: 18 passed.
- Focused 012A/012B/012C backend report/export regressions: 49 passed.
- Complete frontend tests: 503 passed across 63 files.
- Typecheck: passed.
- Lint: passed.
- Production build: passed (existing chunk-size warning only).
- Browser attempt: servers and tests discovered; Chrome aborted at launch. No screenshots were
  fabricated. Trusted validation must run the exact spec twice and capture both named outputs.

## Result

Ready for independent validation
