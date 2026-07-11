# Production Completion Blueprint

Independent audit of Ralph automation, session context, source traceability, prototype fidelity,
and the path from the current slice queue to a production-ready SFPCL application.

Audit snapshot: 2026-07-11 00:10 IST, after slice 004E completed at commit c25950f. This document
does not amend or depend on CONTEXT_FLOW_AUDIT_AND_COMPLETION_PLAN.md. Claims below were checked
against the current scripts, configuration, slice files, source specifications, code, run
artifacts, and Codex rollout telemetry.

---

## 1. Executive decision

Ralph is already a useful implementation engine: it isolates work, limits a run to one selected
slice, runs substantial frontend and backend checks, preserves evidence, and integrates through
staging. It is not yet a production-completion system.

Three different states must not be treated as synonyms:

| State | What it currently proves | What it does not prove |
|---|---|---|
| Slice Complete | One worktree passed the configured mechanical gates and its slice file was marked Complete. | Full source coverage, dependency correctness, visual parity, production deployment, or business acceptance. |
| Queue Empty | No slice file still says Not Started; Blocked files can still exist under the current selector. | That every source requirement and screen has an owner, that all review debt is closed, or that the product can safely go live. |
| Production Ready | Signed-off scope is implemented, traced, production-like, secure, operable, visually accepted, migrated, and validated by business users. | This state does not exist merely because the queue is empty. |

The recommended project shape is therefore:

1. Keep Ralph for bounded vertical implementation.
2. Add a separate, small context-preparation stage before implementation sessions.
3. Make slice readiness, dependencies, evidence, integration, and publication fail closed.
4. Turn the prototype into an immutable, testable design contract rather than a mutable reference.
5. Add explicit production-assurance work before the final UAT and promotion.
6. Let the owner promote staging only after every production gate in section 9 is evidenced.

The highest-risk misconception to avoid is “all current slices complete means finished product.”
The source roadmap places performance, migration, UAT execution, training, production
infrastructure, monitoring, backup/restore, cutover, rollback, and hypercare inside release R8.
The present tail of the queue does not yet implement or prove all of those outcomes.

---

## 2. Current delivery snapshot

### 2.1 Slice inventory

The source of truth for this table is each file's exact Status value in docs/slices, not the
hand-maintained implementation index.

| Group | Total files | Complete | Not Started | Superseded | Current interpretation |
|---|---:|---:|---:|---:|---|
| 001 | 1 | 1 | 0 | 0 | Bootstrap complete |
| 002 | 23 | 23 | 0 | 0 | Platform/auth foundation complete |
| 003 | 15 | 15 | 0 | 0 | Audit/document/config foundations complete |
| 004 | 14 | 14 | 0 | 0 | All current Epic 004 slice files are Complete; delivered backend/product gaps remain below |
| 005 | 18 | 18 | 0 | 0 | Intake cluster marked complete; Completeness Workbench is still mock-backed |
| 006 | 24 | 19 | 4 | 1 | 006G2, 006H2, 006H3, and 006X remain |
| 007 | 10 | 0 | 10 | 0 | Sanction and approval |
| 008 | 13 | 0 | 13 | 0 | Documentation and security package |
| 009 | 11 | 0 | 11 | 0 | SAP, account creation, and disbursement |
| 010 | 14 | 0 | 14 | 0 | Servicing, repayment, interest, and monitoring |
| 011 | 17 | 0 | 17 | 0 | Default, recovery, closure, and compliance |
| 012 | 12 | 0 | 12 | 0 | Reports, hardening, and release readiness |
| CR | 1 | 0 | 1 | 0 | CR-001 deterministic visual baselines |
| **Total** | **173** | **90** | **82** | **1** | **77 future epic slices, 4 Epic 006 slices, and CR-001 remain** |

There are no Blocked slice files at this snapshot. Superseded work must be excluded from completion
percentages. The default loop invocation runs at most 25 iterations, so it cannot drain the
remaining queue even if every run succeeds; an owner can explicitly supply a larger limit.

### 2.2 Planning quality snapshot

- 66 of the 82 Not Started slices still contain the generic template goal or generic backend
  scope. The most consequential generic files include 007A-007I, most of Epic 008-011, and
  012F, 012G, and 012I.
- The implementation index contains fewer entries than the actual slice directory and omits
  corrective, superseded, and CR slices. It is not safe as the queue ledger.
- The Feature Matrix, Risk Register, and API_SCREEN_MAP still describe early prototype/mock-data
  conditions. They are useful history, not current truth.
- The source functional specification contains 217 unique M##-FR-### identifiers. Only 35 are
  explicitly named in current slices, epics, assumptions, or review findings. This does not prove
  that the other 182 requirements are missing; it proves that current planning cannot demonstrate
  their coverage.
- A broader exact-token scan found 606 unique source requirement, acceptance, security, E2E, and
  UAT IDs, but only 24 of those exact tokens in epics/slices. The reproducible extraction rule is
  recorded in section 12. Section references are useful for implementation, but are too coarse for
  final sign-off.
- ASSUMPTIONS.md contains 62 recorded assumptions; 48 say Needs Confirmation = Yes. A production
  gate needs an explicit disposition, owner, and evidence for the high-impact subset.

---

## 3. The automation that actually runs

Only behavior consumed by the scripts is treated as enforced here. Configuration keys or prose
that no script evaluates are classified as advisory.

~~~mermaid
flowchart TD
    A["Owner starts ralph-loop.sh"] --> B["Recover interrupted worktrees"]
    B --> C{"Architecture review due?"}
    C -- "Yes" --> D["Run architecture review"]
    D --> E{"Review passed?"}
    E -- "No" --> F["Log failure and continue"]
    E -- "Yes" --> G
    C -- "No" --> G["Run one normal iteration"]
    F --> G
    G --> H["Preflight and select first filename-sorted Not Started slice"]
    H --> I["Create branch, worktree, prompt, and artifact templates"]
    I --> J["Run Codex with watchdog"]
    J --> K["Independent configured validation"]
    K -- "Fail" --> L["Run one repair session"]
    K -- "Pass" --> M["Update status, state, handoff, and progress"]
    L --> K
    M --> N["Attempt commit"]
    N --> O["Attempt fast-forward merge to staging"]
    O --> P["Attempt push of staging"]
    P --> Q["Post-run advisory context tripwire"]
    Q --> C
