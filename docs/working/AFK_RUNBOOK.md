# Ralph AFK Runbook

## Modes
- `bootstrap`: create or verify Ralph scaffolding. Does not implement product features.
- `normal`: pick one eligible vertical slice, create a worktree, run an agent, validate, save evidence, update state, and commit only passing work.
- `repair`: repair the previous failed slice in its existing quarantined worktree when structured repair context is available; no work is committed until full independent validation passes.
- `architecture-review`: independent quality review, run automatically by the loop every `architecture_review_every_completed_slices` slices. The reviewer does NOT modify production code. It must: (1) read the diffs of slices merged since the last review; (2) critique test quality — real assertions, edge cases, not just coverage numbers; (3) spot-check doc fidelity against the slice's source references and digests; (4) check for duplication and architecture drift; (5) write findings to `docs/working/REVIEW_FINDINGS.md` (append, newest first). Critical/High correctness, security, financial/data-integrity, or binding source-contract findings create immediate corrective work. Medium findings are grouped into the owning slice or epic-closure work; Low findings remain recorded unless they naturally combine with higher-severity work. Related symptoms are grouped by root owner rather than producing one slice per symptom. When an actionable existing root-owner slice already covers a new Critical/High finding, the packet maps it explicitly instead of creating duplicate work; otherwise it creates a new numeric `Not Started` corrective slice. The review packet reports findings closed, new findings by severity, corrective slices added, and existing corrective mappings; two reviews whose additions exceed closures trigger one root-boundary correction recommendation instead of further leaf patches. Every new slice must follow the to-issues slice standard so it executes seamlessly: a `## Status` of `Not Started`, a `## Depends On` section listing real slice ids (`- None` when unblocked; create blockers before dependents so references always resolve), and a numeric id that slots its filename at the intended queue position (name order breaks ties among grabbable slices; avoid non-numeric prefixes like `CR-`, which sort after every numeric slice). The orchestrator executes slices in dependency order regardless of name, and validation rejects any run that leaves the queue with dangling references, malformed sections, or dependency cycles; (6) record ADRs for durable decisions; (7) spot-check that the functional-spec requirement IDs (M##-FR-###) of each epic completed since the last review are implemented or explicitly deferred in ASSUMPTIONS.md; (8) verify `docs/working/CONTEXT.md` still describes the repository truthfully and keep it stable/current rather than appending run history; (9) re-check every `Blocked` slice's stated prerequisites against `completed_slices` in `.ralph/state.json` and flip stale blocks back to `Not Started`. This is the independent second pair of eyes on work where the same agent wrote both code and tests.

Review cadence is adaptive but fail-closed. It remains every four completed slices while a review finds any new Critical/High issue. Two consecutive reviews with zero new Critical/High findings expand the interval to eight; any later Critical/High finding resets it to four. An epic boundary always sets a review due regardless of the current interval, including the final project boundary. Boundary ownership comes from each slice's explicit `## Parent Epic` metadata, including CR slices; Ralph does not close an epic while any Not Started or Blocked slice owned by that epic remains. A due boundary is temporarily deferred in memory—not rewritten in tracked state—while explicit same-epic corrective work remains. A due review is otherwise a mandatory product-work barrier: Ralph allows two bounded attempts for transient or artifact failures and then stops without advancing the queue; it also refuses completion or product work unless a validated review clears the due flag. A deterministic convergence-cap rejection is classified separately and stops after one attempt instead of repeating the same full review.

`review-packet.md` convergence metrics and its semantic finding manifest are machine-validated before a review can merge. Corrective generations are tracked independently by stable `Root ID`, never by one global Epic/review counter: a new root begins at generation one, remapping the same root to a different corrective advances only that root, reusing the same pending corrective consumes no generation, and a `Closed` row removes that root's state. Each root admits one grouped corrective and at most one successor; closed or unrelated roots cannot exhaust another root's budget. After the same root reaches that cap, only a High-risk CR with an exact `## Architecture Review Finalizer` declaration (`Epic`, `Root ID`, and exhausted generation) may close it. The owner has preauthorized exactly one terminal finalizer per stable Root ID through the protected `[approved-finalizer-policy]`; exact legacy `[approved-finalizer]` entries remain supported. An independently validated review may therefore queue one terminal CR instead of exiting at the deterministic cap. If a reviewer first emits an ordinary successor, Ralph retains that quarantined review and performs one bounded metadata-only rewrite into the terminal CR instead of repeating the critique or terminating immediately. A terminal run must replay every original review probe's exact command and retain current-run green evidence; a narrower proxy regression cannot close the root. The transition retains the exhausted generation rather than inventing generation three and records every root grouped into the terminal finalizer, not only its primary root. If executable review evidence later disproves that completed finalizer, the protected `[approved-terminal-repair-policy]` permits one High-risk `## Architecture Review Recurrence Repair` of the same finalizer contract. Ralph rewrites the existing quarantined review once, retains unrelated validated findings, blocks ordinary product work behind the exact repair, and consumes the repair only after all declared gates pass. This does not create generation three or a second finalizer; any later recurrence remains a hard safety stop. Review agents cannot modify or widen either protected policy.

