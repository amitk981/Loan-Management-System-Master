# Execution Plan

Selected slice: 006Y6-witness-contact-and-action-parity-closure

1. Inspect the existing witness model, correction module, permission/object predicates, API
   serializers, Application Detail panel, migrations, and focused tests. Preserve immutable
   verification-time shareholding, folio, member, verifier, PAN, and Aadhaar evidence semantics.
2. Add one failing backend behavior test at a time for address/mobile persistence and history,
   exact payload validation, contact-only versus identity maker-checker behavior, and disabled
   six-field action projections that match public write denials. Save RED output before making
   production changes, then implement the smallest model/service/view changes and save GREEN output.
3. Add failing mounted frontend tests for contact capture/correction request bodies, canonical
   collection refetch, stable disabled reasons, and mutation suppression without authority. Extend
   existing API types and the Application Detail witness form using only established fields and
   layout patterns, then save GREEN output.
4. Create one non-destructive migration, update the maintained API contract/digest where the public
   response changed, and produce self-contained API/history evidence. Attempt the declared browser
   acceptance only if the slice declares it; otherwise rely on mounted interaction coverage.
5. Run frontend build/typecheck/lint/tests and backend check/migration-sync/full coverage with the
   mandated interpreter. Save logs, review the diff/protected paths/diff limits, write changed-files,
   risk assessment, review packet, and final summary, then mark only 006Y6 complete and update
   progress/state/handoff. Sharpen the next one or two eligible Not Started slices only from source
   material already opened during this run.