~~~

Current terminal paths sit beside that happy path: owner veto and merge failure stop immediately;
agent usage exhaustion exits 3 because the configured loop is Codex-only with fallback disabled;
a failed repair stops; and three normal iterations that required repair stop the loop. Reaching the
default 25-iteration limit exits cleanly without implying queue completion.

### 3.1 Controls that are substantively enforced

- Ralph refuses to run outside the staging integration branch.
- The default normal path uses an isolated worktree with a dedicated branch and watchdog.
- The owner veto list is checked before a selected slice starts.
- Frontend build, typecheck, ESLint, and Vitest are configured as required.
- Django check, migration drift, and the full backend suite under coverage are required. The
  current floor is 85%.
- Protected paths are hard-coded in the validator.
- Normal runs must produce a non-.ralph change, except the narrowly special-cased PostgreSQL
  acceptance slice; documentation/status-only changes can currently satisfy this check.
- Normal/repair diffs are capped at 30 non-.ralph files and 2,000 changed non-.ralph lines.
- An explicitly failed, blocked, or “do not commit/merge” review packet now fails validation.
- Interrupted worktrees can be recovered without salvaging ungated product changes.
- Fast-forward merge failure stops the outer loop and preserves the completed branch.
- Only the owner promotes staging to main.

These are worth preserving. They explain why the project has been able to deliver a large number
of slices quickly without directly pushing agent work to main.

### 3.2 Controls that are partial, advisory, or absent

| Concern | Current behavior | Production consequence |
|---|---|---|
| Commit and publication | Commit failure is swallowed; a disabled merge can still exit successfully; push failure is explicitly non-fatal. | “Run success” can mean validated but not integrated or published. |
| Worktree/commit bypasses | afk-dev.sh accepts --no-worktree and --no-commit even though configuration implies otherwise. The first can commit directly on local staging without merge/push; the second can validate and exit 0 with stranded work. | The normal isolation/publication invariant is bypassable. |
| Recovery | The outer loop does not fail closed on a nonzero recovery command. | New work can start after cleanup/reconciliation failed. |
| Repair identity | Repair selects the generic lowest Not Started slice; the outer loop does not pass the failed slice ID; repair lacks the normal no-op check. | A repair can work on the wrong slice or pass without a real product change. |
| Dependency graph | Depends On is prose. Selection checks only filename order and Status. | A slice can start before its declared prerequisites if ordering or corrective insertion diverges. |
| No-op classification | Any non-.ralph change—including only slice status, handoff, or other documentation—satisfies the normal no-op gate. | Validation does not prove the requested product behavior changed. |
| Slice readiness | Generic slices are sharpened inside the implementation session. | Correctness has a fallback, but source discovery consumes the same context needed for code and review. |
| Architecture review | A failed architecture review is logged as non-fatal and normal work continues. | The queue can finish with unresolved reviewer failure or review debt. |
| Review/evidence packet | The default In Progress review result is not treated as failure, and the detailed agent summary is overwritten with generic success after validation. | A run can pass without an explicit positive review or complete evidence narrative. |
| Live state | State is updated mainly after success. It does not reliably record run start, active worktree, failure, retry, or new successful commit SHA. | State alone cannot answer what is running or whether a publication completed. |
| Model profiles | YAML declares models/profiles, but the adapter leaves CODEX_MODEL empty unless an environment override is supplied. | The actual model and context window can change silently. |
| permissions.json | The file is syntax-checked, while the validator uses a separate hard-coded protected list. | allowed_without_approval and requires_approval are not true enforcement lists. |
| Config completeness | Several keys are never consumed, including profile selection, dependency/migration caps, integration/e2e gates, and some risk/worktree flags. | Configuration can imply protections that do not exist. |
| TDD evidence | TDD and red/green logs are prompt requirements, not mechanically verified. | A slice can pass without proving the required red-first sequence. |
| Visual evidence | Screenshots and prototype parity are prompt/review requirements only. | A frontend slice can pass all configured gates with no visual proof. |
| Integration and E2E | integration_tests is disabled and e2e_tests is optional; the validator has no implementation for them. CI has no Playwright job. | Cross-service and browser regressions are not release blockers. |
| Production database | Routine backend gates use SQLite. PostgreSQL is special-cased only for completed slice 006F4. | Production-only locking, constraint, and transaction behavior is under-tested. |
| Context tripwire | It runs after a session and is explicitly non-fatal. | It records an overfull session only after quality may already have degraded. |
| Queue and loop completion | The default loop exits 0 after 25 iterations; queue-empty checks only for Not Started, while Blocked can remain. Maintenance intake also ignores Blocked non-CR work. | Process completion and queue-empty are not backlog or production completion. |
| Evidence storage | Thousands of raw run files and logs are committed into every worktree. | Checkout, disk, push, search noise, and accidental context ingestion grow every slice. |

### 3.3 Automation hardening order

Schedule these owner-side protected-script changes at the next safe checkpoint; do not modify the
active Ralph worktree to make them.

1. **Make entry and completion transactional.** Before spending a run, fetch and fail on unsafe
   remote divergence. Forbid --no-worktree/--no-commit in autonomous normal mode. A run is
   successful only after validation, commit, fast-forward integration, and required remote push all
   succeed. Record branch, commit, merge, and push SHAs in a compact run manifest; use a distinct
   “validated but unpublished” outcome rather than success.
2. **Fail closed on recovery.** Do not select or create new work until recovery returns success and
   state/worktree/Git reconciliation passes.
3. **Bind repair to the failure.** Persist failed run ID and slice ID, pass both to repair, read
   failure-summary first, and apply the non-no-op and dependency gates to repair too.
4. **Enforce dependency and readiness checks before worktree creation.** Every dependency must be
   Complete, or its replacement chain must be Complete, unless an explicit owner waiver removes
   the capability. Require a concrete slice and a classified product/evidence change—not merely
   any documentation edit.
5. **Make evidence explicit and fail closed.** Require Result = Pass/Success and a slice-type
   evidence matrix before status/commit: red/green for backend/business logic, API/database proof
   where applicable, and browser/visual/accessibility proof for UI. Preserve or synthesize the
   detailed final packet instead of overwriting it.