### Semantic finding closure contract

Every architecture review must give findings stable identities instead of relying on narrative and
aggregate counts. Its `review-packet.md` contains exactly one `## Finding Closure Manifest` section.
A clean review writes `- None`; otherwise it uses this exact table:

```markdown
| Finding ID | Root ID | Severity | Disposition | Reproducer | Corrective Slice | Closure Evidence |
|---|---|---|---|---|---|---|
| AR-010-OWNER-001 | ROOT-010-OWNER-DECISION | High | New | .ralph/runs/<review-run>/evidence/review-probes/owner-boundary.log | 010A1 | - |
```

- IDs are uppercase, hyphenated, and permanent. A recurrence is `Carried` under the same Finding ID
  and Root ID; it is never renamed as `New`. `New` IDs must not exist at the fixed point, while
  `Carried` and `Closed` IDs must already exist in the fixed-point `REVIEW_FINDINGS.md`.
- Each manifest row corresponds bijectively to one changed stable section in
  `docs/working/REVIEW_FINDINGS.md`, beginning `## <Finding ID>` and containing the exact standalone
  line `Root: <Root ID>`. Review changes outside those structured sections fail validation.
- Every row names a non-empty retained reproducer under the current review's committed
  `.ralph/runs/<run>/evidence/` tree. The evidence contains exact `Finding ID:` and `Root ID:` lines;
  Critical/High reproducers also contain a failing signal. `Closed` rows name similarly bound
  closure evidence with a positive passing signal, explicit zero exit, and no failure signal, and use `-` for Corrective Slice. Open Critical/High rows name exactly
  one actionable corrective.
- The manifest's `New` severities and `Closed` rows must equal `## Convergence Metrics`. Every ID and
  exact `Root: <Root ID>` is retained in `docs/working/REVIEW_FINDINGS.md`.
- A corrective named by the manifest carries this exact slice section, including explicit acceptance
  IDs. This is the executable interface between the reviewer and implementer:

```markdown
## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-OWNER-001 | ROOT-010-OWNER-DECISION | .ralph/runs/<review-run>/evidence/review-probes/owner-boundary.log | AC-1, AC-2 |
```

The same corrective slice labels every top-level acceptance criterion, and the union of those labels
must exactly equal the contract's Acceptance IDs—no promised criterion can remain outside evidence:

```markdown
## Acceptance Criteria
- [AC-1] Canonical owner rejection removes the identity from counts, pages, and rows.
- [AC-2] Detail, actions, and mutations reject the same identity through permanent public tests.
```

A product run whose slice has that section must create `review-closure-evidence.md` in its current
run folder before independent validation:

```markdown
## Finding Evidence
| Finding ID | Root ID | Permanent Test | RED Evidence | GREEN Evidence |
|---|---|---|---|---|
| AR-010-OWNER-001 | ROOT-010-OWNER-DECISION | backend/tests/test_owner.py::test_boundary | evidence/terminal-logs/owner-red.log | evidence/terminal-logs/owner-green.log |

## Acceptance Evidence
| Acceptance ID | Test | Evidence |
|---|---|---|
| AC-1 | backend/tests/test_owner.py::test_boundary | evidence/terminal-logs/owner-green.log |
| AC-2 | backend/tests/test_owner.py::test_matrix | evidence/terminal-logs/owner-matrix.log |
```

