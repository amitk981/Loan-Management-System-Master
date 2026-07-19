# Ralph AFK Runbook

## Modes
- `bootstrap`: create or verify Ralph scaffolding. Does not implement product features.
- `normal`: pick one eligible vertical slice, create a worktree, run an agent, validate, save evidence, update state, and commit only passing work.
- `repair`: repair the previous failed slice in its existing quarantined worktree when structured repair context is available; no work is committed until full independent validation passes.
- `architecture-review`: independent quality review, run automatically by the loop every `architecture_review_every_completed_slices` slices. The reviewer does NOT modify production code. It must: (1) read the diffs of slices merged since the last review; (2) critique test quality — real assertions, edge cases, not just coverage numbers; (3) spot-check doc fidelity against the slice's source references and digests; (4) check for duplication and architecture drift; (5) write findings to `docs/working/REVIEW_FINDINGS.md` (append, newest first). Critical/High correctness, security, financial/data-integrity, or binding source-contract findings create immediate corrective work. Medium findings are grouped into the owning slice or epic-closure work; Low findings remain recorded unless they naturally combine with higher-severity work. Related symptoms are grouped by root owner rather than producing one slice per symptom. When an actionable existing root-owner slice already covers a new Critical/High finding, the packet maps it explicitly instead of creating duplicate work; otherwise it creates a new numeric `Not Started` corrective slice. The review packet reports findings closed, new findings by severity, corrective slices added, and existing corrective mappings; two reviews whose additions exceed closures trigger one root-boundary correction recommendation instead of further leaf patches. Every new slice must follow the to-issues slice standard so it executes seamlessly: a `## Status` of `Not Started`, a `## Depends On` section listing real slice ids (`- None` when unblocked; create blockers before dependents so references always resolve), and a numeric id that slots its filename at the intended queue position (name order breaks ties among grabbable slices; avoid non-numeric prefixes like `CR-`, which sort after every numeric slice). The orchestrator executes slices in dependency order regardless of name, and validation rejects any run that leaves the queue with dangling references, malformed sections, or dependency cycles; (6) record ADRs for durable decisions; (7) spot-check that the functional-spec requirement IDs (M##-FR-###) of each epic completed since the last review are implemented or explicitly deferred in ASSUMPTIONS.md; (8) verify `docs/working/CONTEXT.md` still describes the repository truthfully and keep it stable/current rather than appending run history; (9) re-check every `Blocked` slice's stated prerequisites against `completed_slices` in `.ralph/state.json` and flip stale blocks back to `Not Started`. This is the independent second pair of eyes on work where the same agent wrote both code and tests.

Review cadence is adaptive but fail-closed. It remains every four completed slices while a review finds any new Critical/High issue. Two consecutive reviews with zero new Critical/High findings expand the interval to eight; any later Critical/High finding resets it to four. An epic boundary always sets a review due regardless of the current interval, including the final project boundary. A due review is a mandatory product-work barrier: Ralph allows two bounded attempts and then stops without advancing the queue; it also refuses completion or product work unless a validated review clears the due flag. `review-packet.md` convergence metrics are machine-validated against corrective slice additions before a review can merge.

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
4. Check the owner veto list; High-risk work otherwise proceeds under standing approval.
5. Create a run folder and prompt.
6. Create an isolated worktree unless disabled by config.
7. Start the selected agent through `scripts/agent-adapters/`.
8. Validate gates and Ralph artifacts.
9. Save substantive risk, test, review, and final-summary evidence; the orchestrator records changed files.
10. After validation passes, the orchestrator alone updates state, progress, mechanical handoff, and slice status.
11. Commit only if gates pass and config allows it.
12. If `auto_merge` is enabled, fast-forward merge the run branch into the `staging` integration branch and remove the worktree; on merge failure the branch is kept for manual review. The owner alone promotes staging to main (`docs/working/RELEASE_PROMOTION.md`).

Validation failures publish a trusted `.ralph/repair-context.json` in the integration checkout. During the active loop, a bounded repair re-enters that registered `ralph/*` worktree, reads the exact prior `failure-summary.md`, preserves the uncommitted slice implementation, and reruns full independent validation. A repeated normalized failure signature stops early; a different downstream failure may use the remaining configured repair budget. Repaired failures do not accumulate across otherwise successful slices.

An oversized product slice follows a separate bounded planning-recovery path. Ralph first discards the ungated product worktree and asks an architecture-review run to rewrite only the queue metadata. If that rewrite fails the dedicated oversized-slice split validator, Ralph records the exact failing paths and rules, discards the rejected planning worktree, and allows one clean corrective planning attempt that reads those diagnostics. A passing correction is committed, merged, pushed, and the loop resumes queue selection automatically. A second planning failure, an untrusted or unrelated failure, or a commit/merge failure stops safely; rejected planning diffs are never salvaged and the retry is never unbounded.