6. **Pin the execution profile.** Resolve model, reasoning effort, verbosity, allowed mode, and
   expected minimum context window from config; pass them to the adapter and record the actual
   model/window from telemetry.
7. **Make architecture review release blocking.** Retry a failed review or stop. A final clean
   review is mandatory before queue completion can advance to production review.
8. **Make state a derived, reconciled ledger.** Record run start/failure/success, current slice,
   worktree, retry count, commit/push outcome, and review debt. Validate state against slice files
   and Git before showing progress.
9. **Unify permissions and configuration enforcement.** Validate that every supported key is
   consumed; reject unknown/decorative safety keys; enforce approval/protected patterns from one
   canonical policy.
10. **Reduce evidence weight.** Keep a compact immutable manifest, summaries, hashes, and essential
   proof in Git. Store raw multi-megabyte terminal logs, videos, and full screenshot bundles in
   bounded artifact storage with retention and secret redaction. At this audit, HEAD tracked about
   4,417 run-artifact files totaling roughly 455.05 MiB; the completed 004E commit alone added a
   50,222-line Codex log.

---

## 4. Context audit: what is really fed to a slice

### 4.1 Important correction

The session is not preloaded with the whole project packet. The generated prompt.md is passed to
Codex standard input. It instructs the agent to open other files. Parent epic, digest, map, source
section, prototype file, and predecessor artifacts are therefore retrieval behavior, not
guaranteed input.

Current practical sequence:

1. Codex system/app/skill instructions plus the generated Ralph prompt.
2. AGENTS.md, TOKEN_RULES.md, CONTEXT.md, AFK_RUNBOOK.md, config, permissions, state, HANDOFF,
   decision policy, and frontend rules.
3. Selected slice.
4. Parent epic only because TOKEN_RULES asks for it; it is absent from the generated numbered
   read list.
5. Matching digest if the agent finds and opens it.
6. Capability map only if the agent chooses it.
7. Source files/sections found through search.
8. Code, tests, diffs, tool output, and run evidence accumulated during implementation.

The design is directionally correct—small stable context first, expensive sources later—but the
important retrieval choices are still indirect.

### 4.2 Source and digest shape

- docs/source contains 23 files totaling about 4.32 MB: 21 Markdown specifications totaling about
  1.86 MB and two SOP PDFs totaling about 2.46 MB.
- The SOP PDFs are 33 and 12 pages. Fourteen queued slices cite them, concentrated in Epic 008
  plus 009K.
- Epic digests exist only through Epic 007. There is no page-cited Epic 008 digest yet.
- The map layer has valuable section links. Across 27 post-map Codex logs, 23 referenced digests,
  22 referenced source documents, and only one referenced docs/working/maps. Restricting the
  population to 23 rollout-task-complete logs gives 22 digest, 22 source, and one map reference.
  Map-first savings are therefore projected, not measured.
- The digest rule says roughly 300 lines, but Epic 005 is 502 lines/37 KB and Epic 006 is
  515 lines/40 KB.
- Large accumulating registries—API contracts, assumptions, review findings, progress, and run
  history—are valuable for search but poor default whole-file context.

### 4.3 Measured context pressure

scripts/ralph-context-tripwire.py measures peak per-call input tokens against the model-reported
context window.

| Measurement | Result |
|---|---:|
| Codex runs analyzed | 104 |
| Runs skipped for missing telemetry | 47 |
| Runs at or above 85% | 5 |
| Additional runs in the 70-85% watch band | 15 |
| Confirmed explicit auto-compactions | 1 |
| Old observed window | 258,400 tokens |
| Runs on old window | 70 |
| Old-window median peak | about 60.6% |
| New observed window | 353,400 tokens |
| Runs on new window | 34 |
| New-window all-row median peak | about 45.8% |
| Completed-agent new-window sessions | 32 |
| Completed-agent new-window median peak | about 47.4% |
| New-window breaches | 0 |

The tripwire itself does not exclude incomplete sessions. Two of the 34 new-window rows did not
reach the agent task-complete event and had very low partial peaks, so the completed-agent median
is the more useful planning number.

The confirmed compaction occurred in repair run 2026-07-09_233958_repair after a peak of
243,521 / 258,400 (94.24%). The larger recent window improved headroom, but it is not pinned by
the Ralph configuration. The adapter currently asks for “Codex CLI default,” and records the
actual model as unknown. Planning must not assume that 353,400 will always be available.

The just-completed 004E session illustrates the cost of combining preparation and implementation.
Sharpening and its source work reached about 63,893 tokens, execution planning/code exploration
reached about 80,023, the first red-test/code phase reached 101,756, and the session finished at a
153,007-token peak (43.3% of 353,400). The 101,756-token point would already be 39.4% against the
smaller observed window.

Across 81 runs with both telemetry and diff data, changed lines and peak input context had a
Pearson correlation of about 0.755. Median peaks rose from 123,814 tokens for runs of at most
500 changed lines to 192,349 for runs in the 1,501-2,000 line band. This does not prove line count
alone causes context use, but it is a strong practical slice-shaping signal.

### 4.4 Conservative operating envelope

Until the model/window is pinned, budget against 258,400 tokens. The 30% and 60% bands below are
proposed planning targets; 70% and 85% are the current post-run tripwire bands. They cannot stop an
active session unless live monitoring/control is added.

| Band | Occupancy | Conservative token value | Required response |
|---|---:|---:|---|
| Context-ready | at most 30% | at most 77,520 | Slice, exact sources, and execution plan should be ready before broad code exploration. |
| Normal implementation target | below 60% | below 155,040 | Enough room remains for tests, failure diagnosis, review, and handoff. |
| Watch | 70% | 180,880 | Stop broad discovery; summarize, narrow, and split future work. |
| Breach | 85% | 219,640 | Treat as a process defect requiring a slice/context review, even if the run passed. |
| Compaction | any explicit event | n/a | Do not claim a fully reliable review from that session without an independent follow-up. |

Use roughly 1,200 changed product lines as a soft planning target. Keep 2,000 as the runaway hard
stop, not the desired slice size.

The table is a conservative policy proposal, not current enforcement. The live tripwire applies
70%/85% to each reported window, so at 353,400 it watches only at 247,380 and breaches at 300,390.
That is why the telemetry table can correctly report zero new-window breaches even though the same
34 rows, measured against the conservative absolute limits above, contain 11 watch-only runs and
four breaches. Add absolute-token thresholds, or calculate percentages from a configured minimum
expected window, before calling this envelope enforced.

