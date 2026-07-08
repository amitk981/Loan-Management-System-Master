# Maintenance Stage Operating Plan (Post-Development Map)

Written 2026-07-08 at the owner's request. This is the complete operating map for the
period AFTER every product slice in `docs/working/IMPLEMENTATION_SLICE_INDEX.md` is
Complete. It composes what is already decided (change-request intake, the Ralph loop,
staging→main promotion) into one document and adds the missing pieces. Sections marked
**[proposed]** are new decisions this plan introduces; everything else restates
mechanisms that already exist and run today.

Status today (2026-07-08): 40 of 147 slices Complete, 107 Not Started. The stage below
begins when that second number reaches zero.

---

## 1. When this stage begins — definition of "development complete"

All of the following, in order:

1. Every slice in `docs/slices/` has Status `Complete` (the loop stops with "No
   eligible slice was found").
2. A final `architecture_review` run has executed after the last slice, and its
   findings in `docs/working/REVIEW_FINDINGS.md` are either fixed (as slices) or
   explicitly accepted by the owner.
3. The operator-side Playwright E2E suite passes in full on the owner's machine and
   screenshot baselines are current and committed.
4. `docs/working/PROTOTYPE_GAP_REPORT.md` shows no unowned gaps — every prototype
   screen is either wired to the backend or explicitly declared out of scope.
5. Staging is promoted to `main` and the production deploy works end-to-end.

## 2. One-time transition checklist (run once, owner + agent together)

- [ ] Verify GitHub branch protection on `main` is active (RELEASE_PROMOTION.md §setup).
- [ ] Verify Netlify: production branch `main`, branch deploys for `staging` (preview URL).
- [ ] Full E2E pass + baseline refresh on the owner's machine; commit baselines.
- [ ] Execute the data import per `docs/working/DATA_IMPORT_MIGRATION_PLAN.md` (real
      member/loan data enters only here, never through test fixtures).
- [ ] Production smoke test: log in as each role, walk the critical path
      (member → application → sanction → disbursement → repayment).
- [ ] **[proposed]** Tag the release `v1.0.0` on `main` and start
      `docs/working/RELEASE_LOG.md` (one line per promotion: date, tag, slices included).
- [ ] **[proposed]** Decide the production database backup routine (daily dump +
      restore drill) — this is the one operational gap no existing doc owns.
- [ ] Retire the development-stage override habit: from here on,
      `./scripts/ralph-intake.sh` runs WITHOUT `--now` (the stage rule now works for
      you, not against you).

## 3. The single rule of the stage

**Nothing changes in the codebase except through `docs/change-requests/`.**
No chat-driven edits, no hot-fixes on `main`, no exceptions for "tiny" changes. Every
change — bug, feature, UI tweak, error report — becomes a file in `inbox/`, is
validated by intake, becomes a gated CR slice, and rides the same pipeline that built
the product. The owner never needs to judge "is this change safe?" — the pipeline
judges; the owner judges "is this change what I wanted?" from the evidence.

## 4. Input taxonomy — every kind of change and its path

| What happened (owner's view) | Template | Type field | Path after intake |
|---|---|---|---|
| Something is broken on a screen | `TEMPLATE-bug.md` | `bug-frontend` | CR slice → loop |
| An API/number/calculation is wrong | `TEMPLATE-bug.md` | `bug-backend` | CR slice → loop |
| Broken and it spans both (or unknown) | `TEMPLATE-bug.md` | `bug-cross-stack` | CR slice (High risk) → loop |
| Error message / crash seen in production | `TEMPLATE-bug.md` | severity per impact; money/security/data = Critical | CR slice → loop |
| New functionality (any size) | `TEMPLATE-feature.md` | `feature` | CR slice → loop |
| UI-only change to the approved design — labels, colours, layout, or new frontend-only behaviour with no backend | `TEMPLATE-feature.md` | `ui-change` (+ "owner approved" in Source Document Reference) | CR slice → loop; impact analysis proves backend untouched |
| Change too big for one run (new module/capability) | `TEMPLATE-feature.md` first, then split | `feature` | CR accepted → owner+agent author epic + child slices from `TEMPLATE-epic.md` / `TEMPLATE-slice.md`, register in the slice index, mark the CR slice `Superseded — see Epic <NNN>` |
| External change (SAP interface, regulation, new document format) | `TEMPLATE-feature.md`, quoting the external source | `feature` | CR slice; agent updates `docs/working/` digests, **never** `docs/source/` |
| The *data* is wrong (misspelled name, wrongly entered amount) — the software behaves correctly | — no template — | — | Not a change request at all — see §4.1 |

Notes:
- "I don't know which type" is fine — pick `bug-cross-stack` or ask the agent in chat
  to classify it; helping fill the template is explicitly allowed.
- **Step 0 for anything puzzling:** before filing, ask the agent in chat "bug or
  intended?" — it checks the behaviour against `docs/source/` and
  `docs/working/ASSUMPTIONS.md`. "Intended, but I want it different" simply becomes a
  `ui-change`/`feature` CR instead of a bug. This filters junk CRs for free.
- **Unreproducible bugs are still filed** — write what you know. A CR run that cannot
  reproduce the bug may legitimately deliver instrumentation/logging as its outcome;
  the real fix follows as a second CR once the logs catch it in the act.
- **Automation problems are not change requests.** The CR pipeline is for the product.
  If the loop, gates, or scripts misbehave, that is an owner chat session (diagnose,
  fix, commit — like the 2026-07 workflow repairs), never an inbox file.
- `docs/source/` stays read-only forever. If the real-world rules change, the change
  request itself becomes the authority ("owner approved"), and working docs record it.

### 4.1 Data corrections — wrong data, not wrong code

When a record is wrong but the software behaves correctly, no code changes and no
change request is filed:

1. **Preferred:** fix it through the app's admin/edit screens — the correction is then
   permission-gated and audit-logged like any other user action.
2. **If no screen can edit that field, THAT is the change request:** file a feature CR
   for the missing admin capability, then do step 1 once it ships.
3. **Direct database edits are a last resort**, only for corrections that cannot wait
   for step 2: take a fresh backup first, make the single correction, and record
   what/why/when (in the audit log if possible, otherwise a dated note in
   `docs/working/HANDOFF.md` until §10.1 fixes the backup routine). Never batch-edit
   production data by hand.

## 5. The pipeline (one picture)

```
 owner notices something (bug / idea / feedback / error)
        │
        ▼
 step 0 — chat pre-check: "bug or intended?"
   (agent checks docs/source/ + ASSUMPTIONS.md;
    data wrong, not code → §4.1, no CR;
    automation misbehaving → chat session, no CR)
        │
        ▼
 chat with agent: describe in plain words ──▶ agent drafts the template file
        │                                      into docs/change-requests/inbox/
        ▼
 ./scripts/ralph-intake.sh
        │ rejected → intake lists what is missing; fix file; rerun (no code touched)
        ▼ accepted
 CR-NNN slice in docs/slices/ (original archived in accepted/)
        │
        ▼
 ./scripts/ralph-loop.sh
        │  gates: impact-analysis (CR-only) + TDD + tests + typecheck
        │         + lint + build + diff limits + protected paths
        ▼
 staging (auto-commit, auto-push, Netlify preview URL)
        │
        ▼
 owner reviews: evidence folder + review packet + staging preview
        │
        ▼
 GitHub PR staging → main (CI green, then merge = release)
        │
        ▼
 production (Netlify deploys main)
```

Rollback at any point: revert the PR on GitHub, or republish the previous Netlify
deploy. Then file the bug as a CR. Never fix `main` by hand (RELEASE_PROMOTION.md).

## 6. The owner's role — feedback in, releases out

The owner intervenes at exactly three points; everything between them is automated.

**Per change (minutes):** describe the problem/idea in chat → agent drafts the
template → owner reads it back ("is this what I meant?") → save to `inbox/` → run
intake.

**Per batch (when convenient):** run the loop → when it stops, review the run
folders' review packets and screenshots, click through the staging preview URL →
if satisfied, promote via PR. If not satisfied, that feedback is itself a new
change request.

**Periodic (see §8):** run the operator E2E suite, skim REVIEW_FINDINGS after
architecture reviews, keep promotions flowing so staging never drifts far from main.

What the owner never does: edit code, edit `docs/slices/` by hand (except the
Superseded status line in the epic-split flow), push `main` from a terminal, merge a
red PR, or approve a change without evidence.

## 7. Skills in the maintenance stage

Checked against the installed Matt Pocock skill set (2026-07-08): **no skill exists
that runs a change-management pipeline end-to-end — and none is needed.**
`ralph-intake.sh` + the loop ARE that pipeline, and they are stronger than any skill
because both agents (codex and Claude) can drive them; skills remain Claude-only
accelerators (`SKILL_REGISTRY.md`). Stage mapping for maintenance:

| Moment | Skill | Use |
|---|---|---|
| CR implementation runs | `tdd` | The reproduction test IS the red test: first prove the bug, then fix it. |
| CR repair / hard bugs | `diagnosing-bugs` | Reproduce → minimize → hypothesize → fix on the failed run's artifacts. |
| After each CR batch | built-in `/code-review` | Owner-side review of the batch diff with the CR slice file as the spec. |
| Epic-split sessions | `grill-with-docs`, `domain-modeling` | Stress-test a big CR's split against source docs; keep terminology consistent while authoring the epic/slice files. |
| New external integrations | `research` | Primary-source digests before an agent touches an unfamiliar API. |

Skills deliberately NOT adopted for this stage: unchanged from `SKILL_REGISTRY.md`
(`git-guardrails-claude-code`, `setup-pre-commit`, `grilling`, etc. — the exclusion
reasons all still hold). New skills from the internet are installed only after the
owner-side operator reviews their content.

## 8. Cadences and health **[proposed defaults — owner may retune]**

| Cadence | Action | Owner effort |
|---|---|---|
| Per CR batch | Loop run + evidence review + promotion PR | ~15 min |
| Every 5 completed CR slices | `architecture_review` run continues exactly as in development (the existing counter in `.ralph/state.json` does this automatically) | skim findings |
| Monthly | Operator E2E full pass; refresh baselines if the UI legitimately changed | ~10 min |
| Monthly | Dependency review per `docs/working/DEPENDENCY_POLICY.md` — security updates enter as change requests like everything else | file CRs |
| Monthly | Verify the production DB backup ran and one restore drill succeeds (once §2 decides the mechanism) | ~10 min |
| Quarterly | Re-planning session: prune stale assumptions in `ASSUMPTIONS.md`, close superseded items in `RISK_REGISTER.md`, review the accepted/ archive for patterns (recurring bug areas = candidate refactor slices) | 1 session |

## 9. Documentation trail (unchanged, listed for completeness)

Every CR run keeps producing the same artifacts as development runs: run folder with
prompt, plan, impact analysis, evidence (self-contained — AFK_RUNBOOK.md §Evidence),
risk assessment, review packet, final summary. Working docs stay live:
`API_CONTRACTS.md` (contract changes), `ASSUMPTIONS.md` (judgment calls),
`REVIEW_FINDINGS.md` (review output), `HANDOFF.md` (state between sessions),
digests (updated when their module changes). The `accepted/` folder is the permanent
audit log of every change ever requested. **[proposed]** `RELEASE_LOG.md` adds the
one missing view: which promotion shipped which CRs, one line each.

## 10. Open decisions the owner still needs to make

1. **Backup mechanism and location** for the production database (§2) — the only
   operational gap with no owning document. Includes the promotion rule in §11.D2:
   back up before promoting any release that contains a migration.
2. **Release tagging** — adopt the `v1.x` tag + RELEASE_LOG proposal, or skip it and
   rely on PR history alone.
3. **Support window** — whether "Critical" bugs get an out-of-order emergency lane
   (`ralph-intake.sh --now` + immediate loop + immediate promotion) as standing
   policy, or stay owner-judgment per case.
4. **Cadence tuning** — accept the §8 defaults or adjust after the first month of
   real maintenance.
5. **Run-artifact archiving** (§11.B6): `.ralph/runs/` is 142 MB / 121 folders after
   one week of development; unbounded over years. Proposed: once a quarter, zip runs
   older than 6 months into `.ralph/archive/` (evidence stays retrievable, repo stays
   light).
6. **Production error visibility** (§11.D4): decide how you LEARN about production
   errors — weekly log check as a calendar habit, or a future CR slice adding simple
   error alerting. Until decided, users reporting problems is the only signal.
7. **Fresh-machine bootstrap** (§11.F2): a one-page checklist for rebuilding the
   operator machine (clone, node via nvm arm64, `.ralph/venv`, `npx playwright
   install chromium`, git identity, GitHub/Netlify access). Worth writing while the
   current machine is healthy.

## 11. Appendix — scenario catalogue (what can happen, and what already protects you)

Compiled 2026-07-08 by walking every failure mode against the actual scripts and
docs. **Bold** = genuine gap, promoted into §10. Everything else is already absorbed
by the system as built.

### A. Changes and requests

| # | Scenario | What protects you / what happens |
|---|---|---|
| A1 | Ordinary bug or feature request | The §4/§5 pipeline — intake, CR slice, impact-analysis gate, full gates, staging, your promotion. |
| A2 | Critical production bug (money/security/data) | Same pipeline at emergency speed: `--now` intake override, immediate loop, immediate promotion; Netlify/PR revert meanwhile (§10.3 decides if this becomes standing policy). |
| A3 | Vague or incomplete request | Intake rejects it, lists the missing sections, touches no code. Agent helps you refill; nothing can enter half-specified. |
| A4 | Request bigger than expected mid-run | Diff limits fail the run before sprawl lands; the CR gets split via the epic/slice templates instead. |
| A5 | Two requests contradict each other | Intake processes in order; the second CR's impact analysis sees the first's changes. Your batch review (§6) is the human check — read `accepted/` before promoting a batch. |
| A6 | Request contradicts `docs/source/` | Allowed deliberately: the CR itself becomes the authority ("owner approved"), working docs record the delta, source docs stay untouched as history. |
| A7 | You change your mind after acceptance | Before the run: edit the CR slice Status to `Superseded — owner withdrew`. After it shipped: file a reversal CR; never hand-edit code. |
| A8 | External change (SAP, regulation, formats) | Feature CR quoting the external source; `docs/source/integrations.md` and digests record the new reality. |
| A9 | Wrong data, correct code (typo in a record) | §4.1 path: admin screens first; missing screen = the CR; backed-up single correction as last resort. |
| A10 | "Is this a bug or intended?" | Step 0 chat pre-check against source docs before any template is filed. |

### B. Automation failures

| # | Scenario | What protects you / what happens |
|---|---|---|
| B1 | Run dies mid-flight (crash, closed lid, usage limit) | `ralph-recover.sh` runs automatically at next loop start: salvages artifacts, removes the orphan worktree, requeues the slice. Half-done work is never kept. |
| B2 | Both agents' usage limits exhausted | Loop switches agents, then stops cleanly. Completed slices are already committed; rerun later. Nothing to fix. |
| B3 | Same slice fails repeatedly | Loop stops after repeated failures rather than thrashing. Owner action: open a chat session, ask the agent to diagnose (`diagnosing-bugs`) using the salvaged run artifacts — never bypass gates to force it through. |
| B4 | Gates break from environment drift (node/OS/tool updates — happened 2026-07: Rosetta terminal ran x86_64 node) | Preflight checks catch the obvious; for the rest, the fix is a chat diagnosis session. Rule: repair the environment, never weaken a gate to get green. |
| B5 | Stale lock / orphaned worktree | Preflight auto-removes locks whose owning process is dead; recovery cleans worktrees. |
| B6 | **Run artifacts grow unbounded** | Nothing owns this today — 142 MB in week one. See §10.5. |
| B7 | Agent CLI update changes behavior (codex/claude adapters) | Two independent adapters mean one broken agent ≠ broken loop (`AGENT_TOOL=claude` or default codex). Treat a broken adapter like B4: diagnose in chat. |

### C. Outside world

| # | Scenario | What protects you / what happens |
|---|---|---|
| C1 | GitHub down / push fails | Verified non-fatal (`ralph-run.sh:424`): the run completes, work is committed locally, push retries on the next run or manually. |
| C2 | CI red on the promotion PR | The rule already exists: never merge red. Staging holds the work; a repair CR fixes it. Production is never exposed. |
| C3 | Netlify build breaks (their node bump, etc.) | Production keeps serving the last good deploy; you see it on the staging preview first. File a CR. |
| C4 | Dependency security vulnerability | Monthly dependency review (§8) per DEPENDENCY_POLICY; the fix enters as a CR like everything else. |
| C5 | Framework major-version EOL (Django/React) | Quarterly re-planning turns it into an upgrade epic via the split flow — the one case where "maintenance" temporarily looks like development again. |
| C6 | AI pricing/limit changes make the loop expensive | The pipeline is agent-agnostic by design; adapters can point at cheaper models, and the queue waits patiently — slices don't rot. |

### D. Production and data

| # | Scenario | What protects you / what happens |
|---|---|---|
| D1 | Bad release reaches production | Two independent one-click rollbacks (PR revert; Netlify publish-previous-deploy), then a CR for the real fix. |
| D2 | **Code rollback ≠ data rollback** | A reverted release does NOT un-run its database migration. Protections today: non-destructive-migrations rule + makemigrations gate. Missing: backup-before-promotion when a release contains a migration — folded into §10.1. |
| D3 | Bad data imported at go-live | DATA_IMPORT_MIGRATION_PLAN governs the import; run it against a copy first, verify counts, then production. |
| D4 | **Production error nobody notices** | No monitoring exists or is planned by any slice. See §10.6. |
| D5 | Secrets rotation / leaked credential | `deployment-ops.md` + `security-privacy.md` own the design; rotation is an ops action + a config change, never a code hot-fix. |

### E. Quality drift (the slow killers)

| # | Scenario | What protects you / what happens |
|---|---|---|
| E1 | Architecture erodes across many small CRs | Architecture-review runs continue automatically every 5 completed slices (the state counter doesn't care that they're CR slices). |
| E2 | Flaky tests erode trust in gates | Treat a flaky test as a Critical bug in the test suite — CR it. A gate people ignore is worse than no gate. |
| E3 | Evidence quality drifts (e.g. the 2026-07-07 unstyled-evidence incident) | Runbook now mandates self-contained evidence; your review habit is the backstop — reject evidence you can't actually review. |
| E4 | Assumptions/risk register go stale | Quarterly cleanup (§8) prunes ASSUMPTIONS.md and RISK_REGISTER.md; recurring bug areas in `accepted/` become refactor-slice candidates. |

### F. Owner-side

| # | Scenario | What protects you / what happens |
|---|---|---|
| F1 | You're unavailable for weeks | Nothing breaks. The queue, staging, and production all hold position; automation only moves when you run it. |
| F2 | **Operator machine dies** | Code, docs, baselines: all on GitHub. Local-only: `.ralph/venv`, node setup, Playwright browsers, git identity — rebuildable but undocumented. See §10.7. |
| F3 | Accidental destructive action (deleted files, bad force-push) | GitHub branch protection on `main`; staging history on the remote; protected-paths validation; worst case is re-cloning. |
| F4 | Handing the system to a real developer someday | The read-order in AGENTS.md *is* the onboarding: AGENTS.md → this plan → AFK_RUNBOOK → change-requests README. A developer inherits a fully documented, gate-enforced pipeline — not tribal knowledge. |
