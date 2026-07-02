# Ralph AFK Runbook

## Modes
- `bootstrap`: create or verify Ralph scaffolding. Does not implement product features.
- `normal`: pick one eligible vertical slice, create a worktree, run an agent, validate, save evidence, update state, and commit only passing work.
- `repair`: repair the previous failed slice.
- `architecture-review`: inspect architecture, create ADRs/refactor slices, and avoid broad production-code changes.

## Start Commands
- Bootstrap/verify setup: `./scripts/afk-dev.sh --mode bootstrap`
- Dry-run next action: `./scripts/afk-dev.sh --dry-run`
- One normal iteration: `./scripts/afk-dev.sh 1 --mode normal`
- Repair: `./scripts/afk-dev.sh --mode repair`
- Architecture review: `./scripts/afk-dev.sh --mode architecture-review`

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
- Frontend (`sfpcl-lms/`): `npm run build`, `npm run typecheck`, `npm test`.
- Backend (`sfpcl_credit/`): `python3 sfpcl_credit/manage.py check` and `python3 sfpcl_credit/manage.py test sfpcl_credit.tests -v 2`.
A failing gate fails the whole run; failing work is never committed or merged. ESLint is a documented gap until a lint setup is added.

## Stopping Conditions
Stop on missing required files, unsafe git state, active locks, forbidden file edits, High-risk slices without an `[approved]` entry in `docs/working/HIGH_RISK_APPROVALS.md`, repeated gate failures, ambiguous requirements, exceeded diff limits, or missing selected agent command.

## Evidence and Review
Every run folder should contain prompt, plan, changed files, validation outputs, risk assessment, review packet, and final summary. Frontend/API/database slices require matching evidence.