### 4.5 Recommended context pipeline

#### Stage A: epic-boundary context preparation

Add a dedicated context_prepare mode before each future epic, or use an explicit CTX planning
slice until that mode exists. It must be unable to mark a product slice Complete. The current
afk-dev.sh does not implement a docs-only mode even though config vocabulary mentions docs_only.
Context preparation should:

- start from the matching capability map;
- resolve exact source headings and PDF page ranges;
- reconcile conflicts with ADRs, assumptions, and review findings;
- create a compact epic index plus per-slice digest sections;
- sharpen only the next execution horizon, not all future implementation details;
- list open decisions that must block, configure, or defer behavior;
- change no product code.

Epic 008 requires this before 008A. Extract both SOP PDFs into a page-cited documentation/security
digest so fourteen implementation slices do not repeatedly search whole PDFs.

#### Stage B: slice-ready gate

No implementation session should start when:

- the generic Goal or generic backend-scope sentence remains;
- Depends On entries are incomplete or unresolved;
- source references lack exact headings/pages;
- business outcome and non-goals are unclear;
- API/model/permission ownership is missing;
- frontend scope lacks screen IDs, prototype files, states, and evidence;
- tests do not name the public behavior and negative paths;
- an open policy/legal decision has no explicit block/configure/defer treatment.

Sharpening inside the implementation session should remain an emergency safety fallback, not the
normal path.

#### Stage C: generated context manifest

Generate a small manifest for the exact mode instead of giving all modes one generic prompt.

~~~yaml
mode: normal
slice: 008A-document-template-model-and-versioning
dependencies:
  - id: 007J
    required_status: Complete
authority:
  - source: docs/source/functional-spec.md
    heading: exact heading
  - source: docs/source/Final SOP - Loan Disbursement V10 (1).pdf
    pages: exact pages
working_context:
  epic: docs/epics/008-documentation-security-package.md
  digest_sections:
    - exact slice heading
  capability_maps:
    - docs/working/maps/Documentation and Security Map.md
decisions:
  confirmed: []
  configurable: []
  blocked_or_deferred: []
prototype:
  source_screen_ids: []
  immutable_reference_commit: owner-confirmed commit
  files: []
  owned_mock_or_fixture_paths: []
code_entrypoints: []
required_tests: []
non_goals: []
soft_diff_budget: 1200
~~~

Mode-specific differences:

- Normal receives exact slice, epic, map, digest headings, source anchors, predecessor contracts,
  code entrypoints, and prototype evidence.
- Repair receives the exact failed run/slice, compact failure summary, changed surface, and only
  the failed gates. It opens full logs on demand.
- Architecture review receives the exact base..HEAD range, merged slice IDs, review packets,
  source anchors, and unresolved prior findings.

#### Stage D: retrieval order

For implementation sessions use:

1. constitutional/policy files;
2. generated context manifest;
3. selected slice;
4. only the named epic/digest sections;
5. only the named source headings/PDF pages;
6. predecessor public contracts and tests;
7. precise code entrypoints;
8. broader search only if a recorded gap remains.

Do not default to a whole source file, the whole source folder, or all run history inside an
implementation session. If exact anchors are insufficient, pause product work and route the gap
to context preparation; whole-corpus reconciliation belongs there, not in the coding session.

#### Stage E: divide agent and orchestrator work

The agent should run focused red/green tests and targeted checks needed to develop the slice. After
repair is bound to the exact failed run and its gate feedback, the orchestrator should become the
sole owner of the full gate suite, state/status/progress bookkeeping, changed-file inventory,
final run result, commit, merge, and publication. Until then, retain agent-side checks but redirect
their full output to artifacts. This transition avoids duplicated context without weakening the
current repair signal.

Redirect full command output to artifacts. Return exit code, failed test names, and a short tail to
the active session. Do not paste multi-megabyte logs or unbounded diffs into context.

#### Stage F: context receipt and feedback

Each run should leave a compact traceability receipt:

- actual model and context window;
- files/headings/pages opened;
- source conflicts found;
- assumptions/ADRs used;
- peak occupancy and compaction count;
- product lines/files changed;
- evidence generated;
- context debt for the next slice.

This receipt records the agent's claimed retrieval; it is not proof that every listed file was
actually opened. The orchestrator must postprocess the actual model, reported window, peak, and
compaction count after the agent exits.

A watch, breach, compaction, or diff-cap failure must influence the next run packet in a
mode-specific way: narrow or split product scope for normal work, improve the failure summary for
repair, and reduce the review range for architecture review. The current tripwire should accept the
exact run ID and report missing telemetry rather than silently scanning whichever folder sorts
last.

---

## 5. Source-to-product traceability

### 5.1 What exists

The capability maps are a good source-navigation layer. They connect requirements, flows, domain,
data, information architecture, screens, components, content, design, APIs, permissions,
security, tests, and roadmap sections.

They stop before the actual delivery proof. They do not show, for every requirement:

- owning epic and slice;
- implemented service/API/model;
- owning prototype screen and final route;
- test that proves it;
- run/release evidence;
- assumption or decision disposition;
- UAT owner and signoff.

### 5.2 Required golden thread

Before final UAT, maintain one program-completion matrix with this schema:

| Source ID and exact section | Decision status | Epic | Backend slice | Frontend/wiring slice | API/model | Prototype screen/route | Automated test | Run evidence | UAT owner | Release disposition |
|---|---|---|---|---|---|---|---|---|---|---|
| Example | Confirmed / Configured / Manual MVP / Deferred R9 / Blocked | 007 | 007B | 007I | public contract | S21/S22 | test ID | run ID | role | Ready / Gap |

Rules:

1. Every signed-off MVP requirement and acceptance ID has one primary accountable owner/path;
   cross-cutting supporting slices and tests may also be linked.
2. Every source screen is implemented, deliberately merged into another screen, or explicitly
   deferred with business approval.
3. Every manual MVP integration still has a recorded request, reference, evidence, status,
   reconciliation, and fallback owner.
4. Every assumption marked Needs Confirmation is confirmed, made configurable, safely blocked, or
   explicitly accepted for the release.