Note on agent approval mode: codex runs headless (`exec` mode, approval mode `never`) because nobody is at the terminal during AFK runs. The human safety control is the orchestrator-level high-risk gate plus quality gates and this runbook — not interactive prompts.

## Slice Selection
Use `.ralph/state.json` first. If architecture review is due, it must pass before any product slice runs. If the previous run failed, prefer repair. Otherwise choose the lowest-numbered `Not Started` slice whose `## Depends On` prerequisites are all `Complete` or `Superseded` (the to-issues standard: a slice is grabbable only when its blockers are done). An owner-supplied `--slice` must resolve to exactly one eligible slice; the only exception is the same unfinished slice named by a resumable trusted repair context. The orchestrator (`select_slice` in `scripts/ralph-run.sh`) enforces this and skips dependency-blocked slices, so never start a slice whose prerequisites are unmet — if the orchestrator hands you one anyway, that is a defect; stop and report rather than no-op. If every remaining slice is blocked, the run exits `queue_blocked` for human review instead of claiming the queue is empty.

## Quality Gates
Enforced by `scripts/ralph-validate.sh` on every run:
- Frontend (`sfpcl-lms/`): `npm run build`, `npm run typecheck`, `npm test` (vitest).
- Backend (`sfpcl_credit/`): `manage.py check`, full test suite, `makemigrations --check` (models and migrations must stay in sync), and coverage with a hard floor (`coverage_fail_under` in `.ralph/config.yaml`, currently 85%; measured above 91% in the 2026-07-17 full-suite proof — raise the floor as coverage grows, never lower it).
- Protected-paths check: the run fails if any guardrail file was modified.
- Slice-queue lint: the run fails if it leaves `docs/slices/` unexecutable — a slice with an unrecognized status, a pending slice without `## Depends On`, a dangling or ambiguous dependency reference, or a dependency cycle.
- Status-transition check: only the executed slice may change its `## Status`; architecture reviews may re-park other slices (`Blocked` <-> `Not Started`, `Superseded`) but no run may flip a slice it did not execute to `Complete`.
- Contract fidelity (checked in review, not by script): API-touching slices follow `docs/source/api-contracts.md` §3 (design principles), §6-8 (envelopes, errors, pagination) and §45 (idempotency for financial actions); model-touching slices follow `docs/source/data-model.md` §30 (indexing) and §34 (transactional integrity); backend module layout follows `docs/source/codebase-design.md`.

Slices that require authoritative PostgreSQL acceptance declare the legacy-compatible capability id
`postgresql-five-race-acceptance` under an exact `## Runtime Capabilities` heading. Despite the
retained name, the gate now executes the slice-owned exact Django labels and positive expected count
twice in isolated databases; it is not a hard-coded five-test suite. The declaration drives both the
scoped Codex socket permission and independent orchestrator validation; unknown capabilities fail
closed. Ordinary slices explicitly declare `none` and use the `:workspace` permission profile.
A failing gate fails the whole run; failing work is never committed, merged, or pushed. ESLint arrives via slice 002FL, then flip `quality_gates.lint` to true.

Ordinary `architecture-review` runs have a specialized documentation-only validation lane. The validator first proves that every agent-authored candidate path is under `docs/` or the current review's own `.ralph/runs/<run-id>/` evidence directory; product paths, configuration, orchestrator-owned state/progress, and historical run evidence fail closed. Once that scope proof, the normal artifact checks, queue lint, and frozen-candidate hash pass, repeated frontend/backend product gates are recorded as deliberately skipped because the unchanged product commit already passed them. The orchestrator then applies state, progress, and status facts. Oversized-slice queue rewrites use the same principle with their narrower queue-metadata allowlist.

Normal and repair runs use `quality_gates.backend_validation_policy: shadow`. The validator records a non-authoritative future lane recommendation in `backend-validation-lane-results.md`, but every candidate still executes the complete configured backend gates. Recommendations fail closed to `full` for High risk, every fourth completed slice, migrations/models/configuration/routing/dependencies, package-root or shared-root changes, multiple backend modules, broad changes, deletions/renames, missing tests, or tests that cannot be mapped to the one changed backend module. This shadow data can quantify likely savings and false classifications before any proposal to amend the binding quality policy; it cannot skip or replace a gate.

GitHub CI also runs the complete suite on `staging`, `main`, and pull requests. Superseded runs on the same ref are cancelled, dependencies use the setup-python pip cache, and complete coverage runs through the shared helper with four workers to match the public runner's CPU allocation. `.github/workflows/backend-serial-canary.yml` separately runs the complete suite serially every night against `staging`, and can be dispatched manually at epic and release checkpoints to detect order or multiprocessing-only defects.

