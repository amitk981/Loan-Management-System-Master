# Ralph Handoff

## Last Run

2026-07-14_130857_normal_run

## Current Status

Corrective 008B4 is complete. Every new legal renderer success atomically freezes contract
`legal-renderer-v1`, the exact generated-file UUID, and the stored SHA-256; instance saves and normal
ORM bulk mutations cannot rewrite that provenance. A current row must still match its retained
`DocumentFile`. Pre-provenance or mismatched rows list honestly as `legacy_unverified`, conflict on
exact replay without writes, and cannot satisfy checklist linkage. Retained plain-text DOCX/minimal
PDF fixtures with executed, verified, stamped, notarised, and checklist-linked history remain
unchanged through the additive migration.

The application-owned authority seam now returns standard 404 for an absent application only to the
source-authorised Compliance Team role holding the route permission; missing-permission and
unrelated roles remain nondisclosing 403. Genuine DOCX and PDF are both reopened against stored
checksums, replay with exact identity and zero writes, and pass the current checklist selector.
A-101 remains open: renderer provenance does not supply missing governed Term Sheet facts.

## Validation

Evidence is in `.ralph/runs/2026-07-14_130857_normal_run/evidence/`. Focused RED/GREEN and retained-
row migration suites pass. Django check and migration sync pass; all 752 backend tests pass with 23
expected PostgreSQL-only skips and 93% coverage against the 85% floor. Frontend build, typecheck,
lint, and all 293 tests pass. Independent Standards and Spec reviews report no remaining findings.

## Next Run

Run 008C2 next. Only after its terminal/checklist lifecycle boundary passes should 008D add
stamp/notary state. 008C2 and 008D are sharpened to consume only the exact 008B4 current-provenance
selector. The real M05-to-full-Term-Sheet path remains configuration-blocked under A-101.