The validator reads the closure contract from the fixed-point slice, requires the candidate slice
to remain byte-for-byte identical, and checks exact ID/root continuity, a discoverable permanent
test file plus parser/declaration-resolvable selector (either `path/to/test.py::Class::test_name` or
an exact Django dotted test label), distinct non-empty RED and GREEN logs containing that exact test
specification and failing/positive-passing-plus-explicit-zero-exit signals, and exactly one similarly bound evidence row for every
declared acceptance ID. Missing, ignored, unrelated, or candidate-weakened evidence stops before
expensive product gates and repairs the same slice; a green full suite cannot substitute for this
closure contract. A blank line terminates each machine-readable Markdown table, so explanatory prose
may follow that boundary without becoming a malformed row. Corrective agents must run the exact fast
preflight printed in their prompt—`scripts/ralph-validate-review-closure.sh`—until it passes before
returning; repair agents likewise clear every error revealed by that same validator in one bounded
validation-domain repair rather than consuming one turn per formatting symptom.

## Start Commands
- Run the whole queue autonomously ("run ralph loop"): `./scripts/ralph-loop.sh`
- Run unattended with safe process restarts: `./scripts/ralph-supervise.sh`
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

Validation failures publish a trusted `.ralph/repair-context.json` in the integration checkout. During the active loop, a bounded repair re-enters that registered `ralph/*` worktree, reads the exact prior `failure-summary.md`, preserves the uncommitted candidate, and reruns full independent validation. Documentation-only architecture-review validation failures use the same candidate and exact summary instead of repeating the complete critique in a fresh worktree; convergence, protected-scope, and unsafe-state outcomes remain separately classified. A repeated normalized failure signature receives one repair and then stops; a genuinely different downstream failure may use the remaining progressive budget. Repaired failures do not accumulate across otherwise successful slices.

An oversized product slice follows a separate bounded planning-recovery path. Ralph first discards the ungated product worktree and asks an architecture-review run to rewrite only the queue metadata. If that rewrite fails the dedicated oversized-slice split validator, Ralph records the exact failing paths and rules, discards the rejected planning worktree, and allows one clean corrective planning attempt that reads those diagnostics. A passing correction is committed, merged, pushed, and the loop resumes queue selection automatically. A second planning failure, an untrusted or unrelated failure, or a commit/merge failure stops safely; rejected planning diffs are never salvaged and the retry is never unbounded.

Note on agent approval mode: codex runs headless (`exec` mode, approval mode `never`) because nobody is at the terminal during AFK runs. The human safety control is the orchestrator-level high-risk gate plus quality gates and this runbook — not interactive prompts.

## Slice Selection
Use `.ralph/state.json` first. If architecture review is effectively due, it must pass before any product slice runs; an epic-boundary reason is effectively deferred only while a queued slice still declares that same Parent Epic. If the previous run failed and a trusted resumable repair context exists, repair that exact quarantined worktree. A failure before any candidate/context exists is not product-repairable and stops immediately with its original preflight/infrastructure diagnosis. Otherwise choose the lowest-numbered `Not Started` slice whose `## Depends On` prerequisites are all `Complete` or `Superseded` (the to-issues standard: a slice is grabbable only when its blockers are done). An owner-supplied `--slice` must resolve to exactly one eligible slice; the only exception is the same unfinished slice named by a resumable trusted repair context. The orchestrator (`select_slice` in `scripts/ralph-run.sh`) enforces this and skips dependency-blocked slices, so never start a slice whose prerequisites are unmet — if the orchestrator hands you one anyway, that is a defect; stop and report rather than no-op. If every remaining slice is blocked, the run exits `queue_blocked` for human review instead of claiming the queue is empty.

## Quality Gates
Enforced by `scripts/ralph-validate.sh` on every run:
- Frontend (`sfpcl-lms/`): `npm run build`, `npm run typecheck`, `npm test` (vitest).
- Backend (`sfpcl_credit/`): `manage.py check`, `makemigrations --check` (models and migrations must stay in sync), and either an independently derived impacted regression pack or complete-suite coverage with a hard floor (`coverage_fail_under` in `.ralph/config.yaml`, currently 85%; measured above 91% in the 2026-07-17 full-suite proof — raise the floor as coverage grows, never lower it). Complete coverage is mandatory for every fail-closed classification and every fourth completed product slice.
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

