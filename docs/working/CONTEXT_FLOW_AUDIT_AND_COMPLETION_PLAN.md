# Context Flow Audit and Production Completion Plan

Owner-session audit, 2026-07-10. Scope: (1) the complete automation flow, (2) how context is fed
into the sessions that execute slices, measured against the real context ceiling, (3) how the
finished product stitches back to the design prototype it started from, and (4) what "all slices
complete" must mean for a production-ready application. Everything below was verified against the
scripts, working docs, run telemetry, and slice files in this repository — not from memory.

**Snapshot at audit time:** 89 of 172 slices Complete, 81 Not Started, 1 Blocked (004E),
1 Superseded. Epic 006 is closing (006G2, 006H2, 006H3, 006X remain), then epics 007–012
(~77 slices). The loop was actively running during this audit (006F4 PostgreSQL concurrency
acceptance passed via repair at 23:05).

---

## 1. The automation flow, end to end (as verified)

```
./scripts/ralph-loop.sh [N]
  └─ ralph-recover.sh            salvage any interrupted run, remove orphan worktree/lock
  └─ per iteration:
       ├─ architecture review    if due (every 4 completed slices; independent critic,
       │                         writes REVIEW_FINDINGS.md, creates corrective slices)
       ├─ afk-dev.sh 1 --mode normal
       │    └─ ralph-run.sh
       │         1. preflight; refuse unless `staging` checked out; refuse inside worktree
       │         2. select lowest filename-sorted "Not Started" slice; veto check
       │         3. lock; create isolated worktree + branch ralph/<run>_<slice>
       │         4. pre-install backend venv deps + frontend node_modules (agent has no network)
       │         5. generate run prompt (embeds core rules + fixed read order)
       │         6. run agent adapter (codex exec headless / claude -p), 2h watchdog
       │         7. independent validation: build, typecheck, lint, vitest, Django check,
       │            migration sync, coverage ≥85%, protected-paths, diff caps (30 files/2000 lines)
       │         8. update state.json, slice Status, HANDOFF fallback, progress.md
       │         9. commit → ff-only merge into staging → push (merge failure stops the loop)
       ├─ context tripwire       advisory peak-occupancy check, logs watch/breach, never fails a run
       └─ on failure: one repair run (high effort); stop after repair failure or 3 total failures
```

Control surfaces that make this safe to run AFK: protected-paths validation (scripts/, config,
AGENTS.md, docs/source/, policy files), the never-do list in DECISION_POLICY.md, the standing
approval + veto model in HIGH_RISK_APPROVALS.md, orchestrator-owned commits (agents never touch
git), staging-only integration with owner-gated promotion to main (RELEASE_PROMOTION.md), and the
independent architecture review every 4 slices.

**Verdict: the flow is sound and battle-tested.** The 2026-07-10 review catching the silently
skipped PostgreSQL acceptance (finding → corrective 006F4 → closed same day) is the loop working
as designed: the same agent writing code and tests is checked by an independent reviewer, and
correctives enter the same gated queue.

---

## 2. The context flow — how a slice session is fed

Each run is a fresh session (no chat history). Context is assembled in layers, cheap to expensive:

| Layer | Content | Size | When read |
|---|---|---|---|
| 0 | Generated `prompt.md` (core rules, slice id, read order) | ~4 KB | Always |
| 1 | Fixed preamble: AGENTS.md, TOKEN_RULES, CONTEXT.md, AFK_RUNBOOK, config, permissions, state.json, HANDOFF, DECISION_POLICY, FRONTEND_DESIGN_RULES | ~30 KB | Always |
| 2 | Selected slice file + parent epic file | 2–8 KB | Always |
| 3 | Epic digest in `docs/working/digests/` | 2–40 KB | If it exists |
| 4 | Owner-curated capability maps (`docs/working/maps/`) | ~4–8 KB each | To locate exact source sections |
| 5 | `docs/source/` originals (21 files, 53–125 KB each, 1.86 MB total) | selective sections via `rg` | Only when the slice/digest requires |

Cross-run memory that substitutes for chat history: `HANDOFF.md` (rewritten every run, currently
high quality), `state.json` (queue truth), digests (accretive extraction — read once from source,
reuse forever), `ASSUMPTIONS.md`, ADRs, `REVIEW_FINDINGS.md`, and the "sharpen the next 1–2 slices
before finishing" rule that front-loads requirements into upcoming slice files while the relevant
source sections are already open.