5. “Covered by source section” is not enough at release time; link the concrete test/evidence.
6. Completed slices are backfilled at epic checkpoints from code, contracts, tests, and run
   packets. Do not reopen the full source corpus in every slice.
7. The matrix is generated/validated against docs/slices and Git where possible; do not create
   another manually drifting queue list.

### 5.3 Scope boundary

Production Ready must be defined against a signed-off release scope, not every future idea in the
source corpus.

The source explicitly permits manual-first SAP, bank, CDSL, subsidiary, and communication flows
for MVP, while direct APIs, CKYC/bureau, e-sign/e-stamp, mobile, AI extraction, advanced BI, and
automated external legal recovery can remain later work. Conversely, the borrower portal is
described as future in parts of the PRD/roadmap but is already partly implemented and has a full
screen specification. The owner must decide whether it is:

- in the go-live scope and therefore subject to full UAT/security/accessibility;
- a controlled beta;
- or disabled/hidden until a later release.

No feature should be simultaneously “future” in release scope and exposed as a production-looking
surface.

---

## 6. Stitching back to the design prototype

### 6.1 Authority and visual contract

Use this precedence:

1. docs/source business, security, content, screen, component, and design requirements;
2. approved owner decisions and ADRs;
3. an immutable approved prototype commit for visual composition and interaction density;
4. the concrete slice contract;
5. current implementation.

The source wins when the prototype is incomplete or contradictory. “Prototype parity” means the
approved design language, composition, role behavior, and interaction density are preserved while
source-required functionality is made real. It does not mean retaining mock data or incorrect
prototype business rules.

The current reference is mutable: FRONTEND_DESIGN_RULES.md and VISUAL_ACCEPTANCE.md point to the
same sfpcl-lms code that Ralph edits. Git history identifies 3f464e3 as the last pre-Ralph product
commit; the owner should confirm that commit or nominate another and tag it as the immutable
prototype baseline. Do not silently choose a baseline.

### 6.2 Current measurable state

- There are 55 non-test page components.
- Only six committed Playwright screenshot baselines exist, concentrated on login, early
  dashboard, and tracer screens; at least the dashboard baselines are currently nondeterministic,
  which is why CR-001 exists.
- Playwright is optional in Ralph and absent from CI.
- 20 non-test production files directly import mockData.
- That count understates the gap because some screens use inline hard-coded business rows.
- Visual screenshot evidence is not required by the validator.
- Current wiring slices are the right architectural seam, but later slices do not yet carry
  sufficiently specific screen/role/state/baseline criteria.

### 6.3 Confirmed delivered-scope and ownership gaps

These must receive explicit corrective ownership; a final mockData count alone will not find all
of them.

| Gap | Evidence-based problem | Required closure |
|---|---|---|
| Member create/update and identity governance | Source requires POST/PATCH member, member change history, and locking of verified identity fields. Live handlers are GET-only, check only global read permission, and no remaining slice owns create/update; object-level scope and full sensitive-field reveal remain deferred. | Backend contract, scoped object permissions, maker-checker/reverification rules, history, individual/FPC forms, sensitive reveal control, tests, and visual states. |
| Completeness Workbench | 005I says 005E already wired it, but CompletenessWorkbench.tsx still imports mock applications, members, and documents and derives decisions locally. | A corrective full-stack wiring slice; remove client-side reference/completeness business decisions. |
| App shell application state | App.tsx seeds application state from mockData and passes it into SanctionWorkbench. | Move all production workflow state behind real APIs; no fallback that looks real. |
| Header search | Header.tsx searches mock member/application/account data, including sensitive fields. | 010N owns real global search; make privacy, authorization, and no-local-sensitive-index criteria explicit. |
| Header notification dropdown | It renders hard-coded notification rows even though the full Notifications Center is API-backed. | Give this shell surface an explicit owner and real notification summary contract. |
| Witness UI | 004E delivered backend APIs only; Application Detail still shows “No API-backed witness details,” while 004K says 004E owns editing. | A reachable capture/read/edit surface with role, validation, and visual evidence. |
| Produce/service history | Source requires persisted evidence for active-member rules; assumptions defer it but no future slice owns it. | Persisted source-backed history, verification, calculation, portal/staff views, and tests. |
| Borrower deficiency response | Portal upload/response/resubmission is explicitly deferred and unowned. | Own-data document response, validation, resubmission, status, audit, and negative access tests. |
| Portal KYC correction | The member portal specification requires KYC update/correction requests, while the current prototype inventory marks KYC update as future. | If the portal is in release scope, own the request, review, evidence, status, audit, and member/staff states; otherwise hide and explicitly defer it. |
| Settings surfaces | SettingsHub has editable-looking inline policy/rate/threshold/retention data; 007J owns only approval matrix. | Either real versioned configuration wiring or clearly disabled/read-only non-production treatment. |
| Tracer surface | The tracer app and API routes remain unconditionally installed; A-011 requires production isolation. | Assign a slice to remove, environment-gate, or separately authorize the tracer before production, with a negative deployment test. |
| Field-encryption keys | Current identity-field protection derives from the general Django SECRET_KEY, while the source separates application, JWT, field, storage, and backup keys. | Dedicated key separation and custody, rotation/versioning, backup/recovery, migration/re-encryption evidence, and fail-closed deployment checks. |

### 6.4 Per-frontend-slice completion contract

Every frontend or full-stack slice must state and validate:

- exact source screen IDs and user-flow steps;
- immutable prototype commit plus exact files/components;
- roles allowed, hidden, read-only, and forbidden;
- loading, empty, error, unauthorized, validation, conflict/stale, and success states;
- desktop/tablet requirements for staff and mobile requirements for member portal;
- owned mockData imports and inline fixtures before/after;
- client-side calculations or invented states that must disappear;
- deterministic Playwright scenario and baseline names;
- API/error envelopes that drive each state;
- screenshots/baselines in the run evidence;
- accessibility checks for keyboard, labels, focus, contrast, and responsive overflow.

The mechanical ratchet is:

1. An owning slice may not leave mockData or runtime business records/calculations as inline
   fixtures in its production paths. Controlled vocabularies, display metadata, and test fixtures
   remain legitimate when explicitly identified.
2. The total mock/fixture surface may not grow.
3. A production screen may not calculate server-owned money, eligibility, approval, state, or
   permission decisions locally.
