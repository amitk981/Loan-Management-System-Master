# CLAUDE.md

Follow the Ralph AFK workflow defined in `AGENTS.md`.

Claude-specific guidance:
- Use Matt Pocock skills only at the workflow stages defined in `docs/working/SKILL_REGISTRY.md`.
- Prefer `/tdd` during implementation when there is a testable seam.
- Use `/diagnose` when tests fail repeatedly.
- Use `/handoff` at the end of a run.
- Use `/improve-codebase-architecture` only when architecture review is due.
- Use `/zoom-out` when repo structure is unclear.

Do not use skills randomly. Do not make broad refactors unless the runbook and risk rules allow it.
