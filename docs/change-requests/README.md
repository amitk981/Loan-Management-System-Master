# Change Requests (Maintenance Stage)

Once all product slices are complete, this is the ONLY way changes enter the codebase. Bugs and feature requests written in chat are never implemented directly — they must become a validated change request first. If a request does not follow the template, **nothing in the code changes**.

## How to file a request (owner)

1. Copy the right template: `TEMPLATE-bug.md` for anything broken (frontend, backend, or cross-stack), or `TEMPLATE-feature.md` for new functionality (`feature`) and for changes to the approved design itself (`ui-change` — labels, colours, layout; requires the phrase "owner approved" in the Source Document Reference, because you are amending your own approved design).
2. Save it as a new file in `inbox/` (any filename, e.g. `login-button-wrong-label.md`).
3. Fill in every section. You can ask codex or Claude to help you fill it in — that is allowed and encouraged; the rule is only that the *file* must be complete.
4. Run: `./scripts/ralph-intake.sh`

## What happens next

- **Invalid request** → intake lists exactly which sections are missing or empty, and rejects it. No slice is created, no code is touched. Fix the file and rerun intake.
- **Valid request** → intake converts it into a `CR-NNN` slice in `docs/slices/` (the original moves to `accepted/` as an audit record). The normal Ralph pipeline then handles it: "run ralph loop" picks it up with all quality gates, plus one extra gate that only CR slices have — **impact analysis**.

## The impact-analysis gate (why cross-stack bugs are safe)

Before a CR run may change any code, it must write `impact-analysis.md` in its run folder, covering: which backend models/endpoints and frontend screens are affected, which OTHER modules consume those pieces (the blast radius), which existing tests cover them, and which regression tests will be added in each affected module. **Validation fails the run if this file is missing** — so a frontend bug with backend consequences (or the reverse) always gets its full impact mapped before the first line of code changes.

## When a change is bigger than one slice (epics)

Most change requests fit in a single `CR-NNN` slice and need nothing beyond the flow above. But occasionally a request describes a whole new capability that cannot be done in one narrow run. For that case this folder carries two extra templates:

- `TEMPLATE-slice.md` — the standard format for a full implementation slice (mirrors the real files in `docs/slices/`).
- `TEMPLATE-epic.md` — the standard format for a parent epic (mirrors the real files in `docs/epics/`).

The flow stays honest and auditable:

1. File the change request normally (feature template) and run intake — the audit record in `accepted/` and the `CR-NNN` slice are still created.
2. If the accepted request is clearly too big for one run, the owner (with agent help in chat — allowed and encouraged) breaks it down: create one epic from `TEMPLATE-epic.md` in `docs/epics/`, and its child slices from `TEMPLATE-slice.md` in `docs/slices/`, each pointing back to the accepted change request under `## Origin`.
3. Register every new slice as a row in `docs/working/IMPLEMENTATION_SLICE_INDEX.md`.
4. Edit the superseded `CR-NNN` slice's `## Status` from `Not Started` to `Superseded — see Epic <NNN>` so the loop skips it but the trail remains.
5. Run the loop as usual — it picks up the new slices by filename order, with all normal gates.

Two rules the templates already encode, worth repeating: the `## Status` and `## Risk Level` section names are parsed by the run scripts and must not be renamed, and the loop only runs slices whose Status is exactly `Not Started`.

## Stage rule

Intake refuses change requests while unfinished product slices remain — the backlog finishes first. Owner emergency override: `./scripts/ralph-intake.sh --now`.