4. Every new/rewired screen adds deterministic browser and visual coverage.
5. CR-001 stabilizes time/date-dependent baselines; a separate protected Ralph-validator and CI
   workflow change must then make Playwright required before the large Epic 007-012 wiring waves.

### 6.5 Final parity sweep

Before final UAT, run the deployed staging app screen by screen against:

- source screen inventory and member-portal screen inventory;
- frozen prototype baseline;
- the nearest approved prototype composition, or an explicit N/A reason, where the authoritative
  source requires a screen that the original prototype never contained;
- current prototype inventory/gap report;
- role-navigation matrix;
- real API ownership;
- all required UI states and viewports;
- zero production mock/inline fixture paths;
- accessibility evidence.

The output is a signed parity table in the final UAT packet. Any miss becomes a corrective slice;
it is not accepted as an informal final-day polish item.

---

## 7. Production readiness gap analysis

### 7.1 What the current queue covers well

The queue broadly follows the intended lifecycle:

- identity, RBAC, audit, documents, configuration, notifications, and task foundations;
- member/KYC and intake;
- eligibility, loan limit, appraisal, and credit review;
- sanction/approval;
- documentation and security instruments;
- SAP/disbursement;
- servicing, repayment, interest, monitoring;
- default, recovery, closure, compliance;
- reports, exports, security hardening, E2E/UAT, and smoke-check concepts.

The source manual-first adapter strategy is appropriate for MVP. Production readiness does not
require direct SAP/bank/CDSL APIs if the manual workflow, evidence, reconciliation, access control,
and operational ownership are complete. If portal authentication or production alerts require
OTP, however, the release still needs a usable provider or an explicitly approved operational
alternative.

### 7.2 What queue completion would still fail to prove

| Production domain | Source expectation | Current queue/evidence gap |
|---|---|---|
| Full regression | Unit, API, frontend, E2E, permissions, financial, integration, report, compliance, operational tests. | Integration/e2e not required by Ralph; 012G is generic. |
| Security | Secret/dependency scanning, production settings, object/document/integration/financial security. | CI audits are report-only; no fail-closed secret scan; 012F is generic. |
| Key management | Separate application/JWT/field/storage/backup keys with custody, rotation, recovery, and migration. | No release slice proves independent field-encryption keys or rotation/re-encryption recovery. |
| Production database | PostgreSQL production semantics. | Routine Ralph and CI backend suites use SQLite; only five special credit races used PostgreSQL. |
| Runtime | Backend, PostgreSQL, durable storage, jobs/workers, scheduler. | Only frontend Netlify deployment exists; no backend/container/runtime target; scheduler is metadata only. |
| Staging | Production-like deployed environment for QA/UAT. | 012H can smoke any URL but excludes hosting/pipeline and currently proves localhost only. |
| Observability | Structured logs, metrics, business/security alerts, job visibility. | No deployed monitoring/alerting proof or operations test owner. |
| Backup/restore/DR | Encrypted backup plus restore and recovery drill. | No implementing/rehearsal slice. |
| Performance | Agreed API/search/report/batch targets, load and stress evidence. | No explicit performance slice or enforced budget. |
| Migration | Trial migrations, dress rehearsal, reconciliation, rollback, signoff if data is in scope. | 003L is planning-only; no importer or rehearsal owner. |
| Integration cutover | Provider/manual mode, credentials, certification, fallback, reconciliation, owner. | Adapter/manual behavior is planned, but release cutover evidence is not owned. |
| UAT | Named roles execute critical scripts and sign off. | 012I is a generic packet, not business execution/signoff. |
| Training/support | Role training, escalation, rollback, hypercare. | No concrete queue owner or evidence gate. |
| Prototype parity | All required screens role-reachable, API-backed, visually accepted. | No final parity gate; browser baselines cover only six early states. |
| Decision closure | Policy/legal/operations questions resolved or explicitly release-treated. | Sixteen consolidated open decision groups and 48 confirm-needed assumptions remain. |

### 7.3 Production infrastructure track required before 012G-012I

The production track must provide:

1. fail-closed production Django settings: DEBUG false, required secret, host/origin/cookie/HTTPS
   controls, safe errors, no local defaults;
2. a supported WSGI/ASGI server and backend deployment artifact;
3. PostgreSQL runtime and the full backend gate suite on PostgreSQL;
4. durable encrypted object storage and restricted/signed document access;
5. reliable job execution for interest, DPD, reminders, compliance, notifications,
   reconciliation, and exports—or an explicitly controlled external scheduler;
6. deployed, isolated staging with production-like configuration and sanitized data;
7. structured logs, redaction, metrics, alerts, dashboards, and business/job failure visibility;
8. backup, restore, point-in-time/DR decision, and executed restore evidence;
9. frontend/backend/database migration and rollback runbooks tested together;
10. manual/live integration cutover matrix for SAP, bank, email/SMS, CDSL, storage, and subsidiary
    reconciliation;
11. secret, dependency, and image/runtime scans that fail on the agreed severity;
12. separate field/storage/backup key custody, rotation, recovery, and migration/re-encryption
    evidence rather than deriving all protection from one application secret;
13. production removal, environment isolation, or explicit authorization of tracer/demo routes;
14. support, escalation, incident response, access review, training, and hypercare ownership.

### 7.4 Sharpen the release tail early

012A-012E and 012DA also need concrete report ownership before Epic 012 begins. Map the 20 named
reports in the implementation roadmap to report APIs, registers, exports, permissions/masking,
audit exploration, dashboard states, tests, and prototype routes. R8-AC-001 must be evidenced for
every critical export rather than inferred from a generic reporting foundation.

012F, 012G, and 012I are too generic to protect the finish line.

012F must enumerate:

- production configuration;
- JWT/session/rate-limit behavior;
- role, object, maker-checker, and conflict controls;
- sensitive masking/reveal/export/download;
- financial idempotency and transactions;
- document/upload/storage security;
- integration payload/redaction/retry security;
- immutable audit behavior;
- secret/dependency/runtime scanning;
- production-like PostgreSQL negative tests.

012G must map the named E2E-001 through E2E-018 scenarios from the source test plan, identify which
are automated versus business-executed, include negative role/security paths, run against
production-like PostgreSQL, and include browser/accessibility/visual coverage.

012I must require:

