# Ralph AFK Runbook

## Modes
- `bootstrap`: create or verify Ralph scaffolding. Does not implement product features.
- `normal`: pick one eligible vertical slice, create a worktree, run an agent, validate, save evidence, update state, and commit only passing work.
- `repair`: repair the previous failed slice.
- `architecture-review`: inspect architecture, create ADRs/refactor slices, and avoid broad production-code changes.

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
12. If `auto_merge` is enabled, fast-forward merge the run branch into main and remove the worktree; on merge failure the branch is kept for manual review.

Note on agent approval mode: codex runs headless (`exec` mode, approval mode `never`) because nobody is at the terminal during AFK runs. The human safety control is the orchestrator-level high-risk gate plus quality gates and this runbook — not interactive prompts.

## Slice Selection
Use `.ralph/state.json` first. If architecture review is due, run it unless explicitly overridden. If the previous run failed, prefer repair. Otherwise choose the lowest-numbered `Not Started` slice.

## Quality Gates
Enforced by `scripts/ralph-validate.sh` on every run:
- Frontend (`sfpcl-lms/`): `npm run build`, `npm run typecheck`, `npm test` (vitest).
- Backend (`sfpcl_credit/`): `manage.py check`, full test suite, `makemigrations --check` (models and migrations must stay in sync), and coverage with a hard floor (`coverage_fail_under` in `.ralph/config.yaml`, currently 85%; measured 92% on 2026-07-02 — raise the floor as coverage grows, never lower it).
- Protected-paths check: the run fails if any guardrail file was modified.
A failing gate fails the whole run; failing work is never committed, merged, or pushed. ESLint arrives via slice 002FL, then flip `quality_gates.lint` to true.

## Stopping Conditions
Stop on missing required files, unsafe git state, active locks, protected/forbidden file edits, an owner veto (`[revoked]` in HIGH_RISK_APPROVALS.md), repeated gate failures, actions on the DECISION_POLICY never-do list, exceeded diff limits, or missing selected agent command. Ambiguity and high risk are NOT stopping conditions — they are handled by DECISION_POLICY.md and the standing approval.

## Interrupted Runs and Recovery
A run can die mid-flight (usage-limit exhaustion, crash, closed terminal) under either agent. Recovery is automatic and agent-agnostic:
- `./scripts/ralph-loop.sh` runs `scripts/ralph-recover.sh` at startup: it salvages the dead run's artifacts into `.ralph/runs/<run-id>/`, removes the orphaned worktree, deletes its branch if it holds no unmerged commits (kept and reported otherwise), clears the lock, and the still-queued slice reruns automatically.
- Preflight independently auto-removes locks whose owning process is dead; a surviving lock means a run is genuinely still active.
- Rerunning is always safe: slice status only flips to Complete at the end of a fully-gated run. Never salvage partial work from an interrupted run.
- Before a manual single run (`afk-dev.sh`), run `./scripts/ralph-recover.sh` first.

## Evidence and Review
Every run folder should contain prompt, plan, changed files, validation outputs, risk assessment, review packet, and final summary. Frontend/API/database slices require matching evidence.
