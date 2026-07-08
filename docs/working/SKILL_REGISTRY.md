# Skill Registry

Skills are **Claude Code accelerators only** — codex cannot invoke them. That is why every essential discipline (TDD, diagnosis loop, handoff, review charter, decision policy) is baked into `scripts/ralph-run.sh` prompts and `docs/working/` rules as plain instructions both agents follow. Skills make Claude-driven runs sharper; the workflow must never *depend* on one. All Matt Pocock skills are installed at user level (`~/.claude/skills/`), so they are available inside AFK worktrees too.

## Skills in use (Claude-driven runs and owner sessions)

| Stage | Skill | How it is used here |
|---|---|---|
| Implementation (normal runs) | `tdd` | The red-green-refactor discipline for backend/business logic. Codex follows the same rule via the run prompt; Claude additionally invokes the skill. |
| Repair mode | `diagnosing-bugs` | Structured reproduce → minimize → hypothesize → instrument → fix loop on the failed run's salvaged artifacts in `.ralph/runs/`. |
| Independent review (architecture-review runs) | `code-review` | Two-axis review of `git diff <last-review-commit>...HEAD`. **Pass the slice files as the spec** — the Spec axis then checks doc fidelity, which is this project's core promise. Findings land in `docs/working/REVIEW_FINDINGS.md`. |
| Independent review (architecture-review runs) | `improve-codebase-architecture`, `codebase-design` | Architecture drift, deep-module quality, refactor-slice proposals (never direct refactors). |
| Digest building (first slice of an epic) | `research`, `domain-modeling` | Extract requirements from `docs/source/` primary sources into `docs/working/digests/`, keeping domain terminology consistent with the source documents. |
| Owner sessions: reviewing recent work | Built-in `/code-review` (Claude Code) | The owner's independent multi-agent review of recent slices — the single best use of owner time. |
| Owner sessions: reading client PDFs | Anthropic `pdf` skill | Extracting the two SOP PDFs in `docs/source/` into digests when a slice needs them. |
| Owner sessions: merge conflicts | `resolving-merge-conflicts` | Only if an auto-merge fails and a branch needs manual merging. |
| Re-planning sessions only | `grill-with-docs`, `to-issues`, `to-prd`, `triage`, `handoff` | The backlog already exists (120+ slices), so these run only if the plan itself is being reworked in an interactive session with the owner. |

## Maintenance stage (post-development)

Once all product slices are Complete, the same skills carry over to change-request
work — stage mapping and the owner's operating rhythm live in
`docs/working/MAINTENANCE_STAGE_PLAN.md` §7. Summary: `tdd` and `diagnosing-bugs`
during CR implementation/repair runs, built-in `/code-review` for owner batch review,
`grill-with-docs` + `domain-modeling` when a big CR is split into an epic,
`research` for new external integrations. No new skills are required for maintenance;
the pipeline itself is `ralph-intake.sh` + the loop, not a skill.

## Deliberately NOT used (decided 2026-07-02)

| Skill | Why excluded |
|---|---|
| `git-guardrails-claude-code` | Its hooks block `git push` and `git branch -D` — operations the automation legitimately performs (auto-push, recovery). Installing it would break the loop. Guardrails here are enforced by `ralph-validate.sh` instead. |
| `setup-pre-commit` | Redundant: gates + CI already block bad commits; husky would add a root `package.json` and slow/fight automated commits. |
| `implement` | Overlaps Ralph's own run discipline; two competing workflows in one prompt degrade both. |
| `grill-me` / `grilling` | Interview loops need a developer interviewee; the owner is a non-developer. `grill-with-docs` (against documents) is kept for re-planning instead. |
| `prototype` | The design is fixed — the approved prototype already exists; throwaway prototyping would invite design drift. |
| `migrate-to-shoehorn` | Premature — revisit if frontend test fixtures grow complex after 002EY. |
| `teach`, `edit-article`, `obsidian-vault`, `scaffold-exercises`, `writing-great-skills`, `ask-matt` | Personal/authoring tools, not relevant to this repository. |

## Rules
- Skills run only at the stages above. Do not invoke skills randomly.
- A missing skill is never a blocker — fall back to the baked-in rules.
- New internet skills are installed only after the owner-side operator reviews their content (skills are prompt injections by design; treat them like dependencies).
