# High-Risk Policy: Standing Approval + Veto

## Standing approval

On 2026-07-02 the project owner (Amit) granted standing approval for autonomous AFK runs, including High-risk slices, stating: the automation "should take any decision within interest of the project… without taking my approval as I am not a developer" and must "work seamlessly without interruption".

High-risk slices therefore run WITHOUT per-slice human approval. This is safe only because the compensating controls below are hard-enforced by scripts (not by trusting the agent):

1. Protected files can never be modified by an agent — `scripts/ralph-validate.sh` fails the run if `scripts/`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, this file, `docs/working/DECISION_POLICY.md`, or `docs/source/` are touched. An agent can never again weaken its own guardrails.
2. Every run must pass all quality gates (frontend typecheck/tests/build; backend check/tests/migrations-sync/coverage floor) or nothing is committed or merged.
3. TDD evidence and an honest risk assessment are required artifacts for every run.
4. Every merged slice is pushed to GitHub so the owner has a visible, reviewable trail.

## Owner's veto (the brake)

To block a slice from ever running autonomously, add one line:

```
- [revoked] <full-slice-id> | <date> | <reason>
```

Runs check this list before starting and refuse vetoed slices.

## Vetoed slices

(none)

## History

- 2026-07-02: Per-slice approvals model replaced by standing approval + veto at the owner's explicit request. Previously seeded approvals (002B2, 002C, 002D) are superseded by the standing approval.
