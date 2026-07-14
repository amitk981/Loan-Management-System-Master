# Ralph Handoff

## Last Run

2026-07-14_062457_repair

## Current Status

Slice 008A is complete. The documents module now owns a versioned template catalogue at the exact
§26.3 GET/POST/PATCH endpoints. PATCH creates and links one immutable successor, exact replay is
zero-write, approved effective ranges cannot overlap for the same document/borrower variant, and
all real mutations atomically write attributable audit and shared version-history evidence.
Template-file ids pass the existing permissioned metadata boundary and responses expose only id/name
metadata—never storage keys, download actions, generation, or disputed Annexure routing.
The repair limits PostgreSQL row locks to the owning `ApprovalCase`/`DocumentTemplate` rows so
nullable eager-loaded evidence/file metadata no longer makes `FOR UPDATE` invalid.

## Validation

Repair evidence is in `.ralph/runs/2026-07-14_062457_repair/evidence/`; the original implementation
evidence remains in `.ralph/runs/2026-07-14_055848_normal_run/evidence/`. Django check/migration sync and
all 700 backend tests pass with 20 expected PostgreSQL-only skips at 93% coverage. Frontend build,
typecheck, lint, and all 269 tests pass. The historical five-race acceptance command passes twice on
PostgreSQL, and 008A's own five-request successor race passes twice on PostgreSQL. No frontend or
browser surface changed.

## Next Run

Run the due architecture review, then start sharpened 008B. It must generate one immutable loan
document only from an approved/effective 008A template and authoritative application facts; template
or file metadata never grants generation/download authority. 008C and 008D are now concretely
sharpened from the same source sections for the subsequent runs. A-095 still owns the unresolved
S72 active-versus-approved vocabulary question.
