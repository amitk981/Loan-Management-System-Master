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

Notes:
- "I don't know which type" is fine — pick `bug-cross-stack` or ask the agent in chat
  to classify it; helping fill the template is explicitly allowed.
- `docs/source/` stays read-only forever. If the real-world rules change, the change
  request itself becomes the authority ("owner approved"), and working docs record it.

## 5. The pipeline (one picture)

```
 owner notices something (bug / idea / feedback / error)
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
   operational gap with no owning document.
2. **Release tagging** — adopt the `v1.x` tag + RELEASE_LOG proposal, or skip it and
   rely on PR history alone.
3. **Support window** — whether "Critical" bugs get an out-of-order emergency lane
   (`ralph-intake.sh --now` + immediate loop + immediate promotion) as standing
   policy, or stay owner-judgment per case.
4. **Cadence tuning** — accept the §8 defaults or adjust after the first month of
   real maintenance.
