# Ralph AFK Runbook

## Modes
- `bootstrap`: create or verify Ralph scaffolding. Does not implement product features.
- `normal`: pick one eligible vertical slice, create a worktree, run an agent, validate, save evidence, update state, and commit only passing work.
- `repair`: repair the previous failed slice.
- `architecture-review`: independent quality review, run automatically by the loop every `architecture_review_every_completed_slices` slices. The reviewer does NOT modify production code. It must: (1) read the diffs of slices merged since the last review; (2) critique test quality — real assertions, edge cases, not just coverage numbers; (3) spot-check doc fidelity against the slice's source references and digests; (4) check for duplication and architecture drift; (5) write findings to `docs/working/REVIEW_FINDINGS.md` (append, newest first) and create or sharpen corrective slices for anything significant; (6) record ADRs for durable decisions; (7) spot-check that the functional-spec requirement IDs (M##-FR-###) of each epic completed since the last review are implemented or explicitly deferred in ASSUMPTIONS.md. This is the independent second pair of eyes on work where the same agent wrote both code and tests.

## Start Commands
- Run the whole queue autonomously ("run ralph loop"): `./scripts/ralph-loop.sh`
- Bootstrap/verify setup: `./scripts/afk-dev.sh --mode bootstrap`
- Dry-run next action: `./scripts/afk-dev.sh --dry-run`
- One normal iteration: `./scripts/afk-dev.sh 1 --mode normal`
- Repair: `./scripts/afk-dev.sh --mode repair`
- Architecture review: `./scripts/afk-dev.sh --mode architecture-review`

## Autonomy Model
The owner granted standing approval for autonomous runs (2026-07-02). Agents never wait for human approval; they follow `docs/working/DECISION_POLICY.md` (source docs first, industry-standard defaults second, never invent business rules, log every assumption). The owner's controls are: the veto list in `docs/working/HIGH_RISK_APPROVALS.md`, the hard-enforced protected-paths check, the quality gates, and the pushed-to-GitHub audit trail.

## Normal Run Order
1. Run preflight (refuses to run from inside a Ralph worktree).
2. Confirm git state is safe.
3. Choose one eligible slice.
4. If the slice is High risk, require an `[approved]` entry in `docs/working/HIGH_RISK_APPROVALS.md`; otherwise stop before starting the agent.
5. Create a run folder and prompt.
6. Create an isolated worktree unless disabled by config.
7. Start the selected agent through `scripts/agent-adapters/`.
8. Validate gates and Ralph artifacts.
9. Save changed files, risk assessment, review packet, and final summary.
10. Update state, progress, handoff, and slice status.
11. Commit only if gates pass and config allows it.
12. If `auto_merge` is enabled, fast-forward merge the run branch into the `staging` integration branch and remove the worktree; on merge failure the branch is kept for manual review. The owner alone promotes staging to main (`docs/working/RELEASE_PROMOTION.md`).

Note on agent approval mode: codex runs headless (`exec` mode, approval mode `never`) because nobody is at the terminal during AFK runs. The human safety control is the orchestrator-level high-risk gate plus quality gates and this runbook — not interactive prompts.

## Slice Selection
Use `.ralph/state.json` first. If architecture review is due, run it unless explicitly overridden. If the previous run failed, prefer repair. Otherwise choose the lowest-numbered `Not Started` slice.

## Quality Gates
Enforced by `scripts/ralph-validate.sh` on every run:
- Frontend (`sfpcl-lms/`): `npm run build`, `npm run typecheck`, `npm test` (vitest).
- Backend (`sfpcl_credit/`): `manage.py check`, full test suite, `makemigrations --check` (models and migrations must stay in sync), and coverage with a hard floor (`coverage_fail_under` in `.ralph/config.yaml`, currently 85%; measured 92% on 2026-07-02 — raise the floor as coverage grows, never lower it).
- Protected-paths check: the run fails if any guardrail file was modified.
- Contract fidelity (checked in review, not by script): API-touching slices follow `docs/source/api-contracts.md` §3 (design principles), §6-8 (envelopes, errors, pagination) and §45 (idempotency for financial actions); model-touching slices follow `docs/source/data-model.md` §30 (indexing) and §34 (transactional integrity); backend module layout follows `docs/source/codebase-design.md`.
A failing gate fails the whole run; failing work is never committed, merged, or pushed. ESLint arrives via slice 002FL, then flip `quality_gates.lint` to true.

## Stopping Conditions
Stop on missing required files, unsafe git state, active locks, protected/forbidden file edits, an owner veto (`[revoked]` in HIGH_RISK_APPROVALS.md), repeated gate failures, actions on the DECISION_POLICY never-do list, exceeded diff limits, or missing selected agent command. Ambiguity and high risk are NOT stopping conditions — they are handled by DECISION_POLICY.md and the standing approval.

## Maintenance Stage (Change Requests)
After the product backlog is finished, changes enter only through `docs/change-requests/` (see its README):
1. The owner (with agent help) fills the strict bug/feature template into `inbox/`.
2. `./scripts/ralph-intake.sh` validates it mechanically. Invalid → rejected with precise errors, nothing enters the pipeline, no code changes. Valid → converted to a `CR-NNN` slice; cross-stack bugs and features are High risk (veto-able as usual).
3. The normal loop implements CR slices with all standard gates PLUS the impact-analysis gate: the run must map affected modules, blast radius, and per-module regression tests in `impact-analysis.md` before code changes; validation fails without it.
4. Intake refuses new CRs while product slices remain (`--now` is the owner's emergency override).
Agents must never implement chat-reported bugs directly — template first, always.

## Interrupted Runs and Recovery
A run can die mid-flight (usage-limit exhaustion, crash, closed terminal) under either agent. Recovery is automatic and agent-agnostic:
- `./scripts/ralph-loop.sh` runs `scripts/ralph-recover.sh` at startup: it salvages the dead run's artifacts into `.ralph/runs/<run-id>/`, removes the orphaned worktree, deletes its branch if it holds no unmerged commits (kept and reported otherwise), clears the lock, and the still-queued slice reruns automatically.
- Preflight independently auto-removes locks whose owning process is dead; a surviving lock means a run is genuinely still active.
- Rerunning is always safe: slice status only flips to Complete at the end of a fully-gated run. Never salvage partial work from an interrupted run.
- Before a manual single run (`afk-dev.sh`), run `./scripts/ralph-recover.sh` first.

## Evidence and Review
Every run folder should contain prompt, plan, changed files, validation outputs, risk assessment, review packet, and final summary. Frontend/API/database slices require matching evidence.
Evidence artifacts must be self-contained and reviewable after the run ends: the run's worktree is deleted on completion, so evidence files must never reference worktree paths, `dist/` build outputs, or anything outside the run folder. Inline built CSS/assets directly into evidence HTML (or copy them into the evidence folder and link relatively). A run that produced evidence 2026-07-07 (004A) linked its stylesheet from the worktree via absolute `file://` path; the pages rendered unstyled by the time the owner reviewed them.
