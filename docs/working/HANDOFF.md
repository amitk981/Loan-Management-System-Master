# Ralph Handoff

## Last Run
2026-07-02-autonomy-upgrade (manual owner session, not an AFK run)

## Current Status
The workflow now runs fully autonomously under the owner's standing approval (granted 2026-07-02, recorded in `docs/working/HIGH_RISK_APPROVALS.md`).

Operating model:
- "run ralph loop" = `./scripts/ralph-loop.sh` — runs the queue slice by slice with full gates, auto-commit, auto-merge to main, auto-push to GitHub (`github-master`); one repair attempt per failure; stops on queue-empty, repeated failure, or owner veto.
- No human approvals during runs. Judgment calls follow `docs/working/DECISION_POLICY.md`; assumptions are logged in `docs/working/ASSUMPTIONS.md`; business rules are never invented.
- Hard-enforced controls (in scripts, not prompts): protected-paths check (agents cannot touch scripts/, config, AGENTS.md, policy files, docs/source), quality gates (frontend typecheck/tests/build; backend check/tests/migrations-sync/coverage ≥ 85%), TDD evidence required.
- Owner's brake: add `- [revoked] <slice-id> | <date> | <reason>` to HIGH_RISK_APPROVALS.md.

## Current Slice
None selected. Next in queue: `002B2-auth-hardening-jwt-library-and-packaging`.

## Current Blocker
None.

## Next Recommended Action
`./scripts/ralph-loop.sh` from the repository root.
