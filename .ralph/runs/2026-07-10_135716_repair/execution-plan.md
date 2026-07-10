# Execution Plan

Selected slice: `006D2-credit-assessment-deep-module-boundary`
Mode: repair
Risk: High, covered by standing approval; no veto found in `docs/working/HIGH_RISK_APPROVALS.md`.

## Repair Diagnosis

- Current run folder had only placeholder artifacts when this plan was written.
- No `.ralph/worktrees` directory exists inside the active worktree, so there is no leftover failed worktree to inspect here.
- Recent run summaries show the latest completed product run, `2026-07-10_125342_normal_run`, passed. The visible failed summaries are old dependency-environment runs from 2026-07-03, not a failed `006D2` attempt.
- Treat the actionable repair target as review finding 4 from `2026-07-10_092630_architecture_review`: eligibility and loan-limit behavior live in `applications.services` instead of the source-named credit module seams, and loan-limit public/audit projections are duplicated.

## Source-Grounded Requirements

- `docs/source/codebase-design.md` §§6.2-6.3 and §7.3: business behavior belongs in `modules/`; views authenticate/parse, call a module interface, and return responses.
- `docs/source/codebase-design.md` §§12.1-12.3: establish `credit.modules.eligibility_assessment`, `credit.modules.loan_limit_calculator`, and future `credit.modules.appraisal_workflow` seams.
- `docs/source/codebase-design.md` §22 and `docs/source/data-model.md` §34: loan-limit calculation, eligibility assessment, audit, workflow, and persistence changes are transactional.
- `docs/source/codebase-design.md` §26: test through the module interface, replacing broad helper-level coupling.
- `docs/source/api-contracts.md` §§22-24: preserve existing eligibility, loan-limit, and appraisal API contracts; no endpoint or field changes.
- `docs/source/data-model.md` §§14.1-14.4: preserve existing credit-assessment table shapes. Model ownership movement will be staged if it cannot be done without destructive migration risk.

## Edit Permissions

Allowed edit paths for this slice:
- `sfpcl_credit/**`
- `docs/working/**`
- `docs/slices/**`
- `.ralph/runs/**`
- `.ralph/progress.md`
- `.ralph/state.json`
- `docs/adr/**`

Protected/forbidden paths will not be modified, including `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`, `docs/working/FRONTEND_DESIGN_RULES.md`, and `docs/source/**`.

## Implementation Plan

1. Capture characterization evidence for the existing credit endpoints before extraction.
2. Add failing module/interface tests for:
   - eligibility runs through `credit.modules.eligibility_assessment`;
   - loan-limit calculation through `credit.modules.loan_limit_calculator`;
   - a canonical loan-limit snapshot used by both public response and audit metadata;
   - an import-boundary/static regression showing credit behavior is not exposed through `applications.services` compatibility aliases and the appraisal seam exists.
3. Implement `sfpcl_credit.credit` as a domain/Django package with public modules:
   - `credit.modules.eligibility_assessment`
   - `credit.modules.loan_limit_calculator`
   - `credit.modules.appraisal_workflow`
4. Implement `configurations.modules.configuration_resolver` for active/effective loan-policy lookup and validation. The calculator must call this seam instead of querying/interpreting `LoanPolicyConfig` directly.
5. Move eligibility and loan-limit orchestration, validation, transaction/locking, persistence, audit/workflow coordination, and result/snapshot projection behind the credit module interfaces.
6. Thin the current eligibility/loan-limit views so they authenticate/parse, call the credit interface, translate typed errors, and serialize returned immutable DTOs.
7. Keep existing assessment models in `applications` for this slice if moving Django model state would require a risky/destructive ownership migration. Record that staged decision in an ADR and sharpen a follow-up model-ownership slice if needed.
8. Run focused red/green tests, then full backend and frontend gates. Save all command output under `.ralph/runs/2026-07-10_135716_repair/evidence/terminal-logs/`.
9. Update digest/source trace, ADR/follow-up slice if staged, state/progress/handoff/slice status, changed-files, risk assessment, review packet, and final summary.

## Expected Public Behavior

No API contract, permission, object-scope, error-code, formula, snapshot, audit, workflow, migration, dependency, or frontend behavior change is intended.
