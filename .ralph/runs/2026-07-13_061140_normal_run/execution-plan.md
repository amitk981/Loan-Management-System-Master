# Execution Plan

Selected slice: `006Z13-member-scope-persistence-and-action-matrix-closure`

## Boundaries

- Change only the persisted member-scope authority seam, its migration, its public member-action
  and calculation callers/tests, and Ralph evidence/status documentation required by this run.
- Do not change frontend behavior or protected/source files.
- Preserve the existing nondisclosure envelope and immutable service-evidence maker provenance.

## TDD sequence

1. Add a focused database-boundary test for invalid scope shapes and nullable duplicate grants;
   run it first and retain RED output.
2. Add conditional check/unique constraints and one non-destructive migration; rerun the focused
   test and migration checks to GREEN.
3. Add independently selectable behavior rows for the public member list, detail/update, identity
   approval, supply capture/verification, service/relaxation maintenance, status calculation, and
   status verification interfaces. Each row will first prove permission-without-scope denial and
   zero writes, then the matching assignment-enabled behavior.
4. Map every production `ActiveMemberStatusModule.calculate` caller. Introduce or tighten the
   staff scope boundary while retaining authenticated `PortalAccount` member derivation; add a
   dependency/source scan preventing arbitrary HTTP member-id calculation.
5. Add real scope-query behavior for global, assigned, active/inactive team, unrelated assignments,
   created-by, and post-filter list totals. Extend denial snapshots to include service-evidence
   maker many-to-many rows and prove earlier makers remain checker-ineligible.
6. Run focused member suites, backend check/migration sync/full coverage, and all configured
   frontend gates. Save terminal logs and dependency-scan evidence.

## Completion records

- Update the Epic 006 digest, API contract only if the public contract changes, assumptions only
  if a source-silent decision is necessary, selected slice status, Ralph state/progress/handoff,
  changed-files, risk assessment, review packet, and final summary.
- Sharpen the next one or two `Not Started` slices only from source material already opened.