- complete source-to-release matrix;
- zero unowned MVP requirements/screens;
- final architecture review;
- prototype-parity report;
- open-decision and assumption dispositions;
- full regression/security/accessibility/performance results;
- deployed-staging smoke evidence;
- migration rehearsal and reconciliation if in scope;
- backup/restore/rollback evidence;
- integration/manual-fallback signoffs;
- named role-based UAT signatures;
- training, support, and hypercare readiness;
- explicit release vetoes and final go/no-go.

---

## 8. Completion sequence from the current queue

### Checkpoint 1: close delivered-scope debt before 006X

- Allow the active iteration to recover/finish; do not salvage or edit an active worktree. At a
  verified clean iteration boundary, stop the outer loop before it selects 006X. Run
  `./scripts/ralph-recover.sh`, then explicitly run
  `./scripts/afk-dev.sh 1 --slice CR-001-e2e-visual-baselines-nondeterministic`; restart the normal
  loop only after CR-001 is integrated. Filename ordering will not schedule CR-001 before 006X by
  itself.
- Give each confirmed unowned gap in section 6.3 a queued corrective owner.
- Fix the automation fail-closed issues in section 3.3 at an owner-controlled checkpoint.
- Confirm the immutable prototype baseline.
- Introduce the slice-ready/context-manifest gate.
- Treat 006X as a real two-role browser + backend tracer, not merely an integration test. It must
  execute Playwright, preserve IDs across the real chain, and capture approved visual evidence.

### Checkpoint 2: Epic 007 sanction and approval

- Prepare the Epic 007 digest/slice packets before 007A starts.
- Resolve exact-threshold, signing-authority, conflict, and special-case decision handling.
- End with a multi-role approval tracer below/at/above the threshold, exception/conflict negative
  paths, immutable history, generated registers, member-facing outcome, and prototype baselines.

### Checkpoint 3: Epic 008 documentation/security

- Build the page-cited digest from both SOP PDFs before 008A.
- Confirm templates, signer authority, Annexure conflict, stamp/notary rules, custody, and
  physical-versus-demat handling.
- Test that no disbursement path bypasses documentation/security gates.
- Finish with API-backed staff/member documentation screens and secure document evidence.

### Checkpoint 4: Epic 009 SAP and disbursement

- Move the full backend gate and CI suite to PostgreSQL before the money path expands.
- Decide manual versus live integration modes and the real staging/deployment topology.
- Prove maker-checker, readiness, CFC authorization, idempotency, UTR uniqueness, rollback, audit,
  and reconciliation without initiating real funds in automated tests.
- Wire the complete disbursement/loan-account experience and deterministic visual coverage.

### Checkpoint 5: Epic 010 servicing and money calculations

- Treat principal allocation, schedules, interest, accrual, capitalisation, DPD, and
  reconciliation as financial invariants.
- Add concurrency, idempotency, boundary/property, reconciliation, and PostgreSQL tests.
- Prove background jobs are retry-safe, singleton/idempotent where required, visible, and alerted.
- Close portal and staff servicing screens with no local money calculations.

### Checkpoint 6: Epic 011 recovery, closure, and compliance

- Resolve recovery authority, waivable gates, closure order, retention, KYC destruction, and legal
  evidence decisions.
- Prove approval-before-recovery, balance-before-closure, security return, NOC, archive,
  compliance cycles, grievance, auditor read-only, and retention evidence.
- Complete the corresponding portal/staff screens and reports.

### Checkpoint 7: Epic 012 release assurance

- Create/verify the production infrastructure track before 012G-012I.
- Reconcile all source requirements, screen IDs, tests, decisions, and evidence.
- Run full regression, security, accessibility, performance, migration, operational, and deployed
  smoke work against production-like staging.
- Execute business UAT with the roles named in the source test plan.
- Do not mark 012I complete when it merely assembles documents; require actual evidence/signatures.

### Checkpoint 8: owner go-live

Only after section 9 is fully evidenced:

1. approve release scope and known accepted residual risks;
2. freeze changes and back up;
3. perform final migration/configuration and reconciliation;
4. provision/review users and roles;
5. promote staging to main through the protected pull request;
6. deploy frontend, backend, database migrations, jobs, and configuration in the approved order;
7. run production smoke and business validation;
8. activate monitoring, support, rollback, and hypercare.

---

## 9. Definition of Production Ready

Every row is a hard gate. “Not applicable” requires named owner approval and a reason.

| Gate | Required evidence |
|---|---|
| Signed scope | MVP/future/manual/beta decisions are explicit; borrower portal release treatment is explicit. |
| Slice ledger | All active product/corrective slices Complete; Superseded excluded; no Blocked, failed, stranded, or unpublished work. |
| Traceability | Every signed-off requirement/AC and screen maps to implementation, tests, evidence, and UAT disposition. |
| Architecture | Final independent review passes; no unresolved critical/high finding. |
| Open decisions | Every high-impact policy, legal, security, integration, data, and operations decision is confirmed, configured, safely blocked, or explicitly deferred. |
| Product behavior | Full lifecycle rules and negative gates work through public interfaces. |
| Prototype parity | Every in-scope screen is role-reachable, API-backed, visually accepted, responsive, and accessible. |
| No production mocks | Zero mockData imports, runtime inline business records/calculations, demo-only authorities, or client-owned business decisions in production paths; controlled vocabularies, display metadata, and test fixtures are identified and allowed. |
| Automated regression | Required unit/API/frontend/permission/financial/compliance/report/integration suites pass. |
| Browser/E2E | Critical E2E journeys and negative access paths pass deterministically in CI. |
| PostgreSQL | Full suite passes on the production database engine, including concurrency and constraint behavior. |
| Security | Production config, secret/dependency scans, RBAC/object access, masking/reveal, documents, exports, audit, and financial controls pass. |
| Performance | Agreed API/search/report/job/load targets pass with production-like data volumes. |
| Operations | Deployed staging, health, workers/jobs, logs, metrics, alerts, backup/restore, rollback, and runbooks are tested. |
| Integrations | Manual/live mode, credentials, evidence, retry/reconciliation, certification, fallback, and owner are signed off. |
| Migration | Scope decided; trials/dress rehearsal/final plan and reconciliation accepted when applicable. |
| UAT | All critical role-based scripts executed; zero open Sev 1 and zero unaccepted Sev 2; business signoff recorded. |
| People/readiness | Training, access review, support, incident escalation, cutover, rollback, and hypercare are active. |
| Release | Validated commit is merged, pushed, deployed, smoke-tested, and formally approved. |