Ordinary `architecture-review` runs have a specialized documentation-only validation lane. The validator first proves that every agent-authored candidate path is under `docs/` or the current review's own `.ralph/runs/<run-id>/` evidence directory; product paths, configuration, orchestrator-owned state/progress, and historical run evidence fail closed. Every newly generated corrective slice must also pass the same trusted runtime-capability and PostgreSQL-acceptance contracts used by normal slice selection before the review may commit; a missing or inconsistent declaration therefore repairs the quarantined review candidate instead of terminating the following product run before a worktree exists. Once that scope proof, the normal artifact checks, queue lint, runtime contracts, and frozen-candidate hash pass, repeated frontend/backend product gates are recorded as deliberately skipped because the unchanged product commit already passed them. The orchestrator then applies state, progress, and status facts. Oversized-slice queue rewrites use the same principle with their narrower queue-metadata allowlist.

Normal and repair runs use `quality_gates.backend_validation_policy: selective`. The validator records its classification, binding lane, reason, changed paths, and independently derived impacted labels in `backend-validation-lane-results.md`, then dispatches exactly one authoritative backend test lane. A localized Low/Medium backend change runs only every changed test module, every repository test module whose parsed Python imports reference the changed production root, and the root's maintained route/contract ownership patterns in `scripts/config/ralph-backend-test-impact.json`; it does not also run complete coverage. Missing or invalid ownership fails closed to complete coverage. Complete coverage alone is required for High risk, every fourth completed product slice, the terminal product slice of an epic, migrations/models/configuration/routing/dependencies, package-root or shared-root changes, multiple backend modules, broad changes, deletions/renames, missing tests, or tests that cannot be mapped to the changed module. Low/Medium frontend/docs-only candidates retain the cheap Django and migration-consistency checks but skip backend test/coverage execution unless they are the periodic or epic checkpoint. The full checkpoint retains the complete label and 85% floor; an impacted lane never claims global coverage. Release complete-suite checkpoints remain mandatory through release CI, without preceding them with the impacted pack.

Backend gates are ordered from cheap to expensive. A failed Django system check, migration consistency check, or required browser contract records the failure and defers the selected backend test lane to the repair attempt. Both impacted and complete test lanes use Django fail-fast only after the candidate is red; green candidates still execute their entire selected label set. A failed impacted pack is repaired with the impacted lane again rather than escalating into a duplicate complete-suite run. This changes failure latency, not passing acceptance scope.

GitHub CI also runs the complete suite on `staging`, `main`, and pull requests. Superseded runs on the same ref are cancelled, dependencies use the setup-python pip cache, complete coverage runs through the shared helper with four workers to match the public runner's CPU allocation, and the backend job has a 45-minute infrastructure cap. `.github/workflows/backend-serial-canary.yml` separately runs the complete suite serially every night against `staging`, and can be dispatched manually at epic and release checkpoints to detect order or multiprocessing-only defects.

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
- `scripts/ralph-supervise.sh` is the recommended overnight entry point. It restarts the loop only after replay-safe process outcomes (agent limit, bounded browser infrastructure failure, iteration limit, or a killed child), relying on startup recovery before work resumes. Validation, convergence without an admitted terminal finalizer, unsafe state, merge ambiguity, policy, and owner-veto outcomes remain hard stops so the supervisor cannot turn a deterministic defect into an infinite loop.

## Evidence and Review
Every run folder should contain prompt, plan, changed files, validation outputs, risk assessment, review packet, and final summary. Frontend/API/database slices require matching evidence.
Evidence artifacts must be self-contained and reviewable after the run ends: the run's worktree is deleted on completion, so evidence files must never reference worktree paths, `dist/` build outputs, or anything outside the run folder. Inline built CSS/assets directly into evidence HTML (or copy them into the evidence folder and link relatively). A run that produced evidence 2026-07-07 (004A) linked its stylesheet from the worktree via absolute `file://` path; the pages rendered unstyled by the time the owner reviewed them.

Full Codex/Claude transcripts are operator-local diagnostics, not committed evidence. Adapters retain them under the repository's common Git directory (`.git/ralph-agent-logs/`) for at most 20 runs or 14 days by default. Each committed run keeps a compact final excerpt, byte/line counts, session id, and SHA-256 digest in `evidence/terminal-logs/<agent>-summary.md`; the context trip-wire reads the retained raw log first and the compact session id after pruning. Historical committed transcripts are left untouched—this policy prevents new growth without rewriting history.
