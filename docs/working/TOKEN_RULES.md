# Token Rules

- Do not read all of `docs/source/` by default during normal runs.
- Read all relevant `docs/source/` files, and the whole source folder if genuinely needed, when a slice touches business rules, architecture, permissions, data models, APIs, money, compliance, or end-to-end workflow behavior.
- Use the existing frontend code in `sfpcl-lms/src/` as the visual and interaction reference for any frontend or full-stack slice.
- Start with `docs/working/CONTEXT.md`.
- Read `docs/working/HANDOFF.md` before choosing work.
- Read the selected slice file and the parent epic file its "Epic file:" line links — the epic carries the distilled scope, validation rules, and screen list for its slices.
- Use `rg` before opening large files.
- Check `docs/working/digests/` first. Read the shared-invariants section and the selected slice's section; do not open the entire digest by default.
- Open a large `docs/source/` file only when the selected digest section does not cover what the slice needs, and add only the missing distilled fact afterwards.
- Open source docs only when the selected slice references them.
- Keep slice files small.
- Batch related searches, reads, edits, and focused tests. Prefer one bounded command over many one-line probes.
- After a candidate grows beyond roughly 500 changed lines, inspect `git diff --stat` and targeted hunks; do not repeatedly print the complete cumulative diff.
- Treat 80 tool calls or 70% context occupancy as a planning warning: stop rediscovering context, reread the execution plan, and finish through focused edits/tests. If the remaining scope is still broad, report that the slice should be split rather than expanding it silently.
- Store long logs and evidence in `.ralph/runs/<run-id>/`.
- Summarize durable decisions in ADRs.
- Keep `AGENTS.md` and `CLAUDE.md` short.
- Update `HANDOFF.md` after each run so future agents do not depend on chat history.