---

## 10. Prioritized action register

| Priority | Action | Placement | Completion signal |
|---|---|---|---|
| P0 | Transactional commit/merge/push outcome | Next safe owner automation checkpoint | A run cannot exit success unpublished. |
| P0 | Bind repair, dependencies, readiness, and review debt | Next safe owner automation checkpoint | Wrong-slice repair and unready/dependency-invalid starts are impossible. |
| P0 | Pin actual model/window and add mode-specific context manifests | Before further generic epic work | Conservative context budget is deterministic and auditable. |
| P0 | Safely stop before 006X, run CR-001 explicitly, then require browser/visual gates through protected validator/CI changes | Before 006X/007 UI waves | Baselines are deterministic and fail CI/Ralph on drift. |
| P0 | Queue confirmed unowned product/screen gaps | Before claiming Epics 004-005 fully closed | Every source-required behavior and production-looking surface has an owner. |
| P0 | Confirm immutable prototype baseline | Before further wiring | Every frontend slice compares to a stable approved reference. |
| P0 | Start program completion matrix and decision dispositions | Now, maintained at epic reviews | Requirements, screens, tests, and release status are provable. |
| P1 | Epic-boundary context preparation; Epic 008 PDF digest first | Before each epic | No generic slice begins implementation; exact source anchors are ready. |
| P1 | Full PostgreSQL Ralph/CI gate | Before Epic 009 | Routine suite and money paths use production semantics. |
| P1 | Production infrastructure and deployed staging track | Before 012G | Browser/UAT/ops tests target a real production-like environment. |
| P1 | Sharpen 012A-012E, 012DA, 012F, 012G, and 012I | Well before Epic 012 execution | All 20 named reports/exports and the source R8 release gates have concrete owners and evidence. |
| P1 | Evidence retention/redaction | Before run history grows materially further | Compact Git history; raw artifacts retained securely outside default context. |
| P2 | Generate queue/progress/index views from slice files/state/Git | After P0 controls | No manually drifting program ledger. |

---

## 11. Final project recommendation

Do not redesign the project or abandon the slice model. The right move is to add two missing
layers around it:

- **before a slice:** a mechanically verified context packet that makes the work ready, narrow,
  source-cited, prototype-cited, and safely inside the session ceiling;
- **after the slices:** a release-assurance layer that proves the assembled product, data,
  infrastructure, operations, design, and business workflows are ready together.

That gives the project a continuous golden thread:

~~~text
authoritative source and signed decisions
  -> capability map and page/heading-cited digest
  -> execution-ready slice and context manifest
  -> API/model/service plus prototype screen
  -> focused TDD plus independent full gates
  -> requirement/visual/run evidence
  -> epic tracer and architecture review
  -> production-like staging
  -> full regression, migration, operations, and UAT
  -> owner promotion, cutover, and hypercare
~~~

The product is finished only when that complete chain is green. This preserves Ralph's speed
while preventing local slice success from being mistaken for a fine-finished, production-ready
loan-management application.

---

## 12. Principal audit evidence

Automation and context:

- AGENTS.md
- .ralph/config.yaml
- .ralph/permissions.json
- .ralph/state.json
- scripts/ralph-loop.sh
- scripts/afk-dev.sh
- scripts/ralph-preflight.sh
- scripts/ralph-run.sh
- scripts/ralph-validate.sh
- scripts/ralph-recover.sh
- scripts/ralph-context-tripwire.py
- scripts/agent-adapters/codex.sh
- docs/working/TOKEN_RULES.md
- docs/working/CONTEXT.md
- docs/working/AFK_RUNBOOK.md
- docs/working/HANDOFF.md
- docs/working/digests/
- docs/working/maps/
- current and historical .ralph/runs artifacts and mapped Codex rollout telemetry

Product, design, and release:

- docs/source/product-requirements.md
- docs/source/functional-spec.md
- docs/source/user-flows.md
- docs/source/api-contracts.md
- docs/source/data-model.md
- docs/source/auth-permissions.md
- docs/source/screen-spec.md
- docs/source/screen-spec-member-portal.md
- docs/source/component-spec.md
- docs/source/design-system.md
- docs/source/test-plan.md
- docs/source/security-privacy.md
- docs/source/deployment-ops.md
- docs/source/integrations.md
- docs/source/implementation-roadmap.md
- both SOP PDFs in docs/source/
- docs/epics/
- docs/slices/
- docs/working/FRONTEND_DESIGN_RULES.md
- docs/working/VISUAL_ACCEPTANCE.md
- docs/working/PROTOTYPE_INVENTORY.md
- docs/working/PROTOTYPE_GAP_REPORT.md
- docs/working/API_CONTRACTS.md
- docs/working/ASSUMPTIONS.md
- docs/working/DATA_IMPORT_MIGRATION_PLAN.md
- docs/working/RELEASE_PROMOTION.md
- sfpcl-lms/src/
- sfpcl-lms/e2e/
- sfpcl_credit/
- .github/workflows/ci.yml
- netlify.toml

### 12.1 Requirement-ID count reproduction

The 606/24 traceability snapshot uses exact, case-sensitive tokens and prevents shorter security
IDs from being counted inside longer IDs:

~~~sh
ID_REGEX='(?<![A-Z0-9-])(?:M[0-9]{2}-FR-[0-9]{3}|[A-Z][A-Z0-9-]*-AC-[0-9]{3}|SEC(?:-[A-Z0-9]+)+|E2E-[0-9]{3}|UAT-[0-9]{3})(?![A-Z0-9-])'

rg -P -o --no-filename -g '*.md' "$ID_REGEX" docs/source \
  | sort -u > /tmp/source_ids
rg -P -o --no-filename -g '*.md' "$ID_REGEX" docs/epics docs/slices \
  | sort -u > /tmp/planning_ids
comm -12 /tmp/source_ids /tmp/planning_ids > /tmp/mapped_ids
wc -l /tmp/source_ids /tmp/mapped_ids
~~~

Snapshot output: 606 source IDs and 24 exact planning matches. This is a documentation-coverage
measure, not a claim that every unmatched behavior is absent from code.
