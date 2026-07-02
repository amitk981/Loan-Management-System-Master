# Change Requests (Maintenance Stage)

Once all product slices are complete, this is the ONLY way changes enter the codebase. Bugs and feature requests written in chat are never implemented directly — they must become a validated change request first. If a request does not follow the template, **nothing in the code changes**.

## How to file a request (owner)

1. Copy the right template: `TEMPLATE-bug.md` or `TEMPLATE-feature.md`.
2. Save it as a new file in `inbox/` (any filename, e.g. `login-button-wrong-label.md`).
3. Fill in every section. You can ask codex or Claude to help you fill it in — that is allowed and encouraged; the rule is only that the *file* must be complete.
4. Run: `./scripts/ralph-intake.sh`

## What happens next

- **Invalid request** → intake lists exactly which sections are missing or empty, and rejects it. No slice is created, no code is touched. Fix the file and rerun intake.
- **Valid request** → intake converts it into a `CR-NNN` slice in `docs/slices/` (the original moves to `accepted/` as an audit record). The normal Ralph pipeline then handles it: "run ralph loop" picks it up with all quality gates, plus one extra gate that only CR slices have — **impact analysis**.

## The impact-analysis gate (why cross-stack bugs are safe)

Before a CR run may change any code, it must write `impact-analysis.md` in its run folder, covering: which backend models/endpoints and frontend screens are affected, which OTHER modules consume those pieces (the blast radius), which existing tests cover them, and which regression tests will be added in each affected module. **Validation fails the run if this file is missing** — so a frontend bug with backend consequences (or the reverse) always gets its full impact mapped before the first line of code changes.

## Stage rule

Intake refuses change requests while unfinished product slices remain — the backlog finishes first. Owner emergency override: `./scripts/ralph-intake.sh --now`.
