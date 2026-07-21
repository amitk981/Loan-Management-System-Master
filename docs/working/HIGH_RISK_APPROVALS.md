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

## Architecture review finalizers

These approvals are narrower than standing High-risk approval. A listed CR may close one named
architecture-review Root ID without another immediate review only after that root's configured
corrective generation is exhausted and every declared product, regression, PostgreSQL, browser,
migration, and coverage gate passes. New approvals use the exact format
`CR | Epic NNN | Root ROOT-NNN-* | generation N | reason`; the orchestrator validates every field.
The completed CR-013 line below is retained in its historical pre-root format.

For unattended execution, the owner additionally authorizes one terminal finalizer per stable
Root ID after that root reaches the configured generation cap. The orchestrator must prove the
exact exhausted root and generation, require a High-risk CR, retain permanent finding/reproducer
contracts, run every full quality gate, and record the consumed root so this policy can never admit
a second terminal finalizer for the same root.

If executable review evidence later disproves that finalizer, the owner authorizes one bounded
High-risk repair of the same terminal contract. The repair must retain the original finalizer and
grouped Root IDs, run every applicable quality gate, and cannot create another corrective
generation or finalizer. A recurrence after that repair remains a hard owner-review stop.

- [approved-finalizer-policy] generation 2 | one terminal finalizer per Root ID | 2026-07-20 owner-authorized unattended convergence recovery
- [approved-terminal-repair-policy] one bounded repair per terminal finalizer | 2026-07-21 owner-authorized recurrence recovery

- [approved-finalizer] CR-013 | Epic 009 | generation 2 | 2026-07-19 owner-authorized terminal root-boundary correction

## History

- 2026-07-02: Per-slice approvals model replaced by standing approval + veto at the owner's explicit request. Previously seeded approvals (002B2, 002C, 002D) are superseded by the standing approval.
