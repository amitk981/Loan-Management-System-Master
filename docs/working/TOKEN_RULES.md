# Token Rules

- Do not read all of `docs/source/` by default during normal runs.
- Read all relevant `docs/source/` files, and the whole source folder if genuinely needed, when a slice touches business rules, architecture, permissions, data models, APIs, money, compliance, or end-to-end workflow behavior.
- Use the existing frontend code in `sfpcl-lms/src/` as the visual and interaction reference for any frontend or full-stack slice.
- Start with `docs/working/CONTEXT.md`.
- Read `docs/working/HANDOFF.md` before choosing work.
- Read only the selected slice file.
- Use `rg` before opening large files.
- Open source docs only when the selected slice references them.
- Keep slice files small.
- Store long logs and evidence in `.ralph/runs/<run-id>/`.
- Summarize durable decisions in ADRs.
- Keep `AGENTS.md` and `CLAUDE.md` short.
- Update `HANDOFF.md` after each run so future agents do not depend on chat history.
