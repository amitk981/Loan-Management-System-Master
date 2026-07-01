# Token Rules

- Do not read all of `docs/source/` by default during normal runs.
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
