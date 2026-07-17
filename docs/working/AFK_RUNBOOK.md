# Ralph AFK Runbook

## Modes
- `bootstrap`: create or verify Ralph scaffolding. Does not implement product features.
- `normal`: pick one eligible vertical slice, create a worktree, run an agent, validate, save evidence, update state, and commit only passing work.
- `repair`: repair the previous failed slice in its existing quarantined worktree when structured repair context is available; no work is committed until full independent validation passes.
- `architecture-review`: independent quality review, run automatically by the loop every `architecture_review_every_completed_slices` slices. The reviewer does NOT modify production code. It must: (1) read the diffs of slices merged since the last review; (2) critique test quality — real assertions, edge cases, not just coverage numbers; (3) spot-check doc fidelity against the slice's source references and digests; (4) check for duplication and architecture drift; (5) write findings to `docs/working/REVIEW_FINDINGS.md` (append, newest first) and create or sharpen corrective slices for anything significant — every new slice must follow the to-issues slice standard so it executes seamlessly: a `## Status` of `Not Started`, a `## Depends On` section listing real slice ids (`- None` when unblocked; create blockers before dependents so references always resolve), and a numeric id that slots its filename at the intended queue position (name order breaks ties among grabbable slices; avoid non-numeric prefixes like `CR-`, which sort after every numeric slice). The orchestrator executes slices in dependency order regardless of name, and validation rejects any run that leaves the queue with dangling references, malformed sections, or dependency cycles; (6) record ADRs for durable decisions; (7) spot-check that the functional-spec requirement IDs (M##-FR-###) of each epic completed since the last review are implemented or explicitly deferred in ASSUMPTIONS.md; (8) verify `docs/working/CONTEXT.md` still describes the repository truthfully (it is read first by every run) and update it when reality has moved; (9) re-check every `Blocked` slice's stated prerequisites against `completed_slices` in `.ralph/state.json` and flip stale blocks back to `Not Started`. This is the independent second pair of eyes on work where the same agent wrote both code and tests.

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

Validation failures publish a trusted `.ralph/repair-context.json` in the integration checkout. During the active loop, a bounded repair re-enters that registered `ralph/*` worktree, reads the exact prior `failure-summary.md`, preserves the uncommitted slice implementation, and reruns full independent validation. A repeated normalized failure signature stops early; a different downstream failure may use the remaining configured repair budget. Repaired failures do not accumulate across otherwise successful slices.

Note on agent approval mode: codex runs headless (`exec` mode, approval mode `never`) because nobody is at the terminal during AFK runs. The human safety control is the orchestrator-level high-risk gate plus quality gates and this runbook — not interactive prompts.

## Slice Selection
Use `.ralph/state.json` first. If architecture review is due, run it unless explicitly overridden. If the previous run failed, prefer repair. Otherwise choose the lowest-numbered `Not Started` slice whose `## Depends On` prerequisites are all `Complete` or `Superseded` (the to-issues standard: a slice is grabbable only when its blockers are done). The orchestrator (`select_slice` in `scripts/ralph-run.sh`) enforces this and skips dependency-blocked slices, so never start a slice whose prerequisites are unmet — if the orchestrator hands you one anyway, that is a defect; stop and report rather than no-op. If every remaining slice is blocked, the run exits `queue_blocked` for human review instead of claiming the queue is empty.

## Quality Gates
Enforced by `scripts/ralph-validate.sh` on every run:
- Frontend (`sfpcl-lms/`): `npm run build`, `npm run typecheck`, `npm test` (vitest).
- Backend (`sfpcl_credit/`): `manage.py check`, full test suite, `makemigrations --check` (models and migrations must stay in sync), and coverage with a hard floor (`coverage_fail_under` in `.ralph/config.yaml`, currently 85%; measured 92% on 2026-07-02 — raise the floor as coverage grows, never lower it).
- Protected-paths check: the run fails if any guardrail file was modified.
- Slice-queue lint: the run fails if it leaves `docs/slices/` unexecutable — a slice with an unrecognized status, a pending slice without `## Depends On`, a dangling or ambiguous dependency reference, or a dependency cycle.
- Status-transition check: only the executed slice may change its `## Status`; architecture reviews may re-park other slices (`Blocked` <-> `Not Started`, `Superseded`) but no run may flip a slice it did not execute to `Complete`.
- Contract fidelity (checked in review, not by script): API-touching slices follow `docs/source/api-contracts.md` §3 (design principles), §6-8 (envelopes, errors, pagination) and §45 (idempotency for financial actions); model-touching slices follow `docs/source/data-model.md` §30 (indexing) and §34 (transactional integrity); backend module layout follows `docs/source/codebase-design.md`.

Slices that require the authoritative PostgreSQL five-race gate declare
`postgresql-five-race-acceptance` under an exact `## Runtime Capabilities` heading. The declaration
drives both the scoped Codex socket permission and independent orchestrator validation; unknown
capabilities fail closed. Ordinary and undeclared slices use the `:workspace` permission profile.
A failing gate fails the whole run; failing work is never committed, merged, or pushed. ESLint arrives via slice 002FL, then flip `quality_gates.lint` to true.

Ordinary `architecture-review` runs have a specialized documentation-only validation lane. The validator first proves that every candidate path is under `docs/`, one of the explicit bookkeeping files `.ralph/state.json` and `.ralph/progress.md`, or the current review's own `.ralph/runs/<run-id>/` evidence directory; product paths, configuration, and historical run evidence fail closed. Once that scope proof, the normal artifact checks, queue lint, and frozen-candidate hash pass, repeated frontend/backend product gates are recorded as deliberately skipped because the unchanged product commit already passed them. Oversized-slice queue rewrites use the same principle with their narrower queue-metadata allowlist. Normal and repair runs always retain the complete product gates.

Backend coverage uses two bounded Django workers through `scripts/ralph-parallel-backend-coverage.sh`. The complete test label, failure semantics, and configured coverage floor are unchanged; subprocess coverage is combined before the floor is enforced, and binary coverage data stays in an ephemeral directory. This was enabled only after the 2026-07-17 shadow pilot proved identical discovered/run/skip/failure/error counts and identical executed, missing, and excluded line sets. Set `quality_gates.backend_coverage_parallel_workers` to `1` for the serial fallback. `scripts/ralph-shadow-parallel-coverage.sh` remains available to repeat the serial-versus-parallel equivalence audit.

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

Full Codex/Claude transcripts are operator-local diagnostics, not committed evidence. Adapters retain them under the repository's common Git directory (`.git/ralph-agent-logs/`) for at most 20 runs or 14 days by default. Each committed run keeps a compact final excerpt, byte/line counts, session id, and SHA-256 digest in `evidence/terminal-logs/<agent>-summary.md`; the context trip-wire reads the retained raw log first and the compact session id after pruning. Historical committed transcripts are left untouched—this policy prevents new growth without rewriting history.
