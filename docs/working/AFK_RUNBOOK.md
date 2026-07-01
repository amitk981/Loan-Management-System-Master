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
1. Run preflight.
2. Confirm git state is safe.
3. Choose one eligible slice.
4. Create a run folder and prompt.
5. Create an isolated worktree unless disabled by config.
6. Start the selected agent through `scripts/agent-adapters/`.
7. Validate gates and Ralph artifacts.
8. Save changed files, risk assessment, review packet, and final summary.
9. Update state, progress, handoff, and slice status.
10. Commit only if gates pass and config allows it.

## Slice Selection
Use `.ralph/state.json` first. If architecture review is due, run it unless explicitly overridden. If the previous run failed, prefer repair. Otherwise choose the lowest-numbered `Not Started` slice.

## Quality Gates
Current repository gate is `npm run build` inside `sfpcl-lms/`. Lint, typecheck, and unit tests are documented gaps until scripts are added.

## Stopping Conditions
Stop on missing required files, unsafe git state, active locks, forbidden file edits, high risk, repeated gate failures, ambiguous requirements, exceeded diff limits, or missing selected agent command.

## Evidence and Review
Every run folder should contain prompt, plan, changed files, validation outputs, risk assessment, review packet, and final summary. Frontend/API/database slices require matching evidence.
