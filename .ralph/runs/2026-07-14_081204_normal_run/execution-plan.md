# Execution Plan

Selected slice: `008A2-template-effective-integrity-and-file-reference-boundary`

## Scope

Close only the 008A template-catalogue integrity gaps: serialize writes by template identity,
centralize template-file reference provenance and authority, move catalogue reads to a selector,
pass transport-neutral request metadata to writes, and expose an explicit fail-closed borrower
variant resolver for 008B. Do not add generation, rendered documents, or frontend behavior.

## TDD sequence

1. Add a public-boundary test proving a globally attributable template upload can be referenced
   without granting template readers/managers download authority, then prove bare, corrupt,
   application-owned, unsupported-sensitivity, inaccessible, and permission-only files all fail
   with the same zero-write validation response. Capture RED, implement the documents-owned
   reference decision, and capture GREEN.
2. Add selector/API tests for strict filters and bounded pagination, then extract query shaping
   from the write module into `documents/selectors.py` while preserving envelopes and fields.
3. Add module tests for explicit borrower-template variant resolution, including unresolved
   repository member variants returning configuration-required validation rather than guessing.
4. Add PostgreSQL transactional races for five different overlapping first approved versions and
   concurrent exact-successor replay. Capture RED, add a database-backed template-identity lock,
   and capture two GREEN race passes. Add at most one non-destructive migration.
5. Refactor only while green; run the focused documents suite, Django check and migration sync,
   then all configured backend/frontend gates.

## Evidence and closeout

- Save RED/GREEN and race logs under `evidence/terminal-logs/`, plus sanitized API/reference
  matrices and gate summaries.
- Record changed files, risk, review traceability, final summary, and any source-silent assumption.
- Mark only 008A2 complete; update Ralph state/progress/handoff.
- Sharpen the next one or two Not Started slices only from already-opened Epic 008 sources/digest.