This is the right architecture. The single most valuable property: **source documents are paid
for once per epic (digest building), not once per slice.** The maps (section-level pointers into
source) make even the first read cheap and precise.

### Measured against the real context ceiling

From Codex session rollouts (peak per-call input tokens vs model window — the signal that predicts
auto-compaction, not the cache-inflated "tokens used" line):

- Window: 258,400 tokens (gpt-5.5) through 2026-07-10 morning; **353,400 (gpt-5.6-sol) since**.
- 30-run audit (2026-07-09): median peak ~58%, max 76%, **zero auto-compactions**.
- Under the old window, later heavy runs breached: 88–94% — and the worst offenders were
  **repair runs** (93–94%) and digest-building/hardening-heavy normal runs.
- Under the new 353K window, the last 12 runs peak at 26–75% (one watch-band run at 72%).

**Verdict: context headroom exists; the ceiling is respected by design, not luck.** The standing
decision (memory: ralph-context-audit-decision) holds: split slices on scope/diff-cap signals, not
on context. The tripwire keeps this honest without adding a failure mode.

---

## 3. Findings — context efficiency (ordered by value)

### F1 — `CONTEXT.md` is stale and is read first by every single run  *(highest value, trivial fix)*
It still says "Backend/database implementation is not present yet", "No product feature
implementation has been started by Ralph yet", and "no dedicated lint, typecheck, or real test
script yet". Reality: 89 slices done, a Django backend with 378 tests at 93–94% coverage, full
gate suite. Every run starts by ingesting a false picture and must reconcile it against
HANDOFF/state, burning reasoning on contradiction. **Fix:** refresh CONTEXT.md to the current
architecture (it is not a protected file), and give the architecture review a standing duty to
keep it current — it already audits every 4 slices, so it is the natural owner. Keep it under one
page: what exists, where, and the invariants; leave per-run detail to HANDOFF.

### F2 — Epic digests have outgrown their own rule
The digest README caps digests at ~300 lines. Actual: epic-005 = 502 lines (37 KB), epic-006 =
515 lines (40 KB ≈ 10K tokens), epic-004 = 350, epic-003 = 337. A slice run reads the whole epic
digest even when only two sections apply. **Fix:** when an epic completes, prune its digest down
to what still matters cross-epic (contracts other epics consume, ADR-linked invariants) and move
the rest to an `archive/` subfolder that stays greppable but is not in the default read path.
For live epics, keep per-slice headings (already the 007 pattern) so a run can `rg` its slice id
and read only that section.

### F3 — Pre-build digests for epics 008–012 from the capability maps
Digests exist only through epic 007. The maps README already prescribes building each digest from
the matching capability map. Today the first slice of each new epic pays the full source-reading
spike inside an implementation run — exactly the runs that breached 88–94% under the old window.
**Fix:** before each epic starts (or as an explicit low-risk docs-only slice at each epic
boundary), build the digest from the map + source sections in a dedicated run that does nothing
else. Digest-building and implementation should not share a session. Epics 009 and 010 (money
paths: disbursement, repayment, interest) deserve this most — their source sections are dense and
their slices are majority High-risk.

### F4 — Repair runs are the context-heaviest sessions (93–94% peaks under the old window)
Repair reads the failed run's full artifacts (multi-MB terminal logs) plus does a fresh
implementation. **Fix (automation change, owner commits to scripts/):** have `ralph-validate.sh`
write a compact `failure-summary.md` (which gates failed, last ~50 lines of each failing log,
changed-files list) into the run folder at failure time; point the repair prompt at that file
first, full logs only on demand. This converts the most expensive session type into a normal one.

