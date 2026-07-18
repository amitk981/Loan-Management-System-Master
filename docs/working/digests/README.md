# Requirement Digests

One digest per epic. A digest is the distilled, slice-ready extract of the large files in `docs/source/` — field lists, endpoints, validation rules, role rules, and exact source-section pointers. A normal Ralph run reads only shared invariants plus its selected slice section (roughly 2–5 KB), even when the bounded epic digest contains additional prepared sections.

Rules:
- Create or extend the digest for an epic the first time one of its slices needs source material; every extraction an agent makes from `docs/source/` gets saved here. Start from the matching owner-curated capability map in `docs/working/maps/` — it already lists the exact source sections per capability (see `docs/working/maps/README.md` for the link syntax).
- Always include the source file and section number for each fact, so anything can be verified against the source of truth.
- Digests summarise the source; they never replace it. On any conflict, `docs/source/` wins.
- Keep each digest under ~300 lines; split by epic, never one giant file.