Backend coverage uses six bounded Django workers through `scripts/ralph-parallel-backend-coverage.sh`. The complete test label, failure semantics, and configured coverage floor are unchanged; subprocess coverage is combined before the floor is enforced, and binary coverage data stays in an ephemeral directory. Corrected 2026-07-17 shadow pilots proved identical discovered/run/skip/failure/error counts and identical executed, missing, and excluded line sets at both six and eight workers. Six is enabled because it completed in 362.9 seconds versus 381.5 seconds for eight on the current 8-core host. Set `quality_gates.backend_coverage_parallel_workers` to `1` for the serial fallback. `scripts/ralph-shadow-parallel-coverage.sh` remains available to repeat the serial-versus-parallel equivalence audit.

## Stopping Conditions
Stop on missing required files, unsafe git state, active locks, protected/forbidden file edits, an owner veto (`[revoked]` in HIGH_RISK_APPROVALS.md), repeated gate failures, actions on the DECISION_POLICY never-do list, exceeded diff limits, an unrecoverable or repeatedly failed oversized-slice rewrite, or a missing selected agent command. An exceeded diff limit stops the oversized product implementation; the bounded queue-rewrite path above may then replace it with smaller successors and resume queue selection. Ambiguity and high risk are NOT stopping conditions — they are handled by DECISION_POLICY.md and the standing approval.

## Maintenance Stage (Change Requests)
After the product backlog is finished, changes enter only through `docs/change-requests/` (see its README):
1. The owner (with agent help) fills the strict bug/feature template into `inbox/`.
2. `./scripts/ralph-intake.sh` validates it mechanically. Invalid → rejected with precise errors, nothing enters the pipeline, no code changes. Valid → converted to a `CR-NNN` slice; cross-stack bugs and features are High risk (veto-able as usual).
3. The normal loop implements CR slices with all standard gates PLUS the impact-analysis gate: the run must map affected modules, blast radius, and per-module regression tests in `impact-analysis.md` before code changes; validation fails without it.
4. Intake refuses new CRs while product slices remain (`--now` is the owner's emergency override).
Agents must never implement chat-reported bugs directly — template first, always.

## Interrupted Runs and Recovery
A run can die mid-flight (usage-limit exhaustion, crash, closed terminal) under either agent. Recovery is automatic and agent-agnostic:
- `./scripts/ralph-loop.sh` runs `scripts/ralph-recover.sh` at startup. Trusted ownership metadata under the common Git directory associates one stable worktree with every normal and repair run id that used it. If the process dies in the tiny bootstrap interval after `git worktree add` but before that metadata write, recovery accepts only an exact dead/live root lock whose run id, recorded worktree, registered Ralph branch, and existing slice stem all agree, then materializes the same ownership record. Recovery skips any worktree with an associated live lock, salvages every matching run's artifacts into `.ralph/runs/<run-id>/`, removes only the dead worktree, keeps any branch with unmerged commits, and clears only stale associated locks and a repair context that names that same dead worktree. The still-queued slice then reruns automatically.
- Preflight independently auto-removes locks whose owning process is dead; a surviving lock means a run is genuinely still active.
- Rerunning is always safe: slice status only flips to Complete at the end of a fully-gated run. Never salvage partial work from an interrupted run.
- Before a manual single run (`afk-dev.sh`), run `./scripts/ralph-recover.sh` first.

## Evidence and Review
Every run folder should contain prompt, plan, changed files, validation outputs, risk assessment, review packet, and final summary. Frontend/API/database slices require matching evidence.
Evidence artifacts must be self-contained and reviewable after the run ends: the run's worktree is deleted on completion, so evidence files must never reference worktree paths, `dist/` build outputs, or anything outside the run folder. Inline built CSS/assets directly into evidence HTML (or copy them into the evidence folder and link relatively). A run that produced evidence 2026-07-07 (004A) linked its stylesheet from the worktree via absolute `file://` path; the pages rendered unstyled by the time the owner reviewed them.

Full Codex/Claude transcripts are operator-local diagnostics, not committed evidence. Adapters retain them under the repository's common Git directory (`.git/ralph-agent-logs/`) for at most 20 runs or 14 days by default. Each committed run keeps a compact final excerpt, byte/line counts, session id, and SHA-256 digest in `evidence/terminal-logs/<agent>-summary.md`; the context trip-wire reads the retained raw log first and the compact session id after pruning. Historical committed transcripts are left untouched—this policy prevents new growth without rewriting history.