### F5 — Tail slices are template stubs; the sharpening chain is the only thing filling them
007A and 010F (checked directly) still carry the generic template ("Deliver this narrow
capability…", "Implement the named backend/API capability only"). The lazy just-in-time sharpening
rule is correct — sharpening 80 slices up front would be wasted and would rot. But the failure
mode is silent: if the chain skips (correctives interleave, an agent forgets), a run starts on a
stub and improvises scope from the epic alone. **Fix:** treat "the selected slice still contains
the template Goal line" as a signal in the run prompt: the run's first deliverable is then
sharpening the slice from digest + maps + epic before writing the execution plan — never
implementing directly off the stub. This costs one paragraph in the prompt template.

### F6 — 004E is stale-blocked (concrete queue bug)
`004E-witness-shareholder-validation` is Blocked pending 004D2, 004F, and 005A — **all three are
Complete**. Nothing re-evaluates Blocked slices. **Fix now:** flip its Status to `Not Started`
(it will slot into the queue by filename order). **Fix structurally:** the architecture review
checklist should include "re-check every Blocked slice's stated prerequisites against
completed_slices".

### F7 — Validation does not parse the agent's own review packet
The 006F3 incident: the run's review-packet said "Failed acceptance; do not commit or merge", yet
the run reported Success and merged. The independent reviewer caught it two runs later, but the
orchestrator could have caught it mechanically. **Fix (scripts/, owner change):**
`ralph-validate.sh` fails the run if `review-packet.md` contains a failed/blocked result marker.
Cheap, mechanical, closes a class of "agent says no, artifacts say yes" gaps.

### F8 — Minor preamble duplication (accept as-is)
AGENTS.md core rules are restated inside the generated prompt; TOKEN_RULES restates the read
order. This redundancy is deliberate insurance for two different agents and costs ~2–3 KB of
cached tokens. Not worth touching.

---

## 4. Stitching the product back to the design prototype

The prototype (`sfpcl-lms/`, built from the same `docs/source/`) is the approved visual system.
The stitching machinery that already exists and works:

- **FRONTEND_DESIGN_RULES.md** (binding): no new colours/typography/layout/components; new screens
  are composed only from the existing component inventory; documents > prototype (gap-closure duty).
- **VISUAL_ACCEPTANCE.md**: required states (loading/empty/error/unauthorized/validation/success),
  screenshot evidence per frontend slice.
- **PROTOTYPE_INVENTORY.md / PROTOTYPE_GAP_REPORT.md**: living ledger of which screens are real
  vs mock, updated in the same run that closes a gap.
- **Per-epic frontend wiring slices** — the deliberate stitch points: 006H (+006H2/006H3), 007I/007J,
  008M, 009K, 010M, 011P, 012DA/012EB. Each replaces mock reads with real APIs for its module.
- **002EY Playwright visual-regression harness** + e2e baselines.
- **Architecture review** spot-checks visual fidelity (it caught 006H redesigning the workbench and
  created 006H3 to restore prototype composition while keeping the real wiring).
- Spec-vs-prototype conflicts are pre-adjudicated: spec IDs win (e.g. member-portal MP22/MP24
  numbering divergence is documented in the gap report and named in both owning slices).

**Current stitching state, measured:** 20 non-test files still import `mockData` —
`SanctionWorkbench`, `RegistersHub` (007J); `DocumentationHub`, `DocumentChecklist`,
`DocumentPackModal`, `AuditTimeline` (008M); `DisbursementHub`, `PaymentAuthorisationHub`,
`LoanAccount360` (009K); `RepaymentsHub`, `RepaymentLedger`, `MonitoringDashboard` (010M);
`GlobalSearchResults` (010N); `ComplianceDashboard`, `GrievancesHub`, `AuditArchiveHub` (011P);
`ReportsMIS` (012DA); `CompletenessWorkbench`, `Header`, `App.tsx` (partial residue). Every one
has a named owning slice — the plan is complete on paper.

### Gaps and what to add

**S1 — The visual baselines rot on their own (open CR, fix it early).**
`docs/change-requests/inbox/e2e-visual-baselines-nondeterministic.md` documents that the dashboard
baselines embed the rendered date and time-of-day greeting, so screenshots fail on any other
day/time even with zero UI change. Until fixed, every future wiring slice's visual evidence is
noise-prone, and agents will be tempted to regenerate baselines (which hides real drift). Intake
refuses CRs while product slices remain — **this is the case for the owner's `--now` override**:
it protects the integrity of every visual gate from 006X onward. Fix before 006X/007I.

**S2 — Make each wiring slice ratchet the mockData count down, mechanically.**
Today "no mock reads remain in its screens" is prose in the gap report. Add to each wiring slice's
acceptance criteria (and to the review checklist): after the slice, `rg -l "mockData" src/ --glob
'!*test*'` must not list any file the slice owns, and the total importer count must be ≤ the
pre-slice count. At 012DA/012EB the count must be zero and `mockData.ts` itself reduced to test
fixtures or deleted. This turns "fully stitched" from a judgment into a number that must reach 0.

**S3 — Grow the visual-regression baseline set at every wiring slice.**
002EY exists but baselines cover only the early screens. Each per-epic wiring slice should commit
deterministic baselines for the screens it wires (after S1 lands), so prototype fidelity is locked
mechanically as each module goes real — not re-litigated at the end. 006H3 already demands exactly
this for the appraisal workbench; make it the standing pattern for 007I/J through 012.

**S4 — Add a final prototype-parity sweep before the UAT packet.**
Between 012H and 012I, walk `PROTOTYPE_INVENTORY.md` screen by screen against the running app:
every screen reachable via its role's navigation, API-backed, all VISUAL_ACCEPTANCE states present,
mockData importer count = 0, member-portal screens matched to spec IDs. Output: a signed-off parity
table into the 012I UAT packet plus corrective slices for any miss. This is one Medium docs+test
slice (call it `012HZ` so it sorts before `012I`), and it is the moment "stitched to the design
prototype" becomes a verified claim instead of an accumulated assumption.

---

## 5. Production readiness at the end of all slices

What the tail of the queue already covers: 012F security/privacy regression, 012G critical E2E UAT
smoke scenarios, 012H health endpoints + deployable smoke command (deployment-ops §13.1/§20), 012I
final UAT review packet. Release mechanics are owner-gated (staging → PR → main → Netlify
production). That is a strong skeleton. What it does **not** yet cover — the gap between "queue
empty" and "production-ready":

### P1 — PostgreSQL must stop being a five-test guest  *(the most important one)*
Production runs PostgreSQL; the gate suite runs SQLite, with exactly five concurrency tests
executed on real PostgreSQL (006F4). Money paths land in epics 009–010 (disbursement, repayment
allocation, interest accrual/capitalisation) — row-locking, transaction, and constraint semantics
differ between engines precisely where it matters most. **Recommendation:** at the epic 009
boundary, flip the backend gate database to PostgreSQL for the full suite (the 006F4 harness and
`postgres_test_settings` already exist; the arm64 venv wrapper note in project memory applies).
Keep SQLite only for fast local iteration. Doing this at the 009 boundary instead of the end means
~50 remaining slices get tested on the production engine; doing it at the end means re-validating
everything.

### P2 — The backend has no deployment target
`netlify.toml` deploys only the frontend. deployment-ops.md describes the backend environment
strategy, and 012H makes the backend *verifiable* once deployed — but nothing in the queue
provisions where the Django app, PostgreSQL, object storage, and scheduled jobs actually run.
**Recommendation:** owner decision needed on hosting; then one infrastructure slice (or an
owner-side setup following deployment-ops) to stand up a real staging environment early in epic
012 — 012G/012H smoke checks should run against a deployed staging URL, not localhost, or they
prove less than they appear to.

### P3 — Integration adapters are shells by design; go-live needs a cutover plan
SAP customer codes (009A/B), bank/payment, email/SMS (003I/F), CDSL pledge (008I) are built as
adapters with stub transports per the source docs. Production needs, per integration: real
credentials/endpoint, a certification test with the counterparty, and a documented manual fallback
(the SOPs imply several of these start manual). **Recommendation:** an
`INTEGRATION_CUTOVER_PLAN.md` working doc started when epic 009 begins, one row per adapter:
stub → manual procedure → live, with owner sign-off per transition. None of this blocks the slice
queue; all of it blocks go-live.

### P4 — Data migration is planned but not executed
003L produced `DATA_IMPORT_MIGRATION_PLAN.md`; no slice executes an import of real members,
shareholdings, KYC records, or in-flight loans. UAT (012I) on seed data alone will miss the
class of defects only real data exposes (encoding, duplicates, partial histories).
**Recommendation:** after 012I, a supervised import-dress-rehearsal into staging using the 003L
plan, feeding defects back through change-request intake. Schedule owner time for this — it is the
one step that cannot be AFK.

### P5 — Performance and volume are untested
The test plan sources cover it, but no slice runs load against the deployed app (dashboard,
registers, report exports with masking are the likely hot paths). **Recommendation:** fold a
minimal budget into 012H's smoke command (p95 latency thresholds on the read-only workflow checks)
rather than adding a new heavy harness; anything worse becomes a CR.

### P6 — Operations for day 2
Backups/restore drill, log retention, secrets rotation, monitoring/alerting beyond health
endpoints, the runbook for "Netlify rollback + Django rollback together". deployment-ops.md
specifies these; they are owner/ops work, not agent slices. **Recommendation:** extract a
one-page go-live checklist from deployment-ops.md into `docs/working/GO_LIVE_CHECKLIST.md` when
epic 012 starts, and treat 012I as incomplete until its items are checked.

### P7 — The maintenance-stage transition is already designed — arm it
Once the queue empties, all change flows through `docs/change-requests/` intake with the
impact-analysis gate. This is the correct production posture. The only missing piece is making
sure UAT/dress-rehearsal findings (P4, P5) are filed as CRs rather than ad-hoc fixes — the
pipeline already refuses ad-hoc changes, which is exactly right.

---

## 6. Recommendation summary, in order

**Do now (owner, minutes each):** — ALL DONE 2026-07-10 late evening
1. ~~Unblock 004E (F6)~~ **Done**: Status flipped to Not Started (slice file + state.json);
   scope note records the verified prerequisites. It will be selected next by filename order.
2. ~~Refresh CONTEXT.md (F1)~~ **Done**: rewritten to current reality; architecture-review
   duties (8) keep CONTEXT.md truthful and (9) re-check Blocked slices added to AFK_RUNBOOK.md.
3. ~~Intake the visual-baselines CR (S1)~~ **Done**: accepted as
   `docs/slices/CR-001-e2e-visual-baselines-nondeterministic.md` (risk Medium). NOTE: CR slices
   sort after all numeric slices, so run it early and explicitly:
   `./scripts/afk-dev.sh 1 --mode normal --slice CR-001` — ideally before 006X/007I.

**Automation changes (owner commits to scripts/, small diffs):** — ALL DONE 2026-07-10
4. ~~failure-summary.md~~ **Done**: `ralph-validate.sh` now records every failed gate's results
   file and writes a compact `failure-summary.md` (FAIL markers, last-50-line tails, changed
   files) on any failure; the repair prompt in `ralph-run.sh` reads it first.
5. ~~Review-packet marker check~~ **Done**: `ralph-validate.sh` fails normal/repair runs whose
   own review-packet.md declares a failed/blocked result or contains "do not commit/merge"
   (architecture-review mode is exempt — its packets quote failure phrases from findings).
6. ~~Stub-slice rule~~ **Done**: the run prompt now requires sharpening a template-stub slice
   from digest + maps + source before execution-plan.md; never implementing off the stub.

**At epic boundaries (fold into the existing rhythm):**
7. Pre-build the epic digest from the capability map in a dedicated docs-only run (F3); prune the
   finished epic's digest to its cross-epic residue (F2).
8. Per-epic wiring slices: mockData importer ratchet (S2) + deterministic visual baselines for the
   screens they wire (S3).
9. Epic 009 boundary: full backend gate suite onto PostgreSQL (P1); start
   INTEGRATION_CUTOVER_PLAN.md (P3).

**Before the finish line:**
10. Real deployed staging for 012G/012H to target (P2), with a small latency budget in the smoke
    command (P5).
11. Add `012HZ` prototype-parity sweep before 012I (S4).
12. GO_LIVE_CHECKLIST.md from deployment-ops.md; 012I is done only when it is (P6).
13. Data-import dress rehearsal after 012I, findings via CR intake (P4, P7).

**The through-line:** the automation and context architecture are correct and proven — 89 slices,
zero compactions, a review loop that catches its own worst failures. The remaining work is not
redesign; it is (a) keeping the always-read context truthful and small as the project ages, (b)
converting prototype fidelity and mock-elimination from prose into ratcheting mechanical checks so
the final product is pixel-faithful to the approved design by construction, and (c) closing the
gap between "all gates green on a laptop" and "running in production on PostgreSQL with real
integrations, real data, and an owner who can roll back."
